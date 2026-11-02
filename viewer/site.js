// Nuclear@Home site: one page, sections switched by the URL hash. All data comes from the
// read-only API; everything is written with textContent (never innerHTML).
const $ = (id) => document.getElementById(id);
const fmt = (v, d = 1) => (v === null || v === undefined) ? "–" : Number(v).toLocaleString(undefined,
  { minimumFractionDigits: d, maximumFractionDigits: d });
const keV = (ev) => `${fmt(ev / 1000, ev % 1000 ? 1 : 0)} keV`;
const tpf = (s) => `${Math.floor(s / 60)}m ${String(Math.round(s % 60)).padStart(2, "0")}s`;

async function getJSON(url) {
  const r = await fetch(url);
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.json();
}

function fill(tbody, rows, empty) {
  tbody.replaceChildren();
  for (const cells of rows) {
    const row = tbody.insertRow();
    for (const c of cells) {
      const td = row.insertCell();
      if (c instanceof Node) td.append(c); else td.textContent = c;
    }
  }
  if (!rows.length) tbody.insertRow().insertCell().textContent = empty;
}

function fail(e) { $("error").textContent = `Could not load data (${e.message}).`; }

// Log in goes to BOINC's own login page once the project's BOINC address is configured.
getJSON("/api/v1/project/summary").then((s) => {
  if (s && s.boinc_url) $("login").href = `${s.boinc_url.replace(/\/$/, "")}/login_form.php`;
}).catch(() => {});

const pages = {
  async overview() {
    const s = await getJSON("/api/v1/project/summary");
    $("o-hosts").textContent = fmt(s.active_hosts_7d, 0);
    $("o-perday").textContent = fmt(s.wus_per_day);
    $("o-total").textContent = fmt(s.total_wus, 0);
    $("o-points").textContent = fmt(s.total_points, 0);
    const { bins } = await getJSON("/api/v1/science/cascades");
    fill($("o-bins"), bins.map((b) => [b.material, b.potential_id, keV(b.pka_energy_ev), `${fmt(b.temperature_k, 0)} K`,
      b.n, fmt(b.mean_frenkel), fmt(b.se_frenkel),
      b.ci95_low === null ? "–" : `${fmt(b.ci95_low)} – ${fmt(b.ci95_high)}`]), "No validated cascades yet.");
  },
  async workunits() {
    const { workunits } = await getJSON("/api/v1/workunits/recent");
    fill($("w-rows"), workunits.map((w) => [w.wu_id, keV(w.pka_energy_ev), `${fmt(w.temperature_k, 0)} K`,
      w.frenkel_pairs, fmt(w.points, 0), w.day, view3d(w)]), "No validated work units yet.");
  },
  async campaigns() {
    const s = await getJSON("/api/v1/project/summary");
    const c = s.campaign;
    $("c-title").textContent = `${c.id}: ${c.material}, potential ${c.potential_id}`;
    $("c-desc").textContent = `Cascades at ${c.energies_ev.map(keV).join(" and ")}, ${c.temperatures_k.map((t) => `${t} K`).join(", ")}; `
      + `${c.target_per_bin} validated runs per energy and temperature.`;
    const done = new Map(s.campaign_progress.map((p) => [`${p.pka_energy_ev}|${p.temperature_k}`, p.n]));
    const box = $("c-bins");
    box.replaceChildren();
    for (const e of c.energies_ev) for (const t of c.temperatures_k) {
      const n = done.get(`${e}|${t}`) || 0;
      const row = document.createElement("div");
      row.className = "bin";
      const label = document.createElement("span");
      label.textContent = `${keV(e)} at ${t} K`;
      const bar = document.createElement("progress");
      bar.max = c.target_per_bin; bar.value = Math.min(n, c.target_per_bin);
      bar.setAttribute("aria-label", `${keV(e)} at ${t} K`);
      const count = document.createElement("span");
      count.textContent = `${n} / ${c.target_per_bin}`;
      row.append(label, bar, count);
      box.append(row);
    }
  },
  async news() {
    const items = await getJSON("news.json");
    const list = $("n-list");
    list.replaceChildren();
    for (const n of items) {
      const card = document.createElement("article");
      card.className = "card";
      const h = document.createElement("h2"); h.textContent = n.title;
      const meta = document.createElement("p"); meta.className = "note"; meta.textContent = n.date;
      card.append(h, meta);
      for (const para of n.body) { const p = document.createElement("p"); p.textContent = para; card.append(p); }
      list.append(card);
    }
  },
  async machines() {}, async stats() {},
  async join() {
    const { boinc_url } = await getJSON("/api/v1/project/summary");
    if (boinc_url) $("j-url").textContent = `Project address: ${boinc_url}`;
  },
};

function view3d(w) {
  if (!w.has_3d) return "";
  const link = document.createElement("a");
  link.href = `cascade.html?wu=${encodeURIComponent(w.wu_id)}`;
  link.textContent = "View 3D";
  return link;
}

async function lookup(form, input, url, show) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const data = await getJSON(url(input.value.trim()));
      $("error").textContent = data ? "" : "Not found, or not public.";
      if (data) show(data);
    } catch (err) { fail(err); }
  });
}

lookup($("m-form"), $("m-id"), (id) => `/api/v1/hosts/${id}`, (h) => {
  $("m-out").hidden = false;
  $("m-est").textContent = fmt(h.est_ppd, 0);
  $("m-act").textContent = fmt(h.actual_ppd_7d, 0);
  $("m-valid").textContent = h.wus_valid_30d;
  $("m-invalid").textContent = h.wus_invalid_30d;
  fill($("m-tpf"), h.tpf_history.map((t) => [t.day, tpf(t.tpf_s)]), "No TPF samples yet.");
  const hw = h.hardware || {};
  $("m-cpu").textContent = hw.cpu || "–";
  $("m-gpu").textContent = hw.gpu || "none reported";
  $("m-os").textContent = hw.os ? `${hw.os}, ${hw.ncpus} threads` : "–";
  fill($("m-work"), h.recent_work.map((w) => {
    const status = document.createElement("span");
    status.className = `status ${w.status.replace(/ /g, "-")}`;
    status.textContent = w.status;
    return [w.project, w.core, w.resource, status, w.wu_id, w.sent || "–", w.returned || "–", view3d(w)];
  }), "No work in the last 14 days.");
});
for (const [who, api] of [["u", "users"], ["t", "teams"]]) {
  lookup($(`${who}-form`), $(`${who}-id`), (id) => `/api/v1/${api}/${id}`, (m) => {
    $(`${who}-out`).hidden = false;
    $(`${who}-rank`).textContent = m.rank ?? "–";
    $(`${who}-ppd`).textContent = fmt(m.ppd, 0);
    $(`${who}-day`).textContent = m.day;
    $(`${who}-points`).textContent = fmt(m.points, 0);
    if (who === "u") {
      const box = $("u-badges");
      box.replaceChildren(...(m.badges.length ? m.badges : ["none yet"]).map((b) => {
        const s = document.createElement("span"); s.className = "badge"; s.textContent = b; return s;
      }));
    }
  });
}

function show() {
  const name = (location.hash || "#overview").slice(1);
  const page = pages[name] ? name : "overview";
  for (const sec of document.querySelectorAll(".page")) sec.hidden = sec.id !== page;
  for (const a of document.querySelectorAll("nav a")) a.toggleAttribute("aria-current", a.hash === `#${page}`);
  $("error").textContent = "";
  pages[page]().catch(fail);
}
window.addEventListener("hashchange", show);
show();
