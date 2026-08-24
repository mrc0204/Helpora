# database.py

import sqlite3

DB_PATH = "payments.db"


def get_connection():
    """Create a connection to the Helpora SQLite database."""
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """
    Initialize the payments table and add demo records
    only when the database is empty.
    """

    db = get_connection()

    db.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            student_id TEXT,
            student_name TEXT,
            amount REAL,
            note TEXT
        )
    """)

    count = db.execute(
        "SELECT COUNT(*) FROM payments"
    ).fetchone()[0]

    # Add demo records only on first initialization
    if count == 0:

        db.executemany(
            """
            INSERT INTO payments
            (student_id, student_name, amount, note)
            VALUES (?, ?, ?, ?)
            """,
            [
                ("S-7-042", "Aditya", 15000, "Course fee"),
                ("S-7-042", "Aditya", 15000, "Course fee"),
                ("S-7-118", "Meera", 15000, "Course fee"),
                ("S-7-091", "Rohan", 2500, "Lab materials"),
                ("S-7-043", "Aliya", 15000, "Course fee"),
                ("S-7-043", "Aliya", 15000, "Course fee"),
            ],
        )

    db.commit()
    db.close()
