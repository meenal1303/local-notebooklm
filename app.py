import streamlit as st
import os
import tempfile
import chromadb

from build_index import build_index
from chat import answer

# --- Page setup ---
st.set_page_config(page_title="Local NotebookLM", page_icon="📚")
st.title("📚 Chat with your PDFs")
st.caption("100% local — Ollama + Chroma + Streamlit")

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar: upload, index, and show what's indexed ---
with st.sidebar:
    st.header("Your documents")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded_file and st.button("Index this PDF"):
        # Reset file pointer (Streamlit reuses the file object across reruns)
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        st.write(f"Indexing `{uploaded_file.name}` ({len(file_bytes):,} bytes)")

        # Save upload to a temp file, keeping the original filename
        # so metadata reflects the real name (not tmp gibberish)
        tmp_dir = tempfile.mkdtemp()
        tmp_path = os.path.join(tmp_dir, uploaded_file.name)
        with open(tmp_path, "wb") as tmp:
            tmp.write(file_bytes)

        with st.spinner("Extracting, chunking, embedding... this may take a minute."):
            n_chunks = build_index(pdf_path=tmp_path)

        os.unlink(tmp_path)
        os.rmdir(tmp_dir)
        st.session_state.messages = []  # reset chat when the corpus changes
        st.success(f"Indexed {n_chunks} chunks from {uploaded_file.name}.")

    st.divider()

    # Live listing of what's currently in ChromaDB
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_or_create_collection(
            name="my_docs",
            metadata={"hnsw:space": "cosine"},
        )
        all_meta = collection.get()["metadatas"] or []
        sources = sorted({m["source"] for m in all_meta if m and "source" in m})

        if sources:
            st.markdown("**Indexed documents:**")
            for s in sources:
                st.markdown(f"- `{s}`")
            st.caption(f"Total chunks: {collection.count()}")
        else:
            st.warning("No documents indexed yet. Upload a PDF to start.")
    except Exception as e:
        st.warning(f"Couldn't read collection: {e}")

# --- Main area: chat ---
# Replay existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# New user input
if question := st.chat_input("Ask something about your documents..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply, chunks_used = answer(question)
        st.markdown(reply)

        with st.expander(f"📎 Sources ({len(chunks_used)} chunks used)"):
            for i, (chunk, meta) in enumerate(chunks_used, start=1):
                source = meta.get("source", "unknown")
                st.markdown(f"**Chunk {i} — from `{source}`:**")
                st.text(chunk[:500] + ("..." if len(chunk) > 500 else ""))

    st.session_state.messages.append({"role": "assistant", "content": reply})
