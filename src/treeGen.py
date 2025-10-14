import random
import os
import shutil
from pathlib import Path
import random as ran
import sys
import random
import time
import json
from utils import getTimeInMs

# CREATION TIME IMMUTABLE ON LINUX
# pywin32 TO MODIFY CREATION ON WINDOWS

SAVE_TO_DIR = "../data/"

def parse_dist_params(degree_mode="low_degree", filetype_mode="default", file_ext_mode="default", permissions_mode="default", size_mode="default"):
    
    # Load JSON from file
    with open("dists/params.json", 'r') as f:
        params = json.load(f)

    # Degree
    degree_distr = {int(k): v for k, v in params["degree"][degree_mode].items()}
    # File type
    fileType_distr = {k: v for k, v in params["type"][filetype_mode].items()}
    # Extensions
    fileExt_distr = {k: v for k, v in params["filetypes"][file_ext_mode].items()}
    # Permissions
    permissions_distr = {int(k, 8): v for k, v in params["permissions"][permissions_mode].items()}
    # Sizes
    size_distr = {k: v for k, v in params["size"][size_mode].items()}

    return degree_distr, fileType_distr, fileExt_distr, permissions_distr, size_distr

# Clean up previous run with same name
def clean_tree(rootName):
        # If root name already exists
        if os.path.exists(rootName):
            startTimeClean = time.perf_counter()
            # If it is a file, remove
            if os.path.isfile(rootName):
                os.remove(rootName)
            
            # If name is a dir
            elif os.path.isdir(rootName):
                shutil.rmtree(rootName)
            endTimeClean = time.perf_counter()
            print(f"Removed tree at '{rootName}' in {getTimeInMs(startTimeClean, endTimeClean)} ms")

class ArtificialTree:
    def __init__(self, rootName, depthRange, degreeDist, sizeDist, timeRange, fileDist, fileExtensions, modeDist, users=1, groups=1):
        # String, name of root
        self.rootName = rootName
        # Fixed int pair, depth
        self.depthRange = depthRange
        self.currentMaxDepth = 0
        # Array / Dict of distribution values to make random nodes in each folder
        self.degreeDist = degreeDist
        # Array / Dict of distribution values to determine size of files made
        # Normal, lognormal, Pareto
        self.sizeDist = sizeDist
        # Tuple of (startTime, endTime) in which files can have CREATION time
        self.timeRange = timeRange
        # Distribution of regular files, folders, symlinks
        self.fileDist = fileDist
        # File types to use
        self.fileExtensions = fileExtensions
        # Distribution of file permissions
        self.modeDist = modeDist
        # Number of users to own files
        self.users = users
        # Number of groups users inhabit
        self.groups = groups
        # Created file locations
        self.filesCreated = []

    # Generate a random degree of a node from the dist
    def sample_degree(self):
        randomProb = ran.random()
        cumulativeProb = 0
        # Dict looks like numChild : prob
        # Move through each prob
        for numChild, childProb in self.degreeDist.items():
            # Sum probs for each child added
            cumulativeProb += childProb
            # If prob surpasses distribution value for a child #, return as num of children
            if randomProb <= cumulativeProb:
                return numChild
        return 0

    # Generate random file size from distribution
    def sample_size(self):
        sizeTypes = list(self.sizeDist.keys())
        probs = [self.sizeDist[c]["prob"] for c in sizeTypes]

        selection = ran.choices(sizeTypes, weights=probs, k=1)[0]

        low, high = self.sizeDist[selection]["range"]
        size = ran.randint(low, high)
        return size

    # Generate random times for file within bounds
    def sample_time(self):
        # Get range
        start, end = self.timeRange
        # Pick random time within range for create
        crtime = ran.randint(start, end)
        # Follow scheme for each succeeding time
        ctime = crtime + ran.randint(0, 1000)
        mtime = ctime + ran.randint(0, 1000)
        atime = mtime + ran.randint(0, 1000)
        return atime, mtime, ctime, crtime

    # Generate a file type to create
    def sample_fileType(self):
        randomProb = ran.random()
        cumulativeProb = 0
        # Dict looks like type : prob
        # Move through each prob
        for type, typeProb in self.fileDist.items():
            # Sum probs for each child added
            cumulativeProb += typeProb
            # If prob surpasses distribution value for a child #, return as num of children
            if randomProb <= cumulativeProb:
                return type
        return 0
    
    def sample_Extensions(self):
        randomProb = ran.random()
        cumulativeProb = 0
        # Dict looks like ext : prob
        # Move through each prob
        for ext, extProb in self.fileExtensions.items():
            # Sum probs for each child added
            cumulativeProb += extProb
            # If prob surpasses distribution value for a child #, return as num of children
            if randomProb <= cumulativeProb:
                return ext
        return 0

    def sample_permissions(self):
        randomProb = ran.random()
        cumProb = 0
        for perm, permProb in self.modeDist.items():
            cumProb += permProb
            if randomProb <= cumProb:
                return perm
        return 0o644
    
    # Generate random file extension
    # Generate tree from params
    def generate_tree(self):
        # Create root dir
        root = Path(self.rootName)
        # remove old root if same name exists
        clean_tree(root)

        startGenTime = time.perf_counter()
        
        root.mkdir(parents=True, exist_ok=True)
        os.chmod(root, 0o755)
        self.gen_tree_atlevel(0, root)

        endGenTime = time.perf_counter()
        print(f"Generated tree '{str(newTree.rootName)[8:]}' in {getTimeInMs(startGenTime, endGenTime)} ms.")

    # Generate at a level, utilize recursion
    def gen_tree_atlevel(self, depth, root, max_files=-1):
        files_made = 0
        # Return if the depth is too far
        if (depth >= self.depthRange[1]):
            return 0

        # Determine number of children
        degree = self.sample_degree()

        # Determine type for each child
        folderNum = 0
        fileNum = 0
        symlinkNum = 0

        # Assign number of each type to make
        for i in range(0, degree):
            childType = self.sample_fileType()
            if (childType == "file"):
                # Check to not exceed max files
                if max_files != -1 and files_made >= max_files:
                    pass
                else:
                    fileNum += 1
                    files_made += 1
            elif (childType == "folder"):
                folderNum += 1
            elif (childType == "symlink"):
                # Check to not exceed max files
                if max_files != -1 and files_made >= max_files:
                    pass
                else:
                    symlinkNum += 1
                    files_made += 1
        
        # Increase number of folders to expand depth if below minimum 
        if depth < self.depthRange[0] and folderNum == 0:
            folderNum = 1
            if fileNum > 0:
                fileNum -= 1
                files_made -= 1

        # Folders
        for i in range(0, folderNum):
            # Attach root/node_depth_num
            sub = root / f"folder{depth}_{i}"
            sub.mkdir(parents=True, exist_ok=True)
            self.filesCreated.append(sub)
            self.currentMaxDepth += 1
            # RECURSION HERE
            # Recurse if min is not met, or if it has on a prob
            if max_files == -1:
                if depth < self.depthRange[0]:
                    files_made += self.gen_tree_atlevel(depth+1, sub)
                elif ran.random() < 0.4:
                    files_made += self.gen_tree_atlevel(depth+1, sub)
            else:
                remaining = max(0, max_files - files_made)
                if remaining == 0:
                    return 0
                if depth < self.depthRange[0]:
                    files_made += self.gen_tree_atlevel(depth+1, sub, max_files=remaining)
                elif ran.random() < 0.4:
                    files_made += self.gen_tree_atlevel(depth+1, sub, max_files=remaining)

        # Files
        for i in range(0, fileNum):
            # Make file
            filePath = root / f"file_{depth}_{i}{self.sample_Extensions()}"
            filePath.touch()
            files_made += 1
            self.filesCreated.append(filePath)
            # File size
            dataSize = self.sample_size()
            with open(filePath, 'wb') as f:
                f.write(os.urandom(dataSize))
            
            # File permissions
            os.chmod(filePath, self.sample_permissions())

            # Times - currently mutable access time and mod time
            atime, mtime, ctime, crtime = self.sample_time()
            os.utime(filePath, (atime, mtime))
        
        # Symlinks
        for i in range(symlinkNum):
            if self.filesCreated:
                target = ran.choice(self.filesCreated)
                linkPath = root / f"symlink_{depth}_{i}_{ran.randint(0, 9999)}"
                try:
                    os.symlink(target, linkPath)
                except FileExistsError:
                    pass
        return files_made
      
"""
Future usages

python3 treeGen.py create <root_name> <min_depth> <max_depth>
    types of json args?
python3 treeGen.py clean <root_name>
python3 treeGen.py modify <root_Name> <iterations>
    types of modifications -- json?

"""
if __name__ == "__main__":
    args = sys.argv[1:]

    # Show help if no args or user explicitly asks
    if not args or args[0] in ("-h", "--help"):
        print("""
This program generates a mock file tree with pseudorandom files, subdirectories, and symlinks.

USAGE:

Generate new tree:
    python3 treeGen.py <root_name> <minDepth> <maxDepth>

Remove tree(s):
    python3 treeGen.py clean <root_name> <num_remove>

        <num_remove> = 0   → remove just <root_name>
          greater than 0   → remove <root_name>0, <root_name>1, ... up to <num_remove - 1>
            """)
        sys.exit(0)

    # Handle CLEAN operation
        if args[0] == "clean":
            if len(args) < 2:
                print("Usage: python3 treeGen.py clean <root_name> <num_remove>")
                sys.exit(1)
            
            elif len(args) == 2:
                root = args[1]
                clean_tree(f"{SAVE_TO_DIR}{root}")
                sys.exit(0)

        else:
            root, num = args[1], int(args[2])

            for i in range(-1, num):
                if i == -1:
                    startTimeClean = time.perf_counter()
                    clean_tree(f"{SAVE_TO_DIR}{root}")
                    endTimeClean = time.perf_counter()
                    print(f"Removed tree at '{root}' in {getTimeInMs(startTimeClean, endTimeClean)} ms")
                else:
                    startTimeClean = time.perf_counter()
                    clean_tree(f"{SAVE_TO_DIR}{root}{i}")
                    endTimeClean = time.perf_counter()
                    print(f"Removed tree at '{root}{i}' in {getTimeInMs(startTimeClean, endTimeClean)} ms")
            
            sys.exit(0)

    # Handle GENERATION
    if len(args) < 3:
        print("Usage: python3 treeGen.py <root_name> <minDepth> <maxDepth>")
        sys.exit(1)

    rootName = f"{SAVE_TO_DIR}{sys.argv[1]}"
    depthRange = [int(sys.argv[2]), int(sys.argv[3])]
    timeRange = (int(time.time()) - 30*24*60*60, int(time.time()))


    degree_type = "low_degree"

    degree_distr, file_type_distr, file_ext_distr, permissions_distr, size_distr = parse_dist_params(degree_mode=degree_type)


    newTree = ArtificialTree(rootName, depthRange, degree_distr, size_distr, timeRange, file_type_distr, file_ext_distr, permissions_distr)
    newTree.generate_tree()