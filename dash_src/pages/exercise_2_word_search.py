import os
import re
import numpy as np
from datetime import datetime

from dash import dcc, html, Input, Output, State, ctx, callback, register_page, no_update
from dash.exceptions import PreventUpdate

from dash_src.data_load import load_file_text
from dash_src.data_save import save_performance

register_page(__name__,
              path="/exercise_word_search",
              order=3)

INTERVAL_VALUE = 100  # ms

DESCRIPTION = """
**Word search** trains your ability to skim text quickly and locate a target word.

1. Select a file in the *Text input* page.
2. Press **Pick cue word** — a random word from the text is chosen and the number of its occurrences is shown.
3. Press **Start** — the full text appears and the timer begins.
4. Skim the text and locate every occurrence of the cue word.
5. Press **Done** (at the bottom of the text) — the timer stops and your time is displayed.
"""


def _clean_words(text):
    return [re.sub(r"[^\w]", "", w).lower() for w in text.split() if re.sub(r"[^\w]", "", w)]


layout = html.Div([
    dcc.Store("ws_timer_ms", data=0),
    dcc.Store("ws_word_count", data=0),
    dcc.Interval(id="ws_interval", n_intervals=0, interval=INTERVAL_VALUE, disabled=True),

    html.H3("Exercise 2 - Word Search"),
    html.Hr(),

    html.H4("Description"),
    dcc.Markdown(children=DESCRIPTION, style={'width': '80%'}),

    html.Hr(),

    html.H4("Exercise"),

    html.Button("Pick cue word", id="ws_pick_button", n_clicks=0),
    html.Br(),
    html.Label(
        id="ws_cue_label",
        style={'fontSize': '22px', 'fontWeight': 'bold', 'marginTop': '12px', 'display': 'block'}
    ),

    html.Br(),
    html.Button("Start", id="ws_start_button", n_clicks=0),

    html.Div(
        id="ws_text_area",
        style={
            'marginLeft': 20, 'marginRight': 20, 'marginTop': 20, 'marginBottom': 20,
            'backgroundColor': 'white', 'border': 'thin lightgrey dashed',
            'padding': '12px', 'whiteSpace': 'pre-wrap', 'lineHeight': '1.8',
            'fontSize': '15px',
        }
    ),

    html.Button("Done", id="ws_finish_button", n_clicks=0),
    html.Br(),
    html.Label(id="ws_time_label", style={'fontSize': '18px', 'marginTop': '10px', 'display': 'block'}),

    html.Br(),
    html.Button("Save performance", id="ws_save_button", n_clicks=0),
    html.Label(id="ws_save_feedback", style={'marginLeft': '12px', 'color': 'grey'}),
])


## Callbacks

@callback(
    Output("ws_cue_label", "children"),
    Input("ws_pick_button", "n_clicks"),
    State("store_file_selected", "data"),
    prevent_initial_call=True,
)
def pick_cue_word(_, file_selected):
    if not file_selected:
        return "No file selected — go to 'Text input' page first."
    text = load_file_text(file_selected[0])
    words = _clean_words(text)
    if not words:
        return "The selected file appears to be empty."
    cue = str(np.random.choice(words))
    count = sum(1 for w in words if w == cue)
    return f'Cue word: "{cue}"  —  appears {count} time(s) in the text'


@callback(
    Output("ws_timer_ms", "data"),
    Output("ws_interval", "disabled"),
    Output("ws_text_area", "children"),
    Output("ws_time_label", "children"),
    Output("ws_word_count", "data"),
    Input("ws_start_button", "n_clicks"),
    Input("ws_finish_button", "n_clicks"),
    Input("ws_interval", "n_intervals"),
    State("ws_timer_ms", "data"),
    State("store_file_selected", "data"),
    prevent_initial_call=True,
)
def control_exercise(_, __, ___, timer_ms, file_selected):
    triggered_id = ctx.triggered_id

    if triggered_id == "ws_start_button":
        if not file_selected:
            return 0, True, "Select a file in the 'Text input' page first.", "", 0
        text = load_file_text(file_selected[0])
        return 0, False, text, "", len(text.split())

    if triggered_id == "ws_finish_button":
        minutes, remainder = divmod(timer_ms, 60_000)
        seconds, ms = divmod(remainder, 1_000)
        time_str = f"Time taken: {int(minutes)}min {int(seconds)}s {int(ms)}ms"
        return timer_ms, True, no_update, time_str, no_update

    if triggered_id == "ws_interval":
        return timer_ms + INTERVAL_VALUE, False, no_update, "", no_update

    raise PreventUpdate


@callback(
    Output("ws_save_feedback", "children"),
    Input("ws_save_button", "n_clicks"),
    State("ws_timer_ms", "data"),
    State("ws_word_count", "data"),
    State("store_file_selected", "data"),
    prevent_initial_call=True,
)
def save_ws_performance(_, timer_ms, word_count, file_selected):
    if not timer_ms or not word_count:
        return "Nothing to save — complete the exercise first."
    filename = os.path.basename(file_selected[0]) if file_selected else "unknown"
    row = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file": filename,
        "word_count": word_count,
        "total_time_ms": timer_ms,
        "time_per_word_ms": round(timer_ms / word_count, 2),
    }
    save_performance("exercise_2_word_search", row)
    return f"Saved  ({row['date']})"
