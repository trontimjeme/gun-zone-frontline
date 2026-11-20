"""Register a separate CS ITALY STYLE map inspired by the supplied brick-and-rose courtyard photograph.
This first stage changes environment identity, not level geometry. Never modifies the existing maps.
"""
from pathlib import Path

map_path = Path("src/02-map.js")
source = map_path.read_text()
needle = "const MAPS = ["
assert source.count(needle) == 1, "Map registry changed upstream"
assert "id: 'csitalystyle'" not in source
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
  art: { ...MAP_DEFS.sable.art }
};
"""
sable_path.write_text(sable)
print("CS ITALY STYLE registered independently (visual atmosphere stage 1)")
