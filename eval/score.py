"""Score a brief against the planted findings and traps.

    python eval/score.py out/brief.json

Keyword matching only. It can miss a finding worded unusually, or count one that is mentioned but wrong,
so read the result next to the brief before quoting numbers on stage.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

KEY = Path(__file__).with_name("answer_key.json")


def _text(value) -> str:
    return json.dumps(value).lower()


def score(brief: dict, key: dict | None = None) -> dict:
    key = key or json.loads(KEY.read_text())
    issues = brief.get("medication_issues") or []
    areas = {
        "medication_issues": _text(issues),
        "tests_already_done": _text(brief.get("tests_already_done") or []),
        "anywhere": _text({k: v for k, v in brief.items() if k != "not_found"}),
    }
    caught, missed = [], []
    for finding in key["findings"]:
        haystack = areas[finding["where"]]
        hit = all(re.search(pattern, haystack) for pattern in finding["all_of"])
        (caught if hit else missed).append(finding["name"])
    titles = [str(issue.get("title", "")).lower() for issue in issues if isinstance(issue, dict)]
    tripped = [t["name"] for t in key["traps"] if any(re.search(t["title_matches"], title) for title in titles)]
    return {
        "caught": caught,
        "missed": missed,
        "traps_flagged": tripped,
        "catch_rate": f"{len(caught)} of {len(key['findings'])}",
        "false_alarms": f"{len(tripped)} of {len(key['traps'])}",
        "flags_raised": len(issues),
    }


if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "out/brief.json")
    print(json.dumps(score(json.loads(path.read_text())), indent=2))
