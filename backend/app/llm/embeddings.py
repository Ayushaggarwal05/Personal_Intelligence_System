from app.services.embedding_service import embedding_service

# Expose embedding service wrapper functions
def get_embedding_vector(text: str) -> list[float]:
    return embedding_service.get_embedding(text)
