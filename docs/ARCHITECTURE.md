# CareerLens AI Architecture

## Runtime

The project is a single-process Streamlit application. `app.py` coordinates the page navigation, reads the selected CSV, calls the analysis modules, and renders Streamlit UI. `src/` contains the data loader, preprocessing, skill dictionary extraction, market summaries, TF-IDF/cosine matching, skill gap calculation, presentation helpers, and SQLite access.

SQLite is local and initialized with additive migrations. Existing `jobs`, `skills`, and `job_skills` tables and records remain in place. User profile, resume, assessment, roadmap, goal, application, and feedback records reference the authenticated user ID. Passwords use Python's scrypt KDF with a random per-password salt. Registration only assigns the `user` role. The session principal and role are refreshed from SQLite every Streamlit rerun; changing `auth_version` invalidates older sessions. An administrator is provisioned only from `CAREERLENS_ADMIN_EMAIL` and `CAREERLENS_ADMIN_PASSWORD`, and only if that email does not already exist.

## Recommendation calculation

The existing matcher vectorizes user profile text and job descriptions with TF-IDF and ranks cosine similarity. A score is lexical similarity, not an employment probability. Skill-gap results count skills found in records matching the selected role and rank missing terms using the application's transparent taxonomy/data. There is no trained predictive model, accuracy claim, or semantic model.

## Data flow

The bundled ESCO v1.1.1 occupation and skill CSV is the local default. Administrator CSV imports are validated, fingerprinted, versioned in SQLite, and activated explicitly; normalization and dictionary skill extraction feed descriptive dataset summaries, gap analysis, and TF-IDF matching. Source URL, licence notes, and collection date for imports remain administrator-entered provenance; unknown fields are not inferred. No external service is called. Resume PDF extraction uses local PyMuPDF; text extraction is not OCR.

## Current boundaries

Career comparisons, readiness coverage, transferable skills, feedback summaries, and demand counts are descriptive. Occupation links can be administrator curated; dataset-derived links remain co-occurrence evidence. Learning suggestions are documentation search labels, not a course catalog. Demand forecasting, live jobs, model accuracy evaluation, email recovery, and model training/deployment are not implemented. SQLite backup/restore and account data export/deletion are local. Streamlit session state is not a persistent remember-me option or production identity provider.
