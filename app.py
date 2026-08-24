# app.py

import os
import gradio as gr

from database import initialize_database
from agents import ask
from guardrails import validate_input, validate_output


# =========================================================
# INITIALIZATION
# =========================================================

initialize_database()


# =========================================================
# HELPORA RESPONSE
# =========================================================

def helpora_response(ticket: str) -> str:
    """Process a user's request through Helpora."""

    if not ticket or not ticket.strip():
        return "Please describe your issue."

    ticket = ticket.strip()

    # Input guardrail
    if not validate_input(ticket):
        return "I'm sorry, I can't process that request."

    try:
        # Run Helpora
        result = ask(ticket)

        reply = result.get(
            "reply",
            "Sorry, I couldn't generate a response."
        )

    except Exception as error:
        # TEMPORARY DEBUGGING
        print(f"Helpora error: {type(error).__name__}: {error}")

        return (
            f"Error: {type(error).__name__}: {error}"
        )

    # Output guardrails
    if not validate_output(reply):
        return "I'm sorry, I can't process that request."

    return reply


# =========================================================
# GRADIO UI
# =========================================================

with gr.Blocks(title="Helpora") as demo:

    gr.Markdown(
        """
        # 🤖 Helpora

        ### AI-powered campus support assistant

        Ask Helpora about:

        - 💳 Payments and billing
        - 💰 Refunds
        - 🧾 Duplicate charges
        - 🔧 Technical issues
        - 🔐 Login problems
        - 📱 App and website problems
        """
    )

    ticket_input = gr.Textbox(
        label="Describe your issue",
        placeholder=(
            "Example: I was charged twice for my course fee. "
            "My ID is S-7-042."
        ),
        lines=5,
    )

    submit_button = gr.Button("Ask Helpora")

    clear_button = gr.Button("Clear")

    response_output = gr.Textbox(
        label="Helpora Response",
        lines=7,
        interactive=False,
    )

    submit_button.click(
        fn=helpora_response,
        inputs=ticket_input,
        outputs=response_output,
    )

    ticket_input.submit(
        fn=helpora_response,
        inputs=ticket_input,
        outputs=response_output,
    )

    clear_button.click(
        fn=lambda: ("", ""),
        inputs=None,
        outputs=[
            ticket_input,
            response_output,
        ],
    )

    gr.Examples(
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
        inputs=ticket_input,
    )


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 10000)),
    )
