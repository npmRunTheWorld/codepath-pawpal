# PawPal Project — CLAUDE.md

## Project Summary
- A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan


## Project Structure
- /.claude → Has all claude related files from agents, rules, to instructions
- streamlit based app and structure

---

## Git Rules
- Always branch before coding. Push initial state before changes.
- Naming: `[action]/[tag]-[number]` → e.g. `feature/ui-001`, `fix/bug-010`
- Actions: `feature` | `fix` | `refactor`
- Tags: `ui` | `bug` | `arch` | `dep`

### Completion Flow
1. Summarize: files touched, line ranges, change type (add/update/remove)
2. Run tests
3. If passing → tell user: **CHECK LOCALHOST**
4. Push branch, request PR

---

## Agents
| Agent | Role |
|---|---|
| Strategist | Writes proposals only → `/proposals/` |
| PM | Creates tickets from proposals |
| Dev | Implements one ticket at a time |
| QA | Validates and closes or fails tickets |

Agents communicate **only** via tickets and logs. No exceptions.

---

## Ticket System

### Locations
- `/tickets/open/` → `/in-progress/` → `/review/` → `/done/`

### Naming & IDs
- `feature-001.md`, `bugfix-001.md`, `task-001.md`
- Increment per type. Scan existing files to determine next ID. Never reuse.

### Priority Order: `bugfix > feature > task`

### Template
```
# [TICKET-ID] Title

| Field | Value |
|---|---|
| Type | feature / bugfix / task |
| Status | open / in-progress / review / done |
| Impact | 1–5 |
| Effort | 1–5 |
| Priority | Impact ÷ Effort |

## Description
One or two sentences max. What and why.

## Requirements
| # | Requirement |
|---|---|
| 1 | |
| 2 | |

## Acceptance Criteria
| # | Criteria | Pass? |
|---|---|---|
| 1 | | ☐ |
| 2 | | ☐ |

---

## Dev Notes
| Field | Value |
|---|---|
| Files Changed | |
| Edge Cases | |

## QA
| Field | Value |
|---|---|
| Status | PASS / FAIL / PASS_WITH_CONCERNS |
| Issues | |
| Over-engineered? | Y / N |
```

---

## Agent Workflows

### PM
1. Create ticket in `/tickets/open/`
2. Do NOT create ticket if Priority Score < 2
3. Log: ACTIVITY_LOG + CHANGELOG (Created) + `tickets/index.md`

### Dev
1. Move ticket → `/in-progress/`
2. Implement (simplest working solution — no unnecessary abstractions)
3. Fill: Implementation Notes, Files Changed, Edge Cases
4. Move → `/review/`
5. Log: ACTIVITY_LOG + CHANGELOG + `tickets/index.md`

### QA
1. Review ticket in `/review/`
2. Test against Acceptance Criteria
3. Fill QA Results
   - PASS → `/done/`
   - FAIL → `/in-progress/` (if fails twice → return to PM)
   - PASS_WITH_CONCERNS → `/done/`
4. Log: ACTIVITY_LOG + CHANGELOG + `tickets/index.md`

---

## Logging (Mandatory — skipping = invalid action)

### `/logs/CHANGELOG.md`
```
## YYYY-MM-DD
### feature-001
- Created
- Implemented: short summary
- Completed
```

### `/logs/ACTIVITY_LOG.md`
```
[HH:MM] PM → created feature-001
[HH:MM] Dev → started feature-001
[HH:MM] QA → PASS feature-001
```

### `/tickets/index.md`
```
## Open
- feature-002 → description

## In Progress
- feature-001 → description

## In Review

## Done
- feature-000 → description
```

---




## Supabase Database Migration Rules
### Never delete immediately for migrations (soft-first strategy)
   - example: DROP TABLE candles; ALTER TABLE candles RENAME TO candles_backup; ALTER TABLE candles SET SCHEMA archive;
 

## Outputs
### Claude reports
   - Any long term data that you want to share with the user, like plans, and ideas store it in the .claude/outputs directory
   - Only store information that is crucial for the user to understand, including schemas, summarized project layout, mental models, etc.

## Global Rules
- Never delete tickets. Never overwrite previous sections.
- Never mark complete without proof — validate behavior, not assumptions.
- Prefer simplest solution. Solve root cause. Minimal code impact.
- Plans go in `tasks/todo.md` before coding on non-trivial work.