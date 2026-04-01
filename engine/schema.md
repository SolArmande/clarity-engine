# Clarity Engine Task Schema (v1)

This document defines the **required Markdown contract** for every task file in this repository.

Clarity Engine is a **task completion system**. A task file is an execution plan, not open-ended advice.

## Required section order

Every task file MUST contain these sections in this exact order:

1. `# TASK: <name>`
2. `## PURPOSE`
3. `## SCOPE`
4. `## REQUIREMENTS`
5. `## STEPS`
6. `## DECISIONS` (optional; allowed only under strict conditions below)
7. `## OUTPUTS`
8. `## COMPLETION CRITERIA`

If `## DECISIONS` is omitted, section numbering/order still remains otherwise unchanged.

---

## Section contract

### `# TASK: <name>`
- **Meaning:** Unique task identity.
- **Allowed:** A concrete title describing one outcome.
- **Forbidden:** Vague titles (e.g., "Help with paperwork").

### `## PURPOSE`
- **Meaning:** One short paragraph defining the end state the user is trying to reach.
- **Allowed:** Outcome language tied to observable completion.
- **Forbidden:** General life advice, motivational language, policy commentary.

### `## SCOPE`
- **Meaning:** Boundaries of what this task covers and excludes.
- **Allowed:** Explicit in-scope and out-of-scope bullets.
- **Forbidden:** Hidden assumptions, implied jurisdiction rules, unstated dependencies.

### `## REQUIREMENTS`
- **Meaning:** Inputs and preconditions required before execution.
- **Allowed:** Specific documents, data, accounts, deadlines, and constraints.
- **Forbidden:** Nice-to-have items presented as required, unclear requirements.

### `## STEPS`
- **Meaning:** Ordered execution sequence from start to finish.
- **Allowed:** Numbered steps using concrete verbs and expected artifacts.
- **Forbidden:** Non-actionable instructions, bundled actions, ambiguous ownership.

### `## DECISIONS` (optional)
- **Meaning:** Minimal branching needed when materially different paths exist.
- **Allowed only when all are true:**
  1. A real branch changes at least one later required step.
  2. The branch condition is objectively testable by a novice.
  3. No more than the minimum set of branches needed to proceed safely.
- **Forbidden:** Preference trees, speculative what-ifs, policy/legal analysis, state-by-state branching in baseline files.

### `## OUTPUTS`
- **Meaning:** Tangible artifacts produced by completion.
- **Allowed:** Filed forms, confirmation numbers, submitted packets, saved records.
- **Forbidden:** Intangible outcomes only (e.g., "better prepared").

### `## COMPLETION CRITERIA`
- **Meaning:** Binary checklist defining done/not-done status.
- **Allowed:** Verifiable items mapped to requirements and outputs.
- **Forbidden:** Soft claims like "should be fine" or "probably complete".

---

## Atomic step rule (mandatory)

Each item in `## STEPS` must be atomic:

- One actor performs one concrete action on one object.
- The action has one clear completion signal.
- If a step contains "and", it is likely multiple steps and must be split.

**Good:** "Upload identity document to the claim portal."  
**Bad:** "Collect documents and upload them and follow up if needed."

---

## Allowed and forbidden content (global)

### Allowed
- Plain-language instructions that a novice can execute.
- Jurisdiction-neutral baseline guidance in core task files.
- Explicit references to overlays when regional/institutional variants exist.

### Forbidden
- Legal/medical guarantees.
- State-specific operational claims in baseline task files.
- Institution-specific procedures in baseline task files.
- Vague verbs (e.g., handle, deal with, manage, follow up) without concrete action.

---

## What counts as completion

A task is complete only when:

1. Every required item in `## REQUIREMENTS` is satisfied or explicitly marked unavailable with a fallback path.
2. Every `## STEPS` item is executed or explicitly skipped under a valid decision branch.
3. Every required artifact in `## OUTPUTS` exists.
4. Every checkbox in `## COMPLETION CRITERIA` can be marked true with evidence.

If any criterion fails, the task is not complete.
