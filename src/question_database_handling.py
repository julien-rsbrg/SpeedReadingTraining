"""
whenever file_path is written, this is meant as from the root of that repository (e.g., absolute path = "<root>/BackToNotes/" + file_path)
"""

import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def save_questions_and_answers(store_MCQ_answers,
                               store_convQ_answers,
                               store_divQ_answers,
                               pred_answers_MCQ,
                               pred_answers_convQ,
                               pred_answers_divQ,
                               MCQ_perf,
                               convQ_perf,
                               divQ_perf,
                               global_perf,
                               speed_perf,
                               original_file_path,
                               dst_path,
                               MCQ_comment="",
                               convQ_comment="",
                               divQ_comment="",
                               global_comment="",
                               speed_comment=""):
    
    new_data = {"path": [original_file_path],
            "administration_date":[pd.to_datetime("today")],
            "MCQ_perf":[MCQ_perf],
            "convQ_perf":[convQ_perf],
            "divQ_perf":[divQ_perf],
            "global_perf":[global_perf],
            "speed (words/min)":[speed_perf],
            "MCQ_comment":[MCQ_comment],
            "convQ_comment":[convQ_comment],
            "divQ_comment":[divQ_comment],
            "global_comment":[global_comment],
            "speed_comment":[speed_comment]
            }
    
    for i in range(len(store_MCQ_answers)):
        new_data[f"MCQ_question_{i}"] = store_MCQ_answers[i]["Question"]
        for j in range(len(store_MCQ_answers[i]["Options"])):
            new_data[f"MCQ_question_{i}_option_{j}"] = store_MCQ_answers[i]["Options"][j]

        new_data[f"MCQ_question_{i}_pred_answer"] = str(pred_answers_MCQ[i])
        new_data[f"MCQ_question_{i}_true_answer"] = store_MCQ_answers[i]["Answer"]

    for i in range(len(store_convQ_answers)):
        new_data[f"convQ_question_{i}"] = store_convQ_answers[i]["Question"]
        new_data[f"convQ_question_{i}_pred_answer"] = pred_answers_convQ[i]
        new_data[f"convQ_question_{i}_true_answer"] = store_convQ_answers[i]["Answer"]
    
    for i in range(len(store_divQ_answers)):
        new_data[f"divQ_question_{i}"] = store_divQ_answers[i]["Question"]
        new_data[f"divQ_question_{i}_pred_answer"] = pred_answers_divQ[i]
        new_data[f"divQ_question_{i}_true_answer"] = store_divQ_answers[i]["Answer"]


    new_data = pd.DataFrame(new_data)

    if os.path.exists(dst_path):
        prev_data = pd.read_csv(dst_path,index_col=0) 
        data = pd.concat([new_data,prev_data],axis=0)
        data = data.reset_index(drop=True)
        data.to_csv(dst_path)
    else:
        new_data.to_csv(dst_path)

    read_data = pd.read_csv(dst_path,index_col=0) 
    print(read_data)


def get_fig_perf_evolution(data,note_path):
    data = data[data["path"] == note_path]

    data = data.dropna(axis=0,subset=["administration_date"])
    mask_null_MCQ_perf = data["MCQ_perf"].isnull()
    mask_null_convQ_perf = data["convQ_perf"].isnull()
    mask_null_divQ_perf = data["divQ_perf"].isnull()
    mask_null_global_perf = data["global_perf"].isnull() 

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data[~mask_null_MCQ_perf]["administration_date"], y=data[~mask_null_MCQ_perf]["MCQ_perf"], mode='lines+markers',name="MCQ performance"))
    fig.add_trace(go.Scatter(x=data[~mask_null_convQ_perf]["administration_date"], y=data[~mask_null_convQ_perf]["convQ_perf"], mode='lines+markers',name="convQ performance"))
    fig.add_trace(go.Scatter(x=data[~mask_null_divQ_perf]["administration_date"], y=data[~mask_null_divQ_perf]["divQ_perf"], mode='lines+markers',name="divQ performance"))
    fig.add_trace(go.Scatter(x=data[~mask_null_global_perf]["administration_date"], y=data[~mask_null_global_perf]["global_perf"], mode='lines+markers',name="global performance"))
    fig.update_layout(title_text = f"Performance evolution on the note: {note_path}")
    
    return fig


def get_fig_perf_speed_evolution(data, note_path):
    data = data[data["path"] == note_path]

    data = data.dropna(axis=0,subset=["administration_date"])
    mask_null_MCQ_perf = data["MCQ_perf"].isnull()
    mask_null_convQ_perf = data["convQ_perf"].isnull()
    mask_null_divQ_perf = data["divQ_perf"].isnull()
    mask_null_global_perf = data["global_perf"].isnull() 
    mask_null_speed = data["speed (words/min)"].isnull()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=data[~mask_null_MCQ_perf]["administration_date"], y=data[~mask_null_MCQ_perf]["MCQ_perf"], mode='lines+markers',name="MCQ performance"),secondary_y=False)
    fig.add_trace(go.Scatter(x=data[~mask_null_convQ_perf]["administration_date"], y=data[~mask_null_convQ_perf]["convQ_perf"], mode='lines+markers',name="convQ performance"),secondary_y=False)
    fig.add_trace(go.Scatter(x=data[~mask_null_divQ_perf]["administration_date"], y=data[~mask_null_divQ_perf]["divQ_perf"], mode='lines+markers',name="divQ performance"),secondary_y=False)
    fig.add_trace(go.Scatter(x=data[~mask_null_global_perf]["administration_date"], y=data[~mask_null_global_perf]["global_perf"], mode='lines+markers',name="global performance"),secondary_y=False)
    fig.add_trace(go.Scatter(x=data[~mask_null_global_perf]["administration_date"], y=data[~mask_null_speed]["speed (words/min)"], mode='lines+markers',name="speed (word/min)"),secondary_y=True)
    
    fig.update_layout(title_text = f"Performance evolution on the note: {note_path}")
    fig.update_yaxes(title_text="Reading comprehension performance", secondary_y=False)
    fig.update_yaxes(title_text="Speed (words/min)", secondary_y=True)
    
    return fig


if __name__ == "__main__":
    import numpy as np


    store_MCQ_answers = [{'Question': 'Which type of machine learning involves training with labeled data?', 'Options': ['a) A. Reinforcement learning', 'b) B. Unsupervised learning', 'c) C. Supervised learning', 'd) D. Quantum learning'], 'Answer': 'c) C. Supervised learning'}]
    store_convQ_answers = [{"Question":"convQ0","Answer":"answer convQ0"},{"Question":"convQ1","Answer":"answer convQ1"}]
    store_divQ_answers = [{"Question":"divQ0","Answer":"answer divQ0"},{"Question":"divQ1","Answer":"answer divQ0"}]

    pred_answers_MCQ = ['c) C. Supervised learning']
    pred_answers_convQ = ['pred answer convQ0','pred answer convQ1']
    pred_answers_divQ = ['pred answer divQ0','pred answer divQ1']

    save_questions_and_answers(store_MCQ_answers,
                               store_convQ_answers,
                               store_divQ_answers,
                               pred_answers_MCQ,
                               pred_answers_convQ,
                               pred_answers_divQ,
                               MCQ_perf=np.random.randint(0,1),
                               convQ_perf=np.random.randint(0,6),
                               divQ_perf=np.random.randint(0,2),
                               global_perf=np.random.randint(0,3),
                               speed_perf=np.random.randn()*50 + 200,
                               original_file_path="texts/text_1.txt",
                               dst_path='test_save.csv')
    read_data = pd.read_csv('test_save.csv',index_col=0) 
    fig = get_fig_perf_speed_evolution(read_data, note_path="texts/text_1.txt")
    
    fig.show()

    
