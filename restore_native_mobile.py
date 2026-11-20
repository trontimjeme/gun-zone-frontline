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
html=q.read_text()
assert "</head>" in html and "</body>" in html
css="""<style>
/* AZONE: use the ORIGINAL touch HUD; expose a manual fire button and one drone button */
@media (pointer:coarse) {
 #touch .tc-fire {display:flex!important;visibility:visible!important;opacity:1!important;pointer-events:auto!important;}
 #touch .tc-az-drone {position:absolute!important;right:2.5vw!important;top:18vh!important;width:54px!important;height:54px!important;display:flex!important;align-items:center;justify-content:center;border-radius:50%;background:#1d313bbf;border:1px solid #f1c77b!important;z-index:10;pointer-events:auto!important;}
}
</style>"""
html=html.replace("</head>",css+"</head>")
q.write_text(html)
# After build.py, original engine is bundled into HTML. CSS overrides
# make fire visible even if auto fire settings hide it.
# Native TC button handling is retained.
print("Native iOS touch HUD patched")
