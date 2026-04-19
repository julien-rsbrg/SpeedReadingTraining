import os
import copy

import pandas as pd
import numpy as np
import networkx as nx

from dash import dcc, html, Input, Output, State, callback, register_page, dash_table
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

import dash_src.display as display
import dash_src.utils as utils

from dash_src.configs.main import config
import src.browser_notes_base as browser
from src.question_database_handling import get_fig_perf_evolution, save_questions_and_answers

from src.LLM_functions import generate_multichoice_questions, generate_convergent_questions, generate_divergent_questions
from dash_src.data_load import load_file_text

register_page(__name__, 
              path="/exercise_3_fixation_points",
              order=2)

PERFORMANCE_MARKS = {0: "very poor",
                    1: "poor",
                    2: "quite poor",
                    3: "good",
                    4: "very good",
                    5: "great"}

QA_FILE_PATH = "test_save.csv"


## Layout

layout = html.Div(
    [   
        html.H3("Parse the notes base"),
        html.Center(
            dcc.Markdown(
                children=
                """
                <span style="color:red">
                Text content
                </span>
                """,
                style={'color': 'black', 'background-color': 'white',"text-align":"right"}
        )),
        html.Center(
            dcc.Markdown(
                children=
                """
                <span style="color:red">
                Text content
                </span>..........             
                """,
                style={'color': 'black', 'background-color': 'white',"text-align":"right"}
        ))

        
    ]   
)


## Callbacks   