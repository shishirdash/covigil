# Answer key for the synthetic patient

**SYNTHETIC DATA. Not a real patient. Do not show this file to the tool; it is for scoring.**

Patient: Hector M. Reyes, 68. New patient visit on 11/23/2026 after a fall on 11/12/2026.
Inputs: `outside_records_fax.pdf` (12 pages), `pharmacy_fills.csv`, `intake_form.md`.

**Before the demo, have a clinician on the team confirm each clinical claim below.** They were written as textbook cases, but no clinician has reviewed them.

## Planted findings the tool should surface (7)

| # | Finding | Where the evidence is | Why it needs more than one source |
|---|---|---|---|
| 1 | **Two overlapping blood pressure drugs.** Lisinopril was stopped at hospital discharge on 08/21 and replaced by losartan, but he still fills and takes both. | Fax p.5 (narrative) and p.6 (STOP lisinopril); fills show lisinopril on 09/09, 10/08, 11/06; intake form lists both | The stop order is only in the hospital record; the continued use is only in the fills and intake form |
| 2 | **Over-the-counter naproxen with a water pill, a blood pressure drug and kidney disease.** Kidney function has worsened: creatinine 1.4, then 1.6, then 1.9. | Naproxen appears only on the intake form; his old doctor advised against it on fax p.3; labs on p.3, p.6, p.10 | Naproxen is in no prescription record or fill history |
| 3 | **Metformin dose needs review.** He takes 2,000 mg a day and his eGFR has fallen from 52 to 36. | Fax p.3 and p.10 (eGFR); fills (metformin 1000 mg twice daily) | Needs the newest lab matched to the current dose |
| 4 | **Drugs that could explain the dizziness and fall.** Standing blood pressure dropped to 98/58. Tamsulosin started 10/02, furosemide started 08/21, and he takes two blood pressure drugs (finding 1). | Fax p.9 (orthostatic vitals), p.8 (tamsulosin start), p.6 (furosemide start), p.10 (ED asks for medication review) | Links the complaint to start dates across three facilities |
| 5 | **Probably off his blood thinner for about three months, with atrial fibrillation.** Last apixaban fill was 07/14 for 30 days. The ED record lists it as a current drug. | Fills (two apixaban fills only); fax p.9 says "apixaban per outside records"; intake form says no bottle | The ED record and the fill history disagree |
| 6 | **Penicillin allergy (hives) that the family does not know about.** | Fax p.3, p.6, p.8 list it; ED record p.9 says no known allergies; intake form says none | Sources conflict |
| 7 | **Workup already done, no need to repeat.** Head CT on 11/12 showed no bleed. Echocardiogram on 08/19 showed normal pumping function (LVEF 55%). Hip X-ray on 11/12 showed no fracture. | Fax p.10 and p.5 | Buried in narrative text |

A good brief would also note two open items the outside doctors asked for: a repeat kidney and potassium blood test (fax p.10, potassium was 5.4), and the hospital follow-up visit that was never scheduled (fax p.6).

## Traps: things the tool should NOT flag

| Item | Why it is fine |
|---|---|
| Hydrochlorothiazide | Stopped at discharge, and fills correctly stop after 08/10. |
| Atorvastatin | Filled as a 90-day supply on 06/12 and 09/09, so there is no gap. |
| Pharmacy change from Ohio to New York | Explained by the move in October. |
| Two prescribers for blood pressure drugs | Expected; the issue is the overlap in finding 1, not the prescribers. |

## How to score a run

- **Catch rate:** planted findings surfaced, out of 7.
- **False alarms:** traps flagged, out of 4, plus any claim with no support in the sources.
- **Citation check:** for each surfaced finding, does the cited page or row actually contain the evidence?

Reasonable extra flags that are not false alarms: naproxen together with a blood thinner raises bleeding risk if apixaban is restarted; potassium of 5.4 while on two overlapping blood pressure drugs.

## Timeline

| Date | Event |
|---|---|
| 06/10/2026 | Office visit in Ohio. Baseline drugs and labs. |
| 07/14/2026 | Last apixaban fill. |
| 08/18 to 08/21/2026 | Hospital stay for leg swelling. Lisinopril and hydrochlorothiazide stopped; losartan and furosemide started. |
| September 2026 | Starts naproxen for knee pain. |
| 10/02/2026 | Urology visit. Tamsulosin started. |
| October 2026 | Moves to New York. |
| 11/12/2026 | Fall at night, emergency visit. |
| 11/23/2026 | New patient visit. |
