# Getting started
## Clone the repo
`git clone https://github.com/raykpridgen/FileSystemAnalysis`

## Move into the src directory
`cd FileSystemAnalysis/src`

## Install dependencies
`./make_venv.sh`

# Generating Filesystem Trees
treeGen.py is the script used to generate trees, located in the /src folder. This will generate a psuedorandom file tree using probabilities in JSON and input parameters. Commandline arguments are as follows:

## To generate a new tree in the /data folder
`python3 treeGen.py <name_of_root_directory> <minimum_depth> <maximum_depth>`

## Remove tree(s)
`python3 treeGen.py clean <root_name> <number_of_trees_to_remove>`

- If the number is set to 0, it will only remove 1 dir associated with the name passed.


# Mofifying Filesystem Trees
modify.py operates on an existing filesystem tree, modeling psuedorandom changes to a tree in time steps. This script may add, delete, or change files, folders, and symlinks based on probabilities provided via JSON.

`python3 modify.py <original_name> <modified_name> <max_new_files> <iterations>`

- First two inputs are the root to edit, and the name of the root to place the modified tree in
- max_new_files is the maximum number of files modify.py will add to the tree
- Iterations determines how many times this process will repeat. It will iterate using the same process, running a further iteration on the newly generated tree. 


# Gather metrics on the file trees
compare_trees.py takes in the two starting directories for your trees and gathers metrics which it then uses to compare the two trees.
Metrics gathered: tree edit distance, change in tree height, number of leaf nodes (nodes with no children)

To compare file system trees:

`python3 compare_trees.py <directory1> <directory2>`

To compare GUFI indexes:

`python3 compare_trees.py <GUFI_index1> <GUFI_index2> --gufi`

print_tree.py will display one or two trees for debugging purposes.

For file system trees:

`python3 print_tree.py <root> [root2]`

For GUFI index trees:

`python3 print_tree.py <GUFI_index> [GUFI_index2] --gufi`

If you need to install the zss library to run treeMetrics.py:

`pip3 install zss`
