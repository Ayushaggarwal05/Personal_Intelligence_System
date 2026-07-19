from app.database.session import get_db

# Expose common database dependency injections
__all__ = ["get_db"]
