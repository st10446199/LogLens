"""Self-contained HTML reports. Every log-derived string is escaped."""
from html import escape

def html_report(data, title):
    def e(value):
        return escape(str(value), quote=True)
    rows = "".join(f"<tr><td>{e(g['service'])}</td><td><span class='tag'>{e(g['level'])}</span></td><td class='message'>{e(g['message'])}</td><td>{g['count']}</td></tr>" for g in data["groups"])
    if not rows:
        rows = "<tr><td colspan='4'>No error groups found in the parsed records.</td></tr>"
    maximum = max((p["count"] for p in data["timeline"]), default=1)
    bars = "".join(f"<div class='barrow'><time>{e(p['minute'])}</time><div class='track'><div class='bar' style='width:{p['count'] / maximum * 100:.2f}%'></div></div><b>{p['count']}</b></div>" for p in data["timeline"])
    levels = "".join(f"<span class='level'>{e(k)} <b>{v}</b></span>" for k,v in data["levels"].items())
    services = "".join(f"<li>{e(k)} <b>{v}</b></li>" for k,v in data["services"].items())
    note = "Numeric and UUID normalization enabled. Groups are heuristic and can combine unrelated events." if data["normalized"] else "Exact message grouping. Service and severity are included in every group."
    skipped = ", ".join(map(str, data["malformed_lines"])) or "None"
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)} | LogLens</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#101820;color:#e7edf4;font:15px/1.6 system-ui}}main{{max-width:1200px;margin:auto;padding:40px}}header{{display:flex;justify-content:space-between;border-bottom:1px solid #33414e;padding-bottom:20px}}.brand{{font-size:24px;font-weight:700}}.accent{{color:#91d7ef}}.eyebrow{{color:#91d7ef;font-size:11px;letter-spacing:2px}}h1{{font-size:44px;line-height:1.15;margin:20px 0}}p,.muted{{color:#a8b7c7}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:32px 0}}.card{{background:#1b2834;border:1px solid #354653;border-radius:10px;padding:24px}}.card strong{{display:block;font-size:36px}}.card span{{color:#a8b7c7;font-size:12px}}.card.error strong{{color:#ffb2a4}}section{{margin-top:32px}}h2{{font-size:23px}}.panel{{background:#16222d;border:1px solid #33414e;border-radius:10px;padding:24px}}.barrow{{display:flex;align-items:center;gap:16px;font-size:12px;margin:12px 0}}.barrow time{{width:200px;flex-shrink:0;color:#a8b7c7}}.track{{flex:1;background:#233849;height:12px;border-radius:4px;overflow:hidden}}.bar{{height:100%;background:#91d7ef}}.barrow b{{width:28px}}.scroll{{overflow:auto;max-height:440px}}table{{border-collapse:collapse;width:100%}}th,td{{padding:16px;text-align:left;border-bottom:1px solid #33414e;vertical-align:top}}th{{font-size:11px;text-transform:uppercase;color:#a8b7c7;letter-spacing:1px}}.message{{font:13px/1.6 ui-monospace,monospace;overflow-wrap:anywhere;min-width:240px}}.tag{{color:#ffb2a4;background:#382d31;font-size:10px;padding:4px 8px;border-radius:4px}}.level{{display:inline-block;background:#233849;border-radius:5px;margin:0 8px 8px 0;padding:8px 12px;font-size:12px}}.level b{{margin-left:12px}}ul{{padding-left:20px}}li b{{margin-left:16px}}footer{{border-top:1px solid #33414e;margin-top:40px;padding-top:18px;font-size:12px;color:#a8b7c7}}@media(max-width:650px){{main{{padding:20px}}.cards{{grid-template-columns:1fr 1fr}}h1{{font-size:32px}}.barrow time{{width:145px;font-size:10px}}.panel{{padding:12px}}.card{{padding:15px}}}}
</style></head><body><main><header><span class="brand">Log<span class="accent">Lens</span></span><span class="eyebrow">OFFLINE DIAGNOSTICS</span></header>
<p class="eyebrow" style="margin-top:36px">APPLICATION HEALTH / LOG SUMMARY</p><h1>{e(title)}</h1><p>From individual events to recurring patterns.</p>
<div class="cards"><div class="card"><strong>{data['total']:,}</strong><span>PARSED RECORDS</span></div><div class="card error"><strong>{data['errors']:,}</strong><span>ERROR + CRITICAL</span></div><div class="card"><strong>{data['error_rate']}%</strong><span>ERROR RATE</span></div><div class="card"><strong>{data['skipped']:,}</strong><span>SKIPPED RECORDS</span></div></div>
<section><h2>Error timeline <span class="muted">/ UTC minutes</span></h2><div class="panel scroll">{bars or '<p>No error events to plot.</p>'}</div><p>Only minutes containing errors are listed; absent minutes have no recorded errors.</p></section>
<section><h2>Recurring errors</h2><p>{e(note)}</p><div class="panel scroll"><table><thead><tr><th>Service</th><th>Severity</th><th>Message / pattern</th><th>Count</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section><h2>Record distribution</h2><div class="panel">{levels or '<p>No valid records.</p>'}<ul>{services}</ul></div></section>
<section><h2>Parsing details</h2><p>Range: {e(data['first'] or 'None')} to {e(data['last'] or 'None')}. All displayed times use UTC.</p><p>First 20 malformed line numbers: {e(skipped)}. Blank lines are ignored.</p></section>
<footer>LogLens · Generated locally. Reports include log messages; review their contents before sharing.</footer></main></body></html>'''
