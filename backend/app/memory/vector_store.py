import os
import json
from typing import List, Dict, Any
from app.core.settings import settings
from app.core.logging import logger

class FallbackVectorStore:
    """A pure-Python/SQLite memory backup vector store when LanceDB is unavailable."""
    def __init__(self, storage_path: str):
        self.storage_path = os.path.join(storage_path, "fallback_vectors.json")
        self.data: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                logger.info(f"Loaded {len(self.data)} vector entries from fallback index.")
            except Exception as e:
                logger.error(f"Failed to load fallback vector file: {e}")

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f)
        except Exception as e:
            logger.error(f"Failed to save fallback vector database: {e}")

    def add_vectors(self, records: List[Dict[str, Any]]):
        """Adds a list of records with vectors: [{'id', 'project_id', 'file_id', 'content', 'vector', 'type'}]"""
        # Remove any existing entries matching the file_id to prevent duplicates
        file_ids_to_add = {r["file_id"] for r in records}
        self.data = [d for d in self.data if d.get("file_id") not in file_ids_to_add]
        
        self.data.extend(records)
        self._save()

    def delete_vectors_by_file(self, file_id: str):
        """Removes all vectors indexed for a specific file."""
        self.data = [d for d in self.data if d.get("file_id") != file_id]
        self._save()

    def similarity_search(self, query_vector: List[float], project_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Performs cosine similarity search over records matching project_id."""
        import math
        
        def cosine_similarity(v1, v2):
            dot_product = sum(a * b for a, b in zip(v1, v2))
            norm_a = math.sqrt(sum(a * a for a in v1))
            norm_b = math.sqrt(sum(b * b for b in v2))
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return dot_product / (norm_a * norm_b)

        results = []
        for record in self.data:
            if record.get("project_id") == project_id:
                sim = cosine_similarity(query_vector, record["vector"])
                results.append({
                    "id": record["id"],
                    "project_id": record["project_id"],
                    "file_id": record["file_id"],
                    "content": record["content"],
                    "type": record.get("type", "code"),
                    "score": sim
                })
                
        # Sort desc by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]


class VectorStoreManager:
    def __init__(self):
        self.db = None
        self.table = None
        self.fallback = None
        self._initialized = False

    def _lazy_init(self):
        if self._initialized:
            return
        
        try:
            import lancedb
            logger.info("Initializing LanceDB vector store...")
            self.db = lancedb.connect(settings.LANCEDB_URI)
            
            # Setup/load table
            table_name = "project_chunks"
            if table_name in self.db.table_names():
                self.table = self.db.open_table(table_name)
            else:
                # schema definitions
                self.table = self.db.create_table(table_name, data=[{
                    "id": "init-id",
                    "project_id": "init-proj",
                    "file_id": "init-file",
                    "chunk_index": 0,
                    "content": "initialization chunk",
                    "vector": [0.0] * 384,
                    "type": "code"
                }])
            logger.info("LanceDB vector store initialized successfully.")
        except ImportError:
            logger.warning("LanceDB not installed. Booting fallback vector store.")
            self.fallback = FallbackVectorStore(settings.LANCEDB_URI)
        except Exception as e:
            logger.error(f"Error starting LanceDB: {e}. Booting fallback vector store.")
            self.fallback = FallbackVectorStore(settings.LANCEDB_URI)
            
        self._initialized = True

    def add_chunks(self, records: List[Dict[str, Any]]):
        """Indexes vector chunks. Each record format: {'id', 'project_id', 'file_id', 'chunk_index', 'content', 'vector', 'type'}"""
        self._lazy_init()
        
        if self.fallback:
            self.fallback.add_vectors(records)
            return

        try:
            # Delete old mappings for this file first
            file_ids = list({r["file_id"] for r in records})
            for file_id in file_ids:
                self.table.delete(f"file_id = '{file_id}'")
            
            # Insert new chunks
            self.table.add(records)
        except Exception as e:
            logger.error(f"Failed to add records to LanceDB: {e}")

    def delete_chunks_by_file(self, file_id: str):
        """Deletes vector database records associated with a file."""
        self._lazy_init()
        
        if self.fallback:
            self.fallback.delete_vectors_by_file(file_id)
            return
            
        try:
            self.table.delete(f"file_id = '{file_id}'")
        except Exception as e:
            logger.error(f"Failed to delete records from LanceDB: {e}")

    def search(self, query_vector: List[float], project_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Queries vector database for top matching semantic records."""
        self._lazy_init()
        
        if self.fallback:
            return self.fallback.similarity_search(query_vector, project_id, limit)

        try:
            # Perform nearest neighbor search filtered by project
            query = self.table.search(query_vector).where(f"project_id = '{project_id}'").limit(limit)
            df = query.to_pandas()
            
            results = []
            for _, row in df.iterrows():
                if row["id"] == "init-id":
                    continue
                results.append({
                    "id": row["id"],
                    "project_id": row["project_id"],
                    "file_id": row["file_id"],
                    "content": row["content"],
                    "type": row["type"],
                    "score": 1.0 - float(row.get("_distance", 1.0)) # Convert Euclidean distance to similarity
                })
            return results
        except Exception as e:
            logger.error(f"LanceDB search failed: {e}")
            return []

vector_store = VectorStoreManager()
