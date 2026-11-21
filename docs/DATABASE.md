# Database Notes

`database/careerlens.db` is created locally at runtime. Schema setup is additive and leaves existing job rows intact.

| Table | Purpose | Ownership |
|---|---|---|
| `jobs` | Imported/processed job records | Shared dataset |
| `skills`, `job_skills` | Existing skill catalog/relationships | Shared dataset |
| `users` | Email, scrypt hash, role, active state, creation time | Account |
| `user_profiles` | Profile fields and user-confirmed skills | `user_id` |
| `resumes` | Extracted text, detected skills, duplicate file hash | `user_id` |
| `assessments` | Self-rated skill and 1–5 level | `user_id` |
| `roadmap_items` | Role-specific skill milestones | `user_id` |
| `career_goals` | User career goals and completion state | `user_id` |
| `applications` | Job application status and notes | `user_id` |
| `recommendation_feedback` | Per-user job relevance ratings | `user_id` |
| `audit_logs` | Login, logout, and administrator account events | Actor ID |
| `dataset_versions` | Immutable imported CSV text, row/column metadata, hash, provenance | Admin/source version |
| `app_settings` | Active dataset version ID | Global |
| `occupations`, `occupation_skills` | Admin-curated occupation relationships | Shared taxonomy |

Foreign keys are enabled for each SQLite connection. User-owned data queries include the current account ID. The admin user list intentionally spans all accounts. SQLite backup/restore uses the online backup API and validates integrity plus required tables before restore. Backups are not encrypted and need secure storage. There is no automated backup rotation.
