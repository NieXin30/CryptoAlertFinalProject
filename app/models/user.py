"""User model."""
from werkzeug.security import generate_password_hash, check_password_hash
from app.services.db import get_db_connection


class User:
    """User model for authentication and profile management."""

    def __init__(self, id=None, email=None, password_hash=None, created_at=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    @staticmethod
    def create(email: str, password: str) -> 'User':
        """Create a new user with hashed password."""
        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id, created_at",
                (email, password_hash)
            )
            result = cur.fetchone()
            conn.commit()
            return User(id=result[0], email=email, password_hash=password_hash, created_at=result[1])
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def find_by_email(email: str) -> 'User':
        """Find user by email."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id, email, password_hash, created_at FROM users WHERE email = %s",
                (email,)
            )
            row = cur.fetchone()
            if row:
                return User(id=row[0], email=row[1], password_hash=row[2], created_at=row[3])
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def find_by_id(user_id: int) -> 'User':
        """Find user by ID."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id, email, password_hash, created_at FROM users WHERE id = %s",
                (user_id,)
            )
            row = cur.fetchone()
            if row:
                return User(id=row[0], email=row[1], password_hash=row[2], created_at=row[3])
            return None
        finally:
            cur.close()
            conn.close()

    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)

    def update_password(self, new_password: str) -> bool:
        """Update user password."""
        new_hash = generate_password_hash(new_password)
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (new_hash, self.id)
            )
            conn.commit()
            self.password_hash = new_hash
            return True
        finally:
            cur.close()
            conn.close()
