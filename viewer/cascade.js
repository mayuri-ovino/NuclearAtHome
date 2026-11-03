// Full-screen Three.js viewer for one finished cascade. Reads the sparse LAMMPS snapshot dump
// (columns: id type x y z c_ke c_ws[1] f_ref[1] f_ref[2] f_ref[3]) from the read-only API.
import * as THREE from "three";
import { OrbitControls } from "./vendor/OrbitControls.js";

const $ = (id) => document.getElementById(id);
const canvas = $("view");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 20000);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.autoRotateSpeed = 0.8;

// Sky: a vertical gradient, deep teal at the horizon to near-black overhead.
const sky = document.createElement("canvas");
sky.width = 2; sky.height = 256;
const g = sky.getContext("2d");
const grad = g.createLinearGradient(0, 0, 0, 256);
grad.addColorStop(0, "#05080d"); grad.addColorStop(0.62, "#0b1a24"); grad.addColorStop(1, "#102f3a");
g.fillStyle = grad; g.fillRect(0, 0, 2, 256);
scene.background = new THREE.CanvasTexture(sky);
scene.background.colorSpace = THREE.SRGBColorSpace;
scene.add(new THREE.HemisphereLight(0xbfe8ff, 0x10202a, 1.1));
const sun = new THREE.DirectionalLight(0xffffff, 1.4);
sun.position.set(1, 2, 1.5);
scene.add(sun);

const MAX = 200000;
const atomMat = new THREE.MeshStandardMaterial({ roughness: 0.35, metalness: 0.1, emissiveIntensity: 0.6 });
const atoms = new THREE.InstancedMesh(new THREE.SphereGeometry(1.0, 16, 12), atomMat, MAX);
const vacancies = new THREE.InstancedMesh(new THREE.BoxGeometry(1.5, 1.5, 1.5),
  new THREE.MeshStandardMaterial({ color: 0x9aa7b4, transparent: true, opacity: 0.55, roughness: 0.6 }), MAX);
// Instanced meshes are culled by the bounding sphere of ONE instance at the origin, which made the
// cascade vanish while rotating. The whole cascade is always worth drawing, so never cull them.
atoms.frustumCulled = vacancies.frustumCulled = false;
scene.add(atoms, vacancies);

let grid = null;
let frames = [];
let current = 0;
let playing = false;
let views = [];

async function readText(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  const bytes = new Uint8Array(await r.arrayBuffer());
  if (!(bytes[0] === 0x1f && bytes[1] === 0x8b)) return new TextDecoder().decode(bytes);
  // BOINC stores uploads gzipped: inflate in chunks and stop at the cap (no decompression bomb).
  const MAX_BYTES = 150e6;
  const reader = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip")).getReader();
  const chunks = [];
  let total = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    total += value.length;
    if (total > MAX_BYTES) { reader.cancel(); throw new Error("snapshot too large"); }
    chunks.push(value);
  }
  return new TextDecoder().decode(await new Blob(chunks).arrayBuffer());
}

function parseDump(text) {
  const lines = text.split(/\r?\n/);  // Windows LAMMPS writes \r\n
  const out = [];
  for (let i = 0; i + 1 < lines.length && lines[i] === "ITEM: TIMESTEP";) {
    const step = Number(lines[i + 1]);
    const n = Number(lines[i + 3]);
    if (i + 9 + n > lines.length || !lines[i + 8 + n]) break;  // live file: last frame still being written
    const cols = lines[i + 8].split(/\s+/).slice(2);
    const at = (name) => cols.indexOf(name);
    const idx = { x: at("x"), y: at("y"), z: at("z"), ke: at("c_ke"), occ: at("c_ws[1]"),
                  rx: at("f_ref[1]"), ry: at("f_ref[2]"), rz: at("f_ref[3]") };
    const rows = lines.slice(i + 9, i + 9 + n).map((l) => l.trim().split(/\s+/).map(Number));
    out.push({ step, rows, idx });
    i += 9 + n;
  }
  return out;
}

const color = new THREE.Color();
const matrix = new THREE.Matrix4();
function show(k) {
  current = Math.max(0, Math.min(frames.length - 1, k));
  const f = frames[current];
  if (!f) return;
  let na = 0, nv = 0;
  for (const r of f.rows) {
    if (r[f.idx.occ] === 0 && nv < MAX) {
      matrix.makeTranslation(r[f.idx.rx], r[f.idx.ry], r[f.idx.rz]);
      vacancies.setMatrixAt(nv++, matrix);
    }
    if (na < MAX) {
      matrix.makeTranslation(r[f.idx.x], r[f.idx.y], r[f.idx.z]);
      atoms.setMatrixAt(na, matrix);
      // Kinetic energy on a log scale, 0..1000 eV: deep blue (settled) through cyan to hot orange.
      const t = Math.min(1, Math.log10(1 + Math.max(0, r[f.idx.ke])) / 3);
      atoms.setColorAt(na++, color.setHSL(0.62 - 0.55 * t, 0.9, 0.45 + 0.2 * t));
    }
  }
  atoms.count = na; vacancies.count = nv;
  atoms.instanceMatrix.needsUpdate = vacancies.instanceMatrix.needsUpdate = true;
  if (atoms.instanceColor) atoms.instanceColor.needsUpdate = true;
  $("counter").textContent = `${current + 1} of ${frames.length}`;
  $("f-step").textContent = `${f.step.toLocaleString()} · ${nv} empty sites`;
}

function setView(i) {
  if (!views[i]) return;
  camera.position.copy(views[i]);
  controls.target.copy(views.center);
  controls.update();
  for (const b of document.querySelectorAll(".view")) b.toggleAttribute("aria-pressed", Number(b.dataset.view) === i);
}

function fact(term, value, id) {
  const dt = document.createElement("dt"); dt.textContent = term;
  const dd = document.createElement("dd"); dd.textContent = value;
  if (id) dd.id = id;
  return [dt, dd];
}

async function open(wu) {
  $("error").textContent = "";
  try {
    const metaResp = await fetch(`/api/v1/cascades/${encodeURIComponent(wu)}/snapshots`);
    if (!metaResp.ok) throw new Error(`work unit not found (${metaResp.status})`);
    const meta = await metaResp.json();
    $("facts").replaceChildren(
      ...fact("Work unit", meta.wu_id), ...fact("Material", meta.material),
      ...fact("PKA energy", `${(meta.pka_energy_ev / 1000).toLocaleString()} keV`),
      ...fact("Temperature", `${meta.temperature_k} K`), ...fact("Frenkel pairs", meta.frenkel_pairs),
      ...fact("Points", Math.round(meta.points).toLocaleString()), ...fact("Step", "–", "f-step"));
    frames = parseDump(await readText(meta.files[0]));
    if (!frames.length) throw new Error("no snapshot frames");
    frameCamera();
    show(frames.length - 1);  // open on the surviving defects; Play replays the cascade
  } catch (e) {
    $("error").textContent = `Could not open the cascade: ${e.message}`;
  }
}

// Fit the grid, fog and the three camera views to the cascade's bounding box.
function frameCamera() {
    const box = new THREE.Box3();
    for (const f of frames) for (const r of f.rows) box.expandByPoint(new THREE.Vector3(r[f.idx.x], r[f.idx.y], r[f.idx.z]));
    const center = box.getCenter(new THREE.Vector3());
    const size = Math.max(...box.getSize(new THREE.Vector3()).toArray(), 40)  // a cascade spans ~30-50 Å;
    const d = size * 1.4;
    // Ground grid just below the cascade, to give a sense of space and scale (1 cell = 5 Å).
    if (grid) scene.remove(grid);
    grid = new THREE.GridHelper(size * 12, Math.round(size * 12 / 5), 0x2f5a66, 0x1a333b);
    grid.position.set(center.x, box.min.y - size * 0.25, center.z);
    scene.add(grid);
    scene.fog = new THREE.Fog(0x0b1a24, d * 1.5, d * 6);
    views = [center.clone().add(new THREE.Vector3(1, 0.45, 1).normalize().multiplyScalar(d)),
             center.clone().add(new THREE.Vector3(0, d, 0.001)),
             center.clone().add(new THREE.Vector3(d, 0, 0))];
    views.center = center;
    setView(0);
}

// Live mode: the tasks running on this computer, served read-only by scripts/serve.py.
let liveSlot = new URLSearchParams(location.search).get("slot");

async function listTasks() {
  const tasks = await (await fetch("/live/tasks.json", { cache: "no-store" })).json();
  const select = $("task");
  const options = tasks.map((t) => {
    const o = document.createElement("option");
    o.value = t.slot;
    o.textContent = `${t.wu} · ${(t.progress * 100).toFixed(0)}%`;
    return o;
  });
  select.replaceChildren(...options);
  if (!tasks.some((t) => t.slot === liveSlot)) liveSlot = tasks.length ? tasks[0].slot : null;  // most advanced
  select.value = liveSlot ?? "";
  $("task-pick").hidden = !tasks.length;
  return tasks.length;
}

async function pollLive() {
  try {
    if (!(await listTasks())) {
      $("facts").replaceChildren(...fact("Work unit", "no Nuclear@Home task is running on this computer"));
      return;
    }
    const base = `/live/${encodeURIComponent(liveSlot)}`;
    const progress = Number(await (await fetch(`${base}/progress.txt`, { cache: "no-store" })).text());
    const r = await fetch(`${base}/snapshots.dump`, { cache: "no-store" });
    const fresh = r.ok ? parseDump(await r.text()) : [];
    const following = current >= frames.length - 1;
    const first = !frames.length && fresh.length;
    frames = fresh;
    $("facts").replaceChildren(...fact("Work unit", $("task").selectedOptions[0]?.textContent.split(" · ")[0] ?? "–"),
      ...fact("Progress", Number.isFinite(progress) ? `${(progress * 100).toFixed(1)}% of 20 ps` : "warming up"),
      ...fact("Frames", frames.length || "none yet (cascade starts after the 10 ps warm-up)"), ...fact("Step", "–", "f-step"));
    if (first) frameCamera();
    if (frames.length) show(following ? frames.length - 1 : current);
    $("error").textContent = "";
  } catch (e) {
    $("error").textContent = `Live view unavailable: ${e.message}`;
  }
}

function resize() {
  const w = innerWidth, h = innerHeight;
  if (canvas.width !== Math.floor(w * renderer.getPixelRatio())) {
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
}
let last = 0;
renderer.setAnimationLoop((t) => {
  resize();
  if (playing && frames.length && t - last > 250) {
    last = t;
    show(current + 1 < frames.length ? current + 1 : 0);
  }
  controls.update();
  renderer.render(scene, camera);
});

function setPlaying(on) {
  playing = on;
  $("play").textContent = on ? "❚❚" : "▶";
  $("play").setAttribute("aria-label", on ? "Pause" : "Play");
}
$("prev").addEventListener("click", () => { setPlaying(false); show(current - 1); });
$("next").addEventListener("click", () => { setPlaying(false); show(current + 1); });
$("play").addEventListener("click", () => setPlaying(!playing));
for (const b of document.querySelectorAll(".view")) b.addEventListener("click", () => setView(Number(b.dataset.view)));
$("showVac").addEventListener("change", (e) => { vacancies.visible = e.target.checked; });
$("showAtoms").addEventListener("change", (e) => { atoms.visible = e.target.checked; });
$("spin").addEventListener("change", (e) => { controls.autoRotate = e.target.checked; });
addEventListener("keydown", (e) => {
  if (e.target.tagName === "INPUT") return;
  if (e.key === "ArrowLeft") { setPlaying(false); show(current - 1); }
  if (e.key === "ArrowRight") { setPlaying(false); show(current + 1); }
  if (e.key === " ") { e.preventDefault(); setPlaying(!playing); }
});
$("pick").addEventListener("submit", (e) => { e.preventDefault(); open($("wu").value.trim()); });
const params = new URLSearchParams(location.search);
$("task").addEventListener("change", (e) => {
  liveSlot = e.target.value;
  frames = [];  // a different cascade: refit the camera to it
  pollLive();
});
if (params.has("live")) {
  $("pick").hidden = true;
  pollLive();
  setInterval(pollLive, 10000);
} else if (params.get("wu")) {
  $("wu").value = params.get("wu");
  open(params.get("wu"));
}
