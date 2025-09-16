import random
import os
import shutil
from pathlib import Path
import random as ran
import string
import sys
import random
import time
# CREATION TIME IMMUTABLE ON LINUX
# pywin32 TO MODIFY CREATION ON WINDOWS

# Permissions scheme
"""
Owner | Group | Others
r w x   r w x   r w x

r = 4
w = 2 
x = 1

Sum bits for each category

"""

# Basic params / structure for generation
"""
Attrs to model for GUFI

name
- vary name length?

type
- Regular files, dirs, symlinks, sockets/pipes
- extentions tied to size expectations

uid
- Pick from a pool of users, assign distributions to each user
gid
- set random groups?

size
- distribution param (many small + few big, etc)

access time
mod time
creation time
status change time
- FOR TIMES: crtime <= ctime <= mtime <= atime
- allow random but do not deviate from scheme, for logical creation
"""

# Use cases from GUFI
"""
- entry queries: find recently accessed files
- dir summaries: size, count, etc
- tree-summary: Full tree rollup

"""

degreeDistr = {
    0 : 0.10,
    1 : 0.17, 
    2 : 0.13, 
    3 : 0.11, 
    4 : 0.10,
    5 : 0.11, 
    6 : 0.09,
    7 : 0.06,
    8 : 0.05,
    9 : 0.05,
    10: 0.03,
               }

sizeDistr = {
    "small" : {"range": (0, 1_000), "prob": 0.55},
    "medium" : {"range": (1_000, 1_000_000), "prob": 0.40},
    "large" : {"range": (1_000_000, 500_000_000), "prob": 0.05},
}

filesDistr = {
    "file" : 0.62,
    "folder" : 0.36,
    "symlink" : 0.02,
}

class ArtificalTree:
    def __init__(self, rootName, maxDepth, degreeDist, sizeDist, timeRange, fileDist, filetypes, modeDist, users=1, groups=1):
        # String, name of root
        self.rootName = rootName
        # Fixed int, depth
        self.maxDepth = maxDepth
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
        self.filetypes = filetypes
        # Distribution of file permissions
        self.modeDist = modeDist
        # Number of users to own files
        self.users = users
        # Number of groups users inhabit
        self.groups = groups

    # Generate a random degree of a node from the dist
    def sample_degree(self):
        randomProb = random.random()
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

        selection = random.choices(sizeTypes, weights=probs, k=1)[0]
        print(f"Picked: {selection}")

        low, high = self.sizeDist[selection]["range"]
        size = random.randint(low, high)
        print(f"Size: {size}")
        return size

    # Generate random times for file within bounds
    def sample_time(self):
        # Get range
        start, end = self.timeRange
        # Pick random time within range for create
        crtime = random.randint(start, end)
        # Follow scheme for each succeeding time
        ctime = crtime + random.randint(0, 1000)
        mtime = ctime + random.randint(0, 1000)
        atime = mtime + random.randint(0, 1000)
        return atime, mtime, ctime, crtime

    # Generate a file type to create
    def sample_fileType(self):
        randomProb = random.random()
        cumulativeProb = 0
        # Dict looks like type : prob
        # Move through each prob
        for type, typeProb in self.degreeDist.items():
            # Sum probs for each child added
            cumulativeProb += typeProb
            # If prob surpasses distribution value for a child #, return as num of children
            if randomProb <= cumulativeProb:
                return type
        return 0
    
    # Clean up previous run with same name
    def clean_tree(self):
        # If root name already exists
        if os.path.exists(self.rootName):
            
            # If it is a file, remove
            if os.path.isfile(self.rootName):
                os.remove(self.rootName)
            
            # If name is a dir
            elif os.path.isdir(self.rootName):
                shutil.rmtree(self.rootName)

    # Generate random file extension
    # Generate tree from params
    def generate_tree(self):
        # Create root dir
        root = Path(self.rootName)
        root.mkdir(parents=True, exist_ok=True)

    # Generate at a level, utilize recursion
    def gen_tree_atlevel(self, depth):
        
        # Return if the depth is too far
        if (depth >= self.maxDepth):
            return
        
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
                fileNum += 1
            elif (childType == "folder"):
                folderNum += 1
            elif (childType == "symlink"):
                symlinkNum += 1

        




