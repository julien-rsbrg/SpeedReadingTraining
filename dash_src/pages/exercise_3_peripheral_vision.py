import os
import numpy as np
from datetime import datetime

from dash import dcc, html, Input, Output, State, ctx, callback, register_page, no_update
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

from dash_src.data_save import save_performance

register_page(__name__,
              path="/exercise_3_peripheral_vision",
              order=4)

INTERVAL_VALUE = 100  # ms

DESCRIPTION = """
**Peripheral vision** trains your ability to process information without shifting your gaze from a central fixation point.

- **Schultz table**: numbers 0 to N−1 are randomly placed in the grid. Find them in ascending order while keeping your gaze fixed at the center cell.
- **Word search**: the cue word is shown at the center cell (your fixation point). Find its one copy hidden among the surrounding words using only peripheral vision. Word lists must be **.txt** files with one word per line.
"""


# ── helpers ──────────────────────────────────────────────────────────────────

def _load_word_list(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def _center_idx(n_rows, n_cols):
    return (n_rows // 2) * n_cols + (n_cols // 2)


def _make_grid(exercise_type, n_rows, n_cols, word_files):
    if exercise_type == "Schultz table":
        n = n_rows * n_cols
        flat = list(range(n))
        np.random.shuffle(flat)
        return {"flat": [str(x) for x in flat], "n_rows": n_rows, "n_cols": n_cols, "cue_word": None}
    else:
        if not word_files:
            return None
        file_path = str(np.random.choice(word_files))
        words = _load_word_list(file_path)
        if not words:
            return None

        cue = str(np.random.choice(words))
        n_cells = n_rows * n_cols
        n_surrounding = n_cells - 1

        others = [w for w in words if w != cue]
        np.random.shuffle(others)
        fill = others[: n_surrounding - 1]
        while len(fill) < n_surrounding - 1:
            fill.append("—")
        surrounding = fill + [cue]
        np.random.shuffle(surrounding)

        ci = _center_idx(n_rows, n_cols)
        flat = surrounding[:ci] + [cue] + surrounding[ci:]
        return {"flat": flat, "n_rows": n_rows, "n_cols": n_cols, "cue_word": cue}


def _render_grid_html(grid_data):
    if not grid_data or "flat" not in grid_data:
        return html.Div()

    flat = grid_data["flat"]
    n_rows, n_cols = grid_data["n_rows"], grid_data["n_cols"]
    ci = _center_idx(n_rows, n_cols)

    cell_px = max(55, min(110, 500 // max(n_rows, n_cols)))
    font_px = max(11, min(20, cell_px // 4))

    rows_html = []
    for r in range(n_rows):
        cells_html = []
        for c in range(n_cols):
            idx = r * n_cols + c
            val = flat[idx] if idx < len(flat) else ""
            is_center = idx == ci
            style = {
                "border": "1px solid #ccc",
                "width": f"{cell_px}px",
                "height": f"{cell_px}px",
                "textAlign": "center",
                "verticalAlign": "middle",
                "fontSize": f"{font_px}px",
                "fontWeight": "bold" if is_center else "normal",
                "backgroundColor": "white",
                "padding": "2px",
                "userSelect": "none",
            }
            cells_html.append(html.Td(str(val), style=style))
        rows_html.append(html.Tr(cells_html))

    return html.Table(
        rows_html,
        style={"borderCollapse": "collapse", "margin": "20px auto", "tableLayout": "fixed"},
    )


# ── layout ────────────────────────────────────────────────────────────────────

layout = html.Div([
    dcc.Store("pv_word_files", data=[]),
    dcc.Store("pv_grid_data", data={}),
    dcc.Store("pv_series_idx", data=0),
    dcc.Store("pv_times_ms", data=[]),
    dcc.Store("pv_timer_ms", data=0),
    dcc.Store("pv_phase", data="settings"),
    dcc.Interval("pv_interval", n_intervals=0, interval=INTERVAL_VALUE, disabled=True),

    html.H3("Exercise 4 - Peripheral Vision"),
    html.Hr(),
    html.H4("Description"),
    dcc.Markdown(DESCRIPTION, style={"width": "80%"}),
    html.Hr(),

    # ── Settings section ──────────────────────────────────────────────────────
    html.Div(id="pv_settings_section", children=[
        html.H4("Settings"),
        html.Div([
            html.Div([
                html.Label("Rows:"),
                dcc.Slider(min=2, max=8, step=1, value=4,
                           marks={i: str(i) for i in range(2, 9)},
                           id="pv_n_rows"),
            ], style={"width": "45%", "display": "inline-block", "paddingRight": "20px"}),
            html.Div([
                html.Label("Columns:"),
                dcc.Slider(min=2, max=8, step=1, value=4,
                           marks={i: str(i) for i in range(2, 9)},
                           id="pv_n_cols"),
            ], style={"width": "45%", "display": "inline-block"}),
        ]),
        html.Br(),
        html.Div([
            html.Label("Number of series:"),
            dcc.Slider(min=1, max=20, step=1, value=5,
                       marks={i: str(i) for i in [1, 5, 10, 15, 20]},
                       id="pv_n_series"),
        ], style={"width": "45%"}),
        html.Br(),

        html.Label("Exercise type:"),
        dcc.RadioItems(
            options=["Schultz table", "Word search"],
            value="Schultz table",
            id="pv_exercise_type",
            inline=True,
        ),
        html.Br(),

        html.Div(id="pv_word_search_settings", style={"display": "none"}, children=[
            html.Label("Folder with word-list .txt files (one word per line):"),
            html.Div([
                dcc.Input(
                    id="pv_folder_path", type="text",
                    placeholder="Absolute folder path...",
                    style={"width": "55%", "display": "inline-block"},
                ),
                html.Button("Parse folder", id="pv_parse_button", n_clicks=0,
                            style={"marginLeft": "8px"}),
            ]),
            html.Label(id="pv_parse_feedback",
                       style={"color": "grey", "fontSize": "13px", "display": "block", "marginTop": "4px"}),
        ]),

        html.Br(),
        html.Button("Start", id="pv_start_button", n_clicks=0,
                    style={"fontSize": "16px", "padding": "8px 24px"}),
        html.Label(id="pv_start_feedback", style={"color": "red", "marginLeft": "12px"}),
    ]),

    # ── Running section ───────────────────────────────────────────────────────
    html.Div(id="pv_running_section", style={"display": "none"}, children=[
        html.Div(id="pv_progress_label",
                 style={"textAlign": "center", "fontSize": "16px", "color": "grey", "marginTop": "10px"}),
        html.Div(id="pv_cue_label",
                 style={"textAlign": "center", "fontSize": "20px", "fontWeight": "bold", "marginTop": "8px"}),
        html.Div(id="pv_grid_display"),
        html.Div(
            html.Button("Next", id="pv_next_button", n_clicks=0,
                        style={"fontSize": "16px", "padding": "8px 32px"}),
            style={"textAlign": "center", "marginBottom": "12px"},
        ),
        html.Div(id="pv_timer_display",
                 style={"textAlign": "center", "fontSize": "20px", "color": "#555",
                        "fontFamily": "monospace", "marginBottom": "16px"}),
    ]),

    # ── Results section ───────────────────────────────────────────────────────
    html.Div(id="pv_results_section", style={"display": "none"}, children=[
        html.H4("Results"),
        dcc.Graph(id="pv_results_chart"),
        html.Label(id="pv_total_time_label",
                   style={"fontSize": "20px", "fontWeight": "bold", "display": "block", "marginTop": "10px"}),
        html.Button("Back to settings", id="pv_back_button", n_clicks=0,
                    style={"marginTop": "14px", "marginRight": "8px"}),
        html.Button("Save performance", id="pv_save_button", n_clicks=0,
                    style={"marginTop": "14px"}),
        html.Label(id="pv_save_feedback", style={"marginLeft": "12px", "color": "grey"}),
    ]),
])


# ── callbacks ─────────────────────────────────────────────────────────────────

@callback(
    Output("pv_word_search_settings", "style"),
    Input("pv_exercise_type", "value"),
)
def toggle_word_search_settings(exercise_type):
    return {"display": "block"} if exercise_type == "Word search" else {"display": "none"}


@callback(
    Output("pv_word_files", "data"),
    Output("pv_parse_feedback", "children"),
    Input("pv_parse_button", "n_clicks"),
    State("pv_folder_path", "value"),
    prevent_initial_call=True,
)
def parse_word_folder(_, folder_path):
    if not folder_path:
        return [], "Please enter a folder path."
    if not os.path.isdir(folder_path):
        return [], f"Directory not found: {folder_path}"
    files = sorted([
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path) if f.endswith(".txt")
    ])
    if not files:
        return [], "No .txt files found in this folder."
    names = ", ".join(os.path.basename(f) for f in files)
    return files, f"Found {len(files)} file(s): {names}"


@callback(
    Output("pv_timer_ms", "data", allow_duplicate=True),
    Input("pv_interval", "n_intervals"),
    State("pv_timer_ms", "data"),
    prevent_initial_call=True,
)
def tick_timer(_, timer_ms):
    return timer_ms + INTERVAL_VALUE


@callback(
    Output("pv_timer_display", "children"),
    Input("pv_timer_ms", "data"),
)
def display_timer(timer_ms):
    minutes, rem = divmod(timer_ms, 60_000)
    seconds, cs = divmod(rem, 1_000)
    return f"{int(minutes):02d}:{int(seconds):02d}.{int(cs) // 100}"


@callback(
    Output("pv_phase", "data", allow_duplicate=True),
    Output("pv_series_idx", "data"),
    Output("pv_times_ms", "data"),
    Output("pv_timer_ms", "data", allow_duplicate=True),
    Output("pv_interval", "disabled"),
    Output("pv_grid_data", "data"),
    Output("pv_start_feedback", "children"),
    Input("pv_start_button", "n_clicks"),
    Input("pv_next_button", "n_clicks"),
    State("pv_phase", "data"),
    State("pv_series_idx", "data"),
    State("pv_times_ms", "data"),
    State("pv_timer_ms", "data"),
    State("pv_n_rows", "value"),
    State("pv_n_cols", "value"),
    State("pv_n_series", "value"),
    State("pv_exercise_type", "value"),
    State("pv_word_files", "data"),
    prevent_initial_call=True,
)
def control_flow(start_clicks, next_clicks, phase, series_idx, times_ms, timer_ms,
                 n_rows, n_cols, n_series, exercise_type, word_files):
    triggered_id = ctx.triggered_id

    if triggered_id == "pv_start_button":
        if exercise_type == "Word search" and not word_files:
            return (no_update, no_update, no_update, no_update, no_update, no_update,
                    "Parse a word folder first.")
        grid = _make_grid(exercise_type, n_rows, n_cols, word_files)
        if grid is None:
            return (no_update, no_update, no_update, no_update, no_update, no_update,
                    "Failed to build grid — check word files.")
        return "running", 0, [], 0, False, grid, ""

    if triggered_id == "pv_next_button" and phase == "running":
        new_times = times_ms + [timer_ms]
        next_idx = series_idx + 1
        if next_idx >= n_series:
            return "finished", next_idx, new_times, 0, True, {}, ""
        grid = _make_grid(exercise_type, n_rows, n_cols, word_files)
        return "running", next_idx, new_times, 0, False, grid, ""

    raise PreventUpdate


@callback(
    Output("pv_settings_section", "style"),
    Output("pv_running_section", "style"),
    Output("pv_results_section", "style"),
    Input("pv_phase", "data"),
)
def toggle_sections(phase):
    show, hide = {"display": "block"}, {"display": "none"}
    if phase == "running":
        return hide, show, hide
    if phase == "finished":
        return hide, hide, show
    return show, hide, hide


@callback(
    Output("pv_grid_display", "children"),
    Output("pv_progress_label", "children"),
    Output("pv_cue_label", "children"),
    Input("pv_grid_data", "data"),
    State("pv_series_idx", "data"),
    State("pv_n_series", "value"),
    State("pv_exercise_type", "value"),
)
def render_grid(grid_data, series_idx, n_series, exercise_type):
    if not grid_data:
        return html.Div(), "", ""
    grid_el = _render_grid_html(grid_data)
    progress = f"Series {series_idx + 1} / {n_series}"
    if exercise_type == "Word search":
        cue = grid_data.get("cue_word", "")
        instruction = f'Find: "{cue}"  —  keep your gaze on the center cell'
    else:
        n_total = grid_data["n_rows"] * grid_data["n_cols"]
        instruction = f"Find numbers 0 → {n_total - 1} in ascending order  —  keep your gaze at the center"
    return grid_el, progress, instruction


@callback(
    Output("pv_results_chart", "figure"),
    Output("pv_total_time_label", "children"),
    Input("pv_phase", "data"),
    State("pv_times_ms", "data"),
)
def show_results(phase, times_ms):
    if phase != "finished" or not times_ms:
        raise PreventUpdate
    labels = [f"#{i + 1}" for i in range(len(times_ms))]
    values_s = [t / 1000 for t in times_ms]
    fig = go.Figure(go.Scatter(
        x=labels, y=values_s,
        mode="lines+markers",
        text=[f"{v:.1f}s" for v in values_s],
        hoverinfo="x+text",
        line={"color": "steelblue"},
    ))
    fig.update_layout(
        title="Time per grid (seconds)",
        xaxis_title="Series",
        yaxis_title="Time (s)",
        showlegend=False,
    )
    total_ms = sum(times_ms)
    minutes, rem = divmod(total_ms, 60_000)
    seconds, ms = divmod(rem, 1_000)
    return fig, f"Total time: {int(minutes)}min {int(seconds)}s {int(ms)}ms"


@callback(
    Output("pv_phase", "data", allow_duplicate=True),
    Input("pv_back_button", "n_clicks"),
    prevent_initial_call=True,
)
def back_to_settings(_):
    return "settings"


@callback(
    Output("pv_save_feedback", "children"),
    Input("pv_save_button", "n_clicks"),
    State("pv_times_ms", "data"),
    State("pv_n_rows", "value"),
    State("pv_n_cols", "value"),
    State("pv_n_series", "value"),
    State("pv_exercise_type", "value"),
    prevent_initial_call=True,
)
def save_pv_performance(_, times_ms, n_rows, n_cols, n_series, exercise_type):
    if not times_ms:
        return "Nothing to save — complete the exercise first."
    total_time_ms = sum(times_ms)
    n = len(times_ms)
    row = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "exercise_type": exercise_type,
        "n_rows": n_rows,
        "n_cols": n_cols,
        "n_series": n,
        "total_time_ms": total_time_ms,
        "time_per_series_ms": round(total_time_ms / n, 2),
    }
    save_performance("exercise_3_peripheral_vision", row)
    return f"Saved  ({row['date']})"
