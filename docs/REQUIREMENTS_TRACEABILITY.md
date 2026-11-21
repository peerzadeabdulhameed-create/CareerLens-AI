# CareerLens AI Requirements Traceability — Continuation

Current against the original master prompt plus the requested enhancements. Statuses describe implementation and executed evidence, not page presence.

## Real user data and demo removal follow-up

| Requirement | Status | Evidence / limitation |
|---|---|---|
| Stop auto-loading the 60-row demo CSV | Completed | Application default points to local `data/esco_occupations.csv`; regression tests verify 3,007 occupation rows and ESCO metadata. |
| Remove generated demo account and related sample records | Completed | The local DB's only account was `demo@careerlens.local`; its profile, assessment, application, goals, roadmap items and login audit rows were identified and removed. Temporary backups were removed after verification. |
| Remove fake employer/listing entities from default experience | Completed | ESCO occupations are presented as occupation profiles, not jobs/vacancies; company/location filters were removed from Data Explorer. |
| Real dataset name, provenance and record counts | Completed | Local ESCO v1.1.1 conversion: 3,007 occupations, 13,896 skills in source table, 123,788 source occupation-skill relations; exact user-facing attribution and adaptation details in `data/ESCO_SOURCE.md`. |
| Use the authentic occupation-skill relationships in analysis | Completed | The app parses essential and optional ESCO links directly for gap, readiness and roadmap features; a regression test verifies all 123,788 labels are retained across all 3,007 occupations. |
| Licence transparency | Partial | European Commission ESCO reuse terms are documented with attribution; separate licence for the Tabiya CSV conversion remains “Not verified.” |
| Empty dataset and empty profile skill behavior | Implemented | No fabricated default skills; missing local data produces an empty dataset and warning. Workflow verification is covered by the test run below. |

The existing versioned administrator CSV import remains supported. The SQLite jobs table is replaced by the selected active CSV through existing indexed upserts; no broad database-clearing behavior was introduced.

| Requirement | Status | Implementation / test evidence |
|---|---|---|
| Preserve Python/Streamlit/SQLite and existing analysis algorithms | Completed and tested | Existing preprocessing, skill extraction, TF-IDF, cosine and role-gap modules retained; original tests pass |
| Secure registration and login, admin provisioning, logout and password changes | Completed and tested | scrypt hashes; public signup is user-only; admin provisioning; sign-in, logout, password change and current-session invalidation exercised |
| Server-side current role/account validation and admin access control | Completed and tested | Principal revalidated every rerun; auth-version invalidation; admin page allowlist; inactive user and role tests; all admin page renders passed |
| Per-user profile, resume, assessment, goals, applications, feedback, roadmap | Implemented but not fully tested | Every read/write uses account ID; profile isolation test; user portal page renders; not every form action browser-driven |
| User data export and deletion | Implemented but not fully tested | JSON export and password-confirmed user delete; account deletion helper tested; export UI not round-trip tested |
| Resume PDF/TXT validation and local extraction | Implemented but not fully tested | Generated PDF text was extracted using PyMuPDF; invalid PDF and duplicate file tests pass; upload widget itself not browser-upload tested; no OCR/structured entity extraction |
| Explainable job recommendations | Implemented but not fully tested | Existing TF-IDF score plus taxonomy-based matching/missing skills; explanation utility tested and job matcher page rendered |
| Transferable skills, career comparison, readiness | Implemented but not fully tested | Shared skills across role records, dataset coverage proxy, comparison table; utilities tested and page rendered; proxy is not employment probability |
| Roadmap and learning recommendations | Implemented but not fully tested | Dataset-ranked missing skills, saved milestone completion, official-documentation search labels; page rendered; no course catalog/provider recommendations |
| Resume improvement suggestions | Implemented but not fully tested | Transparent structure/length/skill-count rules; unit helper tested, not expert/ATS validation |
| Application tracking and user career goals | Implemented but not fully tested | Account-owned SQLite entities and page forms; page rendered; submission/edit interactions not fully exercised |
| User relevance feedback and admin evaluation dashboard | Implemented but not fully tested | 1–5 per-user feedback, admin mean/count by recommendation, descriptive corpus coverage; no relevance-label accuracy or hiring outcome metrics exist |
| Dataset validation, immutable versions, activation, provenance | Implemented but not fully tested | CSV title validation, 10 MB limit, content SHA-256 dedupe, persisted active version/rollback, URL/license/date metadata; DB helpers tested; uploader/activation not browser-upload tested |
| Job management | Partially implemented | Admin data editor saves edited job dataset as a new version; no separate DB CRUD, record-level provenance, or deletion confirmation workflow |
| Occupation/skill knowledge relationships | Partially implemented | Admin-curated occupation-skill links plus observed dataset co-occurrences and transferable intersections; not an external validated occupational taxonomy |
| Canonical skill and synonym management | Partially implemented | Skills can be added through curated mappings; no synonym editing/normalization administration UI |
| Admin user management and audit | Implemented but not fully tested | Search, activation, one-time temporary password reset, login/logout/action logs; page render tests passed, reset/activation UI actions not exercised through browser |
| Admin dataset/job management | Implemented but not fully tested | CSV validation, history, activation/rollback, provenance and job data editor; upload/edit/rollback widgets not exercised through a real browser |
| Admin skill and occupation management | Partially implemented | Admin can curate occupation-to-observed-skill mappings; no complete canonical skill/synonym/category CRUD or occupation relationship editor |
| Admin model lifecycle and reports | Partially implemented | Evaluation dashboard displays dataset coverage and user feedback; no model registry/configuration/training/deployment or report export |
| Explainable/hybrid recommendation scorer | Partially implemented | TF-IDF similarity plus matching/missing skill explanation; structured factors are not combined into a validated hybrid score |
| SQLite backup and recovery | Implemented but not fully tested | In-memory SQLite backup/restore helpers; integrity/schema validation and round-trip test pass; admin download/restore controls rendered but not clicked in UI |
| Offline operation | Implemented but not fully tested | Core job matching and gap analysis tested with socket connections blocked; no live API dependencies; app not tested with OS-level network disabled |
| Responsive UI and accessibility | Partially implemented | Streamlit responsive layout and light theme; all pages rendered in AppTest; no mobile visual, keyboard, screen-reader, or WCAG contrast audit |
| Forecasting and dated market trends | Not implemented | ESCO occupation classifications have no dated vacancy history; no forecast fabricated |
| Live job APIs, external ML, model training/deployment | Not implemented | No service credentials, labeled outcomes, or deployed model |
| Automated email recovery, remember-me, login rate limiting | Not implemented | Admin can issue one-time temporary passwords out of band; no email delivery/session persistence/rate limiting |
| Production-grade security | Not implemented | Local academic app; no encrypted DB/backup, key rotation, deployment-grade CSRF/identity provider, or external penetration test |

## Executed verification

- `python -m pytest -q`: **17 passed**; `python -m compileall -q app.py src scripts tests`: passed.
- Streamlit AppTest: temporary user registration/sign-in passed; profile editing and actual PDF upload/extraction/save passed. User Home, Job Matcher, Career Explorer, Skill Gap, Roadmap, Comparison, Learning Resources, Progress, and Data Explorer rendered without exceptions. Admin Dashboard, User Management, Dataset Management, Model Evaluation, and Audit Logs also rendered without exceptions. All temporary accounts were removed.
- Generated a real PDF in memory with PyMuPDF; extraction returned expected Python/SQL text. Duplicate identical resume save was rejected.
- Core matching against the actual ESCO data returned five ranked occupations; skill-gap analysis returned data-based potential gaps.
- SQLite tests cover preservation of existing job row, new additive schema, isolated profiles, disabled-account session invalidation, dataset version activation, backup/restore, and password verification.
- Localhost Streamlit health endpoint on port 8501 returned `ok`. SQLite contains 3,007 occupation records and no demo users, resumes, assessments, applications, goals, roadmap rows, or demo-company records after test cleanup.
- Regression coverage confirms the essential/optional link parser preserves the 123,788 ESCO skill links (including commas within labels) and that unknown custom source/license metadata stays “Not verified.”

An initial AppTest run hit the runner's default 3-second timeout; rerunning with a 20-second timeout succeeded. The app test runner emitted a deprecation warning for `use_container_width`; calls were migrated to `width="stretch"` and the minimum Streamlit dependency raised. A first dataset fixture used a nonexistent FK actor and failed; the fixture was corrected to use a nullable actor, after which the suite passed.
