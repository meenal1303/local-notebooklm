import streamlit as st
import os
import tempfile

from build_index import build_index
from chat import answer

# --- Page setup ---
st.set_page_config(page_title="Local NotebookLM", page_icon="📚")
st.title("📚 Chat with your PDF")
st.caption("100% local — Ollama + Chroma + Streamlit")

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed" not in st.session_state:
    st.session_state.indexed = False

# --- Sidebar: upload and index ---
with st.sidebar:
    st.header("Your document")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded_file and st.button("Index this PDF"):
        # Save upload to a temp file (build_index expects a path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        with st.spinner("Extracting text, chunking, and embedding... this may take a minute."):
            n_chunks = build_index(pdf_path=tmp_path)

        os.unlink(tmp_path)  # clean up temp file
        st.session_state.indexed = True
        st.session_state.messages = []  # reset chat for new doc
        st.success(f"Indexed {n_chunks} chunks. Ask away!")

    if st.session_state.indexed:
        st.info("✅ Document indexed and ready.")
    else:
        st.warning("Upload and index a PDF to start chatting.")

# --- Main area: chat ---
# Replay existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# New user input
if question := st.chat_input("Ask something about your document..."):
    if not st.session_state.indexed:
        st.error("Please upload and index a PDF first.")
    else:
        # Show user message
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # Get and show assistant reply
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply, chunks_used = answer(question)
            st.markdown(reply)
            with st.expander(f"📎 Sources ({len(chunks_used)} chunks used)"):
                for i, chunk in enumerate(chunks_used, start=1):
                    st.markdown(f"**Chunk {i}:**")
                    st.text(chunk[:500] + ("..." if len(chunk) > 500 else ""))

        st.session_state.messages.append({"role": "assistant", "content": reply})
