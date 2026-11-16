
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

from app.core.security import hash_password, verify_password


class AuthService:

    def __init__(self, db_path="data/users.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_table()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL
                        CHECK(role IN ('admin', 'user')),
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                )
            """)

    def create_user(self, username, password, role="user"):
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Valid username is required.")

        username = username.strip()

        if len(username) > 50:
            raise ValueError("Username must not exceed 50 characters.")

        if role not in {"admin", "user"}:
            raise ValueError("Invalid user role.")

        hashed = hash_password(password)
        created_at = datetime.now(timezone.utc).isoformat()

        try:
            with self._connect() as conn:
                conn.execute("""
                    INSERT INTO users
                    (username, password_hash, role, created_at)
                    VALUES (?, ?, ?, ?)
                """, (username, hashed, role, created_at))

        except sqlite3.IntegrityError:
            raise ValueError("Username already exists.")

        return {
            "username": username,
            "role": role,
            "status": "created"
        }

    def authenticate_user(self, username, password):
        if not isinstance(username, str) or not isinstance(password, str):
            return None

        with self._connect() as conn:
            row = conn.execute("""
                SELECT username, password_hash, role, is_active
                FROM users
                WHERE username = ?
            """, (username.strip(),)).fetchone()

        if row is None:
            return None

        stored_username, stored_hash, role, is_active = row

        if not is_active:
            return None

        try:
            valid = verify_password(password, stored_hash)
        except (ValueError, TypeError):
            return None

        if not valid:
            return None

        return {
            "username": stored_username,
            "role": role
        }

    def get_user(self, username):
        with self._connect() as conn:
            row = conn.execute("""
                SELECT username, role, is_active, created_at
                FROM users
                WHERE username = ?
            """, (username,)).fetchone()

        if row is None:
            return None

        return {
            "username": row[0],
            "role": row[1],
            "is_active": bool(row[2]),
            "created_at": row[3]
        }

    def change_admin_password(self, username, current_password, new_password):
        if not all(
            isinstance(value, str)
            for value in (username, current_password, new_password)
        ):
            raise ValueError("Invalid password change request.")

        username = username.strip()

        if not username:
            raise ValueError("Invalid username.")

        if len(new_password) < 12 or len(new_password) > 128:
            raise ValueError(
                "New password must be between 12 and 128 characters."
            )

        if current_password == new_password:
            raise ValueError(
                "New password must differ from the current password."
            )

        with self._connect() as conn:
            row = conn.execute("""
                SELECT password_hash, role, is_active
                FROM users
                WHERE username = ?
            """, (username,)).fetchone()

            if row is None:
                raise ValueError("Invalid current password.")

            stored_hash, role, is_active = row

            if role != "admin" or not is_active:
                raise ValueError("Admin account is unavailable.")

            try:
                valid = verify_password(current_password, stored_hash)
            except (ValueError, TypeError):
                valid = False

            if not valid:
                raise ValueError("Invalid current password.")

            new_hash = hash_password(new_password)

            conn.execute("""
                UPDATE users
                SET password_hash = ?
                WHERE username = ?
            """, (new_hash, username))

        return {
            "status": "success",
            "message": "Admin password changed."
        }
