"""Database initialization script."""
from app.services.db import init_db

if __name__ == '__main__':
    print("Initializing database tables...")
    init_db()
    print("Done!")

