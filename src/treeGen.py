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
    0 : 0.15,
    1 : 0.17, 
    2 : 0.13, 
    3 : 0.14, 
    4 : 0.05,
    5 : 0.08, 
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

fileExtensions = [".txt", ".csv", ".json", ".log", ".md", ".xml"]
permDist = {
    0o666 : 0.55,
    0o644 : 0.25,
    0o444 : 0.15,
    0o744 : 0.05,
}
permissions = [0o444, 0o644, 0o666, 0o744]


    
# Clean up previous run with same name
def clean_tree(rootName):
        # If root name already exists
        if os.path.exists(rootName):
            
            # If it is a file, remove
            if os.path.isfile(rootName):
                os.remove(rootName)
            
            # If name is a dir
            elif os.path.isdir(rootName):
                shutil.rmtree(rootName)

class ArtificialTree:
    def __init__(self, rootName, depthRange, degreeDist, sizeDist, timeRange, fileDist, filetypes, modeDist, users=1, groups=1):
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
        self.filetypes = filetypes
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

        low, high = self.sizeDist[selection]["range"]
        size = random.randint(low, high)
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
        for type, typeProb in self.fileDist.items():
            # Sum probs for each child added
            cumulativeProb += typeProb
            # If prob surpasses distribution value for a child #, return as num of children
            if randomProb <= cumulativeProb:
                return type
        return 0
    
    def sample_Extensions(self):
        return random.choice(self.filetypes)

    def sample_permissions(self):
        randomProb = random.random()
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
        clean_tree(root)
        root.mkdir(parents=True, exist_ok=True)
        os.chmod(root, 0o755)
        self.gen_tree_atlevel(0, root)


    # Generate at a level, utilize recursion
    def gen_tree_atlevel(self, depth, root):
        
        # Return if the depth is too far
        if (depth >= self.depthRange[1]):
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

        if depth < self.depthRange[0] and folderNum == 0:
            folderNum = 1
            if fileNum > 0:
                fileNum -= 1

        # Folders
        for i in range(0, folderNum):
            # Attach root/node_depth_num
            sub = root / f"folder{depth}_{i}"
            sub.mkdir(parents=True, exist_ok=True)
            self.filesCreated.append(sub)
            self.currentMaxDepth += 1
            # RECURSION HERE
            # Recurse if min is not met, or if it has on a prob
            if depth < self.depthRange[0]:
                self.gen_tree_atlevel(depth+1, sub)
            elif random.random() < 0.4:
                self.gen_tree_atlevel(depth+1, sub)

        # Files
        for i in range(0, fileNum):
            # Make file
            filePath = root / f"file_{depth}_{i}{self.sample_Extensions()}"
            filePath.touch()
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
                target = random.choice(self.filesCreated)
                linkPath = root / f"symlink_{depth}_{i}_{random.randint(0, 9999)}"
                try:
                    os.symlink(target, linkPath)
                except FileExistsError:
                    pass
        


# Args: root name, degree min and max
if len(sys.argv) < 2:
    print("Usage: python3 treeGen.py <root_name> <minDepth> <maxDepth>")
    print("Usage: python3 treeGen.py clean <rootName> --> to clean")
    sys.exit(1)

# Handle clean case
if sys.argv[1] == "clean":
    if len(sys.argv) < 3:
        print("Usage: python3 treeGen.py clean <rootName>")
        sys.exit(1)
    clean_tree(sys.argv[2])
    print("Removed tree.")
    sys.exit(0)

# Otherwise, generate a new tree
if len(sys.argv) < 4:
    print("Usage: python3 treeGen.py <root_name> <minDepth> <maxDepth>")
    sys.exit(1)

rootName = sys.argv[1]
depthRange = [int(sys.argv[2]), int(sys.argv[3])]
timeRange = (int(time.time()) - 30*24*60*60, int(time.time()))

newTree = ArtificialTree(rootName, depthRange, degreeDistr, sizeDistr, timeRange, filesDistr, fileExtensions, permDist)
newTree.generate_tree()