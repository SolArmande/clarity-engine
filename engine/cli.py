"""Command-line interface for Clarity Engine."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .task_engine import TaskEngine, extract_numbered_steps
from .validator import TaskValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="clarity",
        description="Clarity Engine: a task completion engine.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate task file schema.")
    validate.add_argument("task", nargs="?", help="Task name to validate. If omitted, validate all baseline tasks.")
    validate.add_argument("--state", help="Optional state overlay code (e.g. ca, ny).")
    validate.add_argument("--institution", help="Optional institution overlay name.")

    run = subparsers.add_parser("run", help="Run a task in terminal step-by-step mode.")
    run.add_argument("task", help="Task name to run.")
    run.add_argument("--state", help="Optional state overlay code (e.g. ca, ny).")
    run.add_argument("--institution", help="Optional institution overlay name.")

    return parser


def cmd_validate(engine: TaskEngine, task: str | None, state: str | None, institution: str | None) -> int:
    tasks = [task] if task else engine.discover_tasks()
    if not tasks:
        print("No tasks found in tasks/baseline/.", file=sys.stderr)
        return 1

    failed = False
    for task_name in tasks:
        try:
            loaded = engine.load_task(task_name, state=state, institution=institution)
            print(f"OK baseline: {loaded.baseline.path}")
            if state:
                if loaded.state_overlay:
                    print(f"OK state overlay: {loaded.state_overlay.path}")
                else:
                    print(f"SKIP state overlay: no file for --state {state}")
            if institution:
                if loaded.institution_overlay:
                    print(f"OK institution overlay: {loaded.institution_overlay.path}")
                else:
                    print(f"SKIP institution overlay: no file for --institution {institution}")
        except (FileNotFoundError, TaskValidationError) as exc:
            failed = True
            print(f"FAIL {task_name}: {exc}", file=sys.stderr)

    return 1 if failed else 0


def cmd_run(engine: TaskEngine, task: str, state: str | None, institution: str | None) -> int:
    loaded = engine.load_task(task, state=state, institution=institution)
    steps = extract_numbered_steps(loaded.baseline.path.read_text(encoding="utf-8"))
    if not steps:
        raise TaskValidationError(f"{loaded.baseline.path}: no runnable steps found")

    print(f"TASK: {loaded.baseline.task_name}")
    print(f"Baseline source: {loaded.baseline.path}")
    if state:
        if loaded.state_overlay:
            print(f"State overlay loaded: {loaded.state_overlay.path}")
        else:
            print(f"State overlay not found for '{state}'.")
    if institution:
        if loaded.institution_overlay:
            print(f"Institution overlay loaded: {loaded.institution_overlay.path}")
        else:
            print(f"Institution overlay not found for '{institution}'.")

    if not _wait_for_enter("\nPress Enter to begin... "):
        print("\nRun cancelled.")
        return 1
    for idx, step in enumerate(steps, start=1):
        print(f"\nStep {idx}: {step}")
        if not _wait_for_enter("Press Enter for next step..."):
            print("\nRun cancelled.")
            return 1

    print("\nAll baseline steps displayed.")

    if loaded.state_overlay:
        print("\nState overlay guidance is available in composed output via validator/load APIs.")
    if loaded.institution_overlay:
        print("Institution overlay guidance is available in composed output via validator/load APIs.")
    return 0


def _wait_for_enter(prompt: str) -> bool:
    try:
        input(prompt)
        return True
    except (EOFError, KeyboardInterrupt):
        return False


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    engine = TaskEngine(Path(__file__).resolve().parent.parent)

    try:
        if args.command == "validate":
            return cmd_validate(engine, args.task, args.state, args.institution)
        if args.command == "run":
            return cmd_run(engine, args.task, args.state, args.institution)
    except (FileNotFoundError, TaskValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.error(f"Unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
