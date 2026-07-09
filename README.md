# ⚙️ Bitcot Content OS

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![Next.js](https://img.shields.io/badge/Next.js-14.x-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E)

**Bitcot Content OS** is an autonomous, multi-agent AI content generation factory designed for B2B tech companies. Unlike standard AI wrappers, this system acts as an elite in-house ghostwriter. It uses a strict psychological playbook to generate high-density, anti-fluff content specifically optimized for cynical software engineering buyers (CTOs, Senior Developers, and Founders).

---

## ✨ Core Features

*   **🧠 Multi-Agent Architecture:** A chained pipeline of specialized AI agents (ICP, Trend, Writer, Regenerate, Research) powered by Anthropic's Claude 3.5.
*   **📡 Trend Detection (Mode A):** An autonomous `TrendAgent` that scrapes HackerNews and DuckDuckGo News in real-time, feeding 50+ raw headlines through the ICP Gatekeeper to pitch the top 3 most valuable B2B topics.
*   **🎯 ICP Gatekeeper & Auto-Reshaper:** Every topic is scored against the Bitcot Ideal Customer Profile. High-value tech/developer topics pass seamlessly. Topics scoring low are automatically "reshaped" with enterprise angles to continue generation without failing.
*   **📚 Dynamic Narrative Strategy (EEAT & GEO):** Replaces static templates with a dynamic "Library of Narrative Modules". The AI acts as a Content Strategist, dynamically assembling the perfect structure (e.g., CTO Action Frameworks, Code Walkthroughs) based on the target persona. Fully optimized for Google's Generative Engine Optimization (GEO) with mandatory Executive Summaries and "Quick Answers" for AI Search Overviews.
*   **✍️ Omni-Channel Generation:** Inputs a single topic and simultaneously generates an SEO-optimized Blog Post, a LinkedIn post, an X (Twitter) thread, and corresponding Image Prompts.
*   **✨ Directed Enhancement Engine:** Users can input a specific "Enhancement Direction" to forcefully rewrite their Topic, Angle, and Image Idea in a highly targeted direction before generation.
*   **🎨 Intelligent Image Sourcing & Verification:** Choose between highly detailed AI-generated graphics (via OpenAI DALL-E 3) or fetch real-world photography using web search. Features an **OpenAI Vision verification layer** that actively reviews fetched web images for relevance, falling back to AI generation if a poor image is found.
*   **🔍 Enterprise-Grade SEO:** Automatically generates heavily constrained Title Tags (< 60 chars), URL slugs, Image Alt Text, and raw JSON-LD Article Schema markup for Google Rich Snippets.
*   **🎭 Dynamic Persona Overrides:** While it defaults to CTOs/CEOs, the system accepts custom personas on the fly and dynamically adjusts its entire scoring and writing model to target them.
*   **🌐 Factual Grounding:** When "Web Search" is enabled, the `ResearchAgent` fetches live facts and the writer weaves real product names, event details, and metrics into the content.
*   **📄 High-Fidelity PDF Export Engine:** Instantly converts drafts into perfectly styled PDFs for cross-team sharing, fortified with dynamic CSS print styles to prevent broken layouts or images being cut in half across pages.
*   **🎛️ Human-in-the-Loop Dashboard:** A premium, dark-mode Next.js dashboard to review drafts, discover trends, monitor exact AI token/image generation costs, and manage the content lifecycle.
*   **🔬 Surgical Regeneration:** Version-controlled editing. Users can select specific blocks (e.g., "LinkedIn Hook") and provide feedback to surgically regenerate *only* that piece without breaking the rest of the post.

---

## 🏗️ System Architecture

```mermaid
graph TD
    %% Core Infrastructure
    User([User / Content Manager]) --> UI[Next.js Dashboard]
    UI --> API[FastAPI Backend]
    
    %% Agents & Logic
    API --> TrendAgent[Trend Agent]
    API --> Celery[Celery Task Queue]
    Celery --> ICPAgent[ICP Agent]
    Celery --> WriterAgent[Writer Agent]
    Celery --> RegenAgent[Regenerate Agent]
    WriterAgent --> ResearchAgent[Research Agent]
    
    %% Brain & Memory
    ICPAgent -.-> Supabase[(Supabase PostgreSQL)]
    WriterAgent -.-> Supabase
    RegenAgent -.-> Supabase
    
    %% External Services
    TrendAgent --> HN[HackerNews API]
    TrendAgent --> DDG[DuckDuckGo News API]
    TrendAgent --> Claude[Anthropic Claude 3.5]
    WriterAgent --> Claude
    WriterAgent --> OpenAI[OpenAI DALL-E 3 Image Gen]
    ResearchAgent --> DDG
    
    %% Data Models inside DB
    Supabase -.-> BrandContext[brand_context]
    Supabase -.-> ContentLogs[content_logs]
    Supabase -.-> PerfMetrics[performance_metrics]
    
    %% Styling
    classDef ui fill:#000,stroke:#C8FF00,stroke-width:2px,color:#fff;
    classDef api fill:#070707,stroke:#fff,stroke-width:1px,color:#fff;
    classDef agent fill:#1A1A18,stroke:#C8FF00,stroke-width:1px,color:#C8FF00;
    classDef external fill:#0b3a3b,stroke:#00f0ff,stroke-width:1px,color:#fff;
    classDef db fill:#3ECF8E,stroke:#fff,stroke-width:1px,color:#000;
    
    class UI ui;
    class API,Celery api;
    class ICPAgent,WriterAgent,RegenAgent,ResearchAgent,TrendAgent agent;
    class HN,DDG,Claude,OpenAI external;
    class Supabase,BrandContext,ContentLogs,PerfMetrics db;
```

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
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
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

- [ ] **The Learning Loop (Analytics Agent):** Connecting to the LinkedIn and X APIs to pull live engagement data, allowing the AI to retroactively update the `brand_context` database with proven, high-performing hooks.
- [ ] **Automated Scheduling:** Integration with Buffer/Typefully APIs for direct-to-social publishing.

---

## 🔒 License
Proprietary & Confidential. Property of Bitcot Technology.
