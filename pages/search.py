import os
import json

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_cytoscape as cyto
import networkx as nx
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/search", name="Search")

DEFAULT_ROOT = os.path.expanduser("./DataFolder")

# ============================
# データ読み込み（ファイルが存在する場合のみ）
# ============================
from config import FILE_DESCRIPTIONS_JSON_PATH, RELATIONSHIP_DESCRIPTIONS_JSON_PATH

# ============================
# グラフ構築
# ============================

# ── Layout ────────────────────────────────────────────────────

layout = html.Div(
    [
        dcc.Store(id="expanded-dirs", data=[]),
        dcc.Store(id="root-path", data=DEFAULT_ROOT),
        dcc.Store(id="selected-file", data=None),

        # ── Tab bar ──
        html.Div([
            html.Div([
                html.Div([
                    html.Button(
                        "🗂️  File Explorer",
                        id="tab-a-btn",
                        n_clicks=0,
                        className="tab-btn tab-active",
                    ),
                    html.Button(
                        "⚡ Graph",
                        id="tab-b-btn",
                        n_clicks=0,
                        className="tab-btn",
                    ),
                ],style={
                    "display":"flex",
                    "gap": "4px",
                    "padding": "8px 16px",
                    "background": "#11111b",
                    "borderBottom": "2px solid #313244",
                    "flexShrink": "0",
                }),
                html.Div(id="tab-content", style={"display": "flex", "flexDirection": "column", "flex": "1", "minHeight": "0"}),
            ], style={"width": "60%", "margin": "0 20px"}),
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
        # ── Tab content ──
        
    ],
    style={
        "fontFamily": "'Segoe UI', sans-serif",
        "background": "#181825",
        "color": "#cdd6f4",
        "height": "100vh",
        "display": "flex",
        "flexDirection": "column",
        "overflow": "hidden",
    },
)
