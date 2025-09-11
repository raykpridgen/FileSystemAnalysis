import os
import shutil
from pathlib import Path
from igraph import Graph, EdgeSeq
import plotly.graph_objects as go

def build_nested_dict(path: Path):
    tree = {}
    for entry in sorted(os.listdir(path)):
        full = path / entry
        if full.is_dir():
            tree[entry] = build_nested_dict(full)
        else:
            tree[entry] = None  # leaf node
    return tree

def tree_edges(tree, parent=None):
    edges = []
    for node, children in tree.items():
        if parent is not None:
            edges.append((parent, node))
        if isinstance(children, dict):
            edges.extend(tree_edges(children, node))
    return edges


nested = build_nested_dict(root)
edges = tree_edges(nested)

vertices = list({v for edge in edges for v in edge})

G = Graph(directed=True)
G.add_vertices(vertices)
G.add_edges(edges)

layout = G.layout("rt")  # Reingold-Tilford tree layout
position = {v.index: layout[v.index] for v in G.vs}

Y = [layout[k][1] for k in range(vertices)]
M = max(Y)

Xn = [position[v.index][0] for v in G.vs]
Yn = [M - layout[k][1] for k in range(vertices)]

Xe = []
Ye = []
for edge in G.es:
    src, tgt = edge.tuple
    Xe += [position[src][0], position[tgt][0], None]
    Ye += [M - position[edge[0]][1], M - position[edge[1]][1], None]

labels = [v["name"] if "name" in v.attributes() else v.index for v in G.vs]

fig = go.Figure()
# edges
fig.add_trace(go.Scatter(
    x=Xe, y=Ye,
    mode='lines',
    line=dict(color='rgb(210,210,210)', width=1),
    hoverinfo='none'
))
# nodes
fig.add_trace(go.Scatter(
    x=Xn, y=Yn,
    mode='markers+text',
    marker=dict(size=18, color='#6175c1', line=dict(color='rgb(50,50,50)', width=1)),
    text=[v["name"] if "name" in v.attributes() else v.index for v in G.vs],
    textposition="top center"
))

fig.write_html("tree.html")
