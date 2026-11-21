"""Transparent, dataset-grounded career utilities used by the Streamlit app."""
from __future__ import annotations

import io
import re
from collections import Counter
from hashlib import sha256

import pandas as pd


def explain_job_match(profile_skills, job_skills):
    profile = {str(skill).strip().casefold() for skill in profile_skills if str(skill).strip()}
    required = {str(skill).strip().casefold() for skill in job_skills if str(skill).strip()}
    return {"matching_skills": sorted(profile & required), "missing_skills": sorted(required - profile), "overlap": len(profile & required) / len(required) if required else 0.0}


def transferable_skills(jobs: pd.DataFrame, source_role: str, target_role: str) -> list[str]:
    source = jobs[jobs.job_title.astype(str).str.casefold() == source_role.casefold()]
    target = jobs[jobs.job_title.astype(str).str.casefold() == target_role.casefold()]
    source_skills = {s for xs in source.get("detected_skills", []) for s in xs}
    target_skills = {s for xs in target.get("detected_skills", []) for s in xs}
    return sorted(source_skills & target_skills)


def readiness_assessment(jobs: pd.DataFrame, role: str, user_skills) -> dict:
    """A descriptive role-skill coverage measure, explicitly not hiring probability."""
    role_rows = jobs[jobs.job_title.astype(str).str.casefold() == role.casefold()]
    all_skills = [s for xs in role_rows.get("detected_skills", []) for s in (xs if isinstance(xs, list) else [])]
    demanded = set(all_skills)
    known = {str(s).strip().casefold() for s in user_skills if str(s).strip()}
    matched = demanded & known
    return {"coverage_percent": round(100 * len(matched) / len(demanded)) if demanded and known else None,
            "matched": sorted(matched), "missing": sorted(demanded - known),
            "basis": f"{len(demanded)} distinct taxonomy skills in {len(role_rows)} selected-dataset records; {len(known)} user-confirmed profile skills",
            "message": "" if known else "Add skills you confirm in your profile before calculating coverage."}


def recommend_learning_resources(skills):
    """Suggest first-party documentation search targets; no course/catalog is implied."""
    providers = {
        "python": "Python official tutorial", "sql": "SQLite documentation and SQL tutorial",
        "pandas": "pandas getting started", "numpy": "NumPy user guide",
        "scikit-learn": "scikit-learn user guide", "machine learning": "scikit-learn supervised learning guide",
        "docker": "Docker getting started", "git": "Git documentation",
        "javascript": "MDN JavaScript guide", "html": "MDN HTML guide", "css": "MDN CSS guide",
        "react": "React official learn guide", "aws": "AWS Skill Builder official learning search",
        "azure": "Microsoft Learn Azure paths", "pandas": "pandas documentation",
    }
    return [{"skill": skill, "resource_search": providers.get(str(skill).casefold(), f"Search official documentation for {skill}")} for skill in skills]


def resume_improvement_suggestions(text: str, skills: list[str]) -> list[str]:
    content = text or ""
    suggestions = []
    if len(content.split()) < 120: suggestions.append("The extracted text is brief; check whether all relevant experience and projects are included.")
    for section in ("experience", "education", "projects", "skills"):
        if not re.search(rf"\b{section}\b", content, re.I): suggestions.append(f"Consider adding a clearly labeled {section.title()} section if relevant.")
    if len(skills) < 3: suggestions.append("Few terms matched the built-in skill dictionary; verify extracted skills and add relevant skills manually in your profile.")
    if not re.search(r"\b\d+\b", content): suggestions.append("Consider adding accurate, measurable outcomes to experience bullets where evidence supports them.")
    if not suggestions: suggestions.append("No basic structure issue was detected by these simple checks; review accuracy and tailor content to the target role.")
    return suggestions


def extract_resume_text(payload: bytes, filename: str, max_bytes: int = 5 * 1024 * 1024) -> str:
    if not payload or len(payload) > max_bytes: raise ValueError("Resume must be non-empty and no larger than 5 MB.")
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix == "txt":
        try: text = payload.decode("utf-8-sig")
        except UnicodeDecodeError as exc: raise ValueError("Text resume must be UTF-8 encoded.") from exc
    elif suffix == "pdf":
        if not payload.startswith(b"%PDF-"): raise ValueError("File content is not a valid PDF.")
        try:
            import pymupdf
            with pymupdf.open(stream=payload, filetype="pdf") as document:
                if document.needs_pass: raise ValueError("Password-protected PDFs are not supported.")
                if document.page_count > 100: raise ValueError("PDF exceeds the 100-page limit.")
                text = "\n".join(page.get_text("text") for page in document)
        except ImportError as exc: raise RuntimeError("PDF support requires PyMuPDF.") from exc
        except ValueError: raise
        except Exception as exc: raise ValueError("PDF could not be parsed.") from exc
    else:
        raise ValueError("Only PDF and TXT resumes are supported.")
    if not text.strip(): raise ValueError("No readable text found. Scanned PDFs require OCR, which is not enabled.")
    return text[:100000]


def dataset_fingerprint(csv_text: str) -> str:
    return sha256(csv_text.encode("utf-8")).hexdigest()


def model_evaluation_summary(jobs: pd.DataFrame) -> dict:
    """Report observable corpus coverage; no relevance labels means no ranking accuracy score."""
    n = len(jobs)
    has_title = int(jobs.get("job_title", pd.Series(dtype=str)).fillna("").astype(str).str.strip().ne("").sum())
    detected = sum(bool(x) for x in jobs.get("detected_skills", []))
    return {"records": n, "title_coverage": has_title / n if n else 0.0,
            "skill_coverage": detected / n if n else 0.0,
            "ranking_metrics": "Unavailable: no human relevance labels or outcome data"}
