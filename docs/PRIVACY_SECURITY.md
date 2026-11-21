# Privacy and Security

Passwords are stored as salted scrypt hashes. SQL uses parameterized statements for account and profile operations. User-owned profile, resume, and assessment records are selected using the authenticated user ID. Public registration cannot assign roles. Resume uploads are size-checked (5 MB), restricted to PDF/TXT, processed locally, and bounded before storage; extracted text can contain sensitive information and is stored in SQLite until the database is removed by the operator.

No email service, external AI API, telemetry, or live job service is configured. Users can change their password; this invalidates older sessions. A signed-in administrator can issue a one-time temporary password and share it out of band; no email reset flow is available. Users can export their account records and delete their account after re-entering the password. Admins can make and restore full SQLite backups. Backups include password hashes and resume/profile content, are not encrypted, and must be stored securely.

Remaining hardening gaps include login rate limiting, encrypted database/backup storage, key rotation, retention automation, deployment-grade CSRF/session controls, and a production security review. Treat this as an academic/local deployment and do not expose it directly to the public internet.
