import os
import json
import datetime
from pathlib import Path

import dash
from dash import dcc, html, Input, Output, State, ctx, ALL
import stat
import mimetypes
import dash_cytoscape as cyto
import networkx as nx
import dash_bootstrap_components as dbc

from .storage import format_size, get_mime_label, get_file_icon
from .graph_utils import get_file_type, nx_to_cyto
from .analyzer import is_analyzed


BG = "#21252b"
PANEL_STYLE = {
    "background": BG,
    "minHeight": "15rem",
    "whiteSpace": "pre-wrap",
    "fontSize": "1rem",
}

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

def build_tree_item(path: str, name: str, depth: int, expanded_set: set) -> html.Div:
    """Build a single tree row (non-recursive; relies on expanded_set)."""
    is_dir = os.path.isdir(path)
    icon = get_file_icon(path, is_dir)
    is_expanded = path in expanded_set
    indent = depth * 20

    if is_dir:
        arrow = "▾" if is_expanded else "▸"
        row = html.Div(
            [
                html.Span(arrow, style={"marginRight": "4px", "color": "#888"}),
                html.Span(icon, style={"marginRight": "6px"}),
                html.Span(name, style={"fontWeight": "600"}),
            ],
            id={"type": "dir-item", "path": path},
            n_clicks=0,
            style={
                "paddingLeft": f"{indent}px",
                "paddingTop": "5px",
                "paddingBottom": "5px",
                "cursor": "pointer",
                "display": "flex",
                "alignItems": "center",
                "borderRadius": "6px",
                "userSelect": "none",
            },
            className="tree-row dir-row",
        )
        children = []
        if is_expanded:
            try:
                entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
                for entry in entries:
                    children.append(build_tree_item(entry.path, entry.name, depth + 1, expanded_set))
            except PermissionError:
                children.append(html.Div(
                    "🔒 Permission denied",
                    style={"paddingLeft": f"{indent+40}px", "color": "#aaa", "fontSize": "12px"},
                ))
        return html.Div([row, html.Div(children)])
    else:
        row = html.Div(
            [
                html.Span(icon, style={"marginRight": "6px"}),
                html.Span(name),
            ],
            id={"type": "file-item", "path": path},
            n_clicks=0,
            style={
                "paddingLeft": f"{indent + 20}px",
                "paddingTop": "4px",
                "paddingBottom": "4px",
                "cursor": "pointer",
                "display": "flex",
                "alignItems": "center",
                "borderRadius": "6px",
                "userSelect": "none",
                "color": "#cdd6f4",
            },
            className="tree-row file-row",
        )
        return html.Div(row)





def build_tree(root: str, expanded_set: set) -> list:
    items = []
    try:
        entries = sorted(os.scandir(root), key=lambda e: (not e.is_dir(), e.name.lower()))
        for entry in entries:
            items.append(build_tree_item(entry.path, entry.name, 1, expanded_set))
    except PermissionError:
        items.append(html.Div("🔒 Permission denied for this folder.", style={"color": "#f38ba8"}))
    return items



def build_file_info(path: str, description_data) -> html.Div:
    """Build the details panel for the selected file or folder."""
    try:
        st = os.stat(path)
    except Exception as e:
        return html.Div(f"Error reading info: {e}", style={"color": "#f38ba8"})

    is_dir = os.path.isdir(path)
    icon = get_file_icon(path, is_dir)
    name = os.path.basename(path)
    #kind = "Directory" if is_dir else "File"
    size_str = "—" if is_dir else format_size(st.st_size)
    mime = "—" if is_dir else get_mime_label(path)
    mtime = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    #ctime = datetime.datetime.fromtimestamp(st.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
    #mode = stat.filemode(st.st_mode)

    # Text preview for small text files
    preview_block = None
    if not is_dir and st.st_size < 8192:
        mime_val, _ = mimetypes.guess_type(path)
        text_types = ["text/", "application/json", "application/javascript"]
        if mime_val and any(mime_val.startswith(t) for t in text_types):
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read(2000)
                preview_block = html.Div(
                    [
                        html.P("📋 Preview", style={"fontWeight": "700", "marginBottom": "8px", "color": "#cba6f7"}),
                        html.Pre(
                            content,
                            style={
                                "background": "#1e1e2e",
                                "padding": "12px",
                                "borderRadius": "8px",
                                "overflowX": "auto",
                                "fontSize": "12px",
                                "color": "#cdd6f4",
                                "maxHeight": "100px",
                                "overflowY": "auto",
                                "border": "1px solid #313244",
                            },
                        ),
                    ]
                )
            except Exception:
                pass

    def info_row(label, value):
        return html.Div(
            [
                html.Span(label, style={"color": "#a6adc8", "width": "110px", "display": "inline-block", "fontSize": "13px"}),
                html.Span(str(value), style={"color": "#cdd6f4", "fontSize": "13px", "fontFamily": "monospace"}),
            ],
            style={"marginBottom": "4px"},
        )

    rows = [
        info_row("Size", size_str),
        info_row("MIME Type", mime),
        info_row("Modified", mtime),
        info_row("Full Path", path),
    ]
    file_name = Path(path).name
    file_desc = is_analyzed(
        file_name,
        description_data
    )

    file_type = get_file_type(path)

    desc_html_list = [
        html.H4("🔍File Details", style={"marginTop": 0, "color": "#cce0ff"}),
        html.Div([
            file_desc
        ])
    ] 

    if file_type == "image":
        desc_html_list.append(
            html.Img(
                src=f"/files/{path}",
                style={"width": "100%", "maxHeight": "200px",
                       "objectFit": "contain", "borderRadius": "6px", "marginTop": "8px"},
            ),
        )
    elif file_type == "video":
        desc_html_list.append(
            html.Video(
                src=f"/files/{path}",
                controls=True,
                style={"width": "100%", "maxHeight": "200px",
                        "borderRadius": "6px", "marginTop": "8px"},
            ),
        )
    elif file_type == "audio":
        desc_html_list.append(
            html.Audio(
                src=f"/files/{path}",
                controls=True,
                style={
                    "width": "100%",
                    "marginTop": "8px",
                }
            )
        )
    return html.Div([
        html.Div(desc_html_list, style={"width": "50%"}),  # 幅を指定
        html.Div([
            html.Div(
                [
                    html.Span(icon, style={"fontSize": "22px", "marginRight": "10px"}),
                    html.Span(name, style={"fontSize": "17px", "fontWeight": "700", "color": "#cba6f7"}),
                ],
                style={"display": "flex", "alignItems": "center", "marginBottom": "10px"},
            ),
            html.Div(rows, style={"marginBottom": "10px"}),
            preview_block or html.Div(),
        ], style={"width": "50%"}),  # 幅を指定
    ], style={
        "display": "flex",      # ← 横並び
        "gap": "2rem",          # 要素間の余白
    })

def screen_graph_layout(graph):
    """Tab B: placeholder screen."""
    return html.Div([
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
                elements=nx_to_cyto(graph),
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
                    "width": "100%", "height": "420px",
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
                            "height": "14rem",
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
                            "height": "15rem",
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
        ], style={"margin": "0 20px"})



def file_explorer_layout():
    """Tab A: File Explorer."""
    return html.Div(
        [
            # File tree (top, takes remaining space)
            html.Div(
                [
                    html.Div(
                        id="root-label",
                        style={
                            "padding": "8px 16px",
                            "fontSize": "12px",
                            "color": "#6c7086",
                            "borderBottom": "1px solid #313244",
                            "fontFamily": "monospace",
                            "overflow": "hidden",
                            "textOverflow": "ellipsis",
                            "whiteSpace": "nowrap",
                            "flexShrink": "0",
                        },
                    ),
                    html.Div(
                        id="file-tree",
                        style={
                            "flex": "1",
                            "padding": "8px",
                        },
                    ),
                ],
                style={
                    "background": "#1e1e2e",
                    "display": "flex",
                    "flexDirection": "column",
                    "flex": "1",
                    "minHeight": "0",
                    "maxHeight": "400px",
                    "overflowY": "auto"
                    
                },
            ),
            # Details panel (bottom, fixed height)
            html.Div(
                [
                    html.Div(
                        "Select a file or folder to see details",
                        id="file-info-header",
                        style={
                            "padding": "7px 20px",
                            "fontSize": "12px",
                            "color": "#6c7086",
                            "borderBottom": "1px solid #313244",
                            "flexShrink": "0",
                        },
                    ),
                    html.Div(
                        html.Div(
                            "↑ Click a file or folder in the tree above to view its details here",
                            style={"color": "#585b70", "fontSize": "13px", "marginTop": "18px", "textAlign": "center"},
                        ),
                        id="file-info-panel",
                        style={
                            "padding": "14px 24px",
                            "overflowY": "auto",
                            "flex": "1",
                        },
                    ),
                ],
                style={
                    "background": "#181825",
                    "height": "300px",
                    "flexShrink": "0",
                    "display": "flex",
                    "flexDirection": "column",
                    "borderTop": "2px solid #45475a",
                },
            ),
        ],
        style={"display": "flex", "flexDirection": "column", "flex": "1", "minHeight": "0"},
    )


