"""
fetch_jobs MCP tool.

Reads a list of mock internship/job postings from data/mock_jobs.json
and applies optional filters (role, location, keyword).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

# Locate data/mock_jobs.json relative to the repo root.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_MOCK_JOBS_PATH = Path(os.getenv("MOCK_JOBS_PATH", _REPO_ROOT / "data" / "mock_jobs.json"))


def _load_jobs() -> List[dict]:
    if not _MOCK_JOBS_PATH.exists():
        return []
    with open(_MOCK_JOBS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_jobs(
    role: Optional[str] = None,
    location: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 20,
) -> List[dict]:
    """
    Return job postings that match the provided filters.

    Args:
        role: filter by role slug (e.g., "security", "software-engineering").
        location: case-insensitive substring match on job location.
        keyword: case-insensitive substring match on company, title, or job keywords.
        limit: max number of results to return.

    Returns:
        A list of job dicts with id, company, title, location, role, url, keywords.
    """
    jobs = _load_jobs()
    out: List[dict] = []
    role_l = role.lower().strip() if role else None
    loc_l = location.lower().strip() if location else None
    kw_l = keyword.lower().strip() if keyword else None

    for job in jobs:
        if role_l and job.get("role", "").lower() != role_l:
            continue
        if loc_l and loc_l not in job.get("location", "").lower():
            continue
        if kw_l:
            haystack = " ".join([
                job.get("company", ""),
                job.get("title", ""),
                " ".join(job.get("keywords", [])),
            ]).lower()
            if kw_l not in haystack:
                continue
        out.append(job)
        if len(out) >= limit:
            break
    return out
