# Administrator Guide

Set `CAREERLENS_ADMIN_EMAIL` and `CAREERLENS_ADMIN_PASSWORD` in the process environment before first launch. Use a unique, strong password (10+ characters). On startup, the app creates that administrator only if the email is not already registered. Registration never creates admins. Do not commit the secret or place it in source control.

The admin portal displays database counts, recent audit activity, account status, audit records, and local dataset/system information. Administrators can activate/deactivate regular accounts, generate one-time temporary user passwords, import and activate CSV dataset versions, record source/license metadata, edit the active job dataset into a new version, curate occupation-skill mappings, export/restore SQLite backups, and inspect observed coverage/feedback metrics. Admin privileges still come from the bootstrap environment, not the public UI.
