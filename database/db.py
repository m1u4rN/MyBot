import os
import sqlite3
import random
from typing import Optional, Dict, Any

DB_PATH = os.path.join("data", "bot.db")


def _connect() -> sqlite3.Connection:
    """Открывает соединение, создаёт папку data/ при первом запуске."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Создаёт таблицу/триггеры и добавляет недостающие столбцы (миграция)."""
    with _connect() as conn:
        # Базовая схема с новыми полями
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,                  -- Telegram ID пользователя
                phone TEXT UNIQUE,                       -- телефон
                name TEXT,                               -- имя
                email TEXT,                              -- email
                gender TEXT,                             -- 'male'/'female'/'other'
                birth_date TEXT,                         -- 'YYYY-MM-DD'
                card_id TEXT UNIQUE,                     -- уникальная карта клиента (6 символов)
                bonus_balance REAL NOT NULL DEFAULT 0.0, -- баланс
                bonus_transactions TEXT NOT NULL DEFAULT '[]',  -- JSON-список движений
                bonus_expirations  TEXT NOT NULL DEFAULT '[]',  -- JSON-список экспираций
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


def generate_unique_card_id() -> str:
    """Генерирует уникальный card_id (проверяет отсутствия коллизии в БД)."""
    with _connect() as conn:
        while True:
            cand = random.randint(0, 999_999)
            row = conn.execute("SELECT 1 FROM clients WHERE card_id = ?", (cand,)).fetchone()
            if not row:
                return cand


def get_client_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM clients WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def get_client_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM clients WHERE phone = ?", (phone,)).fetchone()
        return dict(row) if row else None


def get_client_by_email(email: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM clients WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None


def get_client_by_card_id(card_id: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM clients WHERE card_id = ?", (card_id,)).fetchone()
        return dict(row) if row else None


def create_client(
    user_id: int,
    phone: str,
    name: str = None,
    email: str = None,
    gender: str = None,
    birth_date_iso: str = None,
    bonus_balance: float = 100.0,
    card_id: str = generate_unique_card_id(),
) -> int:
    """
    Создаёт клиента.
    """

    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO clients (user_id, phone, name, email, gender, birth_date, card_id, bonus_balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, phone, name, email, gender, birth_date_iso, card_id, bonus_balance),
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
