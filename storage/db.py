"""Optional SQLite database for metadata storage."""

import sqlite3
from typing import Optional


class MetadataDB:
    """SQLite database for storing feature and graph metadata."""

    def __init__(self, db_path: str = "storage/metadata.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema."""
        # TODO: Load schema from sql_schema.sql
        pass

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
