# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML design (see `.claude/outputs/design-uml.md`) identified five classes:

- **Task** — holds a single care activity: title, duration, priority, category, and whether it is mandatory. Responsible only for describing work, not scheduling it.
- **Owner** — captures the human's constraints: name, how many minutes they have today, and when they want to start. Does not know about pets directly; acts as a time-budget container.
- **Pet** — metadata about the animal (name, species, age, notes). Purely descriptive; no scheduling logic.
- **Scheduler** — the stateless engine that receives an Owner, a Pet, and a list of Tasks and returns a `DailyPlan`. All scheduling decisions live here, keeping the other classes simple.
- **DailyPlan / ScheduledTask** — output objects: `ScheduledTask` wraps a `Task` with assigned start/end times and a reason string; `DailyPlan` groups scheduled and skipped tasks with a summary.

The core design principle was separation of concerns: data classes hold state, `Scheduler` holds logic, and `DailyPlan` holds results.

**b. Design changes**

During Phase 4 (algorithmic layer), two changes were made:

1. **`Task` gained `frequency` and `completed` attributes plus `mark_complete()`.** The initial design treated tasks as static descriptions. Adding recurrence required tasks to know whether they repeat, and `mark_complete()` encapsulates the rule for spawning the next occurrence. This kept the logic on the data object that owns the state, rather than scattering it through the Scheduler.

2. **`Scheduler` gained `sort_by_time()`, `filter_tasks()`, and `detect_conflicts()`.** These were additive — they did not change the existing `schedule()` algorithm. Putting them on `Scheduler` was deliberate: the class already owns time-based reasoning, so these methods belong there rather than as free functions.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints in this order:

1. **Mandatory flag** — mandatory tasks (e.g., medication) are always included, even if the owner has no time left. Time budget is ignored for these.
2. **Priority** — optional tasks are sorted high → medium → low before placement. A high-priority task beats a low-priority task for any remaining time slot.
3. **Available time** — optional tasks are only scheduled if they fit within the owner's stated available minutes. The first task that doesn't fit is skipped; subsequent tasks of smaller duration are not considered (greedy fit).

The mandatory constraint takes precedence because missing a pet's medication has real health consequences, while skipping a grooming session does not.

**b. Tradeoffs**

The scheduler uses a **greedy first-fit** algorithm: it places tasks in priority order and skips any task that doesn't fit, without looking ahead or backtracking.

*Example tradeoff:* If an owner has 30 minutes and there is one high-priority 25-minute walk and two medium-priority 10-minute tasks, the scheduler schedules only the walk (25 min) and skips both 10-minute tasks, leaving 5 minutes unused. A smarter algorithm could skip the walk and fit both 10-minute tasks (20 min total) and waste less time — but deciding which approach is "better" requires knowing the owner's preferences.

This tradeoff is reasonable because priority is the explicit signal the user provides. Overriding a high-priority task to fit lower-priority ones would violate the user's stated intentions. Conflict detection currently checks only for exact time-window overlaps, not buffer time between tasks.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used across all phases:

- **Phase 1 (Design):** Brainstormed the five-class architecture and generated the initial Mermaid.js UML diagram. Prompts like "Given an Owner, Pet, Task, and Scheduler, draw a class diagram showing their relationships" produced a solid starting point.
- **Phase 2 (Implementation):** Used agent mode to flesh out method bodies. The prompt "#file:pawpal_system.py — implement the Scheduler.schedule() method following the algorithm in the design doc" was effective because it gave the AI a concrete target.
- **Phase 4 (Algorithms):** Asked "How should mark_complete() handle recurring tasks without adding a date dependency?" to scope the feature to what the data model could support.
- **Phase 5 (Testing):** Used "What are the most important edge cases for a scheduler with mandatory tasks and time constraints?" to identify the boundary tests (e.g., task exactly filling time, task one minute over).

**b. Judgment and verification**

During Phase 4, AI suggested implementing conflict detection by raising an exception when a conflict is found. This was rejected: raising exceptions for scheduling conflicts would crash the app on normal user input (two tasks accidentally at the same time). Instead, `detect_conflicts()` was implemented to return a list of warning strings, letting the UI display them gracefully with `st.warning()`. The test `test_detect_conflicts_flags_overlapping_tasks` verified the warning-based approach works correctly.

---

## 4. Testing and Verification

**a. What you tested**

The test suite covers:

- **Priority scoring** — correct numeric mapping and unknown-priority fallback.
- **Task completion** — `mark_complete()` sets `completed=True` and returns a new task only for recurring frequencies.
- **Scheduling correctness** — tasks fit within time, mandatory tasks always included, priority order respected, correct start/end times assigned, no overlaps in sequential output.
- **Sorting** — `sort_by_time()` returns chronological order.
- **Recurrence** — daily and weekly tasks produce a new incomplete instance; "once" tasks return None.
- **Conflict detection** — overlapping windows flagged, adjacent windows not flagged.
- **Filtering** — completed/incomplete/all subsets returned correctly.
- **Edge cases** — empty task list, task exactly filling time, task one minute over limit.

These tests matter because scheduling bugs are silent — a wrong start time or a skipped mandatory task doesn't raise an error, it just produces a bad plan the user might not notice.

**b. Confidence**

Confidence level: ★★★★☆ (4/5)

The core scheduling path is well-covered. Edge cases I would test next with more time:

- Tasks that push past midnight (e.g., 23:00 start + 90-minute task).
- Multiple mandatory tasks that together exceed available time by a large margin.
- `filter_tasks()` with a mix of completed and uncompleted recurring tasks.
- `detect_conflicts()` with three or more overlapping tasks.

---

## 5. Reflection

**a. What went well**

The separation between the logic layer (`pawpal_system.py`) and the UI (`app.py`) worked very well. Every Phase 4 addition — sorting, filtering, conflict detection — could be developed and tested entirely in `main.py` and `pytest` without touching Streamlit. When the logic was confirmed correct, wiring it into the UI took only a few lines.

**b. What you would improve**

The greedy scheduler does not backtrack, which can leave significant time unused. A next iteration would explore a simple knapsack approach: try all combinations of optional tasks that fit within available minutes and pick the highest-priority set. The constraint is that this is O(2^n) in the worst case, so it would need a cap on the number of tasks or a dynamic-programming solution.

**c. Key takeaway**

The most important lesson was that AI is most useful when given precise, scoped prompts tied to existing code — not open-ended requests. "Generate a scheduler" produces generic boilerplate. "#file:pawpal_system.py — implement sort_by_time() that sorts ScheduledTask objects by their start_time string" produces directly usable code. The lead architect's job is to maintain the design intent and verify that AI output actually satisfies the requirements, not just looks plausible.
