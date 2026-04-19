import os

from openai import OpenAI
import json

from dotenv import load_dotenv

load_dotenv()
api_key_value = os.getenv("OPENAI_API_KEY")


def generate_multichoice_questions(text, n_questions, n_options = 4, user_spec = "", api_key = api_key_value):
    """
    Returns:
        X (something): JSON dictionary containing the title and abstract.
    """


    assert n_options < 6

    if len(user_spec) > 0:
        _user_spec = ". Additionally, "+ user_spec
    else:
        _user_spec = "."
    
    prompt = f"""
    Your task is to output {n_questions} multiple choice questions as well as their answers. There should be {n_options} options. The questions' answers should be coming from the following text{_user_spec}
    
    Text:
    {text}
    
    The output should be in JSON format as shown below:
    {{
      "question_id": {{
        "Question": "...",
        "Options": "...",
        "Answer": "..."
      }}
    }}
    """
    
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a machine learning expert."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"}
    )
    out = json.loads(completion.choices[0].message.content)
    print("raw MCQ:\n",out)

    # ensure outputs and answer are numeroted
    potential_numerotation = ["a)","b)","c)","d)","e)","f)"]
    Potential_Numerotation = ["A)","B)","C)","D)","E)","F)"]
    for k in out:
        new_options = []
        for i,single_option in enumerate(out[k]["Options"]):
            if len(single_option) < 2 or not(single_option[:2] in potential_numerotation or single_option[:2] in Potential_Numerotation):
                _option = potential_numerotation[i] + " " + single_option
            else:
                _option = single_option

            new_options.append(_option)

            if single_option == out[k]["Answer"] and (len(out[k]["Answer"]) < 2 or not(out[k]["Answer"][:2] in potential_numerotation)):
                out[k]["Answer"] = potential_numerotation[i] + " " + out[k]["Answer"]
        
        out[k]["Options"] = new_options

    return out



def generate_convergent_questions(text, n_questions, user_spec = "", api_key = api_key_value):
    """
    Returns:
        X (something): JSON dictionary containing the title and abstract.
    """

    if len(user_spec) > 0:
        _user_spec = ". Additionally, "+ user_spec
    else:
        _user_spec = ":"
    
    prompt = f"""
    Your task is to output {n_questions} questions as well as their answers. The questions' answers should be explicitly coming from the following text: 
    
    Text:
    {text}
    
    The output should be in JSON format as shown below:
    {{
      "question_id": {{
        "Question": "...",
        "Answer": "..."
      }}
    }}
    """
    
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a machine learning expert."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)



def generate_divergent_questions(text, n_questions, user_spec = "", api_key = api_key_value):
    """
    Returns:
        X (something): JSON dictionary containing the title and abstract.
    """
    if len(user_spec) > 0:
        _user_spec = ". Additionally, "+ user_spec
    else:
        _user_spec = ":"

    prompt = f"""
    Your task is to output {n_questions} questions as well as their answers. The questions should relate to the topic of the following text but are divergent, ie the reader may have to extrapolate or infer to find the answer{_user_spec}: 
    
    Text:
    {text}
    
    The output should be in JSON format as shown below:
    {{
      "question_id": {{
        "Question": "...",
        "Answer": "..."
      }}
    }}
    """
    
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a machine learning expert."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)



if __name__ == "__main__":
    f = open("test/single_note.txt", "r")
    text = f.read()
    print(text, type(text), len(text), len(text.split(" ")))
    f.close()

    n_questions = 3
    

    out_json = generate_multichoice_questions(text,n_questions=n_questions)
    print(out_json)

    out_json = generate_convergent_questions(text,n_questions=n_questions)
    print(out_json)

    out_json = generate_divergent_questions(text,n_questions=n_questions)
    print(out_json)



