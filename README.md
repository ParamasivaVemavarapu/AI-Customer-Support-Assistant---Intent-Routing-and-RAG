# AI Customer Support Assistant

A full-stack support assistant that routes customer requests, retrieves grounded knowledge, remembers conversations, cites sources, and escalates sensitive or low-confidence cases to a human.

## Product Walkthrough

```mermaid
flowchart LR
    A["1. Customer message"] --> B["2. Detect intent"]
    B --> C["3. Retrieve policy"]
    C --> D{"4. Confidence and safety check"}
    D -->|"Safe"| E["5. Cited answer and memory"]
    D -->|"Sensitive or uncertain"| F["5. Human escalation"]
```

### Example: automated support path

**Customer**

> How do I request a refund for a duplicate charge?

**Representative response**

> I classified this as a **billing** request and found the refund policy. Submit the transaction ID through the billing form; duplicate-charge reviews are normally started after verification.
>
> **Citation:** starter-faq.md · Refunds and duplicate charges

### Example: escalation path

**Customer**

> My account may be compromised. I need a human now.

**Representative response**

> This request has been escalated to a human support agent because it concerns possible account compromise.

The response contract includes intent, confidence, citations, session ID, escalation status, and escalation ID. Examples show implemented behavior and are not classification-accuracy claims.

### API example

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"How do I request a refund for a duplicate charge?"}'
```

```json
{
  "session_id": "example-session-id",
  "message_id": 2,
  "answer": "Submit the transaction ID through the billing form...",
  "intent": "billing",
  "confidence": 0.82,
  "citations": [
    {
      "source": "starter-faq.md",
      "section": "Refunds and duplicate charges",
      "passage": "Duplicate charges can be submitted for review...",
      "score": 0.82
    }
  ],
  "escalated": false,
  "escalation_id": null
}
```

## The Problem

Support teams repeatedly answer the same questions while also handling urgent fraud, safety, account-access, and complaint cases. A useful assistant must do more than generate text: it must understand the request, retrieve approved information, maintain context, and know when automation should stop.

## The Solution

This application combines deterministic intent routing with semantic RAG. FastAPI classifies each request, retrieves relevant knowledge from Qdrant, generates or extracts a cited answer, persists the conversation in SQLite, and creates an escalation record when policy conditions are met. A Next.js console exposes the complete workflow.

## Tech Stack

**Python | FastAPI | Next.js | TypeScript | Sentence Transformers | Qdrant | SQLite | Groq/Gemini/Mistral | Docker | GitHub Actions**

> The current implementation uses sentence-transformer embeddings and deterministic intent rules. It does not claim a separately trained PyTorch intent-classification model.

## Architecture

```mermaid
flowchart TD
    C["Customer"] --> UI["Next.js console"]
    UI --> API["FastAPI API"]
    API --> ROUTE["Intent router"]
    ROUTE --> GATE{"Escalate?"}
    GATE -->|"Yes"| HUMAN["Human queue"]
    GATE -->|"No"| RAG["RAG retriever"]
    RAG --> Q[("Qdrant")]
    RAG --> GEN["LLM or extractive answer"]
    GEN --> DB[("SQLite memory")]
    DB --> UI
```

## Key Features

- Route billing, technical, account, product, complaint, and general requests
- Search a Qdrant knowledge base with sentence-transformer embeddings
- Return source citations with each grounded answer
- Preserve multi-turn session history in SQLite
- Escalate explicit human requests and sensitive language
- Escalate low-confidence retrieval and repeated unresolved responses
- Upload PDF, DOCX, Markdown, and TXT knowledge sources
- Review and update human-escalation cases through the API
- Run without an LLM key using an extractive fallback
- Test and build the project through GitHub Actions CI

## Results

The project implements the complete support decision path in one application: **route → retrieve → answer → remember → escalate**. The default escalation threshold is `0.35`, and two unresolved assistant responses trigger escalation. These are policy settings, not model-accuracy claims. A labeled intent set and offline RAG evaluation are needed before reporting classification or retrieval metrics.

## Screenshots / Demo

Run the local demonstration and test both automation paths:

- Support console: `http://localhost:3000`
- API documentation: `http://localhost:8000/docs`
- Qdrant dashboard: `http://localhost:6333/dashboard`

Example demo flow:

1. Ask a product or billing question and inspect the cited knowledge source.
2. Continue in the same session to verify conversation memory.
3. Ask for a human agent or submit fraud-related language to verify escalation.

## How to Run

### Prerequisites

- Docker and Docker Compose
- Optional: a Groq, Gemini, or Mistral API key

### Setup

```bash
git clone https://github.com/ParamasivaVemavarapu/AI-Customer-Support-Assistant---Intent-Routing-and-RAG.git
cd AI-Customer-Support-Assistant---Intent-Routing-and-RAG
cp backend/.env.example backend/.env
docker compose up --build
```

The backend indexes `knowledge-base/starter-faq.md` on first startup. Extractive mode works without an external LLM key.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Check application health |
| `POST` | `/api/chat` | Route, retrieve, answer, remember, or escalate |
| `GET` | `/api/sessions/{session_id}` | Return conversation history |
| `POST` | `/api/knowledge` | Add knowledge-base content |
| `GET` | `/api/escalations` | List escalation cases |
| `PATCH` | `/api/escalations/{case_id}` | Update escalation status |

## Escalation Policy

The assistant escalates when the customer requests a human, uses urgent safety/fraud/legal/account-compromise language, receives retrieval confidence below the configured threshold, or accumulates two unresolved responses.

## Production Roadmap

- Add screenshots and a hosted demonstration
- Train and evaluate a supervised transformer intent classifier
- Replace SQLite with PostgreSQL and add tenant isolation
- Integrate Zendesk, Salesforce, or ServiceNow
- Add PII redaction, authentication, RBAC, rate limiting, and audit logs
- Add hybrid retrieval, reranking, and offline RAG evaluation

## License

MIT
