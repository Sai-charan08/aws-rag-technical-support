import os
import json
import sqlite3
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import pymysql
from pymysql.cursors import DictCursor

from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class DatabaseManager:
    """Enterprise-ready Database Manager for MySQL with resilient fallback.
    
    Stores user authentication credentials, audit logs, and conversation history
    for the Domain-Specific RAG Technical Support Assistant.
    """

    def __init__(
        self,
        host: str = settings.MYSQL_HOST,
        port: int = settings.MYSQL_PORT,
        user: str = settings.MYSQL_USER,
        password: str = settings.MYSQL_PASSWORD,
        database: str = settings.MYSQL_DATABASE,
        fallback_sqlite: bool = settings.DB_FALLBACK_SQLITE,
        sqlite_path: str = settings.SQLITE_FALLBACK_PATH
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.fallback_sqlite = fallback_sqlite
        self.sqlite_path = sqlite_path

        self.is_mysql = False
        self._init_connection()

    def _init_connection(self):
        """Attempts connection to MySQL; falls back to SQLite if unreachable."""
        try:
            logger.info(f"Attempting to connect to MySQL database at {self.host}:{self.port}...")
            # First connect without database to ensure database exists
            conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                charset="utf8mb4",
                cursorclass=DictCursor,
                connect_timeout=3
            )
            with conn.cursor() as cur:
                cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{self.database}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                )
            conn.commit()
            conn.close()

            # Now verify connection to the target database
            test_conn = self._get_mysql_connection()
            test_conn.close()
            self.is_mysql = True
            logger.info(f"Successfully connected to MySQL database '{self.database}' at {self.host}:{self.port}!")
        except Exception as e:
            self.is_mysql = False
            logger.warning(
                f"MySQL connection to {self.host}:{self.port} was not established: {e}. "
                f"Fallback SQLite mode: {self.fallback_sqlite}"
            )
            if self.fallback_sqlite:
                Path(self.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"Using local SQLite database fallback at '{self.sqlite_path}'.")

        self.init_database()

    def _get_mysql_connection(self):
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset="utf8mb4",
            cursorclass=DictCursor,
            connect_timeout=5,
            autocommit=True
        )

    def _get_sqlite_connection(self):
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Creates the required tables in MySQL or SQLite fallback."""
        if self.is_mysql:
            self._init_mysql_tables()
        else:
            self._init_sqlite_tables()

    def _init_mysql_tables(self):
        try:
            conn = self._get_mysql_connection()
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL DEFAULT NULL,
                    INDEX idx_username (username),
                    INDEX idx_email (email)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)

                cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id VARCHAR(64) PRIMARY KEY,
                    user_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL DEFAULT 'AWS Support Session',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_session_user (user_id),
                    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)

                cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(64) NULL,
                    user_id INT NOT NULL,
                    query TEXT NOT NULL,
                    response MEDIUMTEXT NOT NULL,
                    intent VARCHAR(50) DEFAULT 'GENERAL',
                    service VARCHAR(50) DEFAULT 'General AWS',
                    urgency VARCHAR(20) DEFAULT 'LOW',
                    is_grounded TINYINT(1) DEFAULT 1,
                    latency_ms FLOAT DEFAULT 0.0,
                    sources_json TEXT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_history_user (user_id, created_at),
                    INDEX idx_history_service (service),
                    INDEX idx_history_intent (intent),
                    CONSTRAINT fk_history_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)

                cur.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NULL,
                    event_type VARCHAR(50) NOT NULL,
                    ip_address VARCHAR(50) NULL DEFAULT '127.0.0.1',
                    details TEXT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_audit_user (user_id),
                    INDEX idx_audit_time (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)
            conn.close()
            logger.info("MySQL tables initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize MySQL tables: {e}")

    def _init_sqlite_tables(self):
        try:
            conn = self._get_sqlite_connection()
            cur = conn.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL DEFAULT 'AWS Support Session',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NULL,
                user_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                intent TEXT DEFAULT 'GENERAL',
                service TEXT DEFAULT 'General AWS',
                urgency TEXT DEFAULT 'LOW',
                is_grounded INTEGER DEFAULT 1,
                latency_ms REAL DEFAULT 0.0,
                sources_json TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NULL,
                event_type TEXT NOT NULL,
                ip_address TEXT DEFAULT '127.0.0.1',
                details TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.commit()
            conn.close()
            logger.info("SQLite fallback tables initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite tables: {e}")

    # ================= User Operations =================

    def create_user(
        self, username: str, email: str, password_hash: str, role: str = "user"
    ) -> Optional[Dict[str, Any]]:
        """Inserts a new user into the database."""
        username = username.strip().lower()
        email = email.strip().lower()

        if self.is_mysql:
            try:
                conn = self._get_mysql_connection()
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                        (username, email, password_hash, role)
                    )
                    user_id = cur.lastrowid
                conn.close()
                return self.get_user_by_id(user_id)
            except Exception as e:
                logger.error(f"Error creating user in MySQL: {e}")
                return None
        else:
            try:
                conn = self._get_sqlite_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                    (username, email, password_hash, role)
                )
                user_id = cur.lastrowid
                conn.commit()
                conn.close()
                return self.get_user_by_id(user_id)
            except Exception as e:
                logger.error(f"Error creating user in SQLite: {e}")
                return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        username = username.strip().lower()
        if self.is_mysql:
            try:
                conn = self._get_mysql_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE username = %s LIMIT 1", (username,))
                    res = cur.fetchone()
                conn.close()
                return res
            except Exception as e:
                logger.error(f"Error querying user by username in MySQL: {e}")
                return None
        else:
            try:
                conn = self._get_sqlite_connection()
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE username = ? LIMIT 1", (username,))
                row = cur.fetchone()
                conn.close()
                return dict(row) if row else None
            except Exception as e:
                logger.error(f"Error querying user by username in SQLite: {e}")
                return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        email = email.strip().lower()
        if self.is_mysql:
            try:
                conn = self._get_mysql_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE email = %s LIMIT 1", (email,))
                    res = cur.fetchone()
                conn.close()
                return res
            except Exception as e:
                logger.error(f"Error querying user by email in MySQL: {e}")
                return None
        else:
            try:
                conn = self._get_sqlite_connection()
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE email = ? LIMIT 1", (email,))
                row = cur.fetchone()
                conn.close()
                return dict(row) if row else None
            except Exception as e:
                logger.error(f"Error querying user by email in SQLite: {e}")
                return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        if self.is_mysql:
            try:
                conn = self._get_mysql_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE id = %s LIMIT 1", (user_id,))
                    res = cur.fetchone()
                conn.close()
                return res
            except Exception as e:
                logger.error(f"Error querying user by id in MySQL: {e}")
                return None
        else:
            try:
                conn = self._get_sqlite_connection()
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE id = ? LIMIT 1", (user_id,))
                row = cur.fetchone()
                conn.close()
                return dict(row) if row else None
            except Exception as e:
                logger.error(f"Error querying user by id in SQLite: {e}")
                return None

    def update_last_login(self, user_id: int):
        if self.is_mysql:
            try:
                conn = self._get_mysql_connection()
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                        (user_id,)
                    )
                conn.close()
            except Exception as e:
                logger.error(f"Error updating last login in MySQL: {e}")
        else:
            try:
                conn = self._get_sqlite_connection()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                    (user_id,)
                )
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Error updating last login in SQLite: {e}")

    # ================= Chat History & Log Operations =================

    def add_chat_entry(
        self,
        user_id: int,
        query: str,
        response: str,
        intent: str = "GENERAL",
        service: str = "General AWS",
        urgency: str = "LOW",
        is_grounded: bool = True,
        latency_ms: float = 0.0,
        sources: Optional[List[Dict[str, Any]]] = None,
        session_id: Optional[str] = None
    ) -> Optional[int]:
        sources_json = json.dumps(sources or [])
        grounded_int = 1 if is_grounded else 0

        if self.is_mysql:
            try:
                conn = self._get_mysql_connection()
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO chat_history 
                        (session_id, user_id, query, response, intent, service, urgency, is_grounded, latency_ms, sources_json)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (session_id, user_id, query, response, intent, service, urgency, grounded_int, latency_ms, sources_json)
                    )
                    entry_id = cur.lastrowid
                conn.close()
                return entry_id
            except Exception as e:
                logger.error(f"Error adding chat history in MySQL: {e}")
                return None
        else:
            try:
                conn = self._get_sqlite_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO chat_history 
                    (session_id, user_id, query, response, intent, service, urgency, is_grounded, latency_ms, sources_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (session_id, user_id, query, response, intent, service, urgency, grounded_int, latency_ms, sources_json)
                )
                entry_id = cur.lastrowid
                conn.commit()
                conn.close()
                return entry_id
            except Exception as e:
                logger.error(f"Error adding chat history in SQLite: {e}")
                return None

    def get_chat_history(
        self, user_id: int, session_id: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieves conversational history for a user."""
        records = []
        if self.is_mysql:
            try:
                conn = self._get_mysql_connection()
                with conn.cursor() as cur:
                    if session_id:
                        cur.execute(
                            "SELECT * FROM chat_history WHERE user_id = %s AND session_id = %s ORDER BY created_at ASC LIMIT %s",
                            (user_id, session_id, limit)
                        )
                    else:
                        cur.execute(
                            "SELECT * FROM chat_history WHERE user_id = %s ORDER BY created_at ASC LIMIT %s",
                            (user_id, limit)
                        )
                    records = cur.fetchall()
                conn.close()
            except Exception as e:
                logger.error(f"Error fetching chat history from MySQL: {e}")
        else:
            try:
                conn = self._get_sqlite_connection()
                cur = conn.cursor()
                if session_id:
                    cur.execute(
                        "SELECT * FROM chat_history WHERE user_id = ? AND session_id = ? ORDER BY created_at ASC LIMIT ?",
                        (user_id, session_id, limit)
                    )
                else:
                    cur.execute(
                        "SELECT * FROM chat_history WHERE user_id = ? ORDER BY created_at ASC LIMIT ?",
                        (user_id, limit)
                    )
                rows = cur.fetchall()
                records = [dict(r) for r in rows]
                conn.close()
            except Exception as e:
                logger.error(f"Error fetching chat history from SQLite: {e}")

        # Parse sources_json
        for rec in records:
            if rec.get("sources_json"):
                try:
                    rec["sources"] = json.loads(rec["sources_json"])
                except Exception:
                    rec["sources"] = []
            else:
                rec["sources"] = []
        return records

    def clear_chat_history(self, user_id: int):
        if self.is_mysql:
            try:
                conn = self._get_mysql_connection()
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM chat_history WHERE user_id = %s", (user_id,))
                conn.close()
            except Exception as e:
                logger.error(f"Error clearing chat history in MySQL: {e}")
        else:
            try:
                conn = self._get_sqlite_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Error clearing chat history in SQLite: {e}")

    # ================= Audit Log Operations =================

    def log_audit_event(
        self, user_id: Optional[int], event_type: str, details: Optional[str] = None, ip_address: Optional[str] = "127.0.0.1"
    ):
        if self.is_mysql:
            try:
                conn = self._get_mysql_connection()
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO audit_logs (user_id, event_type, ip_address, details) VALUES (%s, %s, %s, %s)",
                        (user_id, event_type, ip_address or "127.0.0.1", details)
                    )
                conn.close()
            except Exception as e:
                logger.error(f"Error writing audit log to MySQL: {e}")
        else:
            try:
                conn = self._get_sqlite_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO audit_logs (user_id, event_type, ip_address, details) VALUES (?, ?, ?, ?)",
                    (user_id, event_type, ip_address or "127.0.0.1", details)
                )
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Error writing audit log to SQLite: {e}")

    def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        if self.is_mysql:
            try:
                conn = self._get_mysql_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT %s", (limit,))
                    logs = cur.fetchall()
                conn.close()
                return logs
            except Exception as e:
                logger.error(f"Error retrieving audit logs from MySQL: {e}")
                return []
        else:
            try:
                conn = self._get_sqlite_connection()
                cur = conn.cursor()
                cur.execute("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?", (limit,))
                rows = cur.fetchall()
                conn.close()
                return [dict(r) for r in rows]
            except Exception as e:
                logger.error(f"Error retrieving audit logs from SQLite: {e}")
                return []

    def get_stats(self) -> Dict[str, Any]:
        """Returns database operational statistics."""
        stats = {
            "is_mysql": self.is_mysql,
            "engine": "MySQL 8.0" if self.is_mysql else "SQLite (Fallback)",
            "host": f"{self.host}:{self.port}" if self.is_mysql else "Local File",
            "database": self.database if self.is_mysql else str(self.sqlite_path),
            "total_users": 0,
            "total_queries": 0
        }
        try:
            if self.is_mysql:
                conn = self._get_mysql_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) AS total FROM users")
                    stats["total_users"] = cur.fetchone()["total"]
                    cur.execute("SELECT COUNT(*) AS total FROM chat_history")
                    stats["total_queries"] = cur.fetchone()["total"]
                conn.close()
            else:
                conn = self._get_sqlite_connection()
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM users")
                stats["total_users"] = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM chat_history")
                stats["total_queries"] = cur.fetchone()[0]
                conn.close()
        except Exception as e:
            logger.error(f"Error gathering DB stats: {e}")
        return stats

_global_db_manager = None

def get_db_manager() -> DatabaseManager:
    global _global_db_manager
    if _global_db_manager is None:
        _global_db_manager = DatabaseManager()
    return _global_db_manager

