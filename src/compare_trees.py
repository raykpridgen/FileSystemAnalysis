import tree_metrics as tm
import sys


if len(sys.argv) == 4 and sys.argv[3] == "--gufi":
    try:
        root = tm.GUFI_to_zssNodes(sys.argv[1])
        root2 = tm.GUFI_to_zssNodes(sys.argv[2])
        
        print(f"Tree before changes: {root.label} | Tree after changes: {root2.label}")
        print(f"Tree Edit Distance: {tm.zss.simple_distance(root, root2)}")
        print(f"Change in tree height: {(tm.treeHeight(root2)-tm.treeHeight(root)):+}")
        print(f"Change in number of leaf nodes: {(tm.countLeaves(root2)-tm.countLeaves(root)):+}")
    except Exception as e:
        print(f"Input Invalid: {e}\nUsage:\ncompare_trees.py <root1> <root2>\nor\ncompare_trees.py <GUFI_index1> <GUFI_index2> --gufi")



elif len(sys.argv) == 3:
    try:
        root = tm.fileSystem_to_zssNodes(sys.argv[1])
        root2 = tm.fileSystem_to_zssNodes(sys.argv[2])
        
        print(f"Tree before changes: {root.label} | Tree after changes: {root2.label}")
        print(f"Tree Edit Distance: {tm.zss.simple_distance(root, root2)}")
        print(f"Change in tree height: {(tm.treeHeight(root2)-tm.treeHeight(root)):+}")
        print(f"Change in number of leaf nodes: {(tm.countLeaves(root2)-tm.countLeaves(root)):+}")
    except Exception as e:
        print(f"Input Invalid: {e}\nUsage:\ncompare_trees.py <root1> <root2>\nor\ncompare_trees.py <GUFI_index1> <GUFI_index2> --gufi")


else:
    print("Usage:\ncompare_trees.py <root1> <root2>\nor\ncompare_trees.py <GUFI_index1> <GUFI_index2> --gufi")
