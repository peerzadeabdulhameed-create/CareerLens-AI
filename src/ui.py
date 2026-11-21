"""Reusable UI styling and premium dashboard helpers for CareerLens AI."""

from __future__ import annotations

import html
import streamlit as st


def apply_design_theme() -> None:
    """Apply the premium dark/light data-product theme for the application."""
    st.markdown(
        """
        <style>
            :root {
                --bg: #08111f;
                --bg-soft: #101b2b;
                --panel: rgba(17, 25, 39, 0.78);
                --panel-strong: #111c2e;
                --panel-alt: #ecf2ff;
                --border: rgba(148, 163, 184, 0.2);
                --text: #e6eefb;
                --text-soft: #a4b4cf;
                --text-muted: #7f8ca8;
                --accent: #73c5ff;
                --accent-strong: #4f8cff;
                --accent-soft: rgba(115, 197, 255, 0.14);
                --success: #78d7b7;
                --warning: #f7d988;
                --danger: #ff8d8d;
                --shadow: 0 18px 40px rgba(6, 10, 20, 0.35);
                --radius: 18px;
            }

            html, body, [data-testid="stAppViewContainer"], .stApp {
                background: linear-gradient(180deg, #08111f 0%, #0d1626 100%);
                color: var(--text);
            }

            .block-container {
                padding-top: 1.1rem;
                padding-bottom: 3rem;
                max-width: 1460px;
            }

            div[data-testid="stSidebar"] {
                background: rgba(7, 14, 25, 0.92);
                border-right: 1px solid var(--border);
            }

            .sidebar-brand {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.6rem 0.3rem 0.9rem;
                margin-bottom: 0.5rem;
            }

            .brand-mark {
                width: 38px;
                height: 38px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                border-radius: 12px;
                background: linear-gradient(135deg, var(--accent), var(--accent-strong));
                color: #06111d;
                font-weight: 800;
                box-shadow: var(--shadow);
            }

            .brand-text {
                font-size: 1.15rem;
                font-weight: 700;
                letter-spacing: 0.01em;
                color: var(--text);
            }

            .sidebar-sub {
                color: var(--text-soft);
                font-size: 0.78rem;
                margin-top: -0.2rem;
                margin-left: 0.2rem;
            }

            .nav-section {
                margin-top: 0.8rem;
            }

            .status-box {
                background: rgba(115, 197, 255, 0.08);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 0.8rem 0.8rem;
                margin: 0.8rem 0 1rem;
            }

            .status-label {
                color: var(--text-soft);
                font-size: 0.7rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }

            .status-value {
                font-size: 1rem;
                font-weight: 700;
                color: var(--text);
            }

            .nav-item {
                display: flex;
                align-items: center;
                gap: 0.7rem;
                padding: 0.7rem 0.8rem;
                border-radius: 12px;
                margin: 0.25rem 0;
                color: var(--text-soft);
                font-weight: 600;
                transition: 0.2s ease;
            }

            .nav-item:hover {
                background: rgba(148, 163, 184, 0.06);
                color: var(--text);
            }

            .nav-item.active {
                background: linear-gradient(135deg, rgba(115,197,255,0.14), rgba(79,140,255,0.08));
                color: var(--text);
                border: 1px solid rgba(115, 197, 255, 0.28);
            }

            .topbar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: rgba(10, 18, 30, 0.72);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 0.8rem 1.1rem;
                margin-bottom: 1rem;
                box-shadow: var(--shadow);
            }

            .topbar-title {
                font-size: 1.25rem;
                font-weight: 700;
                letter-spacing: 0.01em;
                color: var(--text);
            }

            .topbar-meta {
                color: var(--text-soft);
                font-size: 0.8rem;
            }

            .hero-shell {
                background: linear-gradient(135deg, rgba(115,197,255,0.12), rgba(79,140,255,0.05), rgba(17,25,39,0.84));
                border: 1px solid var(--border);
                border-radius: 22px;
                padding: 1.6rem;
                box-shadow: var(--shadow);
                margin-bottom: 1.5rem;
            }

            .hero-kicker {
                display: inline-block;
                padding: 0.3rem 0.7rem;
                border-radius: 999px;
                background: rgba(115,197,255,0.1);
                color: var(--accent);
                font-size: 0.72rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                font-weight: 700;
            }

            .hero-title {
                font-size: clamp(2.1rem, 4vw, 3.4rem);
                line-height: 1.05;
                font-weight: 800;
                margin: 0.8rem 0;
                color: var(--text);
            }

            .hero-copy {
                max-width: 720px;
                font-size: 1.02rem;
                color: var(--text-soft);
                margin-bottom: 1.2rem;
            }

            .cta-row {
                display: flex;
                gap: 0.8rem;
                flex-wrap: wrap;
                margin-bottom: 1.2rem;
            }

            .primary-btn, .secondary-btn {
                border-radius: 12px;
                padding: 0.72rem 1.1rem;
                font-weight: 700;
                cursor: pointer;
                text-decoration: none;
                transition: all 0.2s ease;
                border: 1px solid transparent;
            }

            .primary-btn {
                background: linear-gradient(135deg, var(--accent), var(--accent-strong));
                color: #071423;
                box-shadow: 0 12px 30px rgba(79, 140, 255, 0.35);
            }

            .secondary-btn {
                background: rgba(148,163,184,0.07);
                border-color: var(--border);
                color: var(--text);
            }

            .stats-strip {
                display: flex;
                gap: 1rem;
                flex-wrap: wrap;
                color: var(--text-soft);
                font-size: 0.9rem;
            }

            .stats-pill {
                display: inline-flex;
                gap: 0.5rem;
                align-items: center;
                background: rgba(15, 23, 36, 0.55);
                border: 1px solid var(--border);
                border-radius: 999px;
                padding: 0.45rem 0.8rem;
            }

            .section-title {
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--text);
                margin: 0.8rem 0 0.3rem;
            }

            .section-sub {
                color: var(--text-soft);
                font-size: 0.9rem;
                margin-bottom: 1rem;
            }

            .kpi-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 1rem;
                margin-top: 1rem;
                margin-bottom: 1.3rem;
            }

            .kpi-card {
                background: rgba(15, 23, 36, 0.9);
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 1rem 1.1rem;
                box-shadow: var(--shadow);
                min-height: 150px;
            }

            .kpi-label {
                font-size: 0.73rem;
                letter-spacing: 0.1em;
                text-transform: uppercase;
                color: var(--text-soft);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .kpi-value {
                font-size: clamp(1.8rem, 3vw, 2.5rem);
                font-weight: 800;
                color: var(--text);
                margin: 1rem 0 0.25rem;
            }

            .kpi-context {
                color: var(--text-soft);
                font-size: 0.85rem;
            }

            .insight-card {
                background: rgba(15, 23, 36, 0.8);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 1rem;
                margin-top: 1rem;
            }

            .job-card {
                background: rgba(15, 23, 36, 0.8);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 1rem;
                margin-bottom: 0.9rem;
            }

            .job-title {
                color: var(--text);
                font-size: 1.12rem;
                font-weight: 700;
            }

            .job-sub {
                color: var(--text-soft);
                font-size: 0.8rem;
                margin: 0.2rem 0 0.6rem;
            }

            .chip-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.45rem;
                margin: 0.7rem 0;
            }

            .chip {
                display: inline-flex;
                align-items: center;
                border-radius: 999px;
                background: rgba(115, 197, 255, 0.09);
                border: 1px solid rgba(115, 197, 255, 0.2);
                color: var(--text);
                padding: 0.28rem 0.6rem;
                font-size: 0.74rem;
                font-weight: 600;
            }

            .metric-foot {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 0.6rem;
                color: var(--text-soft);
                font-size: 0.8rem;
                margin-top: 0.6rem;
            }

            .data-card {
                background: rgba(15, 23, 36, 0.8);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 1rem;
            }

            .pill {
                display: inline-flex;
                align-items: center;
                border-radius: 999px;
                padding: 0.28rem 0.55rem;
                border: 1px solid var(--border);
                font-size: 0.7rem;
                font-weight: 700;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }

            .pill.good {
                background: rgba(120, 215, 183, 0.12);
                color: var(--success);
                border-color: rgba(120, 215, 183, 0.35);
            }

            .pill.warn {
                background: rgba(247, 217, 136, 0.1);
                color: var(--warning);
                border-color: rgba(247, 217, 136, 0.35);
            }

            .pill.danger {
                background: rgba(255, 141, 141, 0.08);
                color: var(--danger);
                border-color: rgba(255, 141, 141, 0.35);
            }

            .empty-box {
                background: rgba(15, 23, 36, 0.8);
                border: 1px dashed rgba(148, 163, 184, 0.35);
                border-radius: 18px;
                padding: 1.3rem;
                text-align: center;
                color: var(--text-soft);
            }

            .footer-links a {
                color: var(--text-soft);
                text-decoration: none;
            }

            @media (max-width: 768px) {
                .topbar { flex-direction: column; align-items: flex-start; }
                .hero-shell { padding: 1.1rem; }
                .cta-row { flex-direction: column; }
                .primary-btn, .secondary-btn { width: 100%; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("""<style>
    :root { --bg:#F8FAFC; --panel:#FFFFFF; --text:#172033; --text-soft:#64748B; --accent:#5145CD; }
    html,body,[data-testid="stAppViewContainer"],.stApp { background:#F8FAFC!important; color:#172033!important; }
    [data-testid="stSidebar"] { background:#FFFFFF!important; border-right:1px solid #E2E8F0!important; }
    [data-testid="stHeader"] { background:rgba(248,250,252,.9)!important; }
    .hero-shell,.topbar,.kpi-card,.insight-card,.job-card,.data-card,.empty-box { background:#FFFFFF!important; color:#172033!important; border-color:#E2E8F0!important; box-shadow:0 8px 24px rgba(23,32,51,.05)!important; }
    .hero-title,.topbar-title,.section-title,.kpi-value,.job-title,.brand-text { color:#172033!important; }
    .hero-copy,.topbar-meta,.section-sub,.kpi-context,.job-sub { color:#64748B!important; }
    .primary-btn { background:#5145CD!important; color:#fff!important; }
    button[kind="primary"] { background:#5145CD!important; }
    </style>""", unsafe_allow_html=True)
    st.markdown("""<style>
    :root {
      --cl-primary:#5145CD; --cl-secondary:#2563EB; --cl-accent:#14B8A6;
      --cl-bg:#F8FAFC; --cl-text:#172033; --cl-muted:#64748B; --cl-border:#E2E8F0;
      --cl-soft:#F1F5F9; --cl-shadow:0 8px 24px rgba(23,32,51,.055);
    }
    html, body, [data-testid="stAppViewContainer"], .stApp {
      background:var(--cl-bg)!important; color:var(--cl-text)!important;
      font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important;
    }
    [data-testid="stHeader"] {background:rgba(248,250,252,.94)!important;}
    [data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stStatusWidget"] {display:none!important;}
    [data-testid="stSidebarNav"] {display:none!important;}
    [data-testid="stToolbar"] {right:1rem;}
    .block-container {max-width:1500px!important;padding:1.25rem 2.15rem 3rem!important;}
    [data-testid="stSidebar"] {background:#fff!important;border-right:1px solid var(--cl-border)!important;}
    [data-testid="stSidebar"] > div:first-child {padding:1.1rem .9rem!important;}
    .sidebar-brand {padding:.55rem .55rem 1.15rem!important;border-bottom:1px solid var(--cl-border);margin-bottom:1rem!important;}
    .brand-mark {background:var(--cl-primary)!important;color:white!important;border-radius:12px!important;box-shadow:none!important;}
    .brand-mark svg {display:block;width:36px;height:36px;}
    .brand-text {color:var(--cl-text)!important;font-size:1.04rem!important;font-weight:750!important;}
    .sidebar-sub {color:var(--cl-muted)!important;font-size:.72rem!important;}
    [data-testid="stSidebar"] [data-testid="stRadio"] > label {font-size:.72rem!important;font-weight:700!important;color:#94A3B8!important;text-transform:uppercase;letter-spacing:.08em;margin:.5rem .35rem!important;}
    [data-testid="stSidebar"] [role="radiogroup"] {gap:.2rem!important;}
    [data-testid="stSidebar"] [role="radiogroup"] > label {border-radius:9px!important;padding:.58rem .7rem!important;margin:0!important;color:#475569!important;font-size:.89rem!important;font-weight:560!important;transition:background .15s ease,color .15s ease;}
    [data-testid="stSidebar"] [role="radiogroup"] > label:hover {background:#F1F5F9!important;color:var(--cl-primary)!important;}
    [data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) {background:#EEEDFF!important;color:var(--cl-primary)!important;font-weight:700!important;}
    [data-testid="stSidebar"] [role="radiogroup"] > label > div:first-child {display:none!important;}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {color:var(--cl-muted)!important;}
    .topbar {background:#fff!important;border:1px solid var(--cl-border)!important;border-radius:14px!important;padding:.85rem 1.15rem!important;margin:0 0 1.45rem!important;box-shadow:none!important;}
    .cl-global-topbar {min-height:48px;display:flex;align-items:center;justify-content:space-between;gap:1rem;background:#fff;border:1px solid var(--cl-border);border-radius:12px;padding:.48rem .8rem .48rem 1rem;margin:0 0 1.2rem;}
    .cl-context {display:flex;align-items:center;gap:.55rem;color:#64748B;font-size:.8rem;font-weight:570;}
    .cl-live-dot {height:8px;width:8px;border-radius:50%;background:#14B8A6;box-shadow:0 0 0 3px #CCFBF1;}
    .cl-account {display:flex;align-items:center;gap:.55rem;}
    .cl-avatar {height:34px;width:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#EEEDFF;color:#5145CD;font-size:.76rem;font-weight:750;}
    .cl-account-copy {display:flex;flex-direction:column;line-height:1.25;}
    .cl-account-copy b {color:#172033;font-size:.77rem;font-weight:650;}
    .cl-account-copy small {color:#64748B;font-size:.67rem;}
    .topbar-title {color:var(--cl-text)!important;font-size:1.14rem!important;font-weight:720!important;}
    .topbar-meta {color:var(--cl-muted)!important;font-size:.8rem!important;}
    h1,h2,h3,h4 {color:var(--cl-text)!important;letter-spacing:-.025em!important;}
    h1 {font-size:1.85rem!important;font-weight:750!important;}
    h2 {font-size:1.38rem!important;font-weight:700!important;}
    h3 {font-size:1.08rem!important;font-weight:690!important;}
    p,li {color:#475569;line-height:1.62;}
    .section-title {color:var(--cl-text)!important;font-size:1.2rem!important;font-weight:700!important;}
    .section-sub {color:var(--cl-muted)!important;}
    .kpi-card,.insight-card,.job-card,.data-card,.empty-box {background:#fff!important;border:1px solid var(--cl-border)!important;border-radius:14px!important;box-shadow:var(--cl-shadow)!important;}
    .kpi-card {min-height:122px!important;padding:1.05rem 1.1rem!important;}
    .kpi-label {color:var(--cl-muted)!important;font-size:.69rem!important;letter-spacing:.045em!important;}
    .kpi-value {color:var(--cl-text)!important;font-size:1.8rem!important;font-weight:750!important;margin:.55rem 0 .15rem!important;}
    .kpi-context {color:var(--cl-muted)!important;font-size:.76rem!important;}
    .metric-tile {display:flex;align-items:center;gap:.9rem;min-height:84px;background:#fff;border:1px solid #DCE5F2;border-radius:13px;padding:.78rem .9rem;box-shadow:0 4px 14px rgba(31,58,108,.045);}
    .metric-icon {width:52px;height:52px;flex:0 0 52px;border-radius:12px;display:flex;align-items:center;justify-content:center;background:#EEEDFF;color:#5145CD;}
    .metric-icon svg {width:28px;height:28px;}
    .metric-icon.blue {background:#E7F0FF;color:#2563EB;}.metric-icon.teal {background:#DDF8F3;color:#14B8A6;}.metric-icon.green {background:#E0F8EA;color:#16A34A;}
    .metric-copy {min-width:0;}.metric-value {color:#101D45;font-size:1.55rem;line-height:1.1;font-weight:760;letter-spacing:-.025em;}
    .metric-label {color:#172033;font-size:.78rem;font-weight:650;margin-top:.22rem;}.metric-context {color:#64748B;font-size:.68rem;line-height:1.3;margin-top:.08rem;}
    [data-testid="stVerticalBlockBorderWrapper"] {border:1px solid #DCE5F2!important;border-radius:14px!important;background:#fff!important;box-shadow:0 5px 16px rgba(31,58,108,.045)!important;}
    .cl-sidebar-profile {display:flex;align-items:center;gap:.65rem;padding:.68rem .7rem;border:1px solid #E2E8F0;border-radius:12px;background:#fff;margin:.9rem 0 .4rem;}
    .cl-sidebar-avatar {height:36px;width:36px;flex:0 0 36px;border-radius:50%;display:grid;place-items:center;background:#E8EEFF;color:#2563EB;font-weight:750;font-size:.8rem;}
    .cl-sidebar-user {display:flex;flex-direction:column;min-width:0;line-height:1.35;}.cl-sidebar-user b {color:#172033;font-size:.78rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}.cl-sidebar-user small {color:#64748B;font-size:.7rem;}
    .dashboard-heading {margin:0!important;font-size:1.55rem!important;}.dashboard-subtitle {margin:.08rem 0 .95rem;color:#64748B;font-size:.83rem;}
    .panel-heading {font-size:1.06rem;font-weight:730;color:#172033;margin:0 0 .75rem;}
    .skill-chip {display:inline-block;background:#E7F5FF;color:#1265A8;padding:.22rem .52rem;border-radius:999px;font-weight:680;font-size:.73rem;margin-right:.25rem;}
    .match-row {margin:.72rem 0;}.match-row-head {display:flex;justify-content:space-between;gap:.5rem;font-size:.78rem;color:#172033;font-weight:630;}.match-row-head span:last-child {color:#14B8A6;font-weight:720;}
    .match-track {height:7px;background:#E9EEF9;border-radius:999px;overflow:hidden;margin-top:.34rem;}.match-fill {height:100%;background:linear-gradient(90deg,#5145CD,#2563EB);border-radius:999px;}
    .quick-action button {min-height:52px!important;border:1px solid #D8E2F0!important;background:#fff!important;color:#172033!important;text-align:left!important;box-shadow:0 3px 10px rgba(31,58,108,.035)!important;}
    .quick-action button:hover {border-color:#B7C6F2!important;background:#F8FAFF!important;color:#5145CD!important;}
    .data-status-table [data-testid="stDataFrame"] {border:1px solid #E2E8F0;border-radius:10px;}
    .hero-shell {background:#fff!important;border:1px solid var(--cl-border)!important;border-radius:18px!important;box-shadow:var(--cl-shadow)!important;}
    .hero-kicker {background:#EEEDFF!important;color:var(--cl-primary)!important;}
    .hero-title {color:var(--cl-text)!important;}
    .hero-copy {color:var(--cl-muted)!important;}
    .stats-pill {background:#F8FAFC!important;color:#475569!important;border-color:var(--cl-border)!important;}
    div[data-testid="stTextInput"] input,div[data-testid="stTextArea"] textarea,div[data-testid="stNumberInput"] input {background:white!important;color:var(--cl-text)!important;border:1px solid #CBD5E1!important;border-radius:9px!important;}
    div[data-testid="stTextInput"] input:focus,div[data-testid="stTextArea"] textarea:focus {border-color:var(--cl-primary)!important;box-shadow:0 0 0 3px rgba(81,69,205,.13)!important;}
    [data-baseweb="select"] > div {background:#fff!important;border-color:#CBD5E1!important;border-radius:9px!important;}
    button[kind="primary"],[data-testid="stFormSubmitButton"] button {background:var(--cl-primary)!important;border:1px solid var(--cl-primary)!important;color:#fff!important;border-radius:9px!important;font-weight:650!important;}
button[kind="primary"]:hover,[data-testid="stFormSubmitButton"] button:hover {background:#4338B8!important;border-color:#4338B8!important;}
    button[kind="secondary"],.stButton button {border-radius:9px!important;font-weight:620!important;}
    button[kind="secondary"] {border:1px solid #CBD5E1!important;color:#334155!important;background:white!important;}
    [data-testid="stTabs"] [role="tab"] {color:#64748B!important;font-weight:620!important;}
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {color:var(--cl-primary)!important;border-bottom-color:var(--cl-primary)!important;}
    [data-testid="stDataFrame"],[data-testid="stTable"] {border:1px solid var(--cl-border)!important;border-radius:12px!important;overflow:hidden!important;}
    [data-testid="stAlert"] {border-radius:10px!important;}
    .auth-canvas {max-width:1420px;margin:1.4rem auto 1rem;}
    .auth-brand {display:flex;align-items:center;gap:.72rem;margin:0 auto 1.05rem;max-width:100%;color:#10234E;font-weight:780;font-size:1.36rem;}
    .auth-mark {height:44px;width:44px;display:flex;align-items:center;justify-content:center;background:transparent;border-radius:0;font-weight:800;}
    .auth-panel {height:100%;min-height:630px;background:radial-gradient(ellipse at 82% 0%,#DCE5FF 0%,transparent 29%),linear-gradient(145deg,#F3F4FF 0%,#F7F8FF 55%,#EFF5FF 100%);border-radius:20px 0 0 20px;padding:2.9rem 3.2rem 0;color:#172033;display:flex;flex-direction:column;justify-content:space-between;box-shadow:none;overflow:hidden;position:relative;}
    .auth-panel h2,.auth-panel h3 {color:#101D45!important;}
    .auth-panel h2 {font-size:clamp(2.15rem,3.3vw,3.1rem)!important;line-height:1.12!important;max-width:540px;margin:.9rem 0 .8rem!important;}
    .auth-panel p {color:#405578!important;}
    .auth-panel .auth-lead {font-size:1.12rem;max-width:520px;line-height:1.55;margin-bottom:1.55rem;}
    .auth-card {height:100%;min-height:630px;background:#fff;border:0;border-left:1px solid #E5E9F4;border-radius:0 20px 20px 0;padding:2.7rem 3.1rem 1.8rem;box-shadow:none;display:flex;flex-direction:column;justify-content:center;}
    .auth-shell {background:#fff;border:1px solid #E8ECF4;border-radius:21px;box-shadow:0 18px 55px rgba(34,51,96,.10);overflow:hidden;margin:0 auto;}
    .auth-shell [data-testid="stHorizontalBlock"] {gap:0!important;align-items:stretch!important;}
    .auth-card .auth-logo-lockup {text-align:center;margin-bottom:1rem;}
    .auth-card .auth-logo-lockup strong {display:block;color:#101D45;font-size:2rem;font-weight:780;letter-spacing:-.04em;line-height:1.25;}
    .auth-card .auth-logo-lockup em {color:#5145CD;font-style:normal;}
    .auth-card .auth-subtitle {text-align:center;color:#475B7D;font-size:1.03rem;margin:0 0 1.8rem;}
    .auth-card [data-testid="stWidgetLabel"] p {color:#14264D!important;font-size:.94rem!important;font-weight:650!important;margin-bottom:.35rem!important;}
    .auth-card [data-testid="stTextInput"] input {height:49px!important;min-height:49px!important;font-size:.96rem!important;padding:.55rem .85rem!important;border-radius:9px!important;background:#fff!important;color:#172033!important;border:1px solid #CBD5E1!important;}
    .auth-card [data-testid="stTextInput"] {margin-bottom:.45rem;}
    .auth-panel .auth-eyebrow {display:inline-block;color:#6327D9;background:#ECE9FF;border:1px solid #DDD5FF;border-radius:999px;padding:.43rem .8rem;letter-spacing:0;font-size:.86rem;text-transform:none;}
    .auth-benefits {display:grid;gap:.78rem;margin-top:.85rem;}
    .auth-benefit {display:flex;align-items:center;gap:.85rem;color:#14264D;font-size:1.02rem;font-weight:620;}
    .auth-benefit i {font-style:normal;color:#fff;background:#5145CD;width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.05rem;box-shadow:0 5px 12px rgba(81,69,205,.16);}
    .auth-benefit:nth-child(2) i {background:#2563EB}.auth-benefit:nth-child(3) i {background:#14B8A6}
    .career-art {display:block;width:calc(100% + 6.4rem);height:auto;max-height:225px;margin:0 -3.2rem;}
    .auth-topbar {display:flex;align-items:center;justify-content:space-between;padding:.15rem 0 1rem;border-bottom:1px solid #E7EBF3;margin-bottom:1.2rem;}
    .auth-topbar .auth-brand {margin:0;}
    .auth-public-nav {color:#14264D;font-size:.9rem;font-weight:620;}
    body:has(.auth-panel) [data-testid="stSidebar"],body:has(.auth-panel) [data-testid="stSidebarNav"] {display:none!important;}
    .block-container:has(.auth-panel) {max-width:1600px!important;padding:0 3.9rem 2.5rem!important;}
    [data-testid="stHorizontalBlock"]:has(.auth-panel) {gap:0!important;align-items:stretch!important;}
    [data-testid="stColumn"]:has(.auth-panel) {padding:0!important;}
    [data-testid="stColumn"]:has(.auth-logo-lockup) {background:#fff;border:1px solid #E8ECF4;border-left:1px solid #E5E9F4;border-radius:0 20px 20px 0;padding:2.55rem 3rem 1.6rem;box-shadow:0 18px 55px rgba(34,51,96,.10);display:flex;flex-direction:column;justify-content:center;}
    [data-testid="stColumn"]:has(.auth-panel) {border-radius:20px 0 0 20px;overflow:hidden;}
    .auth-logo-lockup {text-align:center;margin:0 auto .65rem;}
    .auth-logo-lockup svg {display:block;margin:0 auto .35rem;}
    .auth-logo-lockup strong {display:block;color:#101D45;font-size:1.9rem;font-weight:780;letter-spacing:-.04em;line-height:1.25;}
    .auth-logo-lockup em {color:#5145CD;font-style:normal;}
    .auth-subtitle {text-align:center;color:#475B7D;font-size:1.02rem;margin:0 0 1.35rem;}
    .auth-subtitle strong {display:inline-block;color:#101D45;font-size:1.3rem;font-weight:740;margin-bottom:.12rem;}
    .auth-subtitle span {color:#475B7D;font-size:.98rem;}
    .auth-recovery-note {text-align:center;color:#64748B;font-size:.78rem;margin:.6rem 0 .55rem;}
    [data-testid="stColumn"]:has(.auth-logo-lockup) [data-testid="stWidgetLabel"] p {color:#14264D!important;font-size:.93rem!important;font-weight:650!important;margin-bottom:.3rem!important;}
    [data-testid="stColumn"]:has(.auth-logo-lockup) [data-testid="stTextInput"] input {height:48px!important;min-height:48px!important;font-size:.95rem!important;padding:.55rem .85rem!important;border-radius:9px!important;background:#fff!important;color:#172033!important;border:1px solid #CBD5E1!important;}
    [data-testid="stColumn"]:has(.auth-logo-lockup) [data-testid="stTextInput"] input::placeholder {color:#64748B!important;opacity:1!important;}
    [data-testid="stColumn"]:has(.auth-logo-lockup) [data-testid="stTextInput"] input:focus {border-color:#5145CD!important;box-shadow:0 0 0 3px rgba(81,69,205,.13)!important;}
    [data-testid="stColumn"]:has(.auth-logo-lockup) [data-testid="stTextInput"] button {background:#fff!important;color:#475569!important;border-left:0!important;border-radius:0 9px 9px 0!important;}
    [data-testid="stColumn"]:has(.auth-logo-lockup) [data-testid="stTextInput"] [data-baseweb="input"] {border-radius:9px!important;overflow:hidden!important;}
    [data-testid="stColumn"]:has(.auth-logo-lockup) [data-testid="stTextInput"] [data-baseweb="input"] > div:last-child,[data-testid="stColumn"]:has(.auth-logo-lockup) [data-testid="stTextInput"] [data-baseweb="input"] > div:last-child * {background:#fff!important;color:#475569!important;}
    [data-testid="stColumn"]:has(.auth-logo-lockup) [data-testid="stTextInput"] [data-baseweb="input"] button {background:#fff!important;color:#475569!important;box-shadow:none!important;}
    [data-testid="stColumn"]:has(.auth-logo-lockup) [data-testid="stForm"] {border:0!important;padding:0!important;}
    [data-testid="stColumn"]:has(.auth-logo-lockup) [data-testid="stFormSubmitButton"] button,[data-testid="stColumn"]:has(.auth-logo-lockup) [data-testid="stFormSubmitButton"] button * {height:48px!important;background:#5145CD!important;border-color:#5145CD!important;border-radius:9px!important;font-size:1rem!important;font-weight:680!important;color:#fff!important;}
    [data-testid="stColumn"]:has(.auth-logo-lockup) [data-testid="stTabs"] [data-baseweb="tab-highlight"] {background:#5145CD!important;}
    .auth-benefit i svg {width:20px;height:20px;display:block;}
    .auth-shield svg {width:22px;height:22px;vertical-align:middle;}
    [data-testid="stColumn"]:has(.auth-logo-lockup) [data-testid="stTabs"] [role="tab"] {font-size:.9rem!important;}
    .auth-help {color:#2563EB;text-align:right;font-size:.83rem;margin:.35rem 0 .85rem;}
    .auth-panel .auth-eyebrow {color:#6327D9;background:#ECE9FF;border:1px solid #DDD5FF;border-radius:999px;padding:.43rem .8rem;letter-spacing:0;font-size:.86rem;text-transform:none;}
    .auth-benefits {display:grid;gap:.78rem;margin-top:.85rem;}
    .auth-benefit {display:flex;align-items:center;gap:.85rem;color:#14264D;font-size:1rem;font-weight:620;}
    .auth-benefit i {font-style:normal;color:#fff;background:#5145CD;width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.05rem;box-shadow:0 5px 12px rgba(81,69,205,.16);}
    .auth-benefit:nth-child(2) i {background:#2563EB}.auth-benefit:nth-child(3) i {background:#14B8A6}
    .career-art {display:block;width:calc(100% + 6.4rem);height:auto;max-height:225px;margin:0 -3.2rem;}
    .auth-divider {display:flex;align-items:center;gap:.9rem;color:#64748B;margin:.65rem 0;font-size:.82rem;}
    .auth-divider:before,.auth-divider:after {content:"";height:1px;background:#D8DFEA;flex:1;}
    .auth-secure {text-align:center;color:#506486;font-size:.84rem;margin:.5rem 0 0;}
    .auth-secure:first-letter {color:#14B8A6;}
    .auth-links {display:flex;align-items:center;gap:.45rem;}
    .auth-links [data-testid="stButton"] button {border:0!important;background:transparent!important;color:#14264D!important;padding:.48rem .68rem!important;}
    .auth-links [data-testid="stButton"] button:hover {background:#F1F5FF!important;color:#5145CD!important;}
    .auth-eyebrow {color:var(--cl-primary);font-size:.72rem;font-weight:750;letter-spacing:.1em;text-transform:uppercase;}
    .auth-foot {font-size:.78rem;color:var(--cl-muted);}
    .block-container:has(.auth-topbar) {max-width:1600px!important;padding:0 3.9rem 2.5rem!important;}
    body:has(.auth-topbar) [data-testid="stSidebar"],body:has(.auth-topbar) [data-testid="stSidebarNav"] {display:none!important;}
    .auth-card [data-testid="stTabs"] [role="tablist"] {display:none!important;}
    .auth-card [data-testid="stForm"] {border:0!important;padding:0!important;}
    .auth-divider {display:flex;align-items:center;gap:.9rem;color:#64748B;margin:.8rem 0 .65rem;font-size:.82rem;}
    .auth-divider:before,.auth-divider:after {content:"";height:1px;background:#D8DFEA;flex:1;}
    .auth-secure {text-align:center;color:#506486;font-size:.84rem;margin:.8rem 0 0;}
    .auth-secure span {color:#14B8A6;font-size:1.1rem;margin-right:.4rem;}
    .dashboard-welcome {display:flex;align-items:center;justify-content:space-between;gap:1.2rem;background:#fff;border:1px solid var(--cl-border);border-radius:15px;padding:1.1rem 1.3rem;margin:.1rem 0 1.15rem;box-shadow:var(--cl-shadow);}
    .dashboard-welcome p {margin:.18rem 0 0;color:var(--cl-muted);font-size:.86rem;}
    @media(max-width:900px) {.block-container{padding:1rem 1.15rem 2.5rem!important}.block-container:has(.auth-panel){padding:0 1rem 2rem!important}[data-testid="stHorizontalBlock"]:has(.auth-panel){flex-direction:column!important}[data-testid="stHorizontalBlock"]:has(.auth-panel)>[data-testid="stColumn"]{flex:1 1 100%!important;width:100%!important;max-width:100%!important;min-width:0!important}.auth-panel{min-height:360px;padding:2rem 2rem 0;border-radius:18px 18px 0 0}.auth-card{min-height:0;padding:2rem;border-left:0;border-top:1px solid #E5E9F4;border-radius:0 0 20px 20px}.auth-shell [data-testid="stHorizontalBlock"]{flex-direction:column!important}.block-container:has(.auth-panel) [data-testid="stHorizontalBlock"]{gap:0!important}.block-container:has(.auth-panel) [data-testid="stColumn"]:has(.auth-logo-lockup){border-left:1px solid #E8ECF4;border-top:0;border-radius:0 0 20px 20px;padding:2rem 2.2rem;}.block-container:has(.auth-panel) [data-testid="stColumn"]:has(.auth-panel){border-radius:20px 20px 0 0}.career-art{width:calc(100% + 4rem);margin:0 -2rem}.auth-canvas{margin:1rem auto}.dashboard-welcome{align-items:flex-start;flex-direction:column}}
    @media(max-width:640px) {.block-container{padding:.55rem .65rem 1.5rem!important}.block-container:has(.auth-panel){padding:0 .7rem 1.5rem!important}.topbar{align-items:flex-start!important;flex-direction:column!important}.cl-global-topbar{padding:.45rem .6rem}.cl-context{font-size:.7rem}.kpi-card{min-height:108px!important}.auth-card{padding:1.35rem 1.1rem}.auth-panel{padding:1.5rem 1.2rem 0;min-height:350px}.auth-panel>div:first-child{width:100%;min-width:0}.block-container:has(.auth-panel) [data-testid="stColumn"]:has(.auth-logo-lockup){padding:1.35rem 1.1rem;border-radius:0 0 18px 18px}.block-container:has(.auth-panel) [data-testid="stColumn"]:has(.auth-panel){border-radius:18px 18px 0 0}.auth-panel h2{font-size:2rem!important}.auth-panel .auth-lead{font-size:.97rem;max-width:100%;white-space:normal;overflow-wrap:anywhere}.auth-brand{font-size:1.07rem}.auth-mark{width:36px;height:36px}.auth-topbar{align-items:center;flex-wrap:wrap;gap:.4rem}.auth-public-nav{font-size:.69rem;text-align:left;max-width:100%;width:100%;white-space:normal;overflow-wrap:anywhere}.auth-links{gap:0}.auth-links [data-testid="stButton"] button{font-size:.75rem;padding:.36rem .38rem!important}.career-art{width:calc(100% + 2.4rem);margin:0 -1.2rem}}
    </style>""", unsafe_allow_html=True)


def render_sidebar_brand() -> None:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-mark">""" + career_lens_logo(36) + """</div>
            <div>
                <div class="brand-text">CareerLens AI</div>
                <div class="sidebar-sub">Career intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_tile(label: str, value: str | int, context: str, icon: str = "profile", tone: str = "indigo") -> None:
    """Render a compact dashboard metric using an in-product vector icon."""
    paths = {
        "profile": "M5 4h10l4 4v12H5z M14 4v5h5 M8 13h8 M8 16h6",
        "skills": "M12 3l2 5 5 .5-3.8 3.2 1.2 5.3L12 14l-4.4 3 1.2-5.3L5 8.5 10 8z",
        "jobs": "M4 8h16v12H4z M9 8V5h6v3 M4 12h16 M10 12v2h4v-2",
        "roadmap": "M5 19V5 M5 6h12l-3 4 3 4H5 M9 16l2 2 5-5",
        "users": "M16 20v-1.5a3.5 3.5 0 0 0-3.5-3.5h-5A3.5 3.5 0 0 0 4 18.5V20 M10 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7 M17 4.5a3.5 3.5 0 0 1 0 6.8 M17 15h.5a3.5 3.5 0 0 1 3.5 3.5V20",
        "dataset": "M4 7c0-1.7 3.6-3 8-3s8 1.3 8 3-3.6 3-8 3-8-1.3-8-3z M4 7v10c0 1.7 3.6 3 8 3s8-1.3 8-3V7 M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3",
        "activity": "M3 17l5-5 4 3 8-9 M15 6h5v5",
        "applications": "M4 5h16v15H4z M8 3v4 M16 3v4 M4 9h16 M8 13h3 M8 16h6",
    }
    safe_label, safe_value, safe_context = html.escape(str(label)), html.escape(str(value)), html.escape(str(context))
    path = paths.get(icon, paths["profile"])
    st.markdown(
        f"""<div class="metric-tile"><div class="metric-icon {html.escape(tone)}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="{path}" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></div><div class="metric-copy"><div class="metric-value">{safe_value}</div><div class="metric-label">{safe_label}</div><div class="metric-context">{safe_context}</div></div></div>""",
        unsafe_allow_html=True,
    )


def career_lens_logo(size: int = 52) -> str:
    """Return the small vector mark used by the login portal and sidebar."""
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 100 100" role="img" aria-label="CareerLens AI mark" xmlns="http://www.w3.org/2000/svg">
    <defs><linearGradient id="cl-logo-gradient" x1="15%" y1="90%" x2="85%" y2="5%"><stop stop-color="#14B8A6"/><stop offset=".52" stop-color="#2563EB"/><stop offset="1" stop-color="#6D28D9"/></linearGradient></defs>
    <path d="M10 82c20-6 31-19 38-37l9-24 11 14 19-20-5 29-13-8c-12 28-31 43-59 46z" fill="url(#cl-logo-gradient)"/>
    <circle cx="67" cy="17" r="8" fill="#6D28D9"/><path d="M58 28l14 8-9 16-14-7z" fill="#5145CD"/>
    <path d="M48 45l13 7-18 22-12-5zM63 51l12 2 12 14-8 6-16-12z" fill="#2563EB"/>
    </svg>"""


def career_growth_illustration() -> str:
    """Compact inline SVG illustration for the sign-in panel."""
    return """<svg class="career-art" viewBox="0 0 620 250" role="img" aria-label="A person progressing up career steps" xmlns="http://www.w3.org/2000/svg">
    <defs><linearGradient id="cl-step" x1="0" y1="1" x2="1" y2="0"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#6D5AE6"/></linearGradient><linearGradient id="cl-hill" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#EEF2FF"/><stop offset="1" stop-color="#DDE7FF"/></linearGradient></defs>
    <path d="M0 199c66-32 110-19 167 3 77 29 140 20 220-18 83-39 158-32 233-1v67H0z" fill="url(#cl-hill)"/>
    <g fill="#E7EDFF"><circle cx="86" cy="62" r="19"/><circle cx="109" cy="59" r="25"/><circle cx="131" cy="65" r="17"/><circle cx="458" cy="79" r="18"/><circle cx="482" cy="72" r="26"/><circle cx="507" cy="82" r="17"/></g>
    <g fill="url(#cl-step)"><path d="M230 214h72v36h-72z"/><path d="M302 183h73v67h-73z"/><path d="M375 151h74v99h-74z"/><path d="M449 119h74v131h-74z"/><path d="M523 87h74v163h-74z"/></g>
    <path d="M547 85V28" stroke="#15234A" stroke-width="5" stroke-linecap="round"/><path d="M550 30h49l-22 17h-27z" fill="#6D28D9"/>
    <g stroke="#14B8A6" stroke-width="7" stroke-linecap="round"><path d="M52 239q-28-29-23-55 25 16 29 45"/><path d="M75 242q-2-34 19-48 7 25-9 50"/><path d="M588 245q-4-34 15-53 10 26-5 52"/></g>
    <g fill="#172554"><circle cx="250" cy="111" r="11"/><path d="M240 126l21 4 10 28-19 13-21-16z"/><path d="M240 130l-20 20-19-3-2 8 26 6 26-22z"/><path d="M258 151l21 13 13 19-8 5-19-15-17-5z"/><path d="M240 158l-10 25-18 17 6 7 25-16 13-27z"/><path d="M235 119l20-4 19 11-3 8-20-6-18 8z" fill="#2563EB"/><rect x="203" y="145" width="14" height="17" rx="2" fill="#F59E0B"/></g>
    <path d="M178 249q18-24 35-1M184 249q0-23-13-35M608 248q10-25 26-34M605 248q-4-20-18-30" fill="none" stroke="#14B8A6" stroke-width="8" stroke-linecap="round"/>
    </svg>"""


def render_page_header(title: str, subtitle: str | None = None) -> None:
    st.markdown(
        f"""
        <div class="topbar">
            <div class="topbar-title">{title}</div>
            <div class="topbar-meta">{subtitle or 'Career market intelligence'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_global_topbar(email: str, role: str) -> None:
    safe_email = html.escape(email or "")
    safe_role = html.escape(role.title() if role else "User")
    initials = html.escape("".join(part[0] for part in (email or "CL").split("@")[0].replace(".", " ").split()[:2]).upper() or "CL")
    st.markdown(
        f"""
        <div class="cl-global-topbar">
          <div class="cl-context"><span class="cl-live-dot"></span><span>Career intelligence workspace</span></div>
          <div class="cl-account"><span class="cl-avatar">{initials}</span><span class="cl-account-copy"><b>{safe_email}</b><small>{safe_role} account</small></span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str | None = None) -> None:
    st.markdown(f"<div class=\"section-title\">{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class=\"section-sub\">{subtitle}</div>", unsafe_allow_html=True)


def render_kpi_card(label: str, value: str, context: str, accent: str = "") -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label"><span>{label}</span><span>{accent}</span></div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-context">{context}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_badge(text: str, tone: str = "good") -> str:
    return f'<span class="pill {tone}">{text}</span>'


def render_empty_state(title: str, description: str, action_label: str | None = None) -> None:
    st.markdown(
        f"""
        <div class="empty-box">
            <div style="font-size:1.1rem;font-weight:700;color:var(--text);margin-bottom:0.35rem;">{title}</div>
            <div>{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if action_label:
        st.caption(action_label)


def render_job_card(title: str, company: str, location: str, skills: list[str], description: str, score: str | None = None) -> None:
    chips = "".join(f"<span class='chip'>{skill}</span>" for skill in skills[:6])
    score_html = f"<div class='metric-foot'><span>Text similarity</span><strong>{score}</strong></div>" if score else ""
    st.markdown(
        f"""
        <div class="job-card">
            <div class="job-title">{title}</div>
            <div class="job-sub">{company} • {location}</div>
            <div class="chip-row">{chips}</div>
            <div style="color: var(--text-soft); font-size:0.9rem; line-height:1.6;">{description[:260]}...</div>
            {score_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        """
        <div style="margin-top:2rem;padding-top:1rem;border-top:1px solid #E2E8F0;color:#64748B;font-size:.76rem;">
            CareerLens AI · Local career intelligence · Recommendations reflect the active dataset and are not employment predictions.
        </div>
        """,
        unsafe_allow_html=True,
    )
