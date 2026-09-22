import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("my_docs")

print(f"Chunks stored: {collection.count()}")

# Pull the first 2 chunks to look at
sample = collection.get(limit=2, include=["documents", "embeddings"])

for i, (doc, emb) in enumerate(zip(sample["documents"], sample["embeddings"])):
    print(f"\n--- Chunk {i} ---")
    print(f"Text (first 200 chars): {doc[:200]}...")
    print(f"Embedding: {len(emb)} numbers, first 5: {emb[:5]}")
