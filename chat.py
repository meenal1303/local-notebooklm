import ollama
import chromadb

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "my_docs"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3.2:3b"
TOP_K = 4


def retrieve(query, top_k=TOP_K):
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)

    query_embedding = ollama.embeddings(
        model=EMBED_MODEL, prompt=query
    )["embedding"]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )
    return list(zip(results["documents"][0], results["metadatas"][0]))


def build_prompt(question, chunks_with_meta):
    context_parts = []
    for chunk_text, meta in chunks_with_meta:
        source = meta.get("source", "unknown")
        context_parts.append(f"[From {source}]\n{chunk_text}")
    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""You are a helpful assistant answering questions about a document.
Use ONLY the context below to answer the question.
If the context doesn't contain enough information to answer, say
When information is used, mention which document it came from.
"I couldn't find that in the document."
Do not use any outside knowledge.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
    return prompt

def answer(question):
    chunks_with_meta = retrieve(question)
    prompt = build_prompt(question, chunks_with_meta)
    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"], chunks_with_meta


if __name__ == "__main__":
    while True:
        question = input("\nAsk (or 'quit'): ").strip()
        if question.lower() in ("quit", "exit", "q"):
            break

        print("\nThinking...\n")
        reply, chunks_used = answer(question)

        print("=" * 60)
        print("ANSWER:")
        print(reply)
        print("=" * 60)
        print(f"\n(Answer based on {len(chunks_used)} retrieved chunks)")
