import pandas as pd

from src.data_loader import normalize_columns, get_career_dataset_path, get_dataset_metadata
from src.job_matching import match_jobs
from src.preprocessing import preprocess_jobs, parse_linked_skills
from src.skill_extraction import extract_skills_from_text
from src.skill_gap import calculate_skill_gap
from src.database import (hash_password, verify_password, initialize_database,
                          create_user, authenticate, provision_admin, current_principal,
                          get_profile, save_profile, delete_user_account, archive_dataset,
                          active_dataset, dataset_versions, activate_dataset_version,
                          backup_database_bytes, restore_database_bytes)
from src.database import save_resume, change_password
from src.career_features import (explain_job_match, transferable_skills, readiness_assessment,
                                 recommend_learning_resources, resume_improvement_suggestions,
                                 extract_resume_text, model_evaluation_summary)


def test_preprocessing_removes_duplicates_and_empty_titles():
    df = pd.DataFrame(
        {
            "job_title": ["Data Analyst", "Data Analyst", "", "Data Scientist"],
            "job_description": ["Use SQL and Python.", "Use SQL and Python.", "Use SAS.", "Use statistics."],
            "skills": ["Python, SQL", "Python, SQL", "", "Python, Statistics"],
            "company": ["A", "A", "B", "C"],
            "location": ["Delhi", "Delhi", "Bengaluru", "Hyderabad"],
        }
    )
    result = preprocess_jobs(df)
    assert len(result) == 2
    assert result["job_title"].str.strip().ne("").all()


def test_skill_extraction_detects_known_terms():
    skills = extract_skills_from_text("Python SQL pandas scikit-learn machine learning")
    assert "python" in skills
    assert "sql" in skills
    assert "pandas" in skills
    assert "scikit-learn" in skills
    assert "machine learning" in skills


def test_skill_gap_calculation_uses_dataset_evidence():
    df = pd.DataFrame(
        {
            "job_title": ["Data Scientist", "Data Scientist"],
            "job_description": ["Python, SQL, statistics, machine learning.", "Python, SQL, pandas, model evaluation."],
            "skills": ["Python, SQL", "Python, SQL, Pandas"],
            "company": ["A", "B"],
            "location": ["Delhi", "Bengaluru"],
            "detected_skills": [["python", "sql", "statistics", "machine learning"], ["python", "sql", "pandas", "model evaluation"]],
        }
    )
    result = calculate_skill_gap(df, "Data Scientist", "Python, SQL")
    assert "python" in result["matched"]
    assert "sql" in result["matched"]
    assert "statistics" in result["potential_gaps"] or "machine learning" in result["potential_gaps"]


def test_job_matching_ranks_similar_descs():
    df = pd.DataFrame(
        {
            "job_title": ["Data Analyst", "Python Developer", "Product Manager"],
            "job_description": [
                "Use SQL, Excel, and dashboards for business analysis.",
                "Build Python services using APIs, SQL, and automation.",
                "Manage product backlog and coordinate teams.",
            ],
            "skills": ["SQL, Excel", "Python, SQL", "Project planning"],
            "company": ["A", "B", "C"],
            "location": ["Delhi", "Bengaluru", "Hyderabad"],
            "detected_skills": [["sql", "excel"], ["python", "sql"], ["project planning"]],
        }
    )
    result = match_jobs(df, "Python SQL APIs dashboard analysis", top_n=2)
    assert not result.empty
    assert result.iloc[0]["job_title"] in {"Data Analyst", "Python Developer"}


def test_missing_required_columns_raise_value_error():
    df = pd.DataFrame({"not_title": ["A", "B"]})
    try:
        normalize_columns(df)
        assert False, "Expected ValueError for missing job_title"
    except ValueError:
        pass


def test_empty_profile_returns_empty_matches():
    df = pd.DataFrame({"job_title": ["Data Analyst"], "job_description": ["SQL and Python."], "skills": ["SQL"], "company": ["A"], "location": ["Delhi"], "detected_skills": [["sql"]]})
    result = match_jobs(df, "")
    assert result.empty


def test_password_hash_is_salted_and_verifiable():
    first = hash_password("correct horse battery staple")
    second = hash_password("correct horse battery staple")
    assert first != second
    assert verify_password("correct horse battery staple", first)
    assert not verify_password("incorrect", first)


def test_database_migration_preserves_existing_jobs(tmp_path):
    db_path = tmp_path / "careerlens.db"
    connection = initialize_database(db_path)
    connection.execute("INSERT INTO jobs(job_id,job_title) VALUES (42,'Existing role')")
    connection.commit()
    connection.close()
    connection = initialize_database(db_path)
    assert connection.execute("SELECT job_title FROM jobs WHERE job_id=42").fetchone()[0] == "Existing role"
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"users", "user_profiles", "resumes", "assessments", "audit_logs"} <= tables
    connection.close()


def test_registration_roles_active_session_and_user_isolation(tmp_path):
    db = tmp_path / "auth.sqlite3"
    user_a = create_user("a@example.test", "a-long-password", "A", db)
    user_b = create_user("b@example.test", "b-long-password", "B", db)
    assert provision_admin("admin@example.test", "admin-long-password", db)
    assert authenticate("a@example.test", "a-long-password", db)["role"] == "user"
    assert authenticate("admin@example.test", "admin-long-password", db)["role"] == "admin"
    save_profile(user_a, ("A", "", "", "", "", '["python"]'), db)
    save_profile(user_b, ("B", "", "", "", "", '["sql"]'), db)
    assert get_profile(user_a, db)[0] == "A"
    assert get_profile(user_b, db)[0] == "B"
    session_b = authenticate("b@example.test", "b-long-password", db)
    connection = initialize_database(db)
    connection.execute("UPDATE users SET auth_version=auth_version+1 WHERE user_id=?", (user_b,)); connection.commit(); connection.close()
    assert current_principal(user_b, session_b["auth_version"], db_path=db) is None
    connection = initialize_database(db)
    connection.execute("UPDATE users SET is_active=0 WHERE user_id=?", (user_a,)); connection.commit(); connection.close()
    assert current_principal(user_a, db_path=db) is None
    assert not delete_user_account(user_b, "wrong-password", db)
    assert change_password(user_b, "b-long-password", "a-new-password-123", db)
    assert authenticate("b@example.test", "b-long-password", db) is None
    assert authenticate("b@example.test", "a-new-password-123", db)
    assert delete_user_account(user_b, "a-new-password-123", db)
    assert get_profile(user_b, db) is None


def test_dataset_versions_are_persistent_and_activatable(tmp_path):
    db = tmp_path / "datasets.sqlite3"
    first = archive_dataset("job_title,skills\nAnalyst,sql\n", "first.csv", None, db)
    second = archive_dataset("job_title,skills\nEngineer,python\n", "second.csv", None, db)
    assert active_dataset(db)[0] == second
    activate_dataset_version(first, db)
    assert active_dataset(db)[1:] == ("first.csv", "job_title,skills\nAnalyst,sql\n")
    assert len(dataset_versions(db)) == 2


def test_database_backup_restore_round_trip(tmp_path):
    db = tmp_path / "backup.sqlite3"
    user = create_user("backup@example.test", "long-password-123", db_path=db)
    backup = backup_database_bytes(db)
    connection = initialize_database(db)
    connection.execute("DELETE FROM users WHERE user_id=?", (user,)); connection.commit(); connection.close()
    restore_database_bytes(backup, db)
    assert authenticate("backup@example.test", "long-password-123", db)


def test_explainable_career_features_and_resume_validation():
    explanation = explain_job_match(["python", "sql"], ["python", "docker"])
    assert explanation == {"matching_skills": ["python"], "missing_skills": ["docker"], "overlap": 0.5}
    frame = pd.DataFrame({"job_title": ["Analyst", "Engineer"], "detected_skills": [["sql", "python"], ["python", "docker"]]})
    assert transferable_skills(frame, "Analyst", "Engineer") == ["python"]
    readiness = readiness_assessment(frame, "Analyst", ["sql"])
    assert readiness["coverage_percent"] == 50 and readiness["missing"] == ["python"]
    assert readiness_assessment(frame, "Analyst", [])['coverage_percent'] is None
    assert recommend_learning_resources(["python"])[0]["resource_search"]
    assert resume_improvement_suggestions("short text", ["python"])
    assert extract_resume_text(b"Experience with Python", "resume.txt") == "Experience with Python"
    try:
        extract_resume_text(b"not a PDF", "resume.pdf")
        assert False, "Invalid PDF must be rejected"
    except ValueError:
        pass
    assert model_evaluation_summary(frame)["ranking_metrics"].startswith("Unavailable")


def test_actual_pdf_extraction_and_duplicate_resume_handling(tmp_path):
    import pymupdf
    from src.database import create_user
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Experience\nPython and SQL projects")
    payload = document.tobytes()
    document.close()
    extracted = extract_resume_text(payload, "resume.pdf")
    assert "Python" in extracted and "SQL" in extracted
    db = tmp_path / "resume.sqlite3"
    user = create_user("resume@example.test", "resume-password", db_path=db)
    assert save_resume(user, "resume.pdf", extracted, ["python", "sql"], payload, db)
    assert not save_resume(user, "resume.pdf", extracted, ["python", "sql"], payload, db)


def test_core_analysis_runs_with_network_disabled(monkeypatch):
    import socket
    def blocked(*args, **kwargs):
        raise AssertionError("Unexpected network access")
    monkeypatch.setattr(socket, "create_connection", blocked)
    frame = pd.DataFrame({"job_title": ["Analyst"], "job_description": ["SQL Python"], "skills": ["SQL Python"], "company": ["A"], "location": ["Local"], "detected_skills": [["sql", "python"]]})
    assert not match_jobs(frame, "Python SQL").empty
    assert calculate_skill_gap(frame, "Analyst", "Python")["potential_gaps"] == ["sql"]


def test_bundled_dataset_metadata_and_actual_records():
    path = get_career_dataset_path()
    frame = pd.read_csv(path)
    metadata = get_dataset_metadata(path=path)
    assert len(frame) == 3007
    assert frame["esco_code"].notna().all()
    assert frame["skills"].fillna("").str.strip().ne("").all()
    assert metadata["name"] == "ESCO v1.1.1 Occupations and Skills (English)"
    assert "European Commission" in metadata["source"]
    assert "Not verified" in metadata["license"]


def test_esco_link_parser_preserves_all_link_labels():
    assert parse_linked_skills("Python; Data, analysis", "SQL; Python") == ["python", "data, analysis", "sql"]
    frame = pd.read_csv(get_career_dataset_path())
    relation_count = sum(
        len(parse_linked_skills(essential, optional))
        for essential, optional in frame[["essential_skills", "optional_skills"]].itertuples(index=False, name=None)
    )
    assert len(frame) == 3007
    assert relation_count == 123788


def test_dataset_metadata_source_url_and_backward_compatibility(tmp_path):
    custom = tmp_path / "careers.csv"
    custom.write_text("job_title\nAnalyst\n", encoding="utf-8")
    legacy = get_dataset_metadata(custom, "careers.csv")
    assert legacy["source"] == "Not verified"
    assert legacy["license"] == "Not verified"
    supplied = get_dataset_metadata(custom, "careers.csv", "https://example.test/data", "CC BY 4.0")
    assert "https://example.test/data" in supplied["source"]
    assert supplied["license"] == "CC BY 4.0"
