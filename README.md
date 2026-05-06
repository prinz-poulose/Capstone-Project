# Agentic Career Coach (ACC)

INFO 520 Capstone — **Prince and Ribin**
Virginia Commonwealth University, School of Business

A multi-agent internship-search assistant built on Google Cloud Platform.
A **Supervisor** agent talks to the user and delegates work via **A2A
handoff** to a **Career Specialist** agent, which calls **MCP tools** on a
**Cloud Run** service that reads/writes **Cloud Firestore**.

The MCP server speaks **JSON-RPC 2.0 over Server-Sent Events (SSE)**,
not REST.

## Architecture

```
   User
    │  HTTPS chat
    ▼
┌─────────────────────────── Vertex AI Agent Builder ───────────────────────────┐
│  Supervisor (Lead Orchestrator) ──── A2A handoff ───►  Career Specialist     │
│  └── prompt-based routing decides whether to delegate                        │
└──────────────────────────────────────────────┬───────────────────────────────┘
                                               │  JSON-RPC 2.0 over SSE
                                               ▼
                              ┌────── Cloud Run ──────┐
                              │  MCP Server (Python)  │
                              │  fetch_jobs           │
                              │  sync_pipeline tools  │
                              └──────────┬────────────┘
                                         │  CRUD
                                         ▼
                                ┌─── Cloud Firestore ───┐
                                │  applications         │
                                └───────────────────────┘
```

See `docs/FIRESTORE_SCHEMA.md` for the data model and
`ACC_Architecture_Diagram.pdf` for the full diagram.

## Repo layout

```
acc/
├── agents/
│   ├── supervisor/agent.py     Lead Orchestrator (user-facing)
│   └── specialist/agent.py     Career Specialist (calls MCP tools)
├── mcp_server/
│   ├── server.py               FastMCP server, SSE transport
│   ├── tools/
│   │   ├── fetch_jobs.py       Reads data/mock_jobs.json with filters
│   │   └── sync_pipeline.py    CRUD on Firestore (or in-memory)
│   ├── firestore_client.py     Firestore wrapper + in-memory fallback
│   └── Dockerfile              Container image for Cloud Run
├── data/mock_jobs.json         Mock internship listings
├── scripts/
│   ├── smoke_test.py           Runs the tool layer locally, no LLM
│   └── deploy_mcp.sh           Builds + deploys MCP server to Cloud Run
└── docs/FIRESTORE_SCHEMA.md
```

## Quick start (local, no GCP required)

The MCP server has a built-in in-memory fallback for Firestore, so the
whole tool layer runs locally with no cloud setup.

```bash
# 1. Create a virtualenv
python3 -m venv .venv && source .venv/bin/activate

# 2. Install MCP server deps
pip install -r mcp_server/requirements.txt

# 3. Run the smoke test (no LLM, no network, no GCP)
python -m scripts.smoke_test
```

You should see `ALL CHECKS PASSED` at the bottom.

## Run the MCP server locally

```bash
# In one terminal:
python -m mcp_server.server
# starts an SSE server on http://localhost:8080/sse
```

Sanity-check it from another terminal:

```bash
curl -N http://localhost:8080/sse
# you should see an SSE stream open and stay open (Ctrl-C to exit)
```

## Run the agents locally

```bash
# In a second terminal (with the MCP server running):
pip install -r agents/requirements.txt
export MCP_SERVER_URL=http://localhost:8080/sse
export GOOGLE_API_KEY=...      # for Gemini, see https://aistudio.google.com
adk web agents/supervisor      # opens a local chat UI
```

In the chat, try:

  - "Find security internships in Richmond"
  - "Save job-004 to my pipeline"
  - "Mark job-004 as applied"
  - "Summarize my pipeline"

The Supervisor decides whether to hand off and the Career Specialist
calls MCP tools. The ADK web UI shows the full trace including each
A2A handoff and each MCP tool call.

## Deploy the MCP server to Cloud Run

Prereqs: a GCP project with billing, Firestore (Native mode) created,
and `gcloud` authenticated.

```bash
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1
./scripts/deploy_mcp.sh
```

The script prints the deployed `MCP_SERVER_URL`. Set that env var on the
agent side and the agents now talk to Cloud Run instead of localhost.

## Environment variables

| Variable           | Where      | Default                          | Purpose                                        |
|--------------------|------------|----------------------------------|------------------------------------------------|
| `PORT`             | MCP server | `8080`                           | HTTP port (Cloud Run sets this automatically)  |
| `USE_FIRESTORE`    | MCP server | `0`                              | `1` = real Firestore, `0` = in-memory fallback |
| `LOG_LEVEL`        | MCP server | `INFO`                           |                                                |
| `MOCK_JOBS_PATH`   | MCP server | `data/mock_jobs.json`            | Override the job source                        |
| `MCP_SERVER_URL`   | Agents     | `http://localhost:8080/sse`      | URL the Specialist connects to                 |
| `SUPERVISOR_MODEL` | Agents     | `gemini-2.0-flash`               |                                                |
| `SPECIALIST_MODEL` | Agents     | `gemini-2.0-flash`               |                                                |
| `GOOGLE_API_KEY`   | Agents     | —                                | Required by ADK to call Gemini                 |

## What's in this submission

This repository covers Submission 2 of the capstone:

  - [x] Multi-Agent Source Code (this repo)
  - [x] Agent definitions: Supervisor + Career Specialist
  - [x] MCP server with `fetch_jobs` and `sync_pipeline`
  - [x] README with run + deploy steps
  - [x] Firestore schema doc

Submission 1 deliverables (architecture diagram + data-comm reflection)
live in `docs/`.

## AI use citation

Anthropic. (2026, May 5). *Assisted scaffolding of the multi-agent source
code, MCP server, and README.* [Generative AI chat]. Claude.

Authors: **Prince** and **Ribin** — INFO 520, Spring 2026.
