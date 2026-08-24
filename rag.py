# rag.py

import chromadb
from langchain_core.tools import tool


# -----------------------------
# Policy Document
# -----------------------------

POLICY_DOC = """
Refund window: students who drop a course within the first 14 days of the term are eligible
for a full refund. After day 14 and up to day 30, students receive a 50% refund. No refunds
are issued after day 30.

Refund method: refunds are returned to the original payment method used at checkout. If the
original method no longer works (an expired card, for example), the refund is issued as store
credit instead, valid for one year.

Duplicate charges: if the same charge appears twice for the same student and course, it is
treated as a billing error, not a standard refund, and is reversed in full regardless of the
refund window above.

Lab and material fees: lab and material fees follow the same refund window as the course fee,
but are never eligible for store credit - they are refunded to the original method or not at all.

Scholarship students: students on a scholarship covering more than 50% of the fee should be
routed to the finance office directly; do not process their refund automatically.

Escalation: any request involving more than Rs 20000 must be filed as a task for a human to
approve, never auto-approved by the agent.
""".strip()


# -----------------------------
# Chunking
# -----------------------------

def chunk_text(text: str, max_chars: int = 260):
    """Split the policy document into manageable chunks."""

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    chunks = []

    for paragraph in paragraphs:
        if len(paragraph) <= max_chars:
            chunks.append(paragraph)
        else:
            words = paragraph.split()
            current = ""

            for word in words:
                if len(current) + len(word) + 1 > max_chars:
                    if current.strip():
                        chunks.append(current.strip())
                    current = ""

                current += word + " "

            if current.strip():
                chunks.append(current.strip())

    return chunks


CHUNKS = chunk_text(POLICY_DOC)


# -----------------------------
# ChromaDB
# -----------------------------

chroma_client = chromadb.PersistentClient(path="./chroma_db")

collection = chroma_client.get_or_create_collection(
    "policy",
    metadata={"hnsw:space": "cosine"},
)


# Index policy chunks only once
if collection.count() == 0:
    collection.add(
        ids=[f"chunk-{i}" for i in range(len(CHUNKS))],
        documents=CHUNKS,
    )


# -----------------------------
# Vector Search
# -----------------------------

def vector_search(query: str, n_results: int = 2):
    """Retrieve the most relevant policy chunks."""

    result = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    return result["documents"][0]


# -----------------------------
# RAG Tool
# -----------------------------

@tool
def search_policy(question: str) -> str:
    """Search the refund policy for information relevant to a question."""

    results = vector_search(question, n_results=2)

    return "\n---\n".join(results)
