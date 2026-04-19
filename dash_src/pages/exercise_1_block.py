import os
from datetime import datetime

from dash import dcc, html, Input, Output, State, ctx, callback, register_page
from dash.exceptions import PreventUpdate

from dash_src.data_load import load_file_text
from dash_src.data_save import save_performance

register_page(__name__,
              path="/exercise_1_block",
              order=2)

DESCRIPTION_BLOCK_READ = """
**Block reading** displays text in chunks of N words at a controlled pace.
This trains you to read groups of words at once and reduces subvocalization.

1. Select a file in the *Text input* page.
2. Set **N** (words per block) and **f** (reading speed in words/min).
3. Press **Start**.
"""

layout = html.Div([
    dcc.Store("block_current_index", data=0),
    dcc.Store("block_words", data=[]),
    dcc.Interval(id="block_interval", n_intervals=0, interval=500, disabled=True),

    html.H3("Exercise 1 - Block Read"),
    html.Hr(),

    html.H4("Description"),
    dcc.Markdown(children=DESCRIPTION_BLOCK_READ, style={'width': '80%'}),

    html.Hr(),

    html.H4("Settings"),
    html.Div([
        html.Div([
            html.Label("N — words per block:"),
            dcc.Slider(
                min=1, max=15, step=1, value=3,
                marks={i: str(i) for i in range(1, 16)},
                id="block_n_words",
            ),
        ], style={'width': '45%', 'display': 'inline-block', 'paddingRight': '30px'}),

        html.Div([
            html.Label("f — reading speed (words / min):"),
            dcc.Slider(
                min=100, max=1000, step=50, value=300,
                marks={i: str(i) for i in range(100, 1001, 100)},
                id="block_f_rate",
            ),
        ], style={'width': '45%', 'display': 'inline-block'}),
    ]),

    html.Br(),
    html.Label(id="block_interval_info", style={'color': 'grey', 'fontSize': '13px'}),

    html.Hr(),

    html.H4("Exercise"),
    html.Div([
        html.Button("Start",        id="block_start_button",  n_clicks=0, style={'marginRight': '8px'}),
        html.Button("Pause/Resume", id="block_pause_button",  n_clicks=0, style={'marginRight': '8px'}),
        html.Button("Reset",        id="block_reset_button",  n_clicks=0),
    ]),

    html.Div(
        html.Div(
            id="block_text_display",
            style={'fontSize': '36px', 'fontWeight': 'bold', 'textAlign': 'center',
                   'padding': '40px', 'minHeight': '120px', 'lineHeight': '1.4'},
        ),
        style={'marginLeft': 20, 'marginRight': 20, 'marginTop': 20, 'marginBottom': 20,
               'backgroundColor': 'white', 'border': 'thin lightgrey dashed', 'padding': '8px'}
    ),

    html.Label(id="block_progress_label", style={'color': 'grey'}),

    html.Br(),
    html.Button("Save performance", id="block_save_button", n_clicks=0),
    html.Label(id="block_save_feedback", style={'marginLeft': '12px', 'color': 'grey'}),
])


## Callbacks

@callback(
    Output("block_interval", "interval"),
    Output("block_interval_info", "children"),
    Input("block_n_words", "value"),
    Input("block_f_rate", "value"),
)
def update_interval_duration(n_words, f_rate):
    if not n_words or not f_rate:
        raise PreventUpdate
    interval_ms = int(n_words * 60_000 / f_rate)
    return interval_ms, f"Block duration: {interval_ms} ms  ({n_words} word(s) at {f_rate} words/min)"


@callback(
    Output("block_interval", "disabled"),
    Output("block_current_index", "data"),
    Output("block_words", "data"),
    Input("block_start_button", "n_clicks"),
    Input("block_pause_button", "n_clicks"),
    Input("block_reset_button", "n_clicks"),
    Input("block_interval", "n_intervals"),
    State("block_interval", "disabled"),
    State("block_current_index", "data"),
    State("block_words", "data"),
    State("store_file_selected", "data"),
    State("block_n_words", "value"),
    prevent_initial_call=True,
)
def control_playback(start, pause, reset, n_intervals,
                     is_disabled, current_index, blocks,
                     file_selected, n_words):
    triggered_id = ctx.triggered_id

    if triggered_id == "block_start_button":
        if not file_selected:
            raise PreventUpdate
        text = load_file_text(file_selected[0])
        words = text.split()
        n = n_words or 3
        new_blocks = [" ".join(words[i:i + n]) for i in range(0, len(words), n)]
        return False, 0, new_blocks

    if triggered_id == "block_pause_button":
        return not is_disabled, current_index, blocks

    if triggered_id == "block_reset_button":
        return True, 0, blocks

    if triggered_id == "block_interval":
        next_index = current_index + 1
        if next_index >= len(blocks):
            return True, current_index, blocks  # stop at last block
        return False, next_index, blocks

    raise PreventUpdate


@callback(
    Output("block_text_display", "children"),
    Output("block_progress_label", "children"),
    Input("block_current_index", "data"),
    State("block_words", "data"),
)
def display_current_block(current_index, blocks):
    if not blocks:
        return "Select a text in the 'Text input' page and press Start.", ""
    total = len(blocks)
    idx = min(current_index, total - 1)
    progress = f"Block {idx + 1} / {total}"
    if current_index >= total:
        return "— End of text —", progress
    return blocks[idx], progress


@callback(
    Output("block_save_feedback", "children"),
    Input("block_save_button", "n_clicks"),
    State("block_words", "data"),
    State("block_n_words", "value"),
    State("block_f_rate", "value"),
    State("store_file_selected", "data"),
    prevent_initial_call=True,
)
def save_block_performance(_, blocks, n_words, f_rate, file_selected):
    if not blocks or not f_rate or not n_words:
        return "Nothing to save — complete the exercise first."
    word_count = sum(len(b.split()) for b in blocks)
    n_blocks = len(blocks)
    interval_ms = int(n_words * 60_000 / f_rate)
    total_time_ms = n_blocks * interval_ms
    filename = os.path.basename(file_selected[0]) if file_selected else "unknown"
    row = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file": filename,
        "n_words_per_block": n_words,
        "f_rate": f_rate,
        "word_count": word_count,
        "n_blocks": n_blocks,
        "total_time_ms": total_time_ms,
        "time_per_word_ms": round(60_000 / f_rate, 2),
    }
    save_performance("exercise_1_block", row)
    return f"Saved  ({row['date']})"
