import os

import dash
from dash import ALL, Input, Output, State, ctx, html

from ..layouts import build_file_info, build_tree

def register(app, root_path, description_data):
    @app.callback(
        Output("root-path", "data"),
        Output("expanded-dirs", "data"),
        Input("go-btn", "n_clicks"),
        State("path-input", "value"),
        prevent_initial_call=True,
    )
    def navigate_to_path(_, path):
        path = os.path.expanduser(path or root_path)
        if os.path.isdir(path):
            return path, []
        return dash.no_update, dash.no_update


    @app.callback(
        Output("expanded-dirs", "data", allow_duplicate=True),
        Input({"type": "dir-item", "path": ALL}, "n_clicks"),
        State("expanded-dirs", "data"),
        prevent_initial_call=True,
    )
    def toggle_directory(_, expanded):
        triggered = ctx.triggered_id
        if not triggered:
            return dash.no_update
        path = triggered["path"]
        expanded_set = set(expanded)
        if path in expanded_set:
            expanded_set.discard(path)
        else:
            expanded_set.add(path)
        return list(expanded_set)


    @app.callback(
        Output("selected-file", "data", allow_duplicate=True),
        Input({"type": "dir-item", "path": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def select_dir(_):
        triggered = ctx.triggered_id
        if not triggered:
            return dash.no_update
        return triggered["path"]


    @app.callback(
        Output("selected-file", "data", allow_duplicate=True),
        Input({"type": "file-item", "path": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def select_file(_):
        triggered = ctx.triggered_id
        if not triggered:
            return dash.no_update
        return triggered["path"]


    @app.callback(
        Output("file-tree", "children"),
        Output("root-label", "children"),
        Input("root-path", "data"),
        Input("expanded-dirs", "data"),
    )
    def render_tree(root, expanded):
        expanded_set = set(expanded or [])
        items = build_tree(root, expanded_set)
        return items, f"📂 {root}"


    @app.callback(
        Output("file-info-panel", "children"),
        Output("file-info-header", "children"),
        Input("selected-file", "data"),
    )
    def render_file_info(path):
        if not path:
            return (
                html.Div(
                    "↑ Click a file or folder in the tree above to view its details here",
                    style={"color": "#585b70", "fontSize": "13px", "marginTop": "18px", "textAlign": "center"},
                ),
                "Select a file or folder to see details",
            )
        name = os.path.basename(path)
        header = f"{'📁' if os.path.isdir(path) else '📄'} {name}"
        return build_file_info(path, description_data), header

