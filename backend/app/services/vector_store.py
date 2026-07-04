import os
import chromadb
from sentence_transformers import SentenceTransformer
import logging

from ..utils.circuit_breaker import circuit_breaker

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, db_path=None, model_name="all-MiniLM-L6-v2"):
        if db_path is None:
            # Resolve absolute path relative to this file's directory (backend/app/services)
            # We want backend/app/data/chroma_db
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "data", "chroma_db")
            
        logger.info(f"Initializing VectorStore at: {db_path}")
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Load embedding model once per instance 
        try:
            self.embedding_model = SentenceTransformer(model_name)
            self.model_available = True
            logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            self.embedding_model = None
            self.model_available = False
            logger.error(f"CRITICAL: Failed to load SentenceTransformer model '{model_name}': {e}. Vector search will be disabled.")
    
    def get_collection(self, collection_name: str):
        # get or create
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    @circuit_breaker(failure_threshold=3, recovery_timeout=30)
    def search(self, collection_name: str, query: str, top_k: int = 5):
        try:
            collection = self.get_collection(collection_name)
            
            if not self.model_available or self.embedding_model is None:
                logger.warning("Vector search requested but model is not available. Returning empty results.")
                return []
                
            # Generate generic query embeddings rather than tf-idf sparse maps
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Formatting results
            formatted_results = []
            if results and results["documents"] and results["documents"][0]:
                for idx, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][idx] if results["metadatas"] else {}
                    distance = results["distances"][0][idx] if results["distances"] else 1.0
                    
                    # Convert cosine distance to a similarity-like score
                    score = 1.0 - distance
                    if score < 0.2:
                        continue
                        
                    record = dict(metadata)
                    record['Description'] = doc # Map back to expected interface
                    record['Section'] = metadata.get('section', 'Unknown')
                    record['score'] = float(score)
                    formatted_results.append(record)
                    
            return formatted_results
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

# Singleton Factory
_vector_store = None

def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
