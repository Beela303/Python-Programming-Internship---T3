"""A small raw sqlite3 example showing parameterized SQL and transaction scope."""
import sqlite3
from pathlib import Path


def main() -> None:
    database_path = Path("raw_demo.db")
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                body TEXT NOT NULL CHECK(length(body) > 0)
            )
        """)
        # Parameterized SQL: never build SQL by concatenating user input.
        connection.execute(
            "INSERT INTO notes(body) VALUES (?)",
            ("Raw SQLite gives direct control over SQL.",),
        )
        rows = connection.execute(
            "SELECT id, body FROM notes ORDER BY id"
        ).fetchall()
        for row in rows:
            print(row)


if __name__ == "__main__":
    main()
