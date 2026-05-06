"""
Career Specialist agent ("Worker Agent").

This agent is NOT exposed to the user. It is invoked by the Supervisor via
A2A handoff and does the heavy lifting:
  - calling fetch_jobs / sync_pipeline tools on the MCP server
  - producing structured summaries of pipeline state

The agent uses MCPToolset to discover tools at runtime over the MCP server's
JSON-RPC over SSE channel; we never hardcode tool signatures here.
"""
from __future__ import annotations

import os

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, SseServerParams

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080/sse")
MODEL = os.getenv("SPECIALIST_MODEL", "gemini-2.0-flash")

SPECIALIST_INSTRUCTION = """
You are the Career Specialist for the Agentic Career Coach (ACC).
You receive structured tasks from the Supervisor and respond with structured
results. You are a worker agent and never speak directly to the end user.

Your responsibilities:
  1. Use the `fetch_jobs` tool to discover internships when the task asks
     for new opportunities. Apply the filters that match the user's intent:
     role, location, keyword.
  2. Use the `save_job`, `update_status`, `list_pipeline`, and `delete_job`
     tools to manage the user's internship pipeline.
  3. When asked to summarize pipeline state, call `list_pipeline` first and
     produce a concise summary grouped by status
     (saved / applied / interviewing / offer / rejected).

Hard rules:
  - Always call a tool when the task requires data; do not invent jobs.
  - Return structured JSON-friendly content the Supervisor can re-format.
  - If a tool call fails, surface the error in your response so the
    Supervisor can decide what to tell the user.
"""

career_specialist = LlmAgent(
    name="career_specialist",
    model=MODEL,
    description=(
        "Worker agent that fetches internship listings and updates the "
        "internship pipeline through the MCP server."
    ),
    instruction=SPECIALIST_INSTRUCTION,
    tools=[
        # MCP toolset auto-discovers tools at startup via tools/list.
        MCPToolset(
            connection_params=SseServerParams(url=MCP_SERVER_URL),
        ),
    ],
)
