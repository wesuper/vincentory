#!/usr/bin/env python3
"""Validate presentation content and the machine-checkable READY gate.

Usage:
  python3 validate_content.py presentation.md handoff.json [working-state.json]
"""
import json
import re
import sys
from pathlib import Path


STATUSES = {"DRAFT", "REVIEW", "READY"}
READINESS = {"ready", "needs_review", "blocked"}
STAGES = {"INTAKE", "QUESTION_DEFINED", "SKELETON", "ENRICHED", "REVIEW", "READY"}
SLIDE_MARKER = re.compile(
    r"<!-- slide:id=([^\s]+)\s+role=([^\s]+)\s+chapter=([^\s]+)\s*-->"
)


def front_matter(md):
    if not md.startswith("---\n"):
        return {}
    end = md.find("\n---", 4)
    if end == -1:
        return {}
    result = {}
    for line in md[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def validate(md_path, handoff_path, state_path=None):
    md = Path(md_path).read_text(encoding="utf-8")
    handoff = json.loads(Path(handoff_path).read_text(encoding="utf-8"))
    state = None
    if state_path:
        state = json.loads(Path(state_path).read_text(encoding="utf-8"))

    errors = []
    fm = front_matter(md)
    matches = list(SLIDE_MARKER.finditer(md))
    ids = [m.group(1) for m in matches]
    planned_minutes = 0.0

    if len(ids) != len(set(ids)):
        errors.append("duplicate slide ids")
    if not ids:
        errors.append("no slides found")
    if ids != [s.get("slide_id") for s in handoff.get("slides", [])]:
        errors.append("handoff slide order differs")

    for field in ("title", "audience", "objective"):
        if not fm.get(field):
            errors.append(f"front matter missing {field}")

    duration = fm.get("duration_minutes")
    try:
        duration_value = float(duration) if duration else None
    except ValueError:
        duration_value = None
        errors.append("duration_minutes is not numeric")
    if duration_value is None:
        errors.append("front matter missing duration_minutes")

    status = fm.get("status", "")
    if status not in STATUSES:
        errors.append(f"invalid presentation status {status!r}")

    for i, match in enumerate(matches):
        chunk = md[match.end():matches[i + 1].start() if i + 1 < len(matches) else len(md)]
        slide_id = match.group(1)
        for req in ("> Takeaway:", "## Visible", "## Evidence",
                    "## Visual Intent", "## Speaker Notes",
                    "Purpose:", "Talk:", "Transition:"):
            if req not in chunk:
                errors.append(f"{slide_id} missing {req}")

        evidence = re.search(r"(?ms)^## Evidence\s*\n(.*?)(?=^## |\Z)", chunk)
        if evidence and not evidence.group(1).strip():
            errors.append(f"{slide_id} has empty Evidence")

        minutes = re.findall(r"(?m)^Minutes:\s*([0-9]+(?:\.[0-9]+)?)\s*$", chunk)
        if len(minutes) != 1:
            errors.append(f"{slide_id} must have exactly one numeric Minutes line")
        else:
            planned_minutes += float(minutes[0])

        talk = re.search(
            r"(?ms)^Talk:\s*\n(.*?)(?=^(?:Transition|Minutes|Cue|Interaction|Fallback):|\Z)",
            chunk,
        )
        if talk:
            lines = re.findall(r"(?m)^-\s+(.+)$", talk.group(1))
            if not 2 <= len(lines) <= 4:
                errors.append(f"{slide_id} talk count {len(lines)}")
            for line in lines:
                if len(line) > 40:
                    errors.append(f"{slide_id} talk >40 chars")

    if duration_value is not None and planned_minutes > duration_value * 0.9:
        errors.append(f"planned minutes {planned_minutes} exceeds 90% budget")

    readiness = handoff.get("readiness")
    if readiness not in READINESS:
        errors.append(f"invalid handoff readiness {readiness!r}")
    if "unresolved" not in handoff:
        errors.append("handoff missing unresolved")
    elif not isinstance(handoff["unresolved"], list):
        errors.append("handoff unresolved must be an array")

    expected_readiness = {"DRAFT": "needs_review", "REVIEW": "needs_review",
                          "READY": "ready"}
    if status in expected_readiness and readiness in READINESS:
        if expected_readiness[status] != readiness:
            errors.append("presentation status/readiness mismatch")

    stage = state.get("stage") if state else None

    statuses = set()
    if status in STATUSES:
        statuses.add(status)
    if stage in STAGES:
        mapped_status = "DRAFT" if stage in {
            "INTAKE", "QUESTION_DEFINED", "SKELETON"
        } else "REVIEW" if stage in {"ENRICHED", "REVIEW"} else "READY"
        statuses.add(mapped_status)
    if len(statuses) > 1:
        errors.append("stage/status mismatch: working-state stage and presentation status disagree")

    if status == "READY":
        if state is None:
            errors.append("READY requires working-state.json as third argument")
        else:
            stage = state.get("stage")
            if stage not in STAGES:
                errors.append(f"invalid working-state stage {stage!r}")
            elif stage != "READY":
                errors.append("READY requires working-state stage READY")
            if state.get("open_questions"):
                errors.append("READY requires empty working-state open_questions")

        if handoff.get("unresolved"):
            errors.append("READY requires empty handoff unresolved")

    return {
        "ok": not errors,
        "slides": len(ids),
        "planned_minutes": planned_minutes,
        "status": status,
        "readiness": readiness,
        "errors": errors,
        "gate_scope": "machine-checkable READY conditions only; evidence quality and downstream readiness still require human review",
    }


def main(argv):
    if len(argv) not in (3, 4):
        print(json.dumps({
            "ok": False,
            "errors": ["usage: validate_content.py presentation.md handoff.json [working-state.json]"],
        }, ensure_ascii=False, indent=2))
        return 2
    result = validate(argv[1], argv[2], argv[3] if len(argv) == 4 else None)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
