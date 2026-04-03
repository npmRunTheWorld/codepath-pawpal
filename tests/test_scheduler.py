import pytest
from pawpal_system import Task, Owner, Pet, Scheduler, DailyPlan, ScheduledTask


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def owner():
    return Owner("Jordan", available_minutes=60, start_time="08:00")


@pytest.fixture
def pet():
    return Pet("Mochi", "dog", age=3)


@pytest.fixture
def scheduler():
    return Scheduler()


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

def test_task_priority_score_mapping():
    assert Task("a", 10, "low").priority_score() == 1
    assert Task("a", 10, "medium").priority_score() == 2
    assert Task("a", 10, "high").priority_score() == 3


def test_task_priority_score_unknown_defaults_to_1():
    assert Task("a", 10, "urgent").priority_score() == 1


def test_task_default_frequency_is_once():
    t = Task("Walk", 30, "high")
    assert t.frequency == "once"


def test_task_default_completed_is_false():
    t = Task("Walk", 30, "high")
    assert t.completed is False


# ---------------------------------------------------------------------------
# Task.mark_complete — completion status
# ---------------------------------------------------------------------------

def test_mark_complete_sets_completed_true():
    task = Task("Walk", 30, "high", frequency="once")
    task.mark_complete()
    assert task.completed is True


def test_mark_complete_once_returns_none():
    task = Task("Walk", 30, "high", frequency="once")
    result = task.mark_complete()
    assert result is None


def test_mark_complete_daily_returns_new_task():
    task = Task("Meds", 5, "high", "meds", is_mandatory=True, frequency="daily")
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.title == task.title
    assert next_task.frequency == "daily"


def test_mark_complete_weekly_returns_new_task():
    task = Task("Grooming", 15, "low", frequency="weekly")
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.frequency == "weekly"
    assert next_task.completed is False


# ---------------------------------------------------------------------------
# DailyPlan helpers
# ---------------------------------------------------------------------------

def test_daily_plan_total_minutes(owner, pet, scheduler):
    tasks = [
        Task("Walk", 30, "high"),
        Task("Feed", 10, "high", is_mandatory=True),
    ]
    plan = scheduler.schedule(owner, pet, tasks)
    assert plan.total_minutes() == 40


def test_daily_plan_summary_contains_pet_name(owner, pet, scheduler):
    plan = scheduler.schedule(owner, pet, [])
    assert "Mochi" in plan.summary()


# ---------------------------------------------------------------------------
# Scheduler — basic scheduling
# ---------------------------------------------------------------------------

def test_schedule_returns_daily_plan(owner, pet, scheduler):
    plan = scheduler.schedule(owner, pet, [])
    assert isinstance(plan, DailyPlan)


def test_tasks_fit_within_available_time_are_scheduled(owner, pet, scheduler):
    tasks = [Task("Walk", 30, "high"), Task("Feed", 20, "medium")]
    plan = scheduler.schedule(owner, pet, tasks)
    assert len(plan.scheduled) == 2
    assert len(plan.skipped) == 0


def test_tasks_exceeding_available_time_are_skipped(owner, pet, scheduler):
    # owner has 60 min; these three need 90 total
    tasks = [
        Task("Walk", 30, "high"),
        Task("Playtime", 20, "medium"),
        Task("Grooming", 40, "low"),
    ]
    plan = scheduler.schedule(owner, pet, tasks)
    total_scheduled = sum(st.task.duration_minutes for st in plan.scheduled)
    assert total_scheduled <= 60
    assert any(t.title == "Grooming" for t in plan.skipped)


# ---------------------------------------------------------------------------
# Scheduler — priority ordering
# ---------------------------------------------------------------------------

def test_high_priority_scheduled_before_low(owner, pet, scheduler):
    tasks = [
        Task("Low task", 10, "low"),
        Task("High task", 10, "high"),
        Task("Medium task", 10, "medium"),
    ]
    plan = scheduler.schedule(owner, pet, tasks)
    titles = [st.task.title for st in plan.scheduled]
    assert titles.index("High task") < titles.index("Medium task")
    assert titles.index("Medium task") < titles.index("Low task")


def test_low_priority_task_skipped_when_time_tight(scheduler, pet):
    tight_owner = Owner("Jordan", available_minutes=20, start_time="08:00")
    tasks = [
        Task("High task", 15, "high"),
        Task("Low task", 15, "low"),
    ]
    plan = scheduler.schedule(tight_owner, pet, tasks)
    scheduled_titles = [st.task.title for st in plan.scheduled]
    assert "High task" in scheduled_titles
    assert any(t.title == "Low task" for t in plan.skipped)


# ---------------------------------------------------------------------------
# Scheduler — mandatory tasks
# ---------------------------------------------------------------------------

def test_mandatory_tasks_always_scheduled(scheduler, pet):
    # only 5 min available but meds are mandatory
    tiny_owner = Owner("Jordan", available_minutes=5, start_time="08:00")
    tasks = [
        Task("Medication", 10, "high", is_mandatory=True),
        Task("Walk", 30, "high"),
    ]
    plan = scheduler.schedule(tiny_owner, pet, tasks)
    scheduled_titles = [st.task.title for st in plan.scheduled]
    assert "Medication" in scheduled_titles


def test_mandatory_tasks_scheduled_before_optional(owner, pet, scheduler):
    tasks = [
        Task("Walk", 10, "high"),
        Task("Meds", 5, "high", is_mandatory=True),
    ]
    plan = scheduler.schedule(owner, pet, tasks)
    titles = [st.task.title for st in plan.scheduled]
    assert titles.index("Meds") < titles.index("Walk")


def test_mandatory_task_reason_says_mandatory(owner, pet, scheduler):
    tasks = [Task("Meds", 5, "high", is_mandatory=True)]
    plan = scheduler.schedule(owner, pet, tasks)
    assert "Mandatory" in plan.scheduled[0].reason


# ---------------------------------------------------------------------------
# Scheduler — time assignment
# ---------------------------------------------------------------------------

def test_start_time_matches_owner_start(owner, pet, scheduler):
    tasks = [Task("Feed", 10, "high", is_mandatory=True)]
    plan = scheduler.schedule(owner, pet, tasks)
    assert plan.scheduled[0].start_time == "08:00"


def test_tasks_do_not_overlap(owner, pet, scheduler):
    tasks = [
        Task("Feed", 10, "high", is_mandatory=True),
        Task("Walk", 20, "high"),
        Task("Playtime", 15, "medium"),
    ]
    plan = scheduler.schedule(owner, pet, tasks)
    for i in range(len(plan.scheduled) - 1):
        assert plan.scheduled[i].end_time == plan.scheduled[i + 1].start_time


def test_end_time_is_correct(owner, pet, scheduler):
    tasks = [Task("Walk", 30, "high")]
    plan = scheduler.schedule(owner, pet, tasks)
    assert plan.scheduled[0].start_time == "08:00"
    assert plan.scheduled[0].end_time == "08:30"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_task_list(owner, pet, scheduler):
    plan = scheduler.schedule(owner, pet, [])
    assert plan.scheduled == []
    assert plan.skipped == []


def test_single_task_exactly_fills_time(pet, scheduler):
    owner = Owner("Jordan", available_minutes=30, start_time="09:00")
    tasks = [Task("Walk", 30, "high")]
    plan = scheduler.schedule(owner, pet, tasks)
    assert len(plan.scheduled) == 1
    assert len(plan.skipped) == 0


def test_task_one_minute_over_is_skipped(pet, scheduler):
    owner = Owner("Jordan", available_minutes=29, start_time="09:00")
    tasks = [Task("Walk", 30, "high")]
    plan = scheduler.schedule(owner, pet, tasks)
    assert len(plan.scheduled) == 0
    assert len(plan.skipped) == 1


# ---------------------------------------------------------------------------
# Phase 5 — Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order(owner, pet, scheduler):
    tasks = [
        Task("Low task", 10, "low"),
        Task("High task", 10, "high"),
        Task("Medium task", 10, "medium"),
    ]
    plan = scheduler.schedule(owner, pet, tasks)
    sorted_tasks = scheduler.sort_by_time(plan.scheduled)
    times = [st.start_time for st in sorted_tasks]
    assert times == sorted(times)


def test_sort_by_time_on_empty_list(scheduler):
    assert scheduler.sort_by_time([]) == []


def test_sort_by_time_single_item(owner, pet, scheduler):
    plan = scheduler.schedule(owner, pet, [Task("Walk", 10, "high")])
    result = scheduler.sort_by_time(plan.scheduled)
    assert len(result) == 1


# ---------------------------------------------------------------------------
# Phase 5 — Recurrence logic
# ---------------------------------------------------------------------------

def test_daily_task_completion_creates_new_task():
    task = Task("Morning meds", 5, "high", "meds", is_mandatory=True, frequency="daily")
    next_task = task.mark_complete()
    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.title == "Morning meds"


def test_weekly_task_completion_creates_new_task():
    task = Task("Bath", 20, "medium", "grooming", frequency="weekly")
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.frequency == "weekly"


def test_once_task_completion_returns_none():
    task = Task("Vet visit", 60, "high", frequency="once")
    next_task = task.mark_complete()
    assert task.completed is True
    assert next_task is None


# ---------------------------------------------------------------------------
# Phase 5 — Conflict detection
# ---------------------------------------------------------------------------

def test_no_conflicts_in_sequential_plan(owner, pet, scheduler):
    tasks = [Task("Walk", 30, "high"), Task("Feed", 20, "medium")]
    plan = scheduler.schedule(owner, pet, tasks)
    conflicts = scheduler.detect_conflicts(plan.scheduled)
    assert conflicts == []


def test_detect_conflicts_flags_overlapping_tasks(pet, scheduler):
    # Construct two overlapping ScheduledTasks manually
    t1 = Task("Walk", 30, "high")
    t2 = Task("Feed", 20, "medium")
    st1 = ScheduledTask(t1, "09:00", "09:30", "reason")
    st2 = ScheduledTask(t2, "09:15", "09:35", "reason")  # overlaps with st1
    conflicts = scheduler.detect_conflicts([st1, st2])
    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]
    assert "Feed" in conflicts[0]


def test_detect_conflicts_no_overlap_adjacent(pet, scheduler):
    t1 = Task("Walk", 30, "high")
    t2 = Task("Feed", 20, "medium")
    st1 = ScheduledTask(t1, "09:00", "09:30", "reason")
    st2 = ScheduledTask(t2, "09:30", "09:50", "reason")  # adjacent, not overlapping
    conflicts = scheduler.detect_conflicts([st1, st2])
    assert conflicts == []


def test_detect_conflicts_empty_list(scheduler):
    assert scheduler.detect_conflicts([]) == []


# ---------------------------------------------------------------------------
# Phase 5 — Filter tasks
# ---------------------------------------------------------------------------

def test_filter_tasks_completed(scheduler):
    tasks = [Task("Walk", 30, "high"), Task("Feed", 10, "medium")]
    tasks[0].mark_complete()
    done = scheduler.filter_tasks(tasks, completed=True)
    assert len(done) == 1
    assert done[0].title == "Walk"


def test_filter_tasks_incomplete(scheduler):
    tasks = [Task("Walk", 30, "high"), Task("Feed", 10, "medium")]
    tasks[0].mark_complete()
    pending = scheduler.filter_tasks(tasks, completed=False)
    assert len(pending) == 1
    assert pending[0].title == "Feed"


def test_filter_tasks_none_returns_all(scheduler):
    tasks = [Task("Walk", 30, "high"), Task("Feed", 10, "medium")]
    result = scheduler.filter_tasks(tasks, completed=None)
    assert len(result) == 2
