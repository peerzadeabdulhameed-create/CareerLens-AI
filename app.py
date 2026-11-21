import re
import os
import json
import hashlib
import html
import secrets
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import (
    create_data_quality_summary,
    dataset_as_source_label,
    get_career_dataset_path,
    get_dataset_metadata,
    infer_file_type,
    normalize_columns,
    read_csv_file,
)
from src.database import (initialize_database, persist_jobs, authenticate, create_user,
                          provision_admin, record_audit, current_principal,
                          archive_dataset, backup_database_bytes, restore_database_bytes,
                          active_dataset, dataset_versions, activate_dataset_version,
                          delete_user_account, hash_password, update_dataset_provenance)
from src.database import save_resume, change_password
from src.career_features import (explain_job_match, transferable_skills,
    readiness_assessment, recommend_learning_resources, resume_improvement_suggestions,
    extract_resume_text, model_evaluation_summary)
from src.job_matching import build_profile_text, match_jobs
from src.market_analysis import compute_metrics, location_distribution, reliable_salary_summary, role_distribution, top_skills
from src.preprocessing import build_quality_summary, parse_linked_skills, preprocess_jobs, save_processed_dataset
from src.skill_extraction import extract_skills_for_row, extract_skills_from_text
from src.skill_gap import calculate_skill_gap
from src.ui import (
    apply_design_theme,
    render_footer,
    render_kpi_card,
    render_page_header,
    render_sidebar_brand,
    render_status_badge,
    render_global_topbar,
    career_lens_logo,
    career_growth_illustration,
    render_metric_tile,
)

ROOT = Path(__file__).resolve().parent
CAREER_DATASET_PATH = get_career_dataset_path()
PROCESSED_PATH = ROOT / "data" / "processed" / "jobs_clean.csv"
DB_PATH = ROOT / "database" / "careerlens.db"

st.set_page_config(page_title="CareerLens AI", page_icon="📊", layout="wide")
apply_design_theme()

# Authentication and additive database setup. Admin bootstrap credentials are supplied
# through environment variables; public registration can only create user accounts.
initialize_database().close()
provision_admin(os.getenv("CAREERLENS_ADMIN_EMAIL", ""), os.getenv("CAREERLENS_ADMIN_PASSWORD", ""))
if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = None
elif st.session_state["auth_user"]:
    refreshed_principal = current_principal(st.session_state["auth_user"].get("user_id", -1), st.session_state["auth_user"].get("auth_version"))
    st.session_state["auth_user"] = refreshed_principal
if not st.session_state["auth_user"]:
    st.markdown("<div class='auth-topbar'><div class='auth-brand'><span class='auth-mark'>" + career_lens_logo(48) + "</span><span>CareerLens AI</span></div><div class='auth-public-nav'>Home &nbsp;&nbsp;&nbsp; About &nbsp;&nbsp;&nbsp; Learn &nbsp;&nbsp;&nbsp; Need Help?</div></div>", unsafe_allow_html=True)
    auth_left, auth_right = st.columns([1, 1], gap="small", vertical_alignment="top")
    with auth_left:
        st.markdown(f"""
        <div class="auth-panel">
          <div><div class="auth-eyebrow">Welcome to CareerLens AI</div>
          <h2>Discover. Plan. Grow.</h2>
          <p class="auth-lead">Your AI-powered career companion for smarter career decisions and a brighter future.</p>
          <div class="auth-benefits"><div class="auth-benefit"><i><svg viewBox='0 0 24 24' aria-hidden='true'><path d='M4 7h16v13H4zM9 7V4h6v3M4 12h16M10 12v2h4v-2' fill='none' stroke='white' stroke-width='1.8' stroke-linejoin='round'/></svg></i>Smart Job Matching</div><div class="auth-benefit"><i><svg viewBox='0 0 24 24' aria-hidden='true'><path d='M4 19h16M6 16l4-5 3 2 5-7M15 6h3v3' fill='none' stroke='white' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/></svg></i>Skill Gap Analysis</div><div class="auth-benefit"><i><svg viewBox='0 0 24 24' aria-hidden='true'><path d='m3 11 18-8-8 18-2-8-8-2zM11 13l5-5' fill='none' stroke='white' stroke-width='1.8' stroke-linejoin='round'/></svg></i>Personalised Career Roadmaps</div><div class="auth-benefit"><i><svg viewBox='0 0 24 24' aria-hidden='true'><path d='M12 3v12m0-12 4 4m-4-4L8 7M5 13v7h14v-7' fill='none' stroke='white' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/></svg></i>Learning Recommendations</div></div></div>
          {career_growth_illustration()}
        </div>
        """, unsafe_allow_html=True)
    with auth_right:
        st.markdown(f"<div class='auth-logo-lockup'>{career_lens_logo(68)}<strong>CareerLens <em>AI</em></strong></div>", unsafe_allow_html=True)
        st.session_state.setdefault("auth_mode", "login")
        if st.session_state["auth_mode"] == "login":
            st.markdown("<div class='auth-subtitle'><strong>Welcome Back</strong><br><span>Sign in to continue your career journey</span></div>", unsafe_allow_html=True)
            if st.session_state.pop("registration_success", False):
                st.success("Your account is ready. Sign in to continue.")
            with st.form("login_form"):
                login_email = st.text_input("Email Address", key="login_email", placeholder="Enter your email address", autocomplete="email")
                login_password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password", autocomplete="current-password")
                login_submit = st.form_submit_button("Sign In", type="primary", width="stretch")
            if login_submit:
                identity = authenticate(login_email, login_password)
                if identity:
                    st.session_state["auth_user"] = identity
                    record_audit(identity["user_id"], "login", {"role": identity["role"]})
                    st.rerun()
                st.error("Email or password is incorrect, or the account is inactive.")
            st.markdown("<div class='auth-recovery-note'>For password resets, contact your administrator.</div><div class='auth-divider'>OR</div>", unsafe_allow_html=True)
            if st.button("Create a New Account", key="open_register", width="stretch"):
                st.session_state["auth_mode"] = "register"
                st.rerun()
            st.markdown("<div class='auth-secure'><span class='auth-shield'><svg viewBox='0 0 24 24' aria-hidden='true'><path d='M12 3 19 6v5c0 5-3 8-7 10-4-2-7-5-7-10V6l7-3z' fill='none' stroke='#14B8A6' stroke-width='2'/><path d='m9 12 2 2 4-4' fill='none' stroke='#14B8A6' stroke-width='2'/></svg></span>Your data is secure and private</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='auth-subtitle'><strong>Create your account</strong><br><span>Start planning your next career step</span></div>", unsafe_allow_html=True)
            st.caption("Use a unique password between 10 and 256 characters.")
            with st.form("register_form"):
                register_name = st.text_input("Full name", placeholder="Your name", autocomplete="name")
                register_email = st.text_input("Email Address", key="register_email", placeholder="Enter your email address", autocomplete="email")
                register_password = st.text_input("Password (10+ characters)", type="password", key="register_password", autocomplete="new-password")
                register_confirm = st.text_input("Confirm password", type="password", autocomplete="new-password")
                register_submit = st.form_submit_button("Create Account", type="primary", width="stretch")
            if register_submit:
                if not register_name.strip():
                    st.error("Enter your full name.")
                elif register_password != register_confirm:
                    st.error("Passwords do not match.")
                else:
                    try:
                        create_user(register_email, register_password, register_name)
                        st.session_state["registration_success"] = True
                        st.session_state["auth_mode"] = "login"
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc) if isinstance(exc, ValueError) else "An account with that email may already exist.")
            if st.button("Back to sign in", key="back_to_login"):
                st.session_state["auth_mode"] = "login"
                st.rerun()
    st.stop()

auth_user = st.session_state["auth_user"]
admin_pages = {"Admin Dashboard", "System Analytics", "User Management", "Audit Logs", "System Settings", "Dataset Management", "Job Management", "Skills & Occupations", "Model Evaluation"}
if auth_user["role"] != "admin" and st.session_state.get("current_page") in admin_pages:
    st.error("Administrator access is required for this operation.")
    st.session_state["current_page"] = "Home"
    st.stop()


def set_page(page_name: str) -> None:
    st.session_state["nav_target"] = page_name
    st.rerun()


def get_dataset_preview(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Prepare dataset with upload fallback and source label logic."""
    if raw_df is None or raw_df.empty:
        raw_df = pd.read_csv(CAREER_DATASET_PATH)
        return raw_df, "ESCO v1.1.1 occupations and skills"

    return raw_df, dataset_as_source_label(None, "ESCO v1.1.1 occupations and skills")


def reset_market_filters() -> None:
    st.session_state["market_title_filter"] = "All"
    st.session_state["market_company_filter"] = "All"
    st.session_state["market_location_filter"] = "All"
    st.session_state["market_skill_filter"] = "All"
    st.session_state["market_search"] = ""


def reset_data_filters() -> None:
    st.session_state["data_role_filter"] = "All"
    st.session_state["data_location_filter"] = "All"
    st.session_state["data_search"] = ""
    st.session_state["data_sort"] = "job_title"


def get_user_skill_inputs(user_id: int) -> list[str]:
    """Return skills supplied or assessed by this account or its saved resumes."""
    conn = initialize_database()
    try:
        profile = conn.execute("SELECT verified_skills FROM user_profiles WHERE user_id=?", (int(user_id),)).fetchone()
        resumes = conn.execute("SELECT extracted_skills FROM resumes WHERE user_id=?", (int(user_id),)).fetchall()
        assessments = conn.execute("SELECT skill FROM assessments WHERE user_id=?", (int(user_id),)).fetchall()
    finally:
        conn.close()
    skills = set()
    if profile:
        try:
            skills.update(str(value).strip() for value in json.loads(profile[0] or "[]") if str(value).strip())
        except (TypeError, json.JSONDecodeError):
            pass
    for resume in resumes:
        try:
            skills.update(str(value).strip() for value in json.loads(resume[0] or "[]") if str(value).strip())
        except (TypeError, json.JSONDecodeError):
            continue
    skills.update(str(row[0]).strip() for row in assessments if str(row[0]).strip())
    return sorted(skills, key=str.casefold)


def load_default_dataset() -> tuple[pd.DataFrame, str, dict]:
    source_label = "ESCO v1.1.1 occupations and skills"
    raw_df = pd.read_csv(CAREER_DATASET_PATH)
    processed = prepare_jobs_for_app(raw_df, source_label)
    summary = create_data_quality_summary(raw_df)
    return processed, source_label, summary


def prepare_jobs_for_app(raw_df: pd.DataFrame, source_label: str) -> pd.DataFrame:
    processed = preprocess_jobs(raw_df)
    if "esco_code" in processed.columns:
        processed["detected_skills"] = processed.apply(
            lambda row: parse_linked_skills(row.get("essential_skills", ""), row.get("optional_skills", "")) or extract_skills_for_row(row),
            axis=1,
        )
    else:
        processed["detected_skills"] = processed.apply(extract_skills_for_row, axis=1)
    processed["skills_text"] = processed["detected_skills"].apply(lambda values: ", ".join(values))
    processed["company"] = processed["company"].fillna("")
    processed["location"] = processed["location"].fillna("")
    if processed.empty:
        return processed
    save_processed_dataset(processed, PROCESSED_PATH)
    persist_jobs(processed, DB_PATH)

    return processed


with st.sidebar:
    render_sidebar_brand()
    if auth_user["role"] == "admin":
        nav_options = ["Admin Dashboard", "User Management", "Dataset Management", "Model Evaluation", "System Analytics", "Audit Logs", "System Settings", "Job Management", "Skills & Occupations", "Privacy"]
        nav_labels = {"Admin Dashboard": "System Overview", "System Settings": "System Information", "Privacy": "Settings"}
    else:
        nav_options = ["Home", "My Profile", "Resume Intelligence", "Skill Assessment", "Job Matcher", "Job Market Explorer", "Skill Gap Analyzer", "Career Roadmap", "Career Path Comparison", "Learning Resources", "My Progress", "Privacy", "Skill Demand Analysis", "Career Knowledge Graph", "Data Explorer", "Methodology", "About", "Terms"]
        nav_labels = {"Home": "Overview", "Resume Intelligence": "Resume Analysis", "Job Matcher": "Career Recommendations", "Job Market Explorer": "Career Explorer", "Skill Gap Analyzer": "Skill Gap Analysis", "Career Path Comparison": "Career Comparison", "Privacy": "Settings", "Skill Demand Analysis": "Skill Demand Analytics"}
    if st.session_state.get("current_page") not in nav_options:
        st.session_state["current_page"] = nav_options[0]
    requested_page = st.session_state.pop("nav_target", None)
    if requested_page in nav_options:
        st.session_state["current_page"] = requested_page
    page = st.radio(
        "Navigate",
        nav_options,
        index=0,
        key="current_page",
        format_func=lambda option: nav_labels.get(option, option),
    )

    st.markdown("<div class='status-box'>" + render_status_badge("Local mode", "good") + "<div class='status-label' style='margin-top: 0.7rem;'>External services</div><div class='status-value'>None configured</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='status-label'>Dataset</div>", unsafe_allow_html=True)
    st.caption("Local occupation and skill classification; this is not a live vacancy feed.")
    uploaded_file = None
    if auth_user["role"] == "admin":
        st.caption("Dataset imports are managed from Dataset Management.")
    else:
        st.caption("Dataset updates are restricted to administrators.")

    active = active_dataset()
    if active:
        raw_df = pd.read_csv(__import__("io").StringIO(active[2]))
        source_label = active[1]
    elif CAREER_DATASET_PATH.is_file():
        raw_df = pd.read_csv(CAREER_DATASET_PATH)
        source_label = "ESCO v1.1.1 occupations and skills"
    else:
        raw_df = pd.DataFrame(columns=["job_title", "job_description", "skills", "company", "location"])
        source_label = "No occupation dataset available"
        st.warning("CareerLens has no local occupation dataset. An administrator can import a sourced CSV from Dataset Management.")

    dataset_fingerprint = hashlib.sha256(pd.util.hash_pandas_object(raw_df, index=True).values.tobytes()).hexdigest()
    cached_dataset = st.session_state.get("_prepared_career_dataset")
    if cached_dataset and cached_dataset[0] == dataset_fingerprint and cached_dataset[1] == source_label:
        jobs, summary = cached_dataset[2], cached_dataset[3]
    else:
        try:
            jobs = prepare_jobs_for_app(raw_df, source_label)
            summary = create_data_quality_summary(raw_df)
            st.session_state["_prepared_career_dataset"] = (dataset_fingerprint, source_label, jobs, summary)
        except Exception as exc:
            st.error(str(exc))
            if CAREER_DATASET_PATH.is_file():
                jobs, source_label, summary = load_default_dataset()
            else:
                jobs = pd.DataFrame(columns=["job_title", "job_description", "skills", "company", "location", "detected_skills", "skills_text"])
                summary = create_data_quality_summary(raw_df)

    active_metadata = next((version for version in dataset_versions() if active and int(version[0]) == int(active[0])), None) if active else None
    metadata = get_dataset_metadata(
        path=CAREER_DATASET_PATH if active is None else None,
        file_name=None if active is None else active[1],
        source_url=active_metadata[5] if active_metadata else None,
        license_terms=active_metadata[6] if active_metadata else None,
    )
    st.markdown(
        """
        <div class="status-box" style="margin-top: 1rem;">
            <div class="status-label">Dataset name</div>
            <div class="status-value" style="font-size: 0.92rem; margin-top:0.2rem;">{dataset_name}</div>
            <div class="status-label" style="margin-top:0.8rem;">CSV records</div>
            <div class="status-value">{rows}</div>
            <div class="status-value" style="font-size: 0.78rem;">{usable_rows} unique records after preprocessing</div>
            <div class="status-label" style="margin-top:0.8rem;">Source</div>
            <div class="status-value" style="font-size: 0.82rem;">{source}</div>
            <div class="status-label" style="margin-top:0.8rem;">License</div>
            <div class="status-value" style="font-size: 0.82rem;">{license}</div>
        </div>
        """.format(
            dataset_name=metadata["name"],
            rows=f"{len(raw_df):,}",
            usable_rows=f"{len(jobs):,}",
            source=metadata["source"],
            license=metadata["license"],
        ),
        unsafe_allow_html=True,
    )
    sidebar_conn = initialize_database()
    sidebar_name_row = sidebar_conn.execute("SELECT full_name FROM user_profiles WHERE user_id=?", (auth_user["user_id"],)).fetchone()
    sidebar_conn.close()
    sidebar_name = (sidebar_name_row[0] or auth_user["email"].split("@")[0]) if sidebar_name_row else auth_user["email"].split("@")[0]
    sidebar_initial = html.escape((sidebar_name[:1] or "C").upper())
    st.markdown(f"<div class='cl-sidebar-profile'><span class='cl-sidebar-avatar'>{sidebar_initial}</span><span class='cl-sidebar-user'><b>{html.escape(sidebar_name)}</b><small>{auth_user['role'].title()}</small></span></div>", unsafe_allow_html=True)
    if st.button("Sign out", key="sign_out", width="stretch"):
        record_audit(auth_user["user_id"], "logout")
        st.session_state["auth_user"] = None
        st.rerun()


if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"

render_global_topbar(auth_user["email"], auth_user["role"])


if page == "Admin Dashboard":
    st.markdown("<h1 class='dashboard-heading'>Administrator Dashboard</h1><div class='dashboard-subtitle'>Manage users, datasets and system performance</div>", unsafe_allow_html=True)
    conn = initialize_database()
    try:
        users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        active_count = conn.execute("SELECT COUNT(*) FROM users WHERE is_active=1").fetchone()[0]
        feedback_count = conn.execute("SELECT COUNT(*) FROM recommendation_feedback").fetchone()[0]
        recent = pd.read_sql_query("SELECT created_at,action,details FROM audit_logs ORDER BY log_id DESC LIMIT 8", conn)
        growth = pd.read_sql_query("SELECT date(created_at) AS day,COUNT(*) AS users FROM users GROUP BY date(created_at) ORDER BY day", conn)
    finally:
        conn.close()
    versions = dataset_versions()
    active_version = active_dataset()
    active_id = active_version[0] if active_version else None
    metric_cols = st.columns(4)
    admin_metrics = [
        ("Registered Users", f"{users_count:,}", "SQLite accounts", "users", "indigo"),
        ("Datasets", f"{len(versions):,}", "Imported versions", "dataset", "blue"),
        ("Career Profiles", f"{len(jobs):,}", "Current occupation dataset", "jobs", "teal"),
        ("Recommendation Feedback", f"{feedback_count:,}", "No accuracy claim without labels", "activity", "green"),
    ]
    for col, metric in zip(metric_cols, admin_metrics):
        with col:
            render_metric_tile(*metric)
    left_admin, right_admin = st.columns([1.05, 1], gap="medium")
    with left_admin:
        with st.container(border=True):
            st.markdown("<div class='panel-heading'>User Growth</div>", unsafe_allow_html=True)
            if not growth.empty:
                growth["day"] = pd.to_datetime(growth["day"])
                growth = growth.set_index("day")["users"].cumsum().reset_index(name="Registered users")
                chart = px.line(growth, x="day", y="Registered users", markers=True)
                chart.update_traces(line_color="#5145CD", marker_color="#5145CD", fill="tozeroy", fillcolor="rgba(81,69,205,.10)")
                chart.update_layout(height=300, margin=dict(l=6,r=6,t=8,b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#64748B", xaxis_title="", yaxis_title="")
                st.plotly_chart(chart, width="stretch", config={"displayModeBar": False})
            else:
                st.info("User growth will appear when accounts are registered.")
    with right_admin:
        with st.container(border=True):
            dataset_head, dataset_action = st.columns([1, .42], vertical_alignment="center")
            with dataset_head:
                st.markdown("<div class='panel-heading'>Dataset Status</div>", unsafe_allow_html=True)
            with dataset_action:
                if st.button("Manage Datasets", key="admin_manage_datasets", width="stretch"):
                    set_page("Dataset Management")
            if versions:
                status_rows = []
                for version in versions[:8]:
                    status_rows.append({"Dataset": version[1], "Version": f"v{version[0]}", "Records": f"{version[3]:,}", "Status": "Active" if version[0] == active_id else "Archived"})
                dataset_status = pd.DataFrame(status_rows)
            else:
                dataset_status = pd.DataFrame([{"Dataset": source_label, "Version": "ESCO v1.1.1" if "ESCO" in source_label else "Local", "Records": f"{len(jobs):,}", "Status": "Local classification"}])
            st.dataframe(dataset_status, width="stretch", hide_index=True)
            st.caption("The bundled ESCO dataset contains occupation concepts and skill links, not vacancies. Imported versions retain their provenance and activation state.")
    with st.container(border=True):
        st.markdown("<div class='panel-heading'>Recent Administrative Activity</div>", unsafe_allow_html=True)
        if recent.empty:
            st.info("No administrator activity has been recorded yet.")
        else:
            st.dataframe(recent, width="stretch", hide_index=True)
    st.caption(f"Active account: {active_count:,} of {users_count:,}. Recommendation accuracy is unavailable without labeled relevance or hiring outcomes.")

elif page == "System Analytics":
    st.markdown("<h1 class='dashboard-heading'>System Analytics</h1><div class='dashboard-subtitle'>Descriptive usage and dataset coverage from this local installation</div>", unsafe_allow_html=True)
    conn = initialize_database()
    try:
        actions = pd.read_sql_query("SELECT action,COUNT(*) AS events FROM audit_logs GROUP BY action ORDER BY events DESC", conn)
        daily = pd.read_sql_query("SELECT date(created_at) AS day,COUNT(*) AS events FROM audit_logs GROUP BY date(created_at) ORDER BY day", conn)
        role_count = conn.execute("SELECT COUNT(DISTINCT occupation_id) FROM occupations").fetchone()[0]
        mapping_count = conn.execute("SELECT COUNT(*) FROM occupation_skills").fetchone()[0]
        feedback_count = conn.execute("SELECT COUNT(*) FROM recommendation_feedback").fetchone()[0]
    finally:
        conn.close()
    cols = st.columns(4)
    for col, metric in zip(cols, [
        ("Audit Events", f"{int(actions.events.sum()) if not actions.empty else 0:,}", "Recorded local actions", "activity", "indigo"),
        ("Occupation Profiles", f"{len(jobs):,}", source_label, "dataset", "blue"),
        ("Curated Occupations", f"{role_count:,}", "Administrator-maintained", "roadmap", "teal"),
        ("Feedback Ratings", f"{feedback_count:,}", "User relevance responses", "skills", "green"),
    ]):
        with col: render_metric_tile(*metric)
    chart_col, table_col = st.columns(2, gap="medium")
    with chart_col:
        with st.container(border=True):
            st.markdown("<div class='panel-heading'>Recorded Events by Day</div>", unsafe_allow_html=True)
            if daily.empty:
                st.info("No audit events are available yet.")
            else:
                daily["day"] = pd.to_datetime(daily["day"])
                fig = px.bar(daily, x="day", y="events")
                fig.update_traces(marker_color="#5145CD")
                fig.update_layout(height=300, margin=dict(l=8,r=8,t=8,b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#64748B", xaxis_title="", yaxis_title="Events")
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    with table_col:
        with st.container(border=True):
            st.markdown("<div class='panel-heading'>Activity Types</div>", unsafe_allow_html=True)
            st.dataframe(actions, width="stretch", hide_index=True)
    st.caption(f"There are {mapping_count:,} curated occupation-to-skill relationships. These descriptive system metrics do not represent model accuracy.")


elif page == "Dataset Management":
    st.markdown("<h1 class='dashboard-heading'>Dataset Management</h1><div class='dashboard-subtitle'>Import, validate and track dataset versions</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<div class='panel-heading'>Import Dataset</div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], key="dataset_management_upload")
        if uploaded_file is not None and st.button("Validate and Import Dataset", key="import_csv_dataset", type="primary"):
            try:
                infer_file_type(uploaded_file)
                csv_bytes = uploaded_file.getvalue()
                if len(csv_bytes) > 10 * 1024 * 1024:
                    raise ValueError("CSV exceeds the 10 MB import limit.")
                csv_text = csv_bytes.decode("utf-8-sig")
                candidate = pd.read_csv(__import__("io").StringIO(csv_text))
                normalize_columns(candidate)
                version = archive_dataset(csv_text, uploaded_file.name, auth_user["user_id"])
                record_audit(auth_user["user_id"], "dataset_imported", {"dataset_id": version, "filename": uploaded_file.name})
                st.success("Dataset validated and activated.")
                st.rerun()
            except Exception as exc:
                st.error(f"Dataset import failed: {exc}")
        st.caption("CSV must include job_title. Imports are limited to 10 MB.")
    versions = dataset_versions()
    if not versions:
        st.info("No imported dataset versions yet. Upload and validate a CSV above.")
    else:
        version_df = pd.DataFrame(versions, columns=["Version", "Source", "SHA-256", "Rows", "Columns", "Source URL", "License", "Collected", "Imported"])
        st.dataframe(version_df.drop(columns=["Columns"]), width="stretch", hide_index=True)
        version_id = st.selectbox("Version to activate", version_df["Version"].tolist())
        selected_version = version_df[version_df.Version == version_id].iloc[0]
        conn = initialize_database()
        csv_text = conn.execute("SELECT csv_text FROM dataset_versions WHERE dataset_id=?", (int(version_id),)).fetchone()[0]
        conn.close()
        st.caption("Columns: " + ", ".join(json.loads(selected_version["Columns"])))
        st.download_button("Download this dataset version", csv_text, file_name=f"careerlens-version-{version_id}.csv", mime="text/csv")
        with st.form("dataset_provenance_form"):
            source_url = st.text_input("Source URL or citation", str(selected_version["Source URL"] or ""))
            source_license = st.text_input("License / permission notes", str(selected_version["License"] or ""))
            collected_on = st.text_input("Collection date (if known)", str(selected_version["Collected"] or ""))
            save_provenance = st.form_submit_button("Save provenance")
        if save_provenance:
            update_dataset_provenance(int(version_id), source_url, source_license, collected_on)
            record_audit(auth_user["user_id"], "dataset_provenance_updated", {"dataset_id": int(version_id)})
            st.success("Provenance saved.")
        if st.button("Activate selected version"):
            activate_dataset_version(int(version_id))
            record_audit(auth_user["user_id"], "dataset_version_activated", {"dataset_id": int(version_id)})
            st.success("Version activated. Refreshing the dataset now.")
            st.rerun()
    st.caption("Imports are validated as CSV with a required job_title column, hashed for deduplication, and retained as immutable snapshots in SQLite.")

elif page == "Job Management":
    st.title("Job Management")
    st.caption("Edit the active dataset and save as a new version; prior versions remain available for rollback.")
    source_columns = [c for c in ["job_title", "job_description", "skills", "company", "location", "salary_min", "salary_max"] if c in jobs.columns]
    edited = st.data_editor(jobs[source_columns], num_rows="dynamic", width="stretch", key="admin_jobs_editor")
    if st.button("Save as new dataset version", type="primary"):
        cleaned = edited.dropna(subset=["job_title"])
        cleaned = cleaned[cleaned.job_title.astype(str).str.strip().ne("")]
        if cleaned.empty:
            st.error("The dataset must contain at least one job with a title.")
        else:
            normalized = normalize_columns(cleaned)
            csv_text = normalized.to_csv(index=False)
            new_version = archive_dataset(csv_text, f"admin-edited-version-from-{source_label}", auth_user["user_id"])
            record_audit(auth_user["user_id"], "job_dataset_edited", {"dataset_id": new_version, "rows": len(cleaned)})
            st.success("Saved a new version; previous version remains recoverable.")
            st.rerun()

elif page == "Skills & Occupations":
    st.title("Skills & Occupations")
    inferred_skills = sorted({str(skill).casefold() for values in jobs.get("detected_skills", []) for skill in values})
    with st.form("occupation_form"):
        occupation_title = st.text_input("Occupation title")
        occupation_description = st.text_area("Description / evidence")
        qualification_notes = st.text_area("Qualification requirements (only if sourced)")
        mapped_skills = st.multiselect("Skills mapped to this occupation", inferred_skills)
        save_occupation = st.form_submit_button("Save occupation and skill links")
    if save_occupation and occupation_title.strip():
        conn = initialize_database()
        conn.execute("INSERT INTO occupations(title,description,qualifications) VALUES (?,?,?) ON CONFLICT(title) DO UPDATE SET description=excluded.description,qualifications=excluded.qualifications", (occupation_title.strip(), occupation_description.strip(), qualification_notes.strip()))
        occ = conn.execute("SELECT occupation_id FROM occupations WHERE title=? COLLATE NOCASE", (occupation_title.strip(),)).fetchone()[0]
        for mapped in mapped_skills:
            conn.execute("INSERT OR IGNORE INTO skills(skill_name) VALUES (?)", (mapped,))
            conn.execute("INSERT INTO occupation_skills(occupation_id,skill_name,source) VALUES (?,?, 'admin-curated') ON CONFLICT(occupation_id,skill_name) DO UPDATE SET source='admin-curated'", (occ, mapped))
        conn.commit(); conn.close()
        record_audit(auth_user["user_id"], "occupation_skill_mapping_updated", {"occupation": occupation_title.strip(), "skills": mapped_skills})
        st.success("Occupation and evidence-backed skill links saved.")
    conn = initialize_database()
    mappings = pd.read_sql_query("SELECT o.title AS occupation,os.skill_name,os.importance,os.source FROM occupation_skills os JOIN occupations o USING(occupation_id) ORDER BY o.title,os.skill_name", conn)
    inferred = pd.DataFrame([{"occupation": role, "skill_name": skill, "importance": None, "source": "observed in active dataset"} for role in sorted(jobs.job_title.dropna().unique()) for skill in sorted({s for values in jobs.loc[jobs.job_title == role, "detected_skills"] for s in values})])
    conn.close()
    st.subheader("Curated relationships")
    st.dataframe(mappings, width="stretch", hide_index=True)
    st.subheader("Observed occupation–skill relationships")
    st.dataframe(inferred, width="stretch", hide_index=True)

elif page == "Model Evaluation":
    st.title("Model and Data Evaluation")
    metrics = model_evaluation_summary(jobs)
    cols = st.columns(3)
    cols[0].metric("Dataset records", metrics["records"])
    cols[1].metric("Titles present", f"{metrics['title_coverage']:.1%}")
    cols[2].metric("Records with detected skills", f"{metrics['skill_coverage']:.1%}")
    st.info(metrics["ranking_metrics"])
    conn = initialize_database()
    feedback_stats = conn.execute("SELECT COUNT(*),AVG(relevance) FROM recommendation_feedback").fetchone()
    feedback_by_job = pd.read_sql_query("SELECT job_key,COUNT(*) AS responses,ROUND(AVG(relevance),2) AS mean_relevance FROM recommendation_feedback GROUP BY job_key ORDER BY responses DESC,mean_relevance DESC", conn)
    conn.close()
    f1, f2 = st.columns(2)
    f1.metric("Recommendation feedback responses", int(feedback_stats[0]))
    f2.metric("Mean relevance rating", f"{feedback_stats[1]:.2f}/5" if feedback_stats[1] is not None else "No ratings yet")
    st.dataframe(feedback_by_job, width="stretch", hide_index=True)
    st.caption("Ranking accuracy is not computed because there are no labeled relevance judgments or hiring outcomes. Coverage statistics are descriptive corpus checks, not model quality claims.")

elif page == "User Management":
    st.title("User Management")
    conn = initialize_database()
    users = pd.read_sql_query("SELECT user_id,email,role,is_active,created_at FROM users ORDER BY user_id", conn)
    conn.close()
    search_user = st.text_input("Search email")
    if search_user.strip(): users = users[users.email.str.contains(search_user.strip(), case=False, regex=False)]
    st.dataframe(users, width="stretch", hide_index=True)
    if not users.empty:
        target = st.selectbox("Account", users["user_id"].tolist(), format_func=lambda uid: users.loc[users.user_id == uid, "email"].iloc[0])
        account = users.loc[users.user_id == target].iloc[0]
        if account["role"] != "admin" and st.button("Deactivate account" if account["is_active"] else "Activate account"):
            conn = initialize_database()
            conn.execute("UPDATE users SET is_active=? WHERE user_id=? AND role='user'", (0 if account["is_active"] else 1, int(target)))
            conn.commit(); conn.close()
            record_audit(auth_user["user_id"], "account_status_changed", {"user_id": int(target), "active": not bool(account["is_active"])})
            st.rerun()
        if account["role"] == "user" and st.button("Generate one-time temporary password", key=f"reset_{target}"):
            temporary_password = secrets.token_urlsafe(18)
            conn = initialize_database()
            conn.execute("UPDATE users SET password_hash=?,auth_version=auth_version+1 WHERE user_id=? AND role='user'", (hash_password(temporary_password), int(target)))
            conn.commit(); conn.close()
            record_audit(auth_user["user_id"], "admin_password_reset", {"user_id": int(target)})
            st.warning("Share this temporary password with the account owner through a secure channel. It is shown only in this session.")
            st.code(temporary_password)

elif page == "Audit Logs":
    st.title("Audit Logs")
    conn = initialize_database()
    st.dataframe(pd.read_sql_query("SELECT l.created_at,u.email AS actor,l.action,l.details FROM audit_logs l LEFT JOIN users u ON u.user_id=l.actor_id ORDER BY l.log_id DESC", conn), width="stretch", hide_index=True)
    conn.close()

elif page == "System Settings":
    st.title("System Settings")
    st.write("Database: local SQLite")
    st.write(f"Online updates: not configured · Local dataset rows: {len(jobs):,}")
    st.info("No external model training, deployment, email recovery, or live job API is configured.")
    st.download_button("Download full SQLite backup", backup_database_bytes(DB_PATH), file_name="careerlens-backup.sqlite3", mime="application/vnd.sqlite3", help="Contains account hashes and private resume/profile records. Store securely.")
    restore_file = st.file_uploader("Restore a CareerLens SQLite backup", type=["sqlite3", "db"], key="restore_database")
    if restore_file:
        confirm_restore = st.checkbox("I understand restore replaces the current database")
        if confirm_restore and st.button("Restore database", type="primary"):
            try:
                restore_database_bytes(restore_file.getvalue(), DB_PATH)
                st.success("Database restored. Sign in again using an account in the restored copy.")
                st.session_state["auth_user"] = None
                st.rerun()
            except Exception as exc:
                st.error(f"Restore failed; current database was left in place: {exc}")

elif page == "My Profile":
    st.title("My Profile")
    conn = initialize_database()
    row = conn.execute("SELECT full_name,education,experience,interests,location,verified_skills FROM user_profiles WHERE user_id=?", (auth_user["user_id"],)).fetchone()
    conn.close()
    defaults = row or ("", "", "", "", "", "[]")
    with st.form("profile_form"):
        name = st.text_input("Full name", defaults[0] or "")
        education = st.text_area("Education", defaults[1] or "")
        experience = st.text_area("Experience", defaults[2] or "")
        interests = st.text_input("Career interests", defaults[3] or "")
        location = st.text_input("Preferred location", defaults[4] or "")
        verified_skills = st.text_input("Skills you confirm (comma separated)", ", ".join(json.loads(defaults[5] or "[]")))
        save_profile = st.form_submit_button("Save profile", type="primary")
    if save_profile:
        conn = initialize_database()
        conn.execute("UPDATE user_profiles SET full_name=?,education=?,experience=?,interests=?,location=?,verified_skills=? WHERE user_id=?", (name, education, experience, interests, location, json.dumps([s.strip().lower() for s in verified_skills.split(",") if s.strip()]), auth_user["user_id"]))
        conn.commit(); conn.close(); st.success("Profile saved.")

elif page == "Resume Intelligence":
    st.title("Resume Intelligence")
    st.caption("Resume files are processed locally and extracted text is stored in your account. Maximum 5 MB; PDF and TXT only.")
    resume_file = st.file_uploader("Upload resume", type=["pdf", "txt"], key="resume_upload")
    if resume_file:
        if resume_file.size > 5 * 1024 * 1024:
            st.error("File exceeds the 5 MB limit.")
        else:
            try:
                resume_text = extract_resume_text(resume_file.getvalue(), resume_file.name)
                resume_skills = extract_skills_from_text(resume_text)
                st.text_area("Review extracted text", resume_text[:12000], height=180)
                st.write("Detected skills", resume_skills or "No taxonomy skills found")
                st.subheader("Resume improvement suggestions")
                for suggestion in resume_improvement_suggestions(resume_text, resume_skills): st.write("• " + suggestion)
                if st.button("Save this resume to my account"):
                    if save_resume(auth_user["user_id"], resume_file.name, resume_text, resume_skills, resume_file.getvalue()): st.success("Resume analysis saved.")
                    else: st.info("This exact file has already been saved to your account.")
            except RuntimeError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Could not read resume: {exc}")

elif page == "Skill Assessment":
    st.title("Skill Assessment")
    st.caption("Self-reported proficiency, separate from skills extracted from a resume.")
    with st.form("assessment_form"):
        skill = st.text_input("Skill")
        proficiency = st.slider("Your proficiency", 1, 5, 3, help="1 = beginner, 5 = advanced")
        assessed = st.form_submit_button("Save assessment", type="primary")
    if assessed and skill.strip():
        conn = initialize_database()
        conn.execute("INSERT INTO assessments(user_id,skill,proficiency) VALUES (?,?,?) ON CONFLICT(user_id,skill) DO UPDATE SET proficiency=excluded.proficiency,created_at=CURRENT_TIMESTAMP", (auth_user["user_id"], skill.strip().lower(), proficiency))
        conn.commit(); conn.close(); st.success("Assessment saved.")
    conn = initialize_database()
    assessment_df = pd.read_sql_query("SELECT skill,proficiency,created_at FROM assessments WHERE user_id=?", conn, params=(auth_user["user_id"],))
    conn.close(); st.dataframe(assessment_df, width="stretch", hide_index=True)

elif page == "My Progress":
    st.title("My Progress")
    st.subheader("Career goals")
    with st.form("goal_form"):
        goal_title = st.text_input("Goal")
        goal_date = st.date_input("Target date", value=None)
        add_goal = st.form_submit_button("Add goal")
    conn = initialize_database()
    if add_goal and goal_title.strip():
        conn.execute("INSERT INTO career_goals(user_id,title,target_date) VALUES (?,?,?)", (auth_user["user_id"], goal_title.strip(), str(goal_date)))
        conn.commit()
    goals = pd.read_sql_query("SELECT goal_id,title,target_date,completed FROM career_goals WHERE user_id=? ORDER BY goal_id DESC", conn, params=(auth_user["user_id"],))
    conn.close()
    if not goals.empty:
        edited_goals = st.data_editor(goals, disabled=["goal_id", "title", "target_date"], column_config={"completed": st.column_config.CheckboxColumn("Complete")}, key="goal_tracker", hide_index=True)
        if st.button("Save goal progress"):
            conn = initialize_database()
            for _, goal_row in edited_goals.iterrows(): conn.execute("UPDATE career_goals SET completed=? WHERE goal_id=? AND user_id=?", (int(bool(goal_row.completed)), int(goal_row.goal_id), auth_user["user_id"]))
            conn.commit(); conn.close(); st.success("Goal progress saved.")
    st.subheader("Job application tracker")
    with st.form("application_form"):
        app_title = st.text_input("Job title")
        app_company = st.text_input("Company")
        app_status = st.selectbox("Status", ["Interested", "Applied", "Interviewing", "Offer", "Rejected", "Withdrawn"])
        app_date = st.date_input("Applied date", value=None)
        app_notes = st.text_input("Notes")
        add_application = st.form_submit_button("Save application")
    conn = initialize_database()
    if add_application and app_title.strip():
        conn.execute("INSERT INTO applications(user_id,job_title,company,status,applied_on,notes) VALUES (?,?,?,?,?,?)", (auth_user["user_id"], app_title.strip(), app_company.strip(), app_status, str(app_date), app_notes.strip()))
        conn.commit()
    application_df = pd.read_sql_query("SELECT application_id,job_title,company,status,applied_on,notes FROM applications WHERE user_id=? ORDER BY application_id DESC", conn, params=(auth_user["user_id"],))
    conn.close(); st.dataframe(application_df, width="stretch", hide_index=True)
    st.subheader("Assessment history")
    conn = initialize_database()
    assessment_df = pd.read_sql_query("SELECT skill,proficiency,created_at FROM assessments WHERE user_id=?", conn, params=(auth_user["user_id"],))
    resume_count = conn.execute("SELECT COUNT(*) FROM resumes WHERE user_id=?", (auth_user["user_id"],)).fetchone()[0]
    conn.close()
    st.metric("Saved resume analyses", resume_count)
    if assessment_df.empty: st.info("No assessments yet. Add skills in Skill Assessment to start tracking.")
    else: st.dataframe(assessment_df, width="stretch", hide_index=True)

elif page == "Learning Resources":
    st.markdown("<h1 class='dashboard-heading'>Learning Resources</h1><div class='dashboard-subtitle'>Find documentation references for skills relevant to your target role</div>", unsafe_allow_html=True)
    role_options = sorted(jobs["job_title"].dropna().astype(str).unique())
    current_skills = get_user_skill_inputs(auth_user["user_id"])
    selected_role = st.selectbox("Target role", role_options, key="learning_target_role") if role_options else ""
    if selected_role:
        learning_gap = readiness_assessment(jobs, selected_role, current_skills)
        missing_skills = learning_gap.get("missing", [])
        if missing_skills:
            resource_rows = recommend_learning_resources(missing_skills)
            st.markdown(f"<div class='panel-heading'>Suggested references for {html.escape(selected_role)}</div>", unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(resource_rows), width="stretch", hide_index=True)
            st.caption("Suggestions point to documentation search targets, not verified courses. Skills come from your profile, assessments, and saved resumes.")
        elif learning_gap.get("coverage_percent") is not None:
            st.success("No detected skill gaps for this role in the active dataset.")
        else:
            st.info(learning_gap.get("message") or "No detected skill requirements are available for this role.")
        st.caption(learning_gap.get("basis", "Based on detected skills in the active dataset."))
    else:
        st.info("No target roles are available in the current dataset.")

elif page == "Career Roadmap":
    st.title("Career Roadmap")
    target_role = st.selectbox("Target role", sorted(jobs["job_title"].dropna().astype(str).unique()))
    current = get_user_skill_inputs(auth_user["user_id"])
    gap = calculate_skill_gap(jobs, target_role, ",".join(current))
    st.write("Your skills from profile, assessments, and saved resumes", current or "Add confirmed skills in My Profile or upload a resume")
    readiness = readiness_assessment(jobs, target_role, current)
    if readiness["coverage_percent"] is not None: st.metric("Dataset skill coverage", f"{readiness['coverage_percent']}%", help="Coverage of distinct detected skills in this dataset. Not a hiring probability or validated readiness prediction.")
    else: st.info(readiness["message"] or "No required skills were detected in this dataset.")
    st.caption(readiness["basis"])
    conn = initialize_database()
    for order, skill_gap in enumerate(gap.get("priority", []), start=1):
        conn.execute("INSERT INTO roadmap_items(user_id,occupation,skill,priority) VALUES (?,?,?,?) ON CONFLICT(user_id,occupation,skill) DO UPDATE SET priority=excluded.priority,updated_at=CURRENT_TIMESTAMP", (auth_user["user_id"], target_role, skill_gap["skill"], order))
    conn.commit()
    roadmap = pd.read_sql_query("SELECT item_id,skill,priority,completed FROM roadmap_items WHERE user_id=? AND occupation=? ORDER BY priority,skill", conn, params=(auth_user["user_id"], target_role))
    conn.close()
    if roadmap.empty:
        st.success("No detected gaps for this role, or no skill records were available.")
    else:
        edited_roadmap = st.data_editor(roadmap, disabled=["item_id", "skill", "priority"], column_config={"completed": st.column_config.CheckboxColumn("Milestone complete")}, key=f"roadmap_{target_role}", hide_index=True)
        if st.button("Save roadmap progress"):
            conn = initialize_database()
            for _, item in edited_roadmap.iterrows(): conn.execute("UPDATE roadmap_items SET completed=?,updated_at=CURRENT_TIMESTAMP WHERE item_id=? AND user_id=?", (int(bool(item.completed)), int(item.item_id), auth_user["user_id"]))
            conn.commit(); conn.close(); st.success("Roadmap progress saved.")
        st.subheader("Suggested learning references")
        st.caption("Official documentation search suggestions; no course catalog is connected.")
        st.dataframe(pd.DataFrame(recommend_learning_resources(roadmap.skill.tolist())), width="stretch", hide_index=True)

elif page in {"Career Path Comparison", "Skill Demand Analysis", "Career Knowledge Graph"}:
    st.title(page)
    if page == "Career Path Comparison":
        roles = sorted(jobs["job_title"].dropna().astype(str).unique())
        selected_roles = st.multiselect("Compare roles", roles, default=roles[:2])
        user_skill_list = get_user_skill_inputs(auth_user["user_id"])
        rows = []
        for role in selected_roles:
            role_jobs = jobs[jobs["job_title"].astype(str).str.casefold() == role.casefold()]
            skills = sorted({s for items in role_jobs.get("detected_skills", []) for s in items})
            readiness = readiness_assessment(jobs, role, user_skill_list)
            overlap = transferable_skills(jobs, selected_roles[0], role) if selected_roles else []
            rows.append({"Occupation": role, "Dataset profiles": len(role_jobs), "Skill coverage": readiness["coverage_percent"], "Qualification requirements": "Not provided in this dataset", "Transferable skills from first selected role": ", ".join(overlap) if role != selected_roles[0] else "Baseline role", "Linked skills": ", ".join(skills)})
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    elif page == "Skill Demand Analysis":
        st.write("Descriptive counts only; the included dataset does not provide sufficient dated records for forecasting.")
        st.dataframe(top_skills(jobs, limit=30), width="stretch", hide_index=True)
    else:
        conn = initialize_database()
        curated = pd.read_sql_query("SELECT o.title AS occupation,os.skill_name AS skill,os.source FROM occupations o JOIN occupation_skills os USING(occupation_id)", conn)
        conn.close()
        graph_rows = curated.to_dict("records")
        for _, row in jobs.iterrows():
            for skill_item in row.get("detected_skills", []): graph_rows.append({"Occupation": row.get("job_title", ""), "Relationship": "requires (observed)", "Skill": skill_item})
        st.dataframe(pd.DataFrame(graph_rows).drop_duplicates().head(500), width="stretch", hide_index=True)
        st.caption("The graph combines administrator-curated occupation mappings with observed job-to-skill co-occurrences. Observed relationships are dataset evidence, not an authoritative occupational taxonomy.")

elif page == "Home":
    conn = initialize_database()
    try:
        dashboard_profile = conn.execute("SELECT full_name,education,experience,interests,location,verified_skills FROM user_profiles WHERE user_id=?", (auth_user["user_id"],)).fetchone()
        resume_rows = conn.execute("SELECT extracted_skills FROM resumes WHERE user_id=?", (auth_user["user_id"],)).fetchall()
        assessment_rows = conn.execute("SELECT skill FROM assessments WHERE user_id=?", (auth_user["user_id"],)).fetchall()
        resume_total = conn.execute("SELECT COUNT(*) FROM resumes WHERE user_id=?", (auth_user["user_id"],)).fetchone()[0]
        goal_total = conn.execute("SELECT COUNT(*) FROM career_goals WHERE user_id=? AND completed=0", (auth_user["user_id"],)).fetchone()[0]
        application_total = conn.execute("SELECT COUNT(*) FROM applications WHERE user_id=?", (auth_user["user_id"],)).fetchone()[0]
        roadmap_total = conn.execute("SELECT COUNT(DISTINCT occupation) FROM roadmap_items WHERE user_id=?", (auth_user["user_id"],)).fetchone()[0]
    finally:
        conn.close()
    dashboard_profile = dashboard_profile or ("", "", "", "", "", "[]")
    confirmed_skills = json.loads(dashboard_profile[5] or "[]")
    identified_skills = {str(skill).strip() for skill in confirmed_skills if str(skill).strip()}
    for resume_row in resume_rows:
        try:
            identified_skills.update(str(skill).strip() for skill in json.loads(resume_row[0] or "[]") if str(skill).strip())
        except (TypeError, json.JSONDecodeError):
            continue
    identified_skills.update(str(row[0]).strip() for row in assessment_rows if str(row[0]).strip())
    identified_skills = sorted(identified_skills, key=str.casefold)
    profile_values = [dashboard_profile[0], dashboard_profile[1], dashboard_profile[2], dashboard_profile[3], dashboard_profile[4], confirmed_skills]
    profile_complete = sum(bool(value) for value in profile_values)
    profile_percent = round(profile_complete / len(profile_values) * 100)
    display_name = dashboard_profile[0].strip() or auth_user["email"].split("@")[0]
    st.markdown(f"<h1 class='dashboard-heading'>User Dashboard</h1><div class='dashboard-subtitle'>Your personalised career intelligence hub · Welcome, {html.escape(display_name)}</div>", unsafe_allow_html=True)
    dashboard_profile_text = build_profile_text(", ".join(identified_skills), experience=dashboard_profile[2] or "", target_role=dashboard_profile[3] or "")
    if dashboard_profile_text.strip():
        try:
            dashboard_matches = match_jobs(jobs, dashboard_profile_text, top_n=24)
        except ValueError:
            dashboard_matches = pd.DataFrame(columns=["job_title", "company", "location", "description", "detected_skills", "similarity_score"])
    else:
        dashboard_matches = pd.DataFrame(columns=["job_title", "company", "location", "description", "detected_skills", "similarity_score"])
    match_role_count = dashboard_matches["job_title"].nunique() if not dashboard_matches.empty else 0
    metric_cols = st.columns(4)
    user_metrics = [
        ("Profile Completeness", f"{profile_percent}%", f"{profile_complete} of 6 sections completed", "profile", "indigo"),
        ("Skills Identified", f"{len(identified_skills):,}", "Confirmed, assessed or resume-extracted", "skills", "blue"),
        ("Career Matches", f"{match_role_count:,}", "Distinct occupations in ranked results", "jobs", "teal"),
        ("Active Roadmaps", f"{roadmap_total:,}", "Occupations with saved milestones", "roadmap", "green"),
    ]
    for col, metric in zip(metric_cols, user_metrics):
        with col:
            render_metric_tile(*metric)

    left_panel, right_panel = st.columns([1.08, .92], gap="medium")
    with left_panel:
        with st.container(border=True):
            st.markdown("<div class='panel-heading'>Career Match Overview</div>", unsafe_allow_html=True)
            if not dashboard_matches.empty:
                role_summary = dashboard_matches.groupby("job_title", as_index=False)["similarity_score"].max().sort_values("similarity_score", ascending=False).head(3)
                best_score = float(role_summary.iloc[0]["similarity_score"])
                donut_col, roles_col = st.columns([.72, 1.28], vertical_alignment="center")
                with donut_col:
                    figure = go.Figure(data=[go.Pie(values=[best_score, max(0.001, 1-best_score)], hole=.76, sort=False, marker={"colors":["#5145CD","#E5EAF5"]}, textinfo="none", hoverinfo="skip")])
                    figure.update_layout(height=205, margin=dict(l=0,r=0,t=0,b=0), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", annotations=[dict(text=f"{best_score:.0%}<br><span style='font-size:12px'>Similarity</span>", x=.5,y=.5,showarrow=False,font={"size":22,"color":"#172033"})])
                    st.plotly_chart(figure, width="stretch", config={"displayModeBar":False})
                with roles_col:
                    st.markdown("**Top matching roles**")
                    for _, role_row in role_summary.iterrows():
                        role_name = html.escape(str(role_row["job_title"]))
                        score = float(role_row["similarity_score"])
                        st.markdown(f"<div class='match-row'><div class='match-row-head'><span>{role_name}</span><span>{score:.0%}</span></div><div class='match-track'><div class='match-fill' style='width:{max(0,min(score*100,100)):.1f}%'></div></div></div>", unsafe_allow_html=True)
                st.caption("Scores are TF-IDF text similarity rankings, not hiring probabilities.")
            else:
                st.info("Add confirmed skills or experience in My Profile to get dataset-based role recommendations.")
                if st.button("Complete My Profile", key="dashboard_complete_profile", width="stretch"):
                    set_page("My Profile")
    with right_panel:
        with st.container(border=True):
            st.markdown("<div class='panel-heading'>Skill Gap Summary</div>", unsafe_allow_html=True)
            target_roles = sorted(jobs["job_title"].dropna().astype(str).unique())
            if target_roles:
                default_role = dashboard_profile[3] if dashboard_profile[3] in target_roles else target_roles[0]
                target_role = st.selectbox("Target role", target_roles, index=target_roles.index(default_role), key="dashboard_target_role")
                gap_result = readiness_assessment(jobs, target_role, identified_skills)
                missing = gap_result.get("missing", [])
                coverage = gap_result.get("coverage_percent")
                if coverage is not None:
                    st.markdown(f"**{len(missing)} skills to improve** · {html.escape(target_role)}")
                    st.progress(max(0.0, min(float(coverage)/100, 1.0)), text=f"Dataset skill coverage: {coverage}%")
                    if missing:
                        for skill in missing[:4]:
                            st.markdown(f"? {html.escape(str(skill))}")
                    else:
                        st.success("No detected skill gaps for this role in the active dataset.")
                    st.caption(gap_result.get("basis") or "Based on detected skills in the active dataset.")
                else:
                    st.info(gap_result.get("message") or "No skill requirements were detected for this role.")
            else:
                st.info("No occupations are available in the active dataset.")

    st.markdown("<div class='panel-heading' style='margin:.95rem 0 .5rem'>Quick Actions</div>", unsafe_allow_html=True)
    quick_actions = [
        ("Analyze Resume", "Resume Intelligence", "Resume Analysis"),
        ("Take Skill Assessment", "Skill Assessment", "Skill Assessment"),
        ("Explore Careers", "Job Market Explorer", "Job Market Explorer"),
        ("View Roadmap", "Career Roadmap", "Career Roadmap"),
    ]
    quick_cols = st.columns(4)
    for col, (label, destination, key) in zip(quick_cols, quick_actions):
        with col:
            st.markdown("<div class='quick-action'>", unsafe_allow_html=True)
            if st.button(label, key=f"dashboard_action_{key}", width="stretch"):
                set_page(destination)
            st.markdown("</div>", unsafe_allow_html=True)
    st.caption(f"Dataset: {source_label}. CareerLens compares your supplied profile with standardized occupations and linked skills; it does not provide live vacancies.")

elif page == "Job Market Explorer":
    st.title("Career Explorer")
    st.write("Explore standardized occupation profiles, descriptions and linked skills. These records are not job postings.")

    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            search_text = st.text_input("Search", value=st.session_state.get("market_search", ""), key="market_search")
        with col2:
            title_options = ["All", *sorted(jobs["job_title"].dropna().astype(str).str.strip().unique().tolist())]
            title_filter = st.selectbox("Occupation", title_options, index=0, key="market_title_filter")
        with col3:
            skill_options = ["All", *sorted({skill for skills in jobs["detected_skills"] for skill in skills})]
            skill_filter = st.selectbox("Linked skill", skill_options, index=0, key="market_skill_filter")
    st.caption(f"Occupation profiles available: {len(jobs):,}. This dataset contains no employer, location or salary listings.")

    apply_clicked = st.button("Apply Filters")
    clear_clicked = st.button("Clear Filters")

    if clear_clicked:
        reset_market_filters()
        st.success("Filters cleared.")
        st.rerun()

    filtered = jobs.copy()
    if search_text:
        filtered = filtered[filtered["job_title"].astype(str).str.lower().str.contains(search_text.lower()) | filtered["job_description"].astype(str).str.lower().str.contains(search_text.lower()) | filtered["skills"].astype(str).str.lower().str.contains(search_text.lower())]
    if title_filter != "All":
        filtered = filtered[filtered["job_title"].astype(str).str.lower() == title_filter.lower()]
    if skill_filter != "All":
        filtered = filtered[filtered["detected_skills"].apply(lambda values: skill_filter.lower() in [str(value).lower() for value in values])]

    if apply_clicked:
        st.success("Filters applied.")

    if filtered.empty:
        st.warning("No occupation profiles matched the selected filters.")
    else:
        st.caption(f"Showing {len(filtered)} of {len(jobs)} records")
        display = pd.DataFrame({"Occupation": filtered["job_title"], "ESCO code": filtered["esco_code"] if "esco_code" in filtered else "", "Linked skills": filtered["skills_text"], "Description": filtered["job_description"].apply(lambda text: text[:240] if len(str(text)) > 240 else text)})
        st.dataframe(display, width="stretch", hide_index=True)

elif page == "Skill Gap Analyzer":
    st.title("Skill Gap Analyzer")
    st.write("Compare your current skills against the observed requirements of a target role in the selected dataset.")
    role_options = ["Select a role", *sorted(jobs["job_title"].dropna().astype(str).str.strip().unique().tolist())]
    target_role = st.selectbox("Target Job Role", role_options)
    current_skills = st.text_area(
        "Current Skills",
        value=", ".join(get_user_skill_inputs(auth_user["user_id"])),
        help="Enter your current skills separated by commas or new lines.",
    )

    if target_role == "Select a role":
        st.info("Choose a target role to calculate skill gaps.")
    else:
        result = calculate_skill_gap(jobs, target_role, current_skills)
        matched = result.get("matched", [])
        gaps = result.get("potential_gaps", [])
        priority = result.get("priority", [])

        col1, col2, col3 = st.columns(3)
        col1.metric("Matched skills", len(matched))
        col2.metric("Potential skill gaps", len(gaps))
        col3.metric("Priority items", len(priority))

        if result.get("message"):
            st.caption(result["message"])

        if not current_skills.strip():
            st.warning("Please enter your current skills before calculating the gap.")
        else:
            st.subheader("Matched skills")
            st.write(", ".join(matched) if matched else "No exact skill matches were detected from the selected dataset.")
            st.subheader("Potential skill gaps")
            if gaps:
                gap_df = pd.DataFrame(priority)
                if not gap_df.empty:
                    fig = px.bar(
                        gap_df,
                        x="skill",
                        y="frequency",
                        title="Priority skill gaps by observed frequency",
                        labels={"skill": "Skill", "frequency": "Frequency (%)"},
                    )
                    fig.update_layout(height=320)
                    st.plotly_chart(fig, width="stretch")
                st.write(", ".join(gaps))
            else:
                st.success("No skill gaps were detected for the selected role and skill profile.")

            if priority:
                st.subheader("Skill frequency by role")
                gap_table = pd.DataFrame(priority)
                st.dataframe(gap_table, width="stretch")

elif page == "Job Matcher":
    st.title("Career Recommendations")
    st.write("Find occupation profiles similar to your supplied skills and experience using TF-IDF and cosine similarity.")

    profile_default = ", ".join(get_user_skill_inputs(auth_user["user_id"]))
    profile = st.text_area("Your profile", value=profile_default, help="Use skills you confirm, plus concise experience and interests.")
    role_options = ["All roles", *sorted(jobs["job_title"].dropna().astype(str).str.strip().unique().tolist())]
    role_filter = st.selectbox("Role Filter", role_options)
    top_n = st.selectbox("Number of results", [5, 10, 20], index=1)
    min_similarity = st.slider("Minimum similarity", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
    experience = st.text_input("Optional experience/interests", value="")

    if st.button("Run TF-IDF Matcher"):
        if not profile.strip():
            st.warning("Enter a profile before running the matcher.")
        else:
            profile_text = build_profile_text(profile, target_role="", experience=experience)
            matches = match_jobs(
                jobs,
                profile_text,
                role_filter=None if role_filter == "All roles" else role_filter,
                min_similarity=min_similarity,
                top_n=top_n,
            )
            if matches.empty:
                st.warning("No matching occupation profiles were found for the supplied profile.")
            else:
                st.success("Matching completed.")
                st.caption("Similarity score represents textual similarity and does not predict hiring outcomes.")
                for _, row in matches.iterrows():
                    with st.container(border=True):
                        st.markdown(f"### {row['job_title']}")
                        st.caption(f"Text Similarity: {row['similarity_score']:.1%}")
                        st.write(str(row["description"])[:500])
                        candidate_skills = extract_skills_from_text(profile_text)
                        explanation = explain_job_match(candidate_skills, row["detected_skills"] if isinstance(row["detected_skills"], list) else [])
                        st.write("Matching skills: " + (", ".join(explanation["matching_skills"]) or "None detected"))
                        st.write("Missing skills: " + (", ".join(explanation["missing_skills"]) or "None detected"))
                        job_key = f"{row['job_title']}|{row['company']}|{row['location']}"
                        feedback_score = st.select_slider("Was this recommendation relevant?", options=[1, 2, 3, 4, 5], value=3, key=f"feedback_{job_key}")
                        feedback_comment = st.text_input("Optional feedback", key=f"feedback_comment_{job_key}")
                        fbcol, appcol = st.columns(2)
                        with fbcol:
                            if st.button("Save feedback", key=f"save_feedback_{job_key}"):
                                conn = initialize_database()
                                conn.execute("INSERT INTO recommendation_feedback(user_id,job_key,relevance,comment) VALUES (?,?,?,?) ON CONFLICT(user_id,job_key) DO UPDATE SET relevance=excluded.relevance,comment=excluded.comment,created_at=CURRENT_TIMESTAMP", (auth_user["user_id"], job_key, feedback_score, feedback_comment))
                                conn.commit(); conn.close(); st.success("Feedback saved.")
                        with appcol:
                            if st.button("Track this job", key=f"track_job_{job_key}"):
                                conn = initialize_database()
                                conn.execute("INSERT INTO applications(user_id,job_title,company,status) VALUES (?,?,?,'Interested')", (auth_user["user_id"], str(row["job_title"]), str(row["company"])))
                                conn.commit(); conn.close(); st.success("Added to your application tracker.")

elif page == "Data Explorer":
    st.title("Data Explorer")
    st.write("Explore the underlying dataset, apply filters, and export a filtered CSV. ")

    search_term = st.text_input("Search all records", key="data_search")
    role_options = ["All", *sorted(jobs["job_title"].dropna().astype(str).str.strip().unique().tolist())]
    role_filter = st.selectbox("Job Role", role_options, key="data_role_filter")
    sort_columns = [column for column in ["job_title", "esco_code", "isco_group_code"] if column in jobs.columns]
    sort_option = st.selectbox("Sort by", sort_columns or ["job_title"], key="data_sort")
    apply_button = st.button("Apply Filters")
    clear_button = st.button("Clear Filters")

    if clear_button:
        reset_data_filters()
        st.success("Filters cleared.")
        st.rerun()

    explorer = jobs.copy()
    if search_term:
        explorer = explorer[explorer["job_title"].astype(str).str.lower().str.contains(search_term.lower()) | explorer["job_description"].astype(str).str.lower().str.contains(search_term.lower()) | explorer["skills"].astype(str).str.lower().str.contains(search_term.lower())]
    if role_filter != "All":
        explorer = explorer[explorer["job_title"].astype(str).str.lower() == role_filter.lower()]
    if sort_option in explorer.columns:
        explorer = explorer.sort_values(sort_option)

    if apply_button:
        st.success("Filters applied.")

    if explorer.empty:
        st.warning("No rows match the current filter selection.")
    else:
        st.caption(f"Showing {len(explorer)} of {len(jobs)} records")
        display_columns = ["job_title", *[column for column in ["esco_code", "isco_group_code"] if column in explorer.columns], "skills_text", "job_description"]
        display_df = explorer[display_columns].copy()
        st.dataframe(display_df, width="stretch")
        csv_bytes = display_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Filtered CSV", csv_bytes, file_name="filtered_occupations.csv", mime="text/csv")

elif page == "Methodology":
    st.title("Methodology")
    st.write(
        "This project follows a transparent dataset-driven workflow that is suitable for a college viva and academic demonstration."
    )
    st.markdown(
        """
        1. Data Collection: CareerLens loads the local ESCO v1.1.1 occupation classification and linked skills; administrator-imported CSV snapshots can replace it.
        2. Data Preprocessing: Common columns are standardized, duplicates are removed, empty rows are removed, and occupation text is cleaned. This ESCO dataset contains no salary, employer, location, or vacancy data.
        3. Exploratory Data Analysis: Occupation and linked-skill counts are computed from the selected dataset.
        4. Skill Extraction: A transparent dictionary is used to match observed technology terms such as Python, SQL, and Pandas within titles and descriptions.
        5. Skill Frequency Analysis: Counts show how often ESCO-linked skills appear across occupation profiles; they are not vacancy-demand statistics.
        6. Skill Gap Analysis: The user skills are compared with skills linked to a selected occupation to identify potential learning gaps.
        7. TF-IDF: Term Frequency-Inverse Document Frequency converts profile and occupation text into numeric vectors.
        8. Cosine Similarity: Cosine similarity ranks lexical similarity between a user profile and occupation profiles; it is not a hiring probability.
        9. Career Matching: Profile text is compared against occupation descriptions and linked skills, then the closest matches are ranked.
        10. Evaluation: The output is reviewed manually for sensible skill coverage, role relevance, and practical interpretation.
        11. Limitations: The platform is bounded by the selected dataset, the dictionary coverage, and the fact that text similarity is not hiring prediction.
        """
    )
    st.info("The project is designed to explain the analysis pipeline and make a data-science decision trace visible to students and evaluators.")

elif page == "About":
    st.title("About CareerLens AI")
    st.write("Project title: CareerLens AI")
    st.write("Project objective: To help students compare their own skills with occupation and skill information in a public career classification.")
    st.write("Technology stack: Python, Streamlit, Pandas, NumPy, Plotly, scikit-learn, SQLite, and regular expressions.")
    st.markdown("This service uses the ESCO classification of the European Commission. The CareerLens flattened occupation CSV is adapted from ESCO v1.1.1; see `data/ESCO_SOURCE.md` for provenance and reuse terms.")
    st.warning("ESCO describes standardized occupations and skills. It is not a vacancy feed; similarity scores do not predict employment or hiring outcomes.")
    st.write("Academic context: This student project demonstrates data preprocessing, ESCO occupation-skill relationships, skill extraction, and NLP-based career matching.")
    st.write("Limitations: This project depends on the selected dataset and does not guarantee employment, job selection, or salary outcomes.")
    st.write("Future scope: Live job feeds and forecasting would require separate, dated vacancy datasets and are not part of the current application.")
    st.warning("This project provides analytical career guidance and does not guarantee employment or job selection.")

elif page == "Privacy":
    st.title("Privacy and Data Handling")
    st.write("Users should avoid entering sensitive personal information.")
    st.write("The app collects your email and password for account access; only a salted scrypt password hash is stored. Career profile fields are optional.")
    st.write("Saved resume text, assessments, goals, applications, and recommendation feedback remain in the local SQLite database until you delete your account or an administrator restores another database.")
    st.write("Resume files and uploaded datasets are processed locally. No external AI API, email service, live job feed, or analytics service is configured.")
    st.write("You can export your account data below and delete your user account after confirming your password.")
    st.subheader("Export your account data")
    conn = initialize_database()
    user_export = {
        "profile": dict(zip(["full_name", "education", "experience", "interests", "location", "verified_skills"], conn.execute("SELECT full_name,education,experience,interests,location,verified_skills FROM user_profiles WHERE user_id=?", (auth_user["user_id"],)).fetchone() or ())),
        "resumes": [dict(zip(["filename", "extracted_text", "extracted_skills", "created_at"], row)) for row in conn.execute("SELECT filename,extracted_text,extracted_skills,created_at FROM resumes WHERE user_id=?", (auth_user["user_id"],))],
        "assessments": [dict(zip(["skill", "proficiency", "created_at"], row)) for row in conn.execute("SELECT skill,proficiency,created_at FROM assessments WHERE user_id=?", (auth_user["user_id"],))],
        "goals": [dict(zip(["title", "target_date", "completed"], row)) for row in conn.execute("SELECT title,target_date,completed FROM career_goals WHERE user_id=?", (auth_user["user_id"],))],
        "applications": [dict(zip(["job_title", "company", "status", "applied_on", "notes"], row)) for row in conn.execute("SELECT job_title,company,status,applied_on,notes FROM applications WHERE user_id=?", (auth_user["user_id"],))],
    }
    conn.close()
    st.download_button("Download my account data (JSON)", json.dumps(user_export, ensure_ascii=False, indent=2), file_name="careerlens-my-data.json", mime="application/json")
    st.subheader("Change password")
    with st.form("change_password_form"):
        old_password = st.text_input("Current password", type="password", key="old_password")
        new_password = st.text_input("New password (10–256 characters)", type="password", key="new_password")
        new_password_confirm = st.text_input("Confirm new password", type="password", key="new_password_confirm")
        password_submit = st.form_submit_button("Update password")
    if password_submit:
        if new_password != new_password_confirm: st.error("New passwords do not match.")
        else:
            try:
                if change_password(auth_user["user_id"], old_password, new_password):
                    st.session_state["auth_user"] = None
                    st.success("Password changed. Please sign in again.")
                    st.rerun()
                else: st.error("Current password was not accepted.")
            except ValueError as exc: st.error(str(exc))
    if auth_user["role"] == "user":
        st.subheader("Delete my account and private records")
        with st.form("delete_account_form"):
            delete_password = st.text_input("Confirm your password", type="password")
            confirm_delete = st.checkbox("I understand this permanently deletes my account and associated private records")
            delete_submit = st.form_submit_button("Delete my account")
        if delete_submit and confirm_delete:
            if delete_user_account(auth_user["user_id"], delete_password):
                st.session_state["auth_user"] = None
                st.success("Your account and private records were deleted.")
                st.rerun()
            else:
                st.error("Password was not accepted.")
    else:
        st.info("Administrator account removal is managed outside the user portal; public deletion is disabled for administrator accounts.")

elif page == "Terms":
    st.title("Terms and Limitations")
    st.write("Dataset limitations: ESCO is a standardized European occupational classification, not a live vacancy feed or a complete description of every local labour market.")
    st.write("Analytical limitations: The skill dictionary is transparent but not exhaustive and should not be interpreted as a complete taxonomy.")
    st.write("Similarity limitations: TF-IDF and cosine similarity measure textual similarity and do not infer hiring probability or job suitability.")
    st.write("No employment guarantee: This tool does not guarantee placement, selection, or employment outcomes.")
    st.write("No financial guarantee: Salary and compensation outcomes are not guaranteed and are only shown when the dataset itself contains trustworthy numeric salary information.")
    st.write("No hiring prediction: The model does not predict hiring decisions, interview outcomes, or candidate success.")

else:
    st.title("CareerLens AI")
    st.info("This view is currently unavailable. Please use the navigation in the sidebar.")

st.markdown("---")
render_footer()
st.caption("Results describe standardized occupation concepts and should not be treated as a complete description of every occupation or local labour market.")
