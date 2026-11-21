"""Live-build endpoints: streaming generate, /out allowlist, patient screen. No API key or network needed."""
import json
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from app import server  # noqa: E402
from app.covigil import pipeline  # noqa: E402

FIXTURE = json.loads((ROOT / "fixtures" / "sample_brief.json").read_text())
GOOD = json.dumps({k: v for k, v in FIXTURE.items() if k != "_note"})
def _png() -> bytes:
    import io

    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (8, 8), "white").save(buf, "PNG")
    return buf.getvalue()


PNG = _png()


class FakeStream:
    def __init__(self, chunks, delay=0.0):
        self.chunks, self.delay = chunks, delay

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    @property
    def text_stream(self):
        for chunk in self.chunks:
            if self.delay:
                time.sleep(self.delay)
            yield chunk


class FakeClient:
    def __init__(self, chunks, delay=0.0):
        self.calls = []
        outer = self

        class Messages:
            def stream(self, **kwargs):
                outer.calls.append(kwargs)
                return FakeStream(chunks, delay)

        self.messages = Messages()


@pytest.fixture
def out(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "OUT", tmp_path)
    monkeypatch.setattr(server, "STATE", tmp_path / "state.json")
    monkeypatch.setattr(pipeline, "OUT", tmp_path)
    return tmp_path


def fake(monkeypatch, chunks, delay=0.0):
    client = FakeClient(chunks, delay)
    monkeypatch.setattr(pipeline, "get_client", lambda: client)
    return client


def events(body: str) -> list[tuple[str, dict]]:
    found = []
    for frame in body.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in frame.splitlines() if ": " in line)
        found.append((lines["event"], json.loads(lines["data"])))
    return found


def stream(client) -> list[tuple[str, dict]]:
    resp = client.post("/api/generate/stream")
    assert resp.status_code == 200 and resp.headers["content-type"].startswith("text/event-stream")
    return events(resp.text)


def test_stream_success_writes_files_and_emits_live(out, monkeypatch):
    chunks = ["Here is the brief:\n", GOOD[:200], GOOD[200:], "\nDone."]
    fc = fake(monkeypatch, chunks)
    client = TestClient(server.app)
    client.post("/api/decision", json={"flag_id": "flag-1", "action": "accept"})
    evs = stream(client)
    names = [e for e, _ in evs]
    assert names[0] == "start" and names[-1] == "done" and names.count("delta") == len(chunks)
    assert evs[0][1]["sources"] == ["fax", "fills", "intake"] and evs[0][1]["timeout_s"] == 60
    brief = evs[-1][1]["brief"]
    assert brief["origin"] == "live" and brief["validation_problems"] == [] and brief["generated_at"]
    assert brief["generated_by"] == pipeline.MODEL and brief["medication_issues"][0]["id"] == "flag-1"
    assert json.loads((out / "brief.json").read_text())["notice"] == FIXTURE["notice"]
    assert (out / "response_raw.txt").read_text() == "".join(chunks)
    prompt = (out / "prompt.txt").read_text()
    assert "[PDF attached" in prompt and "<pharmacy_fills>" in prompt and "JVBERi" not in prompt
    assert fc.calls[0]["messages"][0]["content"][0]["type"] == "document"
    state = client.get("/api/brief").json()
    assert state["brief"]["origin"] == "saved" and state["state"]["decisions"] == {}
    assert state["raw"]["prompt"] == "/out/prompt.txt" and state["raw"]["audit"] is None
    assert [i["kind"] for i in state["inputs"]] == ["pdf", "csv", "md", "patient"]
    assert client.get("/out/response_raw.txt").text == "".join(chunks)


def test_bad_json_emits_error_and_keeps_last_good_brief(out, monkeypatch):
    saved = {**json.loads(GOOD), "generated_at": "2026-11-20T10:00:00+00:00"}
    (out / "brief.json").write_text(json.dumps(saved))
    before = (out / "brief.json").read_text()
    fake(monkeypatch, ["I could not ", "write JSON {broken"])
    evs = stream(TestClient(server.app))
    assert evs[-1][0] == "error"
    assert evs[-1][1]["fallback"]["origin"] == "saved"
    assert evs[-1][1]["fallback"]["generated_at"] == "2026-11-20T10:00:00+00:00"
    assert (out / "brief.json").read_text() == before
    assert (out / "response_raw.txt").read_text() == "I could not write JSON {broken"


def test_client_failure_falls_back_to_sample(out, monkeypatch):
    def boom():
        raise RuntimeError("no API key")
    monkeypatch.setattr(pipeline, "get_client", boom)
    evs = stream(TestClient(server.app))
    assert evs[-1][0] == "error" and "no API key" in evs[-1][1]["detail"]
    assert evs[-1][1]["fallback"]["origin"] == "sample"
    assert not (out / "brief.json").exists()


def test_timeout_emits_fallback(out, monkeypatch):
    monkeypatch.setenv("COVIGIL_TIMEOUT", "0.3")
    fake(monkeypatch, ["{", '"a": 1}'], delay=1.0)
    start = time.monotonic()
    evs = stream(TestClient(server.app))
    assert time.monotonic() - start < 0.9
    assert evs[0][1]["timeout_s"] == 0.3
    assert evs[-1][0] == "timeout" and evs[-1][1]["fallback"]["origin"] == "sample"
    assert "0.3 s" in evs[-1][1]["detail"]
    assert not (out / "brief.json").exists()


def test_old_generate_still_works(out, monkeypatch):
    class Block:
        type, text = "text", GOOD

    class Client:
        class messages:
            @staticmethod
            def create(**kwargs):
                return type("M", (), {"content": [Block()]})()

    monkeypatch.setattr(pipeline, "get_client", lambda: Client())
    resp = TestClient(server.app).post("/api/generate")
    assert resp.status_code == 200 and resp.json()["brief"]["validation_problems"] == []
    assert (out / "brief.json").exists()


def test_out_allowlist(out):
    client = TestClient(server.app)
    (out / "state.json").write_text("{}")
    (out / "secret.txt").write_text("no")
    assert client.get("/out/state.json").status_code == 200
    assert client.get("/out/prompt.txt").status_code == 404  # allowed but absent
    for bad in ["/out/secret.txt", "/out/eval/answer_key.json", "/out/../eval/answer_key.json",
                "/out/%2e%2e/eval/answer_key.json", "/out/patient_photos/../../eval/answer_key.json", "/out/patient_photos/sub/x.png", "/out/patient_photos/.hidden",
                "/out/patient_photos/%2e%2e%2fstate.json", "/out/patient_photos/", "/out/..%2f..%2feval%2fanswer_key.json"]:
        assert client.get(bad).status_code == 404, bad
    (out / "patient_photos").mkdir()
    (out / "patient_photos" / "x.png").write_bytes(PNG)
    assert client.get("/out/patient_photos/x.png").status_code == 200


def test_patient_medicines_and_answer_resets_review(out):
    client = TestClient(server.app)
    meds = {m["id"]: m for m in client.get("/api/patient").json()["medicines"]}
    for mid in ["metformin", "losartan", "lisinopril", "furosemide", "tamsulosin", "atorvastatin", "naproxen", "vitamin_d", "apixaban"]:
        assert mid in meds, mid
    assert meds["metformin"]["dose"] == "1000 mg" and meds["metformin"]["from"] == ["intake", "fills"]
    assert meds["apixaban"]["from"] == ["fills"] and meds["apixaban"]["bottle_photo"] is None
    assert meds["vitamin_d"]["dose"] == "1000 units"
    assert client.post("/api/patient/answer", json={"med_id": "nope", "answer": "taking"}).status_code == 404
    assert client.post("/api/patient/answer", json={"med_id": "metformin", "answer": "maybe"}).status_code == 422
    client.post("/api/patient/review", json={"status": "approved", "note": "Checked"})
    assert client.get("/api/patient").json()["review"]["status"] == "approved"
    body = client.post("/api/patient/answer", json={"med_id": "apixaban", "answer": "not_taking", "note": "ran out"}).json()
    assert body["answers"]["apixaban"]["answer"] == "not_taking"
    assert body["review"]["status"] == "pending"
    log = client.get("/api/brief").json()["state"]["log"]
    assert log[-1]["type"] == "patient_review" and log[-1]["by"] == "Pharmacist"
    assert client.post("/api/patient/review", json={"status": "maybe"}).status_code == 422
    assert client.post("/api/patient/reset").json()["answers"] == {}


def test_approved_review_adds_patient_source(out, monkeypatch):
    client = TestClient(server.app)
    client.post("/api/patient/answer", json={"med_id": "apixaban", "answer": "not_taking", "note": "no bottle"})
    up = client.post("/api/patient/photo", files={"file": ("bottle.png", PNG, "image/png")}, data={"med_id": "metformin"})
    assert up.status_code == 200 and up.json()["photos"][0]["kind"] == "upload"
    assert client.get(up.json()["photos"][0]["url"]).status_code == 200
    assert client.post("/api/patient/photo", files={"file": ("x.exe", b"MZ", "application/octet-stream")}).status_code == 422

    blocks = pipeline.source_blocks()
    assert len(blocks) == 2 and "patient_input" not in json.dumps(blocks)
    assert client.get("/api/brief").json()["inputs"][3]["approved"] is False

    client.post("/api/patient/review", json={"status": "returned", "note": "Ask again"})
    assert len(pipeline.source_blocks()) == 2

    client.post("/api/patient/review", json={"status": "approved", "note": "Confirmed by phone"})
    blocks = pipeline.source_blocks()
    assert blocks[2]["type"] == "text" and blocks[2]["text"].startswith("<patient_input>")
    assert "Apixaban" in blocks[2]["text"] and "not taking" in blocks[2]["text"] and "Confirmed by phone" in blocks[2]["text"]
    assert blocks[3]["type"] == "image" and blocks[3]["source"]["media_type"] == "image/jpeg"
    assert client.get("/api/brief").json()["inputs"][3]["approved"] is True
    assert "answer_key" not in json.dumps(blocks[:3])

    fake(monkeypatch, [GOOD])
    evs = stream(client)
    assert evs[0][1]["sources"] == ["fax", "fills", "intake", "patient"]
    assert "[Image attached: /out/patient_photos/" in (out / "prompt.txt").read_text()
    log = client.get("/api/brief").json()["state"]["log"]
    assert [e["type"] for e in log] == ["patient_review", "patient_review"]  # kept across a new brief


def test_dismiss_without_reason_still_refused(out):
    client = TestClient(server.app)
    assert client.post("/api/decision", json={"flag_id": "flag-1", "action": "dismiss", "reason": "  "}).status_code == 422


def test_patient_page_missing_is_404_or_served(out):
    resp = TestClient(server.app).get("/patient")
    page = ROOT / "app" / "static" / "patient.html"
    assert resp.status_code == (200 if page.exists() else 404)


def test_big_phone_photo_is_shrunk_before_it_can_reach_the_model():
    import io

    from PIL import Image

    from app.covigil import patient as patient_mod

    buf = io.BytesIO()
    Image.effect_noise((4000, 3000), 80).convert("RGB").save(buf, "PNG")  # ~ a large phone photo
    small = patient_mod.shrink_photo(buf.getvalue())
    img = Image.open(io.BytesIO(small))
    assert img.format == "JPEG" and max(img.size) <= patient_mod.MAX_PHOTO_EDGE
    assert len(small) < 5 * 1024 * 1024


def test_unreadable_photo_is_refused(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    from app import server

    monkeypatch.setattr(server, "OUT", tmp_path)
    up = TestClient(server.app).post("/api/patient/photo", files={"file": ("x.jpg", b"not an image", "image/jpeg")})
    assert up.status_code == 422


def test_prompt_explains_the_patient_source():
    from app.covigil import pipeline

    text = pipeline.system_prompt()
    assert "<patient_input>" in text and "bottle photo:" in text and "patient:" in text
