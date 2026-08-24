# Helpora

Helpora is a multi-agent AI support system designed to handle campus billing and technical support queries.

## Features

- Multi-agent architecture
- Intelligent ticket routing
- Billing support agent
- Technical support agent
- Payment lookup using SQLite
- Technical issue lookup
- Refund-policy RAG using ChromaDB
- Input guardrails
- Output guardrails
- Policy guardrails
- Groq LLM
- LangGraph orchestration
- Simple Gradio interface
- LangSmith observability support

## Architecture

```text
                    User
                      |
                      v
                 Gradio UI
                      |
                      v
              Input Guardrail
                      |
                      v
                 Helpora Router
                  /          \
                 /            \
                v              v
          Billing Agent     Tech Agent
             |                  |
       +-----+------+      +----+----+
       |            |      |         |
    Payments      RAG    Tech DB   Task Board
       |            |
       +-----+------+
             |
             v
       Output Guardrails
             |
             v
          Response
