
# 🔗 WowSearch — Find Files That Feel Related, powered by Gemma 4

---
## What It Does
**WowSearch** is a tool powered by **Google's Gemma 4** model that understands your files both structurally and semantically, helping creators spark their next "Wow" idea.

### 📊 File Relationship Graph Analysis

Upload a collection of files and WowSearch analyzes their relationships, visualizing semantic connections as an interactive **graph of nodes** and edges — so you can instantly see what your files have in common.

- Each **node** represents a file (document, image, audio clip, video, etc.)
- Each **edge** represents a detected relationship between two files (e.g., shared topics, citations, complementary content)
- The graph can be explored interactively to drill into specific connections

### 💬 Chat-Based Multimodal Search & Recommendations

Using Gemma 4's enhanced multimodal reasoning capabilities, WowSearch lets you search across your files and discover ideal cross-media combinations through a natural chat interface.

Ask questions like:
- *"Which video clip best pairs with this background music?"*
- *"Find an image that complements this article."*
- *"What audio track fits the mood of this video?"*

Gemma 4's ability to reason across **video, audio, text, and image** modalities simultaneously powers these recommendations — going far beyond simple keyword search.

---

## Why Gemma 4?
Gemma 4's multimodal capabilities make it uniquely suited for this system:

1. **Understanding file content semantically**, not just by filename or metadata
2. **Reasoning across different media types** to surface non-obvious relationships
3. **Delivering nuanced recommendations** that reflect how humans naturally combine media (e.g., a melancholic piano track paired with a time-lapse sunset video)
4. **Running locally**, ensuring no data is sent to external servers and sensitive files can be handled without any security risks

---

## Architecture Overview



---

## Getting Started

### Prerequisites

- Python WowSearch or higher
- WowSearch (e.g., GPU with CUDA support / CPU-only mode)
- [Hugging Face account](https://huggingface.co/) with access to Gemma 4

### Installation


### Set up credentials


### Run


## Usage

### 1. Upload Files

Drag and drop your files (documents, images, audio, video) into the upload area. WowSearch supports the following formats:

- **Text / Documents:** `.txt`, `.md`, `.pdf`, `.docx` (WowSearch)
- **Images:** `.jpg`, `.png`, `.webp` (WowSearch)
- **Audio:** `.mp3`, `.wav` (WowSearch)
- **Video:** `.mp4`, `.mov` (WowSearch)

### 2. Explore the Relationship Graph

Once files are processed, the graph view renders automatically. You can:
- Click on a **node** to see file details
- Click on an **edge** to understand why two files are connected
- Filter by file type or relationship strength

### 3. Chat-Based Search

Switch to the **Chat** tab and ask natural language questions:

```
You: Which audio file would pair best with video_001.mp4?
Assistant: Based on the mood and pacing of video_001.mp4, audio_003.mp3 would
           be a strong match. Both share a [WowSearch] tone and similar energy levels...
```

---

## Example Scenarios

### 🎬 Content Creator
Upload a batch of video footage, voiceover recordings, background music, and script drafts. WowSearch reveals which combinations are most coherent and suggests ideal pairings for your edit.

### 📚 Researcher
Drop in a collection of papers, figures, and datasets. The graph shows citation-like relationships and topic clusters — helping you see the "shape" of your research at a glance.

### 🎨 Designer
Upload mood board images alongside copy text. Get recommendations on which images best reflect the written tone and vice versa.

---

## Limitations & Known Issues

- Processing time scales with file size and count; large batches may take several minutes (WowSearch)
- Audio and video analysis requires WowSearch VRAM / RAM (WowSearch)
- Relationship detection accuracy depends on file content quality
- Chat recommendations are suggestions, not guarantees — human judgment is still recommended

---

## Project Structure

```
WowSearch/
├── WowSearch/              # Core application code
├── WowSearch/              # Tests
├── requirements.txt
├── .env.example
└── README.md
```

---

## References

- [Gemma 4](https://ai.google.dev/gemma) — Google's multimodal open model
- [Kaggle: Gemma 4 Good Hackathon](https://www.kaggle.com/competitions/gemma-4-good-hackathon)

---


*Built for the Gemma 4 Good Hackathon.*
