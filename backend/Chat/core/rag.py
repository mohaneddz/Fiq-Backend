"""
RAG (Retrieval Augmented Generation) implementation.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from typing import List, Dict
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
from Chat import config
from shared.db import DatabaseManager


class RAGEngine:
    """RAG engine for semantic search over drug database."""
    
    def __init__(self):
        self.embedding_model = None
        self.index = None
        self.documents = []
        self.db = DatabaseManager(config.DRUGS_DB_PATH)
        
        # Load or create vector store
        if os.path.exists(config.VECTOR_STORE_PATH):
            self.load_index()
        else:
            os.makedirs(os.path.dirname(config.VECTOR_STORE_PATH), exist_ok=True)
    
    def _get_embedding_model(self):
        """Lazy load embedding model."""
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        return self.embedding_model
    
    def ingest_drugs(self) -> Dict:
        """
        Build vector index from drugs database.
        
        Returns:
            Dictionary with ingestion stats
        """
        try:
            # Fetch all drugs from database
            drugs = self.db.execute_query("SELECT * FROM drugs")
            
            if not drugs:
                return {"status": "error", "message": "No drugs found in database"}
            
            # Create documents from drug records
            self.documents = []
            texts = []
            
            for drug in drugs:
                # Combine relevant fields into searchable text
                doc_text = f"""
                Drug: {drug.get('name', '')}
                Common Name: {drug.get('common_name', '')}
                Category: {drug.get('category', '')}
                Effects: {drug.get('effects', '')}
                Risks: {drug.get('risks', '')}
                Treatment: {drug.get('treatment', '')}
                """.strip()
                
                self.documents.append({
                    "text": doc_text,
                    "metadata": drug
                })
                texts.append(doc_text)
            
            # Generate embeddings
            model = self._get_embedding_model()
            embeddings = model.encode(texts, show_progress_bar=True)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype('float32'))
            
            # Save index
            self.save_index()
            
            return {
                "status": "success",
                "documents_indexed": len(self.documents),
                "dimension": dimension
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def query(self, query_text: str, top_k: int = None) -> List[Dict]:
        """
        Perform semantic search.
        
        Args:
            query_text: Query string
            top_k: Number of results to return
            
        Returns:
            List of matching documents with scores
        """
        if self.index is None or not self.documents:
            return []
        
        top_k = top_k or config.RAG_TOP_K
        
        try:
            # Encode query
            model = self._get_embedding_model()
            query_embedding = model.encode([query_text])[0]
            
            # Search
            distances, indices = self.index.search(
                query_embedding.reshape(1, -1).astype('float32'),
                top_k
            )
            
            # Format results
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.documents):
                    results.append({
                        "document": self.documents[idx],
                        "score": float(distances[0][i]),
                        "rank": i + 1
                    })
            
            return results
        except Exception as e:
            print(f"RAG query error: {e}")
            return []
    
    def save_index(self):
        """Save FAISS index and documents to disk."""
        faiss.write_index(self.index, f"{config.VECTOR_STORE_PATH}.index")
        with open(f"{config.VECTOR_STORE_PATH}.docs", 'wb') as f:
            pickle.dump(self.documents, f)
    
    def load_index(self):
        """Load FAISS index and documents from disk."""
        try:
            self.index = faiss.read_index(f"{config.VECTOR_STORE_PATH}.index")
            with open(f"{config.VECTOR_STORE_PATH}.docs", 'rb') as f:
                self.documents = pickle.load(f)
        except Exception as e:
            print(f"Failed to load index: {e}")
            self.index = None
            self.documents = []
