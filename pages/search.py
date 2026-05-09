import os
import json

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_cytoscape as cyto
import networkx as nx
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/search", name="Search")

# ============================
# データ読み込み（ファイルが存在する場合のみ）
# ============================
try:
    from config import FILE_DESCRIPTIONS_JSON_PATH, RELATIONSHIP_DESCRIPTIONS_JSON_PATH

    with open(RELATIONSHIP_DESCRIPTIONS_JSON_PATH, "r", encoding="utf-8") as f:
        relationship_data = json.load(f)

    with open(FILE_DESCRIPTIONS_JSON_PATH, "r", encoding="utf-8") as f:
        description_data = json.load(f)

except Exception:
    # config や JSON が存在しないときはサンプルデータで起動
    relationship_data = []
    description_data = {}

# ============================
# グラフ構築
# ============================
G = nx.Graph()
desc_dict = {}

for each_key in description_data.keys():
    path = description_data[each_key]["path"]
    filename = os.path.basename(path)
    desc_dict[filename] = description_data[each_key]
    G.add_node(filename, title=path)

for each_data in relationship_data:
    each_id = each_data["par_id"]
    xid, yid = each_id.split("_")
    relationship_desc = each_data["relationship"]
    if relationship_desc not in ["None"]:
        path_x = description_data[xid]["path"]
        path_y = description_data[yid]["path"]
        filename_x = os.path.basename(path_x)
        filename_y = os.path.basename(path_y)
        G.add_edge(filename_x, filename_y, relation=relationship_desc)

# ============================
# ヘルパー
# ============================
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


def get_file_type(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        return "image"
    elif ext in [".mp4", ".webm", ".mov"]:
        return "video"
    return "file"


# ============================
# スタイル定数
# ============================
STYLESHEET = [
    {"selector": "node", "style": {
        "label": "data(label)",
        "background-color": "#3B8BD4",
        "color": "#fff",
        "font-size": "12px",
        "text-valign": "center",
        "text-halign": "center",
        "width": 80, "height": 80,
        "border-width": 2,
        "border-color": "#185FA5",
    }},
    {"selector": "node.selected", "style": {
        "background-color": "#EF9F27",
        "border-color": "#BA7517",
        "border-width": 3,
    }},
    {"selector": "node:hover", "style": {
        "background-color": "rgb(68, 107, 180)",
        "cursor": "pointer",
    }},
    {"selector": "edge", "style": {
        "label": "",
        "curve-style": "bezier",
        "line-color": "#888",
        "font-size": "10px",
        "width": 1,
    }},
    {"selector": "edge:hover", "style": {
        "line-color": "#D85A30",
        "target-arrow-color": "#D85A30",
        "width": 1,
    }},
]

BG = "#21252b"
PANEL_STYLE = {
    "background": BG,
    "minHeight": "20rem",
    "whiteSpace": "pre-wrap",
    "fontSize": "1rem",
}

# ============================
# ページレイアウト
# ============================
layout = html.Div([
    html.Div([
        # ---- 左カラム（グラフ＋詳細＋アップロード） ----
        html.Div([
            html.Div([
                html.Button(
                    "View All",
                    id="home-reset-button",
                    n_clicks=0,
                    style={
                        "marginLeft": "12px",
                        "padding": "6px 16px",
                        "backgroundColor": "#3B8BD4",
                        "color": "#fff",
                        "border": "none",
                        "borderRadius": "6px",
                        "cursor": "pointer",
                    },
                ),
            ], style={"margin": "8px 20px"}),

            html.Div(id="home-tooltip", style={
                "position": "fixed",
                "background": BG,
                "color": "#cce0ff",
                "padding": "6px 12px",
                "borderRadius": "6px",
                "fontSize": "12px",
                "pointerEvents": "none",
                "display": "none",
                "zIndex": 1000,
                "boxShadow": "0 2px 8px rgba(0,0,0,0.3)",
            }),

            cyto.Cytoscape(
                id="home-cytoscape",
                elements=nx_to_cyto(G),
                layout={
                    "name": "cose",
                    "animate": True,
                    "idealEdgeLength": 200,
                    "nodeRepulsion": 400000,
                    "edgeElasticity": 100,
                    "gravity": 0,
                    "numIter": 1000,
                },
                stylesheet=STYLESHEET,
                style={
                    "width": "100%", "height": "520px",
                    "border": "1px solid #ddd", "borderRadius": "8px",
                },
            ),

            html.Div([
                html.Div([
                    html.H4("File Details", style={"marginTop": 0, "color": "#cce0ff"}),
                    html.Div(
                        id="home-detail-panel",
                        children="Please click on a node.",
                        style=PANEL_STYLE,
                    ),
                ], style={"width": "65%"}),

                html.Div([
                    html.H4("Drop Files Here", style={"marginTop": 0, "color": "#cce0ff"}),
                    dcc.Upload(
                        id="home-upload-data",
                        children=html.Div([
                            "📂 Drag and Drop"
                        ], style={
                            "height": "18rem",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                        }),
                        style={
                            "width": "calc(100% - 40px)",
                            "margin": "8px 20px",
                            "padding": "16px",
                            "borderWidth": "2px",
                            "borderStyle": "dashed",
                            "borderColor": "#3B8BD4",
                            "borderRadius": "8px",
                            "textAlign": "center",
                            "color": "#cce0ff",
                            "height": "20rem",
                            "backgroundColor": BG,
                        },
                        multiple=True,
                    ),
                ], style={"width": "30%"}),
            ], style={
                "width": "100%", "padding": "16px",
                "borderRadius": "8px", "marginLeft": "8px",
                "display": "flex",
            }),
        ], style={"width": "60%", "margin": "0 20px"}),

        # ---- 右カラム（iFrame） ----
        html.Div([
            html.Iframe(
                src="http://172.18.131.28:7861/?__theme=dark",
                style={
                    "width": "100%",
                    "height": "800px",
                    "border": "none",
                    "borderRadius": "8px",
                },
            ),
        ], style={"width": "40%", "marginLeft": "12px"}),

    ], style={"display": "flex", "margin": "0 20px"}),

    dcc.Store(id="home-api-trigger-store"),
    dcc.Interval(id="home-api-poll", interval=500),

], style={"fontFamily": "sans-serif", "minHeight": "100vh", "background": BG})


# ============================
# コールバック
# ============================
@callback(
    Output("home-detail-panel", "children"),
    Input("home-cytoscape", "tapNodeData"),
)
def display_node_detail(node_data):
    if not node_data:
        return "Please click on a node."
    node_id = node_data["id"]
    file_type = get_file_type(node_id)
    detail_info = desc_dict.get(node_id, {})
    detail = detail_info.get("description", "no details")

    text_info = html.P(
        f"File Name : {node_id}\n\n{detail}",
        style={"whiteSpace": "pre-wrap", "fontSize": "1rem", "color": "#cce0ff"},
    )

    if file_type == "image":
        return html.Div([
            text_info,
            html.Img(
                src=f"/files/{os.path.basename(node_id)}",
                style={"width": "100%", "maxHeight": "200px",
                       "objectFit": "contain", "borderRadius": "6px", "marginTop": "8px"},
            ),
        ])
    elif file_type == "video":
        return html.Div([
            text_info,
            html.Video(
                src=f"/files/{os.path.basename(node_id)}",
                controls=True,
                style={"width": "100%", "maxHeight": "200px",
                       "borderRadius": "6px", "marginTop": "8px"},
            ),
        ])
    return text_info


@callback(
    Output("home-cytoscape", "elements"),
    Input("home-upload-data", "filename"),
    Input("home-reset-button", "n_clicks"),
    Input("home-api-trigger-store", "data"),
    prevent_initial_call=True,
)
def handle_upload(filenames, n_clicks, api_trigger):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered_id == "home-api-trigger-store" and api_trigger:
        filenames = api_trigger["filename"]

    if triggered_id == "home-reset-button":
        return nx_to_cyto(G)

    if not filenames:
        return nx_to_cyto(G)

    if isinstance(filenames, str):
        filenames = [filenames]

    return nx_to_cyto(G, highlight_node=filenames[0])

@callback(
    Output("edge-panel", "children"),
    Input("cytoscape", "mouseoverEdgeData")
)
def display_edge_info(edge_data):
    if not edge_data:
        return "Please hover over an edge."
    return (f"🔗 {edge_data['source']}\n"
            f"    ↓ {edge_data.get('label', 'Relationship')}\n"
            f"  {edge_data['target']}")