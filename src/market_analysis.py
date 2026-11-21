"""Dashboard calculations for the market overview page."""

from __future__ import annotations

import pandas as pd


def compute_metrics(df: pd.DataFrame) -> dict:
    """Return dataset-derived metrics used on the home dashboard."""
    metrics = {
        "jobs": int(len(df)),
        "roles": int(df["job_title"].nunique()) if "job_title" in df.columns else 0,
        "skills": int(df["detected_skills"].explode().nunique()) if "detected_skills" in df.columns else 0,
        "companies": int(df["company"].nunique()) if "company" in df.columns and df["company"].notna().any() else 0,
        "locations": int(df["location"].nunique()) if "location" in df.columns and df["location"].notna().any() else 0,
    }
    return metrics


def top_skills(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Return top skills by frequency within the selected dataset."""
    if "detected_skills" not in df.columns:
        return pd.DataFrame(columns=["skill", "count"])

    flattened = df["detected_skills"].explode().dropna()
    if flattened.empty:
        return pd.DataFrame(columns=["skill", "count"])

    counts = flattened.value_counts().reset_index()
    counts.columns = ["skill", "count"]
    return counts.head(limit).sort_values("count", ascending=False).reset_index(drop=True)


def role_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return a distribution of roles used by the market overview charts."""
    if "job_title" not in df.columns:
        return pd.DataFrame(columns=["job_title", "count"])
    counts = df["job_title"].value_counts().reset_index()
    counts.columns = ["job_title", "count"]
    return counts.head(12).sort_values("count", ascending=False).reset_index(drop=True)


def location_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Provide a location count chart when location data is available."""
    if "location" not in df.columns:
        return pd.DataFrame(columns=["location", "count"])
    filtered = df[df["location"].astype(str).str.strip() != ""]
    if filtered.empty:
        return pd.DataFrame(columns=["location", "count"])
    counts = filtered["location"].value_counts().reset_index()
    counts.columns = ["location", "count"]
    return counts.head(10).sort_values("count", ascending=False).reset_index(drop=True)


def reliable_salary_summary(df: pd.DataFrame) -> pd.DataFrame | None:
    """Return a salary summary only when the dataset has believable numeric salary values."""
    required = {"salary_min", "salary_max"}.issubset(df.columns)
    if not required:
        return None

    numeric = df[["salary_min", "salary_max"]].apply(pd.to_numeric, errors="coerce")
    if numeric.empty or numeric.isna().all().all():
        return None

    valid = numeric.dropna().copy()
    if valid.empty:
        return None

    return valid

