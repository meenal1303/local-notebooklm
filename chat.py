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
    return results["documents"][0]  # list of chunk texts


def build_prompt(question, chunks):
    context = "\n\n---\n\n".join(chunks)
    prompt = f"""You are a helpful assistant answering questions about a document.
Use ONLY the context below to answer the question.
If the context doesn't contain enough information to answer, say
"I couldn't find that in the document."
Do not use any outside knowledge.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
    return prompt


def answer(question):
    # 1. Retrieve relevant chunks
    chunks = retrieve(question)

    # 2. Build prompt
    prompt = build_prompt(question, chunks)

    # 3. Ask the LLM
    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"], chunks


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
