# app.py

import gradio as gr

from database import initialize_database
from agents import ask
from guardrails import validate_input, validate_output


# Initialize database when the app starts
initialize_database()


def helpora_response(ticket: str) -> str:
    """Process a user's ticket through Helpora."""

    if not ticket or not ticket.strip():
        return "Please describe your issue."

    ticket = ticket.strip()

    # Input guardrail
    if not validate_input(ticket):
        return "I'm sorry, I can't process that request."

    try:
        result = ask(ticket)
        reply = result["reply"]

    except Exception as e:
        print(f"Helpora error: {e}")
        return (
            "I'm sorry, something went wrong while processing "
            "your request. Please try again."
        )

    # Output guardrails
    if not validate_output(reply):
        return "I'm sorry, I can't process that request."

    return reply


# -----------------------------
# Gradio Interface
# -----------------------------

demo = gr.Interface(
    fn=helpora_response,
    inputs=gr.Textbox(
        label="How can Helpora help you?",
        placeholder="Describe your billing or technical issue...",
        lines=4,
    ),
    outputs=gr.Textbox(
        label="Helpora",
        lines=6,
    ),
    title="Helpora",
    description=(
        "AI-powered campus support assistant. "
        "Ask about billing, payments, refunds, or technical issues."
    ),
    examples=[
        [
            "I was charged twice for my course fee. "
            "My id is S-7-042."
        ],
        [
            "I can't log in to the app. "
            "It says password incorrect."
        ],
        [
            "If I drop the course in week 2, "
            "how much of my fee do I get back?"
        ],
    ],
)


if __name__ == "__main__":
    demo.launch()
