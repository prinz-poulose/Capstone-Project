"""
ACC MCP server.

Wraps fetch_jobs and sync_pipeline as MCP tools and serves them over
JSON-RPC 2.0 transported on Server-Sent Events (SSE).

Run locally:
    python -m mcp_server.server
which starts an HTTP server on $PORT (default 8080) with:
    GET  /sse        - SSE stream
    POST /messages   - client-to-server JSON-RPC messages
    GET  /health     - liveness probe for Cloud Run

For local agent testing, point the ADK agent at http://localhost:8080/sse
"""
from __future__ import annotations

import logging
import os
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

from mcp_server.tools import fetch_jobs as fetch_jobs_tool
from mcp_server.tools import sync_pipeline as pipeline_tool

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("acc-mcp")

mcp = FastMCP("acc-mcp", instructions=(
    "Agentic Career Coach MCP server. "
    "Use fetch_jobs to discover internships and sync_pipeline tools "
    "(save_job, update_status, list_pipeline, delete_job) to track them."
))


# ---------- fetch_jobs ----------

@mcp.tool()
def fetch_jobs(
    role: Optional[str] = None,
    location: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 20,
) -> List[dict]:
    """
    Fetch internship/job postings.

    Args:
        role: filter by role slug (e.g. 'security', 'software-engineering').
        location: substring match on the location.
        keyword: substring match on company, title, or job keywords.
        limit: maximum results to return (default 20).
    """
    log.info("fetch_jobs role=%s location=%s keyword=%s", role, location, keyword)
    return fetch_jobs_tool.fetch_jobs(role=role, location=location, keyword=keyword, limit=limit)


# ---------- sync_pipeline ----------

@mcp.tool()
def save_job(
    job_id: str,
    company: str,
    title: str,
    location: str,
    url: str,
    notes: Optional[str] = None,
    deadline: Optional[str] = None,
) -> dict:
    """Save a job to the internship pipeline with status='saved'."""
    log.info("save_job %s (%s)", job_id, company)
    return pipeline_tool.save_job(job_id, company, title, location, url, notes, deadline)


@mcp.tool()
def update_status(job_id: str, status: str, notes: Optional[str] = None) -> dict:
    """
    Update the application status of a saved job.
    Valid statuses: saved, applied, interviewing, offer, rejected, withdrawn.
    """
    log.info("update_status %s -> %s", job_id, status)
    return pipeline_tool.update_status(job_id, status, notes)


@mcp.tool()
def list_pipeline(status: Optional[str] = None) -> List[dict]:
    """List every job in the pipeline, optionally filtered by status."""
    log.info("list_pipeline status=%s", status)
    return pipeline_tool.list_pipeline(status)


@mcp.tool()
def delete_job(job_id: str) -> dict:
    """Remove a job from the pipeline."""
    log.info("delete_job %s", job_id)
    return pipeline_tool.delete_job(job_id)


# ---------- entrypoint ----------

def main() -> None:
    port = int(os.getenv("PORT", "8080"))
    log.info("starting acc-mcp on port %d (USE_FIRESTORE=%s)", port, os.getenv("USE_FIRESTORE", "0"))
    # FastMCP picks up host/port from env or kwargs. Use SSE transport
    # so the Vertex AI agent layer can stream JSON-RPC messages.
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = port
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
