"""Utilities for loading and normalizing dataset files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import pandas as pd

DEFAULT_CAREER_DATASET = Path(__file__).resolve().parents[1] / "data" / "esco_occupations.csv"

COLUMN_ALIASES = {
    "job_title": ["job_title", "title", "jobtitle", "position"],
    "job_description": ["job_description", "description", "jobdescription"],
    "skills": ["skills", "required_skills", "job_skills", "job_skill_set", "skill"],
    "company": ["company", "company_name", "companyname", "employer"],
    "location": ["location", "job_location", "joblocation", "city"],
    "salary_min": ["salary_min", "minimum_salary", "minimumsalary", "salary_minimum", "min_salary"],
    "salary_max": ["salary_max", "maximum_salary", "maximumsalary", "salary_maximum", "max_salary"],
}


def normalize_column_name(column_name: object) -> str:
    """Convert a dataset column name to a consistent internal style."""
    cleaned = str(column_name).strip().lower()
    cleaned = re.sub(r"[\s\-]+", "_", cleaned)
    return cleaned


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize common job dataset column names to internal names."""
    normalized = df.copy()
    normalized.columns = [normalize_column_name(col) for col in normalized.columns]

    for standard_name, aliases in COLUMN_ALIASES.items():
        if standard_name in normalized.columns:
            continue
        for alias in aliases:
            alias_key = normalize_column_name(alias)
            if alias_key in normalized.columns:
                normalized[standard_name] = normalized[alias_key]
                break

    if "job_title" not in normalized.columns:
        raise ValueError("Required column 'job_title' was not found. Please provide a job-title column.")

    for column in ["job_description", "skills", "company", "location"]:
        if column not in normalized.columns:
            normalized[column] = ""

    for column in ["salary_min", "salary_max"]:
        if column not in normalized.columns:
            normalized[column] = None

    return normalized


def read_csv_file(file_like) -> pd.DataFrame:
    """Read a CSV file and return a dataframe while preserving useful errors."""
    if file_like is None:
        raise ValueError("No file was provided.")

    if hasattr(file_like, "read"):
        try:
            return pd.read_csv(file_like)
        except Exception as exc:  # pragma: no cover - surfaced for user messages
            raise ValueError(f"Could not read the CSV file: {exc}") from exc

    if isinstance(file_like, (str, Path)):
        path = Path(file_like)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return pd.read_csv(path)

    raise ValueError("Unsupported file input.")


def create_data_quality_summary(df: pd.DataFrame) -> dict:
    """Create a quality summary that explains the dataset without fabricating metrics."""
    original_records = int(len(df))
    duplicate_records = int(df.duplicated().sum())
    valid_records = int(len(df.drop_duplicates()))

    missing_job_titles = int(df["job_title"].fillna("").astype(str).str.strip().eq("").sum()) if "job_title" in df.columns else 0
    missing_descriptions = int(df["job_description"].fillna("").astype(str).str.strip().eq("").sum()) if "job_description" in df.columns else 0
    missing_skills = int(df["skills"].fillna("").astype(str).str.strip().eq("").sum()) if "skills" in df.columns else 0
    salary_values = df[["salary_min", "salary_max"]].fillna("") if {"salary_min", "salary_max"}.issubset(df.columns) else pd.DataFrame()
    missing_salary_values = int(
        salary_values.astype(str).apply(lambda row: row.str.strip().eq("").all(), axis=1).sum()
    ) if not salary_values.empty else 0

    unique_roles = int(df["job_title"].dropna().astype(str).str.strip().nunique()) if "job_title" in df.columns else 0
    unique_companies = int(df["company"].dropna().astype(str).str.strip().nunique()) if "company" in df.columns else 0
    unique_locations = int(df["location"].dropna().astype(str).str.strip().nunique()) if "location" in df.columns else 0

    return {
        "original_records": original_records,
        "duplicate_records": duplicate_records,
        "valid_records": valid_records,
        "missing_job_titles": missing_job_titles,
        "missing_descriptions": missing_descriptions,
        "missing_skills": missing_skills,
        "missing_salary_values": missing_salary_values,
        "unique_roles": unique_roles,
        "unique_companies": unique_companies,
        "unique_locations": unique_locations,
    }


def dataset_as_source_label(file_name: str | None, default_label: str = "Occupation dataset") -> str:
    """Return user-friendly source labels keeping the dataset origin transparent."""
    if file_name:
        return f"Uploaded dataset: {file_name}"
    return default_label


def get_career_dataset_path() -> Path:
    """Return the bundled, authentic ESCO career-classification dataset."""
    return DEFAULT_CAREER_DATASET


def get_demo_dataset_path() -> Path:
    """Backward-compatible alias; the default now points to ESCO, not demo vacancies."""
    return get_career_dataset_path()


def get_dataset_metadata(
    path: Path | None = None,
    file_name: str | None = None,
    source_url: str | None = None,
    license_terms: str | None = None,
) -> dict:
    """Describe the selected CSV without assigning an undocumented source or license."""
    resolved = Path(path) if path is not None else Path(file_name or "")
    is_bundled_esco = bool(path is not None and resolved.resolve() == DEFAULT_CAREER_DATASET.resolve() and resolved.is_file())

    if is_bundled_esco:
        name = "ESCO v1.1.1 Occupations and Skills (English)"
        source = (
            "European Commission ESCO v1.1.1; CSV source: "
            "https://github.com/tabiya-tech/tabiya-open-dataset/tree/main/"
            "tabiya-esco-v1.1.1/csv. See data/ESCO_SOURCE.md."
        )
    else:
        name = file_name or (resolved.name if path is not None else "Dataset")
        source = f"Recorded source: {source_url.strip()} (not independently verified)." if source_url and source_url.strip() else "Not verified"

    license_display = (
        "ESCO reuse under European Commission Decision 2011/833/EU; attribution required. "
        "Tabiya CSV transformation licence: Not verified."
        if is_bundled_esco
        else license_terms.strip() if license_terms and license_terms.strip() else "Not verified"
    )

    return {
        "name": name,
        "source": source,
        "license": license_display,
        "size": f"{resolved.stat().st_size / 1024:.1f} KB" if resolved.is_file() else "N/A",
        "date_accessed": "N/A",
    }


def ensure_available_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Create empty columns for optional values so the app stays robust."""
    for column in ["job_title", "job_description", "skills", "company", "location"]:
        if column not in df.columns:
            df[column] = ""
    for column in ["salary_min", "salary_max"]:
        if column not in df.columns:
            df[column] = None
    return df


def infer_file_type(file_obj) -> str:
    """Confirm the upload looks like a CSV file before processing."""
    filename = getattr(file_obj, "name", "")
    if not filename.lower().endswith(".csv"):
        raise ValueError("Only CSV files are supported for upload.")
    return "csv"

