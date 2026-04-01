"""Core loading and composition logic for Clarity Engine tasks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .validator import ValidationResult, validate_task_file


@dataclass(frozen=True)
class LoadedTask:
    task_name: str
    baseline_path: Path
    baseline: ValidationResult
    state_overlay: Optional[ValidationResult]
    institution_overlay: Optional[ValidationResult]

    @property
    def composed_text(self) -> str:
        chunks: List[str] = [self.baseline_path.read_text(encoding="utf-8").strip()]
        if self.state_overlay:
            chunks.append(
                "\n\n---\n"
                f"## OVERLAY: STATE ({self.state_overlay.path.parent.name.upper()})\n\n"
                f"Source: {self.state_overlay.path}\n\n"
                f"{self.state_overlay.path.read_text(encoding='utf-8').strip()}"
            )
        if self.institution_overlay:
            chunks.append(
                "\n\n---\n"
                f"## OVERLAY: INSTITUTION ({self.institution_overlay.path.parent.name})\n\n"
                f"Source: {self.institution_overlay.path}\n\n"
                f"{self.institution_overlay.path.read_text(encoding='utf-8').strip()}"
            )
        return "\n".join(chunks)


class TaskEngine:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.tasks_dir = root / "tasks"
        self.baseline_dir = self.tasks_dir / "baseline"
        self.state_overlays_dir = self.tasks_dir / "state_overlays"
        self.institution_overlays_dir = self.tasks_dir / "institution_overlays"

    def discover_tasks(self) -> List[str]:
        if not self.baseline_dir.exists():
            return []
        return sorted(path.stem for path in self.baseline_dir.glob("*.md"))

    def _baseline_path(self, task: str) -> Path:
        return self.baseline_dir / f"{task}.md"

    def _overlay_path(self, folder: Path, overlay_name: str, task: str) -> Path:
        return folder / overlay_name / f"{task}.md"

    def load_task(
        self,
        task: str,
        *,
        state: Optional[str] = None,
        institution: Optional[str] = None,
    ) -> LoadedTask:
        baseline_path = self._baseline_path(task)
        if not baseline_path.exists():
            available = ", ".join(self.discover_tasks()) or "(none)"
            raise FileNotFoundError(f"Unknown task '{task}'. Available tasks: {available}")

        baseline = validate_task_file(baseline_path)

        state_overlay = None
        if state:
            state_path = self._overlay_path(self.state_overlays_dir, state.lower(), task)
            if state_path.exists():
                state_overlay = validate_task_file(state_path)

        institution_overlay = None
        if institution:
            inst_path = self._overlay_path(self.institution_overlays_dir, institution.lower(), task)
            if inst_path.exists():
                institution_overlay = validate_task_file(inst_path)

        return LoadedTask(
            task_name=task,
            baseline_path=baseline_path,
            baseline=baseline,
            state_overlay=state_overlay,
            institution_overlay=institution_overlay,
        )


def extract_numbered_steps(markdown_text: str) -> List[str]:
    in_steps = False
    steps: List[str] = []
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if stripped == "## STEPS":
            in_steps = True
            continue
        if in_steps and stripped.startswith("## "):
            break
        if in_steps and stripped and stripped[0].isdigit() and ". " in stripped:
            steps.append(stripped.split(". ", 1)[1])
    return steps
