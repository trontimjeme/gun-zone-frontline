"""Add a visually distinct ITALY REAL map without changing existing maps."""
from pathlib import Path

map_path = Path("src/02-map.js")
source = map_path.read_text()
needle = "const MAPS = ["
assert source.count(needle) == 1, "Map registry changed upstream"
source = source.replace(needle, """const MAPS = [
  { id: 'italyreal', name: 'ITALY REAL', tag: 'Italy · Realistic Tactical', ok: true,
    desc: 'Phố cổ Italy: nắng ấm, đá tự nhiên, tương phản điện ảnh. Bản đồ đồ họa nâng cấp riêng.' },""", 1)
map_path.write_text(source)

sable_path = Path("src/02s-sable.js")
sable = sable_path.read_text()
assert "MAP_DEFS.sable = {" in sable and "MAP_DEFS.italyreal" not in sable
sable += """
/* AZONE Graphics V2: independent selectable map, preserving original map geometry,
   collision, bot routes and all other map visual settings. */
const ITALY_REAL_ATMO = {
  ...ATMO_SABLE,
  sun: [-0.62, 0.33, 0.5],
  sunColor: 0xffe1ad,
  sunI: 1.65,
  vmSun: 0xffe0b2,
  fog: [0.72, 0.69, 0.65],
  fogD: 0.0038,
  fogSun: 0.24,
  hemi: [0xa8c2d8, 0x72614e, 0.7],
  vmHemi: [0xb4cadc, 0x72614e],
  sky: {
    ...ATMO_SABLE.sky,
    zen: [0.22, 0.39, 0.66],
    mid: [0.48, 0.66, 0.84],
    hor: [0.89, 0.82, 0.69],
    gnd: [0.42, 0.37, 0.3],
    glow: [1.0, 0.82, 0.56],
    halo: [1.0, 0.9, 0.72],
    disk: [7, 6, 4]
  },
  lit: false,
  lamps: 0.15,
  winLit: 0.08,
  bounce: [0.42, 0.38, 0.31],
  grade: { lo: [0.94, 0.97, 1.03], hi: [1.06, 1.03, 0.97], exp: 1.02, sat: 1.04, con: 1.08 },
  rays: [1.0, 0.88, 0.68],
  bloom: [0.16, 0.45, 1.0]
};
MAP_DEFS.italyreal = {
  ...MAP_DEFS.sable,
  atmo: ITALY_REAL_ATMO,
  // Reuse tested combat geometry while giving this mode its own identity.
  art: MAP_DEFS.sable.art
};
"""
sable_path.write_text(sable)
print("ITALY REAL registered; original maps unchanged")
