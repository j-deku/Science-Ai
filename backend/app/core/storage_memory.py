# app/core/storage_memory.py
import json
import os
from typing import List, Dict, Optional

import redis

REDIS_URL = os.getenv("REDIS_URL", "")
USE_REDIS = bool(REDIS_URL)

if USE_REDIS:
    r = redis.from_url(REDIS_URL, decode_responses=True)
else:
    r = None
    _INMEMORY = {}

def remember(session_id: str, q: str, a: str):
    record = {"q": q, "a": a}
    if USE_REDIS:
        r.rpush(f"chat:{session_id}", json.dumps(record))
    else:
        _INMEMORY.setdefault(session_id, []).append(record)

def get_history(session_id: str, limit: int = 50):
    if USE_REDIS:
        raw = r.lrange(f"chat:{session_id}", -limit, -1)
        return [json.loads(x) for x in raw]
    else:
        return _INMEMORY.get(session_id, [])[-limit:]

def clear_history(session_id: str):
    if USE_REDIS:
        r.delete(f"chat:{session_id}")
    else:
        _INMEMORY.pop(session_id, None)
