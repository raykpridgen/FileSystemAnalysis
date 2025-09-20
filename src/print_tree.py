import tree_metrics as tm
import sys

if len(sys.argv) == 2:
    root = tm.fileSystem_to_zssNodes(sys.argv[1])
    tm.printNodeTree(root)

elif len(sys.argv) == 3 and sys.argv[2] == "-gufi":
    root = tm.GUFI_to_zssNodes(sys.argv[1])
    tm.printNodeTree(root)

elif len(sys.argv) == 3:
    root = tm.fileSystem_to_zssNodes(sys.argv[1])
    root2 = tm.fileSystem_to_zssNodes(sys.argv[2])
    tm.printNodeTree(root)
    print("===============================================================")
    tm.printNodeTree(root2)
elif len(sys.argv) == 4 and sys.argv[3] == "--gufi":
    root = tm.GUFI_to_zssNodes(sys.argv[1])
    root2 = tm.GUFI_to_zssNodes(sys.argv[2])
    tm.printNodeTree(root)
    print("===============================================================")
    tm.printNodeTree(root2)

else:
    print("Usage:\nprint_tree.py <root> [root2]\nor\nprint_tree.py <GUFI_index> [GUFI_index2] --gufi")

