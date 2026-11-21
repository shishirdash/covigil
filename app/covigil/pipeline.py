"""Sources in, brief out.

generate_brief() makes one model call over the sources (three, plus approved patient input) and returns the brief as a dict.
audit_brief() makes a second call that checks the brief against the same sources.
Neither has been run against the live API yet.
"""
from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path

from . import patient
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


def _pdf_pages(data: bytes) -> int:
    return len(re.findall(rb"/Type\s*/Page(?![a-zA-Z])", data))


def request_parts(out: Path | None = None) -> dict:
    """Everything the brief call sends, plus labels for out/prompt.txt.

    Three sources always; a fourth (patient input) only when the pharmacist approved it.
    eval/ is never read here.
    """
    out = OUT if out is None else out
    pdf_path = DATA / "outside_records_fax.pdf"
    pdf_bytes = pdf_path.read_bytes()
    pdf = base64.standard_b64encode(pdf_bytes).decode()
    fills = (DATA / "pharmacy_fills.csv").read_text()
    intake = (DATA / "intake_form.md").read_text()
    blocks = [
        {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf}},
        {"type": "text", "text": f"<pharmacy_fills>\n{fills}\n</pharmacy_fills>\n\n<intake_form>\n{intake}\n</intake_form>"},
    ]
    labels = [f"[PDF attached: data/{pdf_path.name}, {_pdf_pages(pdf_bytes)} pages, {len(pdf_bytes)} bytes; base64 not shown]", None]
    sources = ["fax", "fills", "intake"]
    state = patient.approved_input(out)
    if state is not None:
        photos = [(ph, patient.photo_file(out, ph.get("url", ""))) for ph in state["photos"]]
        photos = [(ph, f) for ph, f in photos if f is not None and f.suffix.lower() in patient.IMAGE_TYPES]
        blocks.append({"type": "text", "text": patient.summary_text({**state, "photos": [ph for ph, _ in photos]})})
        labels.append(None)
        for ph, f in photos:
            media = patient.IMAGE_TYPES[f.suffix.lower()]
            data = base64.standard_b64encode(f.read_bytes()).decode()
            blocks.append({"type": "image", "source": {"type": "base64", "media_type": media, "data": data}})
            labels.append(f"[Image attached: {ph['url']} ({media}, {f.stat().st_size} bytes); base64 not shown]")
        sources.append("patient")
    return {"blocks": blocks, "labels": labels, "sources": sources}


def source_blocks(out: Path | None = None) -> list[dict]:
    """The sources as message content. eval/ is never read here."""
    return request_parts(out)["blocks"]


def user_instruction() -> dict:
    return {"type": "text", "text": f"The visit is on {VISIT_DATE}. Write the pre-visit brief as JSON."}


def render_prompt(system: str, blocks: list[dict], labels: list[str | None]) -> str:
    """Human-readable copy of the request for out/prompt.txt. Binary blocks become placeholder lines."""
    parts = ["=== SYSTEM ===", system, "", f"=== USER (model: {MODEL}) ==="]
    for block, label in zip(blocks, labels):
        if block["type"] == "text":
            parts.append(block["text"])
        else:
            parts.append(label or f"[{block['type']} block; content not shown]")
        parts.append("")
    return "\n".join(parts)


def get_client():
    """The Anthropic client. Tests monkeypatch this."""
    import anthropic  # imported here so the app and tests run without the package or a key

    return anthropic.Anthropic()


def finish_brief(raw: str) -> dict:
    """Raw model text -> brief dict with ids, validation problems and provenance. Raises if no JSON."""
    brief = add_ids(parse_json(raw))
    brief["generated_by"] = MODEL
    brief["validation_problems"] = validate_brief(brief)
    return brief


def parse_json(raw: str) -> dict:
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        raise ValueError("The model reply contained no JSON:\n" + raw[:500])
    return json.loads(match.group(0))


def _call(system: str, content: list[dict], max_tokens: int = 8000) -> str:
    client = get_client()
    message = client.messages.create(
        model=MODEL, max_tokens=max_tokens, system=system, messages=[{"role": "user", "content": content}]
    )
    return "".join(block.text for block in message.content if block.type == "text")


def add_ids(brief: dict) -> dict:
    for i, issue in enumerate(brief.get("medication_issues", []), 1):
        issue.setdefault("id", f"flag-{i}")
    return brief


def generate_brief(save: bool = True) -> dict:
    content = source_blocks() + [user_instruction()]
    brief = finish_brief(_call(system_prompt(), content))
    brief["generated_at"] = patient.now()
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
