import os
import json 
import requests
from pathlib import Path

import networkx as nx

from .read_txt_file import file_to_string

def is_analyzed(file_name, description_data):
    print("Attached file name:", file_name)
    for key, desc in description_data.items():
        desc_file_name = Path(desc.get("path")).name
        if desc_file_name == file_name:
             print("Matched file description:", desc)
             print("description:", desc.get("description"))
             file_desc = desc.get("description")
             return file_desc

    return None

class MLLMAnalyzer():
    def __init__(self, client=None, local_gemma4_api_url = None, input_summary_prompts=None, input_selector_prompts=None, mllm_type="local",lgm="en"):
        self.client = client
        self.mllm_type = mllm_type
        self.lgm = lgm
        self.local_gemma4_api_url = local_gemma4_api_url
        self.summary_prompts = input_summary_prompts
        self.selector_prompts = input_selector_prompts

    def describe_txt_file(self, input_file_path):
        str_data = file_to_string(input_file_path)
        if(self.mllm_type=="ollama"):
            summary_response = self.client.chat(
                model='gemma4:e4b',
                messages=[
                    {"role": "system", 'content':self.summary_prompts['summary_txt'][self.lgm ]},
                    {'role': 'user', 'content': str_data},    
                ],
            )
            summary = summary_response.message.content
            print("<<<Summary from model>>>:\n", summary)
            response = self.client.chat(
                model='gemma4:e4b',
                messages=[
                    {"role": "system", 'content': self.summary_prompts['summary_title'][self.lgm ]},
                    {'role': 'user', 'content': summary},    
                ],
            )
            file_desc = response.message.content
            print("<<<Description from model>>>:\n")
            print(file_desc)
        else:
            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text":  self.summary_prompts['summary_txt'][self.lgm ]}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": str_data},
                    ],
                },
            ]
            response = requests.post(
                self.local_gemma4_api_url,
                json = messages_list
            )
            summary = response.json()
            print("<<<Summary from model>>>:\n", summary)
            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text":  self.summary_prompts['summary_title'][self.lgm ]}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": summary},
                    ],
                },
            ]
            response = requests.post(
                self.local_gemma4_api_url,
                json = messages_list
            )
            file_desc = response.json()

        return file_desc

    def describe_image(self, input_file_path):
        if(self.mllm_type=="ollama"):
            response = self.client.chat(
                model='gemma4:e4b',
                messages = [
                    {"role": "system",  'content': self.summary_prompts['summary_img'][self.lgm ]},
                    {
                        "role": "user",
                        'images': [input_file_path]
                    }
                ]
            )
            file_desc = response.message.content
            print("<<<Description from model>>>:\n")
            print(file_desc)
        else:
            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text":  self.summary_prompts['summary_img'][self.lgm ]}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": str(input_file_path)},
                    ],
                },
            ]
            response = requests.post(
                self.local_gemma4_api_url,
                json = messages_list
            )
            file_desc = response.json()
            print("<<<Description from model>>>:\n")
            print(file_desc)

        return file_desc

    def describe_video(self, input_file_path):


        print(type(input_file_path))

        print("-------------------------------")
        if(self.mllm_type=="local"):
            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text":  self.summary_prompts['summary_video'][self.lgm ]}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "video", "video": str(input_file_path)},
                    ],
                },
            ]
            response = requests.post(
                self.local_gemma4_api_url,
                json = messages_list
            )
            file_desc = response.json()
            print("<<<Description from model>>>:\n")
            print(file_desc)
            return file_desc
        else:
            return None 

    def describe_audio(self, input_file_path):
        if(self.mllm_type=="local"):
            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text":  self.summary_prompts['summary_audio'][self.lgm ]}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "audio", "audio": input_file_path},
                    ],
                },
            ]
            response = requests.post(
                self.local_gemma4_api_url,
                json = messages_list
            )
            file_desc = response.json()
            print("<<<Description from model>>>:\n")
            print(file_desc)
            return file_desc
        else:
            return None

    def get_task_type(self, question):
        if(self.mllm_type=="ollama"):
            response = self.client.chat(
                model='gemma4:e4b',
                messages=[
                    {"role": "system", 'content': self.selector_prompts['file_selector'][self.lgm ]},
                    {'role': 'user', 'content': question},    
                ],
            )
            task_type = response.message.content
        else:
            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": self.selector_prompts['file_selector'][self.lgm ]}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                    ],
                },
            ]
            response = requests.post(
                self.local_gemma4_api_url,
                json = messages_list
            )
            task_type = response.json()

        return task_type


    def describe_file(self, file_path):
        extension = Path(file_path).suffix.lstrip(".")
        print(f"extension -> {extension}")

        file_desc = None

        if(extension in ['pdf', 'html', 'py', 'java']):
            print("txt file found!")
            file_desc = self.describe_txt_file(file_path)
        elif(extension in ['jpg', 'jpeg', 'png']):
            print("image found!")
            file_desc = self.describe_image(file_path)

        elif(extension in ['mp4']):
            print("video found!")
            file_desc = self.describe_video(file_path)

        elif(extension in ['mp3']):
            print("audio found!")
            file_desc = self.describe_audio(file_path)
        else:
            print(f"unexpected file extension!->{extension}")

        return file_desc

    def ask_reasoning(self, question, desc, select_file_path):
        if(self.mllm_type=="ollama"):
            print("プロンプトは")
            print(self.selector_prompts['select_reason'][self.lgm])
            response = self.client.chat(
                model='gemma4:e4b',
                messages=[
                    {"role": "system", "content": self.selector_prompts['select_reason'][self.lgm]},
                    {'role': 'user', 'content': f"useQ:{question},file_desc : {desc}"},
                ],
            )
            file_reason = response.message.content
            ans = [
                {"role": "assistant", "content": file_reason},
                {"role": "assistant", "content": {"path": select_file_path}}
            ]
        else:
            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text":  self.selector_prompts['select_reason'][self.lgm]}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"useQ:{question},file_desc : {desc}"},
                    ],
                },
            ]
            response = requests.post(
                self.local_gemma4_api_url,
                json = messages_list
            )
            file_reason = response.json()
            ans = [
                {"role": "assistant", "content": file_reason},
                {"role": "assistant", "content": {"path": select_file_path}}
            ]
        
        return ans

    def check_file(self, desc):
        if(self.mllm_type=="ollama"):
            print("プロンプトは")
            print(self.selector_prompts['file_check'][self.lgm])
            response = self.client.chat(
                model='gemma4:e4b',
                messages=[
                    {"role": "system", "content": self.selector_prompts['file_identity_checker'][self.lgm]},
                    {'role': 'user', 'content': f"desc : {desc}"},
                ],
            )
            ans = response.message.content

        else:
            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text":  self.selector_prompts['file_identity_checker'][self.lgm]}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"desc : {desc}"},
                    ],
                },
            ]
            response = requests.post(
                self.local_gemma4_api_url,
                json = messages_list
            )
            ans = response.json()
        
        return ans


    def select_file(self, desc, w_desc):
        if(self.mllm_type=="ollama"):
            response = self.client.chat(
                model='gemma4:e4b',
                messages=[
                    {"role": "system", "content": f"{self.selector_prompts['file_select'][self.lgm]}{w_desc}"},
                    {'role': 'user', 'content': desc},
                ],
            )
            ans = response.message.content

        else:
            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": f"{self.selector_prompts['file_select'][self.lgm]}{w_desc}" }],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": desc},
                    ],
                },
            ]
            response = requests.post(
                self.local_gemma4_api_url,
                json = messages_list
            )
            ans = response.json()
        
        return ans

    def rag_search(self, selected_text, question):
        if(self.mllm_type=="ollama"):
            response = self.client.chat(
                model='gemma4:e4b',
                messages=[
                    {"role": "system", "content": self.selector_prompts['assistant_summary'][self.lgm]},
                    {'role': 'user', 'content': f"Reference: {selected_text}"},
                    {'role': 'user', 'content': question},
                ],
            )
            answer_txt = response.message.content
        else:
            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": self.selector_prompts['assistant_summary'][self.lgm]}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Reference: {selected_text}"},
                        {"type": "text", "text": question},
                    ],
                },
            ]
            response = requests.post(
                self.local_gemma4_api_url,
                json = messages_list
            )
            answer_txt = response.json()

        return answer_txt

    def ask_relevant_files(self, file_desc, question):
        if(self.mllm_type=="ollama"):
            if(file_desc is not None):
                msg_list = [
                    {'role': 'user', 'content': f"file : {file_desc}"},
                    {'role': 'user', 'content': f"userQ : {question}"},
                    {"role": "user",  'content': self.selector_prompts['file_detail_selector'][self.lgm]},
                ]
            else:
                msg_list = [
                    {'role': 'user', 'content': f"userQ : {question}"},
                    {"role": "user",  'content': self.selector_prompts['file_detail_single_selector'][self.lgm]},
                ]

            response = self.client.chat(
                model='gemma4:e4b',
                messages=msg_list,
            )
            file_description = response.message.content
            
        else:
            if(file_desc is not None):
                messages_list = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"file : {file_desc}"},
                            {"type": "text", "text": f"userQ : {question}"},
                            {"type": "text", "text": self.selector_prompts['file_detail_selector'][self.lgm]},
                        ],
                    },
                ]
            else:
                messages_list = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"userQ : {question}"},
                            {"type": "text", "text": self.selector_prompts['file_detail_single_selector'][self.lgm]},
                        ],
                    },
                ]
            
            response = requests.post(
                self.local_gemma4_api_url,
                json = messages_list
            )
            file_description = response.json()
        print("---<ask_relevant_files>---")
        print(file_description)
        return file_description


def load_ana_data(relation_path, desc_path):

    with open(relation_path, "r", encoding="utf-8") as f:
        relationship_data = json.load(f)
    with open(desc_path, "r", encoding="utf-8") as f:
        description_data = json.load(f)

    G = nx.Graph()
    desc_dict = {}

    for each_key in description_data.keys():
        path = description_data[each_key]["path"]
        filename = os.path.basename(path)
        desc_dict[filename] = description_data[each_key]
        G.add_node(filename, title=path)

    for each_data in relationship_data:
        each_id = each_data["par_id"]
        xid, yid = each_id.split("_")
        relationship_desc = each_data["relationship"]
        if relationship_desc not in ["None"]:
            path_x = description_data[xid]["path"]
            path_y = description_data[yid]["path"]
            filename_x = os.path.basename(path_x)
            filename_y = os.path.basename(path_y)
            G.add_edge(filename_x, filename_y, relation=relationship_desc)

    return G, desc_dict, description_data, relationship_data

                    
import json
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI


import json
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI


class GroupClassifier:
    def __init__(self, groups: list[dict], system_prompt: str,
                 model: str = "",
                 base_url: str = "http://localhost:8000/v1",
                 chunk: int = 20):
        self.groups = groups  # [{"id": ..., "text": ...}, ...]
        self.system_prompt = system_prompt
        self.model = model
        self.chunk = chunk
        self.client = OpenAI(base_url=base_url, api_key="EMPTY")

    def pick(self, item: str, idx: list[int]) -> int | None:
        names = [f"G{j+1}" for j in range(len(idx))] + ["該当なし"]
        # 変更:論点の文章は "text" から取り出す
        group_text = "\n".join(f"{names[j]}: {self.groups[i]['text']}" for j, i in enumerate(idx))
        print("Debug: group_text = \n" + group_text)
        schema = {
            "type": "object",
            "properties": {"group": {"type": "string", "enum": names}},
            "required": ["group"],
        }
        res = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"# グループ一覧\n{group_text}\n\n# 論点\n{item}"},
            ],
            response_format={"type": "json_schema",
                             "json_schema": {"name": "pick", "schema": schema}},
            temperature=0,
        )
        g = json.loads(res.choices[0].message.content)["group"]
        if g not in names:
            raise ValueError(f"想定外の出力: {g}")
        return None if g == "該当なし" else idx[names.index(g)]

    def classify(self, item: str) -> dict:
        """戻り値: {"id": グループID, "text": グループの論点}。該当なしはidがNone"""
        not_found = {"id": None, "text": "該当なし"}  # 変更:該当なし用の結果
        idx = list(range(len(self.groups)))
        while len(idx) > self.chunk:
            blocks = [idx[i:i + self.chunk] for i in range(0, len(idx), self.chunk)]

            raise Exception(blocks)
            with ThreadPoolExecutor() as ex:
                futures = []
                for b in blocks:
                    futures.append(ex.submit(self.pick, item, b))
                winners = []
                for f in futures:
                    winners.append(f.result())
            idx = [w for w in winners if w is not None]
            if not idx:
                return not_found
        final = self.pick(item, idx)
        return self.groups[final] if final is not None else not_found  # 変更:辞書ごと返す


def read_model_output2(text):
    decoder = json.JSONDecoder()
    data = None
    text = text.replace("“", '"').replace("”", '"')   # 全角のクォート → "
    if '"' not in text:                               # " が1つも無いときだけ
        text = text.replace("'", '"')
    text = re.sub(r",\s*}", "}", text)                # 末尾の余計なカンマを消す
    text = re.sub(r",\s*]", "]", text)                # 末尾の余計なカンマを消す
    for i, ch in enumerate(text):
        if ch == "[":                           
            try:
                data, _ = decoder.raw_decode(text, i)  # そこからJSONとして読んでみる
                break                           # 読めたら終了
            except json.JSONDecodeError:
                continue 
    return data


def read_model_output(text):
    decoder = json.JSONDecoder()
    data = None

    text = text.replace("“", '"').replace("”", '"')   # 全角のクォート → "
    if '"' not in text:                               # " が1つも無いときだけ
        text = text.replace("'", '"')
    text = re.sub(r",\s*}", "}", text)                # 末尾の余計なカンマを消す
    
    for i, ch in enumerate(text):
        if ch == "{":                           # { を見つけるたびに
            try:
                data, _ = decoder.raw_decode(text, i)  # そこからJSONとして読んでみる
                break                           # 読めたら終了
            except json.JSONDecodeError:
                continue                        # 読めなければ次の { へ
    return data
