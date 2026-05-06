"""
sync_pipeline MCP tool.

Performs CRUD on the internship-search pipeline:
  - save_job:        save a job into the pipeline
  - update_status:   mark a job's application status
                     (saved -> applied -> interviewing -> offer/rejected)
  - list_pipeline:   list every job in the pipeline
  - delete_job:      remove a job from the pipeline

Storage backend: Cloud Firestore (when USE_FIRESTORE=1) or
an in-memory dict (default, for local development).

Collections:
  applications   { jobId, company, title, location, url,
                   status, savedAt, updatedAt, notes, deadline }
"""
from __future__ import annotations

from typing import List, Literal, Optional

from mcp_server.firestore_client import get_db, now_iso

VALID_STATUSES = {"saved", "applied", "interviewing", "offer", "rejected", "withdrawn"}
COLLECTION = "applications"


def save_job(
    job_id: str,
    company: str,
    title: str,
    location: str,
    url: str,
    notes: Optional[str] = None,
    deadline: Optional[str] = None,
) -> dict:
    """Save a job into the pipeline with status='saved'."""
    db = get_db()
    doc = db.collection(COLLECTION).document(job_id)
    payload = {
        "jobId": job_id,
        "company": company,
        "title": title,
        "location": location,
        "url": url,
        "status": "saved",
        "savedAt": now_iso(),
        "updatedAt": now_iso(),
        "notes": notes or "",
        "deadline": deadline or "",
    }
    doc.set(payload)
    return payload


def update_status(
    job_id: str,
    status: Literal["saved", "applied", "interviewing", "offer", "rejected", "withdrawn"],
    notes: Optional[str] = None,
) -> dict:
    """Update the application status of a saved job."""
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status '{status}'. valid: {sorted(VALID_STATUSES)}")

    db = get_db()
    doc = db.collection(COLLECTION).document(job_id)
    snap = doc.get()
    if not snap.exists:
        raise KeyError(f"job {job_id} is not in the pipeline. Save it first.")

    existing = snap.to_dict() or {}
    update = {"status": status, "updatedAt": now_iso()}
    if notes is not None:
        update["notes"] = notes
    existing.update(update)
    doc.set(existing)
    return existing


def list_pipeline(status: Optional[str] = None) -> List[dict]:
    """Return all jobs in the pipeline, optionally filtered by status."""
    db = get_db()
    out: List[dict] = []
    for snap in db.collection(COLLECTION).stream():
        data = snap.to_dict() or {}
        if status and data.get("status") != status:
            continue
        out.append(data)
    # Sort newest update first.
    out.sort(key=lambda d: d.get("updatedAt", ""), reverse=True)
    return out


def delete_job(job_id: str) -> dict:
    """Remove a job from the pipeline."""
    db = get_db()
    doc = db.collection(COLLECTION).document(job_id)
    snap = doc.get()
    if not snap.exists:
        return {"deleted": False, "jobId": job_id}
    doc.delete()
    return {"deleted": True, "jobId": job_id}
