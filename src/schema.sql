CREATE TABLE jobs (
    job_id INTEGER PRIMARY KEY,
    job_title VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    location VARCHAR(255),
    job_description TEXT,
    skills TEXT,
    salary_min DECIMAL(12,2),
    salary_max DECIMAL(12,2)
);

CREATE TABLE skills (
    skill_id INTEGER PRIMARY KEY,
    skill_name VARCHAR(120) NOT NULL UNIQUE,
    category VARCHAR(100)
);

CREATE TABLE job_skills (
    job_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
);
