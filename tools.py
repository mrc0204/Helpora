# tools.py

from langchain_core.tools import tool

from database import get_connection


# =========================================================
# HUMAN TASK BOARD
# =========================================================

TASK_BOARD = []


@tool
def create_task(summary: str) -> str:
    """
    File a follow-up task for a human team member.
    """

    summary = summary.strip()

    if not summary:
        return "Task could not be created."

    TASK_BOARD.append(summary)

    return f"Filed: {summary}"


# =========================================================
# PAYMENT LOOKUP
# =========================================================

@tool
def lookup_payments(student_id: str) -> str:
    """
    Look up all payment records for a student ID.
    """

    student_id = student_id.strip()

    if not student_id:
        return "No student ID was provided."

    db = get_connection()

    try:
        rows = db.execute(
            """
            SELECT student_name, amount, note
            FROM payments
            WHERE student_id = ?
            """,
            (student_id,),
        ).fetchall()

    finally:
        db.close()

    if not rows:
        return "No payment records found."

    return str(rows)


# =========================================================
# TECHNICAL ISSUE DATABASE
# =========================================================

TECH_ISSUES = {
    "login": (
        "Reset the password from Forgot Password, "
        "then wait 5 minutes."
    ),

    "app": (
        "Update to app version 4.2 or later, "
        "then clear the app cache."
    ),

    "video": (
        "Switch the player quality to 480p, "
        "or watch on the website."
    ),

    "website": (
        "Hard refresh with Ctrl+Shift+R, "
        "or clear the browser cache."
    ),
}


@tool
def search_tech_issues(topic: str) -> str:
    """
    Look up the known workaround for a technical issue.

    Supported topics:
    login, app, video, website
    """

    topic = topic.strip().lower()

    if topic in TECH_ISSUES:
        return TECH_ISSUES[topic]

    return (
        "No known issue. "
        "This looks like a new problem."
    )
