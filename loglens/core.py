"""Parse supported log records and aggregate errors without retaining all rows."""
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re

TEXT = re.compile(r"^(\S+)\s+(DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL)\s+(\S+)\s+(.+)$", re.I)
LEVELS = {"WARN": "WARNING", "FATAL": "CRITICAL"}
VALID = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
UUID = re.compile(r"\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b", re.I)
NUMBER = re.compile(r"\b\d+(?:\.\d+)?\b")

@dataclass(frozen=True)
class Entry:
    timestamp: datetime
    level: str
    service: str
    message: str

def parse_line(line):
    if line.lstrip().startswith("{"):
        data = json.loads(line)
        timestamp, level, service, message = (data[k] for k in ("timestamp", "level", "service", "message"))
    else:
        match = TEXT.fullmatch(line.strip())
        if not match:
            raise ValueError("Expected ISO timestamp, level, service and message")
        timestamp, level, service, message = match.groups()
    if not all(isinstance(v, str) and v.strip() for v in (timestamp, level, service, message)):
        raise ValueError("Record fields must be nonempty strings")
    level = LEVELS.get(level.upper(), level.upper())
    if level not in VALID:
        raise ValueError("Unsupported level")
    stamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("Timestamp must include an offset or Z")
    return Entry(stamp.astimezone(timezone.utc), level, service, message)

def fingerprint(message):
    """Optional heuristic: collapse UUIDs and numbers, retaining all other text."""
    return NUMBER.sub("<number>", UUID.sub("<uuid>", message))

def analyze(lines, normalize=False):
    levels, services, timeline, groups = Counter(), Counter(), Counter(), Counter()
    malformed, total, first, last = [], 0, None, None
    skipped = 0
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        # Keep line errors isolated so one damaged record does not discard a file.
        try:
            if len(line) > 65536:
                raise ValueError("Line exceeds 64 KiB character limit")
            entry = parse_line(line)
        except (ValueError, KeyError, TypeError, OverflowError):
            skipped += 1
            if len(malformed) < 20:
                malformed.append(number)
            continue
        total += 1
        levels[entry.level] += 1
        services[entry.service] += 1
        first = min(first, entry.timestamp) if first else entry.timestamp
        last = max(last, entry.timestamp) if last else entry.timestamp
        if entry.level in {"ERROR", "CRITICAL"}:
            minute = entry.timestamp.replace(second=0, microsecond=0).isoformat()
            timeline[minute] += 1
            text = fingerprint(entry.message) if normalize else entry.message
            groups[(entry.service, entry.level, text)] += 1
    errors = levels["ERROR"] + levels["CRITICAL"]
    return {
        "total": total, "errors": errors, "error_rate": round(errors / total * 100, 2) if total else 0,
        "skipped": skipped, "malformed_lines": malformed, "normalized": normalize,
        "first": first.isoformat() if first else None, "last": last.isoformat() if last else None,
        "levels": dict(sorted(levels.items())), "services": dict(sorted(services.items())),
        "timeline": [{"minute": k, "count": v} for k, v in sorted(timeline.items())],
        "groups": [{"service": k[0], "level": k[1], "message": k[2], "count": count}
                   for k, count in sorted(groups.items(), key=lambda pair: (-pair[1], pair[0]))]
    }
