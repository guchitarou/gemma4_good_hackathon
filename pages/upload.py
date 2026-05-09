import os

import dash
from dash import html, dcc, Input, Output, State, callback


dash.register_page(__name__, path="/Upload", name="Upload")

BG = "#21252b" 
TEXT = "#ffffff"
PRIMARY = "#3B8BD4"
TEXT_SUB = "#a0bce0"

layout = html.Div([
    html.Div([
        html.H1("📂 Ingest", style={"fontSize": "2.5rem", "fontWeight": "800", "color": TEXT, "marginBottom": "1rem"}),
        html.P(
            "Register the data to be used for search and graph generation. The added files will be used to build the RAG search index and knowledge graph.", 
            style={"fontSize": "1.1rem", "color": TEXT}
        ),
        
        html.Label("Folder Path", style={"color": TEXT_SUB, "fontSize": "0.85rem", "marginBottom": "0.5rem", "display": "block"}),
        html.Div([   
            html.Div([
                dcc.Input(
                    id="ingest-folder-path",
                    type="text",
                    placeholder="Enter folder path (e.g. /data/my_folder)",
                    value="./DataFolder",  # ← デフォルト値
                    style={
                        "width": "100%",
                        "height": "3rem",          # ← Input自体に指定
                        "padding": "0.75rem 1rem",
                        "borderRadius": "8px",
                        "border": "1.5px solid #1e4080",
                        "background": "#0a2050",
                        "color": "#ffffff",
                        "fontSize": "1rem",
                        "outline": "none",
                    },
                ),
            ], style={"display": "flex","width": "50%","gap": "0.75rem", "marginBottom": "1.5rem"}),
        ], style={
            "display": "flex",
            "margin": "0 20px",
            "justifyContent": "center",  # ← 追加
            "alignItems": "center"
        }),
        
        html.Div([
            html.Div([
                html.Button(
                    "⚡ Ingest",
                    id="ingest-button",
                    n_clicks=0,
                    style={
                        "padding": "0.75rem 2.5rem",
                        "backgroundColor": PRIMARY,
                        "color": TEXT,
                        "border": "none",
                        "borderRadius": "8px",
                        "fontSize": "1rem",
                        "fontWeight": "700",
                        "cursor": "pointer",
                    },
                ),
            ], style={"width": "20%", "marginLeft": "12px"}),
        ], style={
            "display": "flex",
            "margin": "0 20px",
            "justifyContent": "center",  # ← 追加
            "alignItems": "center"
        }),
        # ステータス表示
        html.Div(
            id="ingest-status",
            style={
                "marginTop": "1.5rem",
                "padding": "1rem",
                "borderRadius": "8px",
                "fontSize": "0.95rem",
                "display": "none",
            }
        ),
    ], style={"maxWidth": "900px", "margin": "0 auto", "padding": "3rem 2rem"}),
], style={"minHeight": "100vh", "background": BG})

@callback(
    Output("ingest-status", "children"),
    Output("ingest-status", "style"),
    Input("ingest-button", "n_clicks"),
    State("ingest-folder-path", "value"),
    prevent_initial_call=True,
)
def start_ingest(n_clicks, folder_path):
    base_style = {
        "marginTop": "1.5rem",
        "padding": "1rem",
        "borderRadius": "8px",
        "fontSize": "0.95rem",
        "display": "block",
        "whiteSpace": "pre-wrap",
    }

    if not folder_path or not folder_path.strip():
        return (
            "⚠️ Please enter a folder path.",
            {**base_style, "background": "#3a1a00", "color": "#ffaa55", "border": "1px solid #ff8800"},
        )

    if not os.path.isdir(folder_path):
        return (
            f"❌ Folder not found:\n{folder_path}",
            {**base_style, "background": "#3a0000", "color": "#ff6666", "border": "1px solid #ff0000"},
        )

    # フォルダパスをターミナルにprint
    print("=== Ingest Start ===")
    print(f"  Folder Path : {folder_path}")
    print("====================")

    return (
        f"✅ Ingest started\n📁 {folder_path}",
        {**base_style, "background": "#003a1a", "color": "#66ff99", "border": "1px solid #00cc55"},
    )
