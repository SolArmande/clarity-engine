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
    .wrap {{ max-width: 980px; margin: 0 auto; padding: 1rem; }}
    .controls {{ display: grid; grid-template-columns: 1fr; gap: 0.75rem; margin-bottom: 1rem; }}
    label {{ font-size: 0.9rem; font-weight: 600; display: block; margin-bottom: 0.25rem; }}
    select, input, textarea, button {{ width: 100%; font-size: 1rem; padding: 0.6rem; border-radius: 8px; border: 1px solid #cfd5df; box-sizing: border-box; }}
    textarea {{ min-height: 6rem; resize: vertical; }}
    button {{ cursor: pointer; background: #2d5fff; color: #fff; border: none; font-weight: 600; }}
    button.secondary {{ background: #eef2ff; color: #213174; border: 1px solid #c8d2ff; }}
    .panel {{ background: white; border-radius: 10px; padding: 1rem; box-shadow: 0 2px 10px rgba(0,0,0,.07); }}
    .section {{ margin-bottom: 1.2rem; }}
    .overlay-title {{ border-top: 1px solid #d9dce3; padding-top: 1rem; }}
    .meta {{ color: #596275; font-size: 0.85rem; margin-top: .2rem; }}
    .small {{ font-size: 0.9rem; color: #4e5565; }}
    h1 {{ font-size: 1.4rem; margin-top: 0; }}
    h2 {{ font-size: 1.15rem; }}
    .resume-flow {{ display: none; gap: 1rem; }}
    .resume-grid {{ display: grid; grid-template-columns: 1fr; gap: 1rem; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0.5rem 0 0.75rem; }}
    .chip {{ width: auto; border-radius: 999px; padding: 0.35rem 0.65rem; font-size: 0.85rem; }}
    .experience-card {{ border: 1px solid #e1e5ee; border-radius: 8px; padding: 0.75rem; margin-bottom: 0.75rem; }}
    .resume-preview {{ background: #fff; border: 1px solid #d9dce3; border-radius: 8px; padding: 1rem; min-height: 320px; }}
    .resume-preview h3 {{ margin: 0 0 .2rem; font-size: 1.15rem; }}
    .preview-section {{ margin-top: 0.75rem; }}
    .preview-section h4 {{ margin: 0 0 .3rem; font-size: 0.9rem; text-transform: uppercase; letter-spacing: .04em; }}
    .preview-list {{ margin: 0; padding-left: 1.1rem; }}
    .export-box {{ margin-top: 1rem; border-top: 1px solid #d9dce3; padding-top: 0.75rem; }}
    @media (min-width: 860px) {{
      .controls {{ grid-template-columns: 1fr 1fr; }}
      .resume-grid {{ grid-template-columns: 1fr 1fr; }}
    }}
    @media print {{
      body {{ background: #fff; }}
      .controls, .meta, .small, #guidePanel, .export-box button {{ display: none !important; }}
      .panel {{ box-shadow: none; border: none; padding: 0; }}
      .resume-flow {{ display: block !important; }}
      .resume-preview {{ border: none; padding: 0; }}
    }}
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

    <div class=\"panel\" id=\"guidePanel\">
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

    <div class=\"panel resume-flow\" id=\"resumeFlow\" aria-live=\"polite\">
      <h2>Build your resume on this page</h2>
      <p class=\"small\">Phone-first flow: fill the fields, review the one-page preview, then use your phone browser's Share/Print action to save as PDF.</p>

      <div class=\"resume-grid\">
        <section>
          <label for=\"fullName\">Full name</label>
          <input id=\"fullName\" placeholder=\"Jordan Lee\" />

          <label for=\"phone\">Phone</label>
          <input id=\"phone\" placeholder=\"(555) 123-4567\" />

          <label for=\"email\">Email</label>
          <input id=\"email\" placeholder=\"jordan.lee@email.com\" />

          <label for=\"cityState\">City / State</label>
          <input id=\"cityState\" placeholder=\"Austin, TX\" />

          <div id=\"skillsBlock\"></div>
          <div id=\"experienceBlock\"></div>

          <label for=\"education\">Education</label>
          <textarea id=\"education\" placeholder=\"Austin Community College — Associate of Applied Science, 2023, Austin, TX\"></textarea>
        </section>

        <section>
          <div class=\"resume-preview\" id=\"resumePreview\"></div>
          <div class=\"export-box\">
            <h3>Export options</h3>
            <p class=\"small\">Print-friendly layout is built in. On mobile, tap <strong>Share</strong> or <strong>Print</strong> in your browser, then choose <strong>Save as PDF</strong>.</p>
            <button id=\"printBtn\">Print / Save as PDF</button>
          </div>
        </section>
      </div>
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
    const guidePanel = document.getElementById('guidePanel');
    const resumeFlow = document.getElementById('resumeFlow');

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

      const isResumeTask = task === 'resume';
      guidePanel.style.display = isResumeTask ? 'none' : 'block';
      resumeFlow.style.display = isResumeTask ? 'grid' : 'none';

      updateOverlay();
      if (isResumeTask) {{
        renderResumePreview();
      }}
    }}

    function updateOverlay() {{
      const task = taskSelect.value;
      const state = stateSelect.value;
      const overlays = DATA[task].state_overlays;
      const record = overlays[state];

      if (!record || task === 'resume') {{
        overlaySection.hidden = true;
        overlaySource.textContent = '';
        overlayContent.innerHTML = '';
        return;
      }}

      overlaySection.hidden = false;
      overlaySource.textContent = `Source: ${{record.source}}`;
      overlayContent.innerHTML = record.html;
    }}

    function buildSkillInputs() {{
      const skillsBlock = document.getElementById('skillsBlock');
      skillsBlock.innerHTML = '<label>Skills (3 to 5)</label>';
      for (let i = 0; i < 5; i += 1) {{
        const input = document.createElement('input');
        input.id = `skill${{i + 1}}`;
        input.placeholder = ['Customer service', 'Cash handling', 'Inventory tracking', 'Team collaboration', 'POS systems'][i];
        input.addEventListener('input', renderResumePreview);
        skillsBlock.appendChild(input);
      }}
    }}

    function buildExperienceInputs() {{
      const starters = [
        'Assisted 40+ customers per shift while maintaining friendly service.',
        'Reduced wait times by organizing daily task priorities.',
        'Trained 3 new team members on standard operating procedures.',
        'Maintained accurate records with strong attention to detail.'
      ];
      const expBlock = document.getElementById('experienceBlock');
      expBlock.innerHTML = '<label>Experience (1 to 3 entries)</label>';

      for (let i = 0; i < 3; i += 1) {{
        const card = document.createElement('div');
        card.className = 'experience-card';
        card.innerHTML = `
          <label for=\"jobTitle${{i}}\">Job title</label>
          <input id=\"jobTitle${{i}}\" placeholder=\"Store Associate\" />
          <label for=\"company${{i}}\">Company + dates</label>
          <input id=\"company${{i}}\" placeholder=\"Bright Market — Jan 2023 to Feb 2026\" />
          <label for=\"jobLocation${{i}}\">City / State</label>
          <input id=\"jobLocation${{i}}\" placeholder=\"Austin, TX\" />
          <label for=\"bullets${{i}}\">Bullet points (one per line)</label>
          <textarea id=\"bullets${{i}}\" placeholder=\"Helped customers find products quickly.\"></textarea>
          <div class=\"chips\" id=\"chips${{i}}\"></div>
        `;
        expBlock.appendChild(card);

        for (const line of starters) {{
          const chip = document.createElement('button');
          chip.type = 'button';
          chip.className = 'secondary chip';
          chip.textContent = line;
          chip.addEventListener('click', () => {{
            const bulletField = document.getElementById(`bullets${{i}}`);
            bulletField.value = bulletField.value ? `${{bulletField.value}}\\n${{line}}` : line;
            renderResumePreview();
          }});
          card.querySelector(`#chips${{i}}`).appendChild(chip);
        }}

        for (const field of card.querySelectorAll('input, textarea')) {{
          field.addEventListener('input', renderResumePreview);
        }}
      }}
    }}

    function asListLines(value) {{
      return value.split('\\n').map((line) => line.trim()).filter(Boolean);
    }}

    function renderResumePreview() {{
      const preview = document.getElementById('resumePreview');
      const fullName = document.getElementById('fullName').value.trim();
      const phone = document.getElementById('phone').value.trim();
      const email = document.getElementById('email').value.trim();
      const cityState = document.getElementById('cityState').value.trim();

      const skills = [];
      for (let i = 1; i <= 5; i += 1) {{
        const value = document.getElementById(`skill${{i}}`).value.trim();
        if (value) skills.push(value);
      }}

      const experiences = [];
      for (let i = 0; i < 3; i += 1) {{
        const jobTitle = document.getElementById(`jobTitle${{i}}`).value.trim();
        const company = document.getElementById(`company${{i}}`).value.trim();
        const jobLocation = document.getElementById(`jobLocation${{i}}`).value.trim();
        const bullets = asListLines(document.getElementById(`bullets${{i}}`).value);
        if (jobTitle || company || jobLocation || bullets.length > 0) {{
          experiences.push({{ jobTitle, company, jobLocation, bullets }});
        }}
      }}

      const education = document.getElementById('education').value.trim();

      preview.innerHTML = `
        <h3>${{fullName || 'Your Name'}}</h3>
        <div class=\"small\">${{[phone || '(555) 123-4567', email || 'you@email.com', cityState || 'City, ST'].join(' • ')}}</div>

        <div class=\"preview-section\">
          <h4>Skills</h4>
          <p>${{skills.length ? skills.join(' • ') : 'Add 3 to 5 skills relevant to the job.'}}</p>
        </div>

        <div class=\"preview-section\">
          <h4>Experience</h4>
          ${{experiences.length ? experiences.map((exp) => `
            <div>
              <strong>${{exp.jobTitle || 'Job Title'}}</strong><br />
              <span>${{[exp.company, exp.jobLocation].filter(Boolean).join(' • ')}}</span>
              <ul class=\"preview-list\">${{exp.bullets.map((line) => `<li>${{line}}</li>`).join('') || '<li>Add at least one result-focused bullet.</li>'}}</ul>
            </div>
          `).join('') : '<p>Add 1 to 3 experience entries.</p>'}}
        </div>

        <div class=\"preview-section\">
          <h4>Education</h4>
          <p>${{education || 'School — Credential, Year, City, State'}}</p>
        </div>
      `;
    }}

    document.getElementById('printBtn').addEventListener('click', () => window.print());
    for (const id of ['fullName', 'phone', 'email', 'cityState', 'education']) {{
      document.getElementById(id).addEventListener('input', renderResumePreview);
    }}

    buildSkillInputs();
    buildExperienceInputs();
    taskSelect.addEventListener('change', render);
    stateSelect.addEventListener('change', updateOverlay);

    if (tasks.length > 0) {{
      taskSelect.value = tasks.includes('resume') ? 'resume' : tasks[0];
      render();
    }}
  </script>
</body>
</html>
"""

    out_file = output_dir / "index.html"
    out_file.write_text(html, encoding="utf-8")
    return out_file
