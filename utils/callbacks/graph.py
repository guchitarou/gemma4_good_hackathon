import os

import dash
from dash import ALL, Input, Output, State, ctx, html


from ..graph_utils import get_file_type, nx_to_cyto
from ..analyzer import load_ana_data

def register(app, relation_path, desc_path):
    @app.callback(
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

    @app.callback(
        Output("edge-panel", "children"),
        Input("cytoscape", "mouseoverEdgeData")
    )
    def display_edge_info(edge_data):
        if not edge_data:
            return "Please hover over an edge."
        return (f"🔗 {edge_data['source']}\n"
                f"    ↓ {edge_data.get('label', 'Relationship')}\n"
                f"  {edge_data['target']}")
    # ============================
    # コールバック
    # ============================
    @app.callback(
        Output("home-detail-panel", "children"),
        Input("home-cytoscape", "tapNodeData"),
    )
    def display_node_detail(node_data):
        print("押された！！！！！！！！！！")
        if not node_data:
            return "Please click on a node."


        G, desc_dict, description_data, relationship_data = load_ana_data(
            relation_path,
            desc_path
        )
        node_id = node_data["id"]
        file_type = get_file_type(node_id)
        detail_info = desc_dict.get(node_id, {})
        detail = detail_info.get("description", "no details")

        path = detail_info.get("path", None)


        text_info = html.P(
            f"File Name : {node_id}\n\n{detail}",
            style={"whiteSpace": "pre-wrap", "fontSize": "1rem", "color": "#cce0ff"},
        )

        if file_type == "image":
            return html.Div([
                text_info,
                html.Img(
                    src=f"/files/{path}",
                    style={"width": "100%", "maxHeight": "200px",
                           "objectFit": "contain", "borderRadius": "6px", "marginTop": "8px"},
                ),
            ])
        elif file_type == "video":
            return html.Div([
                text_info,
                html.Video(
                    src=f"/files/{path}",
                    controls=True,
                    style={"width": "100%", "maxHeight": "200px",
                           "borderRadius": "6px", "marginTop": "8px"},
                ),
            ])

        elif file_type == "audio":
            return html.Div([
                text_info,
                html.Audio(
                    src=f"/files/{path}",
                    controls=True,
                    style={
                        "width": "100%",
                        "marginTop": "8px",
                    }
                )
            ])
        return text_info
