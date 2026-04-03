import streamlit as st
from pawpal_system import Task, Owner, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Daily pet care planner — builds a schedule based on your time and priorities.")

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "plan" not in st.session_state:
    st.session_state.plan = None

# ---------------------------------------------------------------------------
# Sidebar — Owner & Pet info
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Owner")
    owner_name = st.text_input("Your name", value="Jordan")
    available_minutes = st.number_input(
        "Time available today (minutes)", min_value=5, max_value=480, value=90, step=5
    )
    start_time = st.time_input("Start time", value=None)
    start_str = start_time.strftime("%H:%M") if start_time else "08:00"

    st.divider()

    st.header("Pet")
    pet_name = st.text_input("Pet's name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
    pet_notes = st.text_area("Special needs / notes", placeholder="e.g. takes medication twice a day")

# ---------------------------------------------------------------------------
# Main — Task input
# ---------------------------------------------------------------------------
st.subheader("Tasks")

with st.form("add_task_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", placeholder="e.g. Morning walk")
        category = st.selectbox("Category", ["walk", "feed", "meds", "enrichment", "grooming", "other"])
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["high", "medium", "low"])

    col3, col4 = st.columns(2)
    with col3:
        is_mandatory = st.checkbox("Mandatory (always include, e.g. medication)")
    with col4:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    submitted = st.form_submit_button("Add task", use_container_width=True)

    if submitted:
        if task_title.strip():
            st.session_state.tasks.append(
                Task(task_title.strip(), int(duration), priority, category, is_mandatory, frequency)
            )
            st.session_state.plan = None  # reset plan on change
        else:
            st.warning("Task title cannot be empty.")

# Show current task list
if st.session_state.tasks:
    st.markdown(f"**{len(st.session_state.tasks)} task(s) added:**")

    for i, task in enumerate(st.session_state.tasks):
        col1, col2 = st.columns([5, 1])
        with col1:
            badge = "🔴" if task.is_mandatory else {"high": "🟠", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
            label = f"{badge} **{task.title}** — {task.duration_minutes} min · {task.priority} · {task.category}"
            if task.is_mandatory:
                label += " · *mandatory*"
            if task.frequency != "once":
                label += f" · _{task.frequency}_"
            st.markdown(label)
        with col2:
            if st.button("Remove", key=f"remove_{i}"):
                st.session_state.tasks.pop(i)
                st.session_state.plan = None
                st.rerun()
else:
    st.info("No tasks yet. Add one above.")

# ---------------------------------------------------------------------------
# Generate schedule
# ---------------------------------------------------------------------------
st.divider()

if st.button("Generate schedule", type="primary", use_container_width=True):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner = Owner(owner_name, int(available_minutes), start_str)
        pet = Pet(pet_name, species, int(pet_age), pet_notes)
        st.session_state.plan = Scheduler().schedule(owner, pet, st.session_state.tasks)

# ---------------------------------------------------------------------------
# Display plan
# ---------------------------------------------------------------------------
plan = st.session_state.plan

if plan:
    scheduler = Scheduler()
    st.subheader("Today's Plan")
    st.success(plan.summary())

    # Conflict detection
    conflicts = scheduler.detect_conflicts(plan.scheduled)
    for warning in conflicts:
        st.warning(f"⚠️ {warning}")

    if plan.scheduled:
        st.markdown("### Scheduled")
        sorted_scheduled = scheduler.sort_by_time(plan.scheduled)
        for st_task in sorted_scheduled:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    title_line = f"**{st_task.task.title}**"
                    if st_task.task.frequency != "once":
                        title_line += f" _{st_task.task.frequency}_"
                    st.markdown(title_line)
                    st.caption(st_task.reason)
                with col2:
                    st.markdown(f"🕐 {st_task.start_time} – {st_task.end_time}")
                    st.caption(f"{st_task.task.duration_minutes} min · {st_task.task.category}")

    if plan.skipped:
        st.markdown("### Skipped (not enough time today)")
        for task in plan.skipped:
            st.markdown(f"- **{task.title}** ({task.duration_minutes} min · {task.priority} priority)")
