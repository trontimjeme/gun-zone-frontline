import fs from 'node:fs';
import assert from 'node:assert/strict';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { AnimationMixer, Vector3 } from 'three';

const bytes = fs.readFileSync(new URL('../public/models/darya/darya.glb', import.meta.url));
const data = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
const gltf = await new GLTFLoader().parseAsync(data, '');
const expected = ['Idle','Walk','Run','Crouch','Jump','KnifeSlash','RifleIdle','RifleWalk','Fire','Reload'];
assert.deepEqual(new Set(gltf.animations.map(a => a.name)), new Set(expected));
assert.ok(gltf.scene.getObjectByName('Dagger'));
assert.ok(gltf.scene.getObjectByName('Rifle'));
let skinCount = 0;
gltf.scene.traverse(o => { if (o.isSkinnedMesh) { skinCount++; assert.ok(o.skeleton.bones.length >= 18); } });
assert.ok(skinCount >= 3);
const mixer = new AnimationMixer(gltf.scene);
for (const clip of gltf.animations) {
  assert.ok(clip.duration > 0);
  mixer.stopAllAction(); mixer.clipAction(clip).play();
  for (const t of [0, clip.duration * .25, clip.duration * .5, clip.duration * .9]) {
    mixer.setTime(t); gltf.scene.updateMatrixWorld(true);
    gltf.scene.traverse(o => {
      if (!o.isSkinnedMesh) return;
      o.skeleton.update();
      const count = o.geometry.getAttribute('position').count;
      for (let i = 0; i < count; i += 37) {
        const v = o.getVertexPosition(i, new Vector3());
        assert.ok(v.toArray().every(Number.isFinite), `${clip.name} invalid skinned vertex`);
        assert.ok(v.length() < 10, `${clip.name} exploded vertex`);
      }
    });
  }
}
const run = gltf.animations.find(a => a.name === 'Run');
const legTrack = run.tracks.find(t => /Thigh.*quaternion/.test(t.name));
assert.ok(legTrack && new Set(legTrack.values).size > 10, 'Run must animate legs');
const jump = gltf.animations.find(a => a.name === 'Jump').tracks.find(t => t.name === 'Root.position');
assert.ok(jump && Math.max(...jump.values) - Math.min(...jump.values) > .3, 'Jump must lift root');
console.log(`DARYA: ${expected.length} clips, ${skinCount} skinned meshes, sampled deformations valid.`);
