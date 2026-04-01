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
  cli.py                    # package CLI command implementation
cli.py                      # thin root entrypoint (developer-facing)
```

## Normalized task discovery

Task discovery is baseline-first:

- Baseline task files are discovered only from `tasks/baseline/*.md`.
- Optional overlays are discovered only when requested with flags.
- Missing overlay files are handled explicitly and never merged silently.

## CLI usage

Use the root-level entrypoint for the simplest developer workflow:

```bash
python cli.py list
python cli.py open unemployment
python cli.py validate
python cli.py run unemployment --state or
```

You can still run the package module style if desired:

```bash
python -m engine list
python -m engine open unemployment
python -m engine validate unemployment --state ca --institution acme_bank
python -m engine run unemployment --state ca
```

## Validation

Use validator mode to catch malformed task files quickly.

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

Run mode provides a standard-library-only step-by-step terminal flow.

Behavior:

- Loads and validates the baseline task first.
- Reports whether requested overlays are found.
- Walks through baseline steps interactively, one step at a time.

## No external dependencies

Clarity Engine uses only Python standard library modules.
