import streamlit as st
from pawpal_system import Task, Owner, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Page background */
.stApp {
    background: #0f0f13;
    color: #e8e8f0;
}

/* Sidebar */
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

/* Inputs */
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

/* Primary button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c6af7 0%, #a855f7 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: opacity 0.2s, transform 0.1s !important;
    box-shadow: 0 4px 15px rgba(124,106,247,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

/* Secondary buttons */
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

/* Containers / cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #16161e !important;
    border: 1px solid #2a2a38 !important;
    border-radius: 14px !important;
}

/* Form */
[data-testid="stForm"] {
    background: #16161e !important;
    border: 1px solid #2a2a38 !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
}

/* Success / warning / info */
[data-testid="stAlert"][data-baseweb="notification"] {
    border-radius: 12px !important;
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

/* Divider */
hr {
    border-color: #2a2a38 !important;
}

/* Checkbox */
[data-testid="stCheckbox"] label {
    color: #a0a0b8 !important;
    font-size: 0.88rem !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0f0f13; }
::-webkit-scrollbar-thumb { background: #2e2e3e; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Hero header
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
    st.markdown("""
        <div style='padding:0.5rem 0 1rem'>
            <div style='font-size:0.7rem;font-weight:700;color:#7c6af7;letter-spacing:0.12em;text-transform:uppercase'>
                Owner Profile
            </div>
        </div>
    """, unsafe_allow_html=True)

    owner_name = st.text_input("Name", value="Jordan")
    available_minutes = st.number_input("Time available (min)", min_value=5, max_value=480, value=90, step=5)
    start_time = st.time_input("Start time", value=None)
    start_str = start_time.strftime("%H:%M") if start_time else "08:00"

    st.markdown("<div style='height:1px;background:#2a2a38;margin:1.2rem 0'></div>", unsafe_allow_html=True)

    st.markdown("""
        <div style='padding:0.2rem 0 1rem'>
            <div style='font-size:0.7rem;font-weight:700;color:#7c6af7;letter-spacing:0.12em;text-transform:uppercase'>
                Pet Profile
            </div>
        </div>
    """, unsafe_allow_html=True)

    pet_name = st.text_input("Pet's name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
    pet_notes = st.text_area("Special needs / notes", placeholder="e.g. takes medication twice a day")

    # Pet avatar
    avatar = {"dog": "🐶", "cat": "🐱", "other": "🐾"}.get(species, "🐾")
    st.markdown(f"""
        <div style='margin-top:1.2rem;padding:1rem;background:#1e1e2a;border-radius:12px;
             border:1px solid #2e2e3e;text-align:center'>
            <div style='font-size:2.2rem'>{avatar}</div>
            <div style='font-size:1rem;font-weight:600;color:#e8e8f0;margin-top:4px'>{pet_name or "—"}</div>
            <div style='font-size:0.78rem;color:#6b6b88'>{species} · {pet_age} yr</div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Layout: left = task input, right = plan
# ---------------------------------------------------------------------------
left, right = st.columns([5, 6], gap="large")

# ── LEFT: Task input ────────────────────────────────────────────────────────
with left:
    st.markdown("""
        <div style='font-size:0.7rem;font-weight:700;color:#7c6af7;
             letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.8rem'>
            Add a Task
        </div>
    """, unsafe_allow_html=True)

    CATEGORY_ICONS = {
        "walk": "🦮", "feed": "🍖", "meds": "💊",
        "enrichment": "🧸", "grooming": "✂️", "other": "📋"
    }
    PRIORITY_COLORS = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}

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

    # Task list
    if st.session_state.tasks:
        st.markdown(f"""
            <div style='font-size:0.7rem;font-weight:700;color:#7c6af7;
                 letter-spacing:0.12em;text-transform:uppercase;margin:1.2rem 0 0.6rem'>
                Queue · {len(st.session_state.tasks)} task{'s' if len(st.session_state.tasks) != 1 else ''}
            </div>
        """, unsafe_allow_html=True)

        for i, task in enumerate(st.session_state.tasks):
            icon = CATEGORY_ICONS.get(task.category, "📋")
            dot_color = "#ef4444" if task.is_mandatory else PRIORITY_COLORS.get(task.priority, "#6b6b88")
            freq_badge = (
                f"<span style='background:#1e1e2a;border:1px solid #2e2e3e;border-radius:5px;"
                f"padding:1px 6px;font-size:0.7rem;color:#a0a0b8;margin-left:4px'>{task.frequency}</span>"
                if task.frequency != "once" else ""
            )
            mandatory_badge = (
                "<span style='background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);"
                "border-radius:5px;padding:1px 6px;font-size:0.7rem;color:#f87171;margin-left:4px'>required</span>"
                if task.is_mandatory else ""
            )

            col_info, col_btn = st.columns([8, 1])
            with col_info:
                st.markdown(f"""
                    <div style='display:flex;align-items:center;padding:0.55rem 0.7rem;
                         background:#16161e;border:1px solid #2a2a38;border-radius:11px;
                         margin-bottom:5px'>
                        <span style='font-size:1.1rem;margin-right:10px'>{icon}</span>
                        <div style='flex:1;min-width:0'>
                            <div style='display:flex;align-items:center;flex-wrap:wrap;gap:2px'>
                                <span style='font-weight:600;font-size:0.88rem;color:#e8e8f0'>{task.title}</span>
                                {mandatory_badge}{freq_badge}
                            </div>
                            <div style='font-size:0.75rem;color:#6b6b88;margin-top:1px'>
                                {task.duration_minutes} min ·
                                <span style='color:{dot_color}'>{task.priority}</span> ·
                                {task.category}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col_btn:
                if st.button("✕", key=f"remove_{i}"):
                    st.session_state.tasks.pop(i)
                    st.session_state.plan = None
                    st.rerun()

    else:
        st.markdown("""
            <div style='text-align:center;padding:2rem 1rem;background:#16161e;
                 border:1px dashed #2a2a38;border-radius:14px;color:#6b6b88;font-size:0.88rem'>
                No tasks yet. Add one above.
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
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
        st.markdown("""
            <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;
                 height:420px;background:#16161e;border:1px dashed #2a2a38;border-radius:16px'>
                <div style='font-size:3rem'>📅</div>
                <div style='font-size:1rem;font-weight:600;color:#e8e8f0;margin-top:0.8rem'>No plan yet</div>
                <div style='font-size:0.82rem;color:#6b6b88;margin-top:0.3rem'>
                    Add tasks and hit Generate Schedule
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Header
        total = plan.total_minutes()
        pct = min(100, int(total / plan.owner.available_minutes * 100))
        bar_color = "#22c55e" if pct <= 80 else "#f59e0b" if pct <= 100 else "#ef4444"

        st.markdown(f"""
            <div style='background:#16161e;border:1px solid #2a2a38;border-radius:16px;padding:1.2rem 1.4rem;margin-bottom:1rem'>
                <div style='font-size:0.7rem;font-weight:700;color:#7c6af7;
                     letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.6rem'>
                    Today's Plan
                </div>
                <div style='display:flex;justify-content:space-between;align-items:baseline'>
                    <div style='font-size:1.3rem;font-weight:700;color:#e8e8f0'>
                        {len(plan.scheduled)} task{'s' if len(plan.scheduled) != 1 else ''} scheduled
                    </div>
                    <div style='font-size:0.82rem;color:#6b6b88'>
                        {total} / {plan.owner.available_minutes} min used
                    </div>
                </div>
                <div style='background:#2a2a38;border-radius:99px;height:6px;margin-top:0.7rem'>
                    <div style='background:{bar_color};width:{pct}%;height:100%;border-radius:99px;
                         transition:width 0.4s ease'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Conflicts
        conflicts = scheduler.detect_conflicts(plan.scheduled)
        for warning in conflicts:
            st.warning(f"⚠️ {warning}")

        # Scheduled tasks
        if plan.scheduled:
            sorted_tasks = scheduler.sort_by_time(plan.scheduled)
            for st_task in sorted_tasks:
                icon = CATEGORY_ICONS.get(st_task.task.category, "📋")
                is_mand = st_task.task.is_mandatory
                border_color = "#7c6af7" if is_mand else "#2a2a38"
                left_bar = "#7c6af7" if is_mand else "#2e2e3e"
                freq = st_task.task.frequency

                freq_tag = (
                    f"<span style='background:#1e1e2a;border:1px solid #2e2e3e;border-radius:5px;"
                    f"padding:1px 6px;font-size:0.7rem;color:#a0a0b8;margin-left:6px'>{freq}</span>"
                    if freq != "once" else ""
                )

                st.markdown(f"""
                    <div style='display:flex;gap:12px;padding:0.8rem 1rem;background:#16161e;
                         border:1px solid {border_color};border-radius:13px;margin-bottom:7px;
                         border-left:3px solid {left_bar}'>
                        <div style='font-size:1.4rem;padding-top:2px'>{icon}</div>
                        <div style='flex:1'>
                            <div style='display:flex;align-items:center'>
                                <span style='font-weight:600;font-size:0.92rem;color:#e8e8f0'>
                                    {st_task.task.title}
                                </span>
                                {freq_tag}
                            </div>
                            <div style='font-size:0.75rem;color:#6b6b88;margin-top:2px'>
                                {st_task.reason}
                            </div>
                        </div>
                        <div style='text-align:right;white-space:nowrap'>
                            <div style='font-size:0.88rem;font-weight:600;color:#c4b5fd'>
                                {st_task.start_time} – {st_task.end_time}
                            </div>
                            <div style='font-size:0.72rem;color:#6b6b88;margin-top:1px'>
                                {st_task.task.duration_minutes} min
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Skipped
        if plan.skipped:
            st.markdown(f"""
                <div style='font-size:0.7rem;font-weight:700;color:#6b6b88;
                     letter-spacing:0.12em;text-transform:uppercase;margin:1.2rem 0 0.5rem'>
                    Skipped · {len(plan.skipped)}
                </div>
            """, unsafe_allow_html=True)
            for task in plan.skipped:
                icon = CATEGORY_ICONS.get(task.category, "📋")
                st.markdown(f"""
                    <div style='display:flex;align-items:center;gap:10px;padding:0.55rem 0.9rem;
                         background:#16161e;border:1px solid #2a2a38;border-radius:11px;
                         margin-bottom:5px;opacity:0.55'>
                        <span style='font-size:1rem'>{icon}</span>
                        <span style='font-size:0.85rem;color:#a0a0b8;text-decoration:line-through'>
                            {task.title}
                        </span>
                        <span style='margin-left:auto;font-size:0.75rem;color:#6b6b88'>
                            {task.duration_minutes} min · {task.priority}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
