"""Checks on the brief the model returns. Returns a list of problems; empty means it passed."""
from __future__ import annotations

WHEN = {"before_visit", "at_visit"}
MAX_FLAGS = 6
BANNED = ("stop ", "start ", "discontinue ", "increase the dose", "decrease the dose", "diagnosis of")


def _needs_sources(items, label, problems):
    for i, item in enumerate(items or []):
        if not isinstance(item, dict) or not item.get("sources"):
            problems.append(f"{label}[{i}] has no sources")


def validate_brief(brief: dict) -> list[str]:
    problems: list[str] = []
    if not brief.get("notice"):
        problems.append("missing the software notice")
    for key in ("story", "medication_issues"):
        if not isinstance(brief.get(key), list):
            problems.append(f"{key} is missing or not a list")
    _needs_sources(brief.get("story"), "story", problems)
    _needs_sources(brief.get("medication_issues"), "medication_issues", problems)
    _needs_sources(brief.get("tests_already_done"), "tests_already_done", problems)

    issues = brief.get("medication_issues") or []
    if len(issues) > MAX_FLAGS:
        problems.append(f"{len(issues)} medication issues; the cap is {MAX_FLAGS}")
    for i, issue in enumerate(issues):
        if not isinstance(issue, dict):
            continue
        if issue.get("when") not in WHEN:
            problems.append(f"medication_issues[{i}] has an invalid 'when'")
        text = (issue.get("title", "") + " " + issue.get("why_review", "")).lower()
        for phrase in BANNED:
            if text.startswith(phrase) or f". {phrase}" in text:
                problems.append(f"medication_issues[{i}] reads like an order or diagnosis: '{phrase.strip()}'")
    return problems
