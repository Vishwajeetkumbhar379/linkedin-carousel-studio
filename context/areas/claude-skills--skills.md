# claude-skills/skills

Automate job application, contract review, creator outreach, CV tailoring, and LinkedIn carousel creation for recruiters and creators.

- `skills/application-humanizer/SKILL.md`: Edits application texts to sound like a specific person, enforcing hard rules, removing AI cues, preserving facts.
- `skills/application-pack/SKILL.md`: Generates full job application package (CV, cover letter, email, referrals, form answers) after verification, runs humanizer, waits for send. (uses profile.md)
- `skills/creator-contract-review/SKILL.md`: Extracts contract text, runs contract-check, prioritizes risky clauses, proposes fair wording, drafts 150-word negotiation email.
- `skills/creator-shortlist/SKILL.md`: Collects creator data, scores with creator-fit, flags outliers, outputs shortlist with reasons and outreach drafts.
- `skills/designed-cv-tailor/SKILL.md`: Takes HTML CV and job ad, aligns phrasing, renders 2-page ATS-safe PDF, reports changes and gaps.
- `skills/job-scout/SKILL.md`: Queries ATS APIs, verifies live jobs, scores against profile with weighted rubric, outputs ranked table with lane and pay. (uses profile.md)
- `skills/linkedin-carousel/SKILL.md`: Creates LinkedIn carousel deck JSON, enforces style, writes copy per humanizer rules, renders PNG slides and PDF.
