"""Mobile iOS HUD bridge, adapted from the control layout in trontimjeme/texas.
The Gun Zone engine differs from Texas: dispatch existing keyboard/mouse inputs,
rather than copying incompatible TypeScript game systems.
"""
from pathlib import Path
p=Path("dist/index.html")
html=p.read_text()
assert "</body>" in html.lower()
if 'id="azone-ios-controls"' in html: raise SystemExit("Already injected")
payload=r'''
<style>
#azone-ios-controls{display:none;position:fixed;inset:0;z-index:9997;pointer-events:none;font-family:system-ui,sans-serif;color:#fff}
@media(pointer:coarse){#azone-ios-controls{display:block}}
#azone-ios-controls button{pointer-events:auto;touch-action:none;user-select:none;-webkit-user-select:none;-webkit-tap-highlight-color:transparent;border:1px solid #ffffff80;background:#17252cb8;color:white;backdrop-filter:blur(8px);border-radius:50%;width:clamp(48px,9vh,72px);height:clamp(48px,9vh,72px);font-size:13px;font-weight:800;box-shadow:0 3px 10px #0008}
#azone-ios-controls button:active,#azone-ios-controls button.pressed{background:#b88642df}
#azone-ios-controls .azone-right{position:absolute;right:calc(env(safe-area-inset-right) + 12px);bottom:calc(env(safe-area-inset-bottom) + 18px);display:grid;grid-template-columns:repeat(3,auto);gap:8px;align-items:center}
#azone-ios-controls .azone-top{position:absolute;right:calc(env(safe-area-inset-right) + 14px);top:calc(env(safe-area-inset-top) + 65px);display:flex;gap:8px}
#azone-ios-controls .azone-fire{width:clamp(68px,13vh,95px)!important;height:clamp(68px,13vh,95px)!important;border:2px solid #efbb68!important;background:#8e3b26c9!important;font-size:16px!important}
#azone-ios-controls .azone-joystick{position:absolute;left:calc(env(safe-area-inset-left) + 24px);bottom:calc(env(safe-area-inset-bottom) + 35px);width:110px;height:110px;border-radius:50%;background:#13252c55;border:2px solid #fff5;pointer-events:auto;touch-action:none}
#azone-ios-controls .azone-knob{position:absolute;left:34px;top:34px;width:42px;height:42px;border-radius:50%;background:#e6c28cb0;pointer-events:none}
@media(orientation:portrait){#azone-ios-controls .azone-right{transform:scale(.8);transform-origin:right bottom}#azone-ios-controls .azone-top{top:100px}}
</style>
<div id="azone-ios-controls" aria-label="Điều khiển bắn súng iOS">
  <div class="azone-top"><button data-key="KeyX" aria-label="Drone toàn cảnh">DRONE</button><button data-key="KeyG" aria-label="Chế độ mìn">MÌN</button></div>
  <div class="azone-joystick" id="azone-joystick"><div class="azone-knob" id="azone-knob"></div></div>
  <div class="azone-right">
    <button data-key="KeyR" aria-label="Nạp đạn">NẠP</button><button data-aim aria-label="Ngắm">NGẮM</button><button data-key="Space" aria-label="Nhảy">NHẢY</button>
    <button data-key="KeyC" aria-label="Ngồi">NGỒI</button><button class="azone-fire" data-fire aria-label="Bắn">BẮN</button><button data-key="KeyQ" aria-label="Đổi súng">SÚNG</button>
  </div>
</div>
<script>
(()=>{const root=document.getElementById('azone-ios-controls');if(!root)return;
const active=new Map();
function key(code,down){const key=({Space:' ',KeyG:'g',KeyX:'x',KeyR:'r',KeyC:'c',KeyQ:'q',KeyW:'w',KeyA:'a',KeyS:'s',KeyD:'d'})[code]||code;
window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{key,code,bubbles:true,cancelable:true}));}
function mouse(button,down){const canvas=document.querySelector('canvas');if(!canvas)return;const event=new MouseEvent(down?'mousedown':'mouseup',{bubbles:true,cancelable:true,button,buttons:down?(button===2?2:1):0,clientX:innerWidth/2,clientY:innerHeight/2});canvas.dispatchEvent(event);window.dispatchEvent(event);}
for(const b of root.querySelectorAll('button')){let pointer=null;const down=e=>{e.preventDefault();e.stopPropagation();if(pointer!==null)return;pointer=e.pointerId;b.setPointerCapture(pointer);b.classList.add('pressed');if(b.hasAttribute('data-fire'))mouse(0,true);else if(b.hasAttribute('data-aim'))mouse(2,true);else{const k=b.dataset.key;key(k,true);if(['KeyG','KeyX','KeyQ','KeyR'].includes(k))setTimeout(()=>key(k,false),90);}};
const up=e=>{e.preventDefault();e.stopPropagation();if(pointer===null)return;pointer=null;b.classList.remove('pressed');if(b.hasAttribute('data-fire'))mouse(0,false);else if(b.hasAttribute('data-aim'))mouse(2,false);else key(b.dataset.key,false);};b.addEventListener('pointerdown',down);for(const type of ['pointerup','pointercancel','lostpointercapture'])b.addEventListener(type,up);}
const stick=document.getElementById('azone-joystick'),knob=document.getElementById('azone-knob');let pid=null;let held=new Set();function update(e){const r=stick.getBoundingClientRect(),x=(e.clientX-r.left-r.width/2)/(r.width/2),y=(e.clientY-r.top-r.height/2)/(r.height/2);const m=Math.max(1,Math.hypot(x,y));knob.style.transform='translate('+(x/m*33)+'px,'+(y/m*33)+'px)';const next=new Set();if(y<-.25)next.add('KeyW');if(y>.25)next.add('KeyS');if(x<-.25)next.add('KeyA');if(x>.25)next.add('KeyD');for(const k of held)if(!next.has(k))key(k,false);for(const k of next)if(!held.has(k))key(k,true);held=next;}
stick.addEventListener('pointerdown',e=>{e.preventDefault();pid=e.pointerId;stick.setPointerCapture(pid);update(e)});stick.addEventListener('pointermove',e=>{if(pid===e.pointerId)update(e)});function stop(){pid=null;knob.style.transform='';for(const k of held)key(k,false);held.clear()}stick.addEventListener('pointerup',stop);stick.addEventListener('pointercancel',stop);window.addEventListener('blur',stop);
})();
</script>
'''
html=html.replace("</body>",payload+"</body>")
p.write_text(html)
print("iOS controls injected into built game")
