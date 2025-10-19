import tree_metrics as tm
import sys


def compare_FS_trees(path1, path2):
    """
    Takes in the starting directories of two file system trees and returns
    a list of metrics that represent the changes from tree 1 to tree 2.

    The trees are converted into in-memory node trees of type FS_Node,
    which is an override of the zss library Node class. These trees are then
    compared and the metrics are appended to a list, which is returned by this
    function.

    Args:
        path1 (string): The path to the root directory of the first file system tree.
        path2 (string): The path to the root directory of the second file system tree.

    Returns:
        list: A list of metrics of type int. These metrics are gathered by comparing the 
        changes from the first tree to the second tree. The list of metrics is in the form
        of:
        [Tree Edit Distance, Change in tree height, Change in leaf node amount]
    """
    root = tm.fileSystem_to_zssNodes(path1)
    root2 = tm.fileSystem_to_zssNodes(path2)
    metrics = []

    metrics.append(tm.zss.simple_distance(root, root2))
    metrics.append((tm.treeHeight(root2)-tm.treeHeight(root)))
    metrics.append((tm.countLeaves(root2)-tm.countLeaves(root)))
    
    return metrics


def compare_GUFI_indexes(path1, path2):
    """
    Takes in the starting directories of two GUFI indexes and returns
    a list of metrics that represent the changes from tree 1 to tree 2.

    The indexes are converted into in-memory node trees of type FS_Node,
    which is an override of the zss library Node class. These trees are then
    compared and the metrics are appended to a list, which is returned by this
    function.

    Args:
        path1 (string): The path to the root directory of the first file system tree.
        path2 (string): The path to the root directory of the second file system tree.

    Returns:
        list: A list of metrics of type int. These metrics are gathered by comparing the 
        changes from the first tree to the second tree. The list of metrics is in the form
        of:
        [Tree Edit Distance, Change in tree height, Change in leaf node amount]
    """
    root = tm.GUFI_to_zssNodes(path1)
    root2 = tm.GUFI_to_zssNodes(path2)
    metrics = []

    metrics.append(tm.zss.simple_distance(root, root2))
    metrics.append((tm.treeHeight(root2)-tm.treeHeight(root)))
    metrics.append((tm.countLeaves(root2)-tm.countLeaves(root)))
    
    return metrics


if __name__ == "__main__":

    if len(sys.argv) == 6 and sys.argv[4] == "-r" and sys.argv[3] == "--gufi":
        try:
            root = tm.GUFI_to_zssNodes(sys.argv[1])
            root2 = tm.GUFI_to_zssNodes(sys.argv[2])

            with open(sys.argv[5], "a") as f:
                f.write(f"{tm.zss.simple_distance(root, root2)} {(tm.treeHeight(root2)-tm.treeHeight(root)):+} {(tm.countLeaves(root2)-tm.countLeaves(root)):+}\n")

        except Exception as e:
            print(f"Input Invalid: {e}\nUsage:\ncompare_trees.py <root1> <root2>\nor\ncompare_trees.py <GUFI_index1> <GUFI_index2> --gufi")



    elif len(sys.argv) == 5 and sys.argv[3] == "-r":
        try:
            root = tm.fileSystem_to_zssNodes(sys.argv[1])
            root2 = tm.fileSystem_to_zssNodes(sys.argv[2])

            with open(sys.argv[4], "a") as f:
                f.write(f"{tm.zss.simple_distance(root, root2)} {(tm.treeHeight(root2)-tm.treeHeight(root)):+} {(tm.countLeaves(root2)-tm.countLeaves(root)):+}\n")
                
        except Exception as e:
            print(f"Input Invalid: {e}\nUsage:\ncompare_trees.py <root1> <root2>\nor\ncompare_trees.py <GUFI_index1> <GUFI_index2> --gufi")
    
    
    elif len(sys.argv) == 5 and sys.argv[4] == "-r" and sys.argv[3] == "--gufi":
        try:
            root = tm.GUFI_to_zssNodes(sys.argv[1])
            root2 = tm.GUFI_to_zssNodes(sys.argv[2])
            
            print(f"{tm.zss.simple_distance(root, root2)}")
            print(f"{(tm.treeHeight(root2)-tm.treeHeight(root)):+}")
            print(f"{(tm.countLeaves(root2)-tm.countLeaves(root)):+}")
        except Exception as e:
            print(f"Input Invalid: {e}\nUsage:\ncompare_trees.py <root1> <root2>\nor\ncompare_trees.py <GUFI_index1> <GUFI_index2> --gufi")


    elif len(sys.argv) == 4 and sys.argv[3] == "-r":
        try:
            root = tm.fileSystem_to_zssNodes(sys.argv[1])
            root2 = tm.fileSystem_to_zssNodes(sys.argv[2])
            
            print(f"{tm.zss.simple_distance(root, root2)}")
            print(f"{(tm.treeHeight(root2)-tm.treeHeight(root)):+}")
            print(f"{(tm.countLeaves(root2)-tm.countLeaves(root)):+}")
        except Exception as e:
            print(f"Input Invalid: {e}\nUsage:\ncompare_trees.py <root1> <root2>\nor\ncompare_trees.py <GUFI_index1> <GUFI_index2> --gufi")


    elif len(sys.argv) == 4 and sys.argv[3] == "--gufi":
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
