# Clarity Engine

Clarity Engine is a mobile-first guided completion system for high-friction public-service tasks, with an embedded reality layer that helps users decide and prepare before acting.
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
  static_site.py            # static HTML generator for public guides
  cli.py                    # package CLI command implementation
cli.py                      # thin root entrypoint (developer-facing)
site/                       # generated public static site output (by CLI)
```

## Interfaces: developer vs public

- **Developer interface (internal):** the CLI used for authoring, validation, and internal run-mode workflows.
- **Public interface:** generated static web site (`site/index.html`) that exposes readable task guides without requiring Python tooling.

## Normalized task discovery

Task discovery is baseline-first:

- Baseline task files are discovered only from `tasks/baseline/*.md`.
- Optional overlays are discovered only when requested with flags (CLI) or selected in the generated site.
- Missing overlay files are handled explicitly and never merged silently.

## Internal CLI usage

Use the root-level entrypoint for the simplest developer workflow:

```bash
python cli.py list
python cli.py open unemployment
python cli.py validate
python cli.py run unemployment --state or
python cli.py build-site
```

You can still run the package module style if desired:

```bash
python -m engine list
python -m engine open unemployment
python -m engine validate unemployment --state ca --institution acme_bank
python -m engine run unemployment --state ca
python -m engine build-site --output site
```

## Static site generation and preview

Generate the public static interface:

```bash
python cli.py build-site --output site
```

Preview locally (no extra dependencies):

```bash
python -m http.server --directory site 8000
```

Then open `http://localhost:8000` in a browser.

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
- Overlays are clearly labeled when composed in engine output and in public static output.
- No silent baseline/overlay claim mixing.

Naming conventions:

- State overlays: `tasks/state_overlays/<state_code>/<task>.md` (e.g. `or/unemployment.md`)
- Institution overlays: `tasks/institution_overlays/<institution_name>/<task>.md`

## Run mode

Run mode provides a standard-library-only step-by-step terminal flow.

Behavior:

- Loads and validates the baseline task first.
- Reports whether requested overlays are found.
- Walks through baseline steps interactively, one step at a time.

## No external dependencies

Clarity Engine uses only Python standard library modules.
