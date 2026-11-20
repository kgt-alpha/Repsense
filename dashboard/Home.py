"""RepSense Streamlit dashboard: workout logging and evidence-backed analytics."""

import html
import os
from datetime import date

import httpx
import pandas as pd
import streamlit as st

st.set_page_config(page_title="RepSense | Training", page_icon="🏋️", layout="wide")
API_URL = os.getenv("REPSENSE_API_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = 10.0

# ----------------------------------------------------------------------------
# Design system: Gray #2B2D31 · Silver #D9DADC · Yellow #FFC93C
# ----------------------------------------------------------------------------
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #2B2D31;
  --panel: #33363B;
  --deep: #232528;
  --line: rgba(217, 218, 220, .13);
  --text: #D9DADC;
  --muted: #9C9EA3;
  --yellow: #FFC93C;
  --ink: #1D1E21;
}

html, body, .stApp, [class*="css"] { font-family: 'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif; }
.stApp { background: var(--bg); color: var(--text); }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"], #MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1200px; }
h1, h2, h3, h4, h5 { color: #fff; letter-spacing: -.02em; font-weight: 800; }
p, li, label, span { color: var(--text); }
a { color: var(--yellow); }
hr { border-color: var(--line); }
[data-testid="stCaptionContainer"], .stCaption, small { color: var(--muted) !important; }

/* ---- Sidebar ---- */
[data-testid="stSidebar"] { background: var(--deep); border-right: 1px solid var(--line); }
[data-testid="stSidebar"] [role="radiogroup"] { gap: .3rem; }
[data-testid="stSidebar"] [role="radiogroup"] label { padding: .62rem .85rem; border-radius: 12px; width: 100%; cursor: pointer; transition: background .15s; }
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child { display: none; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(255, 255, 255, .06); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { background: var(--yellow); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p { color: var(--ink) !important; font-weight: 700; }
[data-testid="stSidebar"] [role="radiogroup"] label p { font-weight: 600; }

/* ---- Buttons ---- */
button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"], button[kind="primary"], button[kind="primaryFormSubmit"] {
  background: var(--yellow) !important; color: var(--ink) !important; border: none !important;
  border-radius: 999px !important; font-weight: 700 !important; padding: .55rem 1.5rem !important;
  transition: transform .12s, filter .12s;
}
button[data-testid="stBaseButton-primary"] p, button[data-testid="stBaseButton-primaryFormSubmit"] p { color: var(--ink) !important; font-weight: 700; }
button[data-testid="stBaseButton-primary"]:hover, button[data-testid="stBaseButton-primaryFormSubmit"]:hover { filter: brightness(1.06); transform: translateY(-1px); }
button[data-testid="stBaseButton-secondary"], button[data-testid="stBaseButton-secondaryFormSubmit"], button[kind="secondary"] {
  background: transparent !important; color: var(--text) !important; border: 1px solid var(--line) !important; border-radius: 999px !important; font-weight: 600 !important;
}
button[data-testid="stBaseButton-secondary"]:hover { border-color: var(--yellow) !important; color: var(--yellow) !important; }

/* ---- Inputs ---- */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"], [data-baseweb="select"] > div, [data-testid="stDateInput"] [data-baseweb="input"] {
  background-color: var(--deep) !important; border-radius: 12px !important; border: 1px solid var(--line) !important;
}
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within, [data-baseweb="select"] > div:focus-within { border-color: var(--yellow) !important; }
input, textarea { color: var(--text) !important; -webkit-text-fill-color: var(--text) !important; }
[data-baseweb="popover"] ul, [data-baseweb="menu"] { background: var(--panel) !important; border-radius: 12px; }
[data-baseweb="popover"] li:hover { background: rgba(255, 201, 60, .14) !important; }
[data-testid="stWidgetLabel"] p { color: var(--text); font-weight: 600; font-size: .88rem; }

/* ---- Forms, tabs, alerts, expanders ---- */
[data-testid="stForm"] { background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 1.4rem; }
button[data-baseweb="tab"] { font-weight: 700; color: var(--muted); }
button[data-baseweb="tab"][aria-selected="true"] { color: #fff; }
[data-baseweb="tab-highlight"] { background-color: var(--yellow) !important; height: 3px; }
[data-baseweb="tab-border"] { background-color: var(--line) !important; }
[data-testid="stAlert"] { border-radius: 14px; border: 1px solid var(--line); background: var(--panel); }
[data-testid="stExpander"] { background: var(--panel); border: 1px solid var(--line) !important; border-radius: 14px; }
[data-testid="stExpander"] details { border: none !important; }
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; border: 1px solid var(--line); }
[data-testid="stMetric"] { background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 16px 18px; }
[data-testid="stMetricLabel"] p { color: var(--muted); font-weight: 600; }
[data-testid="stMetricValue"] { color: #fff; font-weight: 800; }

/* ---- Landing-style components ---- */
.rs-nav { display: flex; align-items: center; justify-content: space-between; padding: .4rem 0 1.6rem; }
.rs-brand { display: flex; align-items: center; gap: .6rem; font-weight: 800; font-size: 1.15rem; color: #fff; letter-spacing: -.02em; }
.rs-logo { display: inline-flex; width: 30px; height: 30px; border-radius: 9px; background: var(--yellow); color: var(--ink); align-items: center; justify-content: center; font-weight: 800; font-size: .95rem; }
.rs-links { display: flex; gap: 1.6rem; color: var(--muted); font-size: .85rem; font-weight: 500; }
.rs-nav-right { display: flex; align-items: center; gap: 1.1rem; font-size: .85rem; color: var(--muted); }
.rs-pill { background: var(--yellow); color: var(--ink); font-weight: 700; padding: .5rem 1.1rem; border-radius: 999px; font-size: .82rem; }
.rs-chip { border: 1px solid var(--line); padding: .4rem .9rem; border-radius: 999px; color: var(--text); font-size: .8rem; }
.rs-badge { display: inline-flex; align-items: center; gap: .55rem; border: 1px solid var(--line); border-radius: 999px; padding: .32rem .8rem .32rem .35rem; font-size: .76rem; color: var(--muted); margin-bottom: 1.3rem; }
.rs-badge b { background: var(--yellow); color: var(--ink); border-radius: 999px; padding: .12rem .55rem; font-size: .66rem; letter-spacing: .04em; }
.rs-hero { font-size: clamp(2.5rem, 5.2vw, 4rem); line-height: 1.04; font-weight: 800; color: #fff; letter-spacing: -.035em; margin: 0 0 1.1rem; }
mark { background: var(--yellow); color: var(--ink); padding: 0 .2em; border-radius: .22em; }
.rs-sub { color: var(--muted); font-size: 1.02rem; line-height: 1.6; max-width: 34rem; margin-bottom: 1.8rem; }
.rs-stats { display: flex; gap: 2.6rem; flex-wrap: wrap; border-top: 1px solid var(--line); padding-top: 1.4rem; margin-top: 1.6rem; }
.rs-stat b { display: block; font-size: 1.55rem; font-weight: 800; color: #fff; letter-spacing: -.02em; }
.rs-stat span { font-size: .78rem; color: var(--muted); }
.rs-status { display: inline-block; font-size: .78rem; font-weight: 600; padding: .3rem .8rem; border-radius: 999px; border: 1px solid var(--line); margin-bottom: .9rem; }
.rs-status.ok { color: #7BD88F; }
.rs-status.bad { color: var(--yellow); }

/* ---- App components ---- */
.rs-page-title { font-size: clamp(1.9rem, 3.4vw, 2.7rem); font-weight: 800; color: #fff; letter-spacing: -.03em; margin: .2rem 0 .3rem; line-height: 1.1; }
.rs-page-sub { color: var(--muted); font-size: .95rem; margin-bottom: 1.5rem; }
.rs-card { background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 14px 18px; margin-bottom: .7rem; }
.rs-card .rs-card-title { color: #fff; font-weight: 700; }
.rs-card .rs-card-meta { color: var(--muted); font-size: .85rem; margin-top: .15rem; }
.rs-card .rs-card-note { color: var(--text); font-size: .9rem; margin-top: .45rem; }
.rs-stat-card { background: var(--panel); border: 1px solid var(--line); border-top: 3px solid var(--yellow); border-radius: 16px; padding: 16px 18px; }
.rs-stat-card .k { color: var(--muted); font-size: .78rem; font-weight: 600; text-transform: uppercase; letter-spacing: .05em; }
.rs-stat-card .v { color: #fff; font-size: 1.8rem; font-weight: 800; letter-spacing: -.02em; margin-top: .25rem; }
.rs-stat-card .h { color: var(--muted); font-size: .78rem; margin-top: .1rem; }
.rs-callout { border-radius: 16px; padding: 1rem 1.2rem; margin: 1rem 0; border: 1px solid var(--line); font-weight: 600; }
.rs-callout.warn { background: rgba(255, 201, 60, .13); border-color: rgba(255, 201, 60, .5); color: var(--yellow); }
.rs-callout.info { background: var(--panel); color: var(--text); }
.rs-callout.ok { background: rgba(123, 216, 143, .1); border-color: rgba(123, 216, 143, .4); color: #7BD88F; }
.rs-ai { background: var(--panel); border: 1px solid var(--line); border-left: 4px solid var(--yellow); border-radius: 16px; padding: 1.2rem 1.4rem; margin: 1rem 0; }
.rs-ai h4 { margin: 0 0 .5rem; font-size: 1.05rem; }
.rs-ai ul { margin: .3rem 0 .8rem 1.1rem; padding: 0; }
.rs-ai .rs-ai-label { color: var(--yellow); font-size: .72rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; margin-bottom: .4rem; }
.rs-ai .rs-ai-caption { color: var(--muted); font-size: .82rem; }
@media (max-width: 900px) { .rs-links { display: none; } .rs-stats { gap: 1.6rem; } }
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# UI helpers
# ----------------------------------------------------------------------------
def esc(value) -> str:
    return html.escape("" if value is None else str(value))


def page_header(prefix: str, highlight: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="rs-page-title">{esc(prefix)} <mark>{esc(highlight)}</mark></div>'
        f'<div class="rs-page-sub">{esc(subtitle)}</div>',
        unsafe_allow_html=True,
    )


def callout(kind: str, text: str) -> None:
    st.markdown(f'<div class="rs-callout {esc(kind)}">{esc(text)}</div>', unsafe_allow_html=True)


def stat_card(label: str, value, hint: str = "") -> str:
    hint_html = f'<div class="h">{esc(hint)}</div>' if hint else ""
    return (
        f'<div class="rs-stat-card"><div class="k">{esc(label)}</div>'
        f'<div class="v">{esc(value)}</div>{hint_html}</div>'
    )


def record_card(title: str, meta: str = "", note: str = "") -> None:
    note_html = f'<div class="rs-card-note">{esc(note)}</div>' if note else ""
    st.markdown(
        f'<div class="rs-card"><div class="rs-card-title">{esc(title)}</div>'
        f'<div class="rs-card-meta">{esc(meta)}</div>{note_html}</div>',
        unsafe_allow_html=True,
    )


def fmt_number(value, *, decimals=0, signed=False, suffix="") -> str:
    if value is None:
        return "—"
    try:
        pattern = f"{{:{'+' if signed else ''},.{decimals}f}}"
        return pattern.format(float(value)) + suffix
    except (TypeError, ValueError):
        return "—"


# ----------------------------------------------------------------------------
# API helpers
# ----------------------------------------------------------------------------
def api_request(method, path, *, token=None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    timeout = kwargs.pop("timeout", TIMEOUT)
    return httpx.request(
        method, f"{API_URL}{path}", headers=headers, timeout=timeout, **kwargs
    )


def show_api_error(response):
    try:
        detail = response.json().get("detail", response.text)
    except (ValueError, AttributeError):
        detail = response.text
    st.error(f"Request failed ({response.status_code}): {detail}")


def api_get(path, token, *, params=None):
    try:
        response = api_request("GET", path, token=token, params=params)
        if response.is_success:
            return response.json()
        show_api_error(response)
    except httpx.HTTPError as exc:
        st.error(f"Could not reach RepSense API: {exc}")
    return None


try:
    health = httpx.get(f"{API_URL}/health", timeout=2.0)
    health.raise_for_status()
    api_available = True
except httpx.HTTPError:
    api_available = False

if "token" not in st.session_state:
    st.session_state.token = None
if "email" not in st.session_state:
    st.session_state.email = None

# ----------------------------------------------------------------------------
# Logged-out landing + auth
# ----------------------------------------------------------------------------
if not st.session_state.token:
    st.markdown(
        '<div class="rs-nav"><div class="rs-brand"><span class="rs-logo">R</span>RepSense</div>'
        '<div class="rs-links"><span>Overview</span><span>Workouts</span><span>Recovery</span><span>Insights</span></div>'
        '<div class="rs-nav-right"><span>Log in</span><span class="rs-pill">Get started</span></div></div>',
        unsafe_allow_html=True,
    )
    hero_col, auth_col = st.columns([1.2, 1], gap="large")

    with hero_col:
        st.markdown(
            '<div class="rs-badge"><b>NEW</b>Insights grounded in your logged data</div>'
            '<h1 class="rs-hero">Train with context, not <mark>guesswork</mark>.</h1>'
            '<p class="rs-sub">RepSense compares each week of training with your own history, '
            "flags unusual volume, and explains every finding using the evidence behind it.</p>"
            '<div class="rs-stats">'
            '<div class="rs-stat"><b>30%</b><span>volume-spike threshold</span></div>'
            '<div class="rs-stat"><b>4 weeks</b><span>prior-week baseline</span></div>'
            '<div class="rs-stat"><b>Rules first</b><span>AI only explains</span></div>'
            "</div>",
            unsafe_allow_html=True,
        )

    with auth_col:
        if api_available:
            st.markdown('<span class="rs-status ok">● API connected</span>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<span class="rs-status bad">● API unavailable — run docker compose up --build</span>',
                unsafe_allow_html=True,
            )
        login_tab, register_tab = st.tabs(["Log in", "Create account"])
        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)
            if submitted:
                try:
                    response = api_request(
                        "POST", "/api/v1/auth/login", json={"email": email, "password": password}
                    )
                    if response.is_success:
                        st.session_state.token = response.json()["access_token"]
                        st.session_state.email = email
                        st.rerun()
                    show_api_error(response)
                except httpx.HTTPError as exc:
                    st.error(f"Could not reach RepSense API: {exc}")
        with register_tab:
            with st.form("register_form"):
                new_email = st.text_input("Email", key="register_email")
                new_password = st.text_input(
                    "Password (at least 10 characters)", type="password", key="register_password"
                )
                create = st.form_submit_button("Create account", type="primary", use_container_width=True)
            if create:
                try:
                    response = api_request(
                        "POST", "/api/v1/auth/register",
                        json={"email": new_email, "password": new_password},
                    )
                    if response.is_success:
                        st.success("Account created. Log in to continue.")
                    else:
                        show_api_error(response)
                except httpx.HTTPError as exc:
                    st.error(f"Could not reach RepSense API: {exc}")
    st.stop()

# ----------------------------------------------------------------------------
# Logged-in app
# ----------------------------------------------------------------------------
token = st.session_state.token
PAGES = ["Overview", "Log workout", "Exercises", "Recovery", "Insights"]
PAGE_ICONS = {"Overview": "📊", "Log workout": "✍️", "Exercises": "🏋️", "Recovery": "🌙", "Insights": "💡"}

with st.sidebar:
    st.markdown('<div class="rs-brand" style="padding:.4rem 0 .2rem"><span class="rs-logo">R</span>RepSense</div>',
                unsafe_allow_html=True)
    st.caption(st.session_state.email or "Signed in")
    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
    page = st.radio(
        "Navigate", PAGES,
        format_func=lambda name: f"{PAGE_ICONS[name]}  {name}",
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Your training records stay in your RepSense account.")
    if st.button("Log out", use_container_width=True):
        st.session_state.token = None
        st.session_state.email = None
        st.rerun()

# Fetch shared data once per rerun so each screen uses consistent account records.
with st.spinner("Loading your training data…"):
    workouts = api_get("/api/v1/workouts", token, params={"limit": 100})
    recovery_entries = api_get("/api/v1/recovery", token, params={"limit": 100})
    exercises = api_get("/api/v1/exercises", token)

workouts = workouts or []
recovery_entries = recovery_entries or []
exercises = exercises or []

if page == "Overview":
    page_header("Your training", "overview",
                "A quick view of your recent logged activity. Metrics reflect records returned by the API.")
    metric_cols = st.columns(4)
    cards = [
        ("Workouts loaded", len(workouts), "most recent 100"),
        ("Sets logged", sum(len(item.get("sets", [])) for item in workouts), "across loaded workouts"),
        ("Recovery logs", len(recovery_entries), "most recent 100"),
        ("Exercises", len(exercises), "in your library"),
    ]
    for col, (label, value, hint) in zip(metric_cols, cards):
        col.markdown(stat_card(label, value, hint), unsafe_allow_html=True)
    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    left, right = st.columns([1.4, 1], gap="large")
    with left:
        st.markdown("#### Recent sessions")
        if workouts:
            for item in workouts[:8]:
                record_card(
                    str(item.get("performed_at", "Date unavailable")),
                    f"{len(item.get('sets', []))} sets logged",
                    item.get("notes") or "",
                )
        else:
            st.info("No workouts yet. Log your first session to start building your history.")
    with right:
        st.markdown("#### Recent recovery")
        if recovery_entries:
            for item in recovery_entries[:6]:
                details = []
                if item.get("sleep_hours") is not None:
                    details.append(f"Sleep {item['sleep_hours']} h")
                if item.get("energy_score") is not None:
                    details.append(f"Energy {item['energy_score']}/10")
                if item.get("soreness_score") is not None:
                    details.append(f"Soreness {item['soreness_score']}/10")
                record_card(
                    str(item.get("recorded_at", "Date unavailable")),
                    " · ".join(details) if details else "Recovery entry saved",
                )
        else:
            st.info("No recovery logs yet.")

elif page == "Exercises":
    page_header("Exercise", "library", "Your system and custom exercises, with estimated progress over time.")
    with st.expander("Add an exercise", expanded=not bool(exercises)):
        with st.form("create_exercise_form"):
            exercise_name = st.text_input("Exercise name", max_chars=120)
            col1, col2 = st.columns(2)
            muscle_group = col1.text_input("Muscle group (optional)", max_chars=80)
            equipment = col2.text_input("Equipment (optional)", max_chars=80)
            add_exercise = st.form_submit_button("Add exercise", type="primary")
        if add_exercise:
            try:
                response = api_request("POST", "/api/v1/exercises", token=token, json={
                    "name": exercise_name, "muscle_group": muscle_group or None,
                    "equipment": equipment or None,
                })
                if response.is_success:
                    st.success("Exercise added. Refresh the page to load it into the library.")
                else:
                    show_api_error(response)
            except httpx.HTTPError as exc:
                st.error(f"Could not create exercise: {exc}")
    if exercises:
        st.dataframe([{
            "Exercise": e["name"], "Muscle group": e.get("muscle_group") or "—",
            "Equipment": e.get("equipment") or "—", "Source": "System" if e["is_system"] else "Custom",
        } for e in exercises], use_container_width=True, hide_index=True)
        st.markdown("#### Exercise progress")
        selected = st.selectbox("View exercise progress", options=exercises,
                                format_func=lambda e: e["name"], key="progress_exercise")
        if st.button("Load progress", type="primary"):
            progress = api_get(f"/api/v1/analytics/exercises/{selected['id']}", token)
            if progress is not None:
                st.markdown(
                    stat_card("Eligible loaded volume",
                              f"{progress['eligible_loaded_volume_kg_reps']:,.0f} kg × reps"),
                    unsafe_allow_html=True,
                )
                points = progress.get("points", [])
                if points:
                    frame = pd.DataFrame(points)
                    chart_frame = frame.dropna(subset=["estimated_1rm_kg"])
                    if not chart_frame.empty:
                        st.line_chart(chart_frame, x="performed_at", y="estimated_1rm_kg",
                                      color="#FFC93C", use_container_width=True)
                    st.dataframe(frame, use_container_width=True, hide_index=True)
                else:
                    st.info("No sets recorded for this exercise yet.")
                st.caption(progress.get("note", "Performance estimates are proxies, not direct measurements of strength."))
    else:
        st.info("Add an exercise before logging workouts.")

elif page == "Log workout":
    page_header("Log a", "workout", "Record sets for one exercise. RPE is optional.")
    if not exercises:
        st.info("Create an exercise in the Exercises section first.")
    else:
        with st.form("workout_form"):
            performed_at = st.date_input("Workout date", value=date.today(), max_value=date.today())
            exercise = st.selectbox("Exercise", options=exercises, format_func=lambda e: e["name"])
            number_sets = st.number_input("Number of sets", min_value=1, max_value=20, value=3)
            sets = []
            for i in range(int(number_sets)):
                st.markdown(f"**Set {i + 1}**")
                cols = st.columns(3)
                weight = cols[0].number_input("Weight (kg)", min_value=0.0, max_value=1000.0,
                                              value=40.0, step=2.5, key=f"weight_{i}")
                reps = cols[1].number_input("Reps", min_value=1, max_value=1000, value=8, key=f"reps_{i}")
                rpe = cols[2].number_input("RPE (0 = omit)", min_value=0.0, max_value=10.0,
                                           value=0.0, step=0.5, key=f"rpe_{i}")
                sets.append({"exercise_id": exercise["id"], "set_number": i + 1,
                             "weight": weight, "reps": int(reps), "rpe": rpe if rpe > 0 else None})
            notes = st.text_area("Session notes (optional)", max_chars=1000)
            submit_workout = st.form_submit_button("Save workout", type="primary", use_container_width=True)
        if submit_workout:
            try:
                response = api_request("POST", "/api/v1/workouts", token=token, json={
                    "performed_at": performed_at.isoformat(), "notes": notes or None, "sets": sets
                })
                if response.is_success:
                    st.success(f"Workout saved with {len(response.json()['sets'])} sets.")
                else:
                    show_api_error(response)
            except httpx.HTTPError as exc:
                st.error(f"Could not save workout: {exc}")

elif page == "Recovery":
    page_header("Recovery", "log", "Sleep, energy, soreness and resting heart rate. Leave a field at 0 to omit it.")
    with st.form("recovery_form"):
        recorded_at = st.date_input("Date", value=date.today(), max_value=date.today(), key="recovery_date")
        col1, col2 = st.columns(2)
        sleep = col1.number_input("Sleep (hours; 0 = omit)", min_value=0.0, max_value=24.0, value=0.0, step=0.5)
        energy = col2.number_input("Energy (1–10; 0 = omit)", min_value=0, max_value=10, value=0)
        col3, col4 = st.columns(2)
        soreness = col3.number_input("Soreness (1–10; 0 = omit)", min_value=0, max_value=10, value=0)
        rhr = col4.number_input("Resting heart rate (bpm; 0 = omit)", min_value=0, max_value=299, value=0)
        recovery_notes = st.text_area("Notes (optional)", max_chars=1000)
        save_recovery = st.form_submit_button("Save recovery log", type="primary", use_container_width=True)
    if save_recovery:
        try:
            response = api_request("POST", "/api/v1/recovery", token=token, json={
                "recorded_at": recorded_at.isoformat(), "sleep_hours": sleep if sleep > 0 else None,
                "energy_score": energy if energy > 0 else None,
                "soreness_score": soreness if soreness > 0 else None,
                "resting_heart_rate": rhr if rhr > 0 else None,
                "notes": recovery_notes or None,
            })
            if response.is_success:
                st.success("Recovery entry saved.")
            else:
                show_api_error(response)
        except httpx.HTTPError as exc:
            st.error(f"Could not save recovery log: {exc}")
    st.markdown("#### Recent recovery entries")
    if recovery_entries:
        st.dataframe([{
            "Date": row.get("recorded_at"), "Sleep (h)": row.get("sleep_hours"),
            "Energy": row.get("energy_score"), "Soreness": row.get("soreness_score"),
            "Resting HR": row.get("resting_heart_rate"),
        } for row in recovery_entries], use_container_width=True, hide_index=True)
    else:
        st.info("Your saved recovery entries will appear here.")

elif page == "Insights":
    page_header("Evidence-backed", "insights",
                "Rules are evaluated from eligible logged data. AI explanations are optional and may be unavailable.")
    if exercises:
        selected = st.selectbox("Exercise to analyze", options=exercises,
                                format_func=lambda e: e["name"], key="insight_exercise")
        if st.button("Analyze volume", type="primary"):
            try:
                with st.spinner("Analyzing... the AI explanation can take a minute or two."):
                    response = api_request("POST", "/api/v1/insights/analyze", token=token,
                                           params={"exercise_id": selected["id"]}, timeout=200.0)
                if response.is_success:
                    result = response.json()
                    evidence = result["evidence"]
                    if evidence["triggered"]:
                        callout("warn", "A possible volume spike was detected by this rule.")
                    elif not evidence["sufficient_data"]:
                        found = evidence.get("prior_weeks_found", 0)
                        needed = evidence.get("prior_weeks_required", 4)
                        problems = []
                        if not evidence.get("has_current_week_data", True):
                            problems.append("no loaded sets logged for this exercise in the current week")
                        if found < needed:
                            problems.append(f"{found} of {needed} prior weeks with logged data")
                        callout(
                            "info",
                            "Not enough eligible history to evaluate this rule yet: "
                            + "; ".join(problems or ["a positive baseline is required"])
                            + ". Log this exercise across more weeks (or run the demo seed script).",
                        )
                    else:
                        callout("ok", "No volume spike was detected by this rule.")

                    if evidence.get("sufficient_data"):
                        stat_cols = st.columns(4)
                        stats = [
                            ("This week", fmt_number(evidence.get("current_value")), "kg × reps"),
                            ("Baseline", fmt_number(evidence.get("baseline_value")), "prior-week average"),
                            ("Change", fmt_number(evidence.get("percentage_change"), decimals=1,
                                                  signed=True, suffix="%"), "vs baseline"),
                            ("Threshold", fmt_number(evidence.get("threshold"), suffix="%"), "strictly greater"),
                        ]
                        for col, (label, value, hint) in zip(stat_cols, stats):
                            col.markdown(stat_card(label, value, hint), unsafe_allow_html=True)
                        st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)

                    with st.expander("View deterministic evidence", expanded=False):
                        st.json(evidence)

                    explanation = result.get("explanation")
                    if explanation:
                        points = "".join(f"<li>{esc(p)}</li>" for p in explanation.get("evidence_points", []))
                        checks = "".join(f"<li>{esc(c)}</li>" for c in explanation.get("next_checks", []))
                        checks_html = (
                            f'<div class="rs-ai-label">Suggested next checks</div><ul>{checks}</ul>' if checks else ""
                        )
                        st.markdown(
                            '<div class="rs-ai"><div class="rs-ai-label">AI explanation</div>'
                            f'<h4>{esc(explanation.get("title", ""))}</h4>'
                            f'<p>{esc(explanation.get("summary", ""))}</p>'
                            f"<ul>{points}</ul>{checks_html}"
                            f'<div class="rs-ai-caption">{esc(explanation.get("uncertainty", ""))}</div></div>',
                            unsafe_allow_html=True,
                        )
                    elif evidence["triggered"]:
                        reasons = {
                            "ai_not_configured": "AI explanation is off: GEMINI_API_KEY is not set in .env.",
                            "ai_rejected": "Gemini answered, but the text was rejected because it contained numbers not in the evidence. Try Analyze again.",
                            "ai_error": "Gemini could not be reached or the model call failed. Check the API terminal for the exact error.",
                        }
                        st.caption(reasons.get(result.get("status"), "AI explanation unavailable.")
                                   + " Deterministic evidence is preserved.")
                else:
                    show_api_error(response)
            except httpx.HTTPError as exc:
                st.error(f"Could not analyze this exercise: {exc}")
    else:
        st.info("Add an exercise before analyzing training data.")
    st.markdown("#### Previous analyses")
    records = api_get("/api/v1/insights", token)
    if records:
        for record in records:
            with st.expander(f"{record['insight_type']} · {record['created_at']}"):
                st.json(record["evidence"])
                if record.get("explanation"):
                    st.write(record["explanation"].get("summary", ""))
    elif records == []:
        st.info("No saved analyses yet.")