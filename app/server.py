"""CoVigil demo server.

Run from the repo root:
    uvicorn app.server:app --reload --port 8000

The page works with no API key: it shows fixtures/sample_brief.json until a real brief exists in out/.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .covigil import pipeline

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
FIXTURE = ROOT / "fixtures" / "sample_brief.json"
STATE = OUT / "state.json"

app = FastAPI(title="CoVigil")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_brief() -> dict:
    path = OUT / "brief.json"
    if path.exists():
        brief = json.loads(path.read_text())
        brief["origin"] = "model"
    else:
        brief = json.loads(FIXTURE.read_text())
        brief["origin"] = "fixture"
    return pipeline.add_ids(brief)


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"verifications": {}, "decisions": {}, "log": []}


def save_state(state: dict) -> None:
    OUT.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2))


class Verification(BaseModel):
    flag_id: str
    status: str  # verified | unresolved
    note: str = ""
    by: str = "Pharmacist"


class Decision(BaseModel):
    flag_id: str
    action: str  # accept | dismiss
    reason: str = ""
    by: str = "Clara"


@app.get("/api/brief")
def get_brief() -> dict:
    audit_path = OUT / "audit.json"
    return {
        "brief": load_brief(),
        "state": load_state(),
        "audit": json.loads(audit_path.read_text()) if audit_path.exists() else None,
    }


@app.post("/api/generate")
def generate() -> dict:
    """Run the model on the three sources. Needs ANTHROPIC_API_KEY. Clears earlier reviews."""
    try:
        brief = pipeline.generate_brief()
    except Exception as exc:  # shown to the person running the demo
        raise HTTPException(status_code=502, detail=f"Could not generate the brief: {exc}")
    save_state({"verifications": {}, "decisions": {}, "log": []})
    return {"brief": brief}


@app.post("/api/audit")
def audit() -> dict:
    try:
        return {"audit": pipeline.audit_brief(load_brief())}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not run the audit: {exc}")


@app.post("/api/verify")
def verify(v: Verification) -> dict:
    if v.status not in ("verified", "unresolved"):
        raise HTTPException(status_code=422, detail="status must be 'verified' or 'unresolved'")
    state = load_state()
    entry = {"status": v.status, "note": v.note, "by": v.by, "at": _now()}
    state["verifications"][v.flag_id] = entry
    state["log"].append({"type": "verification", "flag_id": v.flag_id, **entry})
    save_state(state)
    return state


@app.post("/api/decision")
def decide(d: Decision) -> dict:
    if d.action not in ("accept", "dismiss"):
        raise HTTPException(status_code=422, detail="action must be 'accept' or 'dismiss'")
    if d.action == "dismiss" and not d.reason.strip():
        raise HTTPException(status_code=422, detail="A dismissal needs a one-line reason.")
    state = load_state()
    entry = {"action": d.action, "reason": d.reason.strip(), "by": d.by, "at": _now()}
    state["decisions"][d.flag_id] = entry
    state["log"].append({"type": "decision", "flag_id": d.flag_id, **entry})
    save_state(state)
    return state


@app.post("/api/reset")
def reset() -> dict:
    state = {"verifications": {}, "decisions": {}, "log": []}
    save_state(state)
    return state


@app.get("/")
def index() -> FileResponse:
    return FileResponse(ROOT / "app" / "static" / "index.html")


# The fax PDF is served so a source chip can open the cited page. eval/ is never served.
app.mount("/data", StaticFiles(directory=ROOT / "data"), name="data")
