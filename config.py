# config.py

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq


# Load .env when running locally.
# On Render, environment variables are loaded automatically.
load_dotenv()


# API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")


# Validate Groq API key
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. "
        "Add it to your .env file locally or "
        "to Render Environment Variables."
    )


# Make the Groq key available to LangChain
os.environ["GROQ_API_KEY"] = GROQ_API_KEY


# LangSmith is optional
if LANGSMITH_API_KEY:
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY


# Helpora LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
)
