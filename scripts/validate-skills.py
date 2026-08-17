#!/usr/bin/env python3
"""Validate every skill in skills/ against the Agent Skills specification.

Deliberately dependency-free: CI's primary gate must not break because an
upstream tool moved. `skills-ref` runs alongside this in CI as a second
opinion, but this script is the one that has to keep working.

Spec: https://agentskills.io/specification
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"

# Spec limits.
MAX_NAME = 64
MAX_DESCRIPTION = 1024
# Not a spec rule — the spec recommends keeping SKILL.md short so activation
# stays cheap. We enforce it as a warning so long skills get split into
# references/ rather than silently bloating every agent's context.
RECOMMENDED_MAX_LINES = 500

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

errors: list[str] = []
warnings: list[str] = []


def parse_frontmatter(text: str, where: str) -> dict[str, str] | None:
    """Minimal YAML frontmatter reader for the flat string fields we use.

    Full YAML is overkill here and would mean a dependency. Skills that need
    nested frontmatter will fail this check loudly rather than pass silently.
    """
    if not text.startswith("---\n"):
        errors.append(f"{where}: missing YAML frontmatter (file must start with '---')")
        return None

    end = text.find("\n---", 3)
    if end == -1:
        errors.append(f"{where}: frontmatter is never closed with '---'")
        return None

    fields: dict[str, str] = {}
    key = None
    for raw in text[4:end].splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith((" ", "\t")) and key:
            # Folded continuation of the previous value.
            fields[key] += " " + raw.strip()
            continue
        if ":" not in raw:
            errors.append(f"{where}: cannot parse frontmatter line: {raw!r}")
            continue
        key, _, value = raw.partition(":")
        key = key.strip()
        fields[key] = value.strip().strip("\"'")
    return fields


def check(skill_dir: Path) -> None:
    where = f"skills/{skill_dir.name}"
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.is_file():
        errors.append(f"{where}: no SKILL.md")
        return

    text = skill_md.read_text(encoding="utf-8")
    fields = parse_frontmatter(text, where)
    if fields is None:
        return

    name = fields.get("name")
    if not name:
        errors.append(f"{where}: frontmatter has no 'name'")
    else:
        if name != skill_dir.name:
            errors.append(
                f"{where}: name {name!r} must match its directory {skill_dir.name!r}"
            )
        if len(name) > MAX_NAME:
            errors.append(f"{where}: name is {len(name)} chars, max is {MAX_NAME}")
        if not NAME_RE.match(name):
            errors.append(
                f"{where}: name {name!r} must be lowercase alphanumeric and single "
                "hyphens only, with no leading, trailing or doubled hyphen"
            )

    description = fields.get("description")
    if not description:
        errors.append(f"{where}: frontmatter has no 'description' — this is what the "
                      "agent matches on, so an empty one makes the skill unreachable")
    elif len(description) > MAX_DESCRIPTION:
        errors.append(
            f"{where}: description is {len(description)} chars, max is {MAX_DESCRIPTION}"
        )

    lines = text.count("\n") + 1
    if lines > RECOMMENDED_MAX_LINES:
        warnings.append(
            f"{where}: SKILL.md is {lines} lines (recommended max "
            f"{RECOMMENDED_MAX_LINES}) — move detail into references/"
        )


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print(f"error: no skills directory at {SKILLS_DIR}", file=sys.stderr)
        return 1

    skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())
    if not skill_dirs:
        print(f"error: {SKILLS_DIR} contains no skills", file=sys.stderr)
        return 1

    for skill_dir in skill_dirs:
        check(skill_dir)

    for warning in warnings:
        print(f"warning: {warning}")
    for error in errors:
        print(f"error: {error}", file=sys.stderr)

    if errors:
        print(f"\n{len(errors)} error(s) across {len(skill_dirs)} skills", file=sys.stderr)
        return 1

    print(f"{len(skill_dirs)} skills validated, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
