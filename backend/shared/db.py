"""
Database connection helper for SQLite.
Thread-safe connection management following one connection per request pattern.
"""
import sqlite3
import threading
from typing import Optional
from contextlib import contextmanager


class DatabaseManager:
    """Thread-safe SQLite connection manager."""
    
    _local = threading.local()
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Get or create a connection for the current thread."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=10.0
            )
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection
    
    def close_connection(self):
        """Close the connection for the current thread."""
        if hasattr(self._local, 'connection') and self._local.connection is not None:
            self._local.connection.close()
            self._local.connection = None
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Execute a SELECT query and return results."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def init_schema(self, schema_sql: str):
        """Initialize database schema from SQL string."""
        with self.get_cursor() as cursor:
            cursor.executescript(schema_sql)
