# config.py

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")


if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. "
        "Add it to your .env file locally or "
        "to Render Environment Variables."
    )


os.environ["GROQ_API_KEY"] = GROQ_API_KEY


if LANGSMITH_API_KEY:
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)
