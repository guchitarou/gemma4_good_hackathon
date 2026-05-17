apt-get update
apt-get install -y ffmpeg

pip install --upgrade pip
pip install -U "huggingface_hub[cli]"
pip install -r requirements_gemma4_local.txt

pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124