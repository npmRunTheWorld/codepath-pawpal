from datetime import datetime, timedelta


PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}


class Task:
    """A single pet care activity."""

    def __init__(self, title: str, duration_minutes: int, priority: str,
                 category: str = "other", is_mandatory: bool = False,
                 frequency: str = "once"):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority          # "low" / "medium" / "high"
        self.category = category          # "walk" / "feed" / "meds" / "enrichment" / "grooming" / "other"
        self.is_mandatory = is_mandatory
        self.frequency = frequency        # "once" / "daily" / "weekly"
        self.completed = False

    def priority_score(self) -> int:
        """Return numeric priority for sorting (high=3, medium=2, low=1)."""
        return PRIORITY_MAP.get(self.priority, 1)

    def mark_complete(self):
        """Mark this task complete. Returns a new Task for the next occurrence if recurring, else None."""
        self.completed = True
        if self.frequency == "daily":
            return Task(self.title, self.duration_minutes, self.priority,
                        self.category, self.is_mandatory, self.frequency)
        if self.frequency == "weekly":
            return Task(self.title, self.duration_minutes, self.priority,
                        self.category, self.is_mandatory, self.frequency)
        return None

    def __repr__(self):
        return f"Task({self.title!r}, {self.duration_minutes}min, {self.priority})"


class Owner:
    """Pet owner and their daily time constraints."""

    def __init__(self, name: str, available_minutes: int,
                 start_time: str = "08:00", preferences: dict = None):
        self.name = name
        self.available_minutes = available_minutes
        self.start_time = start_time          # "HH:MM"
        self.preferences = preferences or {}

    def __repr__(self):
        return f"Owner({self.name!r}, {self.available_minutes}min)"


class Pet:
    """The pet being cared for."""

    def __init__(self, name: str, species: str, age: int = 0, notes: str = ""):
        self.name = name
        self.species = species    # "dog" / "cat" / "other"
        self.age = age
        self.notes = notes

    def display_name(self) -> str:
        """Return a human-readable name including species."""
        return f"{self.name} the {self.species}"

    def __repr__(self):
        return f"Pet({self.name!r}, {self.species!r})"


class ScheduledTask:
    """A Task placed into the day's timeline with a start time and reason."""

    def __init__(self, task: Task, start_time: str, end_time: str, reason: str):
        self.task = task
        self.start_time = start_time    # "HH:MM"
        self.end_time = end_time        # "HH:MM"
        self.reason = reason

    def __repr__(self):
        return f"ScheduledTask({self.task.title!r}, {self.start_time}–{self.end_time})"


class DailyPlan:
    """The final output of the scheduler."""

    def __init__(self, owner: Owner, pet: Pet,
                 scheduled: list, skipped: list):
        self.owner = owner
        self.pet = pet
        self.scheduled = scheduled      # list[ScheduledTask], ordered by start time
        self.skipped = skipped          # list[Task]
        self.generated_at = datetime.now()

    def total_minutes(self) -> int:
        """Return total minutes of all scheduled tasks."""
        return sum(st.task.duration_minutes for st in self.scheduled)

    def summary(self) -> str:
        """Return a one-line summary of the plan."""
        return (
            f"{len(self.scheduled)} tasks scheduled "
            f"({self.total_minutes()} min) for {self.pet.display_name()}"
        )

    def __repr__(self):
        return f"DailyPlan({self.summary()})"


class Scheduler:
    """Scheduling engine. Stateless — call schedule() to produce a DailyPlan."""

    def schedule(self, owner: Owner, pet: Pet, tasks: list) -> DailyPlan:
        """Build a DailyPlan by fitting tasks into the owner's available time."""
        mandatory = [t for t in tasks if t.is_mandatory]
        optional = sorted(
            [t for t in tasks if not t.is_mandatory],
            key=lambda t: t.priority_score(),
            reverse=True,
        )

        scheduled = []
        skipped = []
        remaining = owner.available_minutes
        current_dt = self._parse_time(owner.start_time)

        for task in mandatory + optional:
            if task.is_mandatory or task.duration_minutes <= remaining:
                start_str = self._fmt(current_dt)
                end_dt = current_dt + timedelta(minutes=task.duration_minutes)
                end_str = self._fmt(end_dt)
                reason = self._build_reason(task, remaining, owner)
                scheduled.append(ScheduledTask(task, start_str, end_str, reason))
                current_dt = end_dt
                remaining -= task.duration_minutes
            else:
                skipped.append(task)

        return DailyPlan(owner, pet, scheduled, skipped)

    def sort_by_time(self, scheduled_tasks: list) -> list:
        """Return scheduled tasks sorted chronologically by start time."""
        return sorted(scheduled_tasks, key=lambda st: st.start_time)

    def filter_tasks(self, tasks: list, completed: bool = None) -> list:
        """Filter tasks by completion status. Pass None to return all."""
        if completed is None:
            return list(tasks)
        return [t for t in tasks if t.completed == completed]

    def detect_conflicts(self, scheduled_tasks: list) -> list:
        """Return warning strings for any overlapping scheduled tasks."""
        warnings = []
        for i, a in enumerate(scheduled_tasks):
            for b in scheduled_tasks[i + 1:]:
                a_start = self._parse_time(a.start_time)
                a_end = self._parse_time(a.end_time)
                b_start = self._parse_time(b.start_time)
                b_end = self._parse_time(b.end_time)
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"Conflict: '{a.task.title}' ({a.start_time}–{a.end_time}) "
                        f"overlaps with '{b.task.title}' ({b.start_time}–{b.end_time})"
                    )
        return warnings

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_time(self, time_str: str) -> datetime:
        return datetime.strptime(time_str, "%H:%M")

    def _fmt(self, dt: datetime) -> str:
        return dt.strftime("%H:%M")

    def _build_reason(self, task: Task, remaining_minutes: int, owner: Owner) -> str:
        """Generate a human-readable reason why this task was scheduled."""
        if task.is_mandatory:
            return "Mandatory — always scheduled regardless of available time."
        freq_note = f" Recurs {task.frequency}." if task.frequency != "once" else ""
        return (
            f"Priority: {task.priority}.{freq_note} "
            f"Fits within {owner.name}'s remaining time ({remaining_minutes} min left)."
        )
