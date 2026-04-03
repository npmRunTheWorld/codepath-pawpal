import streamlit as st
from pawpal_system import Task, Owner, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ---------------------------------------------------------------------------
# Custom CSS — styling only, no user data embedded here
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background: #0f0f13; color: #e8e8f0; }

[data-testid="stSidebar"] {
    background: #16161e !important;
    border-right: 1px solid #2a2a38;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stTextArea label {
    color: #a0a0b8 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}

input, textarea, [data-baseweb="select"] {
    background: #1e1e2a !important;
    border: 1px solid #2e2e3e !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
}
input:focus, textarea:focus {
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 2px rgba(124,106,247,0.2) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c6af7 0%, #a855f7 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 15px rgba(124,106,247,0.35) !important;
    transition: opacity 0.2s, transform 0.1s !important;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:not([kind="primary"]) {
    background: #1e1e2a !important;
    color: #a0a0b8 !important;
    border: 1px solid #2e2e3e !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
}
.stButton > button:not([kind="primary"]):hover {
    border-color: #ef4444 !important;
    color: #ef4444 !important;
    background: rgba(239,68,68,0.08) !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #16161e !important;
    border: 1px solid #2a2a38 !important;
    border-radius: 14px !important;
}
[data-testid="stForm"] {
    background: #16161e !important;
    border: 1px solid #2a2a38 !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
}

div[data-testid="stSuccessMessage"] {
    background: rgba(16,185,129,0.12) !important;
    border: 1px solid rgba(16,185,129,0.3) !important;
    border-radius: 12px !important;
    color: #6ee7b7 !important;
}
div[data-testid="stWarningMessage"] {
    background: rgba(245,158,11,0.12) !important;
    border: 1px solid rgba(245,158,11,0.3) !important;
    border-radius: 12px !important;
    color: #fcd34d !important;
}
div[data-testid="stInfoMessage"] {
    background: rgba(124,106,247,0.1) !important;
    border: 1px solid rgba(124,106,247,0.25) !important;
    border-radius: 12px !important;
    color: #c4b5fd !important;
}

hr { border-color: #2a2a38 !important; }
[data-testid="stCheckbox"] label { color: #a0a0b8 !important; font-size: 0.88rem !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0f0f13; }
::-webkit-scrollbar-thumb { background: #2e2e3e; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CATEGORY_ICONS = {
    "walk": "🦮", "feed": "🍖", "meds": "💊",
    "enrichment": "🧸", "grooming": "✂️", "other": "📋"
}
PRIORITY_COLORS = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}

# ---------------------------------------------------------------------------
# Hero header (static — safe to use HTML)
# ---------------------------------------------------------------------------
col_logo, col_title = st.columns([1, 11])
with col_logo:
    st.markdown("<div style='font-size:2.8rem;margin-top:6px'>🐾</div>", unsafe_allow_html=True)
with col_title:
    st.markdown("""
        <div style='margin-top:4px'>
            <span style='font-size:2rem;font-weight:700;color:#e8e8f0;letter-spacing:-0.5px'>PawPal</span>
            <span style='font-size:2rem;font-weight:700;background:linear-gradient(135deg,#7c6af7,#a855f7);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent'>+</span>
            <div style='font-size:0.85rem;color:#6b6b88;margin-top:-4px'>Daily pet care planner</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:1px;background:#2a2a38;margin:1rem 0 1.5rem'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "plan" not in st.session_state:
    st.session_state.plan = None

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<div style='font-size:0.7rem;font-weight:700;color:#7c6af7;letter-spacing:0.12em;text-transform:uppercase;padding:0.5rem 0 1rem'>Owner Profile</div>", unsafe_allow_html=True)
    owner_name = st.text_input("Name", value="Jordan")
    available_minutes = st.number_input("Time available (min)", min_value=5, max_value=480, value=90, step=5)
    start_time = st.time_input("Start time", value=None)
    start_str = start_time.strftime("%H:%M") if start_time else "08:00"

    st.markdown("<div style='height:1px;background:#2a2a38;margin:1.2rem 0'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.7rem;font-weight:700;color:#7c6af7;letter-spacing:0.12em;text-transform:uppercase;padding:0.2rem 0 1rem'>Pet Profile</div>", unsafe_allow_html=True)

    pet_name = st.text_input("Pet's name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
    pet_notes = st.text_area("Special needs / notes", placeholder="e.g. takes medication twice a day")

    avatar = {"dog": "🐶", "cat": "🐱", "other": "🐾"}.get(species, "🐾")
    with st.container(border=True):
        st.markdown(f"<div style='text-align:center;padding:0.4rem 0'><div style='font-size:2.2rem'>{avatar}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;font-size:1rem;font-weight:600;color:#e8e8f0'>{pet_name or '—'}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;font-size:0.78rem;color:#6b6b88'>{species} · {pet_age} yr</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Two-column layout
# ---------------------------------------------------------------------------
left, right = st.columns([5, 6], gap="large")

# ── LEFT: Task input ────────────────────────────────────────────────────────
with left:
    st.markdown("<div style='font-size:0.7rem;font-weight:700;color:#7c6af7;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.8rem'>Add a Task</div>", unsafe_allow_html=True)

    with st.form("add_task_form", clear_on_submit=True):
        task_title = st.text_input("Task title", placeholder="e.g. Morning walk")
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("Category", list(CATEGORY_ICONS.keys()))
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col2:
            priority = st.selectbox("Priority", ["high", "medium", "low"])
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        is_mandatory = st.checkbox("Mandatory (e.g. medication — always scheduled)")
        submitted = st.form_submit_button("＋ Add Task", use_container_width=True, type="primary")

        if submitted:
            if task_title.strip():
                st.session_state.tasks.append(
                    Task(task_title.strip(), int(duration), priority, category, is_mandatory, frequency)
                )
                st.session_state.plan = None
            else:
                st.warning("Task title cannot be empty.")

    # Task queue — native Streamlit components to avoid HTML rendering issues
    if st.session_state.tasks:
        n = len(st.session_state.tasks)
        st.markdown(f"<div style='font-size:0.7rem;font-weight:700;color:#7c6af7;letter-spacing:0.12em;text-transform:uppercase;margin:1.2rem 0 0.6rem'>Queue · {n} task{'s' if n != 1 else ''}</div>", unsafe_allow_html=True)

        for i, task in enumerate(st.session_state.tasks):
            icon = CATEGORY_ICONS.get(task.category, "📋")
            dot_color = "#ef4444" if task.is_mandatory else PRIORITY_COLORS.get(task.priority, "#6b6b88")
            tags = []
            if task.is_mandatory:
                tags.append("required")
            if task.frequency != "once":
                tags.append(task.frequency)

            with st.container(border=True):
                c1, c2 = st.columns([8, 1])
                with c1:
                    tag_str = "  `" + "`  `".join(tags) + "`" if tags else ""
                    st.markdown(f"{icon} **{task.title}**{tag_str}")
                    st.caption(f"{task.duration_minutes} min · {task.priority} · {task.category}")
                with c2:
                    if st.button("✕", key=f"remove_{i}"):
                        st.session_state.tasks.pop(i)
                        st.session_state.plan = None
                        st.rerun()
    else:
        st.info("No tasks yet. Add one above.")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if st.button("Generate Schedule →", type="primary", use_container_width=True):
        if not st.session_state.tasks:
            st.warning("Add at least one task first.")
        else:
            owner = Owner(owner_name, int(available_minutes), start_str)
            pet = Pet(pet_name, species, int(pet_age), pet_notes)
            st.session_state.plan = Scheduler().schedule(owner, pet, st.session_state.tasks)

# ── RIGHT: Plan ─────────────────────────────────────────────────────────────
with right:
    plan = st.session_state.plan
    scheduler = Scheduler()

    if not plan:
        with st.container(border=True):
            st.markdown("""
                <div style='text-align:center;padding:3rem 1rem'>
                    <div style='font-size:3rem'>📅</div>
                    <div style='font-size:1rem;font-weight:600;color:#e8e8f0;margin-top:0.8rem'>No plan yet</div>
                    <div style='font-size:0.82rem;color:#6b6b88;margin-top:0.3rem'>Add tasks and hit Generate Schedule</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        # Plan summary header — static values only, safe for HTML
        total = plan.total_minutes()
        pct = min(100, int(total / plan.owner.available_minutes * 100))
        bar_color = "#22c55e" if pct <= 80 else "#f59e0b" if pct <= 100 else "#ef4444"
        n_sched = len(plan.scheduled)

        with st.container(border=True):
            st.markdown(
                "<div style='font-size:0.7rem;font-weight:700;color:#7c6af7;"
                "letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.4rem'>"
                "Today's Plan</div>",
                unsafe_allow_html=True,
            )
            col_a, col_b = st.columns([3, 2])
            with col_a:
                st.markdown(f"**{n_sched} task{'s' if n_sched != 1 else ''} scheduled**")
            with col_b:
                st.markdown(
                    f"<div style='text-align:right;font-size:0.82rem;color:#6b6b88'>"
                    f"{total} / {plan.owner.available_minutes} min</div>",
                    unsafe_allow_html=True,
                )
            st.markdown(
                f"<div style='background:#2a2a38;border-radius:99px;height:6px;margin-top:0.3rem'>"
                f"<div style='background:{bar_color};width:{pct}%;height:100%;border-radius:99px'></div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        # Conflicts
        for warning in scheduler.detect_conflicts(plan.scheduled):
            st.warning(f"⚠️ {warning}")

        # Scheduled tasks — native components, no user data in HTML
        if plan.scheduled:
            st.markdown(
                "<div style='font-size:0.7rem;font-weight:700;color:#7c6af7;"
                "letter-spacing:0.12em;text-transform:uppercase;margin:1rem 0 0.5rem'>"
                "Scheduled</div>",
                unsafe_allow_html=True,
            )
            for st_task in scheduler.sort_by_time(plan.scheduled):
                icon = CATEGORY_ICONS.get(st_task.task.category, "📋")
                freq = st_task.task.frequency
                tags = []
                if st_task.task.is_mandatory:
                    tags.append("required")
                if freq != "once":
                    tags.append(freq)

                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        tag_str = "  `" + "`  `".join(tags) + "`" if tags else ""
                        st.markdown(f"{icon} **{st_task.task.title}**{tag_str}")
                        st.caption(st_task.reason)
                    with c2:
                        st.markdown(
                            f"<div style='text-align:right;font-size:0.88rem;"
                            f"font-weight:600;color:#c4b5fd'>"
                            f"{st_task.start_time} – {st_task.end_time}</div>",
                            unsafe_allow_html=True,
                        )
                        st.caption(f"{st_task.task.duration_minutes} min")

        # Skipped tasks
        if plan.skipped:
            st.markdown(
                f"<div style='font-size:0.7rem;font-weight:700;color:#6b6b88;"
                f"letter-spacing:0.12em;text-transform:uppercase;margin:1.2rem 0 0.5rem'>"
                f"Skipped · {len(plan.skipped)}</div>",
                unsafe_allow_html=True,
            )
            for task in plan.skipped:
                icon = CATEGORY_ICONS.get(task.category, "📋")
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"~~{icon} {task.title}~~")
                    with c2:
                        st.caption(f"{task.duration_minutes} min · {task.priority}")
