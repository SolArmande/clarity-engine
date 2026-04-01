# Clarity Engine Quality Rules (v1)

These rules define quality constraints for all task specifications.

## Core framing

- Clarity Engine is a **task completion engine**, not a chatbot or general advice system.
- Task files must optimize for execution reliability, not conversational breadth.

## Safety and claim constraints

1. **No legal or medical guarantees.**
   - Do not promise legal outcomes, eligibility, approvals, or clinical results.
2. **No unlabeled state-specific claims.**
   - Baseline files must remain federal/general where possible.
   - If state-specific content is necessary, label it clearly and move it to an overlay file.
3. **No institution-specific assumptions in baseline.**
   - Employer/school/hospital/program variants belong in institution overlays.

## Language precision constraints

1. Ban vague verbs unless made concrete.
   - Disallowed by default: "handle," "deal with," "follow up," "take care of," "manage," "work on."
   - Replace with explicit actions, object, and completion signal.
2. Every requirement must be actually required.
   - If a user can complete the task without it, it is optional and must be labeled optional.
3. Every step must be atomic.
   - One actor, one action, one object, one completion signal.

## Stress-proof and beginner-safe standard

Every task must be written so that a stressed novice can execute it without guessing.

Minimum bar:
- Terms are plain language or briefly defined.
- Hidden assumptions are surfaced in `REQUIREMENTS` or `DECISIONS`.
- Each step has an observable end condition.
- Branching is minimal and objectively testable.

## Reviewability standard

Each task must be auditable against a checklist. A reviewer should be able to mark pass/fail per criterion without interpretation drift.

## Review rubric

Use this checklist for PR review and periodic audits:

1. Is every step executable as written?
2. Is any step combining multiple actions?
3. Is any required section missing from the schema?
4. Are requirements truly required (not just useful)?
5. Are decision branches minimal and objectively testable?
6. Can a novice complete this without guessing?
7. Are baseline files free of unlabeled state-specific claims?
8. Are legal/medical guarantees absent?
