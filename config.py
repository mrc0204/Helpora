import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables from .env
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# Validate required key
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set. "
        "Add it to your .env file or deployment secrets."
    )

# Make the key available to LangChain/Groq
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# LangSmith is optional
if LANGSMITH_API_KEY:
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY

# Helpora LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)
