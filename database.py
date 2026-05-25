import sqlite3

DB_PATH = "shortener.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        short_code   TEXT    NOT NULL UNIQUE,
        original_url TEXT    NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        click_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()


def save_url(short_code: str, original_url: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
            (short_code, original_url),
        )
        conn.commit()


def get_url(short_code: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT original_url FROM urls WHERE short_code = ?", (short_code,)
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE urls SET click_count = click_count + 1 WHERE short_code = ?",
                (short_code,),
            )
            conn.commit()
        return row["original_url"] if row else None


def code_exists(short_code: str) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM urls WHERE short_code = ?", (short_code,)
        ).fetchone()
        return row is not None
