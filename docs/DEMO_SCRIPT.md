# Demo script: three minutes on stage

Team 9, General Medicine track. All patient data is invented.

One person talks, one person drives the laptop. Times are a guide. If a step runs long, cut words, not the safety part at 2:30.

| Time | On screen | Say |
|---|---|---|
| 0:00–0:20 | Title: CoVigil | "We're Team 9, General Medicine. We built this for Clara, a physician. Before every new patient, she spends 5 to 10 minutes digging through faxed records from other hospitals. And she still worries about the detail she skimmed past." |
| 0:20–0:35 | The four inputs, each stamped "invented data" | "Our patient is Hector Reyes, 68. He is invented. He moved from Ohio and fell at night. Clara has a 12-page fax from three facilities, a pharmacy fill history, and an intake form his daughter filled in." |
| 0:35–1:00 | Patient screen (`/patient`) | "Clara told us patients often don't know what they really take. So this step was her idea. Before the visit, the patient confirms each medicine and snaps the bottles." Tap "taking" on two medicines, attach two bottle photos. "Nothing he enters goes to the doctor yet. A pharmacist reviews it first." Switch to pharmacist, press Approve. "Now it is a fourth source." |
| 1:00–1:25 | Main page. Press **Run live**. Streaming text and the timer are visible | "This is a live model call. It reads all four sources at once: the fax, the fills, the form and the photos. You can see the text coming in, and the timer. We give it 60 seconds." |
| 1:25–1:50 | The brief. Point at an origin badge and a source chip | "One page. The badge says this line came from the live run. Every line has a source chip. Click one and it opens the fax page it came from." Click one chip. |
| 1:50–2:15 | The flags, most serious first | "Then a short list of medicines to review. Here: the hospital stopped one blood pressure drug and started another, but he still fills and takes both. That only shows up when you read the discharge page and the fills together." Switch to pharmacist: press "I checked: this is right". Switch to physician: press "I'll review this". On a second item press "Not a concern…" and type a reason. "She can't set one aside without a reason. Both choices are logged." Open "How this brief was made" to show the records, the checks and the log. |
| 2:15–2:30 | The checks and audit panel | "A second pass checks the brief against the sources. It shows any line without a source, and any flag worded like an order. Here is the audit log." Point at it. |
| 2:30–2:50 | Same screen | "What it does not do. It does not diagnose. It does not give orders. It says 'review this' and shows where the evidence is. A pharmacist and the physician decide. All data is invented. We scored it against an answer key with seven planted findings and four traps. That key was never shown to the model." |
| 2:50–3:00 | Score line | "On this run it caught N of 7 and flagged M of 4 traps. The model's strength here is reading long, messy records from several places, with a citation behind every line. Thank you." |

Notes for the driver:

- Changing any patient answer sets the review back to pending. Press Approve again before Run live, or the model gets only three sources.
- The call may take most of the 60 seconds. Keep talking through 1:00–1:25. If the brief is not in yet, describe what the sources are while the text streams.

Fill in N and M from `python eval/score.py out/brief.json` before going on stage. Say the real numbers, even if they are not flattering.

## If the live call stalls

The timer runs to 60 seconds, then the page switches to the last saved run. Say:

> "The timer hit 60 seconds, so it switched to the saved run, labeled as such. Same records, same model, run earlier today. You can see the badge says 'saved', not 'live'."

Point at the badge, then carry on from 1:25. Do not press Run live again on stage.

If the page shows a red "hand-written sample" badge, say so out loud: "This is our hand-written sample, not model output." Then show the flags and decisions anyway.

## Lines to have ready for judge questions

- **Who reviews it before a patient sees it?** No patient sees the brief. Patient input reaches the physician only after a pharmacist approves it.
- **What if someone is in crisis?** This is a pre-visit tool, not a chat. It hands nothing to the patient. Urgent issues go to a person.
- **Where did it fall short?** Say what it missed on this run, by name.
- **Is any of this real?** No. Patient, clinicians, pharmacies and bottles are all invented.

## 30-second rehearsal checklist

- [ ] `ANTHROPIC_API_KEY` is set in the terminal running the server (and not in the repo).
- [ ] Server is up: `uvicorn app.server:app --port 8000`, page loads at http://localhost:8000.
- [ ] Patient screen: answers in, photos attached, pharmacist status is **approved**.
- [ ] `out/brief.json` exists and loads with a "saved" badge, as the fallback.
- [ ] Score numbers N and M written on the card above.
- [ ] Browser zoom set so the back row can read it. Notifications off.
