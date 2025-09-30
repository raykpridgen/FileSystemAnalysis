import os
import shutil
from pathlib import Path
import random as ran
import string
import sys
import json
import math
import time
from treeGen import ArtificialTree

SAVE_TO_DIR = "../data/"

def load_json_params(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

class ModifyTree:
    def __init__(self, originalRoot, newRoot, maxNew, iterations):
        # Original root
        self.originalRoot = Path(f"{SAVE_TO_DIR}{originalRoot}")
        # Max new files to be added to the new tree
        self.maxNew = maxNew
        # Dict of edit probabilities
        self.editProbs = load_json_params("dists/modify.json")
        # Iterations, num of trees to generate
        self.iterations = iterations
        # List to easily maintain each iteration of the modification
        self.newRootList = []
        # Populate list
        for i in range(self.iterations):
            self.newRootList.append(Path(f"{SAVE_TO_DIR}{newRoot}{i}"))

    # Create an ArtificialTree instance to leverage utilities
    def makeTempTree(self, currentRoot, maxDepth=3):
        # Parameters for ArtificialTree
        depth = [0, maxDepth]
        degree_distr = {int(k): v for k, v in load_json_params("dists/degree.json").items()}
        fileType_distr = load_json_params("dists/typeDist.json")
        fileExt_distr = load_json_params("dists/filetypes.json")
        permissions_distr = {int(k, 8): v for k, v in load_json_params("dists/permissions.json").items()}
        size_distr = load_json_params("dists/size.json")
        timeRange = (int(time.time()) - 30*24*60*60, int(time.time()))
        # Generate
        tree = ArtificialTree(currentRoot, depth, degree_distr, size_distr, timeRange, fileType_distr, fileExt_distr, permissions_distr)
        return tree

    # Top function
    def modify_tree(self):
        print(f"Modifying folder {self.originalRoot}")
        # For each iteration
        for i in range(self.iterations):
            # Old root is original if just started, otherwise it is the previous root operated on
            oldRoot = self.originalRoot if i == 0 else self.newRootList[i-1]
            # Current path to operate on
            newRoot = self.newRootList[i]
            print(f"Making folder {newRoot}")
            # Remove junk tree if it exists
            if newRoot.exists():
                shutil.rmtree(newRoot)

            # Copy the old tree to the new one
            shutil.copytree(oldRoot, newRoot, symlinks=True)
            
            # Modify the tree with given parameters
            self.modify_recurse(newRoot, 0)

    # Recursively edit a tree
    def modify_recurse(self, root, files_made):
        localDepthAndFiles = max(1, int(math.log(max(2, self.maxNew))))
        # Iterate through direct children at this levels
        for entry in root.iterdir():
            if files_made < self.maxNew:
                # Folders
                if entry.is_dir():
                    # Delete based on probability
                    if ran.random() < self.editProbs["deleteFolder"]:
                        shutil.rmtree(entry)
                        continue
                    # If not deleted, recurse into the subdir
                    files_made += self.modify_recurse(entry, files_made)
                
                # Files
                elif entry.is_file():
                    # Randomly edit a file
                    if ran.random() < self.editProbs["editFile"]:
                        # Open and add data
                        try:
                            with open (entry, "a") as f:
                                size = ran.randint(500, 1000)
                                fileText = "".join(ran.choices(string.ascii_letters + string.digits, k=size))
                                f.write(fileText)
                        # Skip if permissions were set in a certain way
                        except PermissionError:
                            pass

                    # Randomly delete a file
                    elif ran.random() < self.editProbs["deleteFile"]:
                        entry.unlink()
            else:
                return files_made
        if files_made < self.maxNew: 
            # Creation of files and folders
            # Use an ArtificialTree object to leverage functionality
            tempTree = self.makeTempTree(root, localDepthAndFiles)
            
            # Create files - Max at a level is log of max new
            for _ in range(ran.randint(0, localDepthAndFiles)):
                if files_made >= self.maxNew:
                    break
                if ran.random() < self.editProbs["createFile"]:
                    # Build file path and type
                    fileExt = tempTree.sample_Extensions()
                    filePath = root / f"newfile_{ran.randint(0, 500)}{fileExt}"
                    # Write random data to the file
                    with open(filePath, "w") as f:
                        size = tempTree.sample_size()
                        fileText = "".join(ran.choices(string.ascii_letters + string.digits, k=size))
                        f.write(fileText)
                    files_made += 1

        if files_made < self.maxNew:
            # Create folders
            if ran.random() < self.editProbs["createFolder"]:
                files_made += tempTree.gen_tree_atlevel(localDepthAndFiles, root, max_files=max(0, self.maxNew - files_made))
        
        return files_made


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("""
This program modifies a mock file tree with pseudorandom files, subdirectories, and symlinks.

USAGE:

Modify a tree:
    python3 modify.py <original_name> <modified_name> <max_new_files> <iterations>

<original_name> = root of tree to modify
<modified_name> = name stem for new trees
<max_new_files> = most files to add to a new tree, avoid runaway generation
<iterations> = Number of times to generate a tree based on last successive one
            """)
        sys.exit(0)
    if len(args) < 4:
        print("Usage: python3 modify.py <original_name> <modified_name> <max_new_files> <iterations>")
        sys.exit(1)
    originalParam = sys.argv[1]
    modifyParam = sys.argv[2]
    newFilesParam = int(sys.argv[3])
    iterationsParam = int(sys.argv[4])

    modTree = ModifyTree(originalParam, modifyParam, newFilesParam, iterationsParam)
    modTree.modify_tree()
