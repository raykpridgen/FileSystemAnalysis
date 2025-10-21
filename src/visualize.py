import os
import sys
from pathlib import Path
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from utils import getTimeInMs
import time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class TreeVisualizer:
    def __init__(self, rootA, rootB=None, fileSavePath="output", timing=True, savePath="../report/images/", pullPath="../data/"):
        # Validate paths
        if not os.path.exists(pullPath + rootA):
            print(f"Root path does not exist: {pullPath + rootA}")
            raise FileNotFoundError(f"Error")
        
        # Handle parent script sending blank output for file save name
        if fileSavePath == "":
            fileSavePath = rootA + "_plot"

        # Assign paths and build adjacency representation
        self.fileSavePath = savePath + fileSavePath + ".png"
        self.rootA = Path(pullPath + rootA).resolve()
        self.timing = timing

        startAdjA = time.perf_counter() if self.timing else None
        self.graphA, self.metaA = self.build_adjacency_graph(self.rootA)
        endAdjA = time.perf_counter() if self.timing else None
        if self.timing:
            #print(f"Built adjacency graph for {rootA} in {getTimeInMs(startAdjA, endAdjA)} ms")
            pass
        
        if rootB:
            if not os.path.exists(pullPath + rootB):
                raise FileNotFoundError(f"Root path does not exist: {rootB}")
            self.rootB = Path(pullPath + rootB).resolve()
            startAdjB = time.perf_counter() if self.timing else None
            self.graphB, self.metaB = self.build_adjacency_graph(self.rootB)
            endAdjB = time.perf_counter() if self.timing else None
            if self.timing:
                #print(f"Built adjacency graph for {rootB} in {getTimeInMs(startAdjB, endAdjB)} ms")
                pass
        
        # Generate and save visualization
        if hasattr(self, "graphB"):
            self.visualize_comparison()
        else:
            self.visualize_single_tree()

    def walk(self, current: Path, graph, metadata, root: Path):
        """Recursively build adjacency dictionary { parent: [children] } using relative paths."""
        current_key = str(current.relative_to(root)).lower()
        graph[current_key] = []
        
        # Metadata for current folder node 
        metadata[current_key] = {
            'is_dir': current.is_dir(),
            'mtime': current.stat(follow_symlinks=False).st_mtime if current.exists() else None,
            'size': current.stat(follow_symlinks=False).st_size if current.is_file() else None,
        }
        
        for entry in sorted(os.listdir(current)):
            full_path = current / entry
            child_key = str(full_path.relative_to(root)).lower()
            graph[current_key].append(child_key)
            if full_path.is_dir():
                self.walk(full_path, graph, metadata, root)
            # Establish metadata and graph position for child
            else:
                graph[child_key] = []
                metadata[child_key] = {
                "is_dir": False,
                "mtime": full_path.stat(follow_symlinks=False).st_mtime,
                "size": full_path.stat(follow_symlinks=False).st_size,
                }

    def build_adjacency_graph(self, path_to_walk):
        graph = {}
        metadata = {}
        self.walk(path_to_walk, graph, metadata, path_to_walk)
        return graph, metadata

    def merge_graphs(self):
        G = nx.DiGraph()
        for parent, children in self.graphA.items():
            for child in children:
                G.add_edge(parent, child, source="A")

        if hasattr(self, "graphB"):
            for parent, children in self.graphB.items():
                for child in children:
                    if G.has_edge(parent, child):
                        G.edges[parent, child]["source"] = "both"
                    else:
                        G.add_edge(parent, child, source="B")

        # Include metadata for nodes to see mod time
        for key in set(self.metaA.keys()).union(self.metaB.keys()):
            a = self.metaA.get(key)
            b = self.metaB.get(key)
            if a and b:
                changed = a["mtime"] != b["mtime"]
            else:
                changed = False
            G.add_node(
                key, 
                changed=changed, 
                mtimeA=a["mtime"] if a else None,
                mtimeB=b["mtime"] if b else None
                )
            
        return G
    
    def visualize_single_tree(self):
        """Render a single directory tree as an interactive HTML visualization."""
        startVisSingle = time.perf_counter() if self.timing else None
        G = nx.DiGraph()
        for parent, children in self.graphA.items():
            for child in children:
                G.add_edge(parent, child)

        try:
            # Increase node and rank separation for better spacing
            pos = graphviz_layout(
                G,
                prog="dot",
                args="-Grankdir=LR -Gnodesep=5 -Granksep=5")
            
            print("Using graphviz")
        except Exception:
            # Increase k for more spacing in spring layout
            pos = nx.spring_layout(G, seed=42, k=0.5)
            print("Using spring")


        node_colors = []
        for node in G.nodes():
            abs_path = self.rootA / node
            node_colors.append("darkblue" if os.path.isdir(abs_path) else "lightblue")

        plt.figure(figsize=(12, 9))

        nx.draw_networkx_edges(G, pos, edge_color="black")

        nx.draw_networkx_nodes(
            G, pos,
            node_color=node_colors,
            node_size=100,
            edgecolors="darkslategray",
            linewidths=1,
        )

        ys = [y for x, y in pos.values()]
        y_range = max(ys) - min(ys)
        offset = y_range * 0.025
        labels = {node: Path(node).name for node in G.nodes()}
        label_positions = {node: (x, y + offset) for node, (x, y) in pos.items()}

        '''
        nx.draw_networkx_labels(
            G,
            label_positions,
            labels,
            font_size=8,
            horizontalalignment='center',
            bbox=dict(
                boxstyle='round,pad=0.2',  # rounded box with a bit of padding
                facecolor='white',          # fill color
                edgecolor='black',          # border color
                alpha=0.9                   # transparency
            )
        )
        '''
        plt.axis("off")
        plt.title("Directory Tree")

        plt.tight_layout()

        if os.path.isfile(self.fileSavePath):
                os.remove(self.fileSavePath)
                print("Removed old file.")
        plt.savefig(self.fileSavePath, format="png", dpi=300)
        plt.close()
        
        endVisSingle = time.perf_counter() if self.timing else None
        if self.timing:
            print(f"Visualized and saved figure for a single graph in {getTimeInMs(startVisSingle, endVisSingle)} ms")

    def visualize_comparison(self):
        startComparison = time.perf_counter() if self.timing else None
        """Render a comparison of two directory trees as an interactive HTML visualization."""
        G = self.merge_graphs()

        try:
            # Increase node and rank separation for better spacing
            pos = graphviz_layout(
                G,
                prog="dot",
                args="-Grankdir=LR -Gnodesep=0.5 -Granksep=0.5")
       
        except Exception:
            # Increase k for more spacing in spring layout
            pos = nx.spring_layout(G, seed=42, k=0.5)

        node_colors = []
        for node in G.nodes():
            in_A = node in self.graphA
            in_B = node in self.graphB
            abs_path = self.rootA / node if in_A else self.rootB / node
            is_dir = os.path.isdir(abs_path)
            # No change
            if in_A and in_B:
                if G.nodes[node].get("changed") and not is_dir:
                    node_colors.append("yellow")
                else:
                    node_colors.append("darkblue" if is_dir else "lightblue")
            
            # Added
            elif in_B:
                node_colors.append("darkgreen" if is_dir else "lightgreen")
            
            # Removed
            else:
                node_colors.append("darkred" if is_dir else "salmon")

        edge_colors = []
        for src, dst in G.edges():
            abs_path = self.rootA / dst
            in_A_edge = src in self.graphA and dst in self.graphA[src]
            in_B_edge = src in self.graphB and dst in self.graphB[src]
            # No change
            if in_A_edge and in_B_edge:
                edge_colors.append("black")
            
            # Added
            elif in_B_edge:
                edge_colors.append("lightgreen")
            
            # Removed
            else:
                edge_colors.append("salmon")
        
        # For legend
        folder_patch = mpatches.Patch(color='darkblue', label='Folder')
        file_patch = mpatches.Patch(color='lightblue', label='File')
        add_folder_patch = mpatches.Patch(color='darkgreen', label='New Folder')
        add_file_patch = mpatches.Patch(color='lightgreen', label='New File')
        remove_folder_patch = mpatches.Patch(color='darkred', label='Removed Folder')
        remove_file_patch = mpatches.Patch(color='salmon', label='Removed Folder')
        edited_patch = mpatches.Patch(color='yellow', label="Modified File")
        
        plt.figure(figsize=(12, 9))
        plt.legend(
            handles=[folder_patch, file_patch, add_folder_patch, add_file_patch, remove_folder_patch, remove_file_patch, edited_patch],
            loc='upper right',
            frameon=True,
            framealpha=0.9,
            title='Color Scheme'
        )

        nx.draw_networkx_edges(
            G,
            pos,
            edge_color=edge_colors,
            width=1
            )
        
        nx.draw_networkx_nodes(
            G,
            pos,
            node_color=node_colors,
            edgecolors="darkslategray",
            linewidths=0.3,
            node_size=100
        )

        ys = [y for x, y in pos.values()]
        y_range = max(ys) - min(ys)
        offset = y_range * 0.025
        labels = {node: Path(node).name for node in G.nodes()}
        label_positions = {node: (x, y + offset) for node, (x, y) in pos.items()}

        '''
        nx.draw_networkx_labels(
            G,
            label_positions,
            labels,
            font_size=6,
            horizontalalignment='center',
            bbox=dict(
                boxstyle='round,pad=0.2',  # rounded box with a bit of padding
                facecolor='white',          # fill color
                edgecolor='black',          # border color
                alpha=0.9                   # transparency
            )
        )
        '''

        plt.axis("off")
        plt.title("Directory Tree")
        plt.tight_layout()

        if os.path.isfile(self.fileSavePath):
                os.remove(self.fileSavePath)
                print("Removed old file.")
        plt.savefig(self.fileSavePath, format="png", dpi=300)
        plt.close()

        endComparison = time.perf_counter() if self.timing else None
        if self.timing:
            print(f"Visualized and saved figure for two graphs in {getTimeInMs(startComparison, endComparison)} ms")

if __name__ == "__main__":
    if sys.argv[1] == "visual" and len(sys.argv) == 4:
        TreeVisualizer(sys.argv[2], rootB=None, fileSavePath=sys.argv[3])
    elif sys.argv[1] == "compare" and len(sys.argv) == 5:
        TreeVisualizer(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Usage: python3 visualize.py visual <root_name> <save_path>")
        print("Usage: python3 visualize.py compare <original_root_name> <compare_root_name> <save_path>")