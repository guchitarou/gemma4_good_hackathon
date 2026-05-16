import os
from pathlib import Path
import glob
import json
import requests

from pylate import indexes, models
import pymupdf4llm
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .read_txt_file import file_to_string

import itertools

def ingest_with_gemma(file_path, idx, data, client, prompts, lg="en", gemma_type = "ollama", gemma4_api_url=None):
    extension = Path(file_path).suffix.lstrip(".")

    if(extension in ['pdf', 'html', 'py', 'java']):
        str_data  =  file_to_string(file_path)

        if(gemma_type=="ollama"):
            summary_response = client.chat(
                model='gemma4:e4b',
                messages=[
                    {"role": "system", 'content': prompts["summary_txt"][lg]},
                    {'role': 'user', 'content': str_data},    
                ],
            )

            summary = summary_response.message.content

            print("<<<Summary from model>>>:\n", summary)

            response = client.chat(
                model='gemma4:e4b',
                messages=[
                    {"role": "system", 'content': prompts["summary_title"][lg]},
                    {'role': 'user', 'content': summary},    
                ],
            )
            data_type = "None"

           

            print("<<<Description from model>>>:\n")
            print(response.message.content)
            description = response.message.content
        else:
            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text":  prompts['summary_txt'][lg]}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": str_data},
                    ],
                },
            ]
            response = requests.post(
                gemma4_api_url,
                json = messages_list
            )

            summary = response.json()

            print("<<<Summary from model>>>:\n", summary)

            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text":  prompts['summary_title'][lg]}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": summary},
                    ],
                },
            ]
            response = requests.post(
                gemma4_api_url,
                json = messages_list
            )

            print("<<<Description from model>>>:\n")
            description = response.json()
            print(description)
        
        if(extension in ['pdf','txt']):
            data_type = "txt"
        else:
            data_type = "code"


        each_data = {
            "data_type": data_type,
            "description": description,
            "path": file_path
        }
        data[f"id{idx}"] = each_data
    elif(extension in ['jpg', 'jpeg', 'png']):
        if(gemma_type=="ollama"):
            response = client.chat(
                model='gemma4:e4b',
                messages = [
                    {"role": "system",  'content': prompts["summary_img"][lg]},
                    {
                        "role": "user",
                        'images': [file_path]
                    }
                ]
            )
            description = response.message.content
        else:
            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text":  prompts['summary_img'][lg]}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": file_path},
                    ],
                },
            ]
            response = requests.post(
                gemma4_api_url,
                json = messages_list
            )

            print("<<<Description from model>>>:\n")
            description = response.json()
        
        each_data = {
            "data_type": "image",
            "description": description,
            "path": file_path
        }

        data[f"id{idx}"] = each_data
    elif(extension in ['mp4']):
        if(gemma_type=="local"):
            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text":  prompts['summary_video'][lg]}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "video", "video": file_path},
                    ],
                },
            ]
            response = requests.post(
                gemma4_api_url,
                json = messages_list
            )


            description = response.json()

            print("<<<Description from model>>>:\n")
            print(description)

            each_data = {
                "data_type": "video",
                "description": description,
                "path": file_path
            }

            data[f"id{idx}"] = each_data

    elif(extension in ['mp3']):
        if(gemma_type=="local"):
            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text":  prompts['summary_audio'][lg]}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "audio", "audio": file_path},
                    ],
                },
            ]
            response = requests.post(
                gemma4_api_url,
                json = messages_list
            )
            description = response.json()
            print("<<<Description from model>>>:\n")
            print(description)


            each_data = {
                "data_type": "audio",
                "description": description,
                "path": file_path
            }
            data[f"id{idx}"] = each_data

    else:
        print("unexpected file extension!")

    return data

def ingest_relation(data, idx, idy, result_data, client, prompt, gemma_type = "ollama", gemma4_api_url=None):
    description1 = data[idx]["description"]
    description2 = data[idy]["description"]

    if(gemma_type=="ollama"):
        response = client.chat(
            model='gemma4:e4b',
            messages=[
                {"role": "system",  'content': prompt},
                {
                    "role": "user",
                    'content': f"file1: {description1}"
                },
                {
                    "role": "user",
                    'content': f"file2: {description2}"
                }
            ]
        )
        relationship = response.message.content
    else:
        messages_list = [
            {
                "role": "system",
                "content": [{"type": "text", "text": "<|think|>\nYou are a helpful assistant."}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "text", "text": f"file1: {description1}"},
                    {"type": "text", "text": f"file2: {description2}"},
                ],
            },
        ]
        response = requests.post(
            gemma4_api_url,
            json = messages_list
        )
        relationship = response.json()


    
    print(relationship)
    each_data = {
        "par_id": f"{idx}_{idy}",
        "relationship": relationship,
    }
    result_data.append(each_data)

    return result_data

def ingest_colbert(description_data, model_weight_path):    
    id_to_text = {}
    documents_ids = []
    documents_chunks = []
    for key, value in description_data.items():
        print(f"ID: {key}")
        print(f"Description: {value['description']}")
        print(f"Path: {value['path']}")
        print("-" * 40)
        documents_ids.append(key)
        documents_chunks.append(value["description"])

    # スピリッターの設定
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "、", ". ", " ", ""],
    )
    # チャンクとIDの対応をJSONで保存
    id_to_text = {str(i): chunk for i, chunk in enumerate(documents_ids)}

    print(f"PDFから抽出されたテキストを{len(documents_chunks)}チャンクに分割し、IDと対応付けて保存しました。")

    # 1. モデルのロード
    model = models.ColBERT(
        model_name_or_path = model_weight_path
    )
    print("モデルがロードされました。")
    documents_embeddings = model.encode(
        documents_chunks,
        batch_size=32,
        is_query=False,
        show_progress_bar=True,
    )

    # 2. インデックスの初期化
    index = indexes.Voyager(
        index_folder="./my_pylate-index",
        index_name="colbert-index",
        override=True,
    )
    print(index)

    documents_ids = [str(i) for i in range(len(documents_chunks))]

    index.add_documents(
        documents_ids=documents_ids,
        documents_embeddings=documents_embeddings,
    )
    print("pylate-index/ に保存されました。")

    return id_to_text
