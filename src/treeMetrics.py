import os
import math
import zss
from zss import Node
import sys


class customNode(Node):
    def __init__(self, label, isDirectory=True):
        super().__init__(label)
        self.isDirectory = isDirectory


def fileSystem_to_zssNodes(path):

    #Creating the root node
    rootNode = customNode(os.path.basename(path))

    #Parsing through the names of the dir/files in the passed in directory
    for name in os.listdir(path):
        #Ignoring macOS specific metadata files
        if name == ".DS_Store":
            continue
        #If the current name is tied to a directory...
        if os.path.isdir(f"{path}/{name}"):
            #Create a new parent node by recursively calling the function with the path to the directory
            #This lets you parse through subdirectories and files
            childNode = fileSystem_to_zssNodes(f"{path}/{name}")
            #Connect the new child node to the parent
            rootNode.addkid(childNode)
        #If the current name is tied to a file, it is a leaf node
        elif os.path.isfile(f"{path}/{name}"):
            #Simply create a leaf node and attach it to the parent
            leafNode = customNode(f"{name}", False)
            rootNode.addkid(leafNode)
    #Return the root node, or parent node in the case of recursive function calls
    return rootNode


def printNodeTree(root, level = 0):
    #An indent is created to represent a deeper level of the tree
    #Root will always have no indent
    indent = "-----" * level
    #Printing the current node with corresponding indent
    print(f"{indent} {root.label}")
    #Iterating through the child nodes and recursively calling the function with an increased indent
    for child in root.children:
        printNodeTree(child, level + 1)


#Function that counts all nodes in a tree
def countNodes(root):
    if root is None:
        return 0
    else:
        count = 1
        for child in root.children:
            count += countNodes(child)
        return count


def averageDirectoryWidth(root):
    #Counting all children of directories
    totalChildren = 0
    #Total number of directories
    if not root.isDirectory:
        return 0
    else:
        totalChildren += len(root.children)
        countDirectory = 1
        for child in root.children:
            if child.isDirectory:
                countDirectory += 1
                totalChildren += averageDirectoryWidth(child)
    return totalChildren/countDirectory

#Returns the height of the tree (longest path from root to leaf node)
def treeHeight(root):
    if not root.children:
        return 0
    else:
        return 1 + max(treeHeight(child) for child in root.children)
    

#Counts the number of leaf nodes (node with no children) of the passed in tree
def countLeaves(root):
    if root is None:
        return 0
    if root.children == [] or not root.isDirectory:
        return 1
    else:
        count = 0
        for child in root.children:
            count += countLeaves(child)
        return count

#------------------------------------------------------------------------------------------#

if len(sys.argv) == 4 and sys.argv[3].lower() == "tree":
    
    root = fileSystem_to_zssNodes(sys.argv[1])
    root2 = fileSystem_to_zssNodes(sys.argv[2])
    
    printNodeTree(root)
    print("-----------------------------------------------------")
    printNodeTree(root2)
    print("__________________________")

    print(f"Tree before changes: {root.label} | Tree after changes: {root2.label}")
    print(f"Tree Edit Distance: {zss.simple_distance(root, root2)}")
    print(f"Change in tree height: {(treeHeight(root2)-treeHeight(root)):+}")
    print(f"Change in number of leaf nodes: {(countLeaves(root2)-countLeaves(root)):+}")

elif len(sys.argv) == 3:
    root = fileSystem_to_zssNodes(sys.argv[1])
    root2 = fileSystem_to_zssNodes(sys.argv[2])
    
    print(f"Tree before changes: {root.label} | Tree after changes: {root2.label}")
    print(f"Tree Edit Distance: {zss.simple_distance(root, root2)}")
    print(f"Change in tree height: {(treeHeight(root2)-treeHeight(root)):+}")
    print(f"Change in number of leaf nodes: {(countLeaves(root2)-countLeaves(root)):+}")


else:
    print("Please enter the path to the first and second tree, separated by a space.\nEx: python3 ./TreeMetrics.py root root2")
