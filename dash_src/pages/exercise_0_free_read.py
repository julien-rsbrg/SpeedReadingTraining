import os
from datetime import datetime

from dash import dcc, html, Input, Output, ctx, State, callback, register_page, no_update
from dash.exceptions import PreventUpdate

from dash_src.data_load import load_file_text
from dash_src.data_save import save_performance

register_page(__name__,
              path="/exercise_0_free_read",
              order=2)

INTERVAL_VALUE = 100  # ms

DESCRIPTION_FREE_READ = """
**Free read** lets you read a text at your own natural pace while tracking how long it takes.
This establishes a baseline reading speed and helps you gauge improvement over time.

1. Select a file in the *Text input* page.
2. Press **Start reading** — the full text appears and the timer begins.
3. Read at your own pace.
4. Press **Finish reading** when done — the timer stops and your time is displayed.
"""

## Layout

layout = html.Div(
    [
        dcc.Store("free_timer", data=0),
        dcc.Store("free_word_count", data=0),
        dcc.Interval(id="free_interval", n_intervals=0, interval=INTERVAL_VALUE, disabled=True),

        html.H3("Exercise 0 - Free Read"),
        html.Hr(),

        html.H4("Description"),
        dcc.Markdown(
            children=DESCRIPTION_FREE_READ,
            style={'width': '80%'},
        ),

        html.Hr(),

        html.H4("Exercise"),
        html.Button("Start reading", id="free_start_button", n_clicks=0),

        html.Div([
            dcc.Markdown("Click **Start reading** to display text and begin the timer.", id="free_text"),
        ],
            style={'marginLeft': 20, 'marginRight': 20, 'marginTop': 20, 'marginBottom': 20,
                   'backgroundColor': 'white', 'border': 'thin lightgrey dashed',
                   'padding': '12px', 'whiteSpace': 'pre-wrap', 'lineHeight': '1.8',
                   'fontSize': '15px'}
        ),

        html.Button("Finish reading", id="free_finish_button", n_clicks=0),
        html.Label(id="free_show_time", style={'fontSize': '18px', 'marginTop': '10px', 'display': 'block'}),

        html.Br(),
        html.Button("Save performance", id="free_save_button", n_clicks=0),
        html.Label(id="free_save_feedback", style={'marginLeft': '12px', 'color': 'grey'}),
    ]
)


## Callbacks

@callback(
    Output("free_timer", "data"),
    Input("free_interval", "n_intervals"),
    allow_duplicate=True,
)
def update_timer(n_intervals):
    return INTERVAL_VALUE * n_intervals


@callback(
    Output("free_show_time", "children"),
    Input("free_timer", "data"),
    Input("free_interval", "disabled"),
    allow_duplicate=True,
)
def show_time(data, timer_disabled):
    if timer_disabled and data > 0:
        minutes, rem = divmod(data, 60_000)
        seconds, ms = divmod(rem, 1_000)
        return f"Time taken: {int(minutes)}min {int(seconds)}s {int(ms)}ms"
    return ""


@callback(
    Output("free_text", "children"),
    Output("free_interval", "disabled"),
    Output("free_word_count", "data"),
    Input("free_start_button", "n_clicks"),
    Input("free_finish_button", "n_clicks"),
    State("store_file_selected", "data"),
    prevent_initial_call=True,
)
def update_reading(start_clicks, finish_clicks, file_selected):
    triggered_id = ctx.triggered_id
    if triggered_id == "free_start_button":
        if file_selected:
            text = load_file_text(file_selected[0])
            return text, False, len(text.split())
        return "Select a text in the *Text input* page first.", True, 0
    return "— End of text —", True, no_update


@callback(
    Output("free_save_feedback", "children"),
    Input("free_save_button", "n_clicks"),
    State("free_timer", "data"),
    State("free_word_count", "data"),
    State("store_file_selected", "data"),
    prevent_initial_call=True,
)
def save_free_performance(_, timer_ms, word_count, file_selected):
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
    save_performance("exercise_0_free_read", row)
    return f"Saved  ({row['date']})"
