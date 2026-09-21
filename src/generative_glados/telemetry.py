"""Read strictly framed Portal 2 observations; no models, network, or game writes."""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Any, Iterator

PREFIX = b"[GG_EVENT] "
MAX_LINE = 16384
EVENTS = {"bridge_attached", "laser_powered", "laser_unpowered", "hint_requested", "probe_stopped"}
FIELDS = {"schema_version", "origin", "event", "map", "run_id", "seq", "game_time", "data"}


def validate(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != FIELDS:
        raise ValueError("invalid event fields")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise ValueError("unsupported schema")
    if value["origin"] not in ("engine", "synthetic") or value["event"] not in EVENTS:
        raise ValueError("invalid origin or event")
    for key in ("map", "run_id"):
        if not isinstance(value[key], str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value[key]):
            raise ValueError(f"invalid {key}")
    if type(value["seq"]) is not int or not 1 <= value["seq"] <= 2147483647:
        raise ValueError("invalid sequence")
    t = value["game_time"]
    if type(t) not in (int, float) or not math.isfinite(t) or t < 0:
        raise ValueError("invalid game time")
    data = value["data"]
    if not isinstance(data, dict) or set(data) != {"target", "powered", "laser_hook"}:
        raise ValueError("invalid data fields")
    if data["target"] not in (None, "catcher_1"):
        raise ValueError("unexpected target")
    if data["powered"] is not None and type(data["powered"]) is not bool:
        raise ValueError("powered must be boolean or null")
    if type(data["laser_hook"]) is not bool:
        raise ValueError("laser_hook must be boolean")
    if value["event"].startswith("laser_"):
        if data["target"] != "catcher_1" or not data["laser_hook"]:
            raise ValueError("laser event without a hook")
        if data["powered"] is not (value["event"] == "laser_powered"):
            raise ValueError("contradictory laser state")
    return value


def parse_line(line: bytes) -> dict[str, Any] | None:
    """Ignore ordinary console text, including echoed commands containing the prefix."""
    if not line.startswith(PREFIX):
        return None
    if len(line) > MAX_LINE:
        raise ValueError("oversized event")
    try:
        value = json.loads(line[len(PREFIX):].decode("utf-8"))
        return validate(value)
    except (ValueError, TypeError, UnicodeError, RecursionError, OverflowError) as exc:
        raise ValueError("malformed framed event") from exc


class EventStream:
    """Bounded newline decoder. A partial record is not an event."""
    def __init__(self) -> None:
        self.buffer = bytearray()
        self.dropping = False
        self.rejected = 0

    def feed(self, chunk: bytes) -> Iterator[dict[str, Any]]:
        # splitlines() would treat non-newline control bytes as record boundaries.
        parts = chunk.split(b"\n")
        for index, part in enumerate(parts):
            complete = index < len(parts) - 1
            if not self.dropping:
                if len(self.buffer) + len(part) > MAX_LINE:
                    self.rejected += 1
                    self.buffer.clear()
                    self.dropping = True
                else:
                    self.buffer.extend(part)
            if complete:
                if not self.dropping:
                    try:
                        event = parse_line(bytes(self.buffer).rstrip(b"\r"))
                        if event is not None:
                            yield event
                    except ValueError:
                        self.rejected += 1
                self.buffer.clear()
                self.dropping = False


def read_events(path: Path, *, follow: bool = False, from_end: bool = False) -> Iterator[dict[str, Any]]:
    """Follow a file without retaining the log; restart on observed truncation/rotation.

    This diagnostic tailer is not an exactly-once transport. Rapid truncate/regrow
    between polls may be missed. M2 must use run/sequence IDs and detect gaps.
    """
    stream = EventStream()
    offset = 0
    identity = None
    initialized = False
    warned = 0
    while True:
        try:
            stat = path.stat()
            current = (stat.st_dev, stat.st_ino)
            if not initialized:
                offset = stat.st_size if from_end else 0
                initialized = True
            elif current != identity or stat.st_size < offset:
                offset = 0
                stream = EventStream()
                warned = 0
                print("[GG] Log reset; consumers must start a new observation epoch.", file=sys.stderr)
            identity = current
            with path.open("rb") as source:
                source.seek(offset)
                while chunk := source.read(4096):
                    offset += len(chunk)
                    yield from stream.feed(chunk)
            if stream.rejected != warned:
                print(f"[GG] Rejected malformed/oversized records: {stream.rejected}", file=sys.stderr)
                warned = stream.rejected
        except FileNotFoundError:
            if not follow:
                raise
        if not follow:
            break
        time.sleep(0.1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--follow", action="store_true")
    parser.add_argument("--from-end", action="store_true")
    args = parser.parse_args()
    try:
        for event in read_events(args.log, follow=args.follow, from_end=args.from_end):
            print(json.dumps(event, ensure_ascii=False, allow_nan=False), flush=True)
    except KeyboardInterrupt:
        pass
    except (OSError, ValueError) as exc:
        parser.exit(1, f"[GG] {exc}\n")


if __name__ == "__main__":
    main()
