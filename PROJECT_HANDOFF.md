# CLARITY ENGINE — PROJECT HANDOFF

## System Definition

Clarity Engine is a **task completion system** (not a chatbot).

It converts real-world processes into:

- structured
- atomic
- executable steps

Primary goal: a user can complete a task without confusion or external help.

## Architecture (Current)

### Content Layer

- `tasks/baseline/` → canonical, jurisdiction-neutral task files
- `tasks/state_overlays/` → optional state-specific overlays
- `tasks/institution_overlays/` → optional institution-specific overlays

### Engine Layer (`engine/`)

- task discovery/composition
- schema/quality validation
- static site generation

### Interfaces

- Internal developer interface: CLI (`cli.py`)
- Public user interface: generated static site (`site/index.html`)

## Operational Constraints

- Baseline and overlays are never merged silently.
- Overlays are optional and explicitly labeled.
- Task steps must remain atomic and executable under stress.

## Read This With

- `docs/market-and-scope.md` for market, wedge, and non-goals.
- `docs/current-focus.md` for only the active execution focus.
