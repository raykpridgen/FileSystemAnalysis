#define _DEFAULT_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#include <errno.h>
#include <time.h>
#include <pthread.h>

#define SAVE_TO_DIR "../data/"  // Define the base directory
#define MAX_THREADS 16     // Limit threads to avoid contention
#define SEQUENTIAL_THRESHOLD 10  // Use sequential deletion for small directories

double get_time_in_ms(struct timespec start, struct timespec end) {
    return (end.tv_sec - start.tv_sec) * 1000.0 + (end.tv_nsec - start.tv_nsec) / 1000000.0;
}

long get_available_threads() {
    long nthreads = sysconf(_SC_NPROCESSORS_ONLN);
    if (nthreads < 1) {
        fprintf(stderr, "Error: Could not determine number of processors: %s\n", strerror(errno));
        return 1;
    }
    return nthreads > MAX_THREADS ? MAX_THREADS : nthreads; // Cap at MAX_THREADS
}

typedef struct {
    char *path;
    int result;
} thread_arg_t;

int clean_tree_sequential(const char *path) {
    struct stat path_stat;
    if (lstat(path, &path_stat) != 0) {
        fprintf(stderr, "Error accessing %s: %s\n", path, strerror(errno));
        return -1;
    }

    if (S_ISREG(path_stat.st_mode) || S_ISLNK(path_stat.st_mode)) {
        if (unlink(path) != 0) {
            fprintf(stderr, "Error removing file %s: %s\n", path, strerror(errno));
            return -1;
        }
        return 0;
    } else if (S_ISDIR(path_stat.st_mode)) {
        DIR *dir = opendir(path);
        if (!dir) {
            fprintf(stderr, "Error opening directory %s: %s\n", path, strerror(errno));
            return -1;
        }

        struct dirent *entry;
        char subpath[1024];
        int ret = 0;

        while ((entry = readdir(dir)) != NULL) {
            if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
                continue;
            }
            snprintf(subpath, sizeof(subpath), "%s/%s", path, entry->d_name);
            if (clean_tree_sequential(subpath) != 0) {
                ret = -1;
            }
        }
        closedir(dir);

        if (rmdir(path) != 0) {
            fprintf(stderr, "Error removing directory %s: %s\n", path, strerror(errno));
            return -1;
        }
        return ret;
    } else {
        fprintf(stderr, "Unsupported file type for %s\n", path);
        return -1;
    }
}

void *clean_tree_thread(void *arg) {
    thread_arg_t *targ = (thread_arg_t *)arg;

    // Check if path is a file or symbolic link first
    struct stat path_stat;
    if (lstat(targ->path, &path_stat) != 0) {
        fprintf(stderr, "Error accessing %s: %s\n", targ->path, strerror(errno));
        targ->result = -1;
        return NULL;
    }

    if (S_ISREG(path_stat.st_mode) || S_ISLNK(path_stat.st_mode)) {
        if (unlink(targ->path) != 0) {
            fprintf(stderr, "Error removing file %s: %s\n", targ->path, strerror(errno));
            targ->result = -1;
        } else {
            targ->result = 0;
        }
        return NULL;
    }

    // Count entries to decide sequential vs. parallel
    DIR *dir = opendir(targ->path);
    if (!dir) {
        fprintf(stderr, "Error opening directory %s: %s\n", targ->path, strerror(errno));
        targ->result = -1;
        return NULL;
    }

    int entry_count = 0;
    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }
        entry_count++;
    }
    rewinddir(dir);

    // Use sequential deletion for small directories
    if (entry_count <= SEQUENTIAL_THRESHOLD) {
        closedir(dir);
        targ->result = clean_tree_sequential(targ->path);
        return NULL;
    }

    // Parallel deletion for larger directories
    long max_threads = get_available_threads();
    pthread_t *threads = malloc(max_threads * sizeof(pthread_t));
    thread_arg_t *thread_args = malloc(max_threads * sizeof(thread_arg_t));
    int thread_count = 0;
    int ret = 0;

    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        char subpath[1024];
        snprintf(subpath, sizeof(subpath), "%s/%s", targ->path, entry->d_name);
        thread_args[thread_count].path = strdup(subpath);
        thread_args[thread_count].result = 0;

        if (pthread_create(&threads[thread_count], NULL, clean_tree_thread, &thread_args[thread_count]) != 0) {
            fprintf(stderr, "Error creating thread for %s: %s\n", subpath, strerror(errno));
            free(thread_args[thread_count].path);
            ret = -1;
            continue;
        }
        thread_count++;

        if (thread_count >= max_threads) {
            for (int i = 0; i < thread_count; i++) {
                pthread_join(threads[i], NULL);
                if (thread_args[i].result != 0) {
                    ret = -1;
                }
                free(thread_args[i].path);
            }
            thread_count = 0;
        }
    }

    for (int i = 0; i < thread_count; i++) {
        pthread_join(threads[i], NULL);
        if (thread_args[i].result != 0) {
            ret = -1;
        }
        free(thread_args[i].path);
    }

    free(threads);
    free(thread_args);
    closedir(dir);

    if (rmdir(targ->path) != 0) {
        fprintf(stderr, "Error removing directory %s: %s\n", targ->path, strerror(errno));
        targ->result = -1;
    } else {
        targ->result = ret;
    }
    return NULL;
}

int clean_tree(const char *rootName) {
    struct stat path_stat;
    if (lstat(rootName, &path_stat) != 0) {
        fprintf(stderr, "Error accessing %s: %s\n", rootName, strerror(errno));
        return -1;
    }

    if (S_ISREG(path_stat.st_mode) || S_ISLNK(path_stat.st_mode)) {
        return clean_tree_sequential(rootName);
    }

    thread_arg_t arg = { .path = strdup(rootName), .result = 0 };
    clean_tree_thread(&arg);
    int result = arg.result;
    free(arg.path);
    return result;
}

int main(int argc, char *argv[]) {
    if (argc < 2 || strcmp(argv[1], "clean") != 0) {
        fprintf(stderr, "Usage: %s clean <root_name>\n", argv[0]);
        exit(1);
    }

    if (argc < 3) {
        fprintf(stderr, "Usage: %s clean <root_name>\n", argv[0]);
        exit(1);
    }

    char root_path[1024];
    snprintf(root_path, sizeof(root_path), "%s%s", SAVE_TO_DIR, argv[2]);

    struct timespec start_time, end_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    if (clean_tree(root_path) != 0) {
        fprintf(stderr, "Failed to clean tree at '%s'\n", argv[2]);
        exit(1);
    }

    clock_gettime(CLOCK_MONOTONIC, &end_time);
    printf("Removed tree at '%s' in %.2f ms\n", argv[2], get_time_in_ms(start_time, end_time));

    return 0;
}