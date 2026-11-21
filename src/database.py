"""SQLite support for storing processed results and usage history."""

from __future__ import annotations

import sqlite3
import hashlib
import hmac
import json
import secrets
import re
from pathlib import Path


def get_database_path() -> Path:
    root = Path(__file__).resolve().parents[1]
    db_dir = root / "database"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "careerlens.db"


def initialize_database(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Create the application database and return a connection."""
    db_file = Path(db_path) if db_path else get_database_path()
    db_file.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(db_file), timeout=15)
    connection.execute("PRAGMA foreign_keys = ON")

    schema_sql = Path(__file__).resolve().parents[1] / "database" / "schema.sql"
    if schema_sql.exists():
        with schema_sql.open("r", encoding="utf-8") as handle:
            connection.executescript(handle.read())

    # Additive migrations preserve existing job records.
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE COLLATE NOCASE, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user','admin')), is_active INTEGER NOT NULL DEFAULT 1, auth_version INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS user_profiles (user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE, full_name TEXT DEFAULT '', education TEXT DEFAULT '', experience TEXT DEFAULT '', interests TEXT DEFAULT '', location TEXT DEFAULT '', verified_skills TEXT DEFAULT '[]');
        CREATE TABLE IF NOT EXISTS resumes (resume_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, filename TEXT NOT NULL, extracted_text TEXT NOT NULL DEFAULT '', extracted_skills TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS assessments (assessment_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, skill TEXT NOT NULL, proficiency INTEGER NOT NULL CHECK(proficiency BETWEEN 1 AND 5), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(user_id,skill));
        CREATE TABLE IF NOT EXISTS audit_logs (log_id INTEGER PRIMARY KEY AUTOINCREMENT, actor_id INTEGER REFERENCES users(user_id), action TEXT NOT NULL, details TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS dataset_versions (dataset_id INTEGER PRIMARY KEY AUTOINCREMENT, source_name TEXT NOT NULL, sha256 TEXT NOT NULL UNIQUE, row_count INTEGER NOT NULL, columns_json TEXT NOT NULL, csv_text TEXT NOT NULL, source_url TEXT DEFAULT '', license_terms TEXT DEFAULT '', collected_on TEXT DEFAULT '', created_by INTEGER REFERENCES users(user_id), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS app_settings (setting_key TEXT PRIMARY KEY, setting_value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS occupations (occupation_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL UNIQUE COLLATE NOCASE, description TEXT DEFAULT '', qualifications TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS occupation_skills (occupation_id INTEGER NOT NULL REFERENCES occupations(occupation_id) ON DELETE CASCADE, skill_name TEXT NOT NULL, importance INTEGER NOT NULL DEFAULT 1 CHECK(importance BETWEEN 1 AND 5), source TEXT NOT NULL DEFAULT 'admin-curated', PRIMARY KEY(occupation_id,skill_name));
        CREATE TABLE IF NOT EXISTS applications (application_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, job_title TEXT NOT NULL, company TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'Interested' CHECK(status IN ('Interested','Applied','Interviewing','Offer','Rejected','Withdrawn')), applied_on TEXT, notes TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS career_goals (goal_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, title TEXT NOT NULL, target_date TEXT, completed INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS roadmap_items (item_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, occupation TEXT NOT NULL, skill TEXT NOT NULL, priority INTEGER NOT NULL DEFAULT 0, completed INTEGER NOT NULL DEFAULT 0, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(user_id,occupation,skill));
        CREATE TABLE IF NOT EXISTS recommendation_feedback (feedback_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, job_key TEXT NOT NULL, relevance INTEGER NOT NULL CHECK(relevance BETWEEN 1 AND 5), comment TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(user_id,job_key));
        CREATE INDEX IF NOT EXISTS idx_resumes_user ON resumes(user_id);
        CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at);
    """)
    dataset_columns = {row[1] for row in connection.execute("PRAGMA table_info(dataset_versions)")}
    for column, definition in (("source_url", "TEXT DEFAULT ''"), ("license_terms", "TEXT DEFAULT ''"), ("collected_on", "TEXT DEFAULT ''")):
        if column not in dataset_columns:
            connection.execute(f"ALTER TABLE dataset_versions ADD COLUMN {column} {definition}")
    resume_columns = {row[1] for row in connection.execute("PRAGMA table_info(resumes)")}
    if "resume_hash" not in resume_columns:
        connection.execute("ALTER TABLE resumes ADD COLUMN resume_hash TEXT NOT NULL DEFAULT ''")
    connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_resume_hash_unique ON resumes(user_id,resume_hash) WHERE resume_hash != ''")
    user_columns = {row[1] for row in connection.execute("PRAGMA table_info(users)")}
    if "auth_version" not in user_columns:
        connection.execute("ALTER TABLE users ADD COLUMN auth_version INTEGER NOT NULL DEFAULT 0")
    connection.commit()

    return connection


def current_principal(user_id: int, auth_version: int | None = None, db_path: str | Path | None = None):
    """Revalidate active account and role on every Streamlit rerun."""
    connection = initialize_database(db_path)
    try:
        row = connection.execute("SELECT user_id,email,role,is_active,auth_version FROM users WHERE user_id=?", (int(user_id),)).fetchone()
        if not row or not row[3] or (auth_version is not None and row[4] != auth_version):
            return None
        return {"user_id": row[0], "email": row[1], "role": row[2], "auth_version": row[4]}
    finally:
        connection.close()


def get_profile(user_id: int, db_path: str | Path | None = None):
    connection = initialize_database(db_path)
    try:
        return connection.execute("SELECT full_name,education,experience,interests,location,verified_skills FROM user_profiles WHERE user_id=?", (int(user_id),)).fetchone()
    finally:
        connection.close()


def save_profile(user_id: int, values: tuple, db_path: str | Path | None = None) -> None:
    connection = initialize_database(db_path)
    try:
        cursor = connection.execute("UPDATE user_profiles SET full_name=?,education=?,experience=?,interests=?,location=?,verified_skills=? WHERE user_id=?", (*values, int(user_id)))
        if cursor.rowcount != 1:
            raise ValueError("Profile was not found for this account.")
        connection.commit()
    finally:
        connection.close()


def backup_database_bytes(db_path: str | Path | None = None) -> bytes:
    source = sqlite3.connect(str(db_path or get_database_path()))
    target = sqlite3.connect(":memory:")
    try:
        source.backup(target)
        return target.serialize()
    finally:
        target.close(); source.close()


def restore_database_bytes(payload: bytes, db_path: str | Path | None = None) -> None:
    """Restore a valid CareerLens SQLite backup transactionally via SQLite backup API."""
    candidate = sqlite3.connect(":memory:")
    try:
        candidate.deserialize(payload)
        integrity = candidate.execute("PRAGMA integrity_check").fetchone()[0]
        tables = {row[0] for row in candidate.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if integrity != "ok" or not {"users", "jobs", "user_profiles"}.issubset(tables):
            raise ValueError("Backup is invalid or is not a CareerLens database.")
        destination = sqlite3.connect(str(db_path or get_database_path()), timeout=15)
        try:
            candidate.backup(destination)
        finally:
            destination.close()
    finally:
        candidate.close()


def archive_dataset(csv_text: str, source_name: str, actor_id: int | None, db_path: str | Path | None = None) -> int:
    from src.career_features import dataset_fingerprint
    digest = dataset_fingerprint(csv_text)
    import pandas as pd
    frame = pd.read_csv(__import__("io").StringIO(csv_text))
    connection = initialize_database(db_path)
    try:
        connection.execute("INSERT OR IGNORE INTO dataset_versions(source_name,sha256,row_count,columns_json,csv_text,created_by) VALUES (?,?,?,?,?,?)",
                           (source_name[:255], digest, int(len(frame)), json.dumps(frame.columns.tolist()), csv_text, actor_id))
        version = connection.execute("SELECT dataset_id FROM dataset_versions WHERE sha256=?", (digest,)).fetchone()[0]
        connection.execute("INSERT INTO app_settings(setting_key,setting_value) VALUES ('active_dataset_id',?) ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value", (str(version),))
        connection.commit()
        return int(version)
    finally:
        connection.close()


def dataset_versions(db_path: str | Path | None = None):
    connection = initialize_database(db_path)
    try:
        return connection.execute("SELECT dataset_id,source_name,sha256,row_count,columns_json,source_url,license_terms,collected_on,created_at FROM dataset_versions ORDER BY dataset_id DESC").fetchall()
    finally:
        connection.close()


def update_dataset_provenance(dataset_id: int, source_url: str, license_terms: str, collected_on: str) -> None:
    connection = initialize_database()
    try:
        connection.execute("UPDATE dataset_versions SET source_url=?,license_terms=?,collected_on=? WHERE dataset_id=?", (source_url.strip()[:1000], license_terms.strip()[:500], collected_on.strip()[:80], int(dataset_id)))
        connection.commit()
    finally:
        connection.close()


def activate_dataset_version(dataset_id: int, db_path: str | Path | None = None) -> None:
    connection = initialize_database(db_path)
    try:
        if not connection.execute("SELECT 1 FROM dataset_versions WHERE dataset_id=?", (int(dataset_id),)).fetchone():
            raise ValueError("Dataset version does not exist.")
        connection.execute("INSERT INTO app_settings(setting_key,setting_value) VALUES ('active_dataset_id',?) ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value", (str(int(dataset_id)),))
        connection.commit()
    finally:
        connection.close()


def active_dataset(db_path: str | Path | None = None):
    connection = initialize_database(db_path)
    try:
        row = connection.execute("SELECT v.dataset_id,v.source_name,v.csv_text FROM dataset_versions v JOIN app_settings s ON s.setting_key='active_dataset_id' AND v.dataset_id=CAST(s.setting_value AS INTEGER)").fetchone()
        return row
    finally:
        connection.close()


def delete_user_account(user_id: int, password: str, db_path: str | Path | None = None) -> bool:
    connection = initialize_database(db_path)
    try:
        row = connection.execute("SELECT password_hash FROM users WHERE user_id=? AND role='user'", (int(user_id),)).fetchone()
        if not row or not verify_password(password, row[0]):
            return False
        connection.execute("UPDATE audit_logs SET actor_id=NULL WHERE actor_id=?", (int(user_id),))
        connection.execute("DELETE FROM users WHERE user_id=? AND role='user'", (int(user_id),))
        connection.commit()
        return True
    finally:
        connection.close()


def save_resume(user_id: int, filename: str, extracted_text: str, extracted_skills: list[str], payload: bytes, db_path: str | Path | None = None) -> bool:
    digest = hashlib.sha256(payload).hexdigest()
    connection = initialize_database(db_path)
    try:
        cursor = connection.execute("INSERT OR IGNORE INTO resumes(user_id,filename,extracted_text,extracted_skills,resume_hash) VALUES (?,?,?,?,?)", (int(user_id), filename[:255], extracted_text[:100000], json.dumps(extracted_skills), digest))
        connection.commit()
        return cursor.rowcount == 1
    finally:
        connection.close()


def change_password(user_id: int, current_password: str, new_password: str, db_path: str | Path | None = None) -> bool:
    if len(new_password) < 10 or len(new_password) > 256:
        raise ValueError("Use a password between 10 and 256 characters.")
    connection = initialize_database(db_path)
    try:
        row = connection.execute("SELECT password_hash FROM users WHERE user_id=?", (int(user_id),)).fetchone()
        if not row or not verify_password(current_password, row[0]):
            return False
        connection.execute("UPDATE users SET password_hash=?,auth_version=auth_version+1 WHERE user_id=?", (hash_password(new_password), int(user_id)))
        connection.commit()
        return True
    finally:
        connection.close()


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, salt_hex, digest_hex = stored.split("$", 2)
        if algorithm != "scrypt":
            return False
        actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1)
        return hmac.compare_digest(actual.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def create_user(email: str, password: str, name: str = "", db_path: str | Path | None = None) -> int:
    email = email.strip().lower()
    if len(password) < 10 or len(password) > 256:
        raise ValueError("Use a password between 10 and 256 characters.")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or len(email) > 254:
        raise ValueError("Enter a valid email address.")
    connection = initialize_database(db_path)
    try:
        cursor = connection.execute("INSERT INTO users(email,password_hash) VALUES (?,?)", (email, hash_password(password)))
        user_id = cursor.lastrowid
        connection.execute("INSERT INTO user_profiles(user_id,full_name) VALUES (?,?)", (user_id, name.strip()))
        connection.commit()
        return int(user_id)
    finally:
        connection.close()


def authenticate(email: str, password: str, db_path: str | Path | None = None):
    connection = initialize_database(db_path)
    try:
        row = connection.execute("SELECT user_id,email,password_hash,role,is_active,auth_version FROM users WHERE email=? COLLATE NOCASE", (email.strip(),)).fetchone()
        if row and row[4] and verify_password(password, row[2]):
            return {"user_id": row[0], "email": row[1], "role": row[3], "auth_version": row[5]}
        return None
    finally:
        connection.close()


def provision_admin(email: str, password: str, db_path: str | Path | None = None) -> bool:
    if not email or not password:
        return False
    email = email.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or len(email) > 254:
        raise ValueError("Enter a valid administrator email address.")
    if len(password) < 10 or len(password) > 256:
        raise ValueError("Bootstrap administrator password must be 10–256 characters.")
    connection = initialize_database(db_path)
    try:
        if connection.execute("SELECT 1 FROM users WHERE email=? COLLATE NOCASE", (email,)).fetchone():
            return False
        connection.execute("INSERT INTO users(email,password_hash,role) VALUES (?,?, 'admin')", (email, hash_password(password)))
        connection.commit()
        return True
    finally:
        connection.close()


def record_audit(actor_id: int | None, action: str, details: dict | None = None) -> None:
    connection = initialize_database()
    try:
        connection.execute("INSERT INTO audit_logs(actor_id,action,details) VALUES (?,?,?)", (actor_id, action, json.dumps(details or {})))
        connection.commit()
    finally:
        connection.close()


def persist_jobs(df, db_path: str | Path | None = None) -> None:
    """Store processed job rows as a minimal jobs table."""
    connection = initialize_database(db_path)
    try:
        rows = [
            (
                index,
                row.get("job_title", ""),
                row.get("job_description", ""),
                row.get("skills", ""),
                row.get("company", ""),
                row.get("location", ""),
                row.get("salary_min", ""),
                row.get("salary_max", ""),
            )
            for index, row in df.reset_index(drop=True).iterrows()
        ]
        connection.executemany(
            """
            INSERT OR REPLACE INTO jobs (
                job_id, job_title, job_description, skills, company, location, salary_min, salary_max
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()
    finally:
        connection.close()

