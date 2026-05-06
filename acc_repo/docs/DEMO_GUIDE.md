# Demo Video Script & Trace/Logs Capture Guide

This is the playbook for producing the two remaining capstone deliverables:

  1. **System Trace & Logs** — a screenshot showing one user request flow
     through Orchestrator → Specialist → MCP.
  2. **Narrated Demo Video** — a 5-minute Zoom recording covering the
     same scenario end-to-end.

---

## Part 1 — Capturing the trace screenshot

You have two good options. Pick whichever your stack supports.

### Option A (easier): ADK web UI trace panel

If you used `adk web agents/supervisor` to run locally (or against
Cloud Run), the ADK web interface includes a "Trace" tab that shows the
agent loop step by step.

  1. Start the MCP server (local or Cloud Run).
  2. Start the agents: `adk web agents/supervisor`.
  3. In the chat, paste this exact prompt so it's reproducible:

         Help me manage my Spring 2026 internship search.
         First, find security internships in Richmond, VA.
         Then save the Federal Reserve one and mark it as applied.

  4. Wait for the agent to finish its full reply.
  5. Click the **Trace** tab on the right.
  6. Expand the entries so you can see, in order:
       - `supervisor` LLM call (decided to delegate)
       - `career_specialist` AgentTool call    ← this is the A2A handoff
       - `fetch_jobs` MCP tool call
       - `save_job` MCP tool call
       - `update_status` MCP tool call
       - `supervisor` final response
  7. Take a full-window screenshot. Save as
     `docs/trace_screenshot.png`.

### Option B (production-grade): Cloud Trace + Cloud Logging

If you've deployed to Cloud Run and Vertex AI:

  1. In Cloud Console go to **Observability → Trace**.
  2. Run the same prompt above against the deployed Supervisor.
  3. Find the trace whose root is the supervisor request. Open it.
  4. The waterfall should show:
       - supervisor span
       - agent_tool: career_specialist span (A2A handoff)
       - mcp_tool: fetch_jobs span
       - mcp_tool: save_job span
       - mcp_tool: update_status span
  5. Take a full-window screenshot of the waterfall.
  6. (Bonus) Open **Logging → Logs Explorer**, filter on the same trace
     ID, and grab a second screenshot showing the structured log lines
     emitted by `acc-mcp` (`fetch_jobs role=security location=Richmond`,
     `save_job job-004`, `update_status job-004 -> applied`).

What the screenshot must prove (rubric language):
  - A single user request entered the Supervisor.
  - The Supervisor delegated to the Career Specialist.
  - The Specialist called MCP tools on Cloud Run.

Annotate the screenshot lightly (arrows / numbered callouts) before
submitting so the grader can follow the flow at a glance.

---

## Part 2 — 5-minute narrated demo video

Record on Zoom with screen share + your microphones. Aim for **4:30 to
5:00** total. Both team members should speak (Prince and Ribin can split
the script roughly in half — suggested split shown below).

### Setup (do this *before* you hit record)

  - MCP server running and visible in one terminal window.
  - ADK web UI open in a browser, fresh chat.
  - Cloud Console open in a second tab on the **Logs Explorer** for the
    `acc-mcp` Cloud Run service (filter:
    `resource.type="cloud_run_revision" resource.labels.service_name="acc-mcp"`).
  - Architecture diagram open in a third tab.
  - Practice the script once unrecorded.

### Script

**[0:00 – 0:30]   Intro (Prince)**

> "Hi, we're Prince and Ribin from INFO 520. This is the Agentic Career
> Coach, our multi-agent internship-search assistant on Google Cloud.
> In the next five minutes we'll show how a single user request flows
> from the Supervisor agent, through an A2A handoff to the Career
> Specialist, down to MCP tools running on Cloud Run, and finally to
> Cloud Firestore — all using JSON-RPC 2.0 over Server-Sent Events
> instead of REST."

(Show architecture diagram on screen.)

**[0:30 – 1:00]   Architecture walkthrough (Ribin)**

> "On the left is our Supervisor in Vertex AI Agent Builder. It's the
> only agent the user talks to. The yellow note in the middle marks
> where prompt-based routing happens — Gemini reads the user's goal and
> decides whether to answer directly or hand off. On the right of the
> agent layer is the Career Specialist, our worker agent. It calls our
> MCP server on Cloud Run over SSE, and the MCP server reads and writes
> Cloud Firestore."

**[1:00 – 1:30]   Show the code briefly (Prince)**

(Switch to editor, scroll through `agents/supervisor/agent.py`.)

> "The Supervisor is twenty lines of Python. It exposes the Career
> Specialist as an `AgentTool`, which is what makes the A2A handoff
> explicit and traceable."

(Scroll to `mcp_server/server.py`.)

> "On the MCP side, we use FastMCP and decorate each function as a tool.
> The framework handles the JSON-RPC 2.0 envelope and the SSE transport
> for us — every tool call is `tools/list` discoverable at runtime."

**[1:30 – 3:30]   Live demo (alternate speakers)**

(Switch to ADK web UI, fresh session.)

  1. Type: **"Find security internships in Richmond, VA."**

     - Wait for response.
     - Open the Trace panel and point at the spans:
       supervisor → career_specialist → fetch_jobs.

  2. Type: **"Save the Federal Reserve job to my pipeline."**

     - Show the response.
     - Point at the new span: save_job.

  3. Type: **"Mark it as applied."**

     - Show the response.
     - Point at the update_status span.

  4. Type: **"Summarize my current pipeline."**

     - Show the response. Highlight that it includes one job in the
       "applied" bucket.
     - Point at the list_pipeline span.

(Switch to the Cloud Logs Explorer tab.)

> "And here are the structured logs from the MCP server showing each
> tool invocation in order — `fetch_jobs`, `save_job`, `update_status`,
> `list_pipeline`."

**[3:30 – 4:00]   Firestore check (Ribin)**

(Switch to Cloud Console → Firestore → Data tab.)

> "In Firestore, the `applications` collection now contains the saved
> job with status `applied`. This is being written and read through the
> MCP `sync_pipeline` tools, never directly from the agents."

**[4:00 – 4:45]   Why MCP (Prince)**

> "The point of using MCP rather than REST endpoints is that all of
> this — fetching jobs, saving them, updating status, summarizing — uses
> one wire format and one discovery mechanism. When we add a fourth tool
> later, the agents discover it automatically through `tools/list`. We
> don't have to redeploy the agent code or teach it new URL shapes."

**[4:45 – 5:00]   Wrap (Ribin)**

> "Source code, the architecture diagram, the data-communications
> reflection, and the deployment scripts are in the GitHub repository
> linked in the submission. Thanks for watching!"

### Recording checklist

  - [ ] Zoom set to record at 1080p, "record separate audio file" on.
  - [ ] Mic levels checked, no echo.
  - [ ] Notifications silenced (Slack, email, phone).
  - [ ] No personal info visible on screen (other tabs, bookmarks).
  - [ ] Browser zoomed enough that text is readable on a phone.
  - [ ] Trim Zoom's auto-generated waiting-room slide off the front.

### What to upload

  - `demo.mp4` — the recording.
  - `docs/trace_screenshot.png` — the trace capture.
  - This repo, pushed to GitHub, link in the submission form.
