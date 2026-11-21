# CareerLens AI

## Abstract
CareerLens AI is a data-driven occupation and skill exploration platform for students. It compares a user's profile and resume with standardized occupation descriptions and linked skills to support career exploration. It does not provide live vacancies or measure hiring probability.

## Problem Statement
Students often struggle to translate their current skills into career options. Standardized occupation profiles and linked skills can provide a transparent starting point for that exploration.

## Objectives
- Explore standardized occupations and their linked skills.
- Identify frequently linked skills and common occupation profiles.
- Compare a student's skills against a target occupation.
- Rank occupations based on textual similarity to a student profile.
- Explore the underlying data and export filtered results.
- Explain methodology, assumptions, and limitations clearly.

## Existing System
Many students rely on informal browsing, general advice, and broad role descriptions rather than structured comparisons between their skills and documented occupation requirements.

## Proposed System
The proposed system preprocesses occupation records, uses the dataset's linked skills, compares user skills to occupation requirements, and uses TF-IDF and cosine similarity to rank related occupation profiles. It is designed to be explainable, dataset-aware, and academically suitable.

## Features
- CSV upload for job dataset analysis
- Data quality summary and duplicate tracking
- Transparent skill extraction dictionary
- Occupation and linked-skill overview dashboard with Plotly charts
- Personalized skill-gap comparison
- TF-IDF matching with cosine similarity
- Data explorer with search, filters, sorting, and CSV export
- Methodology and limitations explanation
- Privacy and terms sections

## Technology Stack
- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- scikit-learn
- SQLite
- Regular expressions
- pytest

## Dataset
The bundled dataset is the English ESCO v1.1.1 occupation and skills classification, provided as a local flat CSV with 3,007 occupation profiles and 123,788 linked skill labels. Its source, adaptations, attribution, and licence status are documented in `data/ESCO_SOURCE.md`. It is not a vacancy dataset.

## Dataset Source
The default dataset is a local ESCO-derived occupation dataset. Administrators can import and version other CSV datasets; provenance and licence information are shown from entered metadata, and unknown information remains marked “Not verified.”

## Installation
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Running the Application
```powershell
streamlit run app.py
```

## Folder Structure
```text
CareerLens-AI/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── esco_occupations.csv
│   ├── esco_source/
│   └── processed/
├── database/
│   ├── schema.sql
│   └── careerlens.db
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── skill_extraction.py
│   ├── market_analysis.py
│   ├── skill_gap.py
│   ├── job_matching.py
│   └── database.py
├── pages/
├── tests/
├── assets/
└── .venv/
```

## Data Preprocessing
The preprocessing pipeline standardizes common column names, removes duplicate rows, strips whitespace, normalizes text, fills missing fields where appropriate, and keeps the raw dataset separate from the cleaned output. The processed output is written to data/processed/jobs_clean.csv.

## Exploratory Data Analysis (EDA)
The dashboard calculates occupation and linked-skill counts from the selected dataset. The bundled ESCO data has no employer, salary, location, or vacancy fields.

## Skill Extraction
The application uses the ESCO source's essential and optional occupation-skill links for the bundled dataset. Resume text and custom CSVs use a transparent technical-skill dictionary.

## Skill Gap Analysis
For a selected target role, the system compares the user's supplied skills to the ESCO skills linked to that occupation and ranks potential gaps from dataset evidence.

## TF-IDF
TF-IDF converts text into feature vectors by weighting terms based on their frequency in a document and rarity across the corpus. This helps distinguish terms that are more informative in an occupation description.

## Cosine Similarity
Cosine similarity compares the angle between two vector representations of text. In this project, it measures how closely a user profile matches an occupation profile. This is a similarity score only and not a hiring probability.

## System Architecture
The project uses a layered architecture:
- data ingestion and validation
- normalization and preprocessing
- skill extraction
- occupation and skill summaries
- skill-gap analysis
- TF-IDF matching
- Streamlit dashboard presentation
- SQLite persistence for processed jobs

## Implementation
The solution is implemented in a modular structure to keep the code understandable for college demonstration. Each module handles a distinct part of the data pipeline.

## Testing
The project includes tests covering:
- preprocessing reliability
- duplicate handling
- skill extraction
- skill-gap analysis
- TF-IDF matching
- cosine similarity
- missing-column handling
- invalid upload behavior
- empty profile behavior

Run tests with:
```powershell
pytest
```

## Results
The application produces dataset-driven results for the selected occupation classification. They should not be treated as a complete description of local labor markets or as a global forecast.

## Limitations
- Dataset coverage may be incomplete.
- Skill dictionary coverage is not guaranteed to be exhaustive.
- TF-IDF and cosine similarity are lexical and do not measure actual hiring outcomes.
- Salary analysis is shown only when the dataset provides usable numeric values.
- Results remain limited by the selected dataset and may have role or regional bias.

## Future Scope
- Forecasting after a dated, sufficiently large dataset is selected
- Labeled relevance evaluation and model accuracy metrics
- OCR and structured resume education/experience extraction
- Validated occupational standards and skill synonyms
- A sourced course catalog and live job feeds, if licensing/credentials permit
- Production identity, encrypted storage, rate limits, and security review

## Conclusion
CareerLens AI provides a practical, transparent, and explainable approach to student career exploration. It demonstrates how occupation profiles, NLP similarity and skill-gap analysis can support a useful academic project without fabricating results or overclaiming accuracy.

## Account Portal and Current Scope
The current app includes local SQLite authentication, salted scrypt password hashes, per-rerun role/account checks, user/admin roles, profile editing, reviewed PDF/TXT resume text extraction, self-assessed skills, goals, applications, roadmaps, recommendation feedback, account export/deletion, and admin dataset/occupation/backup controls. Set `CAREERLENS_ADMIN_EMAIL` and `CAREERLENS_ADMIN_PASSWORD` before first launch to provision the initial administrator. Registration cannot grant admin privileges.

The user portal builds on the existing market explorer, skill-gap analysis, and TF-IDF job matcher. Recommendations expose matching/missing taxonomy skills and similarity; readiness is dataset-skill coverage, not a hiring outcome. Dataset versions include optional source/license/date notes. Forecasting, email password reset, OCR, live jobs, sourced course catalogs, and model training are not implemented. See `docs/` for architecture, installation, database, security, traceability, and usage notes. PDF extraction requires PyMuPDF. User resume text is stored locally in SQLite when explicitly saved.
