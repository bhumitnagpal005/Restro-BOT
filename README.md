# RestroBot

A full-stack AI assistant for querying restaurant menus in Roorkee, India. Built on an advanced RAG pipeline with hybrid retrieval, cross-encoder reranking, and LLM-as-judge evaluation — served via a Flask REST API and a React + Vite chat frontend.

---

## Architecture

```
User Query (React UI)
        │
        ▼
Flask REST API  (/api/chat)
        │
        ▼
  RAG Pipeline
  ┌─────────────────────────────────────┐
  │  Stage 1 — Hybrid Retrieval         │
  │  ┌─────────────┐  ┌──────────────┐  │
  │  │ FAISS Dense │  │  BM25 Sparse │  │
  │  │ (all-MiniLM)│  │  (keyword)   │  │
  │  └──────┬──────┘  └──────┬───────┘  │
  │         └────────┬────────┘          │
  │    Reciprocal Rank Fusion (top-20)   │
  │                  │                   │
  │  Stage 2 — Cross-Encoder Reranking   │
  │       ms-marco-MiniLM-L-6-v2         │
  │            top-20 → top-5            │
  └──────────────────┬───────────────────┘
                     │
              Conversation Memory
              (5-turn sliding window)
                     │
                     ▼
           Gemini 2.5 Flash (generation)
                     │
                     ▼
              Response + Metrics
```

---

## Project Structure

```
RestroBot/
├── backend/
│   ├── app.py                  # Flask REST API
│   ├── rag/
│   │   ├── pipeline.py         # Orchestrator + session management
│   │   ├── retrieval.py        # HybridRetriever (FAISS + BM25 + reranker)
│   │   ├── memory.py           # ConversationMemory (sliding window)
│   │   ├── generation.py       # Gemini 2.5 Flash response generation
│   │   └── metrics.py          # LLM-as-judge evaluation
│   ├── data/
│   │   ├── scraper.py          # Zomato scraper (Selenium + BeautifulSoup)
│   │   ├── cleaner.py          # JSON → cleaned document strings
│   │   └── runner.py           # Scrape all 9 restaurants
│   ├── menu/                   # Scraped JSON files (9 restaurants)
│   └── index_cache/            # Persisted FAISS index + BM25 (auto-generated)
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   │       ├── Header.jsx
│   │       ├── ChatWindow.jsx
│   │       ├── Message.jsx
│   │       ├── InputBar.jsx
│   │       ├── TypingIndicator.jsx
│   │       └── MetricsPanel.jsx
│   ├── package.json
│   └── vite.config.js          # Proxies /api → localhost:5001
├── requirements.txt
└── .env.example
```

---

## RAG Pipeline

### Stage 1 — Hybrid Retrieval
Two complementary retrieval methods are run in parallel and fused:

- **Dense (FAISS):** Documents and queries are embedded using `all-MiniLM-L6-v2`. FAISS performs fast nearest-neighbour search over 500+ menu document vectors, capturing semantic similarity (e.g. "cheap sandwich" matches "affordable burger").
- **Sparse (BM25):** Classic keyword scoring that excels at exact matches — restaurant names, dish names, prices.
- **Reciprocal Rank Fusion (RRF):** Merges both ranked lists without weight tuning. Documents appearing high in both lists score highest, producing a top-20 candidate pool.

### Stage 2 — Cross-Encoder Reranking
The cross-encoder (`ms-marco-MiniLM-L-6-v2`) reads each (query, candidate) pair jointly and scores direct relevance — more accurate than the bi-encoder used in Stage 1. Top-20 candidates are narrowed to top-5.

### Generation
The top-5 passages and the last 5 turns of conversation history are injected into a structured prompt for **Gemini 2.5 Flash**, which generates the final answer.

### Evaluation (on-demand)
Each response can be evaluated via `/api/evaluate` using **LLM-as-judge** — Gemini scores the response on:
- **Faithfulness** — is every claim grounded in the retrieved context?
- **Answer Relevance** — does the response directly address the query?

This is intentionally on-demand (not automatic) to stay within free-tier API quotas.

---

## Setup

### 1. Environment variables
```sh
cp .env.example .env
# Fill in your Gemini API key
```

### 2. Backend
```sh
cd backend
python -m venv virenv
source virenv/bin/activate      # Windows: virenv\Scripts\activate
pip install -r ../requirements.txt
python app.py
```

On first run, the server builds and caches the FAISS + BM25 index. Subsequent starts load from `index_cache/` in seconds.

### 3. Frontend
```sh
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) (or whichever port Vite assigns).

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/chat` | Send a query, get a response + metrics |
| `POST` | `/api/evaluate` | Run LLM-as-judge on a specific response |
| `DELETE` | `/api/session/<id>` | Clear conversation history for a session |

### `POST /api/chat`
```json
// Request
{ "query": "What's the cheapest veg burger at KFC?", "session_id": "<uuid>" }

// Response
{
  "response": "The cheapest veg option at KFC is the Veg Rice Box at ₹149.",
  "exchange_id": "<uuid>",
  "metrics": {
    "retrieval_confidence": 0.91,
    "latency": { "retrieval_ms": 210, "generation_ms": 1840, "total_ms": 2050 }
  }
}
```

### `POST /api/evaluate`
```json
// Request
{ "exchange_id": "<uuid>" }

// Response
{ "faithfulness": 0.94, "answer_relevance": 0.89 }
```

---

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Zomato dynamic content and lazy-loaded menus | Selenium with retry loops to click all "Read More" buttons before parsing |
| Single-stage dense retrieval missing exact name matches | Hybrid FAISS + BM25 with RRF — keyword precision and semantic recall combined |
| Bi-encoder shallow scoring on top candidates | Cross-encoder reranking on shortlist for fine-grained relevance scoring |
| Gemini API rate limits (5 RPM free tier) | LLM-as-judge evaluation decoupled from chat path; restaurant descriptions cached to disk |
| Slow cold-start from re-encoding 500+ documents | FAISS index + BM25 + embeddings persisted to disk with MD5 cache invalidation |
| Vague follow-up queries ("what about non-veg?") | Per-session sliding-window conversation memory injected into every prompt |

---

## Restaurants Covered

KFC · Domino's · Pizza Hut · Foodbay · Waffle by Nature · Patiala Lassi · Desi Tadka · Baap of Rolls · Prakash Hotel
