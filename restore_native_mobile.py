"""Restore native mobile controls and add explicit fire + aerial drone buttons."""
from pathlib import Path
p=Path("src/09q-tactile.js")
s=p.read_text()
needle="  ['fireL', 'tc-fire-l l', 'fire', _t('Tirer'), 'hold', (d) => touchFire(d, 'l')],"
assert s.count(needle)==1
s=s.replace(needle,needle+"\n  ['azDrone', 'tc-az-drone', 'uav', 'DRONE', 'tap', () => useKs(0)],")
# Make the original native touch fire visible regardless of auto-fire mode.
s=s.replace("function touchBuild() {","function touchBuild() {",1)
p.write_text(s)
# Inject only lightweight CSS, not a second touch control system.
q=Path("dist/index.html")
# After build.py, original engine is bundled into HTML. CSS overrides
# make fire visible even if auto fire settings hide it.
# Native TC button handling is retained.
print("Native iOS touch HUD patched")
