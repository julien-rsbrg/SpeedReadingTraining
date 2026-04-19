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
              path="/questionnaire",
              order=5)

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
        dcc.Store("store_file_paths",data=[]),
        dcc.Store("store_file_selected",data=[]),

        html.H3("Parse the notes base"),
        html.Label("Folder absolute path:"),
        html.Div(
            [
                dcc.Input(
                    value = None,
                    type = "text",
                    placeholder = "Folder absolute path...",
                    id = "input_folder_path",
                    style={'width': '60%', 'display': 'inline-block'}
                ),
            ]
        ),

        html.Label("File extension (.txt, .md...) (if several, separate with a coma ','):"),
        html.Div(
            [
                dcc.Input(
                    value = None,
                    type = "text",
                    placeholder = "Example: .txt, .md",
                    id = "input_file_extension",
                    style={'width': '60%', 'display': 'inline-block'}
                ),
        ]),
        
        html.Button('Parse files', id='parse_button', n_clicks=0),
        html.Br(),

        html.H3("Files description"),

        html.Label(id="n_files_label"),

        html.Div(
            [
                dcc.Graph(
                    id='files_disc_plot',
                    style={'width': '25%', 'display': 'inline-block'}),

                dcc.Graph(
                    id='files_perf_plot', 
                    style={'width': '75%', 'display': 'inline-block'}),
            ]
        ),

        

        html.Hr(),

        html.H3("File selection"),

        

        html.Label("Select a file to study or click on the button for a random selection:"),
        html.Div(
            [
                dcc.Dropdown(
                    options = [], 
                    value = None, 
                    id='file_selection',
                    style={'width': '40%', 'display': 'inline-block'}),

                html.Button(
                    'Random selection', 
                    id='random_selection_button', 
                    n_clicks=0,
                    style={'width': '20%', 'display': 'inline-block'}),
            ]
        ),

        html.H5("Description file selected"),

        html.Div(
            [
                html.Label("File path:",
                           id = "file_path_label",
                           style={'width': '40%', 'display': 'inline-block'}),
                html.Label("File name:",
                           id = "file_name_label",
                           style={'width': '40%', 'display': 'inline-block'}),
            ]
        ),


        dcc.Graph(
            id='selected_file_perf_evolution_plot', 
            style={'width': '75%', 'display': 'inline-block'}),

        dcc.Graph(
            id='selected_file_perf_distrib_plot', 
            style={'width': '25%', 'display': 'inline-block'}),

        html.Hr(),
        ### Multiple Choice Questions

        dcc.Store("store_MCQ_answers",data=[]),
        dcc.Store("store_MCQ_pred_answers",data=[]),

        html.H3("Multiple Choice Questions"),
        html.Label("Number of questions to generate:"),
        html.Div(
            [
                dcc.Slider(1, 
                   10, 
                   step = 1,
                   value = 5,
                   id= 'n_questions_MCQ'
                   )
            ],
            style={'width': '40%', 'display': 'inline-block'}
        ),
        html.Br(),
        html.Button("Generate questions",
                    id="button_MCQ"),
        html.Label(id="MCQ_feedback"),

        html.Div([],
                id = "question_field_MCQ",
                style={'width': '100%', 'display': 'inline-block'}
        ),
        html.Button("Show MCQ's answers",
                    id="button_show_MCQ_answers"),

        dcc.Checklist(
            options = ["Show self-ratings"],
            value = [],
            id = "checklist_self-rating_MCQ"
        ),

        html.Div([
            html.Label("Overall performance on MCQ"),
            html.Div([
                dcc.Slider(min = 0, 
                    max = 5, 
                    step = 1,
                    marks = PERFORMANCE_MARKS,
                    value = 5,
                    id= 'performance_MCQ'
                )],
                style={'width': '40%', 'display': 'inline-block'}
            ),
            html.Br(),
            html.Label("Comment"),
            dcc.Textarea(
                style={'width': '80%'},
                id = "comment_MCQ"
            ),
        ], id = "block_perf_MCQ", style={"display":'none'}),

        html.Hr(),
        ### Convergent questions

        dcc.Store("store_convQ_answers",data=[]),
        dcc.Store("store_convQ_pred_answers",data=[]),

        html.H3("Convergent Questions"),
        html.Label("Number of questions to generate:"),
        html.Div(
            [
                dcc.Slider(1, 
                   10, 
                   step = 1,
                   value = 5,
                   id= 'n_questions_convQ'
                   )
            ],
            style={'width': '40%', 'display': 'inline-block'}
        ),
        html.Br(),
        html.Button("Generate questions",
                    id="button_convQ"),
        html.Label(id="convQ_feedback"),

        html.Div([],
                id = "question_field_convQ",
                style={'width': '100%', 'display': 'inline-block'}
        ),
        html.Button("Show questions' answers",
                    id="button_show_convQ_answers"),
        dcc.Checklist(
            options = ["Show self-ratings"],
            value = [],
            id = "checklist_self-rating_convQ"
        ),
        
        html.Div([
            html.Label("Overall performance on convergent questions"),
            html.Div([
                dcc.Slider(min = 0, 
                    max = 5, 
                    step = 1,
                    marks = PERFORMANCE_MARKS,
                    value = 5,
                    id= 'performance_convQ'
                )],
                style={'width': '40%', 'display': 'inline-block'}
            ),
            html.Br(),
            html.Label("Comment"),
            dcc.Textarea(
                style={'width': '80%'},
                id = "comment_convQ"
            ),
        ], id = "block_perf_convQ", style={"display":'none'}),
        

        html.Hr(),
        ### Divergent questions

        dcc.Store("store_divQ_answers",data=[]),
        dcc.Store("store_divQ_pred_answers",data=[]),

        html.H3("Divergent Questions"),
        html.Label("Number of questions to generate:"),
        html.Div(
            [
                dcc.Slider(1, 
                   10, 
                   step = 1,
                   value = 5,
                   id= 'n_questions_divQ'
                   )
            ],
            style={'width': '40%', 'display': 'inline-block'}
        ),
        html.Br(),
        html.Button("Generate questions",
                    id="button_divQ"),
        html.Label(id="divQ_feedback"),

        html.Div([],
                id = "question_field_divQ",
                style={'width': '100%', 'display': 'inline-block'}
        ),
        html.Button("Show questions' answers",
                    id="button_show_divQ_answers"),

        dcc.Checklist(
            options = ["Show self-ratings"],
            value = [],
            id = "checklist_self-rating_divQ"
        ),

        html.Div([
            html.Label("Overall performance on divergent questions"),
            html.Div([
                dcc.Slider(min = 0, 
                    max = 5, 
                    step = 1,
                    marks = PERFORMANCE_MARKS,
                    value = 5,
                    id= 'performance_divQ'
                )],
                style={'width': '40%', 'display': 'inline-block'}
            ),
            html.Br(),
            html.Label("Comment"),
            dcc.Textarea(
                style={'width': '80%'},
                id = "comment_divQ"
            ),
        ], id = "block_perf_divQ", style={"display":'none'}),

        # Global self-evaluation

        html.Hr(),
        html.H3("Global self-rating"),
        dcc.Markdown(id="global_evaluation_report",style={"width":"80%"}),
        dcc.Markdown("**Overall performance**"),
        html.Div([
            dcc.Slider(min = 0, 
                max = 5, 
                step = 1,
                marks = PERFORMANCE_MARKS,
                value = 5,
                id= 'performance_global'
                )
            ],
            style={'width': '40%', 'display': 'inline-block'}
        ),
        html.Br(),
        html.Label("Global comment"),
        dcc.Textarea(
            id="comment_global",
            style={'width': '80%'},
        ),

        html.Br(),
        html.Button('Save  this test and its results', id='button_global_save', n_clicks=0),
    ]   
)


## Callbacks   

@callback(
    Output("store_file_paths","data"),
    Output("n_files_label","children"),
    Input("parse_button","n_clicks"),
    State("input_folder_path","value"),
    State("input_file_extension","value")
)
def launch_file_parsing(n_clicks, folder_path, file_extension):
    if folder_path is None or file_extension is None:
        return [], None
    
    allowed_file_extensions = file_extension.strip(" ").split(",")

    all_file_paths = []
    for file_extension in allowed_file_extensions:
        file_paths = browser.parse_all_files(folder_path=folder_path,kept_extension=file_extension)
        all_file_paths += file_paths

    return all_file_paths, "Number of files found:"+str(len(all_file_paths))


@callback(
    Output("files_disc_plot","figure"),
    Input("store_file_paths","data")
)
def plot_tested_distribution(file_paths):
    data = pd.read_csv(QA_FILE_PATH,index_col=0) 
    
    n_files = len(file_paths)
    n_tested = 0
    for path in file_paths:
        n_tested += int((data["path"] == path).sum() > 0)

    labels = ["tested","not tested"]
    values = [n_tested, n_files - n_tested]
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values,
        textinfo='label+value+percent',
        pull=[0.2, 0.0])])
    fig.update(layout_showlegend=False)
    fig.update_layout(title_text = "Ratio of tested and not tested notes")
    return fig


@callback(
    Output("files_perf_plot","figure"),
    Input("store_file_paths","data")   
)
def plot_overview_files_performance(file_paths):
    fig = go.Figure()
    fig.update_layout(title_text = "Performance on the notes")

    if len(file_paths) == 0:
        return fig

    data = pd.read_csv(QA_FILE_PATH,index_col=0) 
    last_ids = data.groupby('path')['administration_date'].transform(max) == data['administration_date']
    data = data[last_ids]

    data =  data[data["path"].isin(file_paths)]
        
    fig.add_trace(go.Violin(y=data['MCQ_perf'],
                            name="MCQ",
                            side='positive',
                            box_visible=True,
                            pointpos=-0.25,
                            showlegend=True,
                            text = data['path'].apply(lambda v: os.path.basename(v)),
                            hoverinfo='text+y'
                        )
    )

    fig.add_trace(go.Violin(y=data['convQ_perf'],
                            name="convQ_perf",
                            side='positive',
                            box_visible=True,
                            pointpos=-0.25,
                            showlegend=True,
                            text = data['path'].apply(lambda v: os.path.basename(v)),
                            hoverinfo='text+y'
                        )
    )

    fig.add_trace(go.Violin(y=data['divQ_perf'],
                            name="divQ_perf",
                            side='positive',
                            box_visible=True,
                            pointpos=-0.25,
                            showlegend=True,
                            text = data['path'].apply(lambda v: os.path.basename(v)),
                            hoverinfo='text+y'
                        )
    )

    fig.add_trace(go.Violin(y=data['global_perf'],
                            name="global_perf",
                            side='positive',
                            box_visible=True,
                            pointpos=-0.25,
                            showlegend=True,
                            text = data['path'].apply(lambda v: os.path.basename(v)),
                            hoverinfo='text+y'
                        )
    )

    fig.update_traces(meanline_visible=True,
                    points='all', # show all points
                    jitter=0.05,  # add some jitter on points for better visibility
                    scalemode='count') #scale violin plot area with total count
    
    fig.update_layout(title_text = "Performance on the notes")

    return fig





@callback(
    Output("file_selection","options"),
    Input("store_file_paths","data")
)
def update_file_dropdown(file_paths):
    return file_paths


@callback(
    Output("store_file_selected","data",allow_duplicate=True),
    Input("file_selection","value"),
    prevent_initial_call=True
)
def update_file_selected_dropdown(file_selected):
    if file_selected is None:
        return []
    return [file_selected]

@callback(
    Output("store_file_selected","data",allow_duplicate=True),
    Input("random_selection_button","n_clicks"),
    State("store_file_paths","data"),
    prevent_initial_call=True
)
def update_file_selected_random(n_clicks,file_paths):    
    path_selected = str(np.random.choice(file_paths))
    return [path_selected]

@callback(
    Output("file_path_label","children"),
    Output("file_name_label","children"),
    Input("store_file_selected","data")
)
def update_file_selected_label(store_file_selected):
    if len(store_file_selected) == 0:
        return "File path:...", "File title:..."
    
    else:
        message_path = "File path: "+store_file_selected[0]
        message_title = "File title: "+os.path.basename(store_file_selected[0])
        return message_path,message_title



@callback(
    Output("selected_file_perf_evolution_plot","figure"),
    Input("store_file_selected","data")   
)
def plot_selected_file_performance_evolution(file_selected):
    if len(file_selected) == 0:
        fig = go.Figure()
        fig.update_layout(title_text = "Performance evolution on the note: ...")
        return fig

    data = pd.read_csv(QA_FILE_PATH,index_col=0)
    fig = get_fig_perf_evolution(data,file_selected[0])
    return  fig



@callback(
    Output("selected_file_perf_distrib_plot","figure"),
    Input("store_file_selected","data")   
)
def plot_selected_file_performance_distribution(file_selected):
    fig = go.Figure()

    if len(file_selected) == 0:
        fig.update_layout(title_text = "Performance on the note: ...")
        return fig

    fig.update_layout(title_text = f"Performance on the note: {file_selected[0]}")

    data = pd.read_csv(QA_FILE_PATH,index_col=0) 
    data = data[data["path"] == file_selected[0]]
        
    fig.add_trace(go.Violin(y=data['MCQ_perf'],
                            name="MCQ",
                            side='positive',
                            box_visible=True,
                            pointpos=-0.25,
                            showlegend=True,
                            text = data['path'].apply(lambda v: os.path.basename(v)),
                            hoverinfo='text+y'
                        )
    )

    fig.add_trace(go.Violin(y=data['convQ_perf'],
                            name="convQ_perf",
                            side='positive',
                            box_visible=True,
                            pointpos=-0.25,
                            showlegend=True,
                            text = data['path'].apply(lambda v: os.path.basename(v)),
                            hoverinfo='text+y'
                        )
    )

    fig.add_trace(go.Violin(y=data['divQ_perf'],
                            name="divQ_perf",
                            side='positive',
                            box_visible=True,
                            pointpos=-0.25,
                            showlegend=True,
                            text = data['path'].apply(lambda v: os.path.basename(v)),
                            hoverinfo='text+y'
                        )
    )

    fig.add_trace(go.Violin(y=data['global_perf'],
                            name="global_perf",
                            side='positive',
                            box_visible=True,
                            pointpos=-0.25,
                            showlegend=True,
                            text = data['path'].apply(lambda v: os.path.basename(v)),
                            hoverinfo='text+y'
                        )
    )

    fig.update_traces(meanline_visible=True,
                    points='all',
                    jitter=0.05,
                    scalemode='count')

    return fig



# MCQ

@callback(
    Output("MCQ_feedback","children"),
    Input("button_MCQ","n_clicks"),
    State("store_file_selected","data"),
    prevent_initial_call = True
)
def feedback_MCQ(n_clicks,file_selected):
    if len(file_selected) == 0:
        return "Start by selecting a file."
    else:
        return "Generating MCQ..."

@callback(
    Output("question_field_MCQ","children",allow_duplicate=True),
    Output("store_MCQ_answers","data"),
    Input("MCQ_feedback","children"),
    State("store_file_selected","data"),
    State("n_questions_MCQ","value"),
    prevent_initial_call = True
)
def generate_MCQ(feedback_changed, file_selected, n_questions):
    if len(file_selected) == 0:
        return [], []

    def generate_one_question(question,options):
        one_question = []
        one_question.append(html.H6(question))
        one_question.append(dcc.Checklist(
            options,
            []
        ))
        one_question.append(html.Label()) # empty for the true answer
        return one_question
    
    text_file = load_file_text(file_selected[0])

    MCQ = generate_multichoice_questions(text_file,n_questions=n_questions)
    
    children_UI = []
    store_answers = []
    for single_QOA in MCQ.values():
        print("single_QOA:\n",single_QOA)
        question = single_QOA["Question"]
        options = single_QOA["Options"]
        answer = single_QOA["Answer"]
        children_UI += generate_one_question(question,options)
        store_answers.append({"Question":question,"Options":options,"Answer":answer})

    return children_UI, store_answers

@callback(
    Output("question_field_MCQ","children",allow_duplicate=True),
    Input("button_show_MCQ_answers","n_clicks"),
    State("store_MCQ_answers","data"),
    State("question_field_MCQ","children"),
    prevent_initial_call = True
)
def show_MCQ_answers(n_clicks,stored_MCQ_answers, question_field):
    if len(stored_MCQ_answers) == 0:
        return []
    
    def generate_one_QOA(question,options,pred_answer,true_answer):
        print("question,options,pred_answer,true_answer\n",
              question,options,pred_answer,true_answer)
        one_QOA = []
        one_QOA.append(html.H6(question))

        checklist = dcc.Checklist(
            options=options,
            value=pred_answer
        )

        one_QOA.append(checklist)
        one_QOA.append(html.Label("True answer: "+true_answer,
                                  style={'color': 'blue'}))

        return one_QOA

    children_UI = []
    for question_id in range(0,len(question_field),3):
        question_txt = question_field[question_id]["props"]["children"]
        options = copy.deepcopy(question_field[question_id+1]["props"]["options"])
        pred_answer = copy.deepcopy(question_field[question_id+1]["props"]["value"])

        assert stored_MCQ_answers[question_id//3]["Question"] == question_txt
        true_answer = stored_MCQ_answers[question_id//3]["Answer"]
        
        children_UI += generate_one_QOA(question_txt,options,pred_answer,true_answer)

    return children_UI


@callback(
    Output('block_perf_MCQ', 'style'),
    Input("checklist_self-rating_MCQ","value"),
    prevent_initial_call = True
)
def show_personal_comment_MCQ(checklist_value):
    if checklist_value == []:
        return {"display":"none"}
    elif checklist_value == ["Show self-ratings"]:
        return {"display":"block"}


@callback(
    Output("store_MCQ_pred_answers","data"),
    Input("question_field_MCQ","children"),
    prevent_initial_call = True
)
def store_MCQ_pred_answers(question_field):
    MCQ_pred_answers = []
    for question_id in range(0,len(question_field),3):
        pred_answer = copy.deepcopy(question_field[question_id+1]["props"]["value"])
        MCQ_pred_answers.append(pred_answer)
    
    print("MCQ_pred_answers\n",MCQ_pred_answers)
    return MCQ_pred_answers


# convQ

@callback(
    Output("convQ_feedback","children"),
    Input("button_convQ","n_clicks"),
    State("store_file_selected","data"),
    prevent_initial_call = True
)
def feedback_convQ(n_clicks,file_selected):
    if len(file_selected) == 0:
        return "Start by selecting a file."
    else:
        return "Generating convergent questions..."

@callback(
    Output("question_field_convQ","children",allow_duplicate=True),
    Output("store_convQ_answers","data"),
    Input("convQ_feedback","children"),
    State("store_file_selected","data"),
    State("n_questions_convQ","value"),
    prevent_initial_call = True
)
def generate_convQ(feedback_changed, file_selected, n_questions):
    if len(file_selected) == 0:
        return [], []

    def generate_one_question(question):
        one_question = []
        one_question.append(html.H6(question))
        one_question.append(dcc.Textarea(
            placeholder = "Your answer...",
            style = {'width': '100%', "height": 100,'display': 'inline-block'}
        ))
        one_question.append(html.Label()) # empty for the true answer
        return one_question
    
    text_file = load_file_text(file_selected[0])

    conv_questions = generate_convergent_questions(text_file,n_questions=n_questions)
    
    children_UI = []
    store_answers = []
    for single_QA in conv_questions.values():
        print("single_QA:\n",single_QA)
        question = single_QA["Question"]
        answer = single_QA["Answer"]
        children_UI += generate_one_question(question)
        store_answers.append({"Question":question,"Answer":answer})

    return children_UI, store_answers

@callback(
    Output("question_field_convQ","children",allow_duplicate=True),
    Input("button_show_convQ_answers","n_clicks"),
    State("store_convQ_answers","data"),
    State("question_field_convQ","children"),
    prevent_initial_call = True
)
def show_convQ_answers(n_clicks,stored_convQ_answers, question_field):
    if len(stored_convQ_answers) == 0:
        return []
    
    def generate_one_QA(question,pred_answer,true_answer):
        print("question,pred_answer,true_answer\n",
              question,pred_answer,true_answer)
        one_QA = []
        one_QA.append(html.H6(question))

        pred_answer_input = dcc.Textarea(
            value=pred_answer,
            placeholder = "Your answer...",
            style = {'width': '100%', "height": 100,'display': 'inline-block'}
        )

        one_QA.append(pred_answer_input)
        one_QA.append(html.Label("True answer: "+true_answer,
                                  style={'color': 'blue'}))

        return one_QA

    children_UI = []
    for question_id in range(0,len(question_field),3):
        question_txt = question_field[question_id]["props"]["children"]
        print("question_field[question_id+1]",question_field[question_id+1])
        if "value" in question_field[question_id+1]["props"]:
            pred_answer = copy.deepcopy(question_field[question_id+1]["props"]["value"])
        else:
            pred_answer = None

        assert stored_convQ_answers[question_id//3]["Question"] == question_txt
        true_answer = stored_convQ_answers[question_id//3]["Answer"]
        
        children_UI += generate_one_QA(question_txt,pred_answer,true_answer)

    return children_UI



@callback(
    Output('block_perf_convQ', 'style'),
    Input("checklist_self-rating_convQ","value"),
    prevent_initial_call = True
)
def show_personal_comment_convQ(checklist_value):
    if checklist_value == []:
        return {"display":"none"}
    elif checklist_value == ["Show self-ratings"]:
        return {"display":"block"}


@callback(
    Output("store_convQ_pred_answers","data"),
    Input("question_field_convQ","children"),
    prevent_initial_call = True
)
def store_convQ_pred_answers(question_field):
    convQ_pred_answers = []
    for question_id in range(0,len(question_field),3):
        if "value" in question_field[question_id+1]["props"]:
            pred_answer = copy.deepcopy(question_field[question_id+1]["props"]["value"])
        else:
            pred_answer = None
        convQ_pred_answers.append(pred_answer)

    print("convQ_pred_answers\n",convQ_pred_answers)
    return convQ_pred_answers


# divQ

@callback(
    Output("divQ_feedback","children"),
    Input("button_divQ","n_clicks"),
    State("store_file_selected","data"),
    prevent_initial_call = True
)
def feedback_divQ(n_clicks,file_selected):
    if len(file_selected) == 0:
        return "Start by selecting a file."
    else:
        return "Generating divergent questions..."

@callback(
    Output("question_field_divQ","children",allow_duplicate=True),
    Output("store_divQ_answers","data"),
    Input("divQ_feedback","children"),
    State("store_file_selected","data"),
    State("n_questions_divQ","value"),
    prevent_initial_call = True
)
def generate_divQ(feedback_changed, file_selected, n_questions):
    if len(file_selected) == 0:
        return [], []

    def generate_one_question(question):
        one_question = []
        one_question.append(html.H6(question))
        one_question.append(dcc.Textarea(
            placeholder = "Your answer...",
            style = {'width': '100%', "height": 100,'display': 'inline-block'}
        ))
        one_question.append(html.Label()) # empty for the true answer
        return one_question
    
    text_file = load_file_text(file_selected[0])

    conv_questions = generate_divergent_questions(text_file,n_questions=n_questions)
    
    children_UI = []
    store_answers = []
    for single_QA in conv_questions.values():
        print("single_QA:\n",single_QA)
        question = single_QA["Question"]
        answer = single_QA["Answer"]
        children_UI += generate_one_question(question)
        store_answers.append({"Question":question,"Answer":answer})

    return children_UI, store_answers

@callback(
    Output("question_field_divQ","children",allow_duplicate=True),
    Input("button_show_divQ_answers","n_clicks"),
    State("store_divQ_answers","data"),
    State("question_field_divQ","children"),
    prevent_initial_call = True
)
def show_divQ_answers(n_clicks,stored_divQ_answers, question_field):
    if len(stored_divQ_answers) == 0:
        return []
    
    def generate_one_QA(question,pred_answer,true_answer):
        print("question,pred_answer,true_answer\n",
              question,pred_answer,true_answer)
        one_QA = []
        one_QA.append(html.H6(question))

        pred_answer_input = dcc.Textarea(
            value=pred_answer,
            placeholder = "Your answer...",
            style = {'width': '100%', "height": 100,'display': 'inline-block'}
        )

        one_QA.append(pred_answer_input)
        one_QA.append(html.Label("True answer: "+true_answer,
                                  style={'color': 'blue'}))

        return one_QA

    children_UI = []
    for question_id in range(0,len(question_field),3):
        question_txt = question_field[question_id]["props"]["children"]
        print("question_field[question_id+1]",question_field[question_id+1])
        if "value" in question_field[question_id+1]["props"]:
            pred_answer = copy.deepcopy(question_field[question_id+1]["props"]["value"])
        else:
            pred_answer = None

        assert stored_divQ_answers[question_id//3]["Question"] == question_txt
        true_answer = stored_divQ_answers[question_id//3]["Answer"]
        
        children_UI += generate_one_QA(question_txt,pred_answer,true_answer)

    return children_UI


@callback(
    Output('block_perf_divQ', 'style'),
    Input("checklist_self-rating_divQ","value"),
    prevent_initial_call = True
)
def show_personal_comment_divQ(checklist_value):
    if checklist_value == []:
        return {"display":"none"}
    elif checklist_value == ["Show self-ratings"]:
        return {"display":"block"}


@callback(
    Output("store_divQ_pred_answers","data"),
    Input("question_field_divQ","children"),
    prevent_initial_call = True
)
def store_divQ_pred_answers(question_field):
    divQ_pred_answers = []
    for question_id in range(0,len(question_field),3):
        if "value" in question_field[question_id+1]["props"]:
            pred_answer = copy.deepcopy(question_field[question_id+1]["props"]["value"])
        else:
            pred_answer = None
        divQ_pred_answers.append(pred_answer)
    
    print("divQ_pred_answers\n",divQ_pred_answers)
    return divQ_pred_answers

### Global self-rating
@callback(
        Output("global_evaluation_report","children"),
        Input("performance_MCQ","value"),
        Input("comment_MCQ","value"),
        State("store_MCQ_answers","data"),
        State("store_MCQ_pred_answers","data"),
        Input("performance_convQ","value"),
        Input("comment_convQ","value"),
        State("store_convQ_answers","data"),
        State("store_convQ_pred_answers","data"),
        Input("performance_divQ","value"),
        Input("comment_divQ","value"),
        State("store_divQ_answers","data"),
        State("store_divQ_pred_answers","data"),
        prevent_initial_call = True
)
def update_global_report(perf_MCQ,
                         comment_MCQ,
                         answers_MCQ,
                         pred_answers_MCQ,
                         perf_convQ,
                         comment_convQ,
                         answers_convQ,
                         pred_answers_convQ,
                         perf_divQ,
                         comment_divQ,
                         answers_divQ,
                         pred_answers_divQ):
    def get_emoji(perf):
        # check https://emojidb.org/python-emojis
        if perf == 5:
            return "🌟"
        elif perf == 4:
            return "🚀"
        elif perf == 3:
            return "😃"
        elif perf == 2:
            return "😐"
        elif perf == 1:
            return "🤏"
        elif perf == 0:
            return "❗"
    print("comment_MCQ",comment_MCQ)

    message = f"""
        **Multiple Choice Questions**
            
        - overall performance: {PERFORMANCE_MARKS[perf_MCQ]+ " ("+str(perf_MCQ)+'/5) '+get_emoji(perf_MCQ)}
        - comment: {comment_MCQ}
        - recording: {len(answers_MCQ)} questions  vs {len(pred_answers_MCQ)} answers
            
        **Convergent Questions**

        - overall performance: {PERFORMANCE_MARKS[perf_convQ]+ " ("+str(perf_convQ)+'/5) '+get_emoji(perf_convQ)}
        - comment: {comment_convQ}
        - recording: {len(answers_convQ)} questions  vs {len(pred_answers_convQ)} answers

        **Divergent Questions**

        - overall performance: {PERFORMANCE_MARKS[perf_divQ]+ " ("+str(perf_divQ)+'/5) '+get_emoji(perf_divQ)}
        - comment: {comment_divQ}
        - recording: {len(answers_divQ)} questions  vs {len(pred_answers_divQ)} answers
    """
    
    return message


@callback(
    Input("button_global_save","n_clicks"),
    State("store_file_selected","data"),
    State("store_MCQ_answers","data"),
    State("performance_MCQ","value"),
    State("comment_MCQ","value"),
    State("store_MCQ_pred_answers","data"),
    State("store_convQ_answers","data"),
    State("performance_convQ","value"),
    State("comment_convQ","value"),
    State("store_convQ_pred_answers","data"),
    State("store_divQ_answers","data"),
    State("performance_divQ","value"),
    State("comment_divQ","value"),    
    State("store_divQ_pred_answers","data"),
    State("performance_global","value"),
    State("comment_global","value")
)
def launch_save_test(n_clicks,
                     file_selected,
                     store_MCQ_answers,
                     perf_MCQ,
                     comment_MCQ,
                     pred_answers_MCQ,
                     store_convQ_answers,
                     perf_convQ,
                     comment_convQ,
                     pred_answers_convQ,
                     store_divQ_answers,
                     perf_divQ,
                     comment_divQ,
                     pred_answers_divQ,
                     perf_global,
                     comment_global):
    if len(file_selected) > 0:
        save_questions_and_answers(
            store_MCQ_answers = store_MCQ_answers,
            store_convQ_answers = store_convQ_answers,
            store_divQ_answers = store_divQ_answers,
            pred_answers_MCQ = pred_answers_MCQ,
            pred_answers_convQ = pred_answers_convQ,
            pred_answers_divQ = pred_answers_divQ,
            MCQ_perf = perf_MCQ if len(store_MCQ_answers) else None,
            convQ_perf = perf_convQ if len(store_convQ_answers) else None,
            divQ_perf = perf_divQ if len(store_divQ_answers) else None,
            global_perf = perf_global,
            MCQ_comment=comment_MCQ,
            convQ_comment = comment_convQ,
            divQ_comment = comment_divQ,
            global_comment = comment_global,
            original_file_path = file_selected[0],
            dst_path = QA_FILE_PATH                
        )
    