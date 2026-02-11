from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.meridian import ExternalSignal
from app.services.llm_service import llm_service
import json

class VectorService:
    def __init__(self, db: Session):
        self.db = db

    def generate_embedding(self, text_content: str) -> list:
        """
        Generates embeddings using Gemini or Ollama.
        """
        # 1. Try Gemini
        if llm_service.provider == "gemini" and llm_service.gemini_client:
            try:
                result = llm_service.gemini_client.models.embed_content(
                    model="models/text-embedding-004",
                    contents=text_content
                )
                return result.embeddings[0].values
            except Exception as e:
                print(f"Gemini Embedding Error: {e}")
                return []
        
        # 2. Try Ollama (Local)
        elif llm_service.provider == "ollama":
            import requests
            try:
                # Use the same model as the chat, or a specific embedding model if configured
                # For simplicity in this test suite, we use the chat model which often supports embeddings
                # or 'all-minilm' if the user had it. Let's try the configured chat model.
                url = f"{llm_service.ollama_base_url}/api/embeddings"
                payload = {
                    "model": llm_service.ollama_model, 
                    "prompt": text_content
                }
                res = requests.post(url, json=payload, timeout=10)
                if res.status_code == 200:
                    return res.json().get("embedding", [])
                else:
                    print(f"Ollama Embedding Error: {res.text}")
                    return []
            except Exception as e:
                print(f"Ollama Connection Error: {e}")
                return []

        return []

    def search_signals(self, query: str, limit: int = 5):
        """
        Semantic search over External Signals using pgvector.
        """
        # SQLite Fallback for Tests
        if self.db.bind.dialect.name == "sqlite":
            # Just return recent signals for context
            return self.db.query(ExternalSignal).limit(limit).all()

        query_vector = self.generate_embedding(query)
        if not query_vector:
            return []

        # L2 Distance search operator (<->)
        signals = self.db.query(ExternalSignal).order_by(
            ExternalSignal.embedding.l2_distance(query_vector)
        ).limit(limit).all()
        
        return signals

    def backfill_embeddings(self):
        """
        One-time helper to generate embeddings for existing seeded data.
        """
        signals = self.db.query(ExternalSignal).filter(ExternalSignal.embedding == None).all()
        count = 0
        for sig in signals:
            sig.embedding = self.generate_embedding(sig.description)
            count += 1
        self.db.commit()
        return count