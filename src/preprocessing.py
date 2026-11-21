"""Preprocessing pipeline for job-posting data."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pandas as pd

from src.data_loader import normalize_columns


def clean_text(value) -> str:
    """Normalize text fields by stripping whitespace and collapsing repeated spaces."""
    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text


def parse_skills_field(value) -> list[str]:
    """Parse a skills field from CSV strings, Python lists, or separators."""
    raw_value = value if value is not None else ""
    text = str(raw_value).strip()
    if not text:
        return []

    try:
        if text.startswith("[") and text.endswith("]"):
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                return [clean_text(item).lower() for item in parsed if clean_text(item)]
    except (ValueError, SyntaxError):
        pass

    return [clean_text(piece).lower() for piece in re.split(r"[,;|]", text) if clean_text(piece)]


def parse_linked_skills(*values) -> list[str]:
    """Parse semicolon-delimited ESCO link fields while preserving commas in labels."""
    linked = []
    for value in values:
        if value is None or pd.isna(value):
            continue
        linked.extend(clean_text(item).casefold() for item in str(value).split(";") if clean_text(item))
    return list(dict.fromkeys(linked))


def coerce_numeric(value):
    """Convert a salary value to a float when it is numeric, otherwise return NaN."""
    if pd.isna(value):
        return float("nan")
    text = str(value).strip().replace(",", "")
    if not text:
        return float("nan")
    try:
        number = float(text)
    except ValueError:
        try:
            numbers = re.findall(r"[-+]?\d*\.?\d+", text)
            if not numbers:
                return float("nan")
            number = float(numbers[0])
        except ValueError:
            return float("nan")
    return number


def preprocess_jobs(df: pd.DataFrame) -> pd.DataFrame:
    """Apply reproducible cleaning and produce a fully usable job dataset."""
    cleaned = normalize_columns(df.copy())

    for column in ["job_title", "job_description", "skills", "company", "location"]:
        cleaned[column] = cleaned[column].fillna("").astype(str)

    cleaned["job_title"] = cleaned["job_title"].map(clean_text)
    cleaned["job_description"] = cleaned["job_description"].map(clean_text)
    cleaned["company"] = cleaned["company"].map(clean_text)
    cleaned["location"] = cleaned["location"].map(clean_text)

    cleaned["skills"] = cleaned["skills"].map(lambda value: ", ".join(parse_skills_field(value)))
    cleaned["salary_min"] = cleaned["salary_min"].map(coerce_numeric)
    cleaned["salary_max"] = cleaned["salary_max"].map(coerce_numeric)

    cleaned = cleaned.drop_duplicates(subset=["job_title", "job_description", "skills"]).reset_index(drop=True)
    cleaned = cleaned[cleaned["job_title"].str.strip().ne("")].reset_index(drop=True)

    cleaned["job_title"] = cleaned["job_title"].str.replace(r"\s+", " ", regex=True)
    cleaned["job_description"] = cleaned["job_description"].str.replace(r"\s+", " ", regex=True)
    cleaned["skills"] = cleaned["skills"].str.replace(r"\s*,\s*", ", ", regex=True)

    cleaned["job_description"] = cleaned["job_description"].fillna("")
    cleaned["skills"] = cleaned["skills"].fillna("")

    return cleaned


def save_processed_dataset(df: pd.DataFrame, output_path: str | Path) -> Path:
    """Persist a cleaned dataset to the data/processed directory."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def build_quality_summary(preprocessed_df: pd.DataFrame) -> dict:
    """Create a dataset quality summary for the interface and report."""
    original = int(len(preprocessed_df))
    missing_titles = int(preprocessed_df["job_title"].astype(str).str.strip().eq("").sum())
    missing_descriptions = int(preprocessed_df["job_description"].astype(str).str.strip().eq("").sum())
    missing_skills = int(preprocessed_df["skills"].astype(str).str.strip().eq("").sum())
    missing_salary = int(
        preprocessed_df[["salary_min", "salary_max"]].isna().all(axis=1).sum()
    ) if {"salary_min", "salary_max"}.issubset(preprocessed_df.columns) else 0

    return {
        "original_records": original,
        "duplicate_records": 0,
        "valid_records": original,
        "missing_job_titles": missing_titles,
        "missing_descriptions": missing_descriptions,
        "missing_skills": missing_skills,
        "missing_salary_values": missing_salary,
        "unique_roles": int(preprocessed_df["job_title"].nunique()),
        "unique_companies": int(preprocessed_df["company"].nunique()) if "company" in preprocessed_df.columns else 0,
        "unique_locations": int(preprocessed_df["location"].nunique()) if "location" in preprocessed_df.columns else 0,
    }

