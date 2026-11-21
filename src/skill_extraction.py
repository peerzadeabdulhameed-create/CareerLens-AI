"""Transparent skill extraction using a maintainable skill dictionary."""

from __future__ import annotations

import re
from typing import Iterable

SKILL_DICTIONARY = [
    "python",
    "sql",
    "excel",
    "pandas",
    "numpy",
    "scikit-learn",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch",
    "statistics",
    "data visualization",
    "power bi",
    "tableau",
    "feature engineering",
    "model evaluation",
    "natural language processing",
    "computer vision",
    "javascript",
    "react",
    "node.js",
    "html",
    "css",
    "mongodb",
    "rest apis",
    "git",
    "docker",
    "linux",
    "networking",
    "etl",
    "aws",
    "azure",
    "gcp",
    "cloud computing",
    "data engineering",
    "data analysis",
    "data preprocessing",
    "model monitoring",
    "database",
    "apis",
    "data science",
    "business intelligence",
    "ai",
    "ml",
    "api development",
    "testing",
    "ui testing",
    "accessibility",
    "cloud fundamentals",
    "databases",
    "siem",
    "incident response",
    "vulnerability assessment",
    "authentication",
    "statistics",
    "visualization",
    "machine learning",
]


def normalize_skill_label(skill: str) -> str:
    """Return a normalized skill label for consistent display."""
    return re.sub(r"\s+", " ", str(skill or "")).strip().lower()


def extract_skills_from_text(text: str | None, skill_dictionary: Iterable[str] | None = None) -> list[str]:
    """Find skills in a text string using regex and a configurable skill dictionary."""
    if not text:
        return []

    source_terms = list(skill_dictionary) if skill_dictionary is not None else SKILL_DICTIONARY
    candidate_text = str(text).lower()

    found: list[str] = []
    for skill in source_terms:
        normalized_skill = normalize_skill_label(skill)
        if not normalized_skill:
            continue
        pattern = r"(?<![a-z0-9])" + re.escape(normalized_skill) + r"(?![a-z0-9])"
        if re.search(pattern, candidate_text):
            found.append(normalized_skill)

    unique_found = list(dict.fromkeys(found))
    return sorted(unique_found)


def parse_list_like_skills(raw_value) -> list[str]:
    """Handle stringified arrays, comma-separated lists, and raw skill text."""
    if raw_value is None:
        return []
    value = str(raw_value).strip()
    if not value:
        return []
    if value.startswith("[") and value.endswith("]"):
        try:
            parsed = __import__("ast").literal_eval(value)
            if isinstance(parsed, list):
                return [normalize_skill_label(item) for item in parsed if normalize_skill_label(item)]
        except (ValueError, SyntaxError):
            pass
    return [normalize_skill_label(item) for item in re.split(r"[,;|]", value) if normalize_skill_label(item)]


def extract_skills_for_row(row) -> list[str]:
    """Combine structured skill fields and inferred skills from job titles and descriptions."""
    structured = parse_list_like_skills(row.get("skills", ""))
    text = f"{row.get('job_title', '')} {row.get('job_description', '')}"
    detected = extract_skills_from_text(text)
    combined = structured + detected
    return sorted(dict.fromkeys(combined))


def skill_frequency_df(df, skill_column: str = "detected_skills") -> list[dict]:
    """Convert the detected skills into dataset-based frequency information."""
    skills = []
    for skills_list in df[skill_column].fillna([]):
        if isinstance(skills_list, list):
            skills.extend(skills_list)
    counts = {}
    for skill in skills:
        counts[skill] = counts.get(skill, 0) + 1
    total_records = max(len(df), 1)
    return [{"skill": skill, "count": count, "frequency": round((count / total_records) * 100, 1)} for skill, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]

