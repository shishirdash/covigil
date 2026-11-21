"""Patient screen: the medicine list, the patient's answers and photos, and the pharmacist's review.

State lives in out/patient.json. Nothing here reaches the model unless review.status == "approved"
(see pipeline.source_blocks). All data is synthetic.
"""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"

ANSWERS = ("taking", "not_taking", "unsure")
REVIEW_STATUSES = ("approved", "returned")
IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}
PHOTO_DIR = "patient_photos"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def med_id(drug: str) -> str:
    """'Metformin' -> 'metformin', 'Vitamin D' -> 'vitamin_d'."""
    return re.sub(r"[^a-z0-9]+", "_", drug.lower()).strip("_")


# ---------- medicine list ----------

_DOSE = r"(\d[\d.,]*\s*(?:mg|mcg|g|units|unit|iu|ml)\b)"


def _section(text: str, heading_start: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading_start)}.*?$(.*?)(?=^##\s|\Z)", text, re.M | re.S | re.I)
    return match.group(1) if match else ""


def _intake_table(intake: str) -> list[dict]:
    meds = []
    for line in _section(intake, "Medicines he takes").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not cells[0] or cells[0].lower() == "medicine" or set(cells[0]) <= set("-: "):
            continue
        match = re.match(rf"^(.*?)\s+{_DOSE}(.*)$", cells[0], re.I)
        drug, dose = (match.group(1).strip(), match.group(2).strip()) if match else (cells[0], "")
        meds.append({"id": med_id(drug), "drug": drug, "dose": dose, "how": cells[1], "from": ["intake"]})
    return meds


def _intake_otc(intake: str) -> list[dict]:
    meds = []
    for para in _section(intake, "Over-the-counter").split("\n\n"):
        para = " ".join(para.split())
        if not para:
            continue
        brand = re.match(rf"^(.*?)\s*\(\s*([A-Za-z][A-Za-z ]*?)\s+{_DOSE}\s*\)\s*:?\s*(.*)$", para, re.I)
        if brand:  # "Aleve (naproxen 220 mg): 2 tablets, twice a day..."
            generic = brand.group(2).strip()
            drug, dose, how = f"{generic.capitalize()} ({brand.group(1).strip()})", brand.group(3), brand.group(4)
            mid = med_id(generic)
        else:  # "Vitamin D 1000 units daily."
            plain = re.match(rf"^(.*?)\s+{_DOSE}\s*(.*)$", para, re.I)
            if not plain:
                continue
            drug, dose, how = plain.group(1).strip(), plain.group(2), plain.group(3)
            mid = med_id(drug)
        meds.append({"id": mid, "drug": drug, "dose": dose.strip(), "how": how.strip().rstrip(".").strip(),
                     "from": ["intake"], "otc": True})
    return meds


def _fills() -> list[dict]:
    path = DATA / "pharmacy_fills.csv"
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return sorted(csv.DictReader(f), key=lambda r: r.get("fill_date", ""))


def medicines() -> list[dict]:
    """Intake-form table, then the OTC section, then drugs that appear only in the fill history."""
    intake_path = DATA / "intake_form.md"
    intake = intake_path.read_text() if intake_path.exists() else ""
    meds: list[dict] = []
    by_id: dict[str, dict] = {}
    for med in _intake_table(intake) + _intake_otc(intake):
        if med["id"] not in by_id:
            by_id[med["id"]] = med
            meds.append(med)
    latest: dict[str, dict] = {}
    for row in _fills():  # sorted by date, so the last row per drug wins
        latest[med_id(row["drug"])] = row
    for mid, row in latest.items():
        if mid in by_id:
            if "fills" not in by_id[mid]["from"]:
                by_id[mid]["from"].append("fills")
            continue
        med = {"id": mid, "drug": row["drug"].strip().capitalize(), "dose": row.get("strength", "").strip(),
               "how": row.get("directions", "").strip(), "from": ["fills"]}
        by_id[mid] = med
        meds.append(med)
    for med in meds:
        med["bottle_photo"] = f"/data/bottles/{med['id']}.jpg" if (DATA / "bottles" / f"{med['id']}.jpg").exists() else None
    return meds


# ---------- state ----------

def empty_review() -> dict:
    return {"status": "pending", "note": "", "by": "", "at": ""}


def empty_state() -> dict:
    return {"answers": {}, "photos": [], "review": empty_review()}


def load(out: Path) -> dict:
    path = out / "patient.json"
    state = empty_state()
    if path.exists():
        try:
            state.update(json.loads(path.read_text()))
        except (json.JSONDecodeError, OSError):
            pass
    return state


def save(out: Path, state: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "patient.json").write_text(json.dumps(state, indent=2))


def view(out: Path) -> dict:
    state = load(out)
    return {"medicines": medicines(), "answers": state["answers"], "photos": state["photos"], "review": state["review"]}


def photo_file(out: Path, url: str) -> Path | None:
    """Map a photo url back to a file on disk. Only data/bottles/ and out/patient_photos/ are allowed."""
    for prefix, base in (("/data/bottles/", DATA / "bottles"), (f"/out/{PHOTO_DIR}/", out / PHOTO_DIR)):
        if url.startswith(prefix):
            name = url[len(prefix):]
            if not name or "/" in name or "\\" in name or name.startswith("."):
                return None
            path = (base / name).resolve()
            if path.parent != base.resolve() or not path.is_file():
                return None
            return path
    return None


def approved_input(out: Path) -> dict | None:
    """The patient state, only if the pharmacist approved it."""
    state = load(out)
    return state if state["review"].get("status") == "approved" else None


def summary_text(state: dict) -> str:
    names = {m["id"]: m for m in medicines()}
    review = state["review"]
    lines = [
        "Patient-entered input from the patient screen (patient or family), reviewed and approved by "
        f"{review.get('by') or 'the pharmacist'} at {review.get('at') or 'unknown time'}. Synthetic data.",
    ]
    if review.get("note"):
        lines.append(f"Pharmacist note: {review['note']}")
    lines.append("Answers (is he taking this medicine now?):")
    if not state["answers"]:
        lines.append("- (no answers)")
    for mid, ans in state["answers"].items():
        med = names.get(mid, {"drug": mid, "dose": ""})
        label = f"{med['drug']} {med.get('dose', '')}".strip()
        note = f" - note: {ans['note']}" if ans.get("note") else ""
        lines.append(f"- {label}: {ans.get('answer', '').replace('_', ' ')}{note}")
    if state["photos"]:
        lines.append(f"Photos attached after this block, in order ({len(state['photos'])}):")
        for i, photo in enumerate(state["photos"], 1):
            what = names.get(photo.get("med_id") or "", {}).get("drug") or "no medicine named"
            lines.append(f"- Photo {i}: {photo.get('kind', 'upload')} photo, medicine: {what}")
    return "<patient_input>\n" + "\n".join(lines) + "\n</patient_input>"


MAX_PHOTO_EDGE = 1568  # longest side sent to the model; keeps every photo far below the API's per-image size limit


def shrink_photo(data: bytes) -> bytes:
    """Any uploaded image -> an upright JPEG no larger than MAX_PHOTO_EDGE on its longest side."""
    import io

    from PIL import Image, ImageOps

    img = ImageOps.exif_transpose(Image.open(io.BytesIO(data)))
    img = img.convert("RGB")
    img.thumbnail((MAX_PHOTO_EDGE, MAX_PHOTO_EDGE))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=85)
    return buf.getvalue()
