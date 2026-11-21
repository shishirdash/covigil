# Engineering plan

Team 9, General Medicine track. Demos start 2:30 pm. Written 12:40 pm.

This follows the structure of gstack's `/plan-eng-review` (scope challenge, architecture, code quality, tests, performance, failure modes, decisions). gstack is not installed in the session that wrote this, so it is a condensed pass over that structure, without gstack's interactive decision ledger or its independent "outside voice" review. Run `/plan-eng-review` on this file from a Claude Code session with gstack installed if you want the full pass.

## Step 0: Scope challenge

**What is the smallest thing that wins the rubric?** One screen where Clara sees a brief with sources, a short list of medication flags, and decides on each one. Everything else is optional.

| In scope (built in this scaffold) | Stretch, only if the core works by 1:30 | Not in scope today |
|---|---|---|
| One model call: three sources in, brief and flags out as JSON | Second-pass audit shown on screen (endpoint exists, untested) | Fetching records from other hospitals |
| One screen: brief left, flags right | Patient photo of pill bottles as a fourth source (Clara's suggestion) | A patient-facing chat or app |
| Accept or dismiss per flag, reason required to dismiss, logged | Opening the cited fax page beside the brief instead of in a new tab | A separate pharmacist queue or login |
| Pharmacist stamp: role switch, note, verified or unresolved | | EHR integration, user accounts, a database |
| "Clinic has no pharmacist" switch, flags shown as unverified | | More than one patient |
| Scoring script against the answer key | | |

**Complexity check.** Three Python files, one HTML file, no build step, no database. State is one JSON file. This is the least that supports the demo.

**What already exists.** Synthetic sources in `data/`, the prompt in `prompts/brief_prompt.md`, the answer key in `eval/`.

## 1. Architecture

```
 data/outside_records_fax.pdf ─┐
 data/pharmacy_fills.csv ──────┼─▶ pipeline.generate_brief() ──▶ validate_brief() ──▶ out/brief.json
 data/intake_form.md ──────────┘        (1 model call)             (schema.py)            │
                                                                                          ▼
 eval/answer_key.json ──▶ eval/score.py ◀──────────────────────────────────────── GET /api/brief
   (never sent to the model)                                                              │
                                                                                          ▼
                                    pipeline.audit_brief() ──▶ out/audit.json       app/static/index.html
                                       (2nd model call)                              brief │ flags
                                                                                          │
                              out/state.json ◀── POST /api/verify   (pharmacist: verified / unresolved + note)
                              (verifications,  ◀── POST /api/decision (physician: accept / dismiss + reason)
                               decisions, log)
```

Flag lifecycle:

```
 draft ──(pharmacist)──▶ verified ──┐
   │                    unresolved ─┼─(physician)──▶ accepted
   └──(no pharmacist: unverified)───┘              dismissed (reason required)
```

**Two shapes considered.**

- **A. One call over everything (chosen).** The PDF, fills and intake form go to the model together. Cross-source findings are the whole point, and one call lets the model see all sources at once. Fewest moving parts.
- **B. Extract per page with a lighter model, then synthesize.** Cheaper per call and easier to cite, but it is two stages to debug with under two hours left, and extraction can drop the detail that matters.

A is right for one 12-page patient. B becomes worth it for long charts or many patients.

**Human in the loop.** The model writes `out/brief.json` and nothing else. Only the two POST endpoints change state, and each records a named person and a time. A dismissal without a reason is rejected by the server, not just by the page.

**Trust boundary.** `eval/` holds the answers. `pipeline.source_blocks()` reads only `data/`, the server mounts only `data/` for static files, and a test checks the sources do not contain answer-key text.

## 2. Code quality

- The prompt lives in one place, `prompts/brief_prompt.md`. The pipeline reads the system prompt out of it.
- The fixture `fixtures/sample_brief.json` is hand-written and labelled as such. The page shows a red badge whenever it is displaying the fixture, so sample data cannot be mistaken for model output on stage.
- No abstraction beyond what is used: no base classes, no plugin points.

## 3. Tests

Run `pytest`. Ten tests, all passing on the scaffold.

| Behavior | Test |
|---|---|
| A valid brief passes validation | `test_fixture_passes_validation` |
| A statement with no source is reported | `test_missing_sources_is_reported` |
| More than six flags is reported | `test_too_many_flags_is_reported` |
| A flag worded as an order is reported | `test_order_wording_is_reported` |
| Scoring counts findings, misses and traps | three `score` tests |
| JSON is recovered from a chatty model reply | `test_parse_json_ignores_surrounding_text` |
| The answer key never reaches the model | `test_sources_never_include_the_answer_key` |
| Dismissal needs a reason; decisions and verifications are logged | `test_dismissal_needs_a_reason` |

**Not tested: the model.** There was no API key when this was written, so `generate_brief()` and `audit_brief()` have never run. The evaluation for the model is `eval/score.py` against the seven planted findings and four traps. It matches keywords, so read its result next to the brief before quoting numbers.

## 4. Performance

One call with a 12-page PDF. Expect it to take long enough to be awkward live, and it could fail on stage. So:

- Generate before the demo. The result is cached in `out/brief.json` and the page loads it instantly.
- Keep the "Run on the records" button for showing it live if there is time, with the cached result as the fallback.

## Failure modes

| What can go wrong | Handled? | What the user sees |
|---|---|---|
| No API key, or the call fails | Yes | Error text in the header; the page keeps the last brief or the sample |
| Model returns text around the JSON | Yes | Parsed anyway |
| Model returns no JSON | Yes | Error text; nothing overwritten |
| Model returns a statement with no source, more than six flags, or an order | Reported | Listed in `validation_problems` in `out/brief.json`. **Not yet shown on the page.** |
| Model cites the wrong page | Only by the audit pass, which is untested | "Check against sources" panel |
| Model's flag ids change between runs | Yes | Reviews are cleared when a new brief is generated |
| Sample shown instead of real output | Yes | Red "hand-written sample" badge |
| Two people decide at once | No | Last write wins. Fine for one laptop. |

## Decisions for the team

1. **Patient-facing photo step (Clara's suggestion).** Recommendation: do not build a patient-facing flow today. It needs its own safety handling under the event rules, and there are no bottle photos in the synthetic data. If someone has 30 minutes free after the core works, add bottle photos as a fourth input to the same model call, with no patient interface. Otherwise say it on stage as the next step, credited to Clara.
2. **Live call or cached on stage.** Recommendation: cached, with the live button as a bonus.
3. **Who owns what.** Suggested split for the next hour:
   - One person: get `generate_brief()` running with a key, fix the prompt, run `eval/score.py`.
   - One person: the page (layout, wording, showing `validation_problems`).
   - One person: clinical check of the seven findings with the mentor, and the three-minute script.

## Order of work

1. `pip install -r requirements.txt`, `pytest`, `uvicorn app.server:app --port 8000`. Confirm the sample loads.
2. Set `ANTHROPIC_API_KEY`, press "Run on the records". Fix whatever breaks first.
3. `python eval/score.py out/brief.json`. Write down caught, missed and traps flagged.
4. Press "Check against sources". Fix the audit prompt if needed.
5. Freeze by 2:15. Rehearse once.
