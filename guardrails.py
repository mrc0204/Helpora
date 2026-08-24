BLOCK_PHRASES = [
    "ignore your instructions",
    "ignore previous instructions",
    "forget your instructions",
]


def input_guardrail(ticket: str) -> bool:
    """
    Block prompt-injection attempts before they reach the agent.
    """

    return not any(
        phrase in ticket.lower()
        for phrase in BLOCK_PHRASES
    )


# -----------------------------
# Output Guardrail
# -----------------------------

def output_guardrail(reply: str) -> bool:
    """
    Prevent the agent from leaking student IDs in its response.
    """

    return "S-7-" not in reply


# -----------------------------
# Policy Guardrail
# -----------------------------

POLICY_PHRASES = [
    "i've refunded",
    "i have refunded",
    "i've transferred",
    "i have transferred",
    "money has been sent",
    "payment has been processed",
    "i've processed your refund",
    "i have processed your refund",
]


def policy_guardrail(reply: str) -> bool:
    """
    Prevent the agent from claiming that it directly moved/refunded money.
    """

    return not any(
        phrase in reply.lower()
        for phrase in POLICY_PHRASES
    )


# -----------------------------
# Combined Guardrail
# -----------------------------

def validate_input(ticket: str) -> bool:
    """Run input-level safety checks."""

    return input_guardrail(ticket)


def validate_output(reply: str) -> bool:
    """Run all output-level safety checks."""

    return (
        output_guardrail(reply)
        and policy_guardrail(reply)
    )
