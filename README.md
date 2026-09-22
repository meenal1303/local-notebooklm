# 📚 local-notebooklm

A **fully local** NotebookLM-style RAG app: chat with your PDFs using an LLM running on your own machine. No API keys, no cloud, no data leaves your Mac.

Built with [Ollama](https://ollama.com), [ChromaDB](https://www.trychroma.com/), [LangChain](https://www.langchain.com/), and [Streamlit](https://streamlit.io/).

## ✨ Features

- 📄 Upload any PDF (text-based or scanned — OCR fallback via Tesseract)
- 🔍 Semantic search over document chunks using local embeddings
- 💬 Chat with your document through a browser-based UI
- 📎 Every answer shows the source chunks it was based on
- 🔒 100% local — nothing leaves your machine

## 🏗️ How it works

```
PDF → text extraction → chunking → embeddings → ChromaDB
                                                     ↓
                          your question → embedding → search → top-k chunks
                                                                    ↓
                                            LLM generates answer using chunks
```

## 🛠️ Tech stack

| Piece | Tool |
|---|---|
| LLM | Llama 3.2 (3B) via Ollama |
| Embeddings | nomic-embed-text via Ollama |
| Vector DB | ChromaDB (local, persistent) |
| PDF extraction | PyMuPDF |
| OCR (fallback) | Tesseract + pytesseract |
| Chunking | LangChain RecursiveCharacterTextSplitter |
| UI | Streamlit |

## 🚀 Setup

### Prerequisites

- macOS with Apple Silicon (M1/M2/M3/M4 recommended)
- Python 3.10+
- [Homebrew](https://brew.sh)

### 1. Install Ollama and pull models

```bash
# Install Ollama from https://ollama.com/download
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### 2. Install Tesseract (for OCR)

```bash
brew install tesseract
```

### 3. Clone and set up Python env

```bash
git clone https://github.com/meenal1303/local-notebooklm.git
cd local-notebooklm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501, upload a PDF, click **Index this PDF**, and start chatting.

## 📁 Project structure

```
local-notebooklm/
├── app.py                # Streamlit UI
├── build_index.py        # PDF → chunks → embeddings → ChromaDB
├── chat.py               # Retrieval + LLM answer generation
├── read_pdf_smart.py     # PDF extraction with OCR fallback
├── check_index.py        # Debug tool: inspect what's in ChromaDB
├── search.py             # Debug tool: test retrieval without the LLM
├── requirements.txt
└── README.md
```

## 🧠 What I learned building this

- How RAG actually works under the hood (chunking, embeddings, vector search, prompt assembly)
- Why chunk size and overlap matter for retrieval quality
- The difference between semantic search and keyword search
- How to keep an LLM grounded (anti-hallucination prompting)
- How Streamlit's rerun model works, and how to manage state across it
- Debugging pipelines with lightweight print-based observability

## 🗺️ Roadmap

- [ ] Streaming responses (token-by-token)
- [ ] Multi-document support (chat across several PDFs)
- [ ] Upgrade OCR to GLM-OCR for tables and formulas
- [ ] Chat memory for multi-turn conversations
- [ ] Better source citations (page numbers, highlighted spans)

## 📝 License

MIT
