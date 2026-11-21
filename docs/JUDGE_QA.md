# Judge questions and short answers

Team 9, General Medicine. Two minutes of questions follow the three-minute demo. Fill in the bracketed numbers after the first real model run.

| Likely question | Answer in one or two sentences |
|---|---|
| Does it diagnose? | No. It shows where the records disagree and where the evidence is. It never names a diagnosis or says stop, start or change a drug. |
| Who is in the loop? | Two named people. A pharmacist verifies the medication flags, and Clara, the physician, accepts or dismisses each one. A dismissal needs a reason, and every action is logged with a name and time. |
| What if the clinic has no pharmacist? | Clara gets the same brief with every flag marked unverified, plus a call sheet for staff. |
| Is any of this real patient data? | No. Hector Reyes, the fax packet, the fill history and the bottle photos are all invented. |
| What did it miss? | We hid seven findings and set four traps. It caught [N] of 7 and wrongly flagged [M] of 4. [Name the one it missed.] |
| How do you know the citations are right? | A second pass checks every line against the page it cites. It found [K] problems. Clara can also open the cited fax page from any line. |
| What does the patient screen do, and is it safe? | The family confirms which medicines are actually taken and can photograph the bottles. It asks nothing clinical and gives no advice. A pharmacist reviews the answers before they are used. [Check before the demo that the screen says it is software and tells the patient to call the clinic or 911 for anything urgent.] |
| Which Fable 5.2 capability does it lean on? | Reading a long, messy fax together with two other sources and finding what only shows up when they are compared, with a page citation on every line. |
| Where did Fable 5.2 fall short? | [Fill in from the run: a missed finding, a wrong page, or a slow call.] |
| How is this different from an EHR summary or an AI scribe? | Those work inside one health system or inside the visit. This works before the visit on outside records that arrive by fax, and compares them with what the pharmacy actually dispensed. |
| Who pays for it? | The practice or health system. Pharmacist time is usually billed through the physician. We have not tested pricing. |
| Does this raise liability? | It is designed to lower it: one named decision maker per flag, a recorded reason, a short list so flags get read, and a clear label on anything unverified. We are not lawyers and have not had it reviewed. |
| Why only one patient? | Five hours. One patient with planted findings let us measure misses honestly. It has not been tested on other charts. |
| What is next? | Clara's suggestions: the patient photo step in real use, and a clinician review of the medical content. Then more patients. |

## Before you walk up

- [ ] The page shows the model's brief, not the red "sample" badge.
- [ ] You know the three numbers: findings caught, traps flagged, citation problems.
- [ ] A clinician has confirmed the seven findings, or you say plainly that the medical content is unreviewed.
- [ ] The demo is uploaded to the Team 9 folder.
- [ ] Opening line: "Team 9, General Medicine, built for Clara."
