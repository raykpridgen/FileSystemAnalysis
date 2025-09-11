import os
import shutil
from pathlib import Path
import random as ran
import string
import sys


# CREATION TIME IMMUTABLE ON LINUX
# pywin32 TO MODIFY CREATION ON WINDOWS

"""
Permissions scheme
Owner | Group | Others
r w x   r w x   r w x

r = 4
w = 2 
x = 1

Sum bits for each category

"""
filetypes = [".txt", ".csv", ".json", ".log", ".md", ".xml"]
permissions = ["0o444", "0o644", "0o666", "0o744"]



def basicTree(depth, size, degree, filetypes, permissions):
    root = "root"
    
    if depth == 0:
        return
    
    # If name exists
    if os.path.exists(root):
        # If name is a file
        if os.path.isfile(root):
            os.remove(root)
        # If name is a dir
        elif os.path.isdir(root):
            shutil.rmtree(root)
    
    # Make tree
    os.makedirs(root)

# Top function, handle existence and call recursion
def make_tree(root, depth, degree, files):
    if os.path.exists(root):
        # If name is a file
        if os.path.isfile(root):
            os.remove(root)
        # If name is a dir
        elif os.path.isdir(root):
            shutil.rmtree(root)
    
    root.mkdir(parents=True, exist_ok=True)
    make_recurse(root, depth, degree, files)

# Recursively makes a tree
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


# Args: root name, depth, degree
if (len(sys.argv)) < 3:
    print("Usage: python3 trees.py <root_name> <depth> <degree>")
    sys.exit(1)
rootName = sys.argv[1]
depthParam = int(sys.argv[2])
degreeParam = int(sys.argv[3])
root = Path(rootName)

make_tree(root, depthParam, degreeParam, filetypes)
