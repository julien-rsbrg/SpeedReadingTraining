import os
import numpy as np

from dash import dcc, html, Input, Output, State, callback, register_page

import src.browser_notes_base as browser

register_page(__name__,
              path="/text_input",
              order=0)


## Layout

layout = html.Div([
    html.H3("Text Input"),
    html.Hr(),

    html.H4("Parse folder"),
    html.Div([
        html.Label("Folder absolute path:"),
        dcc.Input(
            value=None, type="text",
            placeholder="Folder absolute path...",
            id="input_folder_path",
            style={'width': '60%', 'display': 'block', 'marginBottom': '8px'},
        ),
        html.Label("File extension(s) — separate with a comma (e.g. .txt, .md):"),
        dcc.Input(
            value=None, type="text",
            placeholder="Example: .txt, .md",
            id="input_file_extension",
            style={'width': '60%', 'display': 'block', 'marginBottom': '8px'},
        ),
        html.Button("Parse files", id="parse_button", n_clicks=0),
        html.Label(id="n_files_label", style={'marginLeft': '12px', 'color': 'grey'}),
    ]),

    html.Hr(),

    html.H4("File selection"),
    html.Div([
        dcc.Dropdown(
            options=[], value=None,
            id="file_selection",
            placeholder="Select a file...",
            style={'width': '60%', 'display': 'inline-block'},
        ),
        html.Button(
            "Random selection", id="random_selection_button", n_clicks=0,
            style={'marginLeft': '8px'},
        ),
    ]),
    html.Div([
        html.Label("File path: —", id="file_path_label",
                   style={'display': 'block', 'marginTop': '8px', 'color': 'grey', 'fontSize': '13px'}),
        html.Label("File name: —", id="file_name_label",
                   style={'display': 'block', 'color': 'grey', 'fontSize': '13px'}),
    ]),

    html.Hr(),
])


## Callbacks

@callback(
    Output("store_file_paths", "data"),
    Output("n_files_label", "children"),
    Input("parse_button", "n_clicks"),
    State("input_folder_path", "value"),
    State("input_file_extension", "value"),
)
def launch_file_parsing(_, folder_path, file_extension):
    if folder_path is None or file_extension is None:
        return [], ""
    extensions = [e.strip() for e in file_extension.split(",")]
    all_file_paths = []
    for ext in extensions:
        all_file_paths += browser.parse_all_files(folder_path=folder_path, kept_extension=ext)
    return all_file_paths, f"{len(all_file_paths)} file(s) found"


@callback(
    Output("file_selection", "options"),
    Input("store_file_paths", "data"),
)
def update_file_dropdown(file_paths):
    return file_paths


@callback(
    Output("store_file_selected", "data", allow_duplicate=True),
    Input("file_selection", "value"),
    prevent_initial_call=True,
)
def update_file_selected_dropdown(file_selected):
    if file_selected is None:
        return []
    return [file_selected]


@callback(
    Output("store_file_selected", "data", allow_duplicate=True),
    Input("random_selection_button", "n_clicks"),
    State("store_file_paths", "data"),
    prevent_initial_call=True,
)
def update_file_selected_random(_, file_paths):
    if not file_paths:
        return []
    return [str(np.random.choice(file_paths))]


@callback(
    Output("file_path_label", "children"),
    Output("file_name_label", "children"),
    Input("store_file_selected", "data"),
)
def update_file_selected_label(file_selected):
    if not file_selected:
        return "File path: —", "File name: —"
    return f"File path: {file_selected[0]}", f"File name: {os.path.basename(file_selected[0])}"
