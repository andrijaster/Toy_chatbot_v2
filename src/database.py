import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, Optional

STORY_STATUSES = {"running", "suspended", "completed"}

class ConversationDB:
    """Database handler for kids' storytelling system."""

    def __init__(self, db_file: str):
        self.db_file = db_file
        self.setup_database()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        try:
            yield conn
        finally:
            conn.close()

    # ---------- Schema ----------
    def setup_database(self):
        with self.get_connection() as conn:
            c = conn.cursor()

            # Users 
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id     TEXT PRIMARY KEY,
                    name        TEXT NOT NULL,
                    age         INTEGER NOT NULL,
                    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Stories
            c.execute("""
                CREATE TABLE IF NOT EXISTS stories (
                    story_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id     TEXT NOT NULL,
                    summary     TEXT DEFAULT '',
                    status      TEXT NOT NULL DEFAULT 'running'
                                CHECK(status IN ('running','suspended','completed')),
                    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)

            c.execute("CREATE INDEX IF NOT EXISTS idx_stories_user_id ON stories(user_id)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_stories_status ON stories(status)")
            conn.commit()

    # ---------- Users ----------
    def create_user(self, user_id: str, name: str, age: int):
        """
        Creates a new user with a given user_id.
        If the user already exists, updates their name/age.
        """
        #TODO: check if user_id is equal to session_id
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO users (user_id, name, age)
                VALUES (?, ?, ?)
            """, (user_id, name, age))
            conn.commit()
        print(f"[DB] Created new user: {user_id}")
        return user_id

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = c.fetchone()
            return {"id": row[0], "name": row[1], "age": row[2]} if row else None

    # ---------- Stories ----------
    def save_story(self, user_id: str, summary: str, status: str = "running"):
        """
        Insert a new story if none exists for this user,
        or update the existing story's summary/status.
        """
        if status not in STORY_STATUSES:
            raise ValueError(f"Invalid status: must be one of {STORY_STATUSES}")

        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO stories (user_id, summary, status, created_at, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (user_id, summary, status))
            conn.commit()

    def get_story(self, user_id: str) -> Optional[Dict]:
        """
        Return the user's current story only if it is not completed.
        (i.e., status is 'running' or 'suspended')
        """
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT * FROM stories
                WHERE user_id = ? AND status IN ('running', 'suspended')
                LIMIT 1
            """, (user_id,))
            row = c.fetchone()
            return {
                "story_id": row[0],
                "user_id": row[1],
                "summary": row[2],
                "status": row[3],
                "created_at": row[4],
                "updated_at": row[5]
            } if row else None
        
# Global database instance
db = ConversationDB("user_stories.db")
