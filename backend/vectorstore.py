import logging
import chromadb
from backend.config import CHROMA_PATH
from backend.embeddings import EmbeddingService

logger = logging.getLogger(__name__)

class VectorStore:
    _client = None
    _collection = None

    @classmethod
    def get_collection(cls):
        if cls._collection is None:
            logger.info(f"Connecting to ChromaDB at {CHROMA_PATH}")
            cls._client = chromadb.PersistentClient(path=CHROMA_PATH)
            try:
                cls._collection = cls._client.get_collection("lecture_vectors")
                logger.info(f"Collection loaded. Count: {cls._collection.count()}")
            except Exception as e:
                logger.warning(f"Collection 'lecture_vectors' not found or error: {e}")
                cls._collection = None
        return cls._collection

    @classmethod
    def retrieve(cls, question: str, top_k: int = 5):
        collection = cls.get_collection()
        if collection is None:
            return "", []
            
        try:
            query_embedding = EmbeddingService.encode(question)
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=top_k
            )
            
            if not results['documents'] or not results['documents'][0]:
                return "", []
                
            context = "\n\n---\n\n".join(results['documents'][0])
            sources = [m['lecture'] for m in results['metadatas'][0]]
            
            return context, sources
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return "", []
