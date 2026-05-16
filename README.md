
# 🔗 WowSearch — Find Files That Feel Related, powered by Gemma 4

---

![screen img](./desc_imgs/UI0.png)

## The Problem

Your files are silent. File Explorer stores them — but never understands them.


It can't tell you which music fits your video, or what that file even contains until you open it.


Finding the *right* combination is slow, accidental, and exhausting.
And the more files you have, the worse it gets.


## What It Does
**WowSearch** is a tool powered by **Google's Gemma 4** model that understands your files both structurally and semantically, helping creators spark their next "Wow" idea.

### 💬 Chat-Based Multimodal Search & Recommendations

Using Gemma 4's enhanced multimodal reasoning capabilities, WowSearch lets you search across your files and discover ideal cross-media combinations through a natural chat interface.

Ask questions like:
- *"Which video clip best pairs with this background music?"*
- *"Find an image that complements this article."*
- *"What audio track fits the mood of this video?"*

Gemma 4's ability to reason across **video, audio, text, and image** modalities simultaneously powers these recommendations — going far beyond simple keyword search.



### 📊 File Relationship Graph Analysis

Upload a collection of files and WowSearch analyzes their relationships, visualizing semantic connections as an interactive **graph of nodes** and edges — so you can instantly see what your files have in common.

- Each **node** represents a file (document, image, audio clip, video, etc.)
- Each **edge** represents a detected relationship between two files (e.g., shared topics, citations, complementary content)
- The graph can be explored interactively to drill into specific connections


---

## Why Gemma 4?
Gemma 4's multimodal capabilities make it uniquely suited for this system:

1. **Understanding file content semantically**, not just by filename or metadata
2. **Reasoning across different media types** to surface non-obvious relationships
3. **Delivering nuanced recommendations** that reflect how humans naturally combine media (e.g., a melancholic piano track paired with a time-lapse sunset video)
4. **Running locally**, ensuring no data is sent to external servers and sensitive files can be handled without any security risks

---



## Architecture Overview

![Architecture Overview](./desc_imgs/Architecture_Overview.png)


## 🛠️Installation
For environment setup and how to run the app, see the guide.

[Quick Start](Env.md)

---

## Usage

### 1. Data Ingestion
Place the data files you want to analyze into the `gemma4_good_hackathon/DataFolder` directory,
then click the **Ingest** button in the app to load them. 

![ingest img](./desc_imgs/Ingest.gif)

WowSearch supports the following formats:

- **Text / Documents:** `.txt`, `.md`, `.pdf`, `.py`
- **Images:** `.png`
- **Audio:** `.mp3` (max. 20s)
- **Video:** `.mp4` (max. 60s)

### 2. Chat-Based Search

Switch to the **Chat** tab and ask natural language questions:

```
You: I want to improve th~~~?
```

```
Assistant: ~~~
```

### 2. Explore the Relationship Graph

Once files are processed, the graph view renders automatically. You can:
- Click on a **node** to see file details
- Click on an **edge** to understand why two files are connected
- Filter by file type or relationship strength

![graph](./desc_imgs/graph.gif)



---

## Example Scenarios

### 🎬 Content Creator
Upload a batch of video footage, voiceover recordings, background music, and script drafts. WowSearch reveals which combinations are most coherent and suggests ideal pairings for your edit.

### 📚 Researcher
Drop in a collection of papers, figures, and datasets. The graph shows citation-like relationships and topic clusters — helping you see the "shape" of your research at a glance.

### 🎨 Designer
Upload mood board images alongside copy text. Get recommendations on which images best reflect the written tone and vice versa.

---

## Experiments and Results



### Experiment 1: HTML File Input — Visual Improvement Suggestions

user input : 
```
attached file : RPG.html
I want to improve the visual quality of this game. Can you suggest some assets I could use?
```

Wowsearchoutput:
```
Better character sprite.
```
#### recmend file
![caractor](./desc_imgs/caractorImage.png)









## Limitations & Known Issues

- Processing time scales with file size and count; large batches may take several minutes (WowSearch)
- Audio and video analysis requires WowSearch VRAM / RAM (WowSearch)
- Relationship detection accuracy depends on file content quality
- Chat recommendations are suggestions, not guarantees — human judgment is still recommended

---

## References
- [Kaggle: Gemma 4 Good Hackathon](https://www.kaggle.com/competitions/gemma-4-good-hackathon)
- [Gemma 4](https://ai.google.dev/gemma) — Google's multimodal open model
- [colbert](https://huggingface.co/colbert-ir/colbertv2.0)
---


*Built for the Gemma 4 Good Hackathon.*
