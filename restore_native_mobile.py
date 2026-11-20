"""Keep the original mobile HUD and expose two thumb fire controls plus AZONE FPV drone."""
from pathlib import Path
p=Path("src/09q-tactile.js")
s=p.read_text()
needle="  ['fireL', 'tc-fire-l l', 'fire', _t('Tirer'), 'hold', (d) => touchFire(d, 'l')],"
assert s.count(needle)==1
if 'tc-az-drone' not in s:
    s=s.replace(needle,needle+"\n  ['azDrone', 'tc-az-drone', 'uav', 'DRONE', 'tap', () => azDroneLaunch()],")
# Do not replace the existing touch system: both fire buttons call native touchFire.
s=s.replace("fireL: [0.1016, 0.5981, 13, 1]", "fireL: [0.205, 0.485, 15, 0]")
s=s.replace("fire: [0.8033, 0.671, 20, 0]", "fire: [0.8033, 0.671, 20, 0]")
p.write_text(s)
q=Path("dist/index.html")
if q.exists():
    html=q.read_text()
    css="""<style>
/* AZONE mobile: two native fire buttons and one FPV drone control. */
@media (pointer:coarse) {
 #touch:not(.hidden):not(.fpv) .tc-fire,
 #touch:not(.hidden):not(.fpv) .tc-fire-l {
   display:grid!important;visibility:visible!important;opacity:1!important;
   pointer-events:auto!important;z-index:25!important;
   border:2px solid #f5c66a!important;
   background:rgba(101,52,28,.52)!important;
   box-shadow:0 0 0 3px #0004,0 0 15px #edb34e66!important;
 }
 #touch:not(.hidden):not(.fpv) .tc-fire { --s:20; }
 #touch:not(.hidden):not(.fpv) .tc-fire-l {
   --s:15;left:20.5vw!important;right:auto!important;top:48.5vh!important;bottom:auto!important;
 }
 #touch:not(.hidden):not(.fpv) .tc-az-drone {
   display:grid!important;position:absolute!important;right:2.8vw!important;
   top:30vh!important;bottom:auto!important;left:auto!important;
   width:clamp(48px,9vh,68px)!important;height:clamp(48px,9vh,68px)!important;
   border:2px solid #e7b94e!important;border-radius:50%!important;
   background:#17242bc9!important;color:#f8e9bd!important;
   box-shadow:0 0 12px #e4ae4d77!important;z-index:26!important;
   pointer-events:auto!important;
 }
 #touch:not(.hidden):not(.fpv) .tc-az-drone:after {
   content:'DRONE';position:absolute;bottom:2px;font:700 9px system-ui;
   color:#fff;letter-spacing:.02em;
 }
}
</style>"""
    if "</head>" in html and "AZONE mobile: two native fire buttons" not in html:
        html=html.replace("</head>",css+"</head>")
        q.write_text(html)
print("Original HUD retained; dual native fire + AZONE drone controls installed")
