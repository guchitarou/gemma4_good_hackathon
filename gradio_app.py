import json 
import requests
from pathlib import Path
import yaml

import threading
import gradio as gr


from ollama import Client
from utils import file_to_string
from config import OLLAMA_GEMMA4_APIURL, FILE_DESCRIPTIONS_JSON_PATH, LANGUAGE_MODE

with open(FILE_DESCRIPTIONS_JSON_PATH, "r", encoding="utf-8") as f:
    description_data = json.load(f)


with open("./prompts/file_selector.yaml", "r") as f:
    selector_prompts = yaml.safe_load(f)

with open("./prompts/summary.yaml", "r") as f:
    summary_prompts = yaml.safe_load(f)


client = Client(host=OLLAMA_GEMMA4_APIURL)

def chat(message, history):
    print("Message received:", message["text"])

    if  len(message["files"]) != 0:
        file_name = Path(message['files'][0]).name
        print("Attached file name:", file_name)

        for key, desc in description_data.items():
            file_path = desc.get("path")

            desc_file_name = Path(file_path).name
            if desc_file_name == file_name:
                 print("Matched file description:", desc)
                 print("description:", desc.get("description"))
                 file_desc = desc.get("description")
                 break

    question = message["text"]
    
    response = client.chat(
        model='gemma4:e4b',
        messages=[
            {"role": "system", 'content': selector_prompts['file_selector'][LANGUAGE_MODE]},
            {'role': 'user', 'content': question},    
        ],
    )

    task_type = response.message.content

    if(task_type == "[TO]"):
        response = requests.get(
            "http://localhost:7860/retriever_id",
            params={"question": question}
        )

        selected_text = response.json().get("selected_text", "No text found")

        response = client.chat(
            model='gemma4:e4b',
            messages=[
                {"role": "system", "content": selector_prompts['assistant_summary'][LANGUAGE_MODE]},
                {'role': 'user', 'content': f"Reference: {selected_text}"},
                {'role': 'user', 'content': question},
            ],
        )

    elif(task_type == "[FS]"):
        file_desc = None
        file_name = None

        if len(message["files"]) != 0:
            file_name = Path(message['files'][0]).name
            print("Attached file name:", file_name)

            for key, desc in description_data.items():
                file_path = desc.get("path")

                desc_file_name = Path(file_path).name
                if desc_file_name == file_name:
                     print("Matched file description:", desc)
                     print("description:", desc.get("description"))
                     file_desc = desc.get("description")
                     break

        msg_list = None
        if(file_name is not None and file_desc is None):
            extension = Path(file_path).suffix.lstrip(".")
            if(extension in ['pdf', 'html', 'py', 'java']):
                str_data  =  file_to_string(file_path)

                summary_response = client.chat(
                    model='gemma4:e4b',
                    messages=[
                        {"role": "system", 'content':summary_prompts['summary_txt'][LANGUAGE_MODE]},
                        {'role': 'user', 'content': str_data},    
                    ],
                )

                summary = summary_response.message.content

                print("<<<Summary from model>>>:\n", summary)

                response = client.chat(
                    model='gemma4:e4b',
                    messages=[
                        {"role": "system", 'content': summary_prompts['summary_title'][LANGUAGE_MODE]},
                        {'role': 'user', 'content': summary},    
                    ],
                )
    

                print("<<<Description from model>>>:\n")

                file_desc = response.message.content
                print("<<<Description from model>>>:\n")
                print(file_desc)

               
        

            elif(extension in ['jpg', 'jpeg', 'png']):
                response = client.chat(
                    model='gemma4:e4b',
                    messages = [
                        {"role": "system",  'content': summary_prompts['summary_img'][LANGUAGE_MODE]},
                        {
                            "role": "user",
                            'images': [file_path]
                        }
                    ]
                )

                file_desc = response.message.content
                print("<<<Description from model>>>:\n")
                print(file_desc)
              
        

        if(file_desc is not None):
            msg_list = [
                {'role': 'user', 'content': f"file : {file_desc}"},
                {'role': 'user', 'content': f"userQ : {question}"},
                {"role": "user",  'content': selector_prompts['file_detail_selector'][LANGUAGE_MODE]},
            ]
        else:
            msg_list = [
                {'role': 'user', 'content': f"userQ : {question}"},
                {"role": "user",  'content': selector_prompts['file_detail_single_selector'][LANGUAGE_MODE]},
            ]

        response = client.chat(
            model='gemma4:e4b',
            messages=msg_list,
        )

        
        file_description = response.message.content
        print(file_description)
        

        response = requests.get(
            "http://localhost:7860/retriever_file",
            params={"file_desc": file_description}
        )

        file_path_list = response.json().get("file_paths", [])
        descriptions = response.json().get("descriptions", [])


        ans = None
        for file_path, desc in zip(file_path_list, descriptions):
            print(f"Retrieved file path: {file_path}, description: {desc}")
            res_file_name = Path(file_path).name

            if (file_name is None) or (file_name is not  None and file_name!=res_file_name):
                response = client.chat(
                    model='gemma4:e4b',
                    messages=[
                        {"role": "system", "content": selector_prompts['select_reason'][LANGUAGE_MODE]},
                        {'role': 'user', 'content': f"useQ:{question},file_desc : {desc}"},
                    ],
                )
                file_reason = response.message.content
                ans = [
                    {"role": "assistant", "content": file_reason},
                    {"role": "assistant", "content": {"path": file_path}}
                ]

                response = requests.post(
                    "http://172.18.131.28:7862/api/upload",
                    json={"filename": res_file_name}
                )

                
                return ans



        return [
            {"role": "assistant", "content": "No matching files were found."}
        ]
    
    print("Response from model:", response.message.content)
    answer_txt = response.message.content
    return answer_txt

demo = gr.ChatInterface(
    fn=chat,
    multimodal=True,  
    textbox=gr.MultimodalTextbox( 
        placeholder="Message (attach files optional)",
        file_types=None, 
        file_count="single", 
    ),
    cache_examples=False,
)
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",  
        server_port=7861, 
        share=False, 
    )
