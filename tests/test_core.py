import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))

from fastapi.testclient import TestClient  # noqa: E402

from app import server  # noqa: E402
from app.covigil.pipeline import parse_json, source_blocks  # noqa: E402
from app.covigil.schema import validate_brief  # noqa: E402
from score import score  # noqa: E402

FIXTURE = json.loads((ROOT / "fixtures" / "sample_brief.json").read_text())


def test_fixture_passes_validation():
    assert validate_brief(FIXTURE) == []


def test_missing_sources_is_reported():
    brief = copy.deepcopy(FIXTURE)
    brief["medication_issues"][0]["sources"] = []
    assert any("no sources" in p for p in validate_brief(brief))


def test_too_many_flags_is_reported():
    brief = copy.deepcopy(FIXTURE)
    brief["medication_issues"] = brief["medication_issues"] * 2
    assert any("cap" in p for p in validate_brief(brief))


def test_order_wording_is_reported():
    brief = copy.deepcopy(FIXTURE)
    brief["medication_issues"][0]["title"] = "Stop lisinopril"
    assert any("order" in p for p in validate_brief(brief))


def test_fixture_scores_all_findings_and_no_traps():
    result = score(FIXTURE)
    assert result["missed"] == []
    assert result["traps_flagged"] == []


def test_trap_is_counted():
    brief = copy.deepcopy(FIXTURE)
    brief["medication_issues"].append({"title": "Hydrochlorothiazide fills stopped", "why_review": "", "when": "at_visit", "sources": ["x"]})
    assert score(brief)["traps_flagged"] == ["Hydrochlorothiazide (correctly stopped)"]


def test_missing_finding_is_counted():
    brief = copy.deepcopy(FIXTURE)
    brief["medication_issues"] = [i for i in brief["medication_issues"] if "pixaban" not in i["title"]]
    assert "Apixaban lapse" in score(brief)["missed"]


def test_parse_json_ignores_surrounding_text():
    assert parse_json('Here it is:\n{"a": 1}\nDone.') == {"a": 1}


def test_sources_never_include_the_answer_key():
    blob = json.dumps(source_blocks()[1])
    assert "planted" not in blob.lower() and "answer key" not in blob.lower()


def test_dismissal_needs_a_reason(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "OUT", tmp_path)
    monkeypatch.setattr(server, "STATE", tmp_path / "state.json")
    client = TestClient(server.app)
    assert client.get("/api/brief").json()["brief"]["origin"] == "fixture"
    assert client.post("/api/decision", json={"flag_id": "flag-1", "action": "dismiss"}).status_code == 422
    ok = client.post("/api/decision", json={"flag_id": "flag-1", "action": "dismiss", "reason": "Discussed with cardiology"})
    assert ok.status_code == 200 and ok.json()["decisions"]["flag-1"]["by"] == "Clara"
    verified = client.post("/api/verify", json={"flag_id": "flag-1", "status": "verified", "note": "Called pharmacy"})
    assert verified.json()["verifications"]["flag-1"]["status"] == "verified"
    assert len(verified.json()["log"]) == 2
