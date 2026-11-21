"""Skill-gap analysis based on dataset job-role requirements."""

from __future__ import annotations

import re
from typing import Iterable

import pandas as pd

from src.skill_extraction import extract_skills_from_text, normalize_skill_label


def parse_current_skills(value: str | Iterable[str]) -> set[str]:
    """Normalize user-entered skills to a clean lower-case set."""
    if value is None:
        return set()
    if isinstance(value, str):
        items = re.split(r"[,;|\n]", value)
    else:
        items = list(value)
    normalized = set()
    for item in items:
        cleaned = normalize_skill_label(item)
        if cleaned:
            normalized.add(cleaned)
    return normalized


def calculate_skill_gap(df: pd.DataFrame, target_role: str, current_skills: str | Iterable[str]) -> dict:
    """Calculate matched skills, potential gaps, and priority ranking from dataset evidence."""
    if not target_role or not str(target_role).strip():
        return {
            "matched": [],
            "potential_gaps": [],
            "skill_frequency": [],
            "priority": [],
            "message": "Please select a target job role.",
        }

    role_rows = df[df["job_title"].astype(str).str.lower() == str(target_role).strip().lower()].copy()

    if role_rows.empty:
        return {
            "matched": [],
            "potential_gaps": [],
            "skill_frequency": [],
            "priority": [],
            "message": "No matching job-role data was found in the selected dataset.",
        }

    required = set()
    for skills in role_rows.get("detected_skills", []):
        if isinstance(skills, list):
            required.update(skills)

    if not required:
        return {
            "matched": [],
            "potential_gaps": [],
            "skill_frequency": [],
            "priority": [],
            "message": "No dataset-detected skills were available for this role.",
        }

    known = parse_current_skills(current_skills)
    matched = sorted(required & known)
    missing = sorted(required - known)

    skill_counts = {}
    for skill in required:
        skill_counts[skill] = int(role_rows["detected_skills"].apply(lambda items: skill in items if isinstance(items, list) else False).sum())

    freq = []
    for skill in sorted(required, key=lambda item: (-skill_counts.get(item, 0), item)):
        count = skill_counts.get(skill, 0)
        freq.append({
            "skill": skill,
            "frequency": round((count / max(len(role_rows), 1)) * 100, 1),
            "count": count,
        })

    missing_ranked = []
    for item in freq:
        if item["skill"] in missing:
            missing_ranked.append({
                "skill": item["skill"],
                "frequency": item["frequency"],
                "count": item["count"],
            })

    return {
        "matched": matched,
        "potential_gaps": missing,
        "skill_frequency": freq,
        "priority": missing_ranked,
        "message": "Potential skill gaps based on the selected dataset.",
    }


def estimate_gap_priority(df: pd.DataFrame, target_role: str, current_skills: str) -> list[dict]:
    """Return ranked missing skills with their frequency percentages."""
    result = calculate_skill_gap(df, target_role, current_skills)
    return result.get("priority", [])

