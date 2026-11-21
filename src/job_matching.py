"""TF-IDF-based job matching using cosine similarity."""

from __future__ import annotations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_profile_text(profile: str, target_role: str = "", experience: str = "") -> str:
    """Combine a student profile into one reusable profile string."""
    parts = [profile.strip(), target_role.strip(), experience.strip()]
    return " ".join(part for part in parts if part and str(part).strip())


def match_jobs(
    df: pd.DataFrame,
    profile_text: str,
    role_filter: str | None = None,
    location_filter: str | None = None,
    min_similarity: float = 0.0,
    top_n: int = 10,
) -> pd.DataFrame:
    """Return ranked job matches using TF-IDF and cosine similarity."""
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame(columns=["job_title", "company", "location", "description", "detected_skills", "similarity_score"]) 

    if not profile_text or not str(profile_text).strip():
        return pd.DataFrame(columns=["job_title", "company", "location", "description", "detected_skills", "similarity_score"]) 

    working = df.copy()
    working["description_text"] = (working["job_title"].fillna("") + " " + working["job_description"].fillna("") + " " + working["skills"].fillna("")).str.lower()
    working["description_text"] = working["description_text"].fillna("")

    if role_filter and str(role_filter).strip():
        working = working[working["job_title"].astype(str).str.lower() == str(role_filter).strip().lower()]

    if location_filter and str(location_filter).strip():
        working = working[working["location"].astype(str).str.lower() == str(location_filter).strip().lower()]

    if working.empty:
        return pd.DataFrame(columns=["job_title", "company", "location", "description", "detected_skills", "similarity_score"]) 

    corpus = [profile_text.strip()] + working["description_text"].fillna("").tolist()
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=5000)
    matrix = vectorizer.fit_transform(corpus)
    similarity_scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

    working = working.copy()
    working["similarity_score"] = similarity_scores
    working = working[working["similarity_score"] >= float(min_similarity)]
    working = working.sort_values("similarity_score", ascending=False).head(int(top_n))
    working = working.reset_index(drop=True)

    results = working[["job_title", "company", "location", "job_description", "detected_skills", "similarity_score"]].copy()
    results.columns = ["job_title", "company", "location", "description", "detected_skills", "similarity_score"]
    return results

