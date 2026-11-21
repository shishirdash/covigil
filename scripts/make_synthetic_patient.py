from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import csv, sys, os

out = sys.argv[1]
os.makedirs(out, exist_ok=True)

PT = "REYES, HECTOR M   DOB 03/14/1958   MRN SYN-004417"
pages = []

pages.append(("MAPLE HOLLOW FAMILY PRACTICE - MEDICAL RECORDS", """
                      F A C S I M I L E   C O V E R   S H E E T

TO:       New Patient Intake, Primary Care           FAX: (555) 010-0142
FROM:     Medical Records, Maple Hollow Family Practice
          410 Orchard Row, Maple Hollow, OH           TEL: (555) 010-0177
DATE:     11/20/2026
RE:       Release of records - REYES, HECTOR M  DOB 03/14/1958
PAGES:    12 including cover

CONTENTS (as received and compiled by our office; some pages are copies
of records sent to us by other facilities):
  - Registration sheet
  - Office visit 06/10/2026
  - Health maintenance / immunizations
  - Northfield Lake Medical Center discharge summary 08/2026
  - Discharge teaching sheet
  - Lakeview Urology Associates consult 10/02/2026
  - Eastbank Community Hospital emergency dept record 11/12/2026
  - ED discharge instructions
  - Authorization for release

CONFIDENTIALITY NOTICE: The documents accompanying this facsimile contain
confidential health information that is legally privileged. This
information is intended only for the use of the individual or entity
named above. If you are not the intended recipient you are hereby
notified that any disclosure, copying, distribution or action taken in
reliance on the contents of these documents is strictly prohibited. If
you have received this facsimile in error, please notify the sender
immediately by telephone and arrange for return or destruction.

Sent by: K. Dunmore, HIM clerk

*** ALL CONTENT IN THIS PACKET IS SYNTHETIC. NO REAL PATIENT, CLINICIAN
*** OR FACILITY IS DESCRIBED. CREATED FOR A HACKATHON DEMO.
"""))

pages.append(("MAPLE HOLLOW FAMILY PRACTICE", f"""
PATIENT REGISTRATION                                    Printed 11/20/2026

{PT}
Sex: M        Marital status: Widowed        Preferred language: Spanish, English
Address on file: 77 Tannery Ln, Maple Hollow, OH
  ** Note 10/14/2026: pt relocating to New York to live with daughter **
Phone: (555) 010-0193
Emergency contact: REYES, MARISOL (daughter)   (555) 010-0126

PRIMARY INSURANCE:  Medicare Part A/B          ID: SYN-MCR-88213
SECONDARY:          Buckeye Senior Supplement  ID: SYN-BSS-40977
Pharmacy on file:   Corner Rx #12, Maple Hollow OH

PCP: A. Whitcombe, MD
Patient since: 04/2009
Advance directive on file: No
Portal account: Not activated
Interpreter needed: No

GUARANTOR: Self
Financial class: MCR
Last statement balance: $0.00
Copay collected 06/10/2026: $0.00

Consent to treat signed: 01/08/2026
Notice of privacy practices acknowledged: 01/08/2026
Communication preference: phone, daytime
"""))

pages.append(("MAPLE HOLLOW FAMILY PRACTICE", f"""
OFFICE VISIT                                             Date: 06/10/2026
{PT}
Provider: A. Whitcombe, MD                               Visit type: Follow-up

CC: Routine follow up, diabetes and blood pressure. Knee pain.

HPI: 68 y/o man here for 6 month follow up. Feels well overall. Home
sugars 120s-150s fasting. No chest pain, no palpitations, no bleeding.
Bilateral knee pain worse on stairs, using acetaminophen with partial
relief. Asks about stronger options. Advised to AVOID ibuprofen/naproxen
because of kidney function and blood thinner. Continue acetaminophen.

PROBLEM LIST
  1. Type 2 diabetes mellitus (2011)
  2. Hypertension
  3. Chronic kidney disease stage 3a
  4. Atrial fibrillation, persistent (dx 2022) - on anticoagulation
  5. Hyperlipidemia
  6. Benign prostatic hyperplasia - nocturia x2, untreated
  7. Osteoarthritis, both knees

ALLERGIES:  PENICILLIN - hives (childhood, confirmed by pt 2009)

CURRENT MEDICATIONS
  metformin 1000 mg tablet        1 tab twice daily
  lisinopril 20 mg tablet         1 tab daily
  hydrochlorothiazide 25 mg tab   1 tab daily
  apixaban 5 mg tablet            1 tab twice daily
  atorvastatin 40 mg tablet       1 tab nightly
  acetaminophen 500 mg            2 tabs up to three times daily as needed

VITALS: BP 138/82  HR 76 irreg  Wt 198 lb  SpO2 97%  Temp 98.1

LABS (drawn 06/10/2026)
  Creatinine  1.4 mg/dL     eGFR 52       Potassium 4.6 mmol/L
  Glucose 131 mg/dL         HbA1c 7.4 %   Hemoglobin 13.6 g/dL
  LDL 78 mg/dL              Urine albumin/creatinine 142 mg/g (H)

A/P: DM2 at goal. HTN acceptable. CKD 3a stable, recheck 6 mo. AF rate
controlled, continue apixaban. Knees: acetaminophen, PT referral offered,
declined. Urology referral placed for nocturia. RTC 6 months.

Electronically signed: A. Whitcombe, MD  06/10/2026 16:42
"""))

pages.append(("MAPLE HOLLOW FAMILY PRACTICE", f"""
HEALTH MAINTENANCE / IMMUNIZATION RECORD                 Printed 11/20/2026
{PT}

IMMUNIZATIONS
  Influenza, high dose            10/03/2025   L deltoid   lot SYN-F2251
  Influenza, high dose            10/11/2024   L deltoid   lot SYN-F1140
  COVID-19 booster                10/03/2025   R deltoid   lot SYN-C7718
  Pneumococcal conjugate (PCV20)  03/22/2024
  Tdap                            05/16/2019
  Zoster recombinant, dose 1      08/09/2021
  Zoster recombinant, dose 2      11/15/2021

SCREENING
  Colonoscopy                     02/2021  2 small polyps, repeat 5 yr
  Diabetic eye exam               09/2025  no retinopathy
  Diabetic foot exam              06/10/2026  monofilament intact
  AAA ultrasound                  2023  normal caliber
  Lung cancer screening           Not indicated (never smoker)
  Hepatitis C antibody            2018  negative
  PSA                             01/2026  1.9 ng/mL

SOCIAL
  Tobacco: never      Alcohol: rare, holidays      Drugs: none
  Occupation: retired machinist
  Lives alone (wife deceased 2023). Daughter in New York.
  Drives. Independent in ADLs.

FAMILY HISTORY
  Father: MI age 71. Mother: type 2 diabetes, stroke age 80.
  Brother: hypertension.
"""))

pages.append(("NORTHFIELD LAKE MEDICAL CENTER - HOSPITAL MEDICINE", f"""
DISCHARGE SUMMARY                                              Page 1 of 2
{PT}     NLMC acct SYN-7730219
Admitted: 08/18/2026        Discharged: 08/21/2026
Attending: P. Oyelaran, MD  PCP: A. Whitcombe, MD (Maple Hollow FP)

PRINCIPAL DIAGNOSIS: Lower extremity edema and exertional dyspnea,
volume overload.
SECONDARY: Atrial fibrillation, DM2, HTN, CKD stage 3, proteinuria.

HISTORY: 68M with AF on apixaban, DM2, HTN, CKD presented with 2 weeks
of progressive bilateral leg swelling and shortness of breath walking to
the mailbox. No chest pain. Weight up 11 lb from baseline. Exam with 2+
pitting edema to the knees, bibasilar crackles, irregular rhythm rate 90s.

HOSPITAL COURSE: Treated with IV furosemide with good urine output and
weight down 9 lb by day 3. Troponin negative x2. BNP 412. Transthoracic
echocardiogram 08/19/2026: LVEF 55%, mild concentric LVH, moderate left
atrial enlargement, no significant valve disease, no pericardial
effusion. Impression: preserved ejection fraction.

Renal: creatinine 1.5 on admission, 1.6 at discharge. Nephrology was
curbsided regarding proteinuria (UACR 310). Recommendation to change the
RAAS agent: lisinopril was discontinued and losartan 50 mg daily was
started. Hydrochlorothiazide was stopped and replaced with oral
furosemide 40 mg daily. Patient counselled that he should no longer take
lisinopril or hydrochlorothiazide at home.

Endocrine: sliding scale insulin in house, metformin held during
admission and resumed at discharge at prior dose. A1c 7.6.

Rhythm: remained in AF, rate controlled without AV nodal agent.
Apixaban continued without interruption.

Condition at discharge: stable, ambulating, room air.

                                                    (continued next page)
"""))

pages.append(("NORTHFIELD LAKE MEDICAL CENTER - HOSPITAL MEDICINE", f"""
DISCHARGE SUMMARY                                              Page 2 of 2
{PT}

LABS                    08/18/2026      08/21/2026
  Creatinine (mg/dL)       1.5             1.6
  eGFR                     48              44
  Potassium (mmol/L)       4.4             4.9
  Sodium                   137             138
  Glucose                  188             146
  Hemoglobin (g/dL)        13.2            13.4
  BNP (pg/mL)              412             --
  HbA1c (%)                7.6             --

DISCHARGE MEDICATIONS
  NEW       losartan 50 mg tablet       1 tab daily
  NEW       furosemide 40 mg tablet     1 tab every morning
  CONTINUE  metformin 1000 mg tablet    1 tab twice daily
  CONTINUE  apixaban 5 mg tablet        1 tab twice daily
  CONTINUE  atorvastatin 40 mg tablet   1 tab nightly
  STOP      lisinopril 20 mg
  STOP      hydrochlorothiazide 25 mg

Prescriptions for losartan and furosemide sent to Corner Rx #12.

FOLLOW UP
  PCP Dr. Whitcombe within 7-10 days with repeat basic metabolic panel.
  (Appointment not scheduled at time of discharge; pt to call.)
  Daily weights; call for gain of 3 lb in 2 days.

PENDING AT DISCHARGE: none.
ALLERGIES: penicillin (hives).
DIET: 2 g sodium, carbohydrate controlled.  ACTIVITY: as tolerated.

Dictated: P. Oyelaran, MD   08/21/2026 11:05
cc: A. Whitcombe, MD
"""))

pages.append(("NORTHFIELD LAKE MEDICAL CENTER - PATIENT EDUCATION", f"""
DISCHARGE TEACHING RECORD - NURSING
{PT}
RN: T. Halvorsen                                              08/21/2026

Topics reviewed (check = taught, pt/family verbalized understanding)
  [x] Low sodium diet - handout "Shake the Salt Habit" given
  [x] Daily weight, same scale, same time, write it down
  [x] Fluid: no specific restriction ordered
  [x] Signs to call: weight gain, more swelling, short of breath lying flat
  [x] Fall prevention at home: remove throw rugs, night light, rise slowly
  [x] Medication list reviewed with patient
  [ ] Family present for teaching - no family at bedside
  [x] Smoking cessation - N/A never smoker
  [x] Follow up appointment instructions

LOW SODIUM TIPS
  Read labels: aim for less than 2,000 mg sodium per day.
  Avoid canned soups, deli meats, frozen dinners, pickles, soy sauce.
  Rinse canned vegetables. Use herbs, lemon, pepper instead of salt.
  Restaurant meals are often high in salt - ask for sauces on the side.

ACTIVITY
  Walk daily as tolerated. Rest when tired. Elevate legs when sitting.

Barriers to learning: none identified. Learning preference: verbal.
Teach-back performed: yes. Belongings returned: glasses, wallet, phone.
IV removed, site clean and dry. Discharged via wheelchair to private
vehicle driven by neighbor at 13:20.
"""))

pages.append(("LAKEVIEW UROLOGY ASSOCIATES", f"""
NEW PATIENT CONSULTATION                                 Date: 10/02/2026
{PT}
Referring: A. Whitcombe, MD        Seen by: R. Brandt, MD

REASON: Nocturia and weak stream.

HPI: 68M referred for lower urinary tract symptoms for about 2 years,
worse since the summer after a "water pill" was started. Up 3-4 times a
night. Weak stream, hesitancy, some post-void dribbling. No hematuria, no
dysuria, no retention episodes. IPSS score 19 (moderate-severe).

MEDS (per patient, did not bring bottles): metformin, "two blood
pressure pills", water pill, cholesterol pill.
ALLERGIES: penicillin.

EXAM: Abdomen soft, bladder not palpable. DRE: prostate ~40 g, smooth,
symmetric, nontender, no nodules.
Post-void residual by bladder scan: 85 mL.
Urinalysis: negative blood, negative leukocyte esterase, glucose trace.
PSA 09/28/2026: 2.1 ng/mL.

ASSESSMENT: Benign prostatic hyperplasia with lower urinary tract
symptoms. Nocturia likely multifactorial incl. diuretic timing.

PLAN:
  1. Start tamsulosin 0.4 mg capsule, 1 cap nightly at bedtime.
     Rx sent to Corner Rx #12.
  2. Counselled on dizziness/lightheadedness on standing, esp. first
     doses. Rise slowly.
  3. Take furosemide in the morning, limit evening fluids.
  4. Return 6-8 weeks for symptom check. (Pt states he is moving to New
     York later this month; advised to establish with urology there.)

Signed: R. Brandt, MD  10/02/2026
"""))

pages.append(("EASTBANK COMMUNITY HOSPITAL - EMERGENCY DEPARTMENT", f"""
ED PROVIDER RECORD                                             Page 1 of 2
{PT}     ED visit SYN-ED-551902
Arrival: 11/12/2026 03:48    Mode: private vehicle (daughter)
Provider: S. Okafor, MD      Triage acuity: 3

CHIEF COMPLAINT: Fall, dizziness.

TRIAGE VITALS: BP 126/74  HR 80 irreg  RR 16  Temp 98.0  SpO2 98% RA
Pain 3/10 left hip. Glucose fingerstick 142.

HPI: 68M, recently moved from Ohio, got out of bed around 03:00 to
urinate, felt lightheaded "like the room went gray" on standing, fell
onto left side striking hip and left side of head on the dresser. No
loss of consciousness per daughter who heard the fall. No chest pain,
palpitations, focal weakness, speech change, incontinence. Similar
lightheadedness on standing "most mornings for a few weeks". Eating
and drinking normally. No vomiting or diarrhea. No black stools.

PMH: DM2, HTN, CKD, atrial fibrillation, BPH, high cholesterol.
MEDICATIONS (per daughter's list and outside record from 08/2026):
  metformin, losartan, furosemide, atorvastatin, tamsulosin
  Anticoagulation: apixaban 5 mg BID (per outside records)
ALLERGIES: NKDA per patient.

ORTHOSTATIC VITALS (04:20)
  Lying     132/78   HR 72
  Sitting   118/70   HR 80
  Standing   98/58   HR 88   - patient reports lightheadedness

EXAM: Alert, oriented x3. 2 cm contusion left parietal scalp, no
laceration. Pupils equal. Neck nontender. Heart irregularly irregular.
Lungs clear. Trace ankle edema. Left hip: tender over greater
trochanter, full range of motion, bears weight. Neuro: nonfocal, gait
steady with standby assist.

                                                    (continued next page)
"""))

pages.append(("EASTBANK COMMUNITY HOSPITAL - EMERGENCY DEPARTMENT", f"""
ED PROVIDER RECORD                                             Page 2 of 2
{PT}

RESULTS 11/12/2026
  Creatinine 1.9 mg/dL (H)    eGFR 36       BUN 38 (H)
  Potassium 5.4 mmol/L (H)    Sodium 136    Bicarbonate 21
  Glucose 142                 Hemoglobin 13.1    Platelets 211
  Troponin <0.01              INR 1.0
  ECG: atrial fibrillation, ventricular rate 84, no acute ST changes.
  CT HEAD without contrast: no acute intracranial hemorrhage, no
    fracture, no mass effect. Mild chronic small vessel changes.
  XR LEFT HIP/PELVIS: no fracture or dislocation.

ED COURSE: 500 mL normal saline given. Repeat standing BP 110/64 with
improved symptoms. Ambulated in hallway without assistance. Observed 4
hours with no neurologic change. Head CT reviewed given reported
anticoagulant use - negative.

IMPRESSION:
  1. Mechanical fall with orthostatic hypotension
  2. Scalp contusion, left hip contusion
  3. Acute on chronic kidney disease vs progression, mild hyperkalemia

DISPOSITION: Discharged home with daughter 08:15.

PLAN / RECOMMENDATIONS TO OUTPATIENT PROVIDER:
  - Patient has no local PCP yet. Daughter to arrange new patient visit.
  - Recommend outpatient medication review; several agents may
    contribute to low standing blood pressure.
  - Repeat basic metabolic panel within 1 week (creatinine, potassium).
  - No medication changes made in the ED.
  - Return precautions for head injury reviewed.

Signed: S. Okafor, MD  11/12/2026 08:22
"""))

pages.append(("EASTBANK COMMUNITY HOSPITAL - EMERGENCY DEPARTMENT", f"""
DISCHARGE INSTRUCTIONS - HEAD INJURY AND FALL
{PT}
Date of visit: 11/12/2026

You were seen today after a fall. Your CT scan and X-rays did not show
bleeding or broken bones.

WATCH FOR THE NEXT 48 HOURS. Return to the emergency department or call
911 if you have:
  - A headache that gets worse or will not go away
  - Repeated vomiting
  - Confusion, unusual sleepiness, or trouble waking up
  - Weakness, numbness, trouble speaking or seeing
  - A seizure
  - Fainting or another fall
  - Black or bloody stools

AT HOME
  - Have someone stay with you for the first 24 hours.
  - Use ice on sore areas 15 minutes at a time.
  - You may take acetaminophen (Tylenol) for pain as directed on the
    package.
  - Get up slowly. Sit on the edge of the bed for a minute before
    standing. Use a night light.
  - Drink fluids unless your doctor has told you to limit them.

FOLLOW UP
  - See a primary care doctor within 1 week. Bring ALL of your pill
    bottles, including over-the-counter medicines.
  - You need a repeat blood test of your kidney function and potassium.

I have received and understand these instructions.
Patient/representative signature: [signed - M. Reyes, daughter]
Nurse: J. Castellano, RN   Time: 08:10
"""))

pages.append(("MAPLE HOLLOW FAMILY PRACTICE - MEDICAL RECORDS", f"""
AUTHORIZATION FOR RELEASE OF HEALTH INFORMATION
{PT}

I authorize Maple Hollow Family Practice to release my health
information to:  New Patient Intake, Primary Care (New York)

Information to be released:
  [x] Office notes, last 12 months     [x] Laboratory results
  [x] Records received from other facilities
  [x] Medication list                  [ ] Billing records
  [ ] Mental health / substance use records (requires separate form)

Purpose: [x] Continuing care   [ ] Insurance   [ ] Legal   [ ] Personal

This authorization expires 12 months from the date signed. I understand
I may revoke this authorization in writing at any time, except to the
extent action has already been taken. I understand that information
disclosed under this authorization may be re-disclosed by the recipient
and may no longer be protected by federal privacy rules. Treatment,
payment, enrollment or eligibility for benefits will not be conditioned
on signing this authorization.

Signature: [signed - Hector M. Reyes]            Date: 11/18/2026
Witness:   [signed - Marisol Reyes]              Relationship: daughter

OFFICE USE ONLY
  Request received: 11/18/2026 by fax       ID verified: yes
  Processed by: K. Dunmore                  Date sent: 11/20/2026
  Pages sent: 12        Method: fax         Fee: waived (continuity)

                          *** END OF TRANSMISSION ***
"""))

c = canvas.Canvas(os.path.join(out, "outside_records_fax.pdf"), pagesize=letter)
W, H = letter
n = len(pages)
for i, (src, body) in enumerate(pages, 1):
    c.setFont("Courier", 7.5)
    c.drawString(40, H - 28, f"11/20/2026 08:{13+i:02d}   FROM: MAPLE HOLLOW FP (555) 010-0177   TO: (555) 010-0142   PAGE {i:02d}/{n:02d}")
    c.line(40, H - 33, W - 40, H - 33)
    c.setFont("Courier-Bold", 10)
    c.drawString(54, H - 56, src)
    c.setFont("Courier", 9)
    y = H - 74
    for line in body.strip("\n").split("\n"):
        assert len(line) <= 90, (i, len(line), line)
        c.drawString(54, y, line)
        y -= 11
    assert y > 40, (i, y)
    c.setFont("Courier", 7.5)
    c.drawCentredString(W / 2, 22, "SYNTHETIC DATA - NOT A REAL PATIENT - HACKATHON DEMO ONLY")
    c.showPage()
c.save()

rows = []
def fills(drug, strength, sig, qty, days, prescriber, dates):
    for d, ph in dates:
        rows.append([d, drug, strength, sig, qty, days, prescriber, ph])
OH, NY = "Corner Rx #12 (Maple Hollow OH)", "Corner Rx #88 (New York NY)"
fills("metformin", "1000 mg", "1 tab twice daily", 60, 30, "Whitcombe A",
      [("2026-06-12", OH), ("2026-07-11", OH), ("2026-08-10", OH), ("2026-09-09", OH), ("2026-10-08", OH), ("2026-11-06", NY)])
fills("lisinopril", "20 mg", "1 tab daily", 30, 30, "Whitcombe A",
      [("2026-06-12", OH), ("2026-07-11", OH), ("2026-08-10", OH), ("2026-09-09", OH), ("2026-10-08", OH), ("2026-11-06", NY)])
fills("hydrochlorothiazide", "25 mg", "1 tab daily", 30, 30, "Whitcombe A",
      [("2026-06-12", OH), ("2026-07-11", OH), ("2026-08-10", OH)])
fills("apixaban", "5 mg", "1 tab twice daily", 60, 30, "Whitcombe A",
      [("2026-06-14", OH), ("2026-07-14", OH)])
fills("atorvastatin", "40 mg", "1 tab nightly", 90, 90, "Whitcombe A",
      [("2026-06-12", OH), ("2026-09-09", OH)])
fills("losartan", "50 mg", "1 tab daily", 30, 30, "Oyelaran P",
      [("2026-08-22", OH), ("2026-09-20", OH), ("2026-10-19", NY), ("2026-11-17", NY)])
fills("furosemide", "40 mg", "1 tab every morning", 30, 30, "Oyelaran P",
      [("2026-08-22", OH), ("2026-09-20", OH), ("2026-10-19", NY), ("2026-11-17", NY)])
fills("tamsulosin", "0.4 mg", "1 cap nightly at bedtime", 30, 30, "Brandt R",
      [("2026-10-02", OH), ("2026-11-01", NY)])
rows.sort()
with open(os.path.join(out, "pharmacy_fills.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["patient", "fill_date", "drug", "strength", "directions", "quantity", "days_supply", "prescriber", "pharmacy"])
    for r in rows:
        w.writerow(["REYES, HECTOR M (SYNTHETIC)"] + r)
print(n, "pages;", len(rows), "fills")
