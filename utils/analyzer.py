
import json 
import requests
from pathlib import Path

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
                        {"type": "image", "image": input_file_path},
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
        if(self.mllm_type=="local"):
            messages_list = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text":  self.summary_prompts['summary_video'][self.lgm ]}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "video", "video": input_file_path},
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
            print("unexpected file extension!")

        return file_desc

    def ask_reasoning(self, question, desc, select_file_path):
        if(self.mllm_type=="ollama"):
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


                    

