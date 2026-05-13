import os
import diskcache  # ← 追加
import dash
from dash import html, dcc, Input, Output, State, DiskcacheManager
from flask import send_file

from cache import background_callback_manager


app = dash.Dash(
    __name__,
    use_pages=True,
    background_callback_manager=background_callback_manager,
    suppress_callback_exceptions=True,
)
 
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
    full_path = f"./DataFolder/{filepath}"  # 画像が置いてあるフォルダ
    if not os.path.exists(full_path):
        return "File not found", 404
    return send_file(full_path)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=7862)  