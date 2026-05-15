import json 
import requests
from pathlib import Path
import yaml

import threading
import gradio as gr


from ollama import Client
from utils import is_analyzed, MLLMAnalyzer
from config import (
    MODEL_TYPE,
    OLLAMA_GEMMA4_APIURL,
    FILE_DESCRIPTIONS_JSON_PATH,
    LANGUAGE_MODE, 
    LOCAL_GEMMA4_API_URL,
    RETRIEVER_API_URL
)

with open(FILE_DESCRIPTIONS_JSON_PATH, "r", encoding="utf-8") as f:
    description_data = json.load(f)


with open("./prompts/file_selector.yaml", "r") as f:
    selector_prompts = yaml.safe_load(f)

with open("./prompts/summary.yaml", "r") as f:
    summary_prompts = yaml.safe_load(f)


if(MODEL_TYPE=="ollama"):
    client = Client(host=OLLAMA_GEMMA4_APIURL)


mllm = MLLMAnalyzer(
    client,
    local_gemma4_api_url = LOCAL_GEMMA4_API_URL, 
    input_summary_prompts = summary_prompts, 
    input_selector_prompts = selector_prompts, 
    mllm_type = MODEL_TYPE,
    lgm = LANGUAGE_MODE
)


def chat(message, history):
    print("Message received:", message["text"])

    file_desc = None
    file_name = None

    if  len(message["files"]) != 0:
        file_name = Path(message['files'][0]).name
        file_desc = is_analyzed(
            file_name,
            description_data
        )
        
    if(file_name is not None and file_desc is None):
        file_path = Path(message['files'][0])
        print(f"file path -> {file_path}")
        file_desc = mllm.describe_file(file_path)

    question = message["text"]

    task_type = mllm.get_task_type(question)

    if(task_type == "[TO]"):
        response = requests.get(
            RETRIEVER_API_URL,
            params={"question": question}
        )

        selected_text = response.json().get("selected_text", "No text found")

        answer_txt = mllm.rag_search(
            selected_text,
            question
        )
        return [
            {"role": "assistant", "content": answer_txt}
        ]

    elif(task_type == "[FS]"):
        ideal_file_description = mllm.ask_relevant_files(
            file_desc,
            question
        )
        # 
        response = requests.get(
            "http://localhost:7860/retriever_file",
            params={"file_desc": ideal_file_description}
        )

        file_path_list = response.json().get("file_paths", [])
        descriptions = response.json().get("descriptions", [])

        for file_path, desc in zip(file_path_list, descriptions):
            print(f"Retrieved file path: {file_path}, description: {desc}")
            res_file_name = Path(file_path).name

            ans=mllm.ask_reasoning(
                question,
                desc,
                file_path
            )

            return ans
        return [
            {"role": "assistant", "content": "No matching files were found."}
        ]
    
    return [
        {"role": "assistant", "content": "Error Occurred"}
    ]

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
