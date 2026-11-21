"""CoVigil demo server.

Run from the repo root:
    uvicorn app.server:app --reload --port 8000

The page works with no API key: it shows fixtures/sample_brief.json until a real brief exists in out/.
"""
from __future__ import annotations

import asyncio
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .covigil import patient, pipeline

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
FIXTURE = ROOT / "fixtures" / "sample_brief.json"
STATE = OUT / "state.json"

app = FastAPI(title="CoVigil")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


OUT_ALLOWLIST = ("prompt.txt", "response_raw.txt", "brief.json", "audit.json", "state.json")
MAX_PHOTO_BYTES = 25 * 1024 * 1024


def load_brief() -> dict:
    """The last good brief: out/brief.json ("saved") if present, else the hand-written fixture ("sample")."""
    path = OUT / "brief.json"
    brief = None
    if path.exists():
        try:
            brief = json.loads(path.read_text())
            brief["origin"] = "saved"
            if not brief.get("generated_at"):
                brief["generated_at"] = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")
        except (json.JSONDecodeError, OSError):
            brief = None
    if brief is None:
        brief = json.loads(FIXTURE.read_text())
        brief["origin"] = "sample"
        brief.setdefault("generated_at", None)
    brief = pipeline.add_ids(brief)
    if "validation_problems" not in brief:
        brief["validation_problems"] = pipeline.validate_brief(brief)
    return brief


def reset_flag_state() -> dict:
    """Clear verifications and decisions for a new brief. Pharmacist reviews of patient input stay in the log."""
    old = load_state()
    state = {"verifications": {}, "decisions": {}, "log": [e for e in old.get("log", []) if e.get("type") == "patient_review"]}
    save_state(state)
    return state


def _raw_links() -> dict:
    names = {"prompt": "prompt.txt", "response": "response_raw.txt", "brief": "brief.json", "audit": "audit.json"}
    return {key: (f"/out/{name}" if (OUT / name).exists() else None) for key, name in names.items()}


def _inputs() -> list[dict]:
    return [
        {"name": "Fax packet (12 pages)", "kind": "pdf", "url": "/data/outside_records_fax.pdf"},
        {"name": "Pharmacy fills", "kind": "csv", "url": "/data/pharmacy_fills.csv"},
        {"name": "Intake form", "kind": "md", "url": "/data/intake_form.md"},
        {"name": "Patient input (pharmacist-approved)", "kind": "patient", "url": "/patient",
         "approved": patient.approved_input(OUT) is not None},
    ]


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"verifications": {}, "decisions": {}, "log": []}


def save_state(state: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
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
        "inputs": _inputs(),
        "raw": _raw_links(),
    }


@app.post("/api/generate")
def generate() -> dict:
    """Run the model on the three sources. Needs ANTHROPIC_API_KEY. Clears earlier reviews."""
    try:
        brief = pipeline.generate_brief()
    except Exception as exc:  # shown to the person running the demo
        raise HTTPException(status_code=502, detail=f"Could not generate the brief: {exc}")
    reset_flag_state()
    return {"brief": brief}


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _timeout_s() -> float:
    try:
        return float(os.environ.get("COVIGIL_TIMEOUT", "60"))
    except ValueError:
        return 60.0


async def _stream_brief():
    timeout = _timeout_s()
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    queue: asyncio.Queue = asyncio.Queue()
    cancel = threading.Event()
    raw_file = None
    try:
        system = pipeline.system_prompt()
        parts = pipeline.request_parts(OUT)
        blocks = parts["blocks"] + [pipeline.user_instruction()]
        labels = parts["labels"] + [None]
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "prompt.txt").write_text(pipeline.render_prompt(system, blocks, labels))
        yield _sse("start", {"model": pipeline.MODEL, "timeout_s": timeout, "sources": parts["sources"]})

        def put(item):
            try:
                loop.call_soon_threadsafe(queue.put_nowait, item)
            except RuntimeError:  # loop closed after a timeout or a disconnect
                pass

        def worker():
            try:
                client = pipeline.get_client()
                with client.messages.stream(
                    model=pipeline.MODEL, max_tokens=8000, system=system,
                    messages=[{"role": "user", "content": blocks}],
                ) as stream:
                    for text in stream.text_stream:
                        if cancel.is_set():
                            return
                        put(("delta", text))
                put(("end", None))
            except Exception as exc:  # reported to the page as an error event
                put(("error", exc))

        threading.Thread(target=worker, daemon=True, name="covigil-stream").start()
        raw_file = (OUT / "response_raw.txt").open("w")
        chunks: list[str] = []
        while True:
            remaining = deadline - loop.time()
            if remaining <= 0:
                raise asyncio.TimeoutError
            kind, value = await asyncio.wait_for(queue.get(), remaining)
            if kind == "delta":
                chunks.append(value)
                raw_file.write(value)
                raw_file.flush()
                yield _sse("delta", {"text": value})
            elif kind == "error":
                raise value
            else:
                break
        raw_file.close()
        raw_file = None
        brief = pipeline.finish_brief("".join(chunks))
        brief["generated_at"] = _now()
        brief["origin"] = "live"
        (OUT / "brief.json").write_text(json.dumps(brief, indent=2))
        reset_flag_state()
        yield _sse("done", {"brief": brief})
    except asyncio.TimeoutError:
        cancel.set()
        yield _sse("timeout", {"detail": f"No complete brief after {timeout:g} s", "fallback": load_brief()})
    except Exception as exc:
        cancel.set()
        yield _sse("error", {"detail": f"{type(exc).__name__}: {exc}", "fallback": load_brief()})
    finally:
        cancel.set()
        if raw_file is not None:
            raw_file.close()


@app.post("/api/generate/stream")
async def generate_stream() -> StreamingResponse:
    """Stream the model's raw text as Server-Sent Events. out/brief.json changes only on a successful parse."""
    return StreamingResponse(
        _stream_brief(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


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


# ---------- raw files ----------

@app.get("/out/{name:path}")
def out_file(name: str) -> FileResponse:
    """Strict allowlist. eval/ is never served; nothing outside out/ is reachable."""
    out = OUT.resolve()
    if name in OUT_ALLOWLIST:
        path = out / name
    elif name.startswith(patient.PHOTO_DIR + "/"):
        leaf = name[len(patient.PHOTO_DIR) + 1:]
        if not leaf or "/" in leaf or "\\" in leaf or leaf.startswith("."):
            raise HTTPException(status_code=404, detail="Not found")
        path = (out / patient.PHOTO_DIR / leaf).resolve()
        if path.parent != out / patient.PHOTO_DIR:
            raise HTTPException(status_code=404, detail="Not found")
    else:
        raise HTTPException(status_code=404, detail="Not found")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    media = "text/plain; charset=utf-8" if path.suffix == ".txt" else None
    return FileResponse(path, media_type=media)


# ---------- patient screen ----------

class PatientAnswer(BaseModel):
    med_id: str
    answer: str  # taking | not_taking | unsure
    note: str = ""


class SamplePhoto(BaseModel):
    med_id: str


class PatientReview(BaseModel):
    status: str  # approved | returned
    note: str = ""
    by: str = "Pharmacist"


def _known_med(med_id: str) -> None:
    if med_id not in {m["id"] for m in patient.medicines()}:
        raise HTTPException(status_code=404, detail=f"Unknown medicine '{med_id}'")


def _changed(state: dict) -> dict:
    """Any patient change sends the input back to the pharmacist."""
    state["review"] = patient.empty_review()
    patient.save(OUT, state)
    return patient.view(OUT)


@app.get("/api/patient")
def get_patient() -> dict:
    return patient.view(OUT)


@app.post("/api/patient/answer")
def patient_answer(a: PatientAnswer) -> dict:
    if a.answer not in patient.ANSWERS:
        raise HTTPException(status_code=422, detail="answer must be 'taking', 'not_taking' or 'unsure'")
    _known_med(a.med_id)
    state = patient.load(OUT)
    state["answers"][a.med_id] = {"answer": a.answer, "note": a.note.strip(), "at": _now()}
    return _changed(state)


@app.post("/api/patient/photo")
async def patient_photo(file: UploadFile = File(...), med_id: Optional[str] = Form(None)) -> dict:
    med_id = (med_id or "").strip() or None
    if med_id:
        _known_med(med_id)
    data = await file.read()
    if not data or len(data) > MAX_PHOTO_BYTES:
        raise HTTPException(status_code=422, detail="Photo is empty or larger than 25 MB")
    try:
        data = patient.shrink_photo(data)
    except Exception:
        raise HTTPException(status_code=422, detail="Could not read that photo. Please try a JPEG or PNG.")
    folder = OUT / patient.PHOTO_DIR
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    name = f"{med_id or 'photo'}-{stamp}.jpg"
    (folder / name).write_bytes(data)
    state = patient.load(OUT)
    state["photos"].append({"med_id": med_id, "url": f"/out/{patient.PHOTO_DIR}/{name}", "kind": "upload", "at": _now()})
    return _changed(state)


@app.post("/api/patient/photo/sample")
def patient_sample_photo(p: SamplePhoto) -> dict:
    _known_med(p.med_id)
    if not (patient.DATA / "bottles" / f"{p.med_id}.jpg").exists():
        raise HTTPException(status_code=404, detail=f"No sample bottle photo for '{p.med_id}'")
    url = f"/data/bottles/{p.med_id}.jpg"
    state = patient.load(OUT)
    state["photos"] = [ph for ph in state["photos"] if ph.get("url") != url]
    state["photos"].append({"med_id": p.med_id, "url": url, "kind": "sample", "at": _now()})
    return _changed(state)


@app.post("/api/patient/review")
def patient_review(r: PatientReview) -> dict:
    if r.status not in patient.REVIEW_STATUSES:
        raise HTTPException(status_code=422, detail="status must be 'approved' or 'returned'")
    state = patient.load(OUT)
    state["review"] = {"status": r.status, "note": r.note.strip(), "by": r.by, "at": _now()}
    patient.save(OUT, state)
    flags = load_state()
    flags.setdefault("log", []).append({"type": "patient_review", **state["review"]})
    save_state(flags)
    return patient.view(OUT)


@app.post("/api/patient/reset")
def patient_reset() -> dict:
    folder = OUT / patient.PHOTO_DIR
    if folder.is_dir():
        for f in folder.iterdir():
            if f.is_file():
                f.unlink()
    patient.save(OUT, patient.empty_state())
    return patient.view(OUT)


# ---------- pages ----------

@app.get("/")
def index() -> FileResponse:
    return FileResponse(ROOT / "app" / "static" / "index.html")


@app.get("/patient")
def patient_page() -> FileResponse:
    page = ROOT / "app" / "static" / "patient.html"
    if not page.exists():
        raise HTTPException(status_code=404, detail="The patient screen is not built yet.")
    return FileResponse(page)


# The fax PDF is served so a source chip can open the cited page. eval/ is never served.
app.mount("/data", StaticFiles(directory=ROOT / "data"), name="data")
