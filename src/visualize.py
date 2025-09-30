import os
import sys
import shutil
from pathlib import Path
import igraph as ig
import plotly.graph_objects as go
import time

class TreeVisualizer:
    def __init__(self, rootName, fileSavePath):
        # Error for invalid root
        if not os.path.exists(rootName):
            raise FileNotFoundError(f"Root path does not exist: {rootName}")
        # Error for save path
        if not os.path.isdir(fileSavePath) and not fileSavePath.endswith(".html"):
            raise ValueError("save path should be a .html file or a folder")
        
        self.rootName = rootName
        self.fileSavePath = fileSavePath
        self.rootPath = Path(rootName)
        self.nestedGraph = self.build_adjacency_graph()
        self.graphObj = self.graph_from_dict()
        self.igraph_to_plotly()
    
    # Walk a path to help build a dict
    def walk(self, current: Path, graph):
        current_key = str(current.resolve())
        # Key : Values == Dir Name : List of children
        graph[current_key] = []
        # For each entry
        for entry in sorted(os.listdir(current)):
            # Attach full path
            full_path = current / entry
            # Append to dict 
            child_key = str(full_path.resolve())
            graph[current_key].append(child_key)
            # If entry is a dir, recurse
            if full_path.is_dir():
                self.walk(full_path, graph)
            # Or append a leaf
            else:
                graph[child_key] = []

    # Build a graph from a file hierarchy
    def build_adjacency_graph(self):
        graph = {}
        self.walk(self.rootPath, graph)
        return graph

    # Construct an igraph graph
    def graph_from_dict(self):
        # List for the edges of the graph
        edges = []
        # For a parent key and a list value
        for parent, childList in self.nestedGraph.items():
            # For each leaf in the list value
            for edge in childList:
                # Add edge as tuple
                edges.append((parent, edge))

        # Make the graph object and add values
        graph = ig.Graph(directed=True)
        vertex_ids = list(self.nestedGraph.keys())
        labels = [Path(v).name for v in vertex_ids]
        graph.add_vertices(list(self.nestedGraph.keys()))
        graph.vs["id"] = vertex_ids
        graph.vs["label"] = labels
        graph.add_edges(edges)

        return graph

    def assign_positions(self):
        pos = {}
        levels = {}  # dict: node -> depth

        def dfs_dict(node_name, current_dict, depth=0):
            levels[node_name] = depth
            for child in current_dict.get(node_name, []):
                dfs_dict(child, current_dict, depth + 1)
        root_key = str(self.rootPath.resolve())
        dfs_dict(root_key, self.nestedGraph)
        
        # Spread nodes horizontally per level
        max_width_per_level = {d: 0 for d in set(levels.values())}
        for node, depth in levels.items():
            max_width_per_level[depth] += 1

        # Assign x, y coordinates
        level_count = {}
        for node, depth in levels.items():
            idx = level_count.get(depth, 0)
            total = max_width_per_level[depth]
            x = idx / (total - 1) if total > 1 else 0.5
            y = -depth  # top-down
            pos[node] = (x, y)
            level_count[depth] = idx + 1

        return pos

    def igraph_to_plotly(self):
        pos = self.assign_positions()
        vertex_names = list(self.nestedGraph.keys())
        layout_coords = [pos[vertex_names[i]] for i in range(len(vertex_names))]    

        # Extract coordinates
        x_nodes = [pos[v["id"]][0] for v in self.graphObj.vs]
        y_nodes = [pos[v["id"]][1] for v in self.graphObj.vs]
        

        # Build edge coordinates
        edge_x = []
        edge_y = []
        for edge in self.graphObj.get_edgelist():
            x0, y0 = layout_coords[edge[0]]
            x1, y1 = layout_coords[edge[1]]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

        # Create Plotly traces
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            mode="lines",
            hoverinfo="none"
        )

        node_trace = go.Scatter(
            x=x_nodes, y=y_nodes,
            mode="markers+text",
            text = [v["label"] for v in self.graphObj.vs],
            textposition="top center",
            hoverinfo="text"
        )

        figure = go.Figure(data=[edge_trace, node_trace])
        figure.update_layout(showlegend=False)
        figure.write_html(f"{self.fileSavePath}", auto_open=False)

# Main code when calling file directly
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 visualize.py <root_name> <save_path>")
    else:
        TreeVisualizer(sys.argv[1], sys.argv[2])
