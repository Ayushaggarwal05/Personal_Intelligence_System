import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.tools.parsers.python_parser import parse_python_file
from app.tools.parsers.javascript_parser import parse_javascript_file
from app.services.embedding_service import embedding_service
from app.memory.vector_store import vector_store

def run_test():
    print("=== Testing Parsers & Vector Store ===")
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="peis_parser_test_")
    
    mock_py = os.path.join(temp_dir, "sample.py")
    mock_js = os.path.join(temp_dir, "server.js")
    
    # 1. Write mock Python code with classes, routes, functions
    with open(mock_py, "w", encoding="utf-8") as f:
        f.write('''
class UserProfile(BaseModel):
    """Represents a user profile."""
    username: str
    email: str

@app.get("/api/v1/users/{user_id}")
async def get_user_profile(user_id: int):
    """Retrieve user details from the database."""
    return {"id": user_id, "username": "ayush"}

def compute_total(price, tax=0.18):
    return price + (price * tax)
''')

    # 2. Write mock JS code with Express route and class
    with open(mock_js, "w", encoding="utf-8") as f:
        f.write('''
class OrderController {
    constructor() {}
}

router.post('/api/orders/checkout', (req, res) => {
    res.json({ success: true });
});
''')

    try:
        # 3. Test Python Parser
        print("\nTesting Python Parser...")
        py_symbols = parse_python_file(mock_py)
        print(f"Found {len(py_symbols)} Python symbols:")
        for s in py_symbols:
            print(f" - [{s['type'].upper()}] Name: {s['name']}, Sig: {s['signature']}, StartLine: {s['line_start']}")
        
        assert len(py_symbols) == 3, f"Expected 3 symbols, got {len(py_symbols)}"
        types = {s["type"] for s in py_symbols}
        assert "model" in types, "Class inheriting from BaseModel not identified as 'model'!"
        assert "route" in types, "FastAPI route not identified as 'route'!"
        assert "function" in types, "Standard function not identified as 'function'!"
        print("Python Parser verification PASSED.")

        # 4. Test JS Parser
        print("\nTesting JS/TS Parser...")
        js_symbols = parse_javascript_file(mock_js)
        print(f"Found {len(js_symbols)} JS/TS symbols:")
        for s in js_symbols:
            print(f" - [{s['type'].upper()}] Name: {s['name']}, Sig: {s['signature']}, StartLine: {s['line_start']}")
            
        assert len(js_symbols) == 2, f"Expected 2 JS symbols, got {len(js_symbols)}"
        js_types = {s["type"] for s in js_symbols}
        assert "class" in js_types, "Class OrdController not identified!"
        assert "route" in js_types, "Express POST route not identified!"
        print("JS/TS Parser verification PASSED.")

        # 5. Test Embeddings and Vector Store
        print("\nTesting Embeddings & Vector Store...")
        chunk1 = "Database model representing order transactions and credit balances."
        chunk2 = "FastAPI router endpoint executing order checkouts."
        
        print("Generating embeddings...")
        vec1 = embedding_service.get_embedding(chunk1)
        vec2 = embedding_service.get_embedding(chunk2)
        
        assert len(vec1) == 384, f"Expected embedding dimensions 384, got {len(vec1)}"
        print("Embeddings generation verification PASSED.")

        # Add chunks to vector store
        print("Adding chunks to Vector Store...")
        records = [
            {
                "id": "chk-1",
                "project_id": "proj-xyz",
                "file_id": "file-111",
                "chunk_index": 0,
                "content": chunk1,
                "vector": vec1,
                "type": "docs"
            },
            {
                "id": "chk-2",
                "project_id": "proj-xyz",
                "file_id": "file-222",
                "chunk_index": 0,
                "content": chunk2,
                "vector": vec2,
                "type": "code"
            }
        ]
        vector_store.add_chunks(records)
        
        # Test Query
        print("Querying Vector Store semantically...")
        # Search for query related to "FastAPI order processing"
        query_vec = embedding_service.get_embedding("FastAPI route checkouts")
        search_res = vector_store.search(query_vector=query_vec, project_id="proj-xyz", limit=2)
        
        print(f"Search results (limit 2):")
        for idx, res in enumerate(search_res, 1):
            print(f" {idx}. [{res['type'].upper()}] Score: {res['score']:.4f} | Content: {res['content']}")
            
        assert len(search_res) >= 1, "Expected search results, got 0!"
        # Since chunk2 is about FastAPI routes, it should have a higher score than chunk1
        assert search_res[0]["id"] == "chk-2", "Semantic vector match failed: expected routes chunk first!"
        print("Vector Store search verification PASSED.")
        print("\n=== ALL PARSER & VECTOR TESTS PASSED ===")

    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
    finally:
        shutil.rmtree(temp_dir)
        print(f"\nCleaned up temp files.")

if __name__ == "__main__":
    run_test()
