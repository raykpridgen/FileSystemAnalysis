# Getting started
## Clone the repo
`git clone https://github.com/raykpridgen/FileSystemAnalysis`

## Move into the src directory
`cd FileSystemAnalysis/src`


# Making file trees
trees.py makes a tree with parameters <root_name> <depth> <degree>
Depth is how far the subdirs go, degree is how many files / folders are at each level (with randomness)

`python3 trees.py <root_name> <depth> <degree>`


modify.py makes changes to an initial tree, with iterations possible
first two are names, max_new is the max number of files the program will add, delete prob is the probability it will delete a file or folder, edit prob is the probability it will edit a given file, create prob is the probability it will make a file or folder, and iterations is how many changed trees to generate, operating off of the last edited tree to generate the next one.

`python3 modify.py <original_name> <modified_name> <max_new_files> <delete_prob> <edit_prob> <create_prob> <iterations>`


clean.py removes any dirs to streamline work
<dir_to_remove> is the name of the folder to remove, <dirs_to_remove> selects how to remove. If it is 0, it will remove the one dir, but greater than 0 will remove all dirs made with the scheme used by modify.py. So an example might be to remove the original dir with <dirs_to_remove> = 0, and then run with <> = 3 to remove 3 modified iterations.

`python3 clean.py <dir_to_remove> <dirs_to_remove>`



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
