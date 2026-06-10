import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            logger.info("Loading embedding model (all-MiniLM-L6-v2)...")
            cls._instance = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded.")
        return cls._instance

    @classmethod
    def encode(cls, text: str):
        model = cls.get_instance()
        return model.encode([text]).tolist()
