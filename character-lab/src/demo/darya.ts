import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import './darya.css';

const canvas = document.querySelector<HTMLCanvasElement>('#stage')!;
const viewport = canvas.parentElement!;
const status = document.querySelector<HTMLElement>('#status')!;
const loading = document.querySelector<HTMLElement>('#loading')!;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 0.05, 40);
camera.position.set(2.5, 1.65, 4.2);
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.35;
const controls = new OrbitControls(camera, canvas);
controls.target.set(0, .98, 0);
controls.enableDamping = true;
controls.minDistance = 1.2;
controls.maxDistance = 7;
controls.maxPolarAngle = Math.PI * .51;
controls.enablePan = false;
scene.add(new THREE.HemisphereLight(0xdbe7e4, 0x393027, 2.4));
function light(color: number, intensity: number, x: number, y: number, z: number) {
  const l = new THREE.DirectionalLight(color, intensity); l.position.set(x, y, z); scene.add(l); return l;
}
const key = light(0xffdeb2, 3, 3, 5, 4); key.castShadow = true;
key.shadow.mapSize.set(1024, 1024); key.shadow.camera.left = -3; key.shadow.camera.right = 3;
key.shadow.camera.top = 4; key.shadow.camera.bottom = -3; key.shadow.bias = -.001;
light(0xa0d4da, 2, -3, 3, -2);
const floor = new THREE.Mesh(new THREE.CylinderGeometry(1.18, 1.24, .10, 72), new THREE.MeshStandardMaterial({ color: 0x3b423c, roughness: .9 }));
floor.position.y = -.055; floor.receiveShadow = true; scene.add(floor);
const ring = new THREE.Mesh(new THREE.TorusGeometry(1.19, .004, 6, 100), new THREE.MeshStandardMaterial({ color: 0xb59a67, metalness: .6, roughness: .4 }));
ring.rotation.x = Math.PI / 2; ring.position.y = .002; scene.add(ring);
const ground = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.ShadowMaterial({ opacity: .3 }));
ground.rotation.x = -Math.PI / 2; ground.position.y = -.11; ground.receiveShadow = true; scene.add(ground);

const labels: Record<string, string> = { Idle: 'Đứng chờ', Walk: 'Đi bộ', Run: 'Chạy', Crouch: 'Ngồi thấp', Jump: 'Nhảy', KnifeSlash: 'Chém dao', RifleIdle: 'Cầm súng', RifleWalk: 'Đi cầm súng', Fire: 'Bắn thử', Reload: 'Thay đạn' };
const oneShots = new Set(['Jump', 'KnifeSlash', 'Fire', 'Reload']);
const actions = new Map<string, THREE.AnimationAction>();
let mixer: THREE.AnimationMixer | undefined;
let active: THREE.AnimationAction | undefined;
let model: THREE.Group | undefined;
let weapon: 'knife' | 'rifle' = 'knife';
let paused = false;
const motions = document.querySelector<HTMLElement>('#motions')!;
for (const [clip, label] of Object.entries(labels)) {
  const button = document.createElement('button'); button.dataset.clip = clip; button.textContent = label; button.disabled = true;
  button.setAttribute('aria-pressed', 'false'); button.addEventListener('click', () => play(clip)); motions.append(button);
}
function setWeapon(value: 'knife' | 'rifle') {
  weapon = value;
  if (model) {
    const dagger = model.getObjectByName('Dagger'); if (dagger) dagger.visible = value === 'knife';
    const rifle = model.getObjectByName('Rifle'); if (rifle) rifle.visible = value === 'rifle';
  }
  document.querySelectorAll<HTMLButtonElement>('[data-weapon]').forEach(b => { b.classList.toggle('selected', b.dataset.weapon === value); b.setAttribute('aria-pressed', String(b.dataset.weapon === value)); });
}
function play(name: string) {
  const action = actions.get(name); if (!action) return;
  setWeapon(name.startsWith('Rifle') || name === 'Fire' || name === 'Reload' ? 'rifle' : 'knife');
  paused = false; syncPause();
  action.reset().setEffectiveTimeScale(1).setEffectiveWeight(1);
  action.setLoop(oneShots.has(name) ? THREE.LoopOnce : THREE.LoopRepeat, oneShots.has(name) ? 1 : Infinity);
  action.clampWhenFinished = oneShots.has(name);
  if (active && active !== action) active.fadeOut(.16);
  action.fadeIn(.16).play(); active = action;
  document.querySelector<HTMLElement>('#current')!.textContent = labels[name];
  document.querySelectorAll<HTMLButtonElement>('[data-clip]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.clip === name)));
  document.body.dataset.motion = name;
}
function syncPause() {
  const b = document.querySelector<HTMLButtonElement>('#pause')!;
  b.textContent = paused ? 'Tiếp tục' : 'Tạm dừng'; b.setAttribute('aria-pressed', String(paused));
}
document.querySelectorAll<HTMLButtonElement>('[data-weapon]').forEach(b => b.addEventListener('click', () => play(b.dataset.weapon === 'rifle' ? 'RifleIdle' : 'Idle')));
document.querySelector('#pause')!.addEventListener('click', () => { paused = !paused; syncPause(); });
document.querySelector('#rotate')!.addEventListener('click', e => { controls.autoRotate = !controls.autoRotate; (e.currentTarget as HTMLElement).setAttribute('aria-pressed', String(controls.autoRotate)); });
document.querySelectorAll<HTMLButtonElement>('[data-view]').forEach(b => b.addEventListener('click', () => {
  controls.autoRotate = false; document.querySelector('#rotate')!.setAttribute('aria-pressed', 'false');
  if (b.dataset.view === 'detail') { controls.target.set(0, 1.4, 0); camera.position.set(.75, 1.62, 1.6); }
  else { controls.target.set(0, .98, 0); camera.position.set(b.dataset.view === 'back' ? -2 : 2, 1.65, b.dataset.view === 'back' ? -4.2 : 4.2); }
}));
new GLTFLoader().load(import.meta.env.BASE_URL + 'models/darya/darya.glb', gltf => {
  model = gltf.scene; scene.add(model);
  model.traverse(o => { if (o instanceof THREE.Mesh) { o.castShadow = true; o.receiveShadow = true; o.frustumCulled = false; } });
  mixer = new THREE.AnimationMixer(model);
  for (const clip of gltf.animations) actions.set(clip.name, mixer.clipAction(clip));
  const missing = Object.keys(labels).filter(n => !actions.has(n));
  if (missing.length) { loading.textContent = 'Thiếu animation: ' + missing.join(', '); status.textContent = 'Lỗi dữ liệu animation'; return; }
  mixer.addEventListener('finished', () => play(weapon === 'rifle' ? 'RifleIdle' : 'Idle'));
  document.querySelectorAll<HTMLButtonElement>('[data-clip]').forEach(b => { b.disabled = false; });
  loading.hidden = true; status.textContent = 'Sẵn sàng · 10 animation'; play('Idle'); document.body.dataset.ready = 'true';
}, undefined, () => { loading.textContent = 'Không tải được nhân vật. Vui lòng tải lại trang.'; status.textContent = 'Tải model thất bại'; });
new ResizeObserver(() => { const w = viewport.clientWidth, h = viewport.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }).observe(viewport);
const clock = new THREE.Clock();
renderer.setAnimationLoop(() => {
  const dt = Math.min(clock.getDelta(), .05);
  if (mixer && !paused) mixer.update(dt * Number((document.querySelector('#speed') as HTMLSelectElement).value));
  controls.update(); renderer.render(scene, camera);
});
window.addEventListener('keydown', e => {
  if (e.target instanceof HTMLSelectElement || e.target instanceof HTMLInputElement || e.repeat) return;
  const keys: Record<string, string> = { '1': 'Idle', '2': 'RifleIdle', w: weapon === 'rifle' ? 'RifleWalk' : 'Walk', Shift: 'Run', c: 'Crouch', ' ': 'Jump', f: weapon === 'rifle' ? 'Fire' : 'KnifeSlash', r: 'Reload' };
  if (keys[e.key]) { e.preventDefault(); play(keys[e.key]); }
});
window.addEventListener('pagehide', () => { renderer.setAnimationLoop(null); controls.dispose(); renderer.dispose(); }, { once: true });
