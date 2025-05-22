"""
    Sample Usage:
        python gpt4_group_criteria.py --text_file "./texts/your_text_file.txt" --result_base_dir "./output_json_files"
"""

import argparse
from tqdm import tqdm
from dotenv import load_dotenv, find_dotenv
import openai
from openai import OpenAI
from pathlib import Path
import time
import os
import json
import numpy as np
import requests

# スクリプトの絶対パスを取得
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

_ = load_dotenv(find_dotenv()) # read local .env file and set OPENAI KEY
api_key = os.environ['OPENAI_API_KEY']

def load_json(json_path):
    with open(json_path) as fin:
        json_obj=json.load(fin)
    return json_obj

def load_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # UTF-8で読み取れない場合は、他のエンコーディングを試す
        with open(file_path, 'r', encoding='shift-jis') as f:
            return f.read()

def convert_to_serializable(obj):
    if isinstance(obj, np.int64):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj
    
def parse_into_json(data_str):
    # Stripping the Markdown code block delimiters
    data_str = data_str.strip("'")
    data_str = data_str.replace('```json\n', '', 1)
    data_str = data_str.rsplit('\n```', 1)[0]

    # Parsing the JSON string
    parsed_json = json.loads(data_str)
    return parsed_json

def write_to_json(json_obj,json_path):
    with open(json_path,'w', encoding='utf-8') as fout:
        json.dump(json_obj,fout,default=convert_to_serializable,ensure_ascii=False)

def get_completion(prompt, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4.1-mini",
        "messages": [
            {
                "role": "user",
                "content": f"{prompt}\n\n評価対象テキスト:\n{text}"
            }
        ],
        "max_tokens": 300,
        "temperature": 0
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response

#load the arguments
parser=argparse.ArgumentParser()
parser.add_argument('--text_file', type=str, required=True, help='評価対象のテキストファイルのパス')
parser.add_argument('--result_base_dir', type=str, default="./output_json_files", help="出力ファイルの保存ディレクトリ")
args=parser.parse_args()

# 入力ファイルのパスを解決
text_file_path = os.path.join(SCRIPT_DIR, args.text_file.lstrip('./'))
# 出力ディレクトリのパスを解決
result_base_dir = os.path.join(SCRIPT_DIR, args.result_base_dir.lstrip('./'))

# テキストファイルを読み込む
try:
    text_content = load_text_file(text_file_path)
except Exception as e:
    print(f"エラー: テキストファイルの読み込みに失敗しました: {e}")
    exit(1)

# create the result directory
if not os.path.exists(result_base_dir):
    Path(result_base_dir).mkdir(parents=True, exist_ok=True)

# load the criteria json file
criteria_path = os.path.join('criteria.json')
criteria = load_json(criteria_path)

total_scores=[]
# loop through the criteria and get the scores

for i in range(3):
    print(f"Run {i+1}")
    total_score = 0
    for cr in criteria:
        try:
            head_prompt=f"Please rate the following text based on the specified criteria '{cr}'. Your task is to assign a score between 0 and 5, following these guidelines:"
            guidelines=criteria[cr]
            tail_prompt=f"""
            If you think the text's performance is between 4-5, choose 5 if it closely meets the guidelines and 4 if it's closer to the next lower level.
            Similarly, for a performance between 2-3, choose 3 if it's close to meeting the guidelines and 2 if it's nearer to the lower level.
            Similarly, for a performance between 0-1, choose 1 if it's close to meeting the guidelines and 0 if it's nearer to the lower level.
            Format your feedback as JSON format with the keys 'score' and 'explanation'"""
            prompt=f"{head_prompt}\n{guidelines}\n{tail_prompt}"
            response=get_completion(prompt=prompt, text=text_content)
            response_json=response.json()
            output_dict=response_json['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error: {e}, failed to retrieve response json file.\n Criteria: {cr},\n Response: {response.json()}")
            continue

        # Stripping the Markdown code block delimiters and parse into JSON
        parsed_json = parse_into_json(output_dict)

        score = int(parsed_json['score'])
        explanation = parsed_json['explanation']
        total_score += score
        print(f"Criteria: {cr},\n Score: {score},\n Explanation: {explanation}")

        time.sleep(0.1)
        
        write_to_json(parsed_json,f"{result_base_dir}/{'_'.join(cr.split())}_score_with_explanation_run{i+1}.json")

    print(f"Total Score: {total_score} of {5*len(criteria)}")
    total_scores.append(total_score)

average_score = sum(score / 3 for score in total_scores)
print(f"Average Score: {average_score} of {5*len(criteria)}")
        