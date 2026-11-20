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
   border:2px solid #e8bd59!important;
   background:radial-gradient(circle at 45% 40%,rgba(74,61,34,.65),rgba(10,12,12,.85))!important;
   box-shadow:0 0 0 2px #080908b0,0 0 10px #e6b34d99,inset 0 0 9px #e6b34d33!important;
 }
 #touch:not(.hidden):not(.fpv) .tc-fire { --s:20; }\n #touch:not(.hidden):not(.fpv) .tc-fire svg,\n #touch:not(.hidden):not(.fpv) .tc-fire-l svg {width:57%!important;height:57%!important;stroke:#fff5d2!important;stroke-width:1.9!important;filter:drop-shadow(0 0 4px #e9b64d)!important;}
 #touch:not(.hidden):not(.fpv) .tc-fire-l {
   --s:15;left:19.5vw!important;right:auto!important;top:52vh!important;bottom:auto!important;
 }
 #touch:not(.hidden):not(.fpv) .tc-az-drone {
   display:grid!important;position:absolute!important;right:2.8vw!important;
   top:21vh!important;bottom:auto!important;left:auto!important;
   width:clamp(48px,9vh,68px)!important;height:clamp(48px,9vh,68px)!important;
   border:2px solid #e7b94e!important;border-radius:50%!important;
   background:radial-gradient(circle,#27302bbf,#090c0de8)!important;color:#f8e9bd!important;
   box-shadow:0 0 0 2px #0009,0 0 10px #e4ae4d99!important;z-index:26!important;
   pointer-events:auto!important;
 }
 #touch:not(.hidden):not(.fpv) .tc-az-drone svg {width:63%!important;height:63%!important;stroke:#f4ebd3!important;transform:translateY(-4px)!important;}\n #touch:not(.hidden):not(.fpv) .tc-az-drone:after {
   content:'DRONE';position:absolute;bottom:2px;font:700 9px system-ui;
   color:#fff;letter-spacing:.02em;
 }
}
</style>"""
    if "</head>" in html and "AZONE mobile: two native fire buttons" not in html:
        html=html.replace("</head>",css+"</head>")
        q.write_text(html)
print("Original HUD retained; dual native fire + AZONE drone controls installed")
