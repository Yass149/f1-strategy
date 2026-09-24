"""Small browser dashboard for exploring the strategy endpoints."""

from fastapi.responses import HTMLResponse

DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Race Engineer AI</title>
  <style>
    :root { color-scheme: dark; --bg:#0b1020; --panel:#141c31; --muted:#9ca9c4; --accent:#ff4d6d; --green:#41d38a; }
    * { box-sizing:border-box; } body { margin:0; font:16px system-ui,sans-serif; background:linear-gradient(135deg,#0b1020,#182342); color:#f6f8ff; }
    main { max-width:1080px; margin:auto; padding:48px 24px; } .eyebrow { color:var(--accent); font-weight:700; letter-spacing:.12em; text-transform:uppercase; }
    h1 { font-size:clamp(2.4rem,7vw,5rem); line-height:1; margin:12px 0; } p { color:var(--muted); max-width:720px; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:18px; margin-top:32px; }
    .card { background:rgba(20,28,49,.92); border:1px solid #2c395a; border-radius:18px; padding:22px; box-shadow:0 18px 40px #05081255; }
    label { display:block; color:var(--muted); font-size:.85rem; margin:12px 0 5px; } input { width:100%; padding:10px; border-radius:9px; border:1px solid #3a496e; background:#0d1528; color:white; }
    button { margin-top:16px; width:100%; padding:11px; border:0; border-radius:9px; background:var(--accent); color:white; font-weight:700; cursor:pointer; }
    pre { white-space:pre-wrap; color:#d7e1ff; min-height:90px; } .ok { color:var(--green); }
  </style>
</head>
<body><main>
  <div class="eyebrow">Race Engineer AI</div>
  <h1>Make the pit-wall decision visible.</h1>
  <p>Explore the explainable baseline and counterfactual strategy simulator. The dashboard calls the same API exposed in Swagger.</p>
  <section class="grid">
    <form class="card" id="compare-form"><h2>Compare strategy</h2>
      <label>Laps remaining</label><input name="laps_remaining" type="number" value="20" min="0">
      <label>Current tyre age</label><input name="current_tyre_age" type="number" value="18" min="0">
      <label>Current lap pace (seconds)</label><input name="current_pace_seconds" type="number" value="90" step="0.1">
      <label>Degradation per lap</label><input name="current_degradation_seconds_per_lap" type="number" value="0.08" step="0.01">
      <label>Pit-lane loss (seconds)</label><input name="pit_loss_seconds" type="number" value="22" step="0.5">
      <button>Run counterfactual</button>
    </form>
    <article class="card"><h2>Decision output</h2><div id="result"><p>Submit the comparison to see the projected race-time difference.</p></div></article>
  </section>
  <p class="ok">● API online · <a href="/docs" style="color:#9eb5ff">Open Swagger docs</a></p>
</main>
<script>
const form = document.querySelector('#compare-form'); const result = document.querySelector('#result');
form.addEventListener('submit', async (event) => { event.preventDefault(); const data = Object.fromEntries(new FormData(form));
  for (const key of Object.keys(data)) data[key] = Number(data[key]);
  result.innerHTML = '<p>Calculating...</p>';
  const response = await fetch('/strategy/compare', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
  const output = await response.json(); result.innerHTML = response.ok ? `<h3>${output.recommendation}</h3><pre>${JSON.stringify(output, null, 2)}</pre>` : `<pre>${JSON.stringify(output, null, 2)}</pre>`;
});
</script></body></html>"""


def dashboard() -> HTMLResponse:
    return HTMLResponse(DASHBOARD_HTML)
