# config.py

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq


# =========================================================
# ENVIRONMENT VARIABLES
# =========================================================

# Loads .env when running locally.
# On Hugging Face, Secrets are already exposed as
# environment variables, so this still works.
load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")


# =========================================================
# API KEY VALIDATION
# =========================================================

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. "
        "Add it to your .env file locally or "
        to Hugging Face Space Secrets."
    )


# Make the Groq key available to LangChain/Groq
os.environ["GROQ_API_KEY"] = GROQ_API_KEY


# LangSmith is optional
if LANGSMITH_API_KEY:
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY


# =========================================================
# LLM
# =========================================================

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
)
