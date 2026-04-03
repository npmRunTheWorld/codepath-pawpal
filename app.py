import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from pawpal_system import Task, Owner, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ---------------------------------------------------------------------------
# Custom CSS — static only, no user data
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
[data-testid="stSidebar"] label {
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
.stButton > button[kind="primary"]:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }
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
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #16161e !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: #6b6b88 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: #7c6af7 !important;
    color: white !important;
}

div[data-testid="stSuccessMessage"] {
    background: rgba(16,185,129,0.12) !important;
    border: 1px solid rgba(16,185,129,0.3) !important;
    border-radius: 12px !important; color: #6ee7b7 !important;
}
div[data-testid="stWarningMessage"] {
    background: rgba(245,158,11,0.12) !important;
    border: 1px solid rgba(245,158,11,0.3) !important;
    border-radius: 12px !important; color: #fcd34d !important;
}
div[data-testid="stInfoMessage"] {
    background: rgba(124,106,247,0.1) !important;
    border: 1px solid rgba(124,106,247,0.25) !important;
    border-radius: 12px !important; color: #c4b5fd !important;
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
    "enrichment": "🧸", "grooming": "✂️", "other": "📋",
}
CATEGORY_COLORS = {
    "walk": "#7c6af7", "feed": "#22c55e", "meds": "#ef4444",
    "enrichment": "#f59e0b", "grooming": "#06b6d4", "other": "#a0a0b8",
}
PRIORITY_COLORS = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def hhmm_to_dt(hhmm: str) -> datetime:
    today = date.today()
    h, m = map(int, hhmm.split(":"))
    return datetime(today.year, today.month, today.day, h, m)


def build_gantt(plan) -> go.Figure:
    """Build a Plotly Gantt-style day-view chart from a DailyPlan."""
    fig = go.Figure()
    today = date.today()

    # Determine x-axis range: start of schedule → end of last task (min 2 hrs shown)
    sched_start = hhmm_to_dt(plan.owner.start_time)
    if plan.scheduled:
        last_end = hhmm_to_dt(plan.scheduled[-1].end_time)
        x_end = max(last_end, sched_start + timedelta(hours=2))
    else:
        x_end = sched_start + timedelta(hours=2)

    # Background "free time" bar
    fig.add_shape(
        type="rect",
        x0=sched_start, x1=x_end,
        y0=-0.4, y1=0.4,
        fillcolor="#1e1e2a", line_color="#2a2a38", line_width=1,
        layer="below",
    )

    for i, st_task in enumerate(plan.scheduled):
        t_start = hhmm_to_dt(st_task.start_time)
        t_end = hhmm_to_dt(st_task.end_time)
        color = CATEGORY_COLORS.get(st_task.task.category, "#a0a0b8")
        icon = CATEGORY_ICONS.get(st_task.task.category, "📋")

        # Task bar
        fig.add_shape(
            type="rect",
            x0=t_start, x1=t_end,
            y0=-0.38, y1=0.38,
            fillcolor=color + "33",  # 20% opacity fill
            line_color=color,
            line_width=2,
        )

        # Label inside bar (invisible scatter point for hover)
        mid = t_start + (t_end - t_start) / 2
        fig.add_trace(go.Scatter(
            x=[mid], y=[0],
            mode="text",
            text=[f"{icon} {st_task.task.title}"],
            textfont=dict(color="#e8e8f0", size=12, family="DM Sans"),
            hovertemplate=(
                f"<b>{st_task.task.title}</b><br>"
                f"{st_task.start_time} – {st_task.end_time}<br>"
                f"{st_task.task.duration_minutes} min · {st_task.task.priority} priority"
                "<extra></extra>"
            ),
            showlegend=False,
        ))

    # Hour tick lines
    current = sched_start.replace(minute=0, second=0)
    while current <= x_end:
        fig.add_shape(
            type="line",
            x0=current, x1=current, y0=-0.5, y1=0.5,
            line=dict(color="#2a2a38", width=1, dash="dot"),
            layer="below",
        )
        current += timedelta(hours=1)

    fig.update_layout(
        paper_bgcolor="#16161e",
        plot_bgcolor="#16161e",
        font=dict(color="#e8e8f0", family="DM Sans"),
        xaxis=dict(
            type="date",
            tickformat="%H:%M",
            showgrid=False,
            zeroline=False,
            range=[sched_start - timedelta(minutes=5), x_end + timedelta(minutes=5)],
            tickfont=dict(color="#a0a0b8", size=11),
            linecolor="#2a2a38",
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            range=[-0.6, 0.6],
        ),
        margin=dict(l=10, r=10, t=10, b=10),
        height=140,
        showlegend=False,
    )
    return fig

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
# Sidebar — owner & pet profile (no user data in HTML)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<div style='font-size:0.7rem;font-weight:700;color:#7c6af7;letter-spacing:0.12em;text-transform:uppercase;padding:0.5rem 0 0.8rem'>Owner Profile</div>", unsafe_allow_html=True)

    owner_name = st.text_input("Name", value="Jordan")
    start_time = st.time_input("Start time", value=None)
    start_str = start_time.strftime("%H:%M") if start_time else "08:00"
    available_minutes = st.number_input("Available time (min)", min_value=5, max_value=480, value=90, step=5)

    # Computed end time — safe: only computed values in HTML
    start_dt = datetime.strptime(start_str, "%H:%M")
    end_dt = start_dt + timedelta(minutes=int(available_minutes))
    end_str = end_dt.strftime("%H:%M")

    with st.container(border=True):
        ca, cb = st.columns(2)
        with ca:
            st.metric("Start", start_str)
        with cb:
            st.metric("End", end_str)
        st.caption(f"{available_minutes} min window")

    st.markdown("<div style='height:1px;background:#2a2a38;margin:1rem 0'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.7rem;font-weight:700;color:#7c6af7;letter-spacing:0.12em;text-transform:uppercase;padding:0.2rem 0 0.8rem'>Pet Profile</div>", unsafe_allow_html=True)

    pet_name = st.text_input("Pet's name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
    pet_notes = st.text_area("Special needs / notes", placeholder="e.g. takes medication twice a day")

    # Pet card — use st.metric / st.markdown (no unsafe HTML with user data)
    avatar = {"dog": "🐶", "cat": "🐱", "other": "🐾"}.get(species, "🐾")
    with st.container(border=True):
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown(f"## {avatar}")
        with c2:
            st.markdown(f"**{pet_name or '—'}**")
            st.caption(f"{species} · {pet_age} yr")

# ---------------------------------------------------------------------------
# Two-column layout: task input (left) + plan (right)
# ---------------------------------------------------------------------------
left, right = st.columns([5, 6], gap="large")

# ── LEFT: Task input ────────────────────────────────────────────────────────
with left:
    st.markdown("<div style='font-size:0.7rem;font-weight:700;color:#7c6af7;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.8rem'>Add a Task</div>", unsafe_allow_html=True)

    with st.form("add_task_form", clear_on_submit=True):
        task_title = st.text_input("Task title", placeholder="e.g. Morning walk")
        c1, c2 = st.columns(2)
        with c1:
            category = st.selectbox("Category", list(CATEGORY_ICONS.keys()))
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with c2:
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

    # Task queue
    if st.session_state.tasks:
        n = len(st.session_state.tasks)
        st.markdown(f"<div style='font-size:0.7rem;font-weight:700;color:#7c6af7;letter-spacing:0.12em;text-transform:uppercase;margin:1.2rem 0 0.6rem'>Queue · {n} task{'s' if n != 1 else ''}</div>", unsafe_allow_html=True)

        for i, task in enumerate(st.session_state.tasks):
            icon = CATEGORY_ICONS.get(task.category, "📋")
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

# ── RIGHT: Plan list ─────────────────────────────────────────────────────────
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
        total = plan.total_minutes()
        pct = min(100, int(total / plan.owner.available_minutes * 100))
        bar_color = "#22c55e" if pct <= 80 else "#f59e0b" if pct <= 100 else "#ef4444"
        n_sched = len(plan.scheduled)

        with st.container(border=True):
            st.markdown("<div style='font-size:0.7rem;font-weight:700;color:#7c6af7;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.4rem'>Today's Plan</div>", unsafe_allow_html=True)
            ca, cb = st.columns([3, 2])
            with ca:
                st.markdown(f"**{n_sched} task{'s' if n_sched != 1 else ''} scheduled**")
            with cb:
                st.markdown(f"<div style='text-align:right;font-size:0.82rem;color:#6b6b88'>{total} / {plan.owner.available_minutes} min</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='background:#2a2a38;border-radius:99px;height:6px;margin-top:0.3rem'><div style='background:{bar_color};width:{pct}%;height:100%;border-radius:99px'></div></div>", unsafe_allow_html=True)

        for warning in scheduler.detect_conflicts(plan.scheduled):
            st.warning(f"⚠️ {warning}")

        tab_list, tab_cal = st.tabs(["📋  List view", "🗓  Day view"])

        with tab_list:
            if plan.scheduled:
                for st_task in scheduler.sort_by_time(plan.scheduled):
                    icon = CATEGORY_ICONS.get(st_task.task.category, "📋")
                    tags = []
                    if st_task.task.is_mandatory:
                        tags.append("required")
                    if st_task.task.frequency != "once":
                        tags.append(st_task.task.frequency)

                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            tag_str = "  `" + "`  `".join(tags) + "`" if tags else ""
                            st.markdown(f"{icon} **{st_task.task.title}**{tag_str}")
                            st.caption(st_task.reason)
                        with c2:
                            st.markdown(f"<div style='text-align:right;font-size:0.88rem;font-weight:600;color:#c4b5fd'>{st_task.start_time} – {st_task.end_time}</div>", unsafe_allow_html=True)
                            st.caption(f"{st_task.task.duration_minutes} min")

            if plan.skipped:
                st.markdown(f"<div style='font-size:0.7rem;font-weight:700;color:#6b6b88;letter-spacing:0.12em;text-transform:uppercase;margin:1.2rem 0 0.5rem'>Skipped · {len(plan.skipped)}</div>", unsafe_allow_html=True)
                for task in plan.skipped:
                    icon = CATEGORY_ICONS.get(task.category, "📋")
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.markdown(f"~~{icon} {task.title}~~")
                        with c2:
                            st.caption(f"{task.duration_minutes} min · {task.priority}")

        with tab_cal:
            if not plan.scheduled:
                st.info("No scheduled tasks to display.")
            else:
                st.markdown("<div style='font-size:0.7rem;font-weight:700;color:#7c6af7;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.6rem'>Day Timeline</div>", unsafe_allow_html=True)
                st.plotly_chart(build_gantt(plan), use_container_width=True, config={"displayModeBar": False})

                # Legend
                st.markdown("<div style='font-size:0.7rem;font-weight:700;color:#6b6b88;letter-spacing:0.12em;text-transform:uppercase;margin:0.8rem 0 0.4rem'>Categories</div>", unsafe_allow_html=True)
                cols = st.columns(len(CATEGORY_COLORS))
                for col, (cat, color) in zip(cols, CATEGORY_COLORS.items()):
                    with col:
                        icon = CATEGORY_ICONS.get(cat, "📋")
                        st.markdown(f"<div style='text-align:center;font-size:1.1rem'>{icon}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align:center;font-size:0.7rem;color:{color};font-weight:600'>{cat}</div>", unsafe_allow_html=True)

                # Task breakdown below chart
                st.markdown("<div style='font-size:0.7rem;font-weight:700;color:#6b6b88;letter-spacing:0.12em;text-transform:uppercase;margin:1rem 0 0.4rem'>Task Breakdown</div>", unsafe_allow_html=True)
                for st_task in scheduler.sort_by_time(plan.scheduled):
                    color = CATEGORY_COLORS.get(st_task.task.category, "#a0a0b8")
                    icon = CATEGORY_ICONS.get(st_task.task.category, "📋")
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1:
                        st.markdown(f"{icon} **{st_task.task.title}**")
                    with c2:
                        st.markdown(f"<span style='color:#c4b5fd;font-size:0.85rem'>{st_task.start_time} – {st_task.end_time}</span>", unsafe_allow_html=True)
                    with c3:
                        st.caption(f"{st_task.task.duration_minutes} min")
