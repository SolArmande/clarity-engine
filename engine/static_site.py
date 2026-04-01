"""Static site generator for Clarity Engine task guides."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path
import re
from typing import Dict, List

from .task_engine import TaskEngine
from .validator import validate_task_file


def _simple_markdown_to_html(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    chunks: List[str] = []
    paragraph_lines: List[str] = []
    in_ol = False
    in_ul = False

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if paragraph_lines:
            chunks.append(f"<p>{escape(' '.join(paragraph_lines))}</p>")
            paragraph_lines = []

    def close_lists() -> None:
        nonlocal in_ol, in_ul
        if in_ol:
            chunks.append("</ol>")
            in_ol = False
        if in_ul:
            chunks.append("</ul>")
            in_ul = False

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            close_lists()
            continue

        heading_match = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if heading_match:
            flush_paragraph()
            close_lists()
            level = len(heading_match.group(1))
            text = escape(heading_match.group(2))
            chunks.append(f"<h{level}>{text}</h{level}>")
            continue

        ordered_match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if ordered_match:
            flush_paragraph()
            if in_ul:
                chunks.append("</ul>")
                in_ul = False
            if not in_ol:
                chunks.append("<ol>")
                in_ol = True
            chunks.append(f"<li>{escape(ordered_match.group(2))}</li>")
            continue

        unordered_match = re.match(r"^[-*]\s+(.*)$", stripped)
        if unordered_match:
            flush_paragraph()
            if in_ol:
                chunks.append("</ol>")
                in_ol = False
            if not in_ul:
                chunks.append("<ul>")
                in_ul = True
            chunks.append(f"<li>{escape(unordered_match.group(1))}</li>")
            continue

        if in_ol:
            chunks.append("</ol>")
            in_ol = False
        if in_ul:
            chunks.append("</ul>")
            in_ul = False
        paragraph_lines.append(stripped)

    flush_paragraph()
    close_lists()

    return "\n".join(chunks)


def _build_site_data(engine: TaskEngine) -> Dict[str, Dict[str, object]]:
    tasks: Dict[str, Dict[str, object]] = {}

    for task_name in engine.discover_tasks():
        baseline_path = engine.baseline_dir / f"{task_name}.md"
        baseline_markdown = baseline_path.read_text(encoding="utf-8")
        validate_task_file(baseline_path)

        overlays: Dict[str, Dict[str, str]] = {}
        for state_dir in sorted(engine.state_overlays_dir.glob("*")):
            if not state_dir.is_dir():
                continue
            overlay_path = state_dir / f"{task_name}.md"
            if not overlay_path.exists():
                continue
            overlays[state_dir.name] = {
                "source": str(overlay_path.relative_to(engine.root)),
                "html": _simple_markdown_to_html(overlay_path.read_text(encoding="utf-8")),
            }

        tasks[task_name] = {
            "baseline_source": str(baseline_path.relative_to(engine.root)),
            "baseline_html": _simple_markdown_to_html(baseline_markdown),
            "state_overlays": overlays,
        }

    return tasks


def generate_static_site(root: Path, output_dir: Path) -> Path:
    engine = TaskEngine(root)
    site_data = _build_site_data(engine)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = json.dumps(site_data)

    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
  <title>Clarity Engine Guides</title>
  <style>
    :root {{ color-scheme: light dark; }}
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; background: #f7f7f9; color: #181a1f; }}
    .wrap {{ max-width: 880px; margin: 0 auto; padding: 1rem; }}
    .controls {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1rem; }}
    label {{ font-size: 0.9rem; font-weight: 600; display: block; margin-bottom: 0.2rem; }}
    select {{ width: 100%; font-size: 1rem; padding: 0.45rem; }}
    .panel {{ background: white; border-radius: 8px; padding: 1rem; box-shadow: 0 2px 10px rgba(0,0,0,.07); }}
    .section {{ margin-bottom: 1.2rem; }}
    .overlay-title {{ border-top: 1px solid #d9dce3; padding-top: 1rem; }}
    .meta {{ color: #596275; font-size: 0.85rem; margin-top: .2rem; }}
    h1 {{ font-size: 1.4rem; margin-top: 0; }}
    @media (max-width: 680px) {{ .controls {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <h1>Clarity Engine Task Guides</h1>
    <p>Public static view of baseline task guides with optional state overlays.</p>

    <div class=\"controls\">
      <div>
        <label for=\"taskSelect\">Task</label>
        <select id=\"taskSelect\"></select>
      </div>
      <div>
        <label for=\"stateSelect\">State overlay (optional)</label>
        <select id=\"stateSelect\"></select>
      </div>
    </div>

    <div class=\"panel\">
      <section class=\"section\">
        <h2>Baseline</h2>
        <div id=\"baselineSource\" class=\"meta\"></div>
        <div id=\"baselineContent\"></div>
      </section>

      <section class=\"section\" id=\"overlaySection\" hidden>
        <h2 class=\"overlay-title\">State Overlay</h2>
        <div id=\"overlaySource\" class=\"meta\"></div>
        <div id=\"overlayContent\"></div>
      </section>
    </div>
  </div>

  <script>
    const DATA = {payload};
    const taskSelect = document.getElementById('taskSelect');
    const stateSelect = document.getElementById('stateSelect');
    const baselineSource = document.getElementById('baselineSource');
    const baselineContent = document.getElementById('baselineContent');
    const overlaySection = document.getElementById('overlaySection');
    const overlaySource = document.getElementById('overlaySource');
    const overlayContent = document.getElementById('overlayContent');

    const tasks = Object.keys(DATA).sort();
    for (const task of tasks) {{
      const option = document.createElement('option');
      option.value = task;
      option.textContent = task;
      taskSelect.appendChild(option);
    }}

    function render() {{
      const task = taskSelect.value;
      const record = DATA[task];
      baselineSource.textContent = `Source: ${{record.baseline_source}}`;
      baselineContent.innerHTML = record.baseline_html;

      const overlays = record.state_overlays;
      stateSelect.innerHTML = '';

      const noneOpt = document.createElement('option');
      noneOpt.value = '';
      noneOpt.textContent = 'None';
      stateSelect.appendChild(noneOpt);

      for (const stateCode of Object.keys(overlays).sort()) {{
        const option = document.createElement('option');
        option.value = stateCode;
        option.textContent = stateCode.toUpperCase();
        stateSelect.appendChild(option);
      }}

      updateOverlay();
    }}

    function updateOverlay() {{
      const task = taskSelect.value;
      const state = stateSelect.value;
      const overlays = DATA[task].state_overlays;
      const record = overlays[state];

      if (!record) {{
        overlaySection.hidden = true;
        overlaySource.textContent = '';
        overlayContent.innerHTML = '';
        return;
      }}

      overlaySection.hidden = false;
      overlaySource.textContent = `Source: ${{record.source}}`;
      overlayContent.innerHTML = record.html;
    }}

    taskSelect.addEventListener('change', render);
    stateSelect.addEventListener('change', updateOverlay);

    if (tasks.length > 0) {{
      taskSelect.value = tasks[0];
      render();
    }}
  </script>
</body>
</html>
"""

    out_file = output_dir / "index.html"
    out_file.write_text(html, encoding="utf-8")
    return out_file
