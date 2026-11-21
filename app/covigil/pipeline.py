"""Sources in, brief out.

generate_brief() makes one model call over the three sources and returns the brief as a dict.
audit_brief() makes a second call that checks the brief against the same sources.
Neither has been run against the live API yet.
"""
from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path

from .schema import validate_brief

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = ROOT / "out"
MODEL = os.environ.get("COVIGIL_MODEL", "claude-fable-5-2")
VISIT_DATE = "2026-11-23"

AUDIT_SYSTEM = """You audit a pre-visit brief written by other software. You are software and you do not diagnose.
You receive the same three sources the brief was written from, and the brief as JSON.
Return only JSON with this shape:
{"unsupported": [{"text": "", "cited": [""], "problem": ""}], "missing": [{"text": "", "sources": [""]}]}
"unsupported" lists statements whose cited page or row does not support them.
"missing" lists facts in the sources that a physician would need before this visit and that the brief leaves out.
Return empty lists if there is nothing to report. Do not repeat items that are correct."""


def system_prompt() -> str:
    text = (ROOT / "prompts" / "brief_prompt.md").read_text()
    start = text.index("## System prompt") + len("## System prompt")
    end = text.index("## Second pass")
    return text[start:end].strip()


def source_blocks() -> list[dict]:
    """The three sources as message content. eval/ is never read here."""
    pdf = base64.standard_b64encode((DATA / "outside_records_fax.pdf").read_bytes()).decode()
    fills = (DATA / "pharmacy_fills.csv").read_text()
    intake = (DATA / "intake_form.md").read_text()
    return [
        {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf}},
        {"type": "text", "text": f"<pharmacy_fills>\n{fills}\n</pharmacy_fills>\n\n<intake_form>\n{intake}\n</intake_form>"},
    ]


def parse_json(raw: str) -> dict:
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        raise ValueError("The model reply contained no JSON:\n" + raw[:500])
    return json.loads(match.group(0))


def _call(system: str, content: list[dict], max_tokens: int = 8000) -> str:
    import anthropic  # imported here so the app and tests run without the package or a key

    client = anthropic.Anthropic()
    message = client.messages.create(
        model=MODEL, max_tokens=max_tokens, system=system, messages=[{"role": "user", "content": content}]
    )
    return "".join(block.text for block in message.content if block.type == "text")


def add_ids(brief: dict) -> dict:
    for i, issue in enumerate(brief.get("medication_issues", []), 1):
        issue.setdefault("id", f"flag-{i}")
    return brief


def generate_brief(save: bool = True) -> dict:
    content = source_blocks() + [
        {"type": "text", "text": f"The visit is on {VISIT_DATE}. Write the pre-visit brief as JSON."}
    ]
    brief = add_ids(parse_json(_call(system_prompt(), content)))
    brief["generated_by"] = MODEL
    problems = validate_brief(brief)
    brief["validation_problems"] = problems
    if save:
        OUT.mkdir(exist_ok=True)
        (OUT / "brief.json").write_text(json.dumps(brief, indent=2))
    return brief


def audit_brief(brief: dict, save: bool = True) -> dict:
    content = source_blocks() + [
        {"type": "text", "text": "<brief>\n" + json.dumps(brief, indent=2) + "\n</brief>\n\nAudit this brief."}
    ]
    audit = parse_json(_call(AUDIT_SYSTEM, content, max_tokens=4000))
    audit.setdefault("unsupported", [])
    audit.setdefault("missing", [])
    if save:
        OUT.mkdir(exist_ok=True)
        (OUT / "audit.json").write_text(json.dumps(audit, indent=2))
    return audit


if __name__ == "__main__":
    result = generate_brief()
    print(json.dumps(result, indent=2))
