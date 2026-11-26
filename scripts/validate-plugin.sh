#!/usr/bin/env bash
# Validate the plugin while allowing one repository-specific warning.
#
# The root CLAUDE.md is project guidance for developing this plugin. The
# validator warns that it is not shipped as installed-plugin context; that is
# expected here. Every other warning or error still fails validation.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

set +e
claude plugin validate . --strict --json >"${TMP_DIR}/report.json" 2>"${TMP_DIR}/stderr"
status=$?
set -e

python3 - "${TMP_DIR}/report.json" "${TMP_DIR}/stderr" "${status}" <<'PY'
import json
import sys
from pathlib import Path

report_path, stderr_path, status_text = sys.argv[1:]
status = int(status_text)
report = json.loads(Path(report_path).read_text(encoding="utf-8"))
stderr = Path(stderr_path).read_text(encoding="utf-8").strip()

allowed_prefix = "CLAUDE.md at the plugin root is not loaded as project context."
unexpected = []
remaining = []

for section in (report.get("manifest", {}), *report.get("contents", [])):
    for error in section.get("errors", []):
        unexpected.append(("error", section.get("file", "?"), error))
    for warning in section.get("warnings", []):
        message = warning.get("message", "")
        if warning.get("path") == "root" and message.startswith(allowed_prefix):
            remaining.append((section.get("file", "?"), warning))
        else:
            unexpected.append(("warning", section.get("file", "?"), warning))

for finding in report.get("directory", {}).get("findings", []):
    unexpected.append(("directory", "plugin-directory", finding))

if unexpected or status not in (0, 1):
    print("Plugin validation failed:", file=sys.stderr)
    for kind, source, item in unexpected:
        print(f"  {kind}: {source}: {item}", file=sys.stderr)
    if stderr:
        print(stderr, file=sys.stderr)
    raise SystemExit(1)

print("Plugin validation passed (1 known root CLAUDE.md warning ignored).")
for source, warning in remaining:
    print(f"  ignored: {source}: {warning['message']}")
PY
