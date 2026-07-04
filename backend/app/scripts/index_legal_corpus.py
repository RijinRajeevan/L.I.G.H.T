import os
import sys
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb

# Ensure we can import app modules when run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def index_dataset(csv_path: str, collection_name: str, desc_col: str, sec_col: str):
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    print(f"Loading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Handle optional columns silently if they don't match exactly
    cols = df.columns.tolist()
    d_col = next((c for c in cols if desc_col.lower() in c.lower() or "offense" in c.lower()), cols[1] if len(cols)>1 else cols[0])
    s_col = next((c for c in cols if sec_col.lower() in c.lower()), cols[0])
    
    df[d_col] = df[d_col].fillna('')
    df[s_col] = df[s_col].fillna('')

    print("Initializing embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Resolve absolute path relative to this file's directory (backend/app/scripts)
    # We want backend/app/data/chroma_db
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "chroma_db")
    
    print(f"Initializing Vector DB at: {db_path}")
    os.makedirs(db_path, exist_ok=True)
    client = chromadb.PersistentClient(path=db_path)
    
    collection = client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})
    
    # Process in batches to avoid OOM
    texts = df[d_col].tolist()
    sections = df[s_col].tolist()
    
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_sections = sections[i:i+batch_size]
        
        print(f"Encoding batch {i} to {i+len(batch_texts)} for {collection_name}...")
        embeddings = model.encode(batch_texts).tolist()
        
        ids = [f"{collection_name}_{idx}" for idx in range(i, i+len(batch_texts))]
        metadatas = [{"section": str(sec), "source": collection_name} for sec in batch_sections]
        
        collection.add(
            embeddings=embeddings,
            documents=batch_texts,
            metadatas=metadatas,
            ids=ids
        )
        
    print(f"Finished indexing {collection_name} successfully!")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # IPC Indexing
    ipc_path = os.path.join(base_dir, "data", "ipc", "ipc.csv")
    index_dataset(ipc_path, "ipc", "desc", "section")
    
    # BSA Indexing
    bsa_path = os.path.join(base_dir, "data", "bsa", "bsa_sections.csv")
    index_dataset(bsa_path, "bsa", "desc", "section")

if __name__ == "__main__":
    main()
