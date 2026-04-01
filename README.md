# Clarity Engine

Clarity Engine is a **task completion engine**. It loads structured task files, validates them against a strict schema, and runs baseline steps in a simple terminal flow.

It is not a chatbot.

## Repository structure

```text
tasks/
  baseline/                 # canonical task files
  state_overlays/           # optional state-specific overlays
    <state_code>/
      <task>.md
  institution_overlays/     # optional institution-specific overlays
    <institution_name>/
      <task>.md
engine/
  task_engine.py            # task discovery + loading logic
  validator.py              # strict schema validation
  cli.py                    # CLI commands (validate, run)
```

## Normalized task discovery

Task discovery is baseline-first:

- Baseline task files are discovered only from `tasks/baseline/*.md`.
- Optional overlays are discovered only when requested with flags.
- Missing overlay files are handled explicitly and never merged silently.

## Validation

Use validator mode to catch malformed task files quickly.

```bash
python -m engine validate
python -m engine validate unemployment
python -m engine validate unemployment --state ca --institution acme_bank
```

Validation guarantees:

- First heading must be `# TASK: <name>`.
- Required sections must exist and be non-empty.
- `## STEPS` must contain sequential numbered steps.
- Errors are explicit and include file paths.

## Overlay strategy

Overlays are optional and append-only.

- Baseline content remains distinct.
- State and institution overlays are loaded only if corresponding files exist.
- Overlays are clearly labeled when composed in engine output.
- No silent baseline/overlay claim mixing.

Naming conventions:

- State overlays: `tasks/state_overlays/<state_code>/<task>.md` (e.g. `ca/unemployment.md`)
- Institution overlays: `tasks/institution_overlays/<institution_name>/<task>.md`

## Run mode

Run mode provides a standard-library-only step-by-step terminal flow:

```bash
python -m engine run unemployment
python -m engine run unemployment --state ca
python -m engine run unemployment --state ca --institution acme_bank
```

Behavior:

- Loads and validates the baseline task first.
- Reports whether requested overlays are found.
- Walks through baseline steps interactively, one step at a time.

## No external dependencies

Clarity Engine uses only Python standard library modules.
