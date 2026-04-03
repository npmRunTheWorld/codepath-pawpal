"""CLI demo for PawPal+ — run with: python main.py"""
from pawpal_system import Owner, Pet, Task, Scheduler


def print_plan(plan, scheduler):
    print(f"\n{'='*50}")
    print(f"  Today's Schedule — {plan.pet.display_name()}")
    print(f"  Owner: {plan.owner.name}  |  Available: {plan.owner.available_minutes} min")
    print(f"{'='*50}")

    if not plan.scheduled:
        print("  (no tasks scheduled)")
    else:
        sorted_tasks = scheduler.sort_by_time(plan.scheduled)
        for st in sorted_tasks:
            tag = "[MANDATORY]" if st.task.is_mandatory else f"[{st.task.priority.upper()}]"
            freq = f" ({st.task.frequency})" if st.task.frequency != "once" else ""
            print(f"  {st.start_time}–{st.end_time}  {tag}  {st.task.title}{freq}")
            print(f"            {st.reason}")

    if plan.skipped:
        print(f"\n  Skipped ({len(plan.skipped)} tasks — not enough time):")
        for t in plan.skipped:
            print(f"    - {t.title} ({t.duration_minutes} min, {t.priority} priority)")

    conflicts = scheduler.detect_conflicts(plan.scheduled)
    if conflicts:
        print("\n  ⚠ CONFLICTS DETECTED:")
        for w in conflicts:
            print(f"    {w}")

    print(f"\n  Total scheduled: {plan.total_minutes()} min")


def demo_recurrence():
    print("\n--- Recurrence Demo ---")
    task = Task("Evening meds", 5, "high", "meds", is_mandatory=True, frequency="daily")
    print(f"  Task: {task}  completed={task.completed}")
    next_task = task.mark_complete()
    print(f"  After mark_complete(): completed={task.completed}")
    if next_task:
        print(f"  Next occurrence created: {next_task}  completed={next_task.completed}")


def demo_filtering(tasks):
    scheduler = Scheduler()
    print("\n--- Filtering Demo ---")
    tasks[0].mark_complete()
    incomplete = scheduler.filter_tasks(tasks, completed=False)
    done = scheduler.filter_tasks(tasks, completed=True)
    print(f"  Total tasks: {len(tasks)}  |  Incomplete: {len(incomplete)}  |  Done: {len(done)}")


def main():
    owner = Owner("Jordan", available_minutes=90, start_time="08:00")

    mochi = Pet("Mochi", "dog", age=3, notes="Loves fetch")
    luna = Pet("Luna", "cat", age=5, notes="Indoor only")

    mochi_tasks = [
        Task("Morning walk", 30, "high", "walk"),
        Task("Breakfast", 10, "high", "feed", is_mandatory=True),
        Task("Playtime", 20, "medium", "enrichment"),
        Task("Grooming", 15, "low", "grooming", frequency="weekly"),
        Task("Evening meds", 5, "high", "meds", is_mandatory=True, frequency="daily"),
    ]

    luna_tasks = [
        Task("Breakfast", 5, "high", "feed", is_mandatory=True),
        Task("Litter box", 5, "high", "grooming", is_mandatory=True),
        Task("Laser pointer play", 10, "medium", "enrichment", frequency="daily"),
        Task("Brushing", 10, "low", "grooming"),
    ]

    scheduler = Scheduler()

    mochi_plan = scheduler.schedule(owner, mochi, mochi_tasks)
    luna_plan = scheduler.schedule(owner, luna, luna_tasks)

    print_plan(mochi_plan, scheduler)
    print_plan(luna_plan, scheduler)

    # Demo: adding tasks out of order and verifying sort
    print("\n--- Sorting Demo (tasks added out of order) ---")
    unsorted_plan = scheduler.schedule(
        Owner("Test", 60, "10:00"), mochi,
        [
            Task("Late task", 10, "low"),
            Task("Early task", 10, "high"),
            Task("Mid task", 10, "medium"),
        ]
    )
    sorted_tasks = scheduler.sort_by_time(unsorted_plan.scheduled)
    for st in sorted_tasks:
        print(f"  {st.start_time}  {st.task.title}")

    demo_recurrence()
    demo_filtering(mochi_tasks)


if __name__ == "__main__":
    main()
