const PULSE_MESH = __PULSE_MESH__;
let pulseParts;

defineGun('pulse_h03', 'rifle', ({ g, info }) => {
  if (!pulseParts) {
    pulseParts = PULSE_MESH.map(([[rgb, metalness, roughness, emission], coordinates, indices]) => {
      const color = new THREE.Color(...rgb);
      const material = new THREE.MeshStandardMaterial({
        color, metalness, roughness, emissive: color, emissiveIntensity: emission > 0 ? 0.85 : 0,
      });
      if (emission > 0) material.userData.pulseEnergy = true;
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.Float32BufferAttribute(coordinates.map((n) => n / 10000), 3));
      geometry.setIndex(indices);
      geometry.computeVertexNormals();
      return [geometry, material];
    });
  }
  for (const [geometry, material] of pulseParts) g.add(new THREE.Mesh(geometry, material));
  info.gripR.set(0, -0.083, 0.068);
  info.gripL.set(0, -0.054, -0.285);
  info.butt = [0, 0, 0.34];
  info.muzzle.position.set(0, 0.033, -0.686);
  info.sightY = 0.168;
  info.adsZ = 0.19;
});

const PULSE_BEAMS = [];
function pulseShotFx(from, to, impact) {
  const dir = to.clone().sub(from), distance = dir.length();
  if (distance > 0.001) {
    let beam = PULSE_BEAMS.find((b) => !b.mesh.visible);
    if (!beam && PULSE_BEAMS.length < 16) {
      const mesh = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 1, 8),
        new THREE.MeshBasicMaterial({ color: 0x32ff75, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
      scene.add(mesh);
      beam = { mesh, time: 0 };
      PULSE_BEAMS.push(beam);
    }
    beam ||= PULSE_BEAMS.reduce((oldest, b) => b.time < oldest.time ? b : oldest);
    beam.time = 0.17;
    beam.mesh.visible = true;
    beam.mesh.material.opacity = 1;
    beam.mesh.position.copy(from).lerp(to, 0.5);
    beam.mesh.quaternion.setFromUnitVectors(UP, dir.multiplyScalar(1 / distance));
    beam.mesh.scale.set(0.031, distance, 0.031);
  }
  if (!impact) return;
  FX.add.spawn(to.x, to.y, to.z, 0, 0, 0, 0.14, 0.34, 1.06, 0.24, 3.4, 0.78, 1, 0);
  for (let i = 0; i < 18; i++) {
    FX.add.spawn(to.x, to.y, to.z, rand(-6, 6), rand(-4, 6), rand(-6, 6),
      rand(0.15, 0.34), 0.036, 0.008, 0.34, 3.6, 0.88, 0.94, 0, 2, 2);
  }
  flashLight(to, 5, 10, 0.18, 0x54ff88);
}
function pulseUpdateFx(dt) {
  for (const beam of PULSE_BEAMS) {
    if (!beam.mesh.visible) continue;
    beam.time -= dt;
    beam.mesh.visible = beam.time > 0;
    beam.mesh.material.opacity = Math.max(0, beam.time / 0.17);
  }
}
