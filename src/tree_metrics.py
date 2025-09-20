import os
import math
import zss
import sqlite3
from zss import Node



class FS_Node(Node):
    """
    A node representing a file or directory in a file system tree.

    Extends zss.Node to include file system metadata

    Attributes:
        label (str): Name of the file or directory.
        isDirectory (bool): True if the node is a directory, False if it's a file.
    """
    def __init__(self, label, isDirectory=True):
        super().__init__(label)
        self.isDirectory = isDirectory




def fileSystem_to_zssNodes(path):
    """
    Creates a tree data structure out of nodes.

    This function takes in a starting directory and constructs a tree with that directory acting as root.
    Nodes in the tree are generated with real file system data.

    :param path: The path to the root directory of the tree
    :type path: string
    :returns: The root node of the tree (FS_Node)
    :rtype: FS_Node
    """

    #Creating the root node
    rootNode = FS_Node(os.path.basename(path))

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
            leafNode = FS_Node(f"{name}", False)
            rootNode.addkid(leafNode)
    #Return the root node, or parent node in the case of recursive function calls
    return rootNode



def GUFI_to_zssNodes(GUFI_Path):
    """
    Creates a tree data structure out of nodes.

    This function takes in the starting directory of a GUFI index and constructs a tree with that directory acting as root.
    Nodes in the tree are generated with GUFI index data.

    :param GUFI_path: The path to the root directory of the GUFI index
    :type path: string
    :returns: The root node of the tree (FS_Node)
    :rtype: FS_Node
    """

    #Creating the root node
    rootNode = FS_Node(os.path.basename(GUFI_Path))

    #Parsing through the names of the dir/files in the passed in directory
    for name in os.listdir(GUFI_Path):
        #Ignoring macOS specific metadata files
        if name == ".DS_Store":
            continue
        #If the current name is tied to a directory...
        if os.path.isdir(f"{GUFI_Path}/{name}"):
            #Create a new parent node by recursively calling the function with the path to the directory
            #This lets you parse through subdirectories and files
            childNode = GUFI_to_zssNodes(f"{GUFI_Path}/{name}")

            ###Folder metadata would be gathered here with a sqlite3 connection to the .db file in the directory

            #Connect the new child node to the parent
            rootNode.addkid(childNode)
        #If the current name is tied to a file, it is a leaf node
        elif os.path.isfile(f"{GUFI_Path}/{name}"):
            #Simply create a leaf node and attach it to the parent
            try:
                conn = sqlite3.connect(f"{GUFI_Path}/{name}")
                cur = conn.cursor()
                #To fetch all data, SELECT * from entries
                cur.execute("SELECT name FROM entries")
                entries = cur.fetchall()
                #print(row)
                for file in entries:
                    if file[0] == ".DS_Store":
                        continue
                    leafNode = FS_Node(file[0], False)
                    rootNode.addkid(leafNode)
            except Exception as e:
                print(f"Skipping entries in {f"{GUFI_Path}/{name}"}: {e}")
    #Return the root node, or parent node in the case of recursive function calls
    return rootNode




def printNodeTree(root, level = 0):
    """
    Recursively prints a visual representation of the node tree.

    Each level of the tree is indented to reflect the depth of the node,
    with child nodes appearing under their parents.

    :param root: The root node of the tree.
    :type root: FS_Node
    :param level: The current depth in the tree (used for indentation). Defaults to 0.
    :type level: int
    :returns: None
    :rtype: None
    """
    #An indent is created to represent a deeper level of the tree
    #Root will always have no indent
    indent = "-----" * level
    #Printing the current node with corresponding indent
    print(f"{indent} {root.label}")
    #Iterating through the child nodes and recursively calling the function with an increased indent
    for child in root.children:
        printNodeTree(child, level + 1)



def countNodes(root):
    """
    Recursively counts all nodes (both files and directories) in the tree.

    :param root: The root node of the tree.
    :type root: FS_Node
    :returns: Total number of nodes in the tree.
    :rtype: int
    """
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
    """
    Computes the height (maximum depth) of the tree.

    The height is defined as the length of the longest path from the root
    node to any leaf node.

    :param root: The root node of the tree.
    :type root: FS_Node
    :returns: Height of the tree.
    :rtype: int
    """
    if not root.children:
        return 0
    else:
        return 1 + max(treeHeight(child) for child in root.children)
    

#Counts the number of leaf nodes (node with no children) of the passed in tree
def countLeaves(root):
    """
    Counts the number of leaf nodes (nodes with no children) in the tree.

    :param root: The root node of the tree.
    :type root: FS_Node
    :returns: Number of leaf nodes in the tree.
    :rtype: int
    """
    if root is None:
        return 0
    if root.children == [] or not root.isDirectory:
        return 1
    else:
        count = 0
        for child in root.children:
            count += countLeaves(child)
        return count