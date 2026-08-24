import sqlite3
from langchain_core.tools import tool

from database import get_connection


# -----------------------------
# Task Board
# -----------------------------

TASK_BOARD = []


@tool
def lookup_payments(student_id: str) -> str:
    """Look up all payments for a student ID."""

    db = get_connection()

    rows = db.execute(
        """
        SELECT student_name, amount, note
        FROM payments
        WHERE student_id = ?
        """,
        (student_id,),
    ).fetchall()

    db.close()

    if not rows:
        return "No payment records found."

    return str(rows)


@tool
def create_task(summary: str) -> str:
    """File a follow-up task for a human to handle."""

    TASK_BOARD.append(summary)

    return "Filed: " + summary


# -----------------------------
# Technical Issues
# -----------------------------

TECH_ISSUES = {
    "login": "Reset the password from Forgot Password, then wait 5 minutes.",
    "app": "Update to app version 4.2 or later, then clear the app cache.",
    "video": "Switch the player quality to 480p, or watch on the website.",
    "website": "Hard refresh with Ctrl+Shift+R, or clear the browser cache.",
}


@tool
def search_tech_issues(topic: str) -> str:
    """
    Look up the known workaround for a technical issue.
    Supported topics: login, app, video, website.
    """

    topic = topic.lower().strip()

    return TECH_ISSUES.get(
        topic,
        "No known issue. This looks like a new problem.",
    )
