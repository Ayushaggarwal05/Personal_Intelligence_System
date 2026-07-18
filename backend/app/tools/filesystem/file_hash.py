import hashlib

def calculate_file_hash(file_path: str) -> str:
    """Calculates the SHA-256 hash of a file in chunks to optimize memory."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        raise IOError(f"Error reading file '{file_path}' for hash calculation: {e}")
