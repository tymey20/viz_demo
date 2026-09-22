"""Commentary = deterministic sentences from facts, optionally replaced by an agent/analyst
draft in reports/<id>/commentary/<as_of>.md. Drafts are DRAFT until signed_off_by is set,
and every number in a draft must be present in the facts (grounding check)."""
from __future__ import annotations

import re
from dataclasses import dataclass

import yaml

from . import facts as F
from .spec import ReportSpec


@dataclass
class Commentary:
    lines: list[str]
    signed_off_by: str | None
    source: str          # "rules" | "draft"

    @property
    def status(self) -> str:
        return f"Signed off: {self.signed_off_by}" if self.signed_off_by else "DRAFT — requires analyst sign-off"


def from_rules(spec: ReportSpec, facts: list[dict]) -> list[str]:
    r = spec.commentary
    lines = [r.header]
    breaches = [f for f in facts if f["status"] != "Green"]
    if not breaches:
        return lines + [r.all_green]
    for f in sorted(breaches, key=lambda f: (f["status"] != "Red", f["label"], f["key"])):
        lines.append((r.red if f["status"] == "Red" else r.amber).format(**f))
    return lines


def load_draft(spec: ReportSpec, label: str):
    path = spec.dir / "commentary" / f"{label}.md"
    if not path.exists():
        return None, None
    text = path.read_text()
    meta, body = {}, text
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        meta = yaml.safe_load(fm) or {}
    lines = [l.strip() for l in body.strip().splitlines() if l.strip()]
    return lines, (meta.get("signed_off_by") or None)


def ungrounded(lines: list[str], facts: list[dict]) -> list[str]:
    allowed = F.allowed_numbers(facts)
    bad = []
    for line in lines:
        for tok in re.findall(r"\d[\d,]*\.?\d*", line):
            if tok not in allowed and not re.fullmatch(r"(19|20)\d\d(-\d\d)?(-\d\d)?|Q[1-4]|[1-4]", tok):
                bad.append(f"{tok!r} in: {line}")
    return bad


def build(spec: ReportSpec, facts: list[dict], label: str) -> Commentary:
    lines, signed = load_draft(spec, label)
    if lines is None:
        return Commentary(from_rules(spec, facts), None, "rules")
    return Commentary(lines, signed, "draft")
