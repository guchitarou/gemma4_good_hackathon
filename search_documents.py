import json
import glob

from pylate import indexes, models
import pymupdf4llm
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import COLBERT_MODEL_WEIGHTS_PATH, FILE_DESCRIPTIONS_JSON_PATH, SEARCH_ID_JSON_PATH

# チャンクとIDの対応をJSONで保存
with open(FILE_DESCRIPTIONS_JSON_PATH, "r", encoding="utf-8") as f:
    description_data = json.load(f)



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
    chunk_size=256,      # トークン数ではなく文字数なので少し多めに
    chunk_overlap=50,    # 前後の文脈を引き継ぐ
    separators=["。", "、", "\n", " ", ""],  # 日本語向け区切り
)

# チャンクとIDの対応をJSONで保存
id_to_text = {str(i): chunk for i, chunk in enumerate(documents_ids)}

with open(SEARCH_ID_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(id_to_text, f, ensure_ascii=False, indent=2)

print(f"PDFから抽出されたテキストを{len(documents_chunks)}チャンクに分割し、IDと対応付けて保存しました。")



# 1. モデルのロード
model = models.ColBERT(
    model_name_or_path = COLBERT_MODEL_WEIGHTS_PATH
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
    index_name="jacolbert-index",
    override=False,
)
print(index)

documents_ids = [str(i) for i in range(len(documents_chunks))]



index.add_documents(
    documents_ids=documents_ids,
    documents_embeddings=documents_embeddings,
)


print("pylate-index/ に保存されました。")