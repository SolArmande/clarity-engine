# Clarity Engine

Clarity Engine is a **task completion engine** for practical life workflows. It defines explicit, reviewable, step-by-step task contracts so a person can reach a concrete end state without ambiguity.

It is **not** a general advice chatbot.

## Current scope

This repository currently contains baseline US task specifications for common workflows (for example, unemployment, banking, healthcare intake, and similar administrative tasks).

The current focus is:
- Clear execution over broad coverage.
- Rigid structure over free-form prose.
- Reviewable quality constraints over ad hoc writing.

## Task completion model

Every task should:
- Use a rigid markdown schema (`engine/schema.md`).
- Pass quality rules and review rubric (`engine/rules.md`).
- Be executable by a novice under stress.

## File structure

- `engine/schema.md` — required task-file contract and section semantics.
- `engine/rules.md` — writing/review quality rules and rubric.
- `*.md` (repo root, current phase) — baseline task files.

Planned structure as scope expands:

- `tasks/` — baseline task specs.
- `tasks/state_overlays/` — state-specific variants, e.g.:
  - `tasks/state_overlays/or_unemployment.md`
  - `tasks/state_overlays/ca_unemployment.md`
- `tasks/institution_overlays/` — institution-specific variants.

## Baseline vs overlays (important)

To prevent drift and duplication, task content should be split into layers:

1. **Federal/general baseline**
   - Reusable core steps and constraints.
2. **State-specific overlays**
   - Only state-dependent differences.
3. **Institution-specific variants**
   - Employer, school, hospital, or program-specific deviations.

Core files should remain baseline-first; overlays capture divergence.

## Contribution standard

When contributing:
1. Keep Clarity Engine framed as a task completion system.
2. Follow the schema exactly.
3. Enforce non-vague, atomic steps.
4. Avoid unlabeled state-specific claims in baseline files.
5. Ensure review checklist pass in `engine/rules.md`.

## Expansion roadmap

Near-term:
1. Normalize existing tasks to full schema compliance.
2. Introduce state overlay folder and first overlays.
3. Add institution overlay patterns.
4. Build a minimal CLI to list tasks and render a clean execution view.

The next implementation milestone after documentation is a small interface (CLI-first) to keep the engine testable and deterministic.
