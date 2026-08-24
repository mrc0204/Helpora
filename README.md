# Helpora 🤖

Helpora is a multi-agent AI campus support system that intelligently routes student requests to specialized billing or technical support agents.

## ✨ Features

- 🤖 Multi-agent AI architecture
- 🔀 Intelligent billing/technical routing
- 💳 Billing and payment support
- 🔧 Technical issue support
- 🧾 SQLite payment lookup
- 📚 RAG-based refund policy search
- 🧠 ChromaDB vector database
- 🛡️ Input and output guardrails
- 👤 Human escalation task system
- ⚡ Groq LLM
- 🔗 LangGraph orchestration
- 🎨 Gradio web interface
- 📊 Optional LangSmith observability

---

## 🏗️ Architecture

```text
                         USER
                           │
                           ▼
                    ┌─────────────┐
                    │  Gradio UI  │
                    └──────┬──────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Input Guardrail  │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  Helpora Router  │
                  └───────┬───┬──────┘
                          │   │
                 Billing  │   │  Tech
                          │   │
              ┌───────────▼┐ ┌▼────────────┐
              │   Billing   │ │    Tech     │
              │    Agent    │ │    Agent    │
              └─────┬───────┘ └──────┬─────┘
                    │                │
          ┌─────────┼────────┐       │
          ▼         ▼        ▼       ▼
       Payments    RAG     Tasks   Tech Issues
          │         │        │       │
          └─────────┴────────┴───────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ Output Guardrails │
                 └─────────┬─────────┘
                           │
                           ▼
                       RESPONSE
