# rag.py

import chromadb
from langchain_core.tools import tool


# =========================================================
# REFUND POLICY
# =========================================================

POLICY_DOC = """
Refund window: students who drop a course within the first 14 days
of the term are eligible for a full refund. After day 14 and up to
day 30, students receive a 50% refund. No refunds are issued after
day 30.

Refund method: refunds are returned to the original payment method
used at checkout. If the original method no longer works
(an expired card, for example), the refund is issued as store credit
instead, valid for one year.

Duplicate charges: if the same charge appears twice for the same
student and course, it is treated as a billing error, not a standard
refund, and is reversed in full regardless of the refund window above.

Lab and material fees: lab and material fees follow the same refund
window as the course fee, but are never eligible for store credit -
they are refunded to the original method or not at all.

Scholarship students: students on a scholarship covering more than
50% of the fee should be routed to the finance office directly;
do not process their refund automatically.

Escalation: any request involving more than Rs 20000 must be filed
as a task for a human to approve, never auto-approved by the agent.
""".strip()


# =========================================================
# CHUNKING
# =========================================================

def chunk_text(text: str, max_chars: int = 260) -> list[str]:
    """
    Split the policy document into reasonably sized chunks.
    """

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    chunks = []

    for paragraph in paragraphs:

        if len(paragraph) <= max_chars:
            chunks.append(paragraph)
            continue

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


# =========================================================
# CHROMA DATABASE
# =========================================================

# Persistent Chroma storage.
#
# This allows the vector database to be stored in the
# application directory instead of existing only in memory.

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)


collection = chroma_client.get_or_create_collection(
    name="policy",
    metadata={
        "hnsw:space": "cosine"
    },
)


# =========================================================
# INDEX POLICY
# =========================================================

def index_policy():
    """
    Add policy chunks to ChromaDB if they are not already indexed.
    """

    if collection.count() > 0:
        return

    collection.add(
        ids=[
            f"chunk-{i}"
            for i in range(len(CHUNKS))
        ],
        documents=CHUNKS,
    )


# Build the index when this module loads.
index_policy()


# =========================================================
# VECTOR SEARCH
# =========================================================

def vector_search(
    query: str,
    n_results: int = 2,
) -> list[str]:
    """
    Retrieve the most relevant policy chunks.
    """

    if not query or not query.strip():
        return []

    result = collection.query(
        query_texts=[query.strip()],
        n_results=n_results,
    )

    documents = result.get("documents", [])

    if not documents:
        return []

    return documents[0]


# =========================================================
# RAG TOOL
# =========================================================

@tool
def search_policy(question: str) -> str:
    """
    Search the refund policy for information relevant
    to the student's question.
    """

    results = vector_search(
        question,
        n_results=2,
    )

    if not results:
        return "No relevant policy information was found."

    return "\n---\n".join(results)
