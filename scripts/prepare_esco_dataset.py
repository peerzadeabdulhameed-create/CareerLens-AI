"""Build CareerLens' local occupation dataset from downloaded ESCO CSV tables.

The source files remain unchanged in data/esco_source/. This script only creates
an app-friendly flattened file; it does not create job-vacancy records.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "esco_source"
OUTPUT_PATH = ROOT / "data" / "esco_occupations.csv"


def _clean(value) -> str:
    return "" if pd.isna(value) else str(value).strip()


def build_dataset(source_dir: Path = SOURCE_DIR, output_path: Path = OUTPUT_PATH) -> pd.DataFrame:
    occupations = pd.read_csv(source_dir / "occupations.csv").fillna("")
    skills = pd.read_csv(source_dir / "skills.csv").fillna("")
    relations = pd.read_csv(source_dir / "occupation_skill_relations.csv").fillna("")

    # The occupations file includes only occupation concepts; guard against taxonomy
    # group records should a future source package include them.
    if "OCCUPATIONTYPE" in occupations:
        occupations = occupations[occupations.OCCUPATIONTYPE.eq("escooccupation")].copy()
    required_occ = {"ID", "ORIGINURI", "CODE", "PREFERREDLABEL", "DESCRIPTION"}
    required_skill = {"ID", "PREFERREDLABEL"}
    required_relation = {"OCCUPATIONID", "RELATIONTYPE", "SKILLID"}
    if not required_occ.issubset(occupations.columns):
        raise ValueError(f"Occupation table is missing columns: {sorted(required_occ - set(occupations.columns))}")
    if not required_skill.issubset(skills.columns) or not required_relation.issubset(relations.columns):
        raise ValueError("ESCO skill or occupation-skill table does not match the documented schema.")

    skill_names = skills.set_index("ID").PREFERREDLABEL.to_dict()
    relations = relations[relations.OCCUPATIONID.isin(set(occupations.ID))].copy()
    relations["skill_name"] = relations.SKILLID.map(skill_names)
    relations = relations.dropna(subset=["skill_name"])

    by_occupation: dict[str, dict[str, list[str]]] = {}
    for row in relations.itertuples(index=False):
        relation_type = _clean(row.RELATIONTYPE).casefold()
        if relation_type not in {"essential", "optional"}:
            continue
        entry = by_occupation.setdefault(_clean(row.OCCUPATIONID), {"essential": [], "optional": []})
        label = _clean(row.skill_name)
        if label and label not in entry[relation_type]:
            entry[relation_type].append(label)

    output_rows = []
    for row in occupations.itertuples(index=False):
        occupation_id = _clean(getattr(row, "ID"))
        linked = by_occupation.get(occupation_id, {"essential": [], "optional": []})
        essential = linked["essential"]
        optional = linked["optional"]
        combined = list(dict.fromkeys([*essential, *optional]))
        title = _clean(getattr(row, "PREFERREDLABEL"))
        if not title:
            continue
        output_rows.append({
            "job_title": title,
            "job_description": _clean(getattr(row, "DESCRIPTION")),
            "skills": "; ".join(combined),
            "essential_skills": "; ".join(essential),
            "optional_skills": "; ".join(optional),
            "alternative_labels": _clean(getattr(row, "ALTLABELS", "")),
            "occupation_uri": _clean(getattr(row, "ORIGINURI")),
            "esco_code": _clean(getattr(row, "CODE")),
            "isco_group_code": _clean(getattr(row, "ISCOGROUPCODE", "")),
        })

    result = pd.DataFrame(output_rows)
    if result.empty:
        raise ValueError("No ESCO occupation records were available to build the local dataset.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False, encoding="utf-8")
    return result


if __name__ == "__main__":
    built = build_dataset()
    print(f"Wrote {len(built):,} ESCO occupation profiles to {OUTPUT_PATH}")
