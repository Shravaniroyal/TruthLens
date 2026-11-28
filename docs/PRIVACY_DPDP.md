# TruthLens: Privacy and Data Handling Note (DRAFT v1)

**Scope.** TruthLens is a visual tamper-screening aid for documents (e.g. PAN, Aadhaar images, marksheets). It is NOT KYC, NOT UIDAI/DigiLocker verification, and does not confirm a document is genuine in law. Results are screening signals for a human reviewer.

**Roles.** The institution using TruthLens decides why and how documents are checked, so it is normally the Data Fiduciary under the DPDP Act, 2023. TruthLens acts as its processing tool. Institutions should give notice to the individual and have a lawful basis (consent or another permitted ground) before upload.

**Data processed.** Uploaded document image/PDF (in memory during analysis), model score, Grad-CAM/ELA visuals, OCR-extracted fields, operator and reviewer names.

**What is stored.**
- Batch job record (JSON): verdicts, masked fields, case id, operator. Uploaded file bytes are not written by the job path.
- Review queue item: filename, truncated content hash (16 chars), doc type, confidence, MASKED fields, reviewer decision.
- Case pack PDF: generated on request from masked data.

**What is logged.** Audit and application logs record only: truncated content hash, extension, size, dimensions, verdict, doc type, timings, request id. Logs do not contain filenames, OCR text, or full Aadhaar/PAN numbers. This is enforced by an automated test (tests/test_log_privacy.py).

**Masking.** Aadhaar and PAN values are masked before storage or display in reports (e.g. XXXXX1234X). Full numbers are not persisted.

**Retention.** Job records and review items are deleted after TRUTHLENS_RETENTION_DAYS (default 7). Logs rotate by size (app log 5 MB x 6 files, audit log 5 MB x 11 files); delete the logs folder on your own schedule if shorter retention is needed.

**Individual rights.** On request, the institution can locate a case by case id, correct it, or delete it (delete the case files under data/). Grievance contact: [institution to fill in].

**Security.** Upload validation (type, size, pixel limit), no public default deployment, access limited to named operators and reviewers. Deploy behind HTTPS and access control; do not expose the API publicly without authentication.

**Breach.** Institution to follow its own breach-notification procedure; TruthLens logs contain no full ID numbers to leak.

**Limits.** Model accuracy is not perfect. UNCERTAIN and FAKE results need human review, and no adverse decision should rest on TruthLens alone.

*This note is a technical description, not legal advice. Have the institution's counsel review before pilot use.*
