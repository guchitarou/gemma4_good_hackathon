# 🚀 Quick Start

## Prerequisites
- Docker with NVIDIA Container Toolkit
- NVIDIA GPU

---


### Option A: Built-in (gemma4.py)
coming soon

### Option B: Ollama
> ⚠️ **Note:** Video and audio inputs are not supported in this mode.

Install Ollama and pull the model:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma4
```

Then update `config.py` with your machine's IP:

```python
OLLAMA_GEMMA4_APIURL = "http://<your-local-ip>:11434"
```

## Setup & Launch

```bash
git clone https://github.com/yourname/gemma4_good_hackathon.git
cd gemma4_good_hackathon
docker build -t wowsearch .
docker run --gpus all --network host -it --name wowsearch_container -v .:/app wowsearch:latest bash
./start.sh
```

Once ready:
```
✅ All processes started! Press Ctrl+C to stop.
```

---

## Access


[http://localhost:7862/Upload](http://localhost:7862/Upload)


