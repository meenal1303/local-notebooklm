import ollama
import chromadb

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "my_docs"
EMBED_MODEL = "nomic-embed-text"
TOP_K = 3  # how many chunks to retrieve


def search(query, top_k=TOP_K):
    # 1. Connect to the existing index
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)

    # 2. Embed the question using the SAME model as indexing
    response = ollama.embeddings(model=EMBED_MODEL, prompt=query)
    query_embedding = response["embedding"]

    # 3. Ask Chroma for the top_k closest chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    return results


if __name__ == "__main__":
    question = input("Ask a question about your document: ")
    results = search(question)

    print(f"\nTop {TOP_K} relevant chunks:\n")
    for i, (doc, distance) in enumerate(
        zip(results["documents"][0], results["distances"][0]),
        start=1,
    ):
        print(f"--- Chunk {i} (distance: {distance:.4f}) ---")
        print(doc[:400])
        print()
