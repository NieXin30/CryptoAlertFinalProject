"""Database connection and initialization."""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """Get a database connection."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    return psycopg2.connect(database_url)


def init_db():
    """Initialize database tables."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create alert_rules table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS alert_rules (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                currency_symbol VARCHAR(10) NOT NULL,
                condition CHAR(1) NOT NULL,
                threshold_price NUMERIC(20, 8) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create price_history table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id SERIAL PRIMARY KEY,
                currency_symbol VARCHAR(10) NOT NULL,
                price_usd NUMERIC(20, 8) NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL
            )
        """)
        
        # Create index for faster price lookups
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_history_symbol_timestamp 
            ON price_history (currency_symbol, timestamp DESC)
        """)
        
        conn.commit()
        print("Database tables initialized successfully.")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error initializing database: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    init_db()

