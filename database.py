import sqlite3

DB_PATH = "payments.db"


def initialize_database():
    """Create and populate the payments table if it doesn't exist."""

    db = sqlite3.connect(DB_PATH)

    db.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            student_id TEXT,
            student_name TEXT,
            amount REAL,
            note TEXT
        )
    """)

    # Add demo data only if the table is empty
    count = db.execute("SELECT COUNT(*) FROM payments").fetchone()[0]

    if count == 0:
        db.executemany(
            "INSERT INTO payments VALUES (?, ?, ?, ?)",
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


def get_connection():
    """Return a connection to the Helpora database."""
    return sqlite3.connect(DB_PATH)
