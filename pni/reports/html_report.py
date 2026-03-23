"""HTML report generation for investigation results."""

from __future__ import annotations

import os
import datetime

from pni.core.models import InvestigationResult


def save_html_report(result: InvestigationResult, output_dir: str) -> str:
    """Generate a dark-themed HTML report and save it."""
    query = result.query
    safe_value = "".join(c if c.isalnum() or c in ".-_" else "_" for c in query.value)[:50]
    path = os.path.join(output_dir, f"pni_{query.query_type.value}_{safe_value}.html")
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Group by category
    categories: dict[str, list] = {}
    for r in result.results:
        categories.setdefault(r.category, []).append(r)

    def badge(status: str) -> str:
        colors = {"found": "#55ff55", "not_found": "#888", "error": "#ff5555"}
        c = colors.get(status, "#888")
        return f"<span style='background:#111;color:{c};border:1px solid {c};padding:1px 6px;border-radius:3px;font-size:0.75em;'>{status.upper()}</span>"

    def render_data(data: dict) -> str:
        rows = []
        for k, v in data.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                for i, item in enumerate(v[:5], 1):
                    detail = " | ".join(f"{ik}: {iv}" for ik, iv in item.items() if iv)
                    rows.append(f"<tr><td class='k'>{k} #{i}</td><td>{_esc(detail[:300])}</td></tr>")
            elif isinstance(v, list):
                rows.append(f"<tr><td class='k'>{k}</td><td>{_esc(', '.join(str(x) for x in v))}</td></tr>")
            elif isinstance(v, dict):
                for dk, dv in v.items():
                    rows.append(f"<tr><td class='k'>{k}.{dk}</td><td>{_esc(str(dv)[:300])}</td></tr>")
            else:
                rows.append(f"<tr><td class='k'>{k}</td><td>{_esc(str(v))}</td></tr>")
        return "\n".join(rows) or "<tr><td colspan='2' style='color:#555'>No data</td></tr>"

    sections = ""
    cat_icons = {
        "analysis": "&#128269;", "search": "&#128270;", "reputation": "&#11088;",
        "breach": "&#128274;", "social": "&#128241;", "api": "&#9881;",
        "archive": "&#128218;", "paste": "&#128203;",
    }

    for cat, items in categories.items():
        found_ct = sum(1 for i in items if i.status == "found")
        icon = cat_icons.get(cat, "&#128196;")
        sections += f"<h2>{icon} {cat.upper()} <small style='color:#666'>({found_ct}/{len(items)} hits)</small></h2>\n"

        for item in items:
            url_row = f"<tr><td class='k'>URL</td><td><a href='{_esc(item.url)}' target='_blank'>{_esc(item.url[:100])}</a></td></tr>" if item.url else ""
            snippet_row = f"<tr><td class='k'>Snippet</td><td>{_esc(item.snippet[:300])}</td></tr>" if item.snippet else ""
            data_rows = render_data(item.data) if item.data else ""

            sections += f"""
<div class='finding {item.status}'>
  <div class='finding-header'>
    <span class='finding-source'>{_esc(item.source_name)}</span>
    {badge(item.status)}
    <span class='finding-title'>{_esc(item.title[:100])}</span>
  </div>
  <table class='info-table'>{url_row}{snippet_row}{data_rows}</table>
</div>"""

    html = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>PNI Report — {_esc(query.value)}</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Courier New',monospace;background:#080808;color:#ddd;padding:28px;max-width:1200px;margin:auto}}
  h1{{color:#ff2222;font-size:1.6em;border-bottom:2px solid #ff2222;padding-bottom:10px;margin-bottom:10px}}
  h2{{color:#ff6644;margin:28px 0 10px;font-size:1em;text-transform:uppercase;letter-spacing:2px;border-left:3px solid #ff6644;padding-left:8px}}
  .meta{{color:#555;font-size:0.8em;margin-bottom:20px}}
  .warn{{background:#150505;border:1px solid #ff2222;border-radius:4px;padding:10px;color:#ff9999;font-size:0.8em;margin-bottom:20px}}
  .summary{{display:flex;gap:16px;margin-bottom:24px}}
  .stat{{background:#111;border:1px solid #333;border-radius:6px;padding:14px 22px;text-align:center}}
  .stat .n{{font-size:2em;font-weight:bold;color:#ff4444}}
  .stat .l{{font-size:0.75em;color:#888;text-transform:uppercase}}
  .stat.green .n{{color:#44ff88}}
  .info-table{{width:100%;border-collapse:collapse;margin:8px 0 16px}}
  .info-table td{{padding:4px 10px;border:1px solid #1a1a1a;font-size:0.82em}}
  .k{{color:#66aaff;width:180px;background:#0d0d0d}}
  .finding{{background:#0d0d0d;border:1px solid #1e1e1e;border-radius:4px;margin-bottom:10px;overflow:hidden}}
  .finding.found{{border-color:#1a3a1a}}
  .finding.error{{border-color:#1a0000}}
  .finding-header{{background:#111;padding:8px 12px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
  .finding-source{{color:#ffaa44;font-weight:bold;font-size:0.85em;min-width:160px}}
  .finding-title{{color:#888;font-size:0.8em;flex:1}}
  a{{color:#66aaff;text-decoration:none}}
  a:hover{{text-decoration:underline}}
</style>
</head>
<body>
<h1>PNI — {_esc(query.query_type.value.upper())} Investigation Report</h1>
<div class='meta'>PNI v0.1.0 &nbsp;|&nbsp; by d3vn0mi &nbsp;|&nbsp; Generated: {ts} &nbsp;|&nbsp; Target: <strong style='color:#ff6644'>{_esc(query.value)}</strong></div>
<div class='warn'>This report is for authorized security research and OSINT investigations only.</div>

<div class='summary'>
  <div class='stat'><div class='n'>{result.total_count}</div><div class='l'>Total Checks</div></div>
  <div class='stat green'><div class='n'>{result.found_count}</div><div class='l'>Hits Found</div></div>
  <div class='stat'><div class='n'>{result.total_count - result.found_count}</div><div class='l'>No Result</div></div>
</div>

{sections}

<div class='meta' style='margin-top:20px'>Generated by PNI (Phone Number Investigator) — d3vn0mi</div>
</body>
</html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def _esc(text: str) -> str:
    """Basic HTML escaping."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
