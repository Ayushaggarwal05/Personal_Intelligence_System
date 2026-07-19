import os
import uuid
from typing import List, Dict, Any

def split_text_overlapping(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Splits a string content into overlapping text segments using character windows."""
    chunks = []
    text_len = len(text)
    
    if text_len <= chunk_size:
        return [text]

    start = 0
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Advance by size minus overlap
        start += (chunk_size - overlap)
        
    return chunks

from app.tools.filesystem.read_file import is_binary_file

def chunk_file_for_indexing(file_path: str, project_id: str, file_id: str) -> List[Dict[str, Any]]:
    """Reads a file, chunk splits its text, and packages it in LanceDB document schema structures."""
    if not os.path.exists(file_path) or is_binary_file(file_path):
        return []

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # 1. Determine file category type
    doc_extensions = {".md", ".txt", ".pdf"}
    file_type = "docs" if ext in doc_extensions else "code"
    
    try:
        # Extract text content depending on file type
        if ext == ".pdf":
            from app.tools.parsers.pdf_parser import parse_pdf_file
            pdf_data = parse_pdf_file(file_path)
            # Combine page texts
            content = "\n\n".join([page["text"] for page in pdf_data.get("pages", [])])
        elif ext == ".md":
            from app.tools.parsers.markdown_parser import parse_markdown_file
            md_data = parse_markdown_file(file_path)
            # Combine section headers & contents
            content = "\n\n".join([f"## {s['heading']}\n{s['content']}" for s in md_data.get("sections", [])])
            if not content: # Fallback to standard read if parsing empty
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
    except Exception:
        return []

    if not content.strip():
        return []

    # 2. Split content into overlapping chunks
    text_chunks = split_text_overlapping(content, chunk_size=800, overlap=100)
    
    records = []
    for idx, chunk in enumerate(text_chunks):
        records.append({
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "file_id": file_id,
            "chunk_index": idx,
            "content": chunk.strip(),
            "vector": [0.0] * 384, # Placeholder dimensions matching all-MiniLM-L6-v2 vector store expectation
            "type": file_type
        })
        
    return records
