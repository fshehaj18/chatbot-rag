from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.IndexFlatL2(384)
texts = []
sources = []

INDEX_FILE = "vector.index"
META_FILE = "meta.pkl"

def embed_chunks(all_pdf_texts, chunk_size=500, overlap=100):
    global texts, sources, index

    for filename, full_text in all_pdf_texts:
        if not full_text.strip():
            continue

        # --- improved chunking with overlap ---
        chunks = []
        start = 0
        text_length = len(full_text)

        while start < text_length:
            end = start + chunk_size
            chunk = full_text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - overlap

        if not chunks:
            continue

        # --- normalized embeddings (important) ---
        embeddings = model.encode(
            chunks,
            normalize_embeddings=True
        )

        index.add(np.array(embeddings, dtype="float32"))
        texts.extend(chunks)
        sources.extend([filename] * len(chunks))

    print(f"✅ Embedded {len(texts)} chunks total")

    # Save index + metadata for reuse (optional)
    faiss.write_index(index, INDEX_FILE)
    with open(META_FILE, "wb") as f:
        pickle.dump({"texts": texts, "sources": sources}, f)

def load_embeddings():
    """Reload previously saved embeddings (to avoid re-embedding every run)."""
    global texts, sources, index
    if os.path.exists(INDEX_FILE) and os.path.exists(META_FILE):
        index = faiss.read_index(INDEX_FILE)
        with open(META_FILE, "rb") as f:
            meta = pickle.load(f)
        texts = meta["texts"]
        sources = meta["sources"]
        print(f"✅ Loaded {len(texts)} chunks from disk.")
    else:
        print("⚠️ No saved embeddings found. Run embed_chunks() first.")
        all_files = load_embeddings("data")
        embed_chunks(all_files)

def search(query, top_k=3):
    if len(texts) == 0:
        print("⚠️ No texts embedded — call embed_chunks() first.")
        return []

    query_emb = model.encode([query])
    D, I = index.search(np.array(query_emb), top_k)

    results = []
    for idx in I[0]:
        if 0 <= idx < len(texts):
            results.append((texts[idx], sources[idx]))
        else:
            print(f"⚠️ Skipping invalid index {idx}")
    return results
