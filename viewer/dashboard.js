const fmt = (v, d = 1) => (v === null || v === undefined) ? "–" : Number(v).toFixed(d);
async function getJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.json();
}
async function load() {
  try {
    const summary = await getJSON("/api/v1/project/summary");
    document.getElementById("hosts").textContent = summary.active_hosts_7d;
    document.getElementById("perday").textContent = fmt(summary.wus_per_day);
    const { bins } = await getJSON("/api/v1/science/cascades");
    const body = document.getElementById("bins");
    body.replaceChildren();
    for (const b of bins) {
      const row = body.insertRow();
      const ci = b.ci95_low === null ? "–" : `${fmt(b.ci95_low)} – ${fmt(b.ci95_high)}`;
      for (const v of [b.material, b.potential_id, fmt(b.pka_energy_ev, 0), fmt(b.temperature_k, 0), b.n,
                       fmt(b.mean_frenkel), fmt(b.se_frenkel), ci]) row.insertCell().textContent = v;
    }
    if (!bins.length) body.insertRow().insertCell().textContent = "No validated cascades yet.";
  } catch (e) {
    document.getElementById("error").textContent = `Could not load statistics (${e.message}).`;
  }
}
load();
