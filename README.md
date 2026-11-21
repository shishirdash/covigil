# CoVigil: pre-visit brief with a medication safety check

Claude Impact Lab, Digital Health, 21 November 2026. General Medicine track.

**All patient data in this repo is synthetic. No real patient, clinician or facility is described.**

## The problem, in one sentence

Clara, a physician, spends 5 to 10 minutes per new patient hunting through faxed records from other hospitals, and still worries about the detail she skimmed past.

## What we are building

One workflow, for one person, before a new-patient visit:

1. **Read.** A faxed records packet, an intake form and a pharmacy fill history go in.
2. **Brief.** Clara gets a one-page story of the patient. Every line links to its source page.
3. **Review.** She sees a short list of medication issues to review, most serious first, and accepts or dismisses each one.

The software does not diagnose and does not give orders. It says "review this" and shows where the evidence is. Clara decides.

It does not fetch records. The workflow starts when the fax arrives.

## What is in this repo

| Path | What it is |
|---|---|
| `data/outside_records_fax.pdf` | 12-page synthetic fax packet from three facilities, with filler pages |
| `data/pharmacy_fills.csv` | Synthetic pharmacy fill history, June to November 2026 |
| `data/intake_form.md` | Intake form filled in by the patient's daughter |
| `eval/answer_key.md` | The 7 planted findings, 4 traps, and how to score a run. **Never pass this to the model.** |
| `prompts/brief_prompt.md` | Draft system prompt and output format |
| `app/server.py` | Demo server: serves the page, the brief, and records pharmacist checks and physician decisions |
| `app/covigil/pipeline.py` | The model call and the audit call. Untested against the live API. |
| `app/covigil/schema.py` | Checks on the model's output: sources present, six flags at most, no orders |
| `app/static/index.html` | The one screen: brief, flags, pharmacist and physician views |
| `fixtures/sample_brief.json` | Hand-written sample so the page works without a key. Not model output. |
| `eval/score.py`, `eval/answer_key.json` | Scores a brief against the planted findings and traps |
| `tests/` | Ten tests for validation, scoring and the decision rules |
| `docs/ENG_PLAN.md` | Engineering plan, following gstack's plan-eng-review structure |
| `scripts/make_synthetic_patient.py` | Regenerates the fax packet and fill history |
| `docs/clara_interview_notes.md` | Notes from the interview with Clara |
| `docs/brainstorm_notes.md` | Team brainstorm notes, with corrections |
| `docs/rubric.md` | Judging criteria and safety questions from the event slides |

Idea scorecard (12 ideas scored on the rubric, with persona reactions): https://claude.ai/artifact/HwfsYDXTK3HQ3qY2CAxr6Y

## Run it

```
pip install -r requirements.txt
pytest                                  # 10 tests, no API key needed
uvicorn app.server:app --port 8000      # then open http://localhost:8000
```

The page opens with a hand-written sample brief (red badge) so the interface works without a key. To run the model:

```
export ANTHROPIC_API_KEY=...            # keep the key out of the repo
# press "Run on the records" in the page, or:
python -m app.covigil.pipeline
python eval/score.py out/brief.json     # findings caught, traps flagged
```

The model call and the audit call have not been run yet. See `docs/ENG_PLAN.md` for the plan, the failure modes and the order of work.

## The demo patient

Hector Reyes, 68, moved from Ohio in October and fell at night on 12 November. The records hide seven things that each need more than one source to catch, for example that the hospital stopped one blood pressure drug and started another, but he still fills and takes both. See `eval/answer_key.md`.

The clinical content was written as textbook cases. **A clinician on the team must confirm each planted finding before the demo.**

## Build order (demos start 2:30)

1. By 12:30: one model call returns the brief and flags with page citations.
2. By 1:30: one screen, brief on the left, flags on the right, accept or dismiss buttons.
3. By 2:00: a second agent audits the brief against the sources; score the run against the answer key.
4. By 2:15: freeze, upload the demo, rehearse once.

## What to say in three minutes

1. Team number, General Medicine track, built for Clara.
2. Show it running: 12-page fax in, one page out, then the flags.
3. The capability we lean on: reasoning across long, messy records from several sources, with a citation behind every line.
4. What surprised us, and where it fell short: caught N of 7 planted findings, flagged M of 4 traps.
