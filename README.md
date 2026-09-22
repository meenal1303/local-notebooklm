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

## 🗺️ What's next

Ideas I explored during this build but chose not to ship in v1 — good candidates for future iterations.

### Retrieval quality
- **Query decomposition** — automatically split compound questions ("what does X do and where is Y based?") into standalone sub-queries, retrieve for each, then combine. Real RAG systems (LlamaIndex, Haystack) do this out of the box.
- **Per-source retrieval balancing** — instead of top-K across everything, retrieve top-K from *each* document. Prevents large documents from drowning out smaller ones.
- **Re-ranking** — after retrieval, re-score the top 20 chunks with a smarter cross-encoder model and keep the best 5. Meaningfully improves precision.
- **Hybrid search** — combine semantic (embeddings) with keyword (BM25) search. Catches cases where the query mentions an exact term the embedder doesn't emphasize.

### UX
- **Streaming responses** — tokens appear as they're generated, ChatGPT-style. Ollama supports it natively with `stream=True`.
- **Chat memory** — multi-turn conversations where "and the second one?" resolves against prior turns. Involves query rewriting with the LLM before retrieval.
- **Better citations** — link each cited chunk back to the exact page and highlighted span in the source PDF.
- **Per-document scoping** — a dropdown to chat with "just this one PDF" instead of the whole corpus.

### Extraction
- **GLM-OCR upgrade** — swap Tesseract for GLM-OCR (a modern vision-language model) for better handling of tables, math, and complex layouts. Especially valuable for research papers and financial docs.
- **Layout-aware chunking** — chunk on section boundaries (headings, tables) rather than character counts. Preserves semantic structure.

### Ops
- **Evaluation harness** — a small test set of Q&A pairs with expected sources, and metrics like retrieval recall@k and answer faithfulness. This is what separates a toy from a real product.
- **Bigger models** — try `qwen2.5:7b` or `llama3.1:8b` for higher-quality answers when latency is less critical.
- **Streaming ingestion** — process very large PDFs page-by-page rather than loading the whole document into memory.

## 🐛 Known limitations

- **Compound queries** across multiple docs may under-retrieve smaller documents (mitigated by `TOP_K=8`, but not fully solved without query decomposition).
- **Scanned PDFs with complex layouts** (tables, multi-column) may lose structure through Tesseract OCR.
- **Small LLM (3B)** occasionally paraphrases loosely; larger models would answer more precisely.
- **No chat memory** — each question is standalone; follow-ups won't resolve pronouns from previous turns.

## 🙏 Acknowledgments

Built as a hands-on RAG learning project. Thanks to the open-source teams behind Ollama, ChromaDB, LangChain, Streamlit, and PyMuPDF for making local AI genuinely accessible.

## 📝 License

MIT
