"""Validation for Clarity Engine task documents."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Dict, List

REQUIRED_SECTIONS = [
    "OUTCOME",
    "REQUIREMENTS",
    "STEPS",
    "DECISIONS",
    "FAILURE POINTS",
    "COMPLETION CHECK",
]


class TaskValidationError(ValueError):
    """Raised when a task file fails schema validation."""


@dataclass(frozen=True)
class ValidationResult:
    path: Path
    task_name: str
    sections: Dict[str, str]


def _split_sections(text: str) -> Dict[str, str]:
    parts = re.split(r"(?m)^##\s+", text)
    sections: Dict[str, str] = {}
    for raw in parts[1:]:
        lines = raw.splitlines()
        if not lines:
            continue
        heading = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        sections[heading] = body
    return sections


def validate_task_text(text: str, path: Path) -> ValidationResult:
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# TASK:"):
        raise TaskValidationError(f"{path}: missing first heading '# TASK: <name>'")

    task_name = lines[0].split(":", 1)[1].strip()
    if not task_name:
        raise TaskValidationError(f"{path}: task heading has empty name")

    sections = _split_sections(text)
    missing = [section for section in REQUIRED_SECTIONS if section not in sections]
    if missing:
        raise TaskValidationError(f"{path}: missing sections: {', '.join(missing)}")

    for section_name in REQUIRED_SECTIONS:
        if not sections[section_name].strip():
            raise TaskValidationError(f"{path}: section '{section_name}' is empty")

    step_lines = [line.strip() for line in sections["STEPS"].splitlines() if line.strip()]
    numbered_steps = [line for line in step_lines if re.match(r"^\d+\.\s+", line)]
    if not numbered_steps:
        raise TaskValidationError(f"{path}: section 'STEPS' must include numbered steps")

    expected = 1
    for step in numbered_steps:
        index = int(step.split(".", 1)[0])
        if index != expected:
            raise TaskValidationError(
                f"{path}: section 'STEPS' numbering error at step {index}, expected {expected}"
            )
        expected += 1

    return ValidationResult(path=path, task_name=task_name, sections=sections)


def validate_task_file(path: Path) -> ValidationResult:
    return validate_task_text(path.read_text(encoding="utf-8"), path)
