"""Minimal stdin/stdout bridge for the first Generative GLaDOS PoC.

One JSON object per line in; one JSON object per line out.
This intentionally has no model dependency yet: it proves the event contract first.
"""

from __future__ import annotations

import json
import sys
from typing import Any


def react(event: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic placeholder response for bridge testing."""
    event_name = str(event.get("event", "unknown"))
    return {
        "speak": True,
        "text": f"[PoC placeholder] Observed event: {event_name}.",
        "source_event": event_name,
    }


def main() -> None:
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            event = json.loads(raw)
            if not isinstance(event, dict):
                raise ValueError("event must be a JSON object")
            response = react(event)
        except (json.JSONDecodeError, ValueError) as exc:
            response = {"speak": False, "error": str(exc)}
        print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
