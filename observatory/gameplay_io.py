"""Shared gameplay transport and logging; model evaluation remains independent."""
from contextlib import nullcontext
from datetime import datetime, timezone
import json
from uuid import uuid4

import httpx


def post_chat(request, client=None):
    """Close clients we create, but leave injected clients owned by the caller."""
    context = httpx.Client(timeout=30, trust_env=False) if client is None else nullcontext(client)
    with context as connection:
        return connection.post('http://127.0.0.1:11434/api/chat', json=request)


def save_record(directory, record, warning):
    try:
        directory.mkdir(parents=True, exist_ok=True)
        name = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid4().hex + '.json'
        (directory / name).write_text(json.dumps(record, indent=2), encoding='utf-8')
    except OSError:
        print(warning)
