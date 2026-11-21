CREATE TABLE IF NOT EXISTS jobs (
    job_id INTEGER PRIMARY KEY,
    job_title TEXT,
    job_description TEXT,
    skills TEXT,
    company TEXT,
    location TEXT,
    salary_min REAL,
    salary_max REAL
);

CREATE TABLE IF NOT EXISTS skills (
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS job_skills (
    job_id INTEGER,
    skill_name TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);

CREATE TABLE IF NOT EXISTS analysis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    dataset_source TEXT,
    target_role TEXT,
    analysis_type TEXT
);
