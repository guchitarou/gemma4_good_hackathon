import os
import json

import diskcache  # ← 追加
import dash
from dash import html, dcc, Input, Output, State, DiskcacheManager
from flask import send_file
import networkx as nx

from cache import background_callback_manager

from config import RELATIONSHIP_DESCRIPTIONS_JSON_PATH, FILE_DESCRIPTIONS_JSON_PATH

from utils import load_ana_data, format_size, get_mime_label, get_file_icon, get_file_type, nx_to_cyto, STYLESHEET, callbacks





DEFAULT_ROOT = os.path.expanduser("./DataFolder")




app = dash.Dash(
    __name__,
    use_pages=True,
    background_callback_manager=background_callback_manager,
    suppress_callback_exceptions=True,
)

app.index_string = '''
<!DOCTYPE html>
<html>
<head>
{%metas%}
<title>File Explorer</title>
{%favicon%}
{%css%}
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #181825; }
  .tree-row:hover { background: #313244 !important; }
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: #1e1e2e; }
  ::-webkit-scrollbar-thumb { background: #45475a; border-radius: 4px; }
  ::-webkit-scrollbar-thumb:hover { background: #585b70; }
  .tab-btn {
    background: transparent; border: 1px solid #313244; color: #6c7086;
    border-radius: 8px; padding: 6px 18px; font-size: 13px; font-weight: 600;
    cursor: pointer; transition: all 0.15s;
  }
  .tab-btn:hover { background: #313244; color: #cdd6f4; }
  .tab-active { background: #313244 !important; color: #cba6f7 !important; border-color: #cba6f7 !important; }
</style>
</head>
<body>{%app_entry%}<footer>{%config%}{%scripts%}{%renderer%}</footer></body>
</html>
'''



# ============================
# スタイル定数
# ============================
DRAWER_WIDTH = "260px"
HEADER_HEIGHT = "60px"
PRIMARY    = "#3B8BD4"   # アクセントブルー
BG         = "#21252b"   # ベース紺
BG_LIGHT   = "#122f6a"   # ドロワー内少し明るい紺
TEXT       = "#ffffff"   # 文字：白
TEXT_SUB   = "#a0bce0"   # サブ文字：薄青白
BORDER     = "#1e4080"   # 区切り線

# ============================
# レイアウト
# ============================
app.layout = html.Div([
    dcc.Location(id="url"),
    # ↓ ここに追加（常にDOMに存在する）
    html.Div(id="tooltip", style={
        "position": "fixed",
        "background": "#21252b",
        "color": "#cce0ff",
        "padding": "6px 12px",
        "borderRadius": "6px",
        "fontSize": "12px",
        "pointerEvents": "none",
        "display": "none",
        "zIndex": 1000,
        "boxShadow": "0 2px 8px rgba(0,0,0,0.3)",
    }),
 
    # ---------- オーバーレイ ----------
    html.Div(
        id="overlay",
        style={
            "display": "none",
            "position": "fixed",
            "top": 0, "left": 0,
            "width": "100vw", "height": "100vh",
            "background": "rgba(0,0,0,0.5)",
            "zIndex": "199",
        }
    ),
 
    # ---------- ドロワー（サイドバー） ----------
    html.Div(
        id="drawer",
        children=[
            # ロゴ・タイトル
            html.Div([
                html.Span("◈", style={"fontSize": "1.6rem", "color": PRIMARY}),
                html.Span("  WowSearch", style={
                    "fontSize": "1.3rem", "fontWeight": "800",
                    "color": TEXT, "letterSpacing": "-0.5px",
                }),
            ], style={"display": "flex", "alignItems": "center", "padding": "1.5rem 1.5rem 1rem"}),
 
            html.Hr(style={"margin": "0 1rem 1rem", "borderColor": BORDER}),
 
            # ナビリンク
            html.Nav([
                dcc.Link([
                    html.Span("🔍", style={"marginRight": "0.75rem", "fontSize": "1.1rem"}),
                    "Search",
                ], href="/search", id="nav-home", style={
                    "display": "flex", "alignItems": "center",
                    "padding": "0.85rem 1.5rem",
                    "color": TEXT,
                    "textDecoration": "none",
                    "fontWeight": "600",
                    "fontSize": "0.95rem",
                    "borderRadius": "10px",
                    "margin": "0 0.75rem 0.25rem",
                    "transition": "background 0.15s",
                }),
                dcc.Link([
                    html.Span("⚙️", style={"marginRight": "0.75rem", "fontSize": "1.1rem"}),
                    "Ingest",
                ], href="/Upload", id="nav-settings", style={
                    "display": "flex", "alignItems": "center",
                    "padding": "0.85rem 1.5rem",
                    "color": TEXT,
                    "textDecoration": "none",
                    "fontWeight": "600",
                    "fontSize": "0.95rem",
                    "borderRadius": "10px",
                    "margin": "0 0.75rem 0.25rem",
                    "transition": "background 0.15s",
                }),
                
            ]),
            # バージョン表示（下部）
            html.Div("v1.0.0", style={
                "position": "absolute", "bottom": "1.5rem", "left": "1.5rem",
                "color": TEXT_SUB, "fontSize": "0.75rem",
            }),
        ],
        style={
            "position": "fixed",
            "top": 0, "left": "-260px",
            "width": DRAWER_WIDTH,
            "height": "100vh",
            "background": BG_LIGHT,
            "boxShadow": "4px 0 24px rgba(0,0,0,0.4)",
            "zIndex": "200",
            "transition": "left 0.3s cubic-bezier(0.4,0,0.2,1)",
            "overflowY": "auto",
        }
    ),
 
    # ---------- ヘッダー ----------
    html.Header([
        # ハンバーガーボタン（三本線を白に）
        html.Button(
            [
                html.Span(style={"display":"block","width":"22px","height":"2px","background":TEXT,"margin":"4px 0","borderRadius":"2px","transition":"0.3s"}),
                html.Span(style={"display":"block","width":"22px","height":"2px","background":TEXT,"margin":"4px 0","borderRadius":"2px","transition":"0.3s"}),
                html.Span(style={"display":"block","width":"22px","height":"2px","background":TEXT,"margin":"4px 0","borderRadius":"2px","transition":"0.3s"}),
            ],
            id="hamburger-btn",
            n_clicks=0,
            style={
                "background": "none",
                "border": "none",
                "cursor": "pointer",
                "padding": "8px",
                "borderRadius": "8px",
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "center",
            }
        ),
        html.Span("WowSearch", style={
            "fontSize": "1.1rem",
            "fontWeight": "800",
            "color": TEXT,
            "letterSpacing": "-0.5px",
            "marginLeft": "0.75rem",
        }),
    ], style={
        "position": "fixed",
        "top": 0, "left": 0, "right": 0,
        "height": HEADER_HEIGHT,
        "background": BG,
        "borderBottom": f"1px solid {BORDER}",
        "display": "flex",
        "alignItems": "center",
        "padding": "0 1.25rem",
        "zIndex": "100",
    }),
 
    # ---------- メインコンテンツ ----------
    html.Main(
        dash.page_container,
        style={"paddingTop": HEADER_HEIGHT, "background": BG, "minHeight": "100vh"},
    ),
 
    dcc.Store(id="drawer-open", data=False),
], style={
    "fontFamily": "'Noto Sans JP', 'Helvetica Neue', sans-serif",
    "margin": 0, "padding": 0,
    "background": BG,
    "width": "100vw",
    "overflowX": "hidden",
    "color": TEXT,
})
 
 
# ============================
# コールバック：ドロワー開閉
# ============================
@app.callback(
    Output("drawer", "style"),
    Output("overlay", "style"),
    Output("drawer-open", "data"),
    Input("hamburger-btn", "n_clicks"),
    Input("overlay", "n_clicks"),
    State("drawer-open", "data"),
    prevent_initial_call=True,
)
def toggle_drawer(ham_clicks, overlay_clicks, is_open):
    new_open = not is_open
    drawer_style = {
        "position": "fixed",
        "top": 0,
        "left": "0" if new_open else "-260px",
        "width": DRAWER_WIDTH,
        "height": "100vh",
        "background": BG_LIGHT,
        "boxShadow": "4px 0 24px rgba(0,0,0,0.4)",
        "zIndex": "200",
        "transition": "left 0.3s cubic-bezier(0.4,0,0.2,1)",
        "overflowY": "auto",
    }
    overlay_style = {
        "display": "block" if new_open else "none",
        "position": "fixed",
        "top": 0, "left": 0,
        "width": "100vw", "height": "100vh",
        "background": "rgba(0,0,0,0.5)",
        "zIndex": "199",
    }
    return drawer_style, overlay_style, new_open
 
 
# ============================
# コールバック：ページ遷移でドロワーを閉じる
# ============================
@app.callback(
    Output("drawer", "style", allow_duplicate=True),
    Output("overlay", "style", allow_duplicate=True),
    Output("drawer-open", "data", allow_duplicate=True),
    Input("url", "pathname"),
    prevent_initial_call=True,
)
def close_drawer_on_navigate(_):
    closed_drawer = {
        "position": "fixed",
        "top": 0, "left": "-260px",
        "width": DRAWER_WIDTH,
        "height": "100vh",
        "background": BG_LIGHT,
        "boxShadow": "4px 0 24px rgba(0,0,0,0.4)",
        "zIndex": "200",
        "transition": "left 0.3s cubic-bezier(0.4,0,0.2,1)",
        "overflowY": "auto",
    }
    return closed_drawer, {"display": "none"}, False



@app.server.route("/files/<path:filepath>")
def serve_file(filepath):
    print("ここが流れた！")
    print(filepath)
    #full_path = f"./DataFolder/{filepath}"  # 画像が置いてあるフォルダ
    if not os.path.exists(filepath):
        return "File not found", 404
    return send_file(filepath)



callbacks.explorer.register(app, DEFAULT_ROOT, RELATIONSHIP_DESCRIPTIONS_JSON_PATH, FILE_DESCRIPTIONS_JSON_PATH)
callbacks.graph.register(app, RELATIONSHIP_DESCRIPTIONS_JSON_PATH, FILE_DESCRIPTIONS_JSON_PATH)
callbacks.tab.register(app, RELATIONSHIP_DESCRIPTIONS_JSON_PATH, FILE_DESCRIPTIONS_JSON_PATH)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=7862)  