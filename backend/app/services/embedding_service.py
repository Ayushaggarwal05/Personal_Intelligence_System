import numpy as np
from typing import List
from app.core.settings import settings
from app.core.logging import logger

class EmbeddingService:
    def __init__(self):
        self.model = None
        self.model_name = settings.EMBEDDINGS_MODEL_NAME
        self._initialized = False

    def _lazy_init(self):
        if self._initialized:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local embedding model: {self.model_name}...")
            # Load model onto CPU explicitly to prevent VRAM memory strain
            self.model = SentenceTransformer(self.model_name, device="cpu")
            logger.info("Local embedding model loaded successfully.")
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Vector database searches will fall back to mock matching or cloud providers."
            )
        except Exception as e:
            logger.error(f"Error initializing sentence-transformers model: {e}")
            
        self._initialized = True

    def get_embedding(self, text: str) -> List[float]:
        """Generates a dense vector embedding for a given text query/chunk."""
        self._lazy_init()
        
        if self.model:
            try:
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            except Exception as e:
                logger.error(f"Error encoding embedding: {e}")
        
        # Fallback Mock: generate reproducible vector based on hash for indexing testing
        import hashlib
        h = hashlib.md5(text.encode("utf-8")).hexdigest()
        np.random.seed(int(h[:8], 16) % (2**32))
        mock_vec = np.random.uniform(-1.0, 1.0, 384).tolist()
        return mock_vec

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates dense vector embeddings for a list of text chunks."""
        self._lazy_init()
        
        if self.model:
            try:
                embeddings = self.model.encode(texts, convert_to_numpy=True)
                return embeddings.tolist()
            except Exception as e:
                logger.error(f"Error encoding multiple embeddings: {e}")
                
        return [self.get_embedding(t) for t in texts]

embedding_service = EmbeddingService()
