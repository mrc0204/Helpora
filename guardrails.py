# guardrails.py


# =========================================================
# INPUT GUARDRAIL
# =========================================================

BLOCK_PHRASES = [
    "ignore your instructions",
    "ignore previous instructions",
    "forget your instructions",
]


def input_guardrail(ticket: str) -> bool:
    """
    Block obvious prompt-injection attempts
    before the request reaches the agents.
    """

    if not ticket:
        return False

    ticket_lower = ticket.lower()

    return not any(
        phrase in ticket_lower
        for phrase in BLOCK_PHRASES
    )


# =========================================================
# OUTPUT GUARDRAIL
# =========================================================

def output_guardrail(reply: str) -> bool:
    """
    Prevent student IDs from being leaked
    in the final response.
    """

    if not reply:
        return False

    return "S-7-" not in reply


# =========================================================
# POLICY GUARDRAIL
# =========================================================

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
    Prevent the agent from claiming that it
    directly moved or refunded money.
    """

    if not reply:
        return False

    reply_lower = reply.lower()

    return not any(
        phrase in reply_lower
        for phrase in POLICY_PHRASES
    )


# =========================================================
# VALIDATION FUNCTIONS
# =========================================================

def validate_input(ticket: str) -> bool:
    """
    Run all input-level safety checks.
    """

    return input_guardrail(ticket)


def validate_output(reply: str) -> bool:
    """
    Run all output-level safety checks.
    """

    return (
        output_guardrail(reply)
        and policy_guardrail(reply)
    )
