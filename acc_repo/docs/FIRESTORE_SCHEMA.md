# Firestore Schema

The ACC system uses **Cloud Firestore (Native mode)** as the central state
store for the user's internship search pipeline. The schema is intentionally
flat and simple so the MCP tools can read and write it without joins.

## Collection: `applications`

Each document represents one job that the user has decided to track.
Document IDs match the `jobId` from the Job Source so that `save_job`,
`update_status`, `list_pipeline`, and `delete_job` are all O(1) lookups.

| Field       | Type     | Notes                                                       |
|-------------|----------|-------------------------------------------------------------|
| `jobId`     | string   | Stable identifier from the Job Source (matches document ID) |
| `company`   | string   | Company name                                                |
| `title`     | string   | Position title                                              |
| `location`  | string   | Free-form location string                                   |
| `url`       | string   | Posting URL                                                 |
| `status`    | string   | `saved` / `applied` / `interviewing` / `offer` / `rejected` / `withdrawn` |
| `savedAt`   | string   | ISO-8601 UTC, set on first save                             |
| `updatedAt` | string   | ISO-8601 UTC, updated on every status change                |
| `notes`     | string   | Free-form notes                                             |
| `deadline`  | string   | Optional ISO-8601 date for the application deadline         |

## Status state machine

```
   saved ──► applied ──► interviewing ──► offer
     │          │              │            │
     └──────────┴──────────────┴───► rejected
                                  └──► withdrawn
```

`update_status` validates the target value but does not enforce
transitions, so the user can recover from mistakes (e.g. moving an
"applied" job back to "saved").

## Why a single collection?

We considered splitting `jobs` and `applications` into two collections
(jobs as a catalogue, applications as a per-user join table). For this
single-user capstone the join table adds complexity without value, so we
inline the job fields onto the application document. If ACC ever serves
multiple users, the natural extension is a `users/{uid}/applications`
sub-collection with the same field set.
