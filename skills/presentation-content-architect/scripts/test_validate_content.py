#!/usr/bin/env python3
"""Regression tests for validate_content.py's READY-gate checks."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("validate_content.py")


def fixture(status="REVIEW", readiness="needs_review", stage="REVIEW",
            duration=True, minutes=True, unresolved=None,
            unresolved_key=True, open_questions=None,
            evidence="- hypothesis: claim"):
    md = ["---", "title: T", "audience: A", "objective: O"]
    if duration:
        md.append("duration_minutes: 10")
    md += [f"status: {status}", "---", "",
           "<!-- slide:id=s1 role=COVER chapter=int -->",
           "# T", "> Takeaway: x", "## Visible", "- x",
           "## Evidence", evidence, "## Visual Intent", "cover",
           "## Speaker Notes", "Purpose: p", "Talk:", "- a", "- b",
           "Transition: t"]
    if minutes:
        md.append("Minutes: 1")

    handoff = {
        "contract_version": "1.0",
        "content_file": "presentation.md",
        "target_renderer": "generic",
        "readiness": readiness,
        "slides": [{
            "slide_id": "s1", "role": "COVER", "title": "T",
            "visual_intent": "cover", "speaker_notes_present": True,
        }],
    }
    if unresolved_key:
        handoff["unresolved"] = unresolved or []

    state = {
        "stage": stage,
        "revision": 1,
        "confirmed": {"audience": "A", "objective": "O"},
        "assumptions": [],
        "open_questions": open_questions or [],
        "decision_log": [],
        "slide_maturity": {"s1": "review"},
    }
    return "\n".join(md) + "\n", handoff, state


class ValidatorReadyGateTests(unittest.TestCase):
    def run_validator(self, tmp, md, handoff, state, with_state=True):
        d = Path(tmp)
        (d / "presentation.md").write_text(md, encoding="utf-8")
        (d / "handoff.json").write_text(json.dumps(handoff, ensure_ascii=False), encoding="utf-8")
        (d / "working-state.json").write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        args = [sys.executable, "-S", str(SCRIPT), str(d / "presentation.md"),
                str(d / "handoff.json")]
        if with_state:
            args.append(str(d / "working-state.json"))
        proc = subprocess.run(args, capture_output=True, text=True)
        self.assertTrue(proc.stdout, proc.stderr)
        return json.loads(proc.stdout), proc.returncode

    def test_valid_review_fixture_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, code = self.run_validator(tmp, *fixture())
            self.assertEqual(code, 0, result["errors"])
            self.assertTrue(result["ok"])

    def test_valid_ready_fixture_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, code = self.run_validator(
                tmp, *fixture(status="READY", readiness="ready", stage="READY"))
            self.assertEqual(code, 0, result["errors"])
            self.assertTrue(result["ok"])

    def test_ready_with_open_questions_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, code = self.run_validator(
                tmp, *fixture(status="READY", readiness="ready", stage="READY",
                              open_questions=["q1"]))
            self.assertEqual(code, 1)
            self.assertTrue(any("open_questions" in e for e in result["errors"]), result)

    def test_ready_with_unresolved_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, code = self.run_validator(
                tmp, *fixture(status="READY", readiness="ready", stage="READY",
                              unresolved=["q1"]))
            self.assertEqual(code, 1)
            self.assertTrue(any("unresolved" in e for e in result["errors"]), result)

    def test_stage_status_mapping_fails_on_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, code = self.run_validator(
                tmp, *fixture(status="DRAFT", readiness="needs_review", stage="ENRICHED"))
            self.assertEqual(code, 1)
            self.assertTrue(any("stage/status" in e for e in result["errors"]), result)

    def test_handoff_schema_requires_unresolved(self):
        schema = json.loads(
            Path(__file__).parents[1].joinpath("schemas/handoff.schema.json").read_text(encoding="utf-8")
        )
        self.assertIn("unresolved", schema["required"])

    def test_status_readiness_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, code = self.run_validator(
                tmp, *fixture(status="REVIEW", readiness="ready"))
            self.assertEqual(code, 1)
            self.assertTrue(any("status/readiness" in e for e in result["errors"]), result)

    def test_invalid_status_enum_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, code = self.run_validator(
                tmp, *fixture(status="needs_review"))
            self.assertEqual(code, 1)
            self.assertTrue(any("status" in e for e in result["errors"]), result)

    def test_missing_duration_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, code = self.run_validator(tmp, *fixture(duration=False))
            self.assertEqual(code, 1)
            self.assertTrue(any("duration_minutes" in e for e in result["errors"]), result)

    def test_missing_minutes_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, code = self.run_validator(tmp, *fixture(minutes=False))
            self.assertEqual(code, 1)
            self.assertTrue(any("Minutes" in e for e in result["errors"]), result)

    def test_missing_unresolved_field_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, code = self.run_validator(tmp, *fixture(unresolved_key=False))
            self.assertEqual(code, 1)
            self.assertTrue(any("unresolved" in e for e in result["errors"]), result)

    def test_ready_requires_working_state_argument(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, code = self.run_validator(
                tmp, *fixture(status="READY", readiness="ready", stage="READY"),
                with_state=False)
            self.assertEqual(code, 1)
            self.assertTrue(any("working-state" in e for e in result["errors"]), result)

    def test_empty_evidence_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, code = self.run_validator(tmp, *fixture(evidence=""))
            self.assertEqual(code, 1)
            self.assertTrue(any("Evidence" in e for e in result["errors"]), result)


if __name__ == "__main__":
    unittest.main()
