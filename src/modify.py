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
from utils import getTimeInMs, parse_dist_params, parse_edit_params
SAVE_TO_DIR = "../data/"

class ModifyTree:
    def __init__(self, originalRoot, newRoot, maxNew, iterations):
        # Original root
        self.originalRoot = Path(f"{SAVE_TO_DIR}{originalRoot}")
        # Max new files to be added to the new tree
        self.maxNew = maxNew
        # Track files
        self.filesMade = 0
        # User mode
        self.userMode = True
        # Dict of edit probabilities
        if (self.userMode):
            self.editProbs = parse_edit_params("user_mode")
        else:
            self.editProbs = parse_edit_params()
        # Level of user home dirs
        self.userHome = self.editProbs["root"]
        print(self.userHome)
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
        degree_distr, fileType_distr, fileExt_distr, permissions_distr, size_distr = parse_dist_params()
        timeRange = (int(time.time()) - 30*24*60*60, int(time.time()))
        # Generate
        tree = ArtificialTree(currentRoot, depth, degree_distr, size_distr, timeRange, fileType_distr, fileExt_distr, permissions_distr)
        return tree

    # Top function
    def modify_tree(self):
        
        print(f"Modifying folder '{str(self.originalRoot)[8:]}'")
        # For each iteration
        for i in range(self.iterations):
            startModifyTime = time.perf_counter()
            # Old root is original if just started, otherwise it is the previous root operated on
            oldRoot = self.originalRoot if i == 0 else self.newRootList[i-1]
            # Current path to operate on
            newRoot = self.newRootList[i]
            print(f"Making folder: '{str(newRoot)[8:]}'")
            # Remove junk tree if it exists
            if newRoot.exists():
                shutil.rmtree(newRoot)

            # Copy the old tree to the new one
            shutil.copytree(oldRoot, newRoot, symlinks=True)
            
            # Modify the tree with given parameters
            if self.userMode:
                self.modify_recurse_user(newRoot, 0, 0)
            else:    
                self.modify_recurse(newRoot, 0, 0)
            endModifyTime = time.perf_counter()
            print(f"Modified tree '{str(oldRoot)[8:]}' in {getTimeInMs(startModifyTime, endModifyTime)} ms.")
            print(f"Made {self.filesMade} new files this iteration.\n")
            self.filesMade = 0
        
    # Recursively edit a tree
    def modify_recurse(self, root, files_made, current_depth):
        localDepthAndFiles = max(1, int(math.log(max(2, self.maxNew))))
        treeCreateDepth = self.editProbs["createDepth"]
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
                    
                    newfiles = self.modify_recurse(entry, files_made, current_depth+1)
                    files_made += newfiles
                    self.filesMade += newfiles
                
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
            tempTree = self.makeTempTree(root, treeCreateDepth)
            
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
                    self.filesMade += 1

        if files_made < self.maxNew:
            # Create folders
            if ran.random() < self.editProbs["createFolder"]:
                
                new_files = tempTree.gen_tree_atlevel(treeCreateDepth, root, max_files=max(0, self.maxNew - files_made))
                files_made += new_files
                self.filesMade += files_made
        
        return files_made

    def modify_recurse_user(self, root, files_made, current_depth):
        localDepthAndFiles = max(1, int(math.log(max(2, self.maxNew))))
        treeCreateDepth = self.editProbs["createDepth"]
        # Iterate through direct children at this levels
        for entry in root.iterdir():
            if files_made < self.maxNew:
                # Folders
                if entry.is_dir():
                    # Delete based on probability
                    if ran.random() < self.editProbs["deleteFolder"]  and self.userHome <= current_depth:
                        shutil.rmtree(entry)
                        continue
                    # If not deleted, recurse into the subdir
                    
                    newfiles = self.modify_recurse_user(entry, files_made, current_depth+1)
                    files_made += newfiles
                    self.filesMade += newfiles
                
                # Files
                elif entry.is_file() and self.userHome <= current_depth:
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
        
        if files_made < self.maxNew and self.userHome <= current_depth: 
            # Creation of files and folders
            # Use an ArtificialTree object to leverage functionality
            tempTree = self.makeTempTree(root, treeCreateDepth)
            
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

        if files_made < self.maxNew and self.userHome <= current_depth:
            # Create folders
            if ran.random() < self.editProbs["createFolder"]:
                
                newfiles = tempTree.gen_tree_atlevel(treeCreateDepth, root, max_files=max(0, self.maxNew - files_made))
                files_made += newfiles
                self.filesMade += newfiles
        
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
