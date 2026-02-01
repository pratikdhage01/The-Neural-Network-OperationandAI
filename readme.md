# MSME Decision‑Centric AI Agent System

An interactive full‑stack demo for **MSME operations management** powered by **Google Gemini** + multi‑agent orchestration.

- **Live demo (UI):** https://the-neural-network-operationand-ai.vercel.app/
- **Backend:** FastAPI + LangGraph/LangChain + MongoDB
- **Frontend:** Next.js dashboard (Vercel-ready)
- **Optional channel:** WhatsApp bot via Twilio webhook (use **ngrok** for local HTTPS)

---

## 🧭 Table of contents

- [What’s inside](#-whats-inside)
- [Architecture](#-architecture)
- [AI agents (actual graph)](#-ai-agents-actual-graph)
- [Quickstart (copy/paste)](#-quickstart-copypaste)
- [WhatsApp local deployment (Twilio + ngrok)](#-whatsapp-local-deployment-twilio--ngrok)
- [Try the API (cURL)](#-try-the-api-curl)
- [Troubleshooting](#-troubleshooting)
- [Repo map](#-repo-map)

---

## ✨ What’s inside

- Consumer chat that routes messages through a LangGraph agent workflow
- Operational endpoints for Orders / Inventory / Suppliers / Staff / Analytics
- Conversation persistence in MongoDB
- WhatsApp webhook endpoint (`/whatsapp/webhook`) compatible with Twilio
- Leads outreach + qualification agent endpoints (`/api/leads/*`)

---

## 🧱 Architecture

```mermaid
flowchart LR
  User[User] -->|Browser| UI[Next.js Dashboard\n(Vercel / :3000)]
  UI -->|HTTP| API[FastAPI\n:8000]

  API -->|/api/chat/*| Graph[LangGraph\nAgent Orchestration]
  Graph -->|LLM calls| Gemini[Google Gemini\n(GEMINI_MODEL)]
  Graph -->|reads/writes| DB[(MongoDB)]

  API -->|/api/leads/*| Leads[Leads Agent\n(outreach + qualification)]
  Leads -->|LLM calls| Gemini
  Leads -->|reads/writes| DB

  Twilio[Twilio WhatsApp Webhook] -->|POST /whatsapp/webhook| API
  ngrok[ngrok HTTPS tunnel] -. exposes .-> API
```

## 🧠 AI agents (actual graph)

This is the **actual decision graph** used by the backend chat pipeline (router → specialist agent → end).

```mermaid
flowchart TD
  Start([User message]) --> Router[router
  route_message()
  (Gemini router)]

  Router -->|customer_agent| Customer[customer_agent
  product inquiries,
  FAQs, guidance]
  Router -->|order_agent| Order[order_agent
  order placement,
  tracking, updates]
  Router -->|inventory_agent| Inventory[inventory_agent
  stock lookup,
  low-stock, adjustments]
  Router -->|supplier_agent| Supplier[supplier_agent
  supplier comms,
  procurement queries]
  Router -->|workload_agent| Workload[workload_agent
  staff tasks,
  workload distribution]
  Router -->|bottleneck_agent| Bottleneck[bottleneck_agent
  detect bottlenecks,
  suggest actions]

  Customer --> End([END])
  Order --> End
  Inventory --> End
  Supplier --> End
  Workload --> End
  Bottleneck --> End
```

---

## 🚀 Quickstart (copy/paste)

### Prerequisites

- **Python 3.12+**
- **Node.js 18+** (Node 20+ recommended)
- **MongoDB** (Docker *or* locally installed)
- Optional: **pnpm** (`npm i -g pnpm`) — recommended because a lockfile exists
- Optional (WhatsApp): **ngrok** + **Twilio** account

### 0) Start MongoDB

> Why Docker here?
> - Easiest “it works everywhere” MongoDB setup for demos.
> - Totally optional — you can use a local MongoDB install too.

**Option A — Docker (recommended):**

```bash
docker run -d --name msme-mongo -p 27017:27017 mongo:7
```

**Option B — Local MongoDB service:**

Make sure MongoDB is running on `mongodb://localhost:27017`.

### 1) Backend (FastAPI)

Create `agent-server/.env` (or copy `agent-server/.env.example`):

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=msme_db

# LLM (Google Gemini)
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.5-flash

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000
```

> Note: the repo uses `agent-server/pyproject.toml` for dependencies (there is no `requirements.txt`).

<details>
<summary><b>Run backend (Windows PowerShell)</b></summary>

```powershell
cd agent-server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

</details>

<details>
<summary><b>Run backend (macOS/Linux)</b></summary>

```bash
cd agent-server
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

</details>

Backend URLs:

- API root: `http://localhost:8000/`
- Health: `http://localhost:8000/health`
- Swagger docs: `http://localhost:8000/docs`

### 2) Seed demo data (optional but recommended)

```powershell
cd agent-server
.\.venv\Scripts\Activate.ps1
python scripts/populate_all.py
```

### 3) Frontend (Next.js)

Create `client/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

<details>
<summary><b>Run frontend (pnpm)</b></summary>

```powershell
cd client
pnpm install
pnpm dev
```

</details>

Open:

- UI: `http://localhost:3000`
- Live demo: https://the-neural-network-operationand-ai.vercel.app/

---

## 📲 WhatsApp local deployment (Twilio + ngrok)

The backend exposes a Twilio-compatible endpoint:

- `POST /whatsapp/webhook`

Twilio requires a **public HTTPS URL**, so for local development we expose `localhost:8000` using **ngrok**.

### Step-by-step

1. Start the backend on port `8000`.
2. Start ngrok:

   ```bash
   ngrok http 8000
   ```

3. Copy the **HTTPS** forwarding URL (example):
   - `https://xxxx-xx-xx-xx.ngrok-free.app`
4. In Twilio Console (WhatsApp Sandbox or your approved WhatsApp sender), set the webhook URL to:
   - `https://xxxx-xx-xx-xx.ngrok-free.app/whatsapp/webhook`
   - Method: `POST`

### Verify

- `GET http://localhost:8000/whatsapp/status`

---

## 🧪 Try the API (cURL)

### Consumer chat

```bash
curl -X POST http://localhost:8000/api/chat/consumer \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Hi! What kitchen appliances are in stock?\"}"
```

### Orders stats

```bash
curl http://localhost:8000/api/orders/stats
```

### Inventory low stock

```bash
curl http://localhost:8000/api/inventory/low-stock
```

### Leads (demo workflow)

```bash
# load demo leads
curl -X POST http://localhost:8000/api/leads/load-demo

# set sales context
curl -X POST http://localhost:8000/api/leads/context \
  -H "Content-Type: application/json" \
  -d "{\"context\":\"We offer an MSME operations dashboard with AI agents for order + inventory automation\"}"

# start outreach sequence
curl -X POST http://localhost:8000/api/leads/start
```

---

## 🛠️ Troubleshooting

<details>
<summary><b>Frontend can’t reach backend</b></summary>

- Confirm `client/.env.local` contains `NEXT_PUBLIC_API_URL=http://localhost:8000`.
- Confirm backend is running and `CORS_ORIGINS` includes `http://localhost:3000`.

</details>

<details>
<summary><b>MongoDB connection errors</b></summary>

- Confirm MongoDB is running and `MONGODB_URI` is correct.
- If using Docker, ensure you mapped ports: `-p 27017:27017`.

</details>

<details>
<summary><b>LLM replies are failing / empty</b></summary>

- Set `GEMINI_API_KEY` in `agent-server/.env`.

</details>

<details>
<summary><b>Twilio webhook errors</b></summary>

- Twilio sends `application/x-www-form-urlencoded` fields `From` and `Body`.
- Use the ngrok **HTTPS** URL (not HTTP) and the exact path `/whatsapp/webhook`.

</details>

---

## 🗺️ Repo map

- `agent-server/` — FastAPI API + agent graph + WhatsApp webhook + MongoDB models
  - `main.py` — FastAPI entrypoint
  - `whatsapp.py` — Twilio webhook routes
  - `agents/graph.py` — LangGraph workflow
  - `agents/leads_agent.py` — Leads outreach + qualification agent
  - `scripts/` — demo data population scripts
- `client/` — Next.js dashboard
  - `lib/api.ts` — API client (uses `NEXT_PUBLIC_API_URL`)
