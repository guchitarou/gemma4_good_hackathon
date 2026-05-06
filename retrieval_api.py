import json
import requests

from fastapi import FastAPI
import uvicorn
from pylate import indexes, models, retrieve
from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils import file_to_string

from config import COLBERT_MODEL_WEIGHTS_PATH, SEARCH_ID_JSON_PATH, FILE_DESCRIPTIONS_JSON_PATH

# チャンクとIDの対応をJSONで保存
with open(FILE_DESCRIPTIONS_JSON_PATH, "r", encoding="utf-8") as f:
    description_data = json.load(f)

with open(SEARCH_ID_JSON_PATH, "r", encoding="utf-8") as f:
    search_id_data = json.load(f)




# 1. モデルのロード
model = models.ColBERT(
    model_name_or_path = COLBERT_MODEL_WEIGHTS_PATH
)

app = FastAPI()



@app.get("/retriever_id")
def retriever_id(question: str):
    print("質問:", question)

    # 2.クエリで検索用のエンベディング取得
    queries_embeddings = model.encode(
        [question],
        batch_size=32,
        is_query=True,
        show_progress_bar=True,
    )

    # 3. インデックスのロード
    index = indexes.Voyager(
        index_folder="./my_pylate-index",
        index_name="jacolbert-index",
        override=False,
    )

    
    # 4. リトリーバーのセットアップ
    retriever = retrieve.ColBERT(index=index)

    results = retriever.retrieve(
        queries_embeddings=queries_embeddings,
        k=1
    )[0]

    retriever_id = search_id_data.get(results[0]["id"])

    desc_str = description_data.get(retriever_id)


    print(f"ID: {retriever_id}")
    print(f"Description: {desc_str}")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=256,      # トークン数ではなく文字数なので少し多めに
        chunk_overlap=50,    # 前後の文脈を引き継ぐ
        separators=["。", "、", "\n", " ", ""],  # 日本語向け区切り
    )


    md_text  =  file_to_string(desc_str["path"])

    documents_chunks = splitter.split_text(md_text)

    documents_embeddings = model.encode(
        documents_chunks,
        batch_size=32,
        is_query=False,
        show_progress_bar=True,
    )

    # 2. インデックスの初期化
    index = indexes.Voyager(
        index_folder="./my_pylate-index",
        index_name="jacolbert-single-index",
        override=False,
    )

    print(index)
    documents_ids = [str(i) for i in range(len(documents_chunks))]

    index.add_documents(
        documents_ids=documents_ids,
        documents_embeddings=documents_embeddings,
    )
    retriever = retrieve.ColBERT(index=index)

    # 5. クエリで検索実施
    results = retriever.retrieve(
        queries_embeddings=queries_embeddings,
        k=1
    )[0]


    id_to_text = {str(i): chunk for i, chunk in enumerate(documents_chunks)}


    print("検索結果:", results[0]["id"])
    print(documents_ids)

    retriever_text = id_to_text.get(results[0]["id"])


    return {"result": "success", "selected_text": retriever_text}



@app.get("/retriever_file")
def retriever_file(file_desc: str):
    print("質問:", file_desc)

    # 2.クエリで検索用のエンベディング取得
    queries_embeddings = model.encode(
        [file_desc],
        batch_size=32,
        is_query=True,
        show_progress_bar=True,
    )

    # 3. インデックスのロード
    index = indexes.Voyager(
        index_folder="./my_pylate-index",
        index_name="jacolbert-index",
        override=False,
    )

    
    # 4. リトリーバーのセットアップ
    retriever = retrieve.ColBERT(index=index)

    results = retriever.retrieve(
        queries_embeddings=queries_embeddings,
        k=3
    )[0]


    file_list = []
    descriptions = []
    for result in results:
        retriever_id = search_id_data.get(result["id"])

        desc_str = description_data.get(retriever_id)

        file_list.append(desc_str["path"])
        descriptions.append(desc_str["description"])
    print(file_list)

    return {"result": "success", "file_paths": file_list, "descriptions": descriptions}

if __name__ == "__main__":
    uvicorn.run("retrieval_api:app", host="0.0.0.0", port=7860, reload=True)