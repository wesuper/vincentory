#!/usr/bin/env bash
# link-skills.sh
#
# Symlinks published skills (engineering/ and productivity/) into ~/.claude/skills/
# so they are available globally during local development.
#
# - Skips directories without a SKILL.md
# - Warns and continues when a conflicting path already exists
# - Supports paths containing spaces

set -euo pipefail

# Resolve repository root relative to this script.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SKILLS_TARGET="${HOME}/.claude/skills"

PUBLISHED_BUCKETS=("engineering" "productivity")

mkdir -p "${SKILLS_TARGET}"

linked=0
skipped=0
warned=0

for bucket in "${PUBLISHED_BUCKETS[@]}"; do
  bucket_dir="${REPO_ROOT}/skills/${bucket}"
  if [ ! -d "${bucket_dir}" ]; then
    continue
  fi

  for skill_dir in "${bucket_dir}"/*/; do
    # Ensure it is actually a directory (glob may not expand).
    [ -d "${skill_dir}" ] || continue

    skill_md="${skill_dir}SKILL.md"
    if [ ! -f "${skill_md}" ]; then
      continue
    fi

    skill_name="$(basename "${skill_dir}")"
    link_path="${SKILLS_TARGET}/${skill_name}"

    if [ -L "${link_path}" ]; then
      current_target="$(readlink "${link_path}")"
      # Resolve to absolute for comparison.
      expected_target="$(cd "${skill_dir}" && pwd)"
      resolved_current="$(cd "$(dirname "${link_path}")" && cd "$(dirname "${current_target}")" && pwd)/$(basename "${current_target}")" 2>/dev/null || resolved_current="${current_target}"

      if [ "${resolved_current}" = "${expected_target}" ] || [ "${current_target}" = "${skill_dir}" ]; then
        skipped=$((skipped + 1))
        continue
      fi

      echo "WARNING: ${link_path} is a symlink but points elsewhere (${current_target}). Skipping."
      warned=$((warned + 1))
      continue
    fi

    if [ -e "${link_path}" ]; then
      echo "WARNING: ${link_path} already exists and is not a symlink. Skipping."
      warned=$((warned + 1))
      continue
    fi

    ln -s "${skill_dir}" "${link_path}"
    echo "Linked: ${skill_name} -> ${link_path}"
    linked=$((linked + 1))
  done
done

echo ""
echo "Done. linked=${linked} skipped(uptodate)=${skipped} warnings=${warned}"
