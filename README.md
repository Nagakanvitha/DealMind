# DealMind — Sales Intelligence That Remembers Every Conversation

DealMind is a memory-first sales intelligence agent. It uses Hindsight to retain durable account facts and recall relevant history before generating the next sales recommendation.

## Architecture

```text
Sales Rep
   ↓
Streamlit UI
   ↓
DealMind Agent
   ├── Hindsight Recall ──→ relevant account memories
   │                           ↓
   └──────────────→ Groq LLM ←┘
                         ↓
                    response
                         ↓
                  Hindsight Retain
```

Hindsight is the persistent memory layer. Groq is used for response generation.

## Run locally

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your Hindsight Cloud API key and Groq API key.

Hindsight Cloud currently uses `https://api.hindsight.vectorize.io` and the official Python package is `hindsight-client`.

4. Start:

```bash
python -m streamlit run app.py
```

## 60-second demo

1. Click **Seed realistic Acme account**.
2. Ask: `Prepare me for my next meeting with Acme.`
3. Show the recalled memories.
4. Ask: `The prospect now says implementation time is their biggest concern. Remember that for future meetings.`
5. Ask again: `Prepare me for my next meeting with Acme.`
6. Show that the response incorporates the newly retained concern.

## Hindsight operations

- `retain()` stores durable account information and interaction outcomes.
- `recall()` retrieves relevant memories for the current sales request.
- The recalled memories are injected into the agent's reasoning context.
- The completed interaction is retained so future sessions can build on it.

## Submission notes

Keep the public article and social post focused on the engineering story. Do not mention the event name in those deliverables, per the content guide.
