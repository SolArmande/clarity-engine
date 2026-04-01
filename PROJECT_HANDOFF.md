# CLARITY ENGINE — PROJECT HANDOFF

## PROJECT PURPOSE

Clarity Engine is a **task completion system**, not a chatbot.

It converts real-world processes into:

* structured
* atomic
* executable steps

Goal:
Enable a user to **complete a task without confusion or external help**.

---

## CURRENT ARCHITECTURE

### 1. Content Layer

Location:

```
/tasks/baseline/
/tasks/state_overlays/
/tasks/institution_overlays/
```

* Baseline = US general process
* Overlays = state/institution-specific modifications
* Strict schema enforced

---

### 2. Schema (MANDATORY)

Each task follows:

* OUTCOME
* REQUIREMENTS
* STEPS (atomic, numbered)
* DECISIONS (if/then only)
* FAILURE POINTS
* COMPLETION CHECK

Rules:

* No fluff
* No vague verbs
* No combined actions
* Must be executable under stress

---

### 3. Engine Layer

Location:

```
/engine/
```

Components:

* `task_engine.py` → discovery + composition
* `validator.py` → schema enforcement
* `static_site.py` → public interface generator

Key behavior:

* Baseline and overlays are NEVER merged silently
* Overlays are appended and explicitly labeled

---

### 4. CLI (Internal Tooling)

Entry:

```
cli.py
```

Commands:

```
python cli.py list
python cli.py open <task>
python cli.py validate [task]
python cli.py run <task> [--state <code>]
python cli.py build-site --output site
```

Purpose:

* validation
* testing
* development

NOT for end users.

---

### 5. Public Interface

Generated:

```
/site/index.html
```

Properties:

* zero-install
* mobile-friendly
* baseline + optional overlay display
* deep-link support
* copy + print support
* feedback entry point

---

## CURRENT STATE (IMPORTANT)

System is:

* structurally complete
* internally validated
* publicly viewable

System is NOT yet:

* user-validated
* correctness-proven
* production-ready

---

## CURRENT PRIORITY

### Transition from BUILD → VALIDATION

Goal:

> One real user successfully completes one real task.

---

## NEXT EXECUTION PLAN

### Phase 1: UI Hardening (DONE)

* metadata display
* deep linking
* copy/print
* feedback entry

---

### Phase 2: First Production Task

Selected task:

```
resume.md
```

Reason:

* low risk
* broad applicability
* easier validation
* faster iteration

---

## NEXT TASK (IMMEDIATE)

### Refine resume.md to production quality

Requirements:

* remove ambiguity
* ensure atomic steps
* validate requirements completeness
* ensure completion check is verifiable
* add metadata (frontmatter optional)

Acceptance test:

> A user with no resume can complete one without asking questions

---

## USER ACQUISITION STRATEGY

DO NOT:

* ask users to run Python
* expose repo
* require setup

USE:

* direct link to static site
* mobile-first interaction

---

### Initial Channels

1. Personal contacts (preferred)
2. Online communities (secondary)
3. Direct outreach with link

---

## FEEDBACK MODEL

Capture:

* where user hesitates
* where user asks questions
* where steps fail

Rule:

> User confusion = system failure

---

## NEXT EXPANSION (AFTER FIRST SUCCESS)

1. Refine schema based on failure points
2. Improve validator rules
3. Add second validated task
4. Return to:

   * unemployment (with overlay system)
   * higher complexity domains

---

## NON-NEGOTIABLE PRINCIPLES

* This is NOT an AI assistant
* This is NOT advice
* This is NOT educational content

This is:

> **execution infrastructure for humans**

---

## FAILURE CONDITIONS

System fails if:

* user must interpret steps
* user must guess next action
* steps combine multiple actions
* instructions are context-dependent but unstated

---

## SUCCESS CONDITION

System succeeds when:

> A stressed, inexperienced user can complete a task without asking for help.

---

## CURRENT RISKS

* false confidence (structure ≠ correctness)
* lack of real-world testing
* hidden ambiguity in steps
* over-expansion before validation

---

## NEXT OPERATOR INSTRUCTIONS

1. Do NOT add new features yet

2. Do NOT expand task list

3. Focus only on:

   * resume.md refinement
   * real user test

4. After first real test:

   * report failure points
   * iterate system

---

## OPTIONAL FUTURE (DO NOT EXECUTE YET)

* automation (OpenClaw / API)
* large-scale generation
* integration with external systems

These are unlocked ONLY after:

* repeatable success patterns exist

---

## FINAL NOTE

This project is now in the only phase that matters:

**contact with reality**

Do not leave this phase prematurely.
