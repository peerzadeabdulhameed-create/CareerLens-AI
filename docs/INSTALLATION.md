# Installation

From the `CareerLens-AI` directory in PowerShell, create/activate the project's virtual environment and install the declared dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
```

Use Python 3.11 or newer (the SQLite backup API uses `Connection.serialize`/`deserialize`). The application creates `database/careerlens.db` on first launch. The `CAREERLENS_ADMIN_EMAIL` and `CAREERLENS_ADMIN_PASSWORD` environment variables are optional and are needed only to provision an administrator. Keep credentials out of source control.

PyMuPDF enables local PDF resume extraction. TXT resume support is available without it. If package installation is unavailable, existing modules can still be run without PDF support.

Launch with `streamlit run app.py`. Run automated checks with `python -m pytest -q` and `python -m compileall -q app.py src tests` from this directory. Tests use local fixtures and do not require network access.
