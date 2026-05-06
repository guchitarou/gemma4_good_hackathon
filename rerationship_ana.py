import json
import itertools
import yaml


from ollama import Client

from config import OLLAMA_GEMMA4_APIURL, FILE_DESCRIPTIONS_JSON_PATH, RELATIONSHIP_DESCRIPTIONS_JSON_PATH, LANGUAGE_MODE

with open("./prompts/relationship.yaml", "r") as f:
    relationship_prompts = yaml.safe_load(f)

with open(FILE_DESCRIPTIONS_JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

keys = list(data.keys())

pairs = list(itertools.combinations(keys, 2))

print(pairs)

client = Client(host = OLLAMA_GEMMA4_APIURL)

result_data = []
for idx, idy in pairs:
    description1 = data[idx]["description"]
    description2 = data[idy]["description"]

    response = client.chat(
        model='gemma4:e4b',
        messages=[
            {"role": "system",  'content': relationship_prompts["relationship_txt"][LANGUAGE_MODE]},
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
    print(relationship)
    each_data = {
        "par_id": f"{idx}_{idy}",
        "relationship": relationship,
    }
    result_data.append(each_data)

# JSONファイルに保存
with open(RELATIONSHIP_DESCRIPTIONS_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(result_data, f, ensure_ascii=False, indent=4)