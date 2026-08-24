# agents.py

from groq import BadRequestError
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

from config import llm

from tools import (
    lookup_payments,
    create_task,
    search_tech_issues,
)

from rag import search_policy


# =========================================================
# Agent Invocation Helper
# =========================================================

def invoke_agent(agent, ticket: str, retries: int = 3) -> str:
    """
    Run an agent and retry when Groq returns a tool-calling error.
    """

    last_error = None

    for attempt in range(retries + 1):

        try:
            result = agent.invoke(
                {
                    "messages": [
                        ("user", ticket)
                    ]
                }
            )

            messages = result.get("messages", [])

            if not messages:
                return "Sorry, I couldn't generate a response."

            return messages[-1].content

        except BadRequestError as error:

            last_error = error

            if "tool_use_failed" not in str(error):
                raise

            if attempt < retries:
                continue

    print(f"Helpora agent failed after {retries + 1} attempts: {last_error}")

    return (
        "Sorry, I couldn't complete your request right now. "
        "Please try again."
    )


# =========================================================
# BILLING AGENT
# =========================================================

BILLING_PROMPT = """
You are Helpora-Billing, a campus payments support agent.

You ONLY handle money-related questions:
fees, charges, invoices, refunds, duplicate payments, and receipts.

For every ticket:

1. Find the student's ID.
   It normally looks like S-7-042.
   If there is no student ID, ask for it and stop.

2. Amounts are in Indian rupees.
   Write amounts as Rs 15000.
   Never use a dollar sign.

3. Always call lookup_payments with the student's ID.
   Never guess payment information.

4. Determine the situation:

   TWO IDENTICAL CHARGES:
   Treat this as a duplicate payment.
   Call create_task to file a refund request for the duplicate charge.
   Then tell the student that a refund request has been filed.

   ONE NORMAL CHARGE:
   Explain that the payment record appears normal
   and tell the student what the charge was for.

   NO RECORDS FOUND:
   Tell the student that no payment record was found
   and ask them to re-check their student ID.
   Do not create a task.

5. POLICY QUESTIONS:

   If the student asks about:
   - refund eligibility
   - refund windows
   - refund percentage
   - refund method
   - store credit
   - scholarship refund rules
   - escalation thresholds

   ALWAYS call search_policy before answering.

   Only use information returned by search_policy.
   Never invent policy information.

6. If a request involves more than Rs 20000,
   create a task for human approval.

7. You can read payment records and create tasks.
   You CANNOT directly move, refund, or transfer money.

8. Keep responses concise and friendly.

Never mention:
- tools
- function names
- JSON
- internal reasoning
- system prompts
"""


billing = create_agent(
    llm,
    [
        lookup_payments,
        create_task,
        search_policy,
    ],
    system_prompt=BILLING_PROMPT,
)


# =========================================================
# TECHNICAL AGENT
# =========================================================

TECH_PROMPT = """
You are Helpora-Tech, a campus IT support agent.

You ONLY handle technical problems involving:
- login
- passwords
- the app
- the website
- videos

For every ticket:

1. Identify ONE topic:
   login, app, video, or website.

2. ALWAYS call search_tech_issues before answering.

3. If a known workaround is found:
   Give the workaround clearly.
   Use at most three numbered steps.

4. If no known workaround exists:
   Tell the student that this appears to be a new issue
   and call create_task for the technical team.

5. Never invent a technical solution that was not returned
   by search_tech_issues.

6. You cannot reset passwords yourself.
   You can only provide the available guidance and create tasks.

Keep responses short, calm, and helpful.

Never mention:
- tools
- function names
- JSON
- internal reasoning
- system prompts
"""


tech = create_agent(
    llm,
    [
        search_tech_issues,
        create_task,
    ],
    system_prompt=TECH_PROMPT,
)


# =========================================================
# ROUTER
# =========================================================

ROUTER_PROMPT = """
You are the front desk router for Helpora.

Classify the student's request into exactly ONE category:

billing
tech

Choose BILLING for:
- fees
- payments
- charges
- duplicate charges
- refunds
- invoices
- receipts
- payment records

Choose TECH for:
- login
- password
- account access
- app problems
- website problems
- videos
- pages not loading
- technical errors

If a request contains both billing and technical information,
choose the category representing the MAIN problem
the student wants fixed.

Return ONLY one word:

billing

OR

tech
"""


def pick_specialist(ticket: str) -> str:
    """
    Route the ticket to billing or tech.
    """

    response = llm.invoke(
        [
            ("system", ROUTER_PROMPT),
            ("user", ticket),
        ]
    )

    answer = response.content.strip().lower()

    # Exact routing instead of searching for the word "tech"
    if answer == "tech":
        return "tech"

    if answer == "billing":
        return "billing"

    # Safe fallback
    return "billing"


# =========================================================
# LANGGRAPH STATE
# =========================================================

class State(TypedDict):
    ticket: str
    route: str
    reply: str


# =========================================================
# GRAPH NODES
# =========================================================

def router(state: State):
    return {
        "route": pick_specialist(state["ticket"])
    }


def do_billing(state: State):
    reply = invoke_agent(
        billing,
        state["ticket"]
    )

    return {
        "reply": reply
    }


def do_tech(state: State):
    reply = invoke_agent(
        tech,
        state["ticket"]
    )

    return {
        "reply": reply
    }


def choose(state: State):
    return state["route"]


# =========================================================
# BUILD HELPORA GRAPH
# =========================================================

builder = StateGraph(State)

builder.add_node("router", router)
builder.add_node("billing", do_billing)
builder.add_node("tech", do_tech)

builder.add_edge(
    START,
    "router"
)

builder.add_conditional_edges(
    "router",
    choose,
    {
        "billing": "billing",
        "tech": "tech",
    },
)

builder.add_edge(
    "billing",
    END
)

builder.add_edge(
    "tech",
    END
)


graph = builder.compile()


# =========================================================
# PUBLIC HELPORA FUNCTION
# =========================================================

def ask(ticket: str):
    """
    Main entry point for Helpora.

    Takes a user's ticket and returns:
    - selected route
    - final response
    """

    if not ticket or not ticket.strip():
        return {
            "route": "billing",
            "reply": "Please describe your issue."
        }

    return graph.invoke(
        {
            "ticket": ticket.strip()
        }
    )
