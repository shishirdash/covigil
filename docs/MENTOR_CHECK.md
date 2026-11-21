# Mentor check: planted findings and traps

**For humans only. Never pass this file to the model.** It restates the answer key. If the model sees it, the score means nothing. Keep it out of `data/` and out of any prompt.

All patient data is invented. The clinical content was written as textbook cases and has not been reviewed by a clinician. Please mark each row, then hand this sheet back to the team.

Sources: **fax** = `data/outside_records_fax.pdf` (page numbers are the fax page stamps, 01 to 12), **fills** = `data/pharmacy_fills.csv`, **intake** = `data/intake_form.md`.

## The 7 planted findings (the tool should raise these)

| # | Item | Where it is planted | Claim to confirm | OK | Change | Note |
|---|---|---|---|---|---|---|
| 1 | Lisinopril and losartan overlap | Fax p.5 (narrative), p.6 (STOP lisinopril); fills: lisinopril 09/09, 10/08, 11/06; intake lists both | Taking an ACE inhibitor and an ARB together after the switch is a real problem worth flagging for review | | | |
| 2 | OTC naproxen with kidney disease | Intake (naproxen 220 mg, 2 tabs twice daily since ~Sept); fax p.3 (old doctor said avoid); creatinine 1.4 (p.3), 1.6 (p.6), 1.9 (p.10) | Regular naproxen with a loop diuretic, an ARB/ACE inhibitor and worsening CKD is worth flagging | | | |
| 3 | Metformin dose vs kidney function | Fills: metformin 1000 mg twice daily; eGFR 52 (fax p.3), 44 (p.6), 36 (p.10) | 2,000 mg a day at eGFR 36 needs dose review (wording: "review", not "stop") | | | |
| 4 | Drugs that may explain the dizziness and fall | Fax p.9 (standing BP 98/58), p.8 (tamsulosin started 10/02), p.6 (furosemide started 08/21), p.10 (ED asks for med review) | Tamsulosin, furosemide and two BP drugs together plausibly contribute to orthostatic hypotension | | | |
| 5 | Probably off apixaban ~3 months, with AF | Fills: apixaban only 06/14 and 07/14 (30 days each); fax p.9 lists it as current "per outside records"; intake says no bottle | The fill gap plus "no bottle" makes a lapse likely; the ED list is not proof he takes it. Flag for review, not "restart" | | | |
| 6 | Penicillin allergy the family does not know | Fax p.3, p.6, p.8 (penicillin, hives); fax p.9 says NKDA; intake says none | Conflicting allergy records should be reconciled; the documented allergy should not be dropped | | | |
| 7 | Workup already done, no need to repeat | Fax p.10 (head CT 11/12 no bleed; hip X-ray no fracture), p.5 (echo 08/19, LVEF 55%) | Saying "already done" is fair and helpful, not a recommendation to skip care | | | |

Open items a good brief should also note: repeat kidney panel and potassium (fax p.10, K 5.4), and the hospital follow-up that was never booked (fax p.6). Fair to include? OK / change: ______

## The 4 traps (the tool should NOT flag these)

| # | Item | Where it is planted | Claim to confirm | OK | Change | Note |
|---|---|---|---|---|---|---|
| T1 | Hydrochlorothiazide | Fax p.6 (STOP); fills stop after 08/10 | Stopped correctly; flagging it would be a false alarm | | | |
| T2 | Atorvastatin | Fills: 90-day supply on 06/12 and 09/09 | No gap; flagging adherence would be a false alarm | | | |
| T3 | Pharmacy change, Ohio to New York | Fills switch to Corner Rx #88 from 10/19; fax p.2 notes the move | Explained by the move; not a concern | | | |
| T4 | Two prescribers for BP drugs | Fills: Whitcombe (lisinopril), Oyelaran (losartan, furosemide) | Normal on its own; the issue is the overlap in finding 1 | | | |

Extra flags the key counts as reasonable, not false alarms: naproxen plus apixaban bleeding risk if apixaban is restarted; potassium 5.4 on two overlapping BP drugs. Agree? OK / change: ______

## Questions about the patient screen

The patient (or family) confirms each medicine as taking / not taking / unsure and can attach bottle photos. A pharmacist approves before anything reaches the physician.

1. Is a pharmacist the right person to review patient input before the physician sees it? Who would do it in a clinic with no pharmacist (nurse, MA, the physician directly)?
2. The screen lists every drug from the fill history, including ones the hospital stopped (hydrochlorothiazide, and apixaban with no bottle). Is it safe to ask a patient "are you taking this?" about a drug that was stopped, or could it prompt him to restart it?
3. Is "taking / not taking / unsure" safe wording for patients? Should the screen add a plain line such as "Do not start or stop any medicine because of this form. Bring all bottles to your visit"?
4. What should the screen say if a patient types something urgent (chest pain, a fall, bleeding)? One option: a fixed message to call 911 or the clinic, with no model reply. Is that enough?

Reviewed by: ____________________   Time: ________
