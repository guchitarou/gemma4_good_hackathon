import os
from pathlib import Path
import glob
import json
import yaml
import itertools

import dash
from dash import html, dcc, Input, Output, State, callback
from ollama import Client

from utils import ingest_with_gemma, ingest_relation, ingest_colbert
from config import LOCAL_GEMMA4_API_URL, OLLAMA_GEMMA4_APIURL, FILE_DESCRIPTIONS_JSON_PATH, LANGUAGE_MODE, RELATIONSHIP_DESCRIPTIONS_JSON_PATH, COLBERT_MODEL_WEIGHTS_PATH, SEARCH_ID_JSON_PATH, MODEL_TYPE


from cache import background_callback_manager

with open("./prompts/summary.yaml", "r") as f:
    prompts = yaml.safe_load(f)


dash.register_page(__name__, path="/Upload", name="Upload")

BG = "#21252b" 
TEXT = "#ffffff"
PRIMARY = "#3B8BD4"
TEXT_SUB = "#a0bce0"

layout = html.Div([
    html.Div([
        html.H1("📂 Ingest", style={"fontSize": "2.5rem", "fontWeight": "800", "color": TEXT, "marginBottom": "1rem"}),
        html.P(
            "Register the data to be used for search and graph generation. The added files will be used to build the RAG search index and knowledge graph.", 
            style={"fontSize": "1.1rem", "color": TEXT}
        ),
        
        html.Label("Folder Path", style={"color": TEXT_SUB, "fontSize": "0.85rem", "marginBottom": "0.5rem", "display": "block"}),
        html.Div([   
            html.Div([
                dcc.Input(
                    id="ingest-folder-path",
                    type="text",
                    placeholder="Enter folder path (e.g. /data/my_folder)",
                    value="./DataFolder",  # ← デフォルト値
                    disabled=True,
                    style={
                        "width": "100%",
                        "height": "3rem",          # ← Input自体に指定
                        "padding": "0.75rem 1rem",
                        "borderRadius": "8px",
                        "border": "1.5px solid #1e4080",
                        "background": "#0a2050",
                        "color": "#ffffff",
                        "fontSize": "1rem",
                        "outline": "none",
                    },
                ),
            ], style={"display": "flex","width": "50%","gap": "0.75rem", "marginBottom": "1.5rem"}),
        ], style={
            "display": "flex",
            "margin": "0 20px",
            "justifyContent": "center",  # ← 追加
            "alignItems": "center"
        }),
        
        html.Div([
            html.Div([
                html.Button(
                    "⚡ Ingest",
                    id="ingest-button",
                    n_clicks=0,
                    style={
                        "padding": "0.75rem 2.5rem",
                        "backgroundColor": PRIMARY,
                        "color": TEXT,
                        "border": "none",
                        "borderRadius": "8px",
                        "fontSize": "1rem",
                        "fontWeight": "700",
                        "cursor": "pointer",
                    },
                ),
            ], style={"width": "20%", "marginLeft": "12px"}),
        ], style={
            "display": "flex",
            "margin": "0 20px",
            "justifyContent": "center",  # ← 追加
            "alignItems": "center"
        }),
        # ステータス表示
        # プログレスバー
        html.Div([
            html.Div(
                id="progress-label",
                children="",
                style={"color": "#a0bce0", "fontSize": "0.85rem", "marginBottom": "0.5rem"}
            ),
            html.Div([
                html.Div(
                    id="progress-bar",
                    style={
                        "height": "8px",
                        "width": "0%",
                        "background": "#3B8BD4",
                        "borderRadius": "4px",
                        "transition": "width 0.3s",
                    }
                )
            ], style={
                "background": "#1e4080",
                "borderRadius": "4px",
                "width": "100%",
            }),
        ], style={"marginTop": "1rem"}, id="progress-container"),
    ], style={"maxWidth": "900px", "margin": "0 auto", "padding": "3rem 2rem"}),
], style={"minHeight": "100vh", "background": BG})

@callback(
    Output("progress-label", "children", allow_duplicate=True),
    Input("ingest-button", "n_clicks"),
    State("ingest-folder-path", "value"),
    background=True,
    manager=background_callback_manager,
    progress=[
        Output("progress-bar", "style"),    # 進捗％
        Output("progress-label", "children") # テキスト表示
    ],
    prevent_initial_call=True,
)
def start_ingest(set_progress, n_clicks, folder_path):
    base_style = {
        "marginTop": "1.5rem",
        "padding": "1rem",
        "borderRadius": "8px",
        "fontSize": "0.95rem",
        "display": "block",
        "whiteSpace": "pre-wrap",
    }

    print("押された！")

    with open("./prompts/summary.yaml", "r") as f:
        prompts = yaml.safe_load(f)

    
    
    description_data = {}

    #for idx, file_path in enumerate(files_path_list):
    #print(f"Processing file: {file_path}")

    base_style = {
        "marginTop": "1.5rem",
        "padding": "1rem",
        "borderRadius": "8px",
        "fontSize": "0.95rem",
        "display": "block",
        "whiteSpace": "pre-wrap",
    }

    files = glob.glob("./DataFolder/**/*", recursive=True)

    files_path_list = [f for f in files if os.path.isfile(f)]

    print(files_path_list)

    total = len(files_path_list)

    
    
    client = Client(host=OLLAMA_GEMMA4_APIURL)
    
    for idx, file_path in enumerate(files_path_list):
        progress_pct = int((idx + 1) / total * 50)
        set_progress([
             {
                "height": "8px",
                "width": f"{progress_pct}%", 
                "background": "#3B8BD4",
                "borderRadius": "4px",
                "transition": "width 0.3s",
            },
            f"Processing {progress_pct}%"
        ])

        ingest_with_gemma(
            file_path,
            idx,
            description_data,
            client,
            prompts,
            lg=LANGUAGE_MODE,
            gemma_type = MODEL_TYPE,
            gemma4_api_url = LOCAL_GEMMA4_API_URL
        )
    


    # JSONファイルに保存
    with open(FILE_DESCRIPTIONS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(description_data, f, ensure_ascii=False, indent=4)

    with open("./prompts/relationship.yaml", "r") as f:
        relationship_prompts = yaml.safe_load(f)

    keys = list(description_data.keys())

    pairs = list(itertools.combinations(keys, 2))

    result_data = []


    for pid, (idx, idy) in enumerate(pairs):
        # 進捗を更新
        progress_pct = 50+int((pid + 1) / len(pairs) * 50)
        set_progress([
             {
                "height": "8px",
                "width": f"{progress_pct}%",   # ← widthで進捗表現
                "background": "#3B8BD4",
                "borderRadius": "4px",
                "transition": "width 0.3s",
            },
            f"Processing {progress_pct}%"
        ])


        result_data = ingest_relation(
            description_data,
            idx, idy,
            result_data,
            client,
            relationship_prompts["relationship_txt"][LANGUAGE_MODE],
            gemma_type = MODEL_TYPE,
            gemma4_api_url=LOCAL_GEMMA4_API_URL
        )
    
    with open(RELATIONSHIP_DESCRIPTIONS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=4)


    set_progress([
         {
            "height": "8px",
            "width": f"{progress_pct}%",   # ← widthで進捗表現
            "background": "#3B8BD4",
            "borderRadius": "4px",
            "transition": "width 0.3s",
        },
        f"Setting up ColBERT.."
    ])


    # setting colbert!
    id_to_text = ingest_colbert(
        description_data,
        COLBERT_MODEL_WEIGHTS_PATH
    )


    with open(SEARCH_ID_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(id_to_text, f, ensure_ascii=False, indent=2)


    # フォルダパスをターミナルにprint
    print("=== Ingest Start ===")
    print(f"  Folder Path : {folder_path}")
    print("====================")
    return "✅ Ingest complete!"
