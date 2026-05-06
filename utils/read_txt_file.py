import os
from pathlib import Path
import chardet # pip install chardet (文字コード自動判定用)
import pymupdf4llm
def file_to_string(file_path):
    """
    あらゆるファイルをstringに変換して返す
    """

    extension = Path(file_path).suffix.lstrip(".")

    if(extension not in ['pdf', 'html', 'py', 'java']):
        raise Exception(f"File type .{extension} is not supported for text extraction. Attempting binary read instead.")


    # 1. まずはテキストとして読み込みを試みる
    try:
         # 強制的に例外を出してPDF等の処理に行かせる

        if(extension in ['pdf']):
            pdf_text = pymupdf4llm.to_markdown(file_path)
            return pdf_text
        else:
            with open(file_path) as f:
                raw_data = f.read()
                print(f"Raw data read from file (first 100 bytes): {raw_data[:100]}")  # デバッグ用に最初の100バイトを表示

                return raw_data

    except Exception as e:
        return f"Error reading file: {str(e)}"

# 使用例
if __name__ == "__main__":
    test_file = "./DataFolder/GANPrototype.py"
    result_string = file_to_string(test_file)
    print(result_string) # 最初の1000文字を表示