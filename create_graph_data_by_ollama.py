import os
from pathlib import Path
import glob
import json

from ollama import Client

from utils import file_to_string
from config import OLLAMA_GEMMA4_APIURL, FILE_DESCRIPTIONS_JSON_PATH, DATA_FOLDER_PATH, LANGUAGE_MODE


import yaml

with open("./prompts/summary.yaml", "r") as f:
    prompts = yaml.safe_load(f)

files_path_list = glob.glob(DATA_FOLDER_PATH)

client = Client(host=OLLAMA_GEMMA4_APIURL)

data = {}
for idx, file_path in enumerate(files_path_list):
    print(f"Processing file: {file_path}")
    
    extension = Path(file_path).suffix.lstrip(".")

    if(extension in ['pdf', 'html', 'py', 'java']):
        str_data  =  file_to_string(file_path)

        summary_response = client.chat(
            model='gemma4:e4b',
            messages=[
                {"role": "system", 'content': prompts["summary_txt"][LANGUAGE_MODE]},
                {'role': 'user', 'content': str_data},    
            ],
        )

        summary = summary_response.message.content

        print("<<<Summary from model>>>:\n", summary)

        response = client.chat(
            model='gemma4:e4b',
            messages=[
                {"role": "system", 'content': prompts["summary_title"][LANGUAGE_MODE]},
                {'role': 'user', 'content': summary},    
            ],
        )
        data_type = "None"

        if(extension in ['pdf','txt']):
            data_type = "txt"

        else:
            data_type = "code"

        print("<<<Description from model>>>:\n")
        print(response.message.content)
        description = response.message.content

        each_data = {
            "data_type": data_type,
            "description": description,
            "path": file_path
        }
        data[f"id{idx}"] = each_data
        

    elif(extension in ['jpg', 'jpeg', 'png']):
        response = client.chat(
            model='gemma4:e4b',
            messages = [
                {"role": "system",  'content': prompts["summary_img"][LANGUAGE_MODE]},
                {
                    "role": "user",
                    'images': [file_path]
                }
            ]
        )

        data_type = "image"
        description = response.message.content
        each_data = {
            "data_type": data_type,
            "description": description,
            "path": file_path
        }

        data[f"id{idx}"] = each_data


# JSONファイルに保存
with open(FILE_DESCRIPTIONS_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
