import os
from pydub import AudioSegment

input_folder = "./DataFolder"
output_folder = "./out_audio"

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.endswith(".mp3"):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        audio = AudioSegment.from_mp3(input_path)
        trimmed = audio[:25 * 1000]
        trimmed.export(output_path, format="mp3")
        print(f"処理完了: {filename}")

print("全ファイル処理完了")