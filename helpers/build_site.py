#!/usr/bin/env python3
"""Build a static OSC&R website from YAML content into docs/ (GitHub Pages)."""

from __future__ import annotations

import glob
import html
import json
import os
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OSCAR = os.path.join(ROOT, "content", "oscar")

TACTIC_ORDER = [
    "Reconnaissance",
    "Resource Development",
    "Initial Access",
    "Execution",
    "Persistence",
    "Privilege Escalation",
    "Defense Evasion",
    "Credential Access",
    "Lateral Movement",
    "Collection",
    "Exfiltration",
    "Impact",
]

TACTIC_IDS = {
    "Reconnaissance": "TA01",
    "Resource Development": "TA02",
    "Initial Access": "TA03",
    "Execution": "TA04",
    "Persistence": "TA05",
    "Privilege Escalation": "TA06",
    "Defense Evasion": "TA07",
    "Credential Access": "TA08",
    "Lateral Movement": "TA09",
    "Collection": "TA10",
    "Exfiltration": "TA11",
    "Impact": "TA12",
}

BANNER = "This catalogue is <strong>AI-generated</strong>."


def load_yaml_dir(rel):
    items = {}
    for path in glob.glob(os.path.join(OSCAR, rel, "*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        if not data or "id" not in data:
            continue
        data["_path"] = path
        items[data["id"]] = data
    return items


def clean_list(values):
    if not values:
        return []
    out = []
    for v in values:
        if v in (None, "", "-"):
            continue
        out.append(v)
    return out


def md_lite(text):
    if not text:
        return ""
    text = str(text).strip()
    text = html.escape(text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" rel="noopener">\1</a>', text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return "".join(f"<p>{p.replace(chr(10), '<br>')}</p>" for p in paras)


def refs_html(refs):
    refs = clean_list(refs)
    if not refs:
        return "<p class='muted'>None listed.</p>"
    lis = []
    for r in refs:
        if isinstance(r, dict):
            path = (r.get("reference") or r).get("path") if isinstance(r.get("reference"), dict) else r.get("path") or r.get("url")
            if path:
                lis.append(f'<li><a href="{html.escape(str(path))}" rel="noopener">{html.escape(str(path))}</a></li>')
            continue
        s = str(r)
        if s.startswith("http"):
            lis.append(f'<li><a href="{html.escape(s)}" rel="noopener">{html.escape(s)}</a></li>')
        else:
            lis.append(f"<li>{html.escape(s)}</li>")
    return "<ul class='refs'>" + "".join(lis) + "</ul>"


def page(title, body, root_prefix, crumb, extra_head=""):
    nav = f"""
    <header class="top">
      <div class="ai-banner">{BANNER}</div>
      <div class="bar">
        <a class="brand" href="{root_prefix}index.html">SCIC</a>
        <nav>
          <a href="{root_prefix}index.html">Home</a>
          <a href="{root_prefix}matrix.html">Technique matrix</a>
          <a href="{root_prefix}techniques/index.html">Techniques</a>
          <a href="{root_prefix}incidents/index.html">Incident mapping</a>
          <a href="{root_prefix}platforms/index.html">Platforms</a>
          <a href="{root_prefix}stories/index.html">Attack stories</a>
          <a href="{root_prefix}guidance.html">Guidance</a>
          <a href="{root_prefix}origins.html">Origins</a>
          <a href="{root_prefix}talks.html">Talks</a>
          <a href="{root_prefix}sources.html">Sources</a>
          <a href="{root_prefix}changelog.html">Changelog</a>
          <a href="{root_prefix}about.html">About</a>
        </nav>
      </div>
    </header>"""
    footer = f"""
    <footer>
      <p>AI-generated catalogue of software supply-chain incidents. Apache-2.0.
      <a href="{root_prefix}about.html">About</a>.</p>
    </footer>"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · SCIC</title>
<link rel="stylesheet" href="{root_prefix}assets/style.css">
{extra_head}
</head>
<body>
{nav}
<main>
<p class="crumb">{crumb}</p>
{body}
</main>
{footer}
</body>
</html>
"""


CSS = """
:root {
  --bg: #10131a;
  --panel: #181c25;
  --panel-2: #1f2531;
  --ink: #eceef2;
  --muted: #9aa3b2;
  --line: #2a3140;
  --copper: #e2a24b;
  --copper-dim: #b67b2a;
  --teal: #6db3a8;
  --rose: #d46a6a;
  --chip: #2a3344;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--ink);
  font-family: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif; line-height: 1.5; }
a { color: var(--copper); text-decoration: none; }
a:hover { text-decoration: underline; }
.ai-banner {
  background: #2a2114; color: #f0d9a8; font-size: 0.85rem; padding: 0.45rem 1.2rem;
  border-bottom: 1px solid #4a3a22; text-align: center;
}
.bar { display: flex; align-items: center; justify-content: space-between; gap: 1rem;
  padding: 0.8rem 1.2rem; border-bottom: 1px solid var(--line); background: var(--panel);
  flex-wrap: wrap; }
.brand { font-weight: 700; letter-spacing: 0.08em; color: var(--ink); font-size: 1.05rem; }
.brand:hover { color: var(--copper); text-decoration: none; }
nav { display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.92rem; }
nav a { color: var(--muted); }
nav a:hover { color: var(--ink); }
main { padding: 1.4rem 1.2rem 3rem; max-width: 1400px; margin: 0 auto; }
.crumb { color: var(--muted); font-size: 0.82rem; }
h1 { font-size: 1.8rem; margin: 0.2rem 0 0.6rem; font-weight: 650; }
h2 { font-size: 1.15rem; margin-top: 1.6rem; }
.lede { color: var(--muted); max-width: 70ch; }
.muted { color: var(--muted); }
.notice {
  background: var(--panel); border: 1px solid var(--line); border-left: 3px solid var(--copper);
  padding: 0.9rem 1rem; margin: 1rem 0 1.4rem;
}
.stats { display: flex; gap: 0.8rem; flex-wrap: wrap; margin: 1rem 0 1.4rem; }
.stat { background: var(--panel); border: 1px solid var(--line); padding: 0.7rem 1rem; min-width: 7.5rem; }
.stat b { display: block; font-size: 1.3rem; color: var(--copper); }
.search { width: 100%; max-width: 28rem; padding: 0.55rem 0.7rem; background: var(--panel-2);
  border: 1px solid var(--line); color: var(--ink); margin: 0.6rem 0 1rem; }
.matrix-wrap { overflow-x: auto; padding-bottom: 1rem; }
.matrix { display: grid; gap: 0.45rem; align-items: start; }
.col { background: var(--panel); border: 1px solid var(--line); min-width: 8.4rem; }
.col.hidden, .tech.hidden { display: none !important; }
.col h3 { margin: 0; padding: 0.55rem 0.45rem; font-size: 0.72rem; letter-spacing: 0.03em;
  text-transform: uppercase; background: var(--panel-2); border-bottom: 1px solid var(--line);
  color: var(--copper); }
.col h3 span { display: block; color: var(--muted); font-weight: 500; font-size: 0.68rem; }
.tech {
  display: block; margin: 0.35rem; padding: 0.4rem 0.45rem; background: var(--chip);
  color: var(--ink); font-size: 0.75rem; line-height: 1.25; border: 1px solid transparent;
  position: relative;
}
.tech:hover { border-color: var(--copper); text-decoration: none; }
.tech .id { color: var(--teal); font-family: ui-monospace, monospace; font-size: 0.7rem; }
.tech .n {
  float: right; font-family: ui-monospace, monospace; font-size: 0.68rem;
  background: #0006; padding: 0 0.28rem; border-radius: 2px; color: var(--copper);
}
.tech.used-0 { opacity: 0.42; background: #161a22; }
.tech.used-0 .n { color: var(--muted); }
.tech.used-1 { background: #1c2a32; }
.tech.used-2 { background: #24363c; }
.tech.used-3 { background: #2c3a28; border-color: #3d5a32; }
.tech.used-4 { background: #3a3420; border-color: var(--copper-dim); }
.tech.used-5 { background: #4a3a18; border-color: var(--copper); }
.legend { display: flex; flex-wrap: wrap; gap: 0.6rem; align-items: center;
  color: var(--muted); font-size: 0.8rem; margin: 0.4rem 0 1rem; }
.legend i { display: inline-block; width: 0.85rem; height: 0.85rem; margin-right: 0.25rem;
  vertical-align: -0.1rem; border: 1px solid var(--line); }
.legend .l0 { background: #161a22; opacity: 0.7; }
.legend .l1 { background: #1c2a32; }
.legend .l3 { background: #2c3a28; }
.legend .l5 { background: #4a3a18; }
.list { display: grid; gap: 0.45rem; }
.row {
  display: grid; grid-template-columns: 5.5rem 12rem 1fr; gap: 0.7rem; align-items: baseline;
  background: var(--panel); border: 1px solid var(--line); padding: 0.55rem 0.8rem;
}
.row .id { font-family: ui-monospace, monospace; color: var(--teal); }
.chips { display: flex; flex-wrap: wrap; gap: 0.3rem; }
.chip { background: var(--chip); border: 1px solid var(--line); padding: 0.1rem 0.45rem;
  font-size: 0.75rem; color: var(--muted); }
.plat { display: inline-block; background: var(--chip); border: 1px solid var(--line);
  padding: 0.08rem 0.4rem; font-size: 0.72rem; color: var(--teal); margin: 0.1rem 0.15rem 0 0; }
.filter-bar { display: flex; flex-wrap: wrap; gap: 0.35rem; margin: 0.8rem 0 1.1rem; }
.filter-bar button, .filter-bar a {
  background: var(--panel); border: 1px solid var(--line); color: var(--muted);
  padding: 0.25rem 0.55rem; cursor: pointer; font: inherit; font-size: 0.8rem;
  text-decoration: none; display: inline-block;
}
.filter-bar button.on, .filter-bar button:hover, .filter-bar a:hover, .filter-bar a.on {
  border-color: var(--copper); color: var(--ink); text-decoration: none;
}
.dash { display: grid; grid-template-columns: repeat(auto-fit, minmax(21rem, 1fr)); gap: 1rem; margin: 1.2rem 0; }
.dash .panelbox { background: var(--panel); border: 1px solid var(--line); padding: 0.9rem 1rem 1.1rem; }
.dash .panelbox h3 { margin: 0 0 0.7rem; font-size: 0.95rem; color: var(--ink); }
.dash .panelbox .sub { color: var(--muted); font-size: 0.78rem; margin: 0.45rem 0 0; }
.hbar { display: grid; gap: 0.3rem; }
.hbar .hb { display: grid; grid-template-columns: 9.5rem 1fr 2.6rem; gap: 0.5rem; align-items: center;
  font-size: 0.78rem; }
.hbar .hb .track { background: var(--panel-2); border: 1px solid var(--line); height: 0.85rem; position: relative; }
.hbar .hb .fill { position: absolute; inset: 0 auto 0 0; background: linear-gradient(90deg, var(--copper-dim), var(--copper)); }
.hbar .hb .val { color: var(--copper); font-family: ui-monospace, monospace; text-align: right; }
.bars { display: flex; align-items: flex-end; gap: 3px; height: 9.5rem; margin-top: 0.6rem; }
.bars .b { flex: 1 1 0; background: linear-gradient(180deg, var(--copper), var(--copper-dim));
  min-width: 3px; position: relative; border-radius: 1px 1px 0 0; }
.bars .b:hover::after {
  content: attr(data-tip); position: absolute; bottom: 105%; left: 50%; transform: translateX(-50%);
  background: #000d; color: var(--ink); padding: 0.25rem 0.45rem; font-size: 0.72rem;
  white-space: nowrap; border: 1px solid var(--line); z-index: 5;
}
.tline { display: flex; gap: 0.9rem; flex-wrap: wrap; margin-top: 0.5rem; }
.tline span { font-size: 0.78rem; color: var(--muted); }
.big { font-size: 2.2rem; color: var(--copper); font-weight: 700; line-height: 1.1; }
.era { display: grid; grid-template-columns: 6.2rem 1fr; gap: 0.6rem; align-items: baseline;
  font-size: 0.82rem; margin: 0.3rem 0; }
.era .n { font-family: ui-monospace, monospace; color: var(--teal); }
.card.hidden { display: none !important; }
.inc-card { position: relative; display: block; }
.inc-card .card-link { position: absolute; inset: 0; z-index: 1; }
.inc-card h3 a { color: inherit; }
.inc-card .plat { position: relative; z-index: 2; }
.inc-card .card-link:focus-visible + .stage ~ h3 { outline: 2px solid var(--copper); }
.status { display: inline-block; margin-left: 0.5rem; padding: 0.05rem 0.4rem;
  border-radius: 2px; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.04em; }
.status.research { background: #1c2a44; color: #7fa7e8; border: 1px solid #2c3d5e; }
.status.demo { background: #2b2333; color: #c99ce8; border: 1px solid #3d2e4a; }
.sep { flex-basis: 100%; height: 0; }
.meta { color: var(--muted); font-size: 0.9rem; }
.card { background: var(--panel); border: 1px solid var(--line); padding: 1rem 1.1rem; margin: 0.8rem 0; }
.card h3 { margin-top: 0; }
.plat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(11.5rem, 1fr)); gap: 0.75rem; margin-top: 1.2rem; }
@media (max-width: 36rem) {
  .plat-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
.plat-box { display: flex; flex-direction: column; justify-content: space-between; min-height: 6.4rem;
  background: var(--panel); border: 1px solid var(--line); padding: 0.85rem 0.95rem; color: inherit; }
.plat-box:hover { border-color: var(--copper); text-decoration: none; }
.plat-box h3 { margin: 0 0 0.7rem; font-size: 0.98rem; line-height: 1.25; color: var(--ink); }
.plat-box .n { display: block; font-size: 1.35rem; font-weight: 650; color: var(--copper); line-height: 1.1; }
.plat-box .lbl { color: var(--muted); font-size: 0.75rem; }
.talk-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(17rem, 1fr)); gap: 0.75rem; margin-top: 1.2rem; }
.talk-box { min-height: 0; justify-content: flex-start; gap: 0.35rem; }
.talk-box h3 { font-size: 0.95rem; }
.talk-box h3 a { color: var(--copper); }
.talk-box p { margin: 0.15rem 0; font-size: 0.82rem; }
.flow { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0.6rem; margin: 1rem 0 1.4rem; }
.flow-col { background: var(--panel); border: 1px solid var(--line); padding: 0.75rem 0.8rem; }
.flow-col h2 { margin: 0 0 0.25rem; font-size: 0.95rem; }
.flow-col .def { color: var(--muted); font-size: 0.78rem; min-height: 3.2rem; }
.flow-col .n { font-size: 1.45rem; color: var(--copper); font-weight: 650; line-height: 1.1; }
.flow-col .lbl { color: var(--muted); font-size: 0.72rem; }
.flow-col ul { margin: 0.4rem 0 0; padding-left: 1rem; font-size: 0.78rem; }
.flow-col li { margin: 0.15rem 0; }
@media (max-width: 64rem) {
  .flow { grid-template-columns: 1fr; }
  .flow-col .def { min-height: 0; }
}
.gaps { border-left: 3px solid var(--rose); }
.stage { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--teal); }
footer { border-top: 1px solid var(--line); padding: 1.2rem; color: var(--muted); font-size: 0.85rem;
  background: var(--panel); }
footer p { max-width: 1400px; margin: 0 auto; }
.refs { overflow-wrap: anywhere; }
code { font-family: ui-monospace, SFMono-Regular, monospace; font-size: 0.88em; }
@media (max-width: 800px) {
  .row { grid-template-columns: 1fr; }
}
"""


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def build(dest):
    techs = load_yaml_dir("techniques")
    mits = load_yaml_dir("mitigations")
    dets = load_yaml_dir("detections")
    stories = load_yaml_dir("stories")
    origin_path = os.path.join(ROOT, "content", "portal", "technique-origin.yaml")
    origins = {}
    if os.path.exists(origin_path):
        with open(origin_path) as f:
            origins = (yaml.safe_load(f) or {}).get("techniques") or {}
    KIND_LABEL = {
        "incident": "Public incident / advisory",
        "research": "Security research",
        "guidance": "Standard or guidance",
        "analog": "ATT&CK / AppSec analog",
        "article": "Security article",
        "original": "Original corpus",
    }
    plat_path = os.path.join(ROOT, "content", "portal", "platforms.yaml")
    plat_labels = {}
    if os.path.exists(plat_path):
        with open(plat_path) as f:
            plat_doc = yaml.safe_load(f) or {}
        for p in plat_doc.get("platforms") or []:
            if p.get("id"):
                plat_labels[p["id"]] = p.get("label") or p["id"]

    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    write(os.path.join(dest, ".nojekyll"), "")
    write(os.path.join(dest, "assets", "style.css"), CSS)

    by_tactic = {t: [] for t in TACTIC_ORDER}
    for t in techs.values():
        by_tactic.setdefault(t["tactic"], []).append(t)
    for tname in by_tactic:
        by_tactic[tname].sort(key=lambda x: x["id"])

    usage = Counter()
    for s in stories.values():
        seen = set()
        for attack in s.get("attacks") or []:
            for tech in attack.get("techniques") or []:
                tid = tech.get("techniqueID")
                if tid:
                    seen.add(tid)
        for tid in seen:
            usage[tid] += 1

    def used_class(n):
        if n <= 0:
            return "used-0"
        if n == 1:
            return "used-1"
        if n == 2:
            return "used-2"
        if n <= 4:
            return "used-3"
        if n <= 7:
            return "used-4"
        return "used-5"

    # matrix.json for consumers
    matrix = {}
    for tname in TACTIC_ORDER:
        items = []
        for t in by_tactic.get(tname, []):
            items.append({
                "id": t["id"],
                "name": t["summary"],
                "tooltip": t["summary"],
                "tags": t.get("realm") or [],
                "url": f"techniques/{t['id']}.html",
                "description": t.get("description") or "",
                "incidentCount": usage[t["id"]],
            })
        matrix[tname] = {
            "items": items,
            "amount": len(items),
            "tooltip": tname,
            "tacticid": TACTIC_IDS.get(tname, ""),
        }
    write(os.path.join(dest, "data", "matrix.json"), json.dumps(matrix, indent=2) + "\n")
    write(os.path.join(ROOT, "matrix.json"), json.dumps(matrix, indent=2) + "\n")
    write(os.path.join(ROOT, "content", "website", "matrix.json"), json.dumps(matrix, indent=2) + "\n")

    # home / matrix
    cols = []
    n_cols = len(TACTIC_ORDER)
    for tname in TACTIC_ORDER:
        items = sorted(
            by_tactic.get(tname, []),
            key=lambda t: (-usage[t["id"]], t["id"]),
        )
        cells = []
        for t in items:
            n = usage[t["id"]]
            cells.append(
                f'<a class="tech {used_class(n)}" data-used="{n}" href="techniques/{html.escape(t["id"])}.html">'
                f'<span class="n" title="Mapped incidents">{n}</span>'
                f'<span class="id">{html.escape(t["id"])}</span><br>{html.escape(t["summary"])}</a>'
            )
        cols.append(
            f'<div class="col"><h3>{html.escape(tname)}'
            f'<span>{TACTIC_IDS.get(tname, "")} · {len(items)}</span></h3>'
            + "".join(cells) + "</div>"
        )
    n_tech, n_mit, n_det, n_story = len(techs), len(mits), len(dets), len(stories)

    # ---------- dashboard data ----------
    # incidents per year
    per_year = Counter()
    for s in stories.values():
        d = str(s.get("date") or "")
        if d[:4].isdigit():
            per_year[d[:4]] += 1
    years = sorted(per_year)

    # top techniques
    top_techs = usage.most_common(12)
    max_top = top_techs[0][1] if top_techs else 1
    top_rows = "".join(
        f'<div class="hb"><span class="id">{html.escape(tid)}</span>'
        f'<span class="track"><span class="fill" style="width:{round(100 * n / max_top)}%"></span></span>'
        f'<span class="val">{n}</span></div>'
        for tid, n in top_techs
    )

    # incidents per platform
    per_plat = Counter()
    for s in stories.values():
        for p in s.get("platforms") or []:
            if p:
                per_plat[p] += 1
    top_plats = per_plat.most_common(12)
    max_plat = top_plats[0][1] if top_plats else 1
    plat_rows = "".join(
        f'<div class="hb"><a href="platforms/{html.escape(slug)}.html">{html.escape(plat_labels.get(slug, slug))}</a>'
        f'<span class="track"><span class="fill" style="width:{round(100 * n / max_plat)}%"></span></span>'
        f'<span class="val">{n}</span></div>'
        for slug, n in top_plats
    )

    # observed vs identified techniques
    n_observed = sum(1 for tid in techs if usage[tid] > 0)
    n_identified = n_tech - n_observed

    # era split (pre-2020 classics vs modern wave)
    eras = Counter()
    for s in stories.values():
        d = str(s.get("date") or "")
        y = int(d[:4]) if d[:4].isdigit() else 0
        if y == 0:
            eras["unknown"] += 1
        elif y < 2020:
            eras["pre-2020 classics"] += 1
        elif y < 2025:
            eras["2020–2024"] += 1
        else:
            eras["2025–2026 wave"] += 1

    # top actors / malware names from summaries (crude but useful)
    name_pat = re.compile(r"\b([A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+|[A-Z]{2,}[A-Za-z0-9]*)\b")
    name_hits = Counter()
    for s in stories.values():
        blob = (s.get("summary") or "") + " " + (s.get("description") or "")[:300]
        for m in name_pat.findall(blob):
            if len(m) >= 5 and m.lower() not in ("supply", "chain", "github", "windows", "chrome", "firefox", "linux", "package", "attack", "campaign", "backdoor", "stealer", "malware", "npm", "pypi", "pytorch", "solarwinds", "circleci", "codecov", "ultralytics", "dependabot", "wednesday"):
                name_hits[m] += 1
    top_names = name_hits.most_common(10)
    name_chips = " ".join(
        f'<a class="chip" href="incidents/index.html">{html.escape(nm)} <b>{c}</b></a>'
        for nm, c in top_names
    ) or '<span class="muted">—</span>'

    year_bars = "".join(
        f'<div class="b" data-tip="{y}: {per_year[y]} incidents" style="height:{round(100 * per_year[y] / max(per_year.values()))}%"></div>'
        for y in years
    )
    year_labels = "".join(f"<span>{y[2:]}</span>" for y in years)

    dash = f"""
    <h1>Supply Chain Incidences Catalogue</h1>
    <p class="lede">An AI-generated catalogue of software supply-chain incidents:
    {n_story} documented cases, {n_tech} techniques, and the ecosystems they hit.</p>
    <div class="notice">{BANNER} Published from
    <a href="https://github.com/ai-anant/supply-chain-incidences-catalogue">ai-anant/supply-chain-incidences-catalogue</a>.</div>
    <div class="stats">
      <div class="stat"><b>{n_story}</b> incidents</div>
      <div class="stat"><b>{n_tech}</b> techniques</div>
      <div class="stat"><b>{n_observed}</b> observed in incidents</div>
      <div class="stat"><b>{n_identified}</b> identified from research</div>
    </div>

    <div class="dash">
      <div class="panelbox" style="grid-column: 1 / -1;">
        <h3>Incidents per year</h3>
        <div class="bars">{year_bars}</div>
        <div class="tline">{''.join(f'<span>{y}</span>' for y in years)}</div>
        <p class="sub">Hover a bar for the count. 2025–2026 is the worm/ATO wave
        (Shai-Hulud and descendants); the pre-2020 bars are the classic vendor-updater era.</p>
      </div>
      <div class="panelbox">
        <h3>Most-used techniques</h3>
        <div class="hbar">{top_rows}</div>
        <p class="sub">By number of incidents mapping to each technique. Full list in the
        <a href="matrix.html">technique matrix</a>.</p>
      </div>
      <div class="panelbox">
        <h3>Incidents per platform</h3>
        <div class="hbar">{plat_rows}</div>
        <p class="sub">Grouped lists per ecosystem in
        <a href="platforms/index.html">Platforms</a>.</p>
      </div>
      <div class="panelbox">
        <h3>Eras</h3>
        <div class="era"><span class="n">{eras.get('pre-2020 classics', 0)}</span> pre-2020 classics (CCleaner, NotPetya, ShadowHammer era)</div>
        <div class="era"><span class="n">{eras.get('2020–2024', 0)}</span> 2020–2024 (extension and registry hijack era)</div>
        <div class="era"><span class="n">{eras.get('2025–2026 wave', 0)}</span> 2025–2026 worm/ATO wave</div>
        <p class="sub">The 2025–2026 wave is roughly one incident every three days per
        StepSecurity's tracking.</p>
      </div>
      <div class="panelbox">
        <h3>Frequently seen in write-ups</h3>
        <div class="chips">{name_chips}</div>
        <p class="sub">Actor / malware names appearing most often across incident summaries.</p>
      </div>
    </div>

    <div class="dash">
      <div class="panelbox"><h3>Browse</h3>
        <p><a href="matrix.html">Technique matrix</a> — techniques × tactics, heat-mapped by incident count</p>
        <p><a href="incidents/index.html">Incident mapping</a> — every incident → techniques</p>
        <p><a href="platforms/index.html">Platforms</a> — all incidents for npm, PyPI, GitHub Actions, …</p>
        <p><a href="stories/index.html">Attack stories</a> — chronological list</p>
      </div>
      <div class="panelbox"><h3>Project</h3>
        <p><a href="guidance.html">Guidance mapping</a> — OWASP / NIST / SLSA / CISA</p>
        <p><a href="origins.html">Origins</a> — where each technique came from</p>
        <p><a href="talks.html">Conference talks</a> — supply-chain and AI talks, mapped or gapped</p>
        <p><a href="sources.html">Sources</a> — the watch list this catalogue tracks</p>
        <p><a href="changelog.html">Changelog</a> — what the AI maintainer added</p>
      </div>
    </div>
    """
    write(os.path.join(dest, "index.html"), page("Home", dash, "", "SCIC / Home"))

    matrix_body = f"""
    <h1>OSC&R Matrix</h1>
    <p class="lede">This catalogue uses OSC&amp;R and maps incidents onto it.
    Techniques × tactics, heat-mapped by how many incidents use each technique.</p>
    <div class="stats">
      <div class="stat"><b>{n_tech}</b> techniques</div>
      <div class="stat"><b>{n_story}</b> mapped incidents</div>
    </div>
    <p><input class="search" id="q" placeholder="Filter techniques… empty columns hide"></p>
    <p class="legend">Mapped incidents:&nbsp;
      <span><i class="l0"></i>0</span>
      <span><i class="l1"></i>1–2</span>
      <span><i class="l3"></i>3–4</span>
      <span><i class="l5"></i>5+</span>
      <span>Badge = mapped incidents. Dim cells are identified from research/guidance, not yet tied to a named case. Search hides non-matches and empty columns.</span>
    </p>
    <div class="matrix-wrap">
      <div class="matrix" id="matrix" style="grid-template-columns: repeat({n_cols}, minmax(8.4rem, 1fr))">
        {''.join(cols)}
      </div>
    </div>
    <script>
    const q = document.getElementById('q');
    const matrix = document.getElementById('matrix');
    function applyFilter() {{
      const v = q.value.toLowerCase().trim();
      document.querySelectorAll('.tech').forEach(el => {{
        const hit = !v || el.textContent.toLowerCase().includes(v);
        el.classList.toggle('hidden', !hit);
      }});
      let visible = 0;
      document.querySelectorAll('.col').forEach(col => {{
        const any = [...col.querySelectorAll('.tech')].some(t => !t.classList.contains('hidden'));
        col.classList.toggle('hidden', !any);
        if (any) visible++;
      }});
      if (visible) {{
        matrix.style.gridTemplateColumns = 'repeat(' + visible + ', minmax(8.4rem, 1fr))';
        matrix.style.minWidth = (visible * 8.9) + 'rem';
      }} else {{
        matrix.style.gridTemplateColumns = 'none';
        matrix.style.minWidth = '0';
      }}
    }}
    q.addEventListener('input', applyFilter);
    applyFilter();
    </script>
    """
    write(os.path.join(dest, "matrix.html"), page("OSC&R Matrix", matrix_body, "", "SCIC / OSC&R Matrix"))

    # techniques index + pages
    rows = []
    for tid in sorted(techs):
        t = techs[tid]
        rows.append(
            f'<a class="row" href="{html.escape(tid)}.html">'
            f'<span class="id">{html.escape(tid)}</span>'
            f'<span>{html.escape(t["tactic"])}</span>'
            f'<span>{html.escape(t["summary"])}</span></a>'
        )
    t_index = f"""
    <h1>Techniques</h1>
    <p class="lede">{n_tech} techniques across {len(TACTIC_ORDER)} tactics.</p>
    <div class="list">{''.join(rows)}</div>
    """
    write(os.path.join(dest, "techniques", "index.html"), page("Techniques", t_index, "../", "SCIC / Techniques"))

    for tid, t in techs.items():
        m_links = []
        for mid in clean_list(t.get("mitigations")):
            name = (mits[mid].get("summary") if mid in mits else None) or mid
            m_links.append(f'<li><span class="id">{html.escape(str(mid))}</span> {html.escape(str(name))}</li>')
        d_links = []
        for did in clean_list(t.get("detections")):
            name = (dets[did].get("summary") if did in dets else None) or did
            d_links.append(f'<li><span class="id">{html.escape(str(did))}</span> {html.escape(str(name))}</li>')
        realms = " ".join(f'<span class="chip">{html.escape(r)}</span>' for r in (t.get("realm") or []))
        subs = clean_list(t.get("subTechniques") or t.get("subtechniques"))
        sub_html = ""
        if subs:
            sub_html = "<h2>Sub-techniques</h2><ul>" + "".join(
                f'<li><a href="{html.escape(s)}.html">{html.escape(s)}</a>'
                f' {html.escape(techs[s]["summary"]) if s in techs else ""}</li>'
                for s in subs
            ) + "</ul>"
        used_in = []
        for s in stories.values():
            for attack in s.get("attacks") or []:
                for tech in attack.get("techniques") or []:
                    if tech.get("techniqueID") == tid:
                        used_in.append(s)
                        break
        used_html = ""
        if used_in:
            used_html = (
                f'<h2>Observed in incidents ({len(used_in)})</h2><ul>'
                + "".join(
                    f'<li><a href="../incidents/{html.escape(s["id"])}.html">{html.escape(s["summary"])}</a></li>'
                    for s in used_in
                )
                + "</ul>"
            )
        else:
            used_html = (
                "<div class='notice'><strong>Identified, not yet observed here.</strong> "
                "This technique set includes behaviors from pentest research, "
                "defender guidance, and analog attacker behavior — not only from "
                "named public breaches. No incident in this corpus maps here yet.</div>"
            )
        n_obs = len(used_in)
        origin = origins.get(tid) or {}
        origin_kind = origin.get("kind") or ("incident" if n_obs else "original")
        origin_note = origin.get("note") or ""
        origin_src = origin.get("sources") or t.get("references") or []
        origin_html = (
            f'<h2>Where this idea came from</h2>'
            f'<p class="meta">{html.escape(KIND_LABEL.get(origin_kind, origin_kind))}</p>'
            f'{md_lite(origin_note)}'
            f'{refs_html(origin_src)}'
        )
        body = f"""
        <p class="meta">{html.escape(tid)} · {html.escape(t["tactic"])} · {html.escape(TACTIC_IDS.get(t["tactic"], ""))} · {'observed in ' + str(n_obs) + ' incident(s)' if n_obs else 'identified from research/guidance'}</p>
        <h1>{html.escape(t["summary"])}</h1>
        <div class="chips">{realms}</div>
        {md_lite(t.get("description"))}
        {origin_html}
        {sub_html}
        <h2>Mitigations</h2>
        {"<ul>" + "".join(m_links) + "</ul>" if m_links else "<p class='muted'>None linked yet.</p>"}
        <h2>Detections</h2>
        {"<ul>" + "".join(d_links) + "</ul>" if d_links else "<p class='muted'>None linked yet.</p>"}
        {used_html}
        <h2>References</h2>
        {refs_html(t.get("references"))}
        """
        write(
            os.path.join(dest, "techniques", f"{tid}.html"),
            page(f"{tid} {t['summary']}", body, "../", f'SCIC / <a href="index.html">Techniques</a> / {html.escape(tid)}'),
        )

    # stories + incidents (same data; incidents page is the mapping view)
    def story_sort_key(s):
        raw = str(s.get("date") or "1970")
        m = re.match(r"(\d{4})(?:-(\d{1,2}))?", raw)
        if not m:
            return (0, 0)
        return (int(m.group(1)), int(m.group(2) or 0))

    ordered_stories = sorted(stories.values(), key=story_sort_key, reverse=True)

    def story_card(s, story_href, plat_href):
        n_techs = sum(len(a.get("techniques") or []) for a in s.get("attacks") or [])
        plats = [p for p in (s.get("platforms") or []) if p]
        status = s.get("status") or "incident"
        status_badges = {
            "incident": "",
            "research": '<span class="status research" title="Bug/PoC found by a researcher or vendor; no confirmed in-the-wild exploitation">research</span>',
            "demo": '<span class="status demo" title="Author demonstration or concept; no victim">demo</span>',
        }
        chips = "".join(
            f'<a class="plat" href="{html.escape(plat_href)}{html.escape(p)}.html">{html.escape(plat_labels.get(p, p))}</a>'
            if plat_href
            else f'<span class="plat">{html.escape(plat_labels.get(p, p))}</span>'
            for p in plats
        )
        return (
            f'<div class="card inc-card status-{status}" data-platforms="{" ".join(html.escape(p) for p in plats)}" data-status="{status}">'
            f'<a class="card-link" href="{story_href}{html.escape(s["id"])}.html"></a>'
            f'<div class="stage">{html.escape(str(s.get("date") or ""))}{status_badges.get(status, "")}</div>'
            f'<h3><a href="{story_href}{html.escape(s["id"])}.html">{html.escape(s["summary"])}</a></h3>'
            f'<p>{chips}</p>'
            f'<p class="muted">{n_techs} mapped techniques</p></div>'
        )

    used_plats = sorted(
        {p for s in stories.values() for p in (s.get("platforms") or []) if p},
        key=lambda p: (
            -sum(1 for s in stories.values() if p in (s.get("platforms") or [])),
            p,
        ),
    )
    plat_counts = {
        p: sum(1 for s in stories.values() if p in (s.get("platforms") or []))
        for p in used_plats
    }
    filter_btns = ['<a class="on" href="index.html">All</a>']
    for p in used_plats:
        filter_btns.append(
            f'<a href="../platforms/{html.escape(p)}.html">'
            f'{html.escape(plat_labels.get(p, p))} ({plat_counts[p]})</a>'
        )

    n_incident = sum(1 for s in stories.values() if (s.get("status") or "incident") == "incident")
    n_research = sum(1 for s in stories.values() if s.get("status") == "research")
    n_demo = sum(1 for s in stories.values() if s.get("status") == "demo")
    status_btns = (
        f'<span class="status-btns" id="status-btns">'
        f'<button type="button" class="on" data-status-filter="all">All {len(ordered_stories)}</button>'
        f'<button type="button" data-status-filter="incident">Real incidents {n_incident}</button>'
        f'<button type="button" data-status-filter="research">Research {n_research}</button>'
        f'<button type="button" data-status-filter="demo">Demos {n_demo}</button>'
        f'</span>'
    )
    inc_index = f"""
    <h1>Incident mapping</h1>
    <p class="lede">Software-supply-chain events mapped onto techniques,
    tagged by the registry or platform that was hit. Open a platform for the full group.
    <strong>Real incidents</strong> hit victims in the wild; <strong>research</strong> entries are
    bug/PoC discoveries with no confirmed exploitation; <strong>demos</strong> are author
    demonstrations with no victim.</p>
    <div class="filter-bar">{status_btns}<span class="sep"></span>{''.join(filter_btns)}</div>
    <script>
    (function() {{
      const btns = document.getElementById('status-btns');
      btns.addEventListener('click', function(e) {{
        const b = e.target.closest('button'); if (!b) return;
        btns.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
        const v = b.getAttribute('data-status-filter');
        document.querySelectorAll('.inc-card').forEach(c => {{
          const show = v === 'all' || c.getAttribute('data-status') === v;
          c.style.display = show ? '' : 'none';
        }});
      }});
    }})();
    </script>
    {''.join(story_card(s, '', '../platforms/') for s in ordered_stories)}
    """
    write(os.path.join(dest, "incidents", "index.html"), page("Incident mapping", inc_index, "../", "SCIC / Incident mapping"))

    st_index = f"""
    <h1>Attack stories</h1>
    <p class="lede">Narrative reconstructions of supply-chain events.
    Real incidents, research discoveries, and demos are labelled.</p>
    <div class="filter-bar">{status_btns}</div>
    <script>
    (function() {{
      const btns = document.getElementById('status-btns');
      btns.addEventListener('click', function(e) {{
        const b = e.target.closest('button'); if (!b) return;
        btns.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
        const v = b.getAttribute('data-status-filter');
        document.querySelectorAll('.inc-card').forEach(c => {{
          const show = v === 'all' || c.getAttribute('data-status') === v;
          c.style.display = show ? '' : 'none';
        }});
      }});
    }})();
    </script>
    {''.join(story_card(s, '', '../platforms/') for s in ordered_stories)}
    """
    write(os.path.join(dest, "stories", "index.html"), page("Attack stories", st_index, "../", "SCIC / Attack stories"))

    by_plat = {p: [] for p in used_plats}
    for s in ordered_stories:
        for p in s.get("platforms") or []:
            if p in by_plat:
                by_plat[p].append(s)
    agg_cards = []
    for p in used_plats:
        items = by_plat[p]
        agg_cards.append(
            f'<a class="plat-box" href="{html.escape(p)}.html">'
            f'<h3>{html.escape(plat_labels.get(p, p))}</h3>'
            f'<span><span class="n">{len(items)}</span> <span class="lbl">incidents</span></span></a>'
        )
    plat_index = f"""
    <h1>Incidents by platform</h1>
    <p class="lede">Open a platform to see every mapped incident that hit it.</p>
    <div class="plat-grid">{''.join(agg_cards)}</div>
    """
    write(os.path.join(dest, "platforms", "index.html"), page("Platforms", plat_index, "../", "SCIC / Platforms"))
    for p in used_plats:
        items = by_plat[p]
        other = "".join(
            f'<a href="{html.escape(q)}.html">{html.escape(plat_labels.get(q, q))} ({plat_counts[q]})</a>'
            for q in used_plats if q != p
        )
        body = f"""
        <h1>{html.escape(plat_labels.get(p, p))}</h1>
        <p class="lede">{len(items)} mapped incident(s) that touched this platform or registry.</p>
        <div class="filter-bar">
          <a href="index.html">All platforms</a>
          <a class="on" href="{html.escape(p)}.html">{html.escape(plat_labels.get(p, p))} ({len(items)})</a>
          {other}
        </div>
        {''.join(story_card(s, '../incidents/', './') for s in items)}
        """
        write(
            os.path.join(dest, "platforms", f"{p}.html"),
            page(plat_labels.get(p, p), body, "../", f'SCIC / <a href="index.html">Platforms</a> / {html.escape(plat_labels.get(p, p))}'),
        )

    for s in stories.values():
        stages = []
        all_tech_rows = []
        for attack in s.get("attacks") or []:
            tech_bits = []
            for tech in attack.get("techniques") or []:
                tid = tech.get("techniqueID") or ""
                name = tech.get("techName") or (techs[tid]["summary"] if tid in techs else "")
                link = f'<a href="../techniques/{html.escape(tid)}.html">{html.escape(tid)}</a>' if tid else ""
                tech_bits.append(
                    f'<div class="card"><p class="meta">{link} · {html.escape(tech.get("tactic") or "")} · {html.escape(name)}</p>'
                    f'{md_lite(tech.get("comment"))}</div>'
                )
                all_tech_rows.append(tid)
            stages.append(
                f'<h2><span class="stage">{html.escape(attack.get("stage") or "")}</span> '
                f'{html.escape(attack.get("attack") or "")}</h2>' + "".join(tech_bits)
            )
        gaps = s.get("gaps") or []
        gap_html = ""
        if gaps:
            items = []
            for g in gaps:
                if isinstance(g, dict):
                    items.append(f"<li>{html.escape(g.get('note') or json.dumps(g))}</li>")
                else:
                    items.append(f"<li>{html.escape(str(g))}</li>")
            gap_html = '<div class="card gaps"><h3>Framework gaps noted</h3><ul>' + "".join(items) + "</ul></div>"
        unique = []
        for tid in all_tech_rows:
            if tid and tid not in unique:
                unique.append(tid)
        map_list = "<ul>" + "".join(
            f'<li><a href="../techniques/{html.escape(tid)}.html">{html.escape(tid)}</a> '
            f'{html.escape(techs[tid]["summary"]) if tid in techs else ""}</li>'
            for tid in unique
        ) + "</ul>"
        plats = [p for p in (s.get("platforms") or []) if p]
        plat_html = "".join(
            f'<a class="plat" href="../platforms/{html.escape(p)}.html">{html.escape(plat_labels.get(p, p))}</a>'
            for p in plats
        )
        body = f"""
        <p class="meta">{html.escape(s["id"])} · {html.escape(str(s.get("date") or ""))}</p>
        <h1>{html.escape(s["summary"])}</h1>
        <p>{plat_html}</p>
        {md_lite(s.get("description"))}
        <h2>Mapped techniques</h2>
        {map_list}
        {''.join(stages)}
        {gap_html}
        <h2>Sources</h2>
        {refs_html(s.get("links"))}
        """
        html_page = page(
            s["summary"],
            body,
            "../",
            f'SCIC / <a href="index.html">Incidents</a> / {html.escape(s["id"])}',
        )
        write(os.path.join(dest, "incidents", f"{s['id']}.html"), html_page)
        write(os.path.join(dest, "stories", f"{s['id']}.html"), html_page)

    portal = os.path.join(ROOT, "content", "portal")
    cl = {}
    gd = {}
    cl_path = os.path.join(portal, "changelog.yaml")
    gd_path = os.path.join(portal, "guidance.yaml")
    if os.path.exists(cl_path):
        with open(cl_path) as f:
            cl = yaml.safe_load(f) or {}
    if os.path.exists(gd_path):
        with open(gd_path) as f:
            gd = yaml.safe_load(f) or {}

    cl_blocks = []
    for e in cl.get("entries") or []:
        lis = "".join(f"<li>{html.escape(str(i))}</li>" for i in (e.get("items") or []))
        cl_blocks.append(
            f'<div class="card"><p class="stage">{html.escape(str(e.get("date") or ""))}</p>'
            f'<h3>{html.escape(e.get("title") or "")}</h3><ul>{lis}</ul></div>'
        )
    changelog_body = f"""
    <h1>Changelog</h1>
    <p class="lede">What changed in this catalogue. Dated, meant to be skimmed.
    Git history remains the audit trail.</p>
    {''.join(cl_blocks) or '<p class="muted">No entries yet.</p>'}
    """
    write(os.path.join(dest, "changelog.html"), page("Changelog", changelog_body, "", "SCIC / Changelog"))

    origin_groups = {}
    for tid, o in origins.items():
        origin_groups.setdefault(o.get("kind") or "original", []).append((tid, o))
    og_html = []
    for kind in ["incident", "research", "guidance", "analog", "article", "original"]:
        items = sorted(origin_groups.get(kind) or [], key=lambda x: x[0])
        if not items:
            continue
        rows = []
        for tid, o in items:
            src0 = ""
            srcs = o.get("sources") or []
            if srcs:
                u = srcs[0]
                src0 = f'<a href="{html.escape(str(u))}">{html.escape(str(u)[:70])}</a>'
            rows.append(
                f'<a class="row" href="techniques/{html.escape(tid)}.html">'
                f'<span class="id">{html.escape(tid)}</span>'
                f'<span>{html.escape(o.get("summary") or "")}</span>'
                f'<span class="muted">{html.escape((o.get("note") or "")[:160])}</span></a>'
            )
        og_html.append(
            f'<h2>{html.escape(KIND_LABEL.get(kind, kind))} ({len(items)})</h2>'
            f'<div class="list">{"".join(rows)}</div>'
        )
    origins_body = f"""
    <h1>Where each technique came from</h1>
    <p class="lede">Every technique has an origin kind and at least one source URL.
    Techniques that started with no references now point at the
    ATT&amp;CK, OWASP, SLSA, or research analog that justifies them.</p>
    {''.join(og_html)}
    """
    write(os.path.join(dest, "origins.html"), page("Origins", origins_body, "", "SCIC / Origins"))

    src_doc = {}
    src_path = os.path.join(portal, "sources.yaml")
    if os.path.exists(src_path):
        with open(src_path) as f:
            src_doc = yaml.safe_load(f) or {}
    tracked, reference = [], []
    for s in src_doc.get("sources") or []:
        card = (
            f'<div class="card"><h3><a href="{html.escape(s.get("url") or "#")}">{html.escape(s.get("name") or "")}</a></h3>'
            f'<p class="meta">{html.escape(s.get("kind") or "")}'
            f'{" · watched daily" if s.get("track") else " · guidance baseline"}</p>'
            f'<p class="muted">{html.escape(s.get("note") or "")}</p></div>'
        )
        (tracked if s.get("track") else reference).append(card)
    sources_body = f"""
    <h1>Sources we track</h1>
    <p class="lede">First-party research blogs and advisories the daily intake job reads.
    Add a row in <code>content/portal/sources.yaml</code> to watch a new feed.
    Aggregators are not primary sources.</p>
    <h2>Watched daily</h2>
    {''.join(tracked) or '<p class="muted">None.</p>'}
    <h2>Guidance baselines (not polled daily)</h2>
    {''.join(reference) or '<p class="muted">None.</p>'}
    """
    write(os.path.join(dest, "sources.html"), page("Sources", sources_body, "", "SCIC / Sources"))

    talks_doc = {}
    talks_path = os.path.join(portal, "talks.yaml")
    if os.path.exists(talks_path):
        with open(talks_path) as f:
            talks_doc = yaml.safe_load(f) or {}
    talk_cards = []
    for t in talks_doc.get("talks") or []:
        tids = t.get("techniques") or []
        if tids:
            chips = " ".join(
                f'<a href="techniques/{html.escape(tid)}.html">{html.escape(tid)}</a>'
                for tid in tids
            )
            status = f'<p class="meta">mapped · {html.escape(t.get("field") or "")}</p><p>{chips}</p>'
        else:
            status = f'<p class="meta">recorded, not mapped · {html.escape(t.get("field") or "")}</p>'
        speakers = ", ".join(t.get("speakers") or [])
        body_note = t.get("gap") or t.get("note") or ""
        talk_cards.append(
            f'<div class="plat-box talk-box">'
            f'<p class="stage">{html.escape(t.get("event") or "")}</p>'
            f'<h3><a href="{html.escape(t.get("url") or "#")}">{html.escape(t.get("title") or "")}</a></h3>'
            f'<p class="muted">{html.escape(speakers)}</p>'
            f'{status}'
            f'<p>{html.escape(body_note)}</p></div>'
        )
    talks_body = f"""
    <h1>Conference talks</h1>
    <p class="lede">Supply-chain and AI talks from conferences we have walked.
    These are not attack stories. A technique link means the abstract describes that
    technique. “Recorded, not mapped” means the talk is in the field but no technique
    ID fits — a wrong mapping is worse than a gap.</p>
    <div class="talk-grid">{''.join(talk_cards) or '<p class="muted">No talks yet.</p>'}</div>
    """
    write(os.path.join(dest, "talks.html"), page("Talks", talks_body, "", "SCIC / Talks"))

    unused_n = sum(1 for tid in techs if usage[tid] == 0)
    doc_blocks = []
    for d in gd.get("documents") or []:
        gaps = d.get("gaps_found") or []
        glis = []
        for g in gaps:
            if isinstance(g, dict):
                gid = g.get("id") or ""
                note = g.get("note") or ""
                glis.append(f"<li><strong>{html.escape(str(gid))}</strong> {html.escape(note)}</li>")
            else:
                glis.append(f"<li>{html.escape(str(g))}</li>")
        doc_blocks.append(
            f'<div class="card"><h3><a href="{html.escape(d.get("url") or "#")}">{html.escape(d.get("name") or "")}</a></h3>'
            f'<p class="muted">{html.escape(d.get("publisher") or "")}</p>'
            f'<ul>{"".join(glis)}</ul></div>'
        )
    new_ts = gd.get("new_techniques") or []
    new_lis = "".join(
        f'<li><a href="techniques/{html.escape(tid)}.html">{html.escape(tid)}</a> '
        f'{html.escape(techs[tid]["summary"]) if tid in techs else ""}</li>'
        for tid in new_ts
    )
    guidance_body = f"""
    <h1>Guidance</h1>
    <p class="lede">Defender documents (OWASP, NIST SSDF, SLSA, CISA) describe controls.
    This catalogue describes attacker techniques. This page records where a control
    had no matching technique, and what we added.</p>
    <div class="notice"><strong>Why a technique can exist with zero incidents.</strong>
    Some techniques come from pentest findings and published research, the same way
    other catalogues list a technique before a public victim write-up exists.
    Dim cells on the matrix are identified from literature ({unused_n} right now).
    Bright cells are observed in a mapped incident. That is not a claim the unused
    ones are fake. We have not yet attached a named public case.</div>
    <h2>Documents reviewed</h2>
    {''.join(doc_blocks)}
    <h2>Techniques added from this review</h2>
    <ul>{new_lis or '<li class="muted">None</li>'}</ul>
    """
    write(os.path.join(dest, "guidance.html"), page("Guidance", guidance_body, "", "SCIC / Guidance"))

    about = f"""
    <h1>About</h1>
    <div class="notice"><strong>AI-generated.</strong> Supply Chain Incidences Catalogue.</div>
    <h2>What this catalogue is</h2>
    <p>Incidents, the platforms they hit, conference talks, the sources those came from,
    and the technique matrix those incidents are mapped onto.</p>
    <h2>This catalogue</h2>
    <ul>
      <li>Repo: <a href="https://github.com/ai-anant/supply-chain-incidences-catalogue">ai-anant/supply-chain-incidences-catalogue</a></li>
      <li>Site: <a href="https://ai-anant.github.io/supply-chain-incidences-catalogue/">ai-anant.github.io/supply-chain-incidences-catalogue</a></li>
      <li>License: Apache-2.0. See NOTICE.</li>
    </ul>
    <p class="muted">Generated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}.</p>
    """
    write(os.path.join(dest, "about.html"), page("About", about, "", "SCIC / About"))

    # Preview cut: five pipeline stages. Not linked from the nav.
    stage_meta = [
        ("dev", "Development environment", "Machine and tools before code is pushed: IDE, agent, workstation."),
        ("repo", "Code repository", "Source control: commits, review, keys, the repo itself."),
        ("cicd", "CI/CD", "Pipelines, runners, and the service that builds."),
        ("artifact", "Artifact / container", "Registries, images, signatures, hosted build outputs."),
        ("deploy", "Deployment / cloud / exec", "Where it runs: cloud, IaC apply, customer environment."),
    ]
    realm_stage = {
        "SCM Posture": "repo",
        "CI/CD Posture": "cicd",
        "Artifact Security": "artifact",
        "Container Security": "artifact",
        "Open Source Security": "artifact",
        "Cloud Security": "deploy",
        "Infrastructure as code": "deploy",
        "AI Posture": "dev",
    }
    dev_ids = {"T0152", "T0153", "T0154", "T0210", "T0213"}
    plat_stage = {
        "vscode": "dev", "ai-agents": "dev", "mcp": "dev", "browser-extensions": "dev",
        "git": "repo",
        "github-actions": "cicd", "jenkins": "cicd", "cicd-saas": "cicd",
        "npm": "artifact", "pypi": "artifact", "rubygems": "artifact", "packagist": "artifact",
        "crates": "artifact", "golang": "artifact", "maven": "artifact", "nuget": "artifact",
        "pub": "artifact", "docker": "artifact", "cdn": "artifact",
        "terraform": "deploy",
    }
    os_plats = {"linux", "windows", "macos"}

    def technique_stages(tid, t):
        realms = t.get("realm") or []
        if isinstance(realms, str):
            realms = [realms]
        found = {realm_stage[r] for r in realms if r in realm_stage}
        if tid in dev_ids:
            found.add("dev")
        return found

    tech_in = {k: [] for k, _, _ in stage_meta}
    unplaced = []
    spanning = 0
    for tid, t in sorted(techs.items()):
        found = technique_stages(tid, t)
        if not found:
            unplaced.append((tid, t.get("summary") or ""))
        else:
            if len(found) > 1:
                spanning += 1
            for k in found:
                tech_in[k].append((tid, t.get("summary") or ""))
    inc_in = {k: set() for k, _, _ in stage_meta}
    plat_in = {k: {} for k, _, _ in stage_meta}
    endpoint_only = 0
    for s in stories.values():
        plats = [p for p in (s.get("platforms") or []) if p]
        touched = set()
        for p in plats:
            if p in plat_stage:
                touched.add(plat_stage[p])
                plat_in[plat_stage[p]][p] = plat_in[plat_stage[p]].get(p, 0) + 1
        if touched:
            for k in touched:
                inc_in[k].add(s["id"])
        elif plats and all(p in os_plats for p in plats):
            endpoint_only += 1
    cols = []
    for key, title, defin in stage_meta:
        examples = tech_in[key][:5]
        lis = "".join(
            f'<li><a href="techniques/{html.escape(tid)}.html">{html.escape(tid)}</a> {html.escape(name)}</li>'
            for tid, name in examples
        )
        chips = " ".join(
            f'<span class="plat">{html.escape(plat_labels.get(p, p))} {n}</span>'
            for p, n in sorted(plat_in[key].items(), key=lambda kv: -kv[1])[:6]
        )
        cols.append(
            f'<div class="flow-col"><h2>{html.escape(title)}</h2>'
            f'<p class="def">{html.escape(defin)}</p>'
            f'<div class="n">{len(inc_in[key])}</div><div class="lbl">incidents touch this stage</div>'
            f'<div class="n">{len(tech_in[key])}</div><div class="lbl">techniques, including ones that also sit elsewhere</div>'
            f'<p>{chips}</p><ul>{lis}</ul></div>'
        )
    un_lis = "".join(
        f'<li><a href="techniques/{html.escape(tid)}.html">{html.escape(tid)}</a> {html.escape(name)}</li>'
        for tid, name in unplaced
    )
    pipeline = f"""
    <h1>Five-stage cut</h1>
    <p class="lede">Not in the nav. A reading of the catalogue as five supply-chain stages,
    using the platform and realm tags we already have. Nothing was retagged for this page.</p>
    <div class="flow">{''.join(cols)}</div>
    <h2>Does this cover the five?</h2>
    <p>Yes, in pieces. No, not as five sections. Repository, CI/CD, and registries are thick.
    The developer environment has incident tags (IDE, agents, MCP) and only a handful of techniques,
    and those techniques are also tagged as CI or source control. Deployment and cloud have many
    techniques and almost no incident tags: we record the registry or the operating system, not the
    place it was deployed. {endpoint_only} incidents are tagged only Windows, Linux, or macOS, which
    is not one of these stages. {spanning} techniques sit in more than one stage already.</p>
    <p>A flow of these five is a useful second view. It should not replace the matrix until the tags
    match the stages. Repo-jacking and malicious commits are tagged open-source security, so this
    cut files them under artifact, not repository.</p>
    <h2>Not a pipeline stage</h2>
    <ul>{un_lis}</ul>
    <p class="muted">Application bugs inherited with the technique set. They are not a sixth stage.</p>
    """
    write(os.path.join(dest, "pipeline.html"), page("Five-stage cut", pipeline, "", "SCIC / Preview"))

    print(
        f"Built site → {dest} ({n_tech} techniques, {n_story} incidents)"
    )


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--dest", default=os.path.join(ROOT, "docs"))
    args = p.parse_args()
    build(args.dest)
