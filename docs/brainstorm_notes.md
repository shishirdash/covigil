# Team brainstorm notes

## Corrections to these notes

- The notes say diagnostic errors are 33% of all malpractice claims. Published figures for all paid claims are lower: 28.6% in a Johns Hopkins review of 350,706 paid claims, and 26.6% in a 20-year closed-claims analysis. A figure of 34% applies only to claims involving death or serious disability. Say "over a quarter of paid claims" or leave it out.
- "Cross-reference AI against your diagnosis" invites the question of whether the tool diagnoses. Say it catches where the records disagree with each other.
- The claim that AI beats fatigued physicians at reading micro-expressions has not been checked. It is not part of the build.
- "Pharmacovigilance" usually means population-level drug safety monitoring for regulators and drug makers. Our build is a patient-level medication check for one clinician.

## Context and problem space

- Hackathon session focused on healthcare AI, building for a demo with a scoring rubric.
- Rubric constraints: one real problem, one real user, software must not diagnose.
- Key informant: Clara (physician), who emphasized doctor-led patient interaction with no software during visits.
  - All her tooling preference is pre-charting focused.
  - Patient interaction is fully human assessment, consults called as needed.

## Healthcare data and workflow pain points

- Pre-charting is the core bottleneck: retrieving messy, unstructured records from other hospitals.
  - Data arrives via fax, PDF or phone call, not usable structured data.
  - Even Epic-to-Epic transfers are difficult due to hospital territoriality and HIPAA restrictions.
  - Independent practices lack Epic entirely, buried in paperwork.
- Two distinct time costs: time to retrieve records, and time to summarize and synthesize them. The build addresses the second.
- Ambient recording idea raised (watch, necklace, small device). Needs patient consent, and existing companies are already in this space. Dropped.

## Personas

- Clinician (Clara): pre-charting, information retrieval. **The one user we build for.**
- Patient: largely unaware of pre-charting burden, 15-minute interaction window.
- Consults and physician assistants: specialists called for second opinions.
- Past care teams: source of historical records.
- Hospital system: holds the budget. Mid-size community hospitals seen as a realistic first customer. Keep this to a one-line answer if a judge asks who pays.

## Idea convergence

- Pre-visit brief: synthesize prior records before the visit.
- Medication safety check: flag possible medication errors, drug interactions and unaddressed symptoms. Does not diagnose; leaves decisions to the clinician. Patients on five or more medications are at higher risk.
- Presented as one workflow: build the patient story, then run the medication check.

## Reference read

"Automated Classification of Adverse Events in Pharmacovigilance" (Dev, Zhang, Rao, Voyles, IEEE BIBM 2017). Drug-company side of the problem, not ours. Useful points: they chose explainable models over more accurate ones because auditors need to see the logic; overall accuracy hid a model that caught only 24% of serious cases; ranking by seriousness is a cheap feature.
