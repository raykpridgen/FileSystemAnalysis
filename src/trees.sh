#!/bin/bash

max_levels=$1
max_nodes=$2
nodes_created=0

# Remove previous tree if it exists
[ -d "root" ] && rm -r "root" && echo "Previous tree removed"

# Create root
mkdir -p root
cd root || exit

# Function to fill a given subdirectory with files and folders
populate_folders()
{
    local level=$1
    local num_folders=$((RANDOM % 5 + 1))
    local num_files=$((RANDOM % 7 + 1))

    # Adjust for remaining nodes
    local remaining=$((max_nodes - nodes_created))
    if [ $((num_folders + num_files)) -gt $remaining ]; then
        if [ "$remaining" -le 0 ]; then return; fi
        num_folders=$((RANDOM % remaining + 1))
        num_files=$((remaining - num_folders))
    fi

    # Create files
    for f in $(seq 1 $num_files); do
        [ "$nodes_created" -ge "$max_nodes" ] && break
        touch "fileL${level}N${f}.txt"
        nodes_created=$((nodes_created + 1))
    done

    # Create folders
    for d in $(seq 1 $num_folders); do
        [ "$nodes_created" -ge "$max_nodes" ] && break
        mkdir "folderL${level}N${d}"
        nodes_created=$((nodes_created + 1))
    done
}

# Breadth-first iterative traversal
current_level_folders=(".")
# For each level down from root
for ((level=1; level<=max_levels; level++)); do
    next_level_folders=()
    # For each folder
    for folder in "${current_level_folders[@]}"; do
        cd "$folder" || continue
        populate_folders "$level"
        # add subfolders to next level
        for sub in */; do
            [ -d "$sub" ] || continue
            # randomly skip some
            if [ $((RANDOM % 4)) == 1 ]; then continue; fi
            next_level_folders+=("$folder/$sub")
        done
        cd - > /dev/null || exit
    done
    # Move to next level
    current_level_folders=("${next_level_folders[@]}")
done
