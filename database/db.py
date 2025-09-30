import os
import sqlite3
from typing import Optional, Dict, Any, Tuple

DB_PATH = os.path.join("data", "bot.db")


def _connect() -> sqlite3.Connection:
    """Открывает соединение, создаёт папку data/ при первом запуске."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Создаёт таблицы, триггеры и добавляет недостающие столбцы."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,                  -- Telegram ID пользователя
                phone TEXT UNIQUE,                       -- телефон
                name TEXT,                               -- имя для удобства
                email TEXT,                              -- email (уникальность можно включить ниже)
                gender TEXT,                             -- 'male'/'female'/'other' (или свой набор)
                birth_date TEXT,                         -- 'YYYY-MM-DD' (ISO)
                bonus_balance REAL NOT NULL DEFAULT 0.0, -- баланс в баллах
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trg_clients_updated_at
            AFTER UPDATE ON clients
            BEGIN
                UPDATE clients SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """
        )

def get_client_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM clients WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def get_client_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM clients WHERE phone = ?", (phone,)
        ).fetchone()
        return dict(row) if row else None


def get_client_by_email(email: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM clients WHERE email = ?", (email,)
        ).fetchone()
        return dict(row) if row else None


def create_client(
    user_id: int,
    phone: str,
    name: str = None,
    email: str = None,
    gender: str = None,
    birth_date_iso: str = None,
    bonus_balance: float = 100.0,
) -> int:
    """Создаёт клиента. Доп.поля можно не передавать (по умолчанию NULL)."""
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO clients (user_id, phone, name, bonus_balance, email, gender, birth_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, phone, name, bonus_balance, email, gender, birth_date_iso),
        )
        return cur.lastrowid


def update_client_user_id_for_phone(phone: str, user_id: int) -> None:
    with _connect() as conn:
        conn.execute("UPDATE clients SET user_id = ? WHERE phone = ?", (user_id, phone))


def set_balance_by_user_id(user_id: int, amount: float) -> None:
    with _connect() as conn:
        conn.execute("UPDATE clients SET bonus_balance = ? WHERE user_id = ?", (amount, user_id))


def update_profile(
    user_id: int,
    *,
    email: Optional[str],
    gender: Optional[str],
    birth_date_iso: Optional[str],  # 'YYYY-MM-DD'
) -> None:
    """Обновляет email, пол и дату рождения по user_id."""
    with _connect() as conn:
        conn.execute(
            """
            UPDATE clients
               SET email = ?,
                   gender = ?,
                   birth_date = ?
             WHERE user_id = ?
            """,
            (email, gender, birth_date_iso, user_id),
        )


def format_amount(amount: float) -> str:
    """Два знака после запятой и запятая как в примере: 100,00"""
    return f"{amount:.2f}".replace(".", ",")
