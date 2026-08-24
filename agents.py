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


# -----------------------------
# Agent Invocation Helper
# -----------------------------

def invoke_agent(agent, ticket: str, retries: int = 3) -> str:
    """Run an agent with automatic retry for Groq tool-calling errors."""

    for attempt in range(retries + 1):
        try:
            result = agent.invoke({
                "messages": [("user", ticket)]
            })

            return result["messages"][-1].content

        except BadRequestError as e:

            if "tool_use_failed" not in str(e):
                raise

            if attempt == retries:
                return (
                    "[Helpora couldn't complete this request. "
                    "Please try again.]"
                )


# -----------------------------
# Billing Agent
# -----------------------------

BILLING_PROMPT = """
You are Helpora-Billing, a campus payments support agent.

You ONLY handle money questions:
fees, charges, invoices, refunds and duplicate payments.

For every ticket:

1. Find the student's ID. It looks like S-7-042.
   If there is none, ask for it and stop.

2. Amounts are in rupees.
   Write them as Rs 15000, never with a dollar sign.

3. Call lookup_payments with that ID.
   Always check with the tool. Never guess.

4. Decide which case you are in:

- TWO IDENTICAL CHARGES:
  This is a duplicate.
  Call create_task with an appropriate refund task.
  Then tell the student that a refund request has been filed.

- ONE NORMAL CHARGE:
  Nothing is wrong.
  Reassure the student and explain what the charge was for.

- NO RECORDS FOUND:
  Say that you could not find that ID and ask the student to re-check it.
  Do not file a task.

5. For questions about refund policies, refund windows,
   refund methods, or escalation thresholds:
   ALWAYS call search_policy before answering.

6. Reply in two or three warm sentences.
   No bullet points unless explaining technical steps.

Never mention tools, function names, JSON, or your reasoning.

You can read records and file tasks.
You cannot move money yourself.
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


# -----------------------------
# Technical Agent
# -----------------------------

TECH_PROMPT = """
You are Helpora-Tech, a campus IT support agent.

You ONLY handle technical problems:
logging in, passwords, the app, the website, and videos.

For every ticket:

1. Choose ONE topic:
   login, app, video, or website.

2. Call search_tech_issues with that topic.
   Always search before answering.
   Never invent a fix.

3. If a known issue matches:
   Give the exact workaround in your own words,
   using at most three numbered steps.

4. If nothing matches:
   Say it looks like a new problem and call create_task
   so the tech team can investigate.

Lead with the fix, not an apology.

Never mention tools, function names, JSON, or your reasoning.

You cannot reset passwords yourself.
You can only advise and log.
"""


tech = create_agent(
    llm,
    [
        search_tech_issues,
        create_task,
    ],
    system_prompt=TECH_PROMPT,
)


# -----------------------------
# Router
# -----------------------------

ROUTER_PROMPT = """
You are the front desk of a campus support team.

Read the student's ticket and decide which specialist should handle it.

Answer "billing" if the ticket is about:
money, fees, charges, invoices, refunds,
duplicate payments, or receipts.

Answer "tech" if the ticket is about:
technology, logging in, passwords, accounts,
the app, the website, videos, or pages not loading.

Rules:

- Reply with exactly one word: billing or tech.
- Lowercase.
- No punctuation.
- No explanation.
- If the ticket mentions both, choose the thing
  the student is asking you to FIX.
- If you genuinely cannot tell, answer billing.
"""


def pick_specialist(ticket: str) -> str:
    answer = llm.invoke([
        ("system", ROUTER_PROMPT),
        ("user", ticket),
    ]).content.lower()

    return "tech" if "tech" in answer else "billing"


# -----------------------------
# LangGraph State
# -----------------------------

class State(TypedDict):
    ticket: str
    route: str
    reply: str


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


# -----------------------------
# Build Graph
# -----------------------------

builder = StateGraph(State)

builder.add_node("router", router)
builder.add_node("billing", do_billing)
builder.add_node("tech", do_tech)

builder.add_edge(START, "router")

builder.add_conditional_edges(
    "router",
    choose,
    {
        "billing": "billing",
        "tech": "tech",
    },
)

builder.add_edge("billing", END)
builder.add_edge("tech", END)

graph = builder.compile()


# -----------------------------
# Public Helpora Function
# -----------------------------

def ask(ticket: str):
    """Send a user ticket through the Helpora multi-agent system."""

    return graph.invoke({
        "ticket": ticket
    })
