"""Register a separate CS ROSE map inspired by the supplied brick-and-rose courtyard photograph.
This first stage changes environment identity, not level geometry. Never modifies the existing maps.
"""
from pathlib import Path

map_path = Path("src/02-map.js")
source = map_path.read_text()
needle = "const MAPS = ["
assert source.count(needle) == 1, "Map registry changed upstream"
assert "id: 'csrose'" not in source
source = source.replace(needle, """const MAPS = [
  { id: 'csitalystyle', name: 'CS ITALY STYLE', tag: 'Italy · Rose Heritage', ok: true,
    desc: 'Phố cổ Italy: tường gạch đỏ, vòm cổ điển, sân đất nung, hoa hồng leo và nắng tự nhiên.' },""", 1)
map_path.write_text(source)

sable_path = Path("src/02s-sable.js")
sable = sable_path.read_text()
assert "MAP_DEFS.italyreal = {" in sable, "Run italy_real.py first"
assert "MAP_DEFS.csitalystyle" not in sable
sable += """
/* AZONE / CS ITALY STYLE: independent selectable visual treatment.
   Stage 1: daylight, warm brick/terracotta grade, neutral stone bounce.
   Combat geometry, collision, nav, spawn and bot routes inherited unchanged.
   Future stage: real rose meshes, arches and photographic PBR textures. */
const CS_ITALY_STYLE_ATMO = {
  ...ITALY_REAL_ATMO,
  sun: [-0.38, 0.72, 0.54],
  sunColor: 0xfff1d7,
  sunI: 1.75,
  vmSun: 0xffe7c5,
  fog: [0.79, 0.79, 0.75],
  fogD: 0.0022,
  fogSun: 0.18,
  hemi: [0xc4d9ec, 0x94745d, 0.82],
  vmHemi: [0xc4d9ec, 0x94745d],
  sky: {
    ...ITALY_REAL_ATMO.sky,
    zen: [0.22, 0.49, 0.82],
    mid: [0.40, 0.67, 0.94],
    hor: [0.77, 0.86, 0.93],
    gnd: [0.57, 0.45, 0.36],
    glow: [1.0, 0.93, 0.77],
    halo: [1.0, 0.97, 0.88]
  },
  lit: false,
  lamps: 0.08,
  winLit: 0.04,
  bounce: [0.53, 0.38, 0.28],
  grade: { lo: [1.01, 0.99, 0.96], hi: [1.07, 1.02, 0.96], exp: 1.02, sat: 1.11, con: 1.09 },
  rays: [1.0, 0.92, 0.8],
  bloom: [0.12, 0.32, 0.9]
};
MAP_DEFS.csitalystyle = {
  ...MAP_DEFS.sable,
  atmo: CS_ITALY_STYLE_ATMO,
  art: { ...MAP_DEFS.sable.art },
  // New rose-and-brick environment pass, no changes to the original Sable map.
  build() { MAP_DEFS.sable.build(); buildCsRoseDecor(); }
};
function buildCsRoseDecor() {
  // Visual-only architecture details outside primary combat lanes.
  // These do not alter collision, spawns, or bot navigation.
  const M = DECOR;
  const roses = [[-35,18],[-35,-18],[-35,34],[-35,-34],[35,18],[35,-18],[35,34],[35,-34],[-14,38],[-14,-38]];
  for (const [x,z] of roses) {
    const side = x < 0 ? 1 : -1;
    M.save().world(1).color([0.52,0.31,0.22]);
    M.boxB('brick', x, x+side*0.04, 0.15, 4.8, z-1.25,z+1.25);
    M.restore();
    // Climbing rose stems, green leaves and red blossoms.
    for (let i=0;i<9;i++) {
      const y=0.5+i*0.43, zz=z+Math.sin(i*1.9)*0.85;
      M.save().world(1).color([0.17,0.34,0.13]);
      M.boxB('wood',Math.min(x,x+side*0.09),Math.max(x,x+side*0.09),y,y+0.13,zz-0.12,zz+0.12);
      M.restore();
      if (i%2===0) {
        M.save().world(1).color([0.70,0.055,0.065]);
        M.boxB('paintwood',Math.min(x,x+side*0.14),Math.max(x,x+side*0.14),y+0.13,y+0.33,zz-0.13,zz+0.13);
        M.restore();
      }
    }
  }
  // Terracotta accents along existing boundary walls, non-colliding.
  for (const z of [-43,-27,27,43]) {
    for (const x of [-35.5,35.5]) {
      M.save().world(1).color([0.64,0.29,0.18]);
      M.boxB('brick',x-0.13,x+0.13,0.1,0.55,z-0.3,z+0.3);
      M.restore();
    }
  }
}
"""
sable_path.write_text(sable)
print("CS ITALY STYLE registered independently (visual atmosphere stage 1)")
