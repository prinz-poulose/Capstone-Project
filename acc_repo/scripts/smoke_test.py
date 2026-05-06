"""
Local smoke test: exercise fetch_jobs and sync_pipeline directly
(without an LLM and without any cloud services).

Run from repo root:
    python -m scripts.smoke_test
"""
from __future__ import annotations

import json

from mcp_server.tools import fetch_jobs as fj
from mcp_server.tools import sync_pipeline as sp


def banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main() -> None:
    banner("1) fetch_jobs - all security roles in Richmond")
    jobs = fj.fetch_jobs(role="security", location="Richmond")
    print(json.dumps(jobs, indent=2))
    assert any(j["company"] == "Federal Reserve Bank of Richmond" for j in jobs), (
        "expected the FRB Richmond cybersecurity intern to match"
    )

    banner("2) save_job - put job-002 (Markel) in the pipeline")
    saved = sp.save_job(
        job_id="job-002",
        company="Markel",
        title="Information Security Intern",
        location="Glen Allen, VA",
        url="https://example.com/markel/security-intern",
        notes="good local fit",
    )
    print(json.dumps(saved, indent=2))
    assert saved["status"] == "saved"

    banner("3) update_status - move job-002 to 'applied'")
    updated = sp.update_status("job-002", "applied", notes="submitted on portal")
    print(json.dumps(updated, indent=2))
    assert updated["status"] == "applied"

    banner("4) save_job - also save job-004 (FRB cyber)")
    sp.save_job(
        job_id="job-004",
        company="Federal Reserve Bank of Richmond",
        title="Cybersecurity Intern",
        location="Richmond, VA",
        url="https://example.com/frbr/cyber-intern",
    )

    banner("5) list_pipeline - everything currently saved")
    pipeline = sp.list_pipeline()
    print(json.dumps(pipeline, indent=2))
    assert len(pipeline) == 2, f"expected 2 jobs in pipeline, got {len(pipeline)}"

    banner("6) list_pipeline - only status='applied'")
    applied_only = sp.list_pipeline(status="applied")
    print(json.dumps(applied_only, indent=2))
    assert len(applied_only) == 1
    assert applied_only[0]["jobId"] == "job-002"

    banner("7) delete_job - remove job-004")
    result = sp.delete_job("job-004")
    print(json.dumps(result, indent=2))
    assert result["deleted"] is True

    banner("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
