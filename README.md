# ⚙️ Bitcot Content OS

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![Next.js](https://img.shields.io/badge/Next.js-14.x-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E)

**Bitcot Content OS** is an autonomous, multi-agent AI content generation factory designed for B2B tech companies. Unlike standard AI wrappers, this system acts as an elite in-house ghostwriter. It uses a strict psychological playbook to generate high-density, anti-fluff content specifically optimized for cynical software engineering buyers (CTOs, Senior Developers, and Founders).

---

## ✨ Core Features

*   **🧠 Multi-Agent Architecture:** A chained pipeline of specialized AI agents (ICP, SEO, Writer, Repurposing, Regenerate) powered by Anthropic's Claude 3 Opus/Sonnet.
*   **🎯 ICP Gatekeeper:** Every topic is automatically scored against the Bitcot Ideal Customer Profile. Topics scoring below 65% are outright rejected to save token costs and maintain brand focus.
*   **✍️ Omni-Channel Generation:** Inputs a single topic and simultaneously generates an SEO-optimized Blog Post, a LinkedIn post, an X (Twitter) thread, and corresponding Image Prompts.
*   **🎨 Dynamic Brand Imagery:** Integrated with Pollinations.ai (FLUX models) to autonomously generate header images. Features dynamic logo injection based on author voice (e.g., forcing the exact Bitcot typographic logo in corporate posts).
*   **🎛️ Human-in-the-Loop Dashboard:** A premium, dark-mode Next.js dashboard to review drafts, monitor token costs, and manage the content lifecycle.
*   **🔬 Surgical Regeneration:** Version-controlled editing. Users can select specific blocks (e.g., "LinkedIn Hook") and provide feedback to surgically regenerate *only* that piece without breaking the rest of the post.

---

## 🏗️ System Architecture

The project is split into a heavily decoupled frontend and backend:

*   **Frontend (`/frontend`):** Next.js 14, React, Tailwind CSS, TypeScript.
*   **Backend (`/backend`):** FastAPI (Python), SQLAlchemy, Celery (Background Workers), Redis (Message Broker).
*   **Database:** Supabase (PostgreSQL) storing dynamic brand contexts, content versioning logs, and performance metrics.
*   **LLM Provider:** Anthropic Claude (via `anthropic-python`).

---

## 🚀 Getting Started

### Prerequisites
*   Node.js (v18+)
*   Python (3.10+)
*   Redis (for Celery background tasks)
*   Supabase Account (or local Postgres instance)
*   Anthropic API Key

### 1. Database Setup (Supabase)
1. Create a new Supabase project.
2. Run the SQL script found in `supabase_schema.sql` in your Supabase SQL Editor to generate the `brand_context`, `content_logs`, and `performance_metrics` tables.

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the `/backend` directory:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SUPABASE_DB_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
REDIS_URL=redis://localhost:6379/0
```

Start the Redis server, Celery worker, and FastAPI server:
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
cd backend
celery -A tasks.celery_app worker --loglevel=info

# Terminal 3: FastAPI Backend
cd backend
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:3000` to access the Control Center.

---

## 🗺️ Roadmap (Upcoming Features)

- [ ] **Mode A (Trend Detection):** A proactive `ResearchAgent` that scrapes HackerNews, X, and TechCrunch to detect viral spikes and automatically pitch highly relevant topics.
- [ ] **The Learning Loop (Analytics Agent):** Connecting to the LinkedIn and X APIs to pull live engagement data, allowing the AI to retroactively update the `brand_context` database with proven, high-performing hooks.
- [ ] **Automated Scheduling:** Integration with Buffer/Typefully APIs for direct-to-social publishing.

---

## 🔒 License
Proprietary & Confidential. Property of Bitcot Technology.
