import os
import networkx as nx


def get_file_type(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        return "image"
    elif ext in [".mp4", ".webm", ".mov"]:
        return "video"
    elif ext in [".mp3"]:
        return "audio"
    return "file"


def nx_to_cyto(graph, highlight_node=None):
    elements = []
    if highlight_node is not None:
        nodes = set(nx.ego_graph(graph, highlight_node).nodes)
        for src, tgt, data in graph.edges(data=True):
            if src == highlight_node or tgt == highlight_node:
                elements.append({
                    "data": {
                        "source": src, "target": tgt,
                        "label": data.get("relation", ""),
                        "id": f"{src}-{tgt}",
                    }
                })
    else:
        nodes = set(graph.nodes)
        for src, tgt, data in graph.edges(data=True):
            if src in nodes and tgt in nodes:
                elements.append({
                    "data": {
                        "source": src, "target": tgt,
                        "label": data.get("relation", ""),
                        "id": f"{src}-{tgt}",
                    }
                })

    for node in nodes:
        elements.append({
            "data": {"id": node, "label": node},
            "classes": "selected" if node == highlight_node else "",
        })
    return elements