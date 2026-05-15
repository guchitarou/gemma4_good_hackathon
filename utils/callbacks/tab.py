
from dash import ctx, Input, Output

from ..layouts import screen_graph_layout, file_explorer_layout


def register(app, graph):
    @app.callback(
        Output("tab-content", "children"),
        Output("tab-a-btn", "className"),
        Output("tab-b-btn", "className"),
        Input("tab-a-btn", "n_clicks"),
        Input("tab-b-btn", "n_clicks"),
    )
    def switch_tab(n_a, n_b):
        triggered = ctx.triggered_id
        if triggered == "tab-b-btn":
            return screen_graph_layout(graph), "tab-btn", "tab-btn tab-active"
        return file_explorer_layout(), "tab-btn tab-active", "tab-btn"

