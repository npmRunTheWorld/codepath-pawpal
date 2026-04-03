# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Features

- **Priority-based scheduling** — Tasks are ranked high → medium → low. Higher-priority tasks claim time first.
- **Mandatory task guarantee** — Tasks marked "mandatory" (e.g., medication) are always scheduled, regardless of remaining time.
- **Sorting by time** — The generated plan displays tasks in chronological order using `Scheduler.sort_by_time()`.
- **Filtering by completion status** — `Scheduler.filter_tasks()` lets you retrieve only completed or only pending tasks.
- **Recurring task support** — Tasks can recur `daily` or `weekly`. Calling `mark_complete()` on a recurring task automatically creates the next occurrence.
- **Conflict warnings** — `Scheduler.detect_conflicts()` scans the schedule for overlapping time windows and surfaces warnings in the UI via `st.warning()`.

## Smarter Scheduling

Phase 4 of development added an algorithmic layer on top of the core scheduler:

| Feature | Method | Description |
|---|---|---|
| Sorting | `Scheduler.sort_by_time(scheduled_tasks)` | Returns `ScheduledTask` list sorted chronologically by start time. Uses Python's `sorted()` with a `lambda` key on `"HH:MM"` strings. |
| Filtering | `Scheduler.filter_tasks(tasks, completed)` | Filters a task list by completion status. Pass `True`, `False`, or `None` (all). |
| Recurrence | `Task.mark_complete()` | Marks a task done. Returns a fresh `Task` copy for the next cycle if `frequency` is `"daily"` or `"weekly"`. Returns `None` for one-time tasks. |
| Conflict detection | `Scheduler.detect_conflicts(scheduled_tasks)` | Compares every pair of `ScheduledTask` time windows. Returns a list of human-readable warning strings for any overlaps. Does not raise exceptions — warnings are displayed in the UI. |

**Tradeoff:** The scheduler uses a greedy first-fit strategy (highest priority first). This can leave small gaps of unused time when a large high-priority task crowds out several smaller lower-priority tasks that would collectively fit. Priority is respected over time efficiency, which reflects the owner's explicit ranking.

## 📸 Demo

_Add a screenshot of your running Streamlit app here._

## Testing PawPal+

### Running tests

```bash
python3 -m pytest
```

### What the tests cover

| Category | Tests |
|---|---|
| Task attributes | Priority score mapping, default frequency/completed values |
| Task completion | `mark_complete()` sets flag; daily/weekly creates new task; once returns None |
| Core scheduling | Tasks fit in time, mandatory always included, priority order, correct start/end times, no overlaps |
| Edge cases | Empty task list, task exactly filling time, task one minute over limit |
| Sorting | Chronological order, empty list, single item |
| Recurrence | Daily and weekly produce new incomplete task; once produces None |
| Conflict detection | Overlapping windows flagged; adjacent windows not flagged; empty list safe |
| Filtering | Completed, incomplete, and all subsets returned correctly |

**Confidence level: ★★★★☆** — All 37 tests pass. Core scheduling paths, recurrence logic, conflict detection, and filter behavior are verified. Edge cases around midnight-crossing schedules and large numbers of overlapping mandatory tasks would be tested in a next iteration.
