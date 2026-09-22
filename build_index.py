import ollama
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from read_pdf_smart import extract_text_from_pdf
import os

# --- Config ---
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "my_docs"
PDF_PATH = "sample.pdf"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def build_index(pdf_path=PDF_PATH, collection_name=COLLECTION_NAME):
    source_name = os.path.basename(pdf_path) 
    
    # 1. Extract text from the PDF (using our Stage 3 function)
    print(f"Extracting text from {pdf_path}...")
    full_text = extract_text_from_pdf(pdf_path)
    print(f"Got {len(full_text)} characters total.\n")

    # 2. Chunk the text
    print("Chunking text...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(full_text)
    print(f"Created {len(chunks)} chunks.\n")

    # 3. Set up ChromaDB (persists to disk)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


    # 4. Remove any existing chunks from this same source (so re-indexing works)
    existing = collection.get(where={"source": source_name})
    if existing["ids"]:
        collection.delete(ids=existing["ids"])
        print(f"Removed {len(existing['ids'])} old chunks from {source_name}.\n")

    # 5. Embed each chunk and store it
    print("Embedding and storing chunks (this may take a minute)...")
    for i, chunk in enumerate(chunks):
        # Get the embedding from Ollama
        response = ollama.embeddings(model=EMBED_MODEL, prompt=chunk)
        embedding = response["embedding"]

        # Store: id, embedding, and the original text
        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=[embedding],
            documents=[chunk],
	    metadatas=[{"source": source_name}],
        )

        if (i + 1) % 10 == 0 or i == len(chunks) - 1:
            print(f"  Stored {i + 1} / {len(chunks)}")

    print(f"\n✅ Done! Index saved to {CHROMA_DIR}")


if __name__ == "__main__":
    build_index()
