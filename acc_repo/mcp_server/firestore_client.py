"""
Firestore client wrapper.

If USE_FIRESTORE=1 in the environment, talks to real Cloud Firestore.
Otherwise falls back to an in-memory dict so the team can run everything
locally without a GCP project.

The in-memory store keeps the same API surface as the Firestore client
methods we actually use (set, get, update, delete, stream).
"""
from __future__ import annotations

import os
import threading
import time
import uuid
from typing import Any, Dict, Iterable, List, Optional

USE_FIRESTORE = os.getenv("USE_FIRESTORE", "0") == "1"


# ---------- in-memory fallback ----------

class _InMemoryDoc:
    def __init__(self, store: Dict[str, dict], doc_id: str):
        self._store = store
        self.id = doc_id

    def set(self, data: dict, merge: bool = False) -> None:
        if merge and self.id in self._store:
            self._store[self.id].update(data)
        else:
            self._store[self.id] = dict(data)

    def update(self, data: dict) -> None:
        if self.id not in self._store:
            raise KeyError(f"document {self.id} does not exist")
        self._store[self.id].update(data)

    def get(self):
        data = self._store.get(self.id)
        return _InMemorySnapshot(self.id, data)

    def delete(self) -> None:
        self._store.pop(self.id, None)


class _InMemorySnapshot:
    def __init__(self, doc_id: str, data: Optional[dict]):
        self.id = doc_id
        self._data = data

    @property
    def exists(self) -> bool:
        return self._data is not None

    def to_dict(self) -> Optional[dict]:
        return dict(self._data) if self._data else None


class _InMemoryCollection:
    def __init__(self, store: Dict[str, dict]):
        self._store = store

    def document(self, doc_id: Optional[str] = None) -> _InMemoryDoc:
        if doc_id is None:
            doc_id = str(uuid.uuid4())
        return _InMemoryDoc(self._store, doc_id)

    def stream(self) -> Iterable[_InMemorySnapshot]:
        for doc_id, data in list(self._store.items()):
            yield _InMemorySnapshot(doc_id, data)


class _InMemoryDB:
    _lock = threading.Lock()
    _collections: Dict[str, Dict[str, dict]] = {}

    def collection(self, name: str) -> _InMemoryCollection:
        with self._lock:
            if name not in self._collections:
                self._collections[name] = {}
            return _InMemoryCollection(self._collections[name])


# ---------- public factory ----------

def get_db():
    """Return a Firestore client or an in-memory stand-in."""
    if USE_FIRESTORE:
        from google.cloud import firestore  # noqa: WPS433 (lazy import on purpose)

        return firestore.Client()
    return _InMemoryDB()


# ---------- helpers used by the tools ----------

def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
