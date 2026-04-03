# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I started by mapping out what the app actually needed to do before writing any code. I landed on five classes:

- **Task**: just describes one care activity. Has a title, how long it takes, priority, category, and a flag for whether it's required no matter what. It doesn't do any scheduling itself.
- **Owner**: stores the human side of things: their name, how many minutes they have free today, and when they want to start. I kept it separate from pets on purpose so the time budget stays its own thing.
- **Pet**: basically just a profile: name, species, age, any special notes. No logic, just data.
- **Scheduler**: this is where all the decision-making lives. It takes an Owner, a Pet, and a list of Tasks and figures out what fits. I wanted all the scheduling rules in one place so the other classes stayed simple.
- **DailyPlan / ScheduledTask**: the output. A `ScheduledTask` is a task that got a real time slot (start, end, and a reason why it was picked). `DailyPlan` wraps everything up: what got scheduled, what got skipped, and a short summary.

The main thing I wanted to avoid was spreading logic around. Data classes hold data, Scheduler makes decisions, DailyPlan carries the results.

**b. Design changes**

Two things changed once I got into Phase 4:

1. **Task needed to know about recurrence.** Originally a task was just a description: it had no idea whether it repeated. I added `frequency` ("once", "daily", "weekly"), a `completed` flag, and `mark_complete()`. The method handles the recurrence rule itself: if a task is daily, completing it returns a fresh copy for tomorrow. I put this on Task rather than Scheduler because the task is the thing that "knows" how often it happens.

2. **Scheduler got three new methods.** `sort_by_time()`, `filter_tasks()`, and `detect_conflicts()` were all added without touching the original `schedule()` logic. Since Scheduler already deals with time, it made more sense to keep these there than to make them standalone functions.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler looks at three things, in this order:

1. **Mandatory flag**: these always go in, no matter how little time is left. Medication can't be skipped because the owner is running behind.
2. **Priority**: optional tasks get sorted high to low before anything is placed. Higher priority gets first shot at the remaining time.
3. **Time budget**: an optional task only gets added if its duration fits in what's left. If it doesn't fit, it's skipped.

I put mandatory first because the consequences of missing a vet-prescribed task are way more serious than skipping enrichment or grooming.

**b. Tradeoffs**

The scheduler is greedy: it locks in the highest-priority task first and moves on. It never goes back to reconsider.

Here's where that bites: say the owner has 30 minutes, a high-priority 25-minute walk, and two medium-priority 10-minute tasks. The scheduler takes the walk (25 min), then both 10-minute tasks don't fit in the 5 minutes left: so they're skipped. Meanwhile, skipping the walk would've let both 10-minute tasks in (20 min total). But that would mean ignoring the priority the user explicitly set, which felt wrong.

The other limitation is that conflict detection only flags exact time-window overlaps. It doesn't account for any buffer time between tasks.

---

## 3. AI Collaboration

**a. How I used AI**

I used AI throughout, but differently at each stage:

- **Phase 1:** I described the four main classes and asked for a Mermaid diagram. It was a good starting point but I had to rearrange some of the relationships.
- **Phase 2:** I used agent mode and pointed it at my existing file: something like "#file:pawpal_system.py, implement the schedule() method based on this algorithm." Giving it the file context made the output way more usable than generic prompts.
- **Phase 4:** I asked specifically how to handle recurring tasks without adding a date library dependency. That constraint shaped the design: `mark_complete()` returns a new Task rather than computing a future date.
- **Phase 5:** I asked for edge cases to test on a scheduler with mandatory tasks and a time budget. It caught the "task one minute over" boundary case I hadn't thought about.

**b. Judgment and verification**

At one point during Phase 4, AI suggested making `detect_conflicts()` raise an exception when it found overlapping tasks. I didn't use that. If two tasks conflict, that's something the user should see and fix: not a crash. I rewrote it to return a list of warning strings instead, and the UI shows those with `st.warning()`. I wrote `test_detect_conflicts_flags_overlapping_tasks` specifically to confirm this version worked before moving on.

---

## 4. Testing and Verification

**a. What I tested**

The test suite ended up covering:

- Priority score mapping (including unknown priority fallbacks)
- `mark_complete()`: does it actually set the flag? Does it return a new task only when it should?
- Core scheduling: does time get respected, do mandatory tasks always make it in, does priority order hold, are start/end times right, do tasks overlap?
- Sorting: does `sort_by_time()` actually return things in order?
- Recurrence: does daily return a fresh task? Does "once" return None?
- Conflict detection: overlapping windows flagged, adjacent ones not
- Filtering: does asking for completed/incomplete/all give the right subset?
- Edge cases: empty list, task that exactly fills time, task one minute over

I focused on these because scheduling bugs tend to be quiet. A wrong time slot doesn't raise an error: it just gives the user a bad plan.

**b. Confidence**

Confidence level: 4/5

The main paths are solid. Things I'd want to add with more time:

- What happens if tasks run past midnight (e.g., 23:00 start, 90-minute task)?
- What if several mandatory tasks together go way over the time budget?
- Filtering on a list where some recurring tasks are done and some aren't
- Conflict detection with three or more overlapping tasks at once

---

## 5. Reflection

**a. What went well**

Keeping the logic in `pawpal_system.py` completely separate from the UI paid off in Phase 4. I could test every new method in `main.py` and with pytest before touching `app.py` at all. When I was confident the logic was right, wiring it into Streamlit was only a few lines. That separation made debugging way easier.

**b. What I would improve**

The greedy approach can leave a lot of time on the table. A knapsack-style algorithm: try combinations of optional tasks and pick whichever set has the highest total priority score while fitting in the budget: would be smarter. The catch is it's O(2^n) in the worst case, so I'd need to cap the number of tasks or use dynamic programming to make it practical.

**c. Key takeaway**

The most useful thing I learned is that being specific with AI prompts matters a lot more than I expected. "Build a scheduler" gives you something generic. "#file:pawpal_system.py, add a sort_by_time() method that sorts ScheduledTask objects by start_time string" gives you something you can actually use. The job isn't just giving instructions: it's making sure the output actually does what the design requires, not just what it looks like it does.
