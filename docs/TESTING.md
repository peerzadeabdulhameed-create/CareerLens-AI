# Verification Report

Updated on 2026-11-21 in the project environment.

| Check | Expected | Actual | Result |
|---|---|---|---|
| pytest suite | Existing analysis plus auth, isolation, migration, dataset version, backup, career feature, PDF, offline and ESCO metadata/link tests pass | `.venv\Scripts\python.exe -m pytest -q`: **17 passed** | Pass |
| Project virtual environment | Declared dependencies are installed and consistent | `.venv` Python 3.14.5; `pip check` reported no broken requirements; PyMuPDF 2.1 imports successfully | Pass |
| Virtual-environment test run | Tests use the same interpreter as the launch environment | `.venv\Scripts\python.exe -m pytest -q`: **17 passed** | Pass |
| Python compile check | App/source/scripts/tests compile | `.venv\Scripts\python.exe -m compileall -q app.py src scripts tests` returned 0 | Pass |
| User and admin sign-in | Temporary user/admin sign in without app errors | Streamlit AppTest passed | Pass |
| Portal route rendering | Every user route and all 9 admin routes render | Streamlit AppTest: 26 routes, zero exceptions; changed Home/Privacy/Roadmap/Progress routes rerun | Pass |
| Resume upload and extraction | Actual PDF is uploaded through AppTest, parsed, saved per account, and its skills prefill the career matcher | Temporary user upload/matcher flow passed with no exceptions; account deleted afterward | Pass |
| Real career dataset | Source counts and actual skill relationships are used | 3,007 occupation rows, 123,788 links; TF-IDF returned 5 real role matches | Pass |
| Offline core analysis | Matching and skill-gap work with socket connections blocked | Network-disabled test passed | Pass |
| Database persistence/recovery | Profile isolation, session invalidation, dataset activation, backup round trip | Temporary SQLite test databases passed | Pass |
| Live startup | Streamlit server starts | Server announced local URL on port 8501 | Pass |
| Live health endpoint | Health endpoint responds | `/_stcore/health` returned `ok` | Pass |
| Test account cleanup | Temporary integration accounts removed | Local user table returned zero registered accounts after cleanup | Pass |

Not exercised: uploading through an external real browser, clicking the admin restore/download controls, concurrent sessions, adversarial data-isolation testing, OS-level internet shutdown, responsive/mobile rendering, keyboard/screen-reader checks, WCAG contrast audit, and production threat testing. AppTest verifies application rendering and upload widget behavior, not a visual/browser transport audit.

Iteration notes: an early AppTest used its 3-second default and timed out; a longer timeout passed. A temporary dataset test first failed because it referenced a nonexistent audit actor; the fixture was corrected. The `fitz` deprecation and Streamlit `use_container_width` warning were resolved by using the recommended `pymupdf` module and `width="stretch"` API.
