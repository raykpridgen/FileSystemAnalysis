import os
import shutil
from pathlib import Path
import random as ran
import string
import sys

# Top function
def modify_tree(root, newRoot, files, max_new=5, delete_prob=0.1, edit_prob=0.3, create_prob=0.4):
    if newRoot.exists():
        shutil.rmtree(newRoot)

    shutil.copytree(root, newRoot)
    
    modify_recurse(newRoot, files, max_new, delete_prob, edit_prob, create_prob)

# Recursively edit a tree
def modify_recurse(root, files, max_new=2, delete_prob=0.2, edit_prob=0.3, create_prob=0.2):
    # Iterate through directory, edit files
    for entry in root.iterdir():
        
        # Randomly delete folders
        if entry.is_dir():
            if ran.random() < delete_prob:
                shutil.rmtree(entry)
                continue

            modify_recurse(entry, files, max_new, delete_prob, edit_prob, create_prob)

        
        elif entry.is_file():
            # Randomly edit a file
            if ran.random() < edit_prob:
                with open (entry, "a") as f:
                    size = ran.randint(500, 1000)
                    fileText = "".join(ran.choices(string.ascii_letters + string.digits, k=size))
                    f.write(fileText)

            # Randomly delete a file
            elif ran.random() < delete_prob:
                entry.unlink()

        # Create files
        for _ in range(ran.randint(0, max_new)):
            if ran.random() < create_prob:
                fileExt = files[ran.randint(0, len(files) - 1)]
                filePath = root / f"newfile_{ran.randint(0, 500)}{fileExt}"
                with open(filePath, "w") as f:
                    size = ran.randint(100, 5000)
                    fileText = "".join(ran.choices(string.ascii_letters + string.digits, k=size))
                    f.write(fileText)

        # Create folders
        if ran.random() < create_prob * 0.5:
            make_recurse(root, max_new-2, max_new-2, files)

def make_recurse(root, depth, degree, files):
    if depth == 0:
        return

    # For each subfolder at a level
    for i in range(degree):
        # Attach root/node_depth_num
        sub = root / f"node_{depth}_{i}"
        # Skip making a node randomly
        if ran.random() < 0.5:
            # Make the subdirectory
            sub.mkdir(parents=True, exist_ok=True)
            print(f"node_{depth}_{i}")
            
            # Random number of files at a level
            ranFile = ran.randint(0, degree)
            if ranFile > 0:
                # Create each file
                for j in range(0, ranFile):
                    # Extension selection from list
                    fileExt = files[ran.randint(0, len(files) - 1)]
                    filePath = sub / f"file_{depth}_{i}_{j}{fileExt}"
                    filePath.touch()
                    print(f"file_{depth}_{i}{fileExt}")
                    # Put random size of data in each file
                    dataSize = ran.randint(100, 5000)
                    fileText = "".join(ran.choices(string.ascii_letters + string.digits, k=dataSize))
                    with open(filePath, "w") as f:
                        f.write(fileText)
            # Run again with new, decreased depth
            make_recurse(sub, depth-1, degree, files)



if (len(sys.argv) < 7):
    print("usage: python3 modify.py <original_name> <modified_name> <max_new_files> <delete_prob> <edit_prob> <create_prob> <iterations>")
    sys.exit(1)

originalParam = sys.argv[1]
modifyParam = sys.argv[2]
newFilesParam = int(sys.argv[3])
deleteProbParam = float(sys.argv[4])
editProbParam = float(sys.argv[5])
createProbParam = float(sys.argv[6])
iterationsParam = int(sys.argv[7])

filetypes = [".txt", ".csv", ".json", ".log", ".md", ".xml"]

root = Path(originalParam)
newRoot = Path(modifyParam)


for i in range(0, iterationsParam):
    if i == 0:
        root = Path(originalParam)
        newRoot = Path(f"{modifyParam}{i}")
    else:
        root = Path(f"{modifyParam}{i-1}")
        newRoot = Path(f"{modifyParam}{i}")
    
    modify_tree(root, newRoot, filetypes, newFilesParam, deleteProbParam, editProbParam, createProbParam)

