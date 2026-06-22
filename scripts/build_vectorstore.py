"""Build the Chroma vector store used by the RAG FrontierAgent.

Usage:
    uv run python scripts/build_vectorstore.py --lite      # 20k items (fast)
    uv run python scripts/build_vectorstore.py             # full 800k items
"""

import argparse
import os

from dotenv import load_dotenv
from huggingface_hub import login
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import chromadb

from dealscout.core.items import Item

DB = "products_vectorstore"
COLLECTION_NAME = "products"
HF_USERNAME = "Ankit-Singh-ai"


def build(lite: bool) -> None:
    load_dotenv(override=True)
    if os.environ.get("HF_TOKEN"):
        login(token=os.environ["HF_TOKEN"], add_to_git_credential=False)

    dataset = f"{HF_USERNAME}/dealscout_items_lite" if lite else f"{HF_USERNAME}/dealscout_items_full"
    train, _val, _test = Item.from_hub(dataset)
    print(f"Loaded {len(train):,} training items from {dataset}")

    client = chromadb.PersistentClient(path=DB)
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        print(f"Collection '{COLLECTION_NAME}' already exists - delete {DB}/ to rebuild.")
        return

    encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    collection = client.create_collection(COLLECTION_NAME)

    for i in tqdm(range(0, len(train), 1000)):
        batch = train[i : i + 1000]
        documents = [item.summary for item in batch]
        vectors = encoder.encode(documents).astype(float).tolist()
        metadatas = [{"category": item.category, "price": item.price} for item in batch]
        ids = [f"doc_{j}" for j in range(i, i + len(batch))]
        collection.add(ids=ids, documents=documents, embeddings=vectors, metadatas=metadatas)

    print(f"Done. Vector store written to ./{DB}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the DealScout Chroma vector store")
    parser.add_argument("--lite", action="store_true", help="Use the smaller lite dataset")
    args = parser.parse_args()
    build(lite=args.lite)