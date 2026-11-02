// Three.js viewer for one finished cascade. Reads the sparse LAMMPS snapshot dump
// (columns: id type x y z c_ke c_ws[1] f_ref[1] f_ref[2] f_ref[3]) from the read-only API.
import * as THREE from "three";
import { OrbitControls } from "./vendor/OrbitControls.js";

const $ = (id) => document.getElementById(id);
const canvas = $("view");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 5000);
const controls = new OrbitControls(camera, canvas);
scene.add(new THREE.AmbientLight(0xffffff, 0.6));
const sun = new THREE.DirectionalLight(0xffffff, 0.9);
sun.position.set(1, 2, 3);
scene.add(sun);

const MAX = 200000;
const atoms = new THREE.InstancedMesh(new THREE.SphereGeometry(0.6, 10, 8), new THREE.MeshLambertMaterial(), MAX);
const vacancies = new THREE.InstancedMesh(new THREE.BoxGeometry(0.8, 0.8, 0.8),
  new THREE.MeshLambertMaterial({ color: 0x8a8a84 }), MAX);
scene.add(atoms, vacancies);
let frames = [];
let playing = false;

const MAX_SNAPSHOT_BYTES = 150e6;  // same cap the server applies; snapshots come from volunteers

async function readText(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  const bytes = new Uint8Array(await r.arrayBuffer());
  if (!(bytes[0] === 0x1f && bytes[1] === 0x8b)) return new TextDecoder().decode(bytes);
  // BOINC stores uploads gzipped: inflate in chunks and stop at the cap (no decompression bomb).
  const reader = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip")).getReader();
  const chunks = [];
  let total = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    total += value.length;
    if (total > MAX_SNAPSHOT_BYTES) { reader.cancel(); throw new Error("snapshot too large"); }
    chunks.push(value);
  }
  return new TextDecoder().decode(await new Blob(chunks).arrayBuffer());
}

function parseDump(text) {
  const lines = text.split("\n");
  const out = [];
  for (let i = 0; i + 1 < lines.length && lines[i] === "ITEM: TIMESTEP";) {
    const step = Number(lines[i + 1]);
    const n = Number(lines[i + 3]);
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
  const f = frames[k];
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
      const t = Math.min(1, Math.log10(1 + Math.max(0, r[f.idx.ke])) / 3);  // 0..1000 eV, log scale
      atoms.setColorAt(na++, color.setHSL(0.66 * (1 - t), 0.8, 0.5));
    }
  }
  atoms.count = na; vacancies.count = nv;
  atoms.instanceMatrix.needsUpdate = vacancies.instanceMatrix.needsUpdate = true;
  if (atoms.instanceColor) atoms.instanceColor.needsUpdate = true;
  $("step").textContent = `step ${f.step} · ${nv} vacancies`;
}

async function open(wu) {
  $("error").textContent = "";
  try {
    const metaResp = await fetch(`/api/v1/cascades/${encodeURIComponent(wu)}/snapshots`);
    if (!metaResp.ok) throw new Error(`work unit not found (${metaResp.status})`);
    const meta = await metaResp.json();
    $("info").textContent = `${meta.material} · PKA ${meta.pka_energy_ev} eV · ${meta.temperature_k} K · `
      + `${meta.frenkel_pairs} surviving Frenkel pairs · ${meta.points} points`;
    frames = parseDump(await readText(meta.files[0]));
    if (!frames.length) throw new Error("no snapshot frames");
    $("frame").max = frames.length - 1;
    $("frame").value = 0;
    const all = frames.flatMap((f) => f.rows.map((r) => [r[f.idx.x], r[f.idx.y], r[f.idx.z]]));
    const center = all.reduce((a, p) => a.map((v, i) => v + p[i] / all.length), [0, 0, 0]);
    controls.target.set(...center);
    camera.position.set(center[0] + 80, center[1] + 60, center[2] + 80);
    show(0);
  } catch (e) {
    $("error").textContent = `Could not open the cascade: ${e.message}`;
  }
}

function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
let last = 0;
renderer.setAnimationLoop((t) => {
  resize();
  if (playing && frames.length && t - last > 400) {
    last = t;
    $("frame").value = (Number($("frame").value) + 1) % frames.length;
    show(Number($("frame").value));
  }
  controls.update();
  renderer.render(scene, camera);
});

$("frame").addEventListener("input", (e) => show(Number(e.target.value)));
$("play").addEventListener("click", () => { playing = !playing; $("play").textContent = playing ? "Pause" : "Play"; });
$("showVac").addEventListener("change", (e) => { vacancies.visible = e.target.checked; });
$("showAtoms").addEventListener("change", (e) => { atoms.visible = e.target.checked; });
$("pick").addEventListener("submit", (e) => { e.preventDefault(); open($("wu").value.trim()); });
const initial = new URLSearchParams(location.search).get("wu");
if (initial) { $("wu").value = initial; open(initial); }
