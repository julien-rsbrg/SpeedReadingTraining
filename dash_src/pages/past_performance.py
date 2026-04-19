from dash import dcc, html, Input, Output, callback, register_page
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

from dash_src.data_save import load_performance

register_page(__name__,
              path="/past_performance",
              order=1)

_EXERCISES = [
    {
        "key": "0",
        "name": "exercise_0_free_read",
        "title": "Exercise 0 — Free Read",
        "columns": ["date", "file", "word_count", "total_time_ms", "time_per_word_ms"],
        "default_x": "date",
        "default_y": "time_per_word_ms",
        "default_color": "file",
    },
    {
        "key": "1",
        "name": "exercise_1_block",
        "title": "Exercise 1 — Block Read",
        "columns": ["date", "file", "n_words_per_block", "f_rate", "word_count",
                    "n_blocks", "total_time_ms", "time_per_word_ms"],
        "default_x": "date",
        "default_y": "f_rate",
        "default_color": "n_words_per_block",
    },
    {
        "key": "2",
        "name": "exercise_2_word_search",
        "title": "Exercise 2 — Word Search",
        "columns": ["date", "file", "word_count", "total_time_ms", "time_per_word_ms"],
        "default_x": "date",
        "default_y": "time_per_word_ms",
        "default_color": "file",
    },
    {
        "key": "3",
        "name": "exercise_3_peripheral_vision",
        "title": "Exercise 3 — Peripheral Vision",
        "columns": ["date", "exercise_type", "n_rows", "n_cols", "n_series",
                    "total_time_ms", "time_per_series_ms"],
        "default_x": "date",
        "default_y": "time_per_series_ms",
        "default_color": "exercise_type",
    },
]

_CTRL_STYLE = {"display": "inline-block", "verticalAlign": "top", "paddingRight": "14px"}


def _exercise_section(ex):
    k = ex["key"]
    opts = [{"label": c, "value": c} for c in ex["columns"]]
    return html.Div([
        html.H4(ex["title"]),
        html.Div([
            html.Div([
                html.Label("X:"),
                dcc.Dropdown(id=f"perf_{k}_x", options=opts,
                             value=ex["default_x"], clearable=False),
            ], style={**_CTRL_STYLE, "width": "16%"}),
            html.Div([
                html.Label("Y:"),
                dcc.Dropdown(id=f"perf_{k}_y", options=opts,
                             value=ex["default_y"], clearable=False),
            ], style={**_CTRL_STYLE, "width": "16%"}),
            html.Div([
                html.Label("Color:"),
                dcc.Dropdown(id=f"perf_{k}_color", options=opts,
                             value=ex["default_color"], clearable=False),
            ], style={**_CTRL_STYLE, "width": "16%"}),
            html.Div([
                html.Label("Use color:"),
                dcc.RadioItems(["On", "Off"], "On",
                               id=f"perf_{k}_color_toggle", inline=True),
            ], style={**_CTRL_STYLE, "width": "12%"}),
            html.Div([
                html.Label("Mode:"),
                dcc.RadioItems(["lines+markers", "markers"], "lines+markers",
                               id=f"perf_{k}_mode", inline=True),
            ], style={**_CTRL_STYLE, "width": "20%"}),
        ], style={"marginBottom": "8px"}),
        dcc.Graph(id=f"perf_{k}_graph"),
        html.Hr(),
    ])


layout = html.Div([
    html.H3("Past Performance"),
    html.Hr(),
    *[_exercise_section(ex) for ex in _EXERCISES],
])


## Callbacks


def _make_fig(exercise_name, x_col, y_col, color_col, color_on, mode):
    df = load_performance(exercise_name)
    fig = go.Figure()
    if df.empty or x_col not in df.columns or y_col not in df.columns:
        fig.update_layout(
            title="No data yet — save some sessions first.",
            xaxis={"visible": False}, yaxis={"visible": False},
        )
        return fig

    df = df.sort_values(x_col, kind="stable")

    if color_on == "On" and color_col in df.columns:
        for grp_val, grp_df in df.groupby(color_col, sort=False):
            fig.add_trace(go.Scatter(
                x=grp_df[x_col], 
                y=grp_df[y_col],
                mode=mode,
                name=str(grp_val),
            ))
    else:
        fig.add_trace(go.Scatter(
            x=df[x_col], 
            y=df[y_col],
            mode=mode,
            showlegend=False,
        ))
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col,
        showlegend=(color_on == "On"),
        margin={"t": 30},
    )
    return fig


@callback(
    Output("perf_0_graph", "figure"),
    Input("perf_0_x", "value"),
    Input("perf_0_y", "value"),
    Input("perf_0_color", "value"),
    Input("perf_0_color_toggle", "value"),
    Input("perf_0_mode", "value"),
)
def update_perf_0(x, y, color, color_on, mode):
    return _make_fig("exercise_0_free_read", x, y, color, color_on, mode)


@callback(
    Output("perf_1_graph", "figure"),
    Input("perf_1_x", "value"),
    Input("perf_1_y", "value"),
    Input("perf_1_color", "value"),
    Input("perf_1_color_toggle", "value"),
    Input("perf_1_mode", "value"),
)
def update_perf_1(x, y, color, color_on, mode):
    return _make_fig("exercise_1_block", x, y, color, color_on, mode)


@callback(
    Output("perf_2_graph", "figure"),
    Input("perf_2_x", "value"),
    Input("perf_2_y", "value"),
    Input("perf_2_color", "value"),
    Input("perf_2_color_toggle", "value"),
    Input("perf_2_mode", "value"),
)
def update_perf_2(x, y, color, color_on, mode):
    return _make_fig("exercise_2_word_search", x, y, color, color_on, mode)


@callback(
    Output("perf_3_graph", "figure"),
    Input("perf_3_x", "value"),
    Input("perf_3_y", "value"),
    Input("perf_3_color", "value"),
    Input("perf_3_color_toggle", "value"),
    Input("perf_3_mode", "value"),
)
def update_perf_3(x, y, color, color_on, mode):
    return _make_fig("exercise_3_peripheral_vision", x, y, color, color_on, mode)
