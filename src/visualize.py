import os
import sys
from pathlib import Path
import plotly.graph_objects as go
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from utils import getTimeInMs
import time

class TreeVisualizer:
    def __init__(self, rootA, rootB=None, fileSavePath="output", timing=False):
        # Validate paths
        if not os.path.exists(rootA):
            raise FileNotFoundError(f"Root path does not exist: {rootA}")
        if not os.path.isdir(fileSavePath) and not fileSavePath.endswith(".html"):
            fileSavePath += ".html"

        # Assign paths and build adjacency representation
        self.fileSavePath = fileSavePath
        self.rootA = Path(rootA).resolve()
        self.timing = timing

        startAdjA = time.perf_counter() if self.timing else None
        self.graphA = self.build_adjacency_graph(self.rootA)
        endAdjA = time.perf_counter() if self.timing else None
        if self.timing:
            print(f"Built adjacency graph for {rootA} in {getTimeInMs(startAdjA, endAdjA)} ms")
        
        if rootB:
            if not os.path.exists(rootB):
                raise FileNotFoundError(f"Root path does not exist: {rootB}")
            self.rootB = Path(rootB).resolve()
            startAdjB = time.perf_counter() if self.timing else None
            self.graphB = self.build_adjacency_graph(self.rootB)
            endAdjB = time.perf_counter() if self.timing else None
            if self.timing:
                print(f"Built adjacency graph for {rootB} in {getTimeInMs(startAdjB, endAdjB)} ms")
        
        # Generate and save visualization
        if hasattr(self, "graphB"):
            self.visualize_comparison()
        else:
            self.visualize_single_tree()

    def walk(self, current: Path, graph, root: Path):
        """Recursively build adjacency dictionary { parent: [children] } using relative paths."""
        current_key = str(current.relative_to(root)).lower()
        graph[current_key] = []
        for entry in sorted(os.listdir(current)):
            full_path = current / entry
            child_key = str(full_path.relative_to(root)).lower()
            graph[current_key].append(child_key)
            if full_path.is_dir():
                self.walk(full_path, graph, root)
            else:
                graph[child_key] = []

    def build_adjacency_graph(self, path_to_walk):
        graph = {}
        self.walk(path_to_walk, graph, path_to_walk)
        return graph

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
            pos = graphviz_layout(G, prog="dot", args="-Grankdir=LR -Gnodesep=0.5 -Granksep=0.5")
        except Exception:
            # Increase k for more spacing in spring layout
            pos = nx.spring_layout(G, seed=42, k=0.5)

        node_x, node_y, node_text = [], [], []
        edge_x, edge_y = [], []

        for node in G.nodes():
            x, y = pos[node]
            abs_path = self.rootA / node
            is_dir = os.path.isdir(abs_path)
            label = Path(node).name
            node_x.append(x)
            node_y.append(y)
            node_text.append(label)

        for src, dst in G.edges():
            x0, y0 = pos[src]
            x1, y1 = pos[dst]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            mode="lines",
            hoverinfo="none",
            line=dict(color="black"),
            name="Edges"
        )

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode="markers",
            name="Nodes",
            hoverinfo="text",
            hovertext=node_text,
            marker=dict(
                color=["darkblue" if os.path.isdir(self.rootA / node) else "lightblue" for node in G.nodes()],
                size=10,
                line=dict(width=1, color="darkslategray")
            )
        )

        figure = go.Figure(data=[edge_trace, node_trace])
        figure.update_layout(
            showlegend=True,
            legend=dict(itemsizing="constant", bgcolor="rgba(255,255,255,0.7)"),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            title="Directory Tree"
        )
        figure.write_html(f"{self.fileSavePath}", auto_open=False)
        endVisSingle = time.perf_counter() if self.timing else None
        if self.timing:
            print(f"Visualized and saved figure for a single graph in {getTimeInMs(startVisSingle, endVisSingle)} ms")

    def visualize_comparison(self):
        startComparison = time.perf_counter() if self.timing else None
        """Render a comparison of two directory trees as an interactive HTML visualization."""
        G = self.merge_graphs()

        try:
            # Increase node and rank separation for better spacing
            pos = graphviz_layout(G, prog="dot", args="-Grankdir=LR -Gnodesep=0.5 -Granksep=0.5")
        except Exception:
            # Increase k for more spacing in spring layout
            pos = nx.spring_layout(G, seed=42, k=0.5)

        common_x, common_y, common_text = [], [], []
        added_x, added_y, added_text = [], [], []
        removed_x, removed_y, removed_text = [], [], []

        common_count = added_count = removed_count = 0
        sample_common = sample_added = sample_removed = None

        for node in G.nodes():
            x, y = pos[node]
            in_A = node in self.graphA
            in_B = node in self.graphB
            abs_path = self.rootA / node if in_A else self.rootB / node
            is_dir = os.path.isdir(abs_path)
            if in_A and in_B:
                color = "darkblue" if is_dir else "lightblue"
                label = f"{Path(node).name} (common)"
                common_x.append(x)
                common_y.append(y)
                common_text.append(label)
                common_count += 1
                if not sample_common:
                    sample_common = node
            elif in_B:
                color = "darkgreen" if is_dir else "lightgreen"
                label = f"{Path(node).name} (added)"
                added_x.append(x)
                added_y.append(y)
                added_text.append(label)
                added_count += 1
                if not sample_added:
                    sample_added = node
            else:
                color = "darkred" if is_dir else "salmon"
                label = f"{Path(node).name} (removed)"
                removed_x.append(x)
                removed_y.append(y)
                removed_text.append(label)
                removed_count += 1
                if not sample_removed:
                    sample_removed = node

        edge_traces = []
        edge_x_common, edge_y_common = [], []
        edge_x_added, edge_y_added = [], []
        edge_x_removed, edge_y_removed = [], []

        common_edge_count = added_edge_count = removed_edge_count = 0

        for src, dst in G.edges():
            x0, y0 = pos[src]
            x1, y1 = pos[dst]
            source = G.edges[src, dst].get("source", "A")
            if source == "both":
                edge_x_common += [x0, x1, None]
                edge_y_common += [y0, y1, None]
                common_edge_count += 1
            elif source == "B":
                edge_x_added += [x0, x1, None]
                edge_y_added += [y0, y1, None]
                added_edge_count += 1
            else:
                edge_x_removed += [x0, x1, None]
                edge_y_removed += [y0, y1, None]
                removed_edge_count += 1

        if edge_x_common:
            edge_traces.append(go.Scatter(
                x=edge_x_common, y=edge_y_common,
                mode="lines",
                hoverinfo="none",
                line=dict(color="lightblue"),
                name="Common edges"
            ))
        if edge_x_added:
            edge_traces.append(go.Scatter(
                x=edge_x_added, y=edge_y_added,
                mode="lines",
                hoverinfo="none",
                line=dict(color="green"),
                name="Added edges"
            ))
        if edge_x_removed:
            edge_traces.append(go.Scatter(
                x=edge_x_removed, y=edge_y_removed,
                mode="lines",
                hoverinfo="none",
                line=dict(color="red"),
                name="Removed edges"
            ))

        trace_common = go.Scatter(
            x=common_x, y=common_y,
            mode="markers",
            name="Common nodes",
            hoverinfo="text",
            hovertext=common_text,
            marker=dict(color="lightblue", size=10, line=dict(width=1, color="darkslategray"))
        )

        trace_added = go.Scatter(
            x=added_x, y=added_y,
            mode="markers",
            name="Added nodes",
            hoverinfo="text",
            hovertext=added_text,
            marker=dict(color="lightgreen", size=10, line=dict(width=1, color="darkslategray"))
        )

        trace_removed = go.Scatter(
            x=removed_x, y=removed_y,
            mode="markers",
            name="Removed nodes",
            hoverinfo="text",
            hovertext=removed_text,
            marker=dict(color="salmon", size=10, line=dict(width=1, color="darkslategray"))
        )

        figure = go.Figure(data=edge_traces + [trace_common, trace_added, trace_removed])
        figure.update_layout(
            showlegend=True,
            legend=dict(itemsizing="constant", bgcolor="rgba(255,255,255,0.7)"),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            title="Directory Tree Comparison"
        )
        figure.write_html(f"{self.fileSavePath}", auto_open=False)
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