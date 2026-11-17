"""Apply the Gun ZONE Vietnamese edition to the pinned game source."""
import json
import re
import shutil
import sys
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
vi = json.loads((ROOT / "vi.json").read_text())
sys.path.insert(0, str(Path("tools").resolve()))
import i18n

entries, errors = i18n.load_en()
assert not errors
Path("i18n/en.txt").write_text("".join(f"{i18n.esc(k)} ⇒ {i18n.esc(vi[k])}\n" for k in entries))
news = Path("changelog.json")
changes = json.loads(news.read_text())
for entry in changes:
    for item, key in [(entry, "title"), *((c, "x") for c in entry["changes"])]:
        if item.get(key):
            item[key] = vi[item[key]]
news.write_text(json.dumps(changes, ensure_ascii=False))

def replace(path, old, new):
    path = Path(path)
    s = path.read_text()
    if old not in s:
        raise ValueError(old)
    path.write_text(s.replace(old, new))

lang = Path("src/00-i18n.js")
s = lang.read_text()
s = s[:s.index("const LANG_PREF")] + "const LANG_PREF = 'vi', LANG = 'vi', LOCALE = 'vi-VN';\n" + s[s.index("const PCT"):]
lang.write_text(s.replace("LANG === 'en'", "LANG === 'vi'").replace("LANG !== 'en'", "LANG !== 'vi'"))
menu = Path("src/09e-menus.js")
menu.write_text("".join(line for line in menu.read_text().splitlines(True) if "['select', 'lang'," not in line))
replace("src/09n-armurerie.js", "LANG === 'fr' ? 'fr-FR' : 'en-US'", "LOCALE")
game = Path("src/09-game.js")
game.write_text(re.sub(r"^const ordinal = .*?;$", "const ordinal = (n) => 'hạng ' + n;", game.read_text(), flags=re.M))
maps = {"Khamsin":"ANH HÙNG THỜI LOẠN","Val-Blanc":"Ga Núi Tuyết","Kervénec":"Cảng Hoàng Hôn","Hortus":"Vườn Bách Thảo","Meltem":"Đảo Gió","Tephra":"Trạm Núi Lửa","Stratus":"Quần Đảo Trên Mây","Simoun":"AZONE Công Thành Chiến","French Dream":"Khu Ngoại Ô"}
for old, new in maps.items():
    replace("src/02-map.js", f"name: '{old}'", f"name: '{new}'")
replace("src/07-bots.js", "'AZONE TUẤN ANH', ", "")
replace("src/07-bots.js", "['Volkov', 'Rahim', 'Karimov', 'Drago', 'Sokol', 'Petrenko']", "enemyRoster.slice(0, 6)")
replace("src/07-bots.js", "const BOT_NAMES = [", """const enemyRoster = ['Hải Nam', 'Hoàng Long', 'Minh Khôi', 'Quốc Huy', 'Thanh Sơn', 'Bảo Ngọc', 'Hồng Phúc', 'Gia Hân', 'Hà Linh', 'Tuấn Kiệt', 'Đức Anh', 'Ngọc Mai', 'Vân Anh', 'Quang Vinh', 'Khánh An', 'Trọng Nghĩa'];
for (let i = enemyRoster.length - 1; i > 0; i--) {
  const j = Math.floor(Math.random() * (i + 1));
  [enemyRoster[i], enemyRoster[j]] = [enemyRoster[j], enemyRoster[i]];
}
const BOT_NAMES = [""")
replace("src/07-bots.js", "['AZONE', 'Bravo']", "['AZONE', 'Đối thủ']")
replace("shell.html", '<html lang="fr">', '<html lang="vi">')
replace("shell.html", 'content="Riposte"', 'content="Gun ZONE"')
replace("shell.html", 'Gun ZONE, FPS gratuit dans le navigateur', 'Gun ZONE · Anh hùng thời loạn')
replace("shell.html", 'fr_FR', 'vi_VN')
replace("shell.html", 'FPS gratuit dans le navigateur, sur téléphone comme sur ordinateur : en solo contre des bots ou en ligne entre amis, sans rien télécharger.', 'Chơi Gun ZONE trên điện thoại hoặc máy tính. Chiến đấu cùng đội AZONE hoặc vào trận cùng bạn bè.')
replace("build.py", 'FPS en ligne dans le navigateur : solo contre des bots ou en ligne entre amis.', 'Chơi đơn cùng đồng đội máy hoặc chơi trực tuyến cùng bạn bè.')
im = Image.open(ROOT / "menu-1776.webp").convert("RGB")
size = Image.open("assets/menu-bg.webp").size
ImageOps.fit(im, size).save("assets/menu-bg.webp", quality=88)
Image.new("L", Image.open("assets/menu-depth.webp").size, 128).save("assets/menu-depth.webp")
replace("shell.html", '"inLanguage": ["fr", "en"]', '"inLanguage": "vi"')

replace("shell.html", '<footer class="mfoot">', '<footer class="mfoot" style="display:none">')

import base64
import io
import zipfile

Path("assets/logo.webp").write_bytes(base64.b64decode((ROOT / "menu-logo.webp.b64").read_bytes()))
with zipfile.ZipFile(io.BytesIO(base64.b64decode((ROOT / "radio-vi.zip.b64").read_bytes()))) as radio:
    radio.extractall("assets/sfx/voix_vi")
replace("src/05a-sfx.js", "'voix_' + (LANG === 'fr' ? 'fr' : 'en')", "'voix_vi'")
replace("shell.html", 'data-go="news"', 'data-go="news" style="display:none"')
with zipfile.ZipFile(io.BytesIO(base64.b64decode((ROOT / "texas-voices.zip.b64").read_bytes()))) as clips:
    clips.extractall("dist/texas-voices")

replace("src/09y-decompte.js", "function cdGo(late) {", """const texasVoice = new Audio();
texasVoice.preload = 'auto';
texasVoice.src = 'texas-voices/go.mp3';
let nextTexasBark = 0, lastTexasBark = 0;
function playTexasVoice(file) {
  if (Settings.voice === false || !Settings.volume) return;
  texasVoice.volume = Math.min(1, Settings.volume);
  texasVoice.src = 'texas-voices/' + file + '.mp3';
  texasVoice.play().catch(() => {});
}
function texasCombatBark() {
  if (!CD.done || MATCH.state !== 'playing' || MATCH.time < nextTexasBark || !texasVoice.paused) return;
  const pick = (lastTexasBark + 1 + Math.floor(Math.random() * (lastTexasBark ? 10 : 11)) - 1) % 11 + 1;
  lastTexasBark = pick;
  nextTexasBark = MATCH.time + 8 + Math.random() * 6;
  playTexasVoice('bark-' + String(pick).padStart(2, '0'));
}
function cdGo(late) {""")
replace("src/09y-decompte.js", "sfxAnnounce(null, 'st_start');", "nextTexasBark = MATCH.time + 3; playTexasVoice('go');")
replace("src/09y-decompte.js", "go.textContent = _t('En avant !')", "go.textContent = 'GO GO GO'")
replace("src/09y-decompte.js", "function cdClear() {", "function cdClear() {\n  texasVoice.pause();")
replace("src/09-game.js", "if (victim.protT > 0) return;", "if (victim.protT > 0) return;\n  if (attacker && attacker !== victim && (attacker === PL.ent || victim === PL.ent)) texasCombatBark();")

import hashlib, struct, math, subprocess
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

def italy_part(i):
    return subprocess.check_output(["curl","-fsSL","--retry","3",f"https://texas-eta.vercel.app/Map/CsItaly/part-{i:02}.bin"])
with ThreadPoolExecutor(max_workers=4) as workers:
    raw=b"".join(workers.map(italy_part,range(11)))
assert hashlib.sha256(raw).hexdigest()=="e71e5774d4a54af7d6be6ecf2045162607abd7beef2e54da91e4e92c9602a2a2"
size=struct.unpack_from("<I",raw,12)[0]
doc=json.loads(raw[20:20+size])
data=raw[28+size:]
out=Path("dist/italy")
out.mkdir(parents=True,exist_ok=True)
def view(i):
    v=doc["bufferViews"][i]
    a=v.get("byteOffset",0)
    return data[a:a+v["byteLength"]]
def read(i,fmt):
    return list(struct.iter_unpack(fmt,view(doc["accessors"][i]["bufferView"])))
def clip(poly,axis,edge,sign):
    q=[]
    for a,b in zip(poly[-1:]+poly[:-1],poly):
        da,db=sign*(a[axis]-edge),sign*(b[axis]-edge)
        if (da<0)!=(db<0):
            t=da/(da-db)
            q.append(tuple(x+t*(y-x) for x,y in zip(a,b)))
        if db>=0:q.append(b)
    return q
boxes=set()
def box(poly):
    b=[]
    for axis in range(3):
        vals=[p[axis] for p in poly]
        lo,hi=min(vals),max(vals)
        b.extend((round(min(lo,hi-.06),3),round(hi,3)))
    boxes.add(tuple(b))
def triangle(poly):
    spans=[max(v[i] for v in poly)-min(v[i] for v in poly) for i in range(3)]
    pieces=[poly]
    for axis in sorted(range(3),key=lambda i:spans[i],reverse=True)[:2]:
        result=[]
        for p in pieces:
            for k in range(math.floor(min(v[axis] for v in p)),math.ceil(max(v[axis] for v in p))):
                q=clip(clip(p,axis,k,1),axis,k+1,-1)
                if len(q)>=3:result.append(q)
        pieces=result
    for p in pieces:box(p)
meshes=[]
for n in doc["nodes"][1:]:
    if int(n["name"].split("_")[1]) in (0,1,3,8):continue
    for p in doc["meshes"][n["mesh"]]["primitives"]:
        pos=[(x,z+8,-y) for x,y,z in read(p["attributes"]["POSITION"],"<fff")]
        uv=read(p["attributes"]["TEXCOORD_0"],"<ff")
        idx=[i for i, in read(p["indices"],"<I")]
        im=doc["textures"][doc["materials"][p["material"]]["pbrMetallicRoughness"]["baseColorTexture"]["index"]]["source"]
        (out/f"{im}.png").write_bytes(view(doc["images"][im]["bufferView"]))
        meshes.append([im,pos,uv,idx])
        j=0
        while j<len(idx):
            tri=[pos[k] for k in idx[j:j+3]]
            other=[pos[k] for k in idx[j+3:j+6]]
            quad=set(tri+other)
            if len(quad)==4 and sorted(len({v[a] for v in quad}) for a in range(3))==[1,2,2] and len(set(tri)&set(other))==2:
                box(quad);j+=6
            else:
                triangle(tri);j+=3
for axis in (0,4,2,0):
    groups=defaultdict(list)
    for b in boxes:groups[b[:axis]+b[axis+2:]].append(b[axis:axis+2])
    boxes=set()
    for key,ranges in groups.items():
        merged=[]
        for lo,hi in sorted(ranges):
            if merged and lo<=merged[-1][1]+.001:merged[-1][1]=max(merged[-1][1],hi)
            else:merged.append([lo,hi])
        for pair in merged:boxes.add(key[:axis]+tuple(pair)+key[axis:])
(out/"map.json").write_text(json.dumps([meshes,sorted(boxes)],separators=(",",":")))

Path('src/02yz-italy.js').write_text("MAPS.unshift({id:'italy', name:'CS_Italy 1.6',tag:'Làng Ý',desc:'Những ngõ hẹp và quảng trường của CS_Italy.',ok:true});\nconst italyBases=[\n[[-19,47],[-15,49],[-15,46],[-18,50],[-21,43],[-17,43],[-13,43],[-27,47],[-13,50],[-27,50]],\n[[7,-55],[11,-53],[6,-52],[10,-50],[3,-50],[10,-62],[24,-52],[16,-51],[4,-59],[3,-56]]];\nconst italyHeights=new Map();\nfunction italyPlaceTeams(){\n  italyHeights.clear();\n  for(let team=0;team<2;team++){\n    const slots=[];\n    for(const [x,z] of italyBases[team]){\n      let best=-1,score=Infinity;\n      const height=team?9.32:3;\n      for(let i=0;i<NAV.count;i++){\n        if(NAV.comp[i]!==NAV.mainComp)continue;\n        const nx=NAV.nx[i], nz=NAV.nz[i];\n        const d=(nx-x)**2+(nz-z)**2+4*(NAV.ny[i]-height)**2;\n        if(d>=score || slots.some(([sx,sz])=>(sx-nx)**2+(sz-nz)**2<2.25))continue;\n        best=i;score=d;\n      }\n      if(best<0)throw new Error('Thiếu điểm xuất phát trên đường đi của bot');\n      const sx=NAV.nx[best],sz=NAV.nz[best];\n      slots.push([sx,sz]);italyHeights.set(sx+','+sz,NAV.ny[best]);\n    }\n    SPAWNS[team]=slots;\n  }\n}\nMAP_DEFS.italy={\n type:'mid',bounds:{x0:-44,x1:31,z0:-67,z1:67},splat:{x0:-48,z0:-72,w:88,d:144,ppm:4},\n textures:MAP_DEFS.sable.textures,atmo:ATMO_SABLE,void:{kill:-4},spawns:italyBases[0],\n poi:[[-18,3,46,'M'],[8,9.32,-54,'M']],zones:[['Phố cổ',-44,31,-67,67]],lane:x=>x < -15?'L':x>5?'E':'M',\n sniper:[-18,3,46],coverZ:60,heli:[44,65],cam:64,surface:()=> 'concrete',\n async build(){\n   const response=await fetch('italy/map.json');\n   if(!response.ok)throw new Error('Không tải được CS_Italy');\n   const [meshes,boxes]=await response.json();\n   const loader=new THREE.TextureLoader(), mats=new Map();\n   await Promise.all([...new Set(meshes.map(row=>row[0]))].map(async id=>{\n     const tex=await loader.loadAsync('italy/'+id+'.png');\n     tex.flipY=false;tex.wrapS=tex.wrapT=THREE.RepeatWrapping;tex.encoding=THREE.sRGBEncoding;\n     const mat=new THREE.MeshStandardMaterial({map:tex,roughness:1,metalness:0,side:THREE.DoubleSide,alphaTest:italyCutoutIds.has(id)?0.48:0});\n     mat.addEventListener('dispose',()=>tex.dispose());mats.set(id,mat);\n   }));\n   for(const [id,pos,uv,indices] of meshes){\n     const geom=new THREE.BufferGeometry();\n     geom.setAttribute('position',new THREE.Float32BufferAttribute(pos.flat(),3));\n     geom.setAttribute('uv',new THREE.Float32BufferAttribute(uv.flat(),2));\n     geom.setIndex(indices);geom.computeVertexNormals();\n     const mesh=new THREE.Mesh(geom,mats.get(id));mesh.receiveShadow=true;mapAdd(mesh);\n   }\n   for(const [x0,x1,y0,y1,z0,z1] of boxes)COL.push({x0,x1,y0,y1,z0,z1,m:'stone',ray:false});\n }\n};\n")
replace("src/09a-loading.js", "def.build(); tissusBuild();", "await def.build(); tissusBuild();")
replace("src/09a-loading.js", "buildNav(); buildCovers();", "buildNav(); if (id === 'italy') italyPlaceTeams(); buildCovers();")
replace("src/02-relief.js", "const gy0 = (x, z) => (RELIEF.on ? reliefAt(x, z) : 0);", "const gy0 = (x, z) => CURMAP.id === 'italy' ? (italyHeights.get(x + ',' + z) || 0) : (RELIEF.on ? reliefAt(x, z) : 0);")

# Apply cutouts only to textures with transparent pixels (foliage and grilles).
italy_cutouts = []
for image_file in sorted(out.glob("*.png")):
    with Image.open(image_file) as tile:
        if tile.convert("RGBA").getchannel("A").getextrema()[0] < 122:
            italy_cutouts.append(int(image_file.stem))
italy_source = Path("src/02yz-italy.js")
italy_source.write_text("const italyCutoutIds = new Set(" + json.dumps(italy_cutouts) + ");\n" + italy_source.read_text())
Path("assets/maps/italy.webp").write_bytes(base64.b64decode((ROOT/"italy-loading.webp.b64").read_bytes()))

Path('src/08x-italy-rpg.js').write_text("function italyTubeModel(){let e=new THREE.Group;e.name=`gun`,e.position.set(.08,-.14,-.42),e.rotation.set(.05,.12,.04);let t=new THREE.MeshPhysicalMaterial({color:`#5a6238`,roughness:.48,metalness:.35,clearcoat:.2,clearcoatRoughness:.4,envMapIntensity:.9}),n=new THREE.MeshPhysicalMaterial({color:`#1a1c18`,roughness:.28,metalness:.82,envMapIntensity:1.25}),r=new THREE.MeshPhysicalMaterial({color:`#222420`,roughness:.88,metalness:.06,envMapIntensity:.35}),i=new THREE.MeshPhysicalMaterial({color:`#1a2a1a`,roughness:.06,metalness:.2,transparent:!0,opacity:.9,envMapIntensity:1.5}),a=new THREE.Mesh(new THREE.CylinderGeometry(.085,.09,1.05,24),t);a.rotation.x=Math.PI/2,a.position.set(0,0,-.15),e.add(a);let o=new THREE.Mesh(new THREE.TorusGeometry(.091,.006,8,24),n);o.position.set(0,0,-.15),e.add(o);let s=new THREE.Mesh(new THREE.CylinderGeometry(.1,.085,.08,20),n);s.rotation.x=Math.PI/2,s.position.set(0,0,-.7),e.add(s);let c=new THREE.Mesh(new THREE.CylinderGeometry(.14,.08,.16,20),n);c.rotation.x=Math.PI/2,c.position.set(0,0,.42),e.add(c);let l=new THREE.Mesh(new THREE.BoxGeometry(.16,.14,.28),r);l.position.set(0,-.02,.05),e.add(l);let u=new THREE.Mesh(new THREE.BoxGeometry(.05,.14,.06),n);u.position.set(.02,-.12,-.05),u.rotation.x=.2,e.add(u);let d=new THREE.Mesh(new THREE.BoxGeometry(.04,.12,.045),n);d.position.set(.02,-.12,-.42),e.add(d);let f=new THREE.Mesh(new THREE.BoxGeometry(.06,.07,.16),n);f.position.set(-.06,.1,-.35),e.add(f);let p=new THREE.Mesh(new THREE.CylinderGeometry(.025,.025,.04,14),i);p.rotation.x=Math.PI/2,p.position.set(-.06,.1,-.44),e.add(p);let m=new THREE.Mesh(new THREE.CylinderGeometry(.012,.015,.18,8),n);m.position.set(0,-.16,-.1),e.add(m);let h=new THREE.Mesh(new THREE.SphereGeometry(.015,8,8),new THREE.MeshBasicMaterial({color:`#ff2222`}));return h.position.set(0,-.02,-.74),e.add(h),e}\nconst italyRpg={on:false,left:9,next:0,model:null,round:null,sound:null};\nfunction italyGunOff(){\n  italyRpg.on=false;\n  if(italyRpg.model) italyRpg.model.visible=false;\n  if(italyRpg.hidden){italyRpg.hidden.visible=true;italyRpg.hidden=null;}\n}\nfunction italyGunReset(){\n  italyGunOff(); italyRpg.left=9;italyRpg.next=0;\n  if(italyRpg.round){scene.remove(italyRpg.round.mesh);italyRpg.round=null;}\n}\nfunction italyGunPrepare(){\n  if(italyRpg.model)return;\n  const m=italyTubeModel();m.position.set(.22,-.18,-.46);m.visible=false;VM.root.add(m);italyRpg.model=m;\n  italyRpg.projectile=new THREE.Mesh(new THREE.SphereGeometry(.095,8,6),new THREE.MeshBasicMaterial({color:0xff9c38}));\n  italyRpg.sound=new Audio('italy/bazooka.mp3');italyRpg.sound.preload='auto';italyRpg.sound.load();\n}\nfunction italyGunToggle(){\n  if(CURMAP.id!=='italy'||MATCH.state!=='playing'||busy()||PILOT.d||MECHA_P.me)return;\n  if(italyRpg.on){italyGunOff();return;}\n  italyGunPrepare();italyRpg.on=true;PL.knifeOut=false;PL.reload=null;PL.adsWant=false;\n  PL.queued=false;PL.held=false;italyRpg.model.visible=true;\n  italyRpg.hidden=VM.cur.group;italyRpg.hidden.visible=false;\n}\nfunction italyShoot(){\n  PL.queued=false;\n  if(italyRpg.round||MATCH.time<italyRpg.next||!italyRpg.left)return;\n  const dir=camFwd(new V3()),mesh=italyRpg.projectile;\n  mesh.position.copy(camera.position);scene.add(mesh);\n  italyRpg.round={mesh,dir,age:0,life:PL.ent.life};\n  italyRpg.next=MATCH.time+1.1;italyRpg.left--;\n  const a=italyRpg.sound;a.currentTime=0;a.volume=Math.min(1,Settings.volume);a.play().catch(()=>{});\n}\nfunction italyRocketTick(dt){\n  const r=italyRpg.round;if(!r)return;\n  const p=r.mesh.position;\n  if(italyRpg.on&&PL.ent.alive)r.dir.lerp(camFwd(new V3()),1-Math.exp(-2*dt)).normalize();\n  const step=42*dt,w=rayWorld(p.x,p.y,p.z,r.dir.x,r.dir.y,r.dir.z,step,1);\n  const h=rayEntities(p,r.dir,w?w.t:step,PL.ent);\n  p.addScaledVector(r.dir,h?h.t:w?w.t:step);r.age+=dt;\n  if(h||w||r.age>3){\n    p.addScaledVector(r.dir,-.12);explode(p,PL.ent,'Bazoka Texas',7,100,r.life);\n    if(MATCH.online)netEvent({k:'italyBoom',x:p.x,y:p.y,z:p.z});\n    scene.remove(r.mesh);italyRpg.round=null;\n  }\n}\ndocument.getElementById('italyBaz').addEventListener('pointerdown',e=>{e.preventDefault();e.stopPropagation();italyGunToggle();});\n")
# The map list is also used by the network protocol, so order only its menu cards.
replace("src/09e-menus.js", "return MAPS.map((m) => ({", "return [...MAPS].sort((a,b) => Number(b.id === 'italy') - Number(a.id === 'italy')).map((m) => ({")
replace("src/09e-menus.js", "tag: [m.tag, mapSize(m)].filter(Boolean).join(' · ')", "tag: m.id === 'italy' ? 'Bản đặc biệt' : [m.tag, mapSize(m)].filter(Boolean).join(' · ')")
replace("src/02yz-italy.js","tag:'Làng Ý',desc:'Những ngõ hẹp và quảng trường của CS_Italy.'","tag:'Bản đặc biệt',desc:'Nhớ buổi tan học, mấy đứa góp tiền giờ net, kéo ghế ngồi chung một dãy. Vừa nghe “Go go go!” là có đứa gọi cả đội ra chợ Ý. Phố cũ vẫn đây, lần này có thêm Bazoka Texas.'")
replace("src/09e-menus.js", "${esc(m.name)}</b><span class=\"pv-m\">", "${esc(m.name)}</b>${m.id === 'italy' ? '<span class=\"pv-m\">Bản đặc biệt · Hồi ức 8x, 9x</span><span class=\"italy-story\">' + esc(m.desc) + '</span><span class=\"pv-i\">Phím 7 hoặc nút Bazoka để đổi súng</span>' : ''}<span class=\"pv-m\">")
replace("shell.html", '<div id="hud" class="hidden">','<div id="hud" class="hidden"><button type="button" id="italyBaz" hidden>Bazoka · 7</button>')
replace("shell.html","</style>",".italy-story{display:block;line-height:1.35;white-space:normal;font-size:.88em} #italyBaz{position:absolute;right:2%;top:27%;pointer-events:auto;touch-action:manipulation;background:#252315dd;color:#ffe1a1;border:1px solid #ba945b;border-radius:6px;padding:6px 10px} #italyBaz[hidden]{display:none}</style>")
replace("src/08-player.js","function giveLoadout() {","function giveLoadout() {\n  italyGunOff();")
replace("src/08-player.js","function switchWeapon(i) {","function switchWeapon(i) {\n  italyGunOff();")
replace("src/08-player.js","if (c === 'KeyR') startReload();","if (c === 'Digit7' && CURMAP.id === 'italy') italyGunToggle();\n  else if (c === 'KeyR') { if (!italyRpg.on) startReload(); }")
replace("src/08-player.js","knifeButtonTick(dt);","knifeButtonTick(dt);\n  if(italyRpg.on && (PL.knifeOut || PL.nadeState || KS.mode)) italyGunOff();")
replace("src/08-player.js","  ctlWeapon(e, dt, now);","  if(italyRpg.on){ if(I.firePressed && !hold && !e.busy) italyShoot(); I.firePressed=false; I.fire=false; PL.queued=false; }\n  ctlWeapon(e, dt, now);")
replace("src/08-player.js","if (!e.alive) { updateDeadPlayer(dt);","if (!e.alive) { italyGunOff(); updateDeadPlayer(dt);")
replace("src/09-game.js","function startMatch(opt = {}) {","function startMatch(opt = {}) {\n  italyGunReset(); if(CURMAP.id==='italy') italyGunPrepare();")
replace("src/09a-loading.js","function mapUnload() {","function mapUnload() {\n  italyGunReset();")
replace("src/09-game.js","updateNades(dt); updateThrowKnives(dt);","italyRocketTick(dt); updateNades(dt); updateThrowKnives(dt);")
replace("src/09-game.js","const ammo = `${kn", """$('italyBaz').hidden = CURMAP.id!=='italy' || !e.alive;
  const ammo = `${italyRpg.on?italyRpg.left+'-'+(now>=italyRpg.next):'normal'}|${kn""")
replace("src/09-game.js","$('wname').textContent = kn ? _t('Couteau') : d.name;", """$('wname').textContent = kn ? _t('Couteau') : d.name;
    if(italyRpg.on){const loaded=Number(now>=italyRpg.next && italyRpg.left>0); $('mag').textContent=loaded; $('reserve').textContent=italyRpg.left-loaded; $('wname').textContent='Bazoka Texas';}""")
replace("src/09c-net.js","} else if (ev.k === 'nade') {","""} else if (ev.k === 'italyBoom' && CURMAP.id==='italy') {
    if(![ev.x,ev.y,ev.z].every(Number.isFinite) || MATCH.time-(e.net.italyBoomAt??-10)<0.8)return;
    e.net.italyBoomAt=MATCH.time;
    const p=new V3(clamp(ev.x,MAP.x0-5,MAP.x1+5),clamp(ev.y,-8,80),clamp(ev.z,MAP.z0-5,MAP.z1+5));
    explosionFx(p); sfxExplosion(p);
  } else if (ev.k === 'nade') {""")

italy_audio=out/"bazooka.mp3"
subprocess.run(["curl","-fsSL","--retry","3","https://texas-eta.vercel.app/audio/sfx/bazooka.mp3","-o",str(italy_audio)],check=True)
assert hashlib.sha256(italy_audio.read_bytes()).hexdigest()=="a1bb826359c0e8e9128a8ea563055acfe530970cf7c2acf7c34d14b55d95a573"

with zipfile.ZipFile(io.BytesIO(base64.b64decode((ROOT/"golden-gate-sky.zip.b64").read_bytes()))) as sky:
    Path("assets/sky/golden_gate_hills.webp").write_bytes(sky.read("sky.webp"))
    Path("assets/vendor/hdri/golden_gate_hills.exr").write_bytes(sky.read("golden.exr"))
replace("src/02yz-italy.js","atmo:ATMO_SABLE", """skyPhoto:{key:'golden_gate_hills',rot:0,gain:1.1},atmo:{...ATMO_SABLE,hdri:'golden_gate_hills',sun:[0.594,0.681,0.429],sunColor:0xfff3db,vmSun:0xfff3db,sunI:1.1,hemi:[0xcbdfff,0xa38c72,0.65],vmHemi:[0xcbdfff,0xa38c72],fog:[0.58,0.73,0.9],fogD:0.0025,grade:{lo:[1,1,1],hi:[1,1,1],exp:1},rays:[1,0.96,0.88]}""")
Path("src/08w-italy-gifts.js").write_text("const italyGift={node:null,next:10,land:0,type:0,expires:0,speed:0,knife:0};\nconst giftLabels=['Hồi 10 máu','Chạy nhanh +20%','Sát thương dao +50%'];\nfunction removeItalyGift(){\n const root=italyGift.node;if(!root)return;\n scene.remove(root);root.traverse(o=>{if(o.geometry)o.geometry.dispose();if(o.material)o.material.dispose();});italyGift.node=null;\n}\nfunction resetItalyGift(){\n removeItalyGift();Object.assign(italyGift,{next:10,speed:0,knife:0});\n}\nfunction italyGiftTick(dt){\n if(CURMAP.id!=='italy'||MATCH.state!=='playing'||playHold())return;\n const g=italyGift,e=PL.ent,t=MATCH.time;\n if(!g.node && e.alive && t>=g.next){\n  g.next=t+2;\n  for(let k=0;k<160;k++){\n   const i=Math.floor(Math.random()*NAV.count),x=NAV.nx[i],y=NAV.ny[i],z=NAV.nz[i];\n   const dist=Math.hypot(x-e.pos.x,z-e.pos.z);\n   if(NAV.comp[i]!==NAV.mainComp||dist<3||dist>28||ceilingAbove(x,z,y+.5,.8)<y+13)continue;\n   const root=new THREE.Group();g.type=Math.floor(Math.random()*3);\n   const crate=new THREE.Mesh(new THREE.BoxGeometry(.8,.7,.8),new THREE.MeshStandardMaterial({color:[0xb7373c,0x297dbb,0x9763cd][g.type]}));\n   root.add(crate);\n   const ribbon=new THREE.Mesh(new THREE.BoxGeometry(.14,.72,.82),new THREE.MeshStandardMaterial({color:0xffdc8c}));root.add(ribbon);\n   const chute=new THREE.Mesh(new THREE.SphereGeometry(.95,12,6,0,Math.PI*2,0,Math.PI/2),new THREE.MeshStandardMaterial({color:0xf5ce79,side:THREE.DoubleSide}));chute.scale.y=.5;chute.position.y=1.25;root.add(chute);\n   for(const a of [-1,1])for(const b of [-1,1]){const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new V3(a*.65,1.25,b*.65),new V3(a*.34,.3,b*.34)]),new THREE.LineBasicMaterial({color:0x715b48}));chute.userData.lines=chute.userData.lines||[];chute.userData.lines.push(line);root.add(line);}\n   root.position.set(x,y+11,z);scene.add(root);g.node=root;g.land=y+.36;g.expires=t+38;break;\n  }\n }\n if(!g.node)return;\n const p=g.node.position;p.y=Math.max(g.land,p.y-dt*3);\n if(p.y===g.land){\n  for(const part of g.node.children.slice(2))part.visible=false;\n  if(e.alive && Math.hypot(p.x-e.pos.x,p.z-e.pos.z)<1.4 && Math.abs(p.y-e.pos.y)<1.5){\n   const wasFull=g.type===0 && e.health>=100; if(g.type===0)e.health=Math.min(100,e.health+10);\n   else if(g.type===1)g.speed=t+30;\n   else g.knife=t+30;\n   hudMsg(wasFull?'Đã nhặt hộp máu · Máu đã đầy':giftLabels[g.type]+(g.type?' · 30 giây':''),'ally',2);removeItalyGift();g.next=t+12+Math.random()*12;\n  }\n }\n if(g.node && t>=g.expires){removeItalyGift();g.next=t+3;}\n}\nconst texasWeaponHints={ar:'Súng trường · Linh hoạt ở tầm trung',smg:'Tiểu liên · Cơ động ở cự ly gần',sniper:'Súng ngắm · Chính xác ở tầm xa',shotgun:'Shotgun · Uy lực tầm gần',pistol:'Súng ngắn · Gọn nhẹ'};\n")
replace("src/08x-italy-rpg.js","function italyGunReset(){","function italyGunReset(){\n resetItalyGift();")
replace("src/09-game.js","italyRocketTick(dt);","italyGiftTick(dt); italyRocketTick(dt);")
replace("src/07c-controller.js","if (sprint) spd *= SPRINT_MUL;","if (sprint) spd *= SPRINT_MUL * (ent.isPlayer && CURMAP.id==='italy' && MATCH.time<italyGift.speed ? 1.2 : 1);")
replace("src/08-player.js","applyDamage(T, 200, e,","applyDamage(T, CURMAP.id==='italy' && MATCH.time<italyGift.knife ? 300 : 200, e,")
replace("shell.html",'<div id="wname">M4A1</div>','<div id="wname">M4A1</div><small id="weaponDetail"></small>')
replace("shell.html",'grid-template-areas: "w w" "p p" "g n"', 'grid-template-areas: "w w" "detail detail" "p p" "g n"')
replace("shell.html","#wname { grid-area:", "#weaponDetail {grid-area:detail;color:#e4dbc8;font-size:clamp(10px,1.2vw,14px);text-shadow:0 1px 3px #201b14} #wname { grid-area:")
replace("src/09-game.js","HUD.lastAmmo = ammo;", """HUD.lastAmmo = ammo;
    $('weaponDetail').textContent = italyRpg.on ? 'Hủy diệt · Vũ khí phóng tên lửa' : kn ? 'Dao · Cận chiến' : (texasWeaponHints[d.cat] || d.type);""")

# Italy uses the existing panorama for the visible sky. Soften its solar hotspot before filtering reflections.
replace("src/01-core.js","const d = loader.parse(buf.buffer);","""const d = loader.parse(buf.buffer);
    if (name === 'golden_gate_hills' && d.type === THREE.HalfFloatType) {
      const ceiling = THREE.DataUtils.toHalfFloat(4);
      for (let i=0;i<d.data.length;i++) if (d.data[i] < 0x8000 && d.data[i] > ceiling) d.data[i]=ceiling;
    }""")
replace("src/02yz-italy.js","sunI:1.1","sunI:0.82")
replace("src/02yz-italy.js","gain:1.1","gain:0.96")
replace("src/02yz-italy.js","exp:1},rays:[1,0.96,0.88]","exp:0.93},bloom:[0.08,0.3,1.4],raysThr:3,raysCap:0.18,rays:[0.40,0.38,0.35]")
replace("src/02yz-italy.js","mat.addEventListener('dispose',()=>tex.dispose());","mat.envMapIntensity=0.55; csmMaterial(mat); mat.addEventListener('dispose',()=>{if(csm)csm.shaders.delete(mat);tex.dispose();});")
replace("src/02yz-italy.js","mesh.receiveShadow=true;mapAdd(mesh);","mesh.receiveShadow=true;mesh.castShadow=true;mapAdd(mesh);")
replace("src/01-core.js","map: 'sable', volume:","map: 'italy', volume:")
replace("src/01-core.js","  if (Settings.aimAssist !== 'off')","""  if (!Settings.italyDefaultApplied || !['italy', 'simoun'].includes(Settings.map)) {
    Settings.map = 'italy'; Settings.italyDefaultApplied = true; saveSettings();
  }
  if (Settings.aimAssist !== 'off')""")
replace("src/09c-net.js","time: 10, map: 'sable'","time: 10, map: 'italy'")

# Public link metadata identifies the Gun ZONE edition.
page=Path("shell.html")
html=page.read_text()
html=re.sub(r'<meta (name="description"|property="og:description") content="[^"]*">',r'<meta \1 content="AZONE STUDIO">',html)
html=html.replace('<meta name="application-name"', '<meta name="author" content="AZONE STUDIO">\n<meta name="twitter:title" content="Gun ZONE">\n<meta name="twitter:description" content="AZONE STUDIO">\n<meta name="application-name"')
schema={"@context":"https://schema.org","@type":"WebSite","name":"Gun ZONE","url":"__SITE__/","author":{"@type":"Organization","name":"AZONE STUDIO"}}
html=re.sub(r'(<script type="application/ld\+json">).*?(</script>)',lambda m:m[1]+json.dumps(schema)+m[2],html,flags=re.S)
html=re.sub(r'<button [^>]*id="srcBtn"[^>]*>.*?</button>', '',html)
html=re.sub(r'<span class="credit">[^<]*</span>','<span class="credit">AZONE STUDIO</span>',html)
page.write_text(html)
menus=Path("src/09e-menus.js")
menus.write_text("".join(line for line in menus.read_text().splitlines(True) if "$('srcBtn').addEventListener(" not in line))
# Deliver the menu markup to the running game; keep the initial share document concise.
with Path("build.py").open("a") as handle:
    handle.write("\nfrom pathlib import Path\nfrom html.parser import HTMLParser\ngame_path=Path(\"dist/riposte-frontline.html\")\ngame_html=game_path.read_text()\nbody_match=re.search(r'<body\\b[^>]*>',game_html,re.I)\nstart=body_match.end()\nend=game_html.lower().index(\"</body>\",start)\nbody=game_html[start:end]\nchunks=re.split(r'(<script\\b[^>]*>[\\s\\S]*?</script\\s*>)',body,flags=re.I)\nfor i in range(0,len(chunks),2):\n    markup=chunks[i]\n    if not markup.strip():continue\n    payload=\"document.write(\"+json.dumps(markup,ensure_ascii=True)+\");\"\n    filename=\"ui-\"+hashlib.sha256(payload.encode()).hexdigest()[:16]+\".js\"\n    Path(\"dist\",filename).write_text(payload)\n    chunks[i]='<script src=\"'+filename+'\"></script>'\ngame_path.write_text(game_html[:start]+'<noscript>Gun ZONE · AZONE STUDIO</noscript>'+''.join(chunks)+game_html[end:])\n")

# Other map assets stay available in the project, outside the playable catalogue.
replace("src/02-map.js", "];\nconst mapById", "].filter(m => m.id === 'simoun');\nconst mapById")

replace("src/08-player.js", "function onKey(e, down) {", "function jumpHeld() { return !!(KEYS.Space || KEYS.Enter || KEYS.NumpadEnter || KEYS.MiddleJump); }\nfunction onKey(e, down) {\n  if (e.code === 'Enter' || e.code === 'NumpadEnter') {\n    if (!down) KEYS[e.code] = false;\n    if (MATCH.state === 'playing' && PL.ent.alive && pointerActive() && !CHAT.open && !KS.map.open && !e.defaultPrevented && !e.target?.closest?.('input,textarea,button,[contenteditable=true]')) {\n      e.preventDefault(); KEYS[e.code] = down; return;\n    }\n  }")
replace("src/08-player.js", "  if (e.button === 0) { if (trackpadOn())", "  if (e.button === 1 && PL.ent.alive) { e.preventDefault(); KEYS.MiddleJump = true; return; }\n  if (e.button === 0) { if (trackpadOn())")
replace("src/08-player.js", "addEventListener('mouseup', (e) => {", "addEventListener('mouseup', (e) => { if (e.button === 1) KEYS.MiddleJump = false;")
replace("src/08-player.js", "if (KEYS.Space && e.crouch", "if (jumpHeld() && e.crouch")
replace("src/08-player.js", "I.jump = !!KEYS.Space", "I.jump = jumpHeld()")
replace("src/08g-mecha-pilote.js", "P.jump = !!KEYS.Space", "P.jump = jumpHeld()")

# Each physical Shift keeps its own held state in KEYS.
replace("src/08-player.js", "function onKey(e, down) {", """function sprintHeld() {
  return !!(KEYS.ShiftLeft || (KEYS.ShiftRight && !BIND.rev.has('ShiftRight')));
}
function onKey(e, down) {""")
replace("src/08-player.js", "(KEYS.ShiftLeft || TOUCH.sprint", "(sprintHeld() || TOUCH.sprint")
replace("src/08-player.js", "TOUCH.sprint : !!KEYS.ShiftLeft", "TOUCH.sprint : sprintHeld()")
replace("src/08-player.js", "(KEYS.ShiftLeft || PAD.l3)", "(sprintHeld() || PAD.l3)")
replace("src/08a-binds.js", "'ShiftLeft', 'ControlLeft']; }", "'ShiftLeft', 'ShiftRight', 'ControlLeft']; }")

replace("src/09b-killcam.js", "function startKillcam(opts) {", "const kcVideos = { active:null, clips:new Map(), last:null, mvp:null, round:0, error:'' };\nfunction kcVideoStop() {\n  const rec = kcVideos.active;\n  kcVideos.active = null;\n  if (rec && rec.state !== 'inactive') rec.stop();\n}\nfunction kcVideoReset() {\n  kcVideoStop();\n  kcVideos.round++;\n  for (const clip of kcVideos.clips.values()) URL.revokeObjectURL(clip.url);\n  kcVideos.clips.clear(); kcVideos.last = null; kcVideos.mvp = null; kcVideos.error = '';\n  kcVideoLinks();\n}\nfunction kcVideoLinks() {\n  for (const id of ['againBtn','quitBtn']) {\n    const anchor = $(id); if (!anchor) continue;\n    let wrap = $('kcVideo'+id);\n    if (!wrap) {\n      wrap = document.createElement('span'); wrap.id = 'kcVideo'+id;\n      wrap.style.cssText = 'display:inline-flex;flex-wrap:wrap;gap:4px;align-items:center';\n      anchor.before(wrap);\n    }\n    wrap.replaceChildren();\n    const mvp = kcVideos.clips.get(kcVideos.mvp);\n    for (const clip of new Set([mvp,kcVideos.last])) {\n      if (!clip) continue;\n      const a = document.createElement('a'); a.className = 'btn'; a.href = clip.url;\n      const kind = clip === mvp ? 'MVP' : clip.final ? 'Killcam cuối trận' : 'Killcam';\n      a.textContent = 'Tải video '+kind;\n      a.download = 'Gun-ZONE-'+kind.replace(/ /g,'-')+'-'+clip.time+'.'+clip.ext;\n      wrap.append(a);\n    }\n    if (!wrap.childElementCount) wrap.textContent = kcVideos.error;\n  }\n}\nfunction kcVideoStart(killer, final) {\n  kcVideoStop();\n  if (!window.MediaRecorder || !canvas.captureStream) {\n    kcVideos.error = 'Trình duyệt chưa hỗ trợ lưu video.'; kcVideoLinks(); return;\n  }\n  const round = kcVideos.round, parts = [];\n  let stream, audio;\n  function release() {\n    if (audio) AU.videoOutput.disconnect(audio);\n    if (stream) stream.getTracks().forEach(track=>track.stop());\n  }\n  try {\n    stream = canvas.captureStream(30);\n    if (AU.videoOutput && AU.ctx.state === 'running') {\n      audio = AU.ctx.createMediaStreamDestination(); AU.videoOutput.connect(audio);\n      audio.stream.getAudioTracks().forEach(track=>stream.addTrack(track));\n    }\n    const mimeType = ['video/webm;codecs=vp8,opus','video/webm','video/mp4'].find(t=>MediaRecorder.isTypeSupported(t));\n    const rec = new MediaRecorder(stream,mimeType ? {mimeType,videoBitsPerSecond:4000000} : {});\n    rec.ondataavailable = e=>{ if (e.data.size) parts.push(e.data); };\n    rec.onstop = ()=>{\n      release(); if (round !== kcVideos.round || !parts.length) return;\n      const type = rec.mimeType || parts[0].type;\n      const clip = {url:URL.createObjectURL(new Blob(parts,{type})),ext:type.includes('mp4')?'mp4':'webm',time:Date.now(),final};\n      const old = kcVideos.clips.get(killer); if (old) URL.revokeObjectURL(old.url);\n      kcVideos.clips.set(killer,clip); kcVideos.last = clip; kcVideoLinks();\n    };\n    rec.onerror = ()=>{ kcVideos.error = 'Không ghi được video killcam.'; kcVideoLinks(); };\n    rec.start(); kcVideos.active = rec;\n  } catch { release(); kcVideos.error = 'Không ghi được video killcam.'; kcVideoLinks(); }\n}\nfunction startKillcam(opts) {")
replace("src/09b-killcam.js", "  sfxKs('killcam');", "  kcVideoStart(k, KC.final);\n  sfxKs('killcam');")
replace("src/09b-killcam.js", "function endKillcam() {", "function endKillcam() {\n  kcVideoStop();")
replace("src/09b-killcam.js", "function kcAbort() {", "function kcAbort() {\n  kcVideoStop();")
replace("src/05-audio.js", "lim.connect(ctx.destination);", "lim.connect(ctx.destination); AU.videoOutput = lim;")
replace("src/09-game.js", "kcReset(); MATCH.finalPending = null;", "kcVideoReset(); kcReset(); MATCH.finalPending = null;")
replace("src/09-game.js", "  $('end').classList.add('show');", "  kcVideos.mvp = MATCH.mode === 'ffa' ? ffaList().sort(ffaCmp)[0] : [0,1].flatMap(boardList).sort(boardCmp)[0]; kcVideoLinks();\n  $('end').classList.add('show');")

# Keep the results open until the player explicitly leaves.
def end_edit(file, pattern, replacement):
    p = Path(file)
    value, count = re.subn(pattern, lambda _: replacement, p.read_text())
    if count != 1:
        raise ValueError("Unexpected results-screen source: " + pattern)
    p.write_text(value)

end_edit("src/09-game.js", r"function updateEnd\(dt\) \{[\s\S]*?\n\}", "")
end_edit("src/09-game.js", r"  END\.t = END_SECONDS;[^\n]*", "")
end_edit("src/09-game.js", r"    updateEnd\(dt\);[^\n]*", "")
end_edit("src/09-game.js", r"  \$\('againBtn'\)\.textContent =[^\n]*", "  $('againBtn').textContent = 'EXIT';")
end_edit("src/09-game.js", r"  \$\('menuBtn'\)\.classList\.toggle\('hidden', !!MATCH.online\);", "  $('menuBtn').classList.remove('hidden'); $('menuBtn').textContent = 'Quay về màn hình chính';")
end_edit("src/09e-menus.js", r"\$\('againBtn'\)\.addEventListener\('click', \(\) => \{[\s\S]*?\n  \}\);", "$('againBtn').addEventListener('click', () => toMenu());")
replace("src/09e-menus.js", "$('menuBtn').addEventListener('click', () => toMenu());", "$('menuBtn').addEventListener('click', () => toMenu('main'));")
end_edit("shell.html", r'<div class="end-time">[\s\S]*?</i></i></div>', '')
replace("src/09c-net.js", "if (wasPlaying && MATCH.state !== 'menu' &&", "if (wasPlaying && MATCH.state !== 'ended' && MATCH.state !== 'menu' &&")
replace("src/09c-net.js", "case 'start': netStartOnline(m); break;", "case 'start': if (MATCH.state === 'ended') netSend({t:'leave'}); else netStartOnline(m); break;")

replace("src/09-game.js", "function killEnt(v, a, weapon, head, dir, life) {", "// Personal highlights use only frames rendered from the local player's view.\nconst tripleFPS = 12;\nlet triple = newTriple();\nfunction newTriple() { return {ring:[], kills:[], open:[], parts:[], links:[], last:-Infinity, total:0, n:0, busy:0, error:'', screen:null, target:null}; }\nfunction tripleUI() {\n  for (const id of ['againBtn','quitBtn']) {\n    const button=$(id); if (!button) continue;\n    let box=$('personalClips'+id);\n    if (!box) { box=document.createElement('div'); box.id='personalClips'+id; box.style.cssText='display:grid;gap:4px;max-height:18vh;overflow:auto'; button.before(box); }\n    box.replaceChildren();\n    for (const clip of triple.links) {\n      const a=document.createElement('a'); a.className='btn'; a.href=clip.url; a.download=clip.name;\n      a.textContent='Tải phim 3 mạng · '+clip.n; box.append(a);\n    }\n    if (triple.busy || triple.error) { const s=document.createElement('small'); s.textContent=triple.error || 'Đang ghép phim 3 mạng…'; box.append(s); }\n  }\n}\nfunction tripleReset() {\n  for(const c of triple.links) URL.revokeObjectURL(c.url);\n  triple=newTriple(); tripleUI();\n}\nfunction tripleKill(victim) {\n  if (!window.MediaRecorder || !canvas.captureStream) { triple.error='Trình duyệt chưa hỗ trợ lưu highlight.'; tripleUI(); return; }\n  const t=performance.now();\n  triple.open.push({t,number:++triple.total,name:String(victim.name||''),frames:triple.ring.filter(f=>t-f.t<=2400)});\n}\nfunction tripleFrame(now) {\n  const r=triple;\n  if (!window.MediaRecorder || !canvas.captureStream) return;\n  const live=MATCH.state==='playing' && !KC.active && PL.ent.alive;\n  if (live && now-r.last>=1000/tripleFPS && canvas.width && canvas.height) {\n    r.last=now;\n    const c=r.screen || (r.screen=document.createElement('canvas'));\n    const ratio=Math.min(1,768/Math.max(canvas.width,canvas.height));\n    const w=Math.max(2,2*Math.round(canvas.width*ratio/2)), h=Math.max(2,2*Math.round(canvas.height*ratio/2));\n    if (c.width!==w||c.height!==h){c.width=w;c.height=h;}\n    c.getContext('2d').drawImage(canvas,0,0,w,h);\n    const f={t:now,w,h,data:new Promise(resolve=>c.toBlob(resolve,'image/jpeg',.79))};\n    r.ring.push(f); while(r.ring.length>30)r.ring.shift();\n    for(const k of r.open)k.frames.push(f);\n  } else if (!live) r.ring.length=0;\n  while(r.open.length && (!live || now-r.open[0].t>=750)){\n    const kill=r.open.shift();r.parts.push(kill);\n    if(r.parts.length===3){\n      const group=r.parts.splice(0);const n=++r.n;\n      r.busy++;tripleUI();tripleFilm(r,group,n).catch(()=>{r.error='Không tạo được phim 3 mạng.';}).finally(()=>{r.busy--;if(r===triple)tripleUI();});\n    }\n  }\n}\nasync function tripleFilm(r,group,n) {\n  const frames=[...new Set(group.flatMap(k=>k.frames))].sort((a,b)=>a.t-b.t);\n  if(!frames.length)throw Error();\n  const c=document.createElement('canvas'); c.width=frames[0].w;c.height=frames[0].h;\n  const ctx=c.getContext('2d'),stream=c.captureStream(tripleFPS),chunks=[];\n  const type=['video/webm;codecs=vp8','video/webm','video/mp4'].find(t=>MediaRecorder.isTypeSupported(t));\n  let rec;\n  try {\n    rec=new MediaRecorder(stream,type?{mimeType:type}:undefined);\n    const done=new Promise((ok,fail)=>{rec.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};rec.onstop=ok;rec.onerror=fail;});done.catch(()=>{});\n    rec.start();\n    for(const f of frames){\n      if(r!==triple)break;\n      const blob=await f.data;if(!blob)continue;\n      const img=await createImageBitmap(blob);ctx.drawImage(img,0,0,c.width,c.height);img.close();\n      const kill=group.filter(k=>k.t<=f.t+60).pop();\n      ctx.fillStyle='rgba(0,0,0,.65)';ctx.fillRect(0,c.height-34,c.width,34);\n      ctx.fillStyle='#fff';ctx.font='bold 16px sans-serif';ctx.fillText('GUN ZONE   ·   '+(kill?'Hạ '+kill.name+'   ·   '+(group.indexOf(kill)+1)+'/3':'Highlight cá nhân'),12,c.height-11);\n      await new Promise(ok=>setTimeout(ok,1000/tripleFPS));\n    }\n    if(rec.state!=='inactive')rec.stop();await done;\n    if(r!==triple)return;\n    if(!chunks.length)throw Error();\n    const mime=rec.mimeType||chunks[0].type, ext=mime.includes('mp4')?'mp4':'webm';\n    r.links.push({n,url:URL.createObjectURL(new Blob(chunks,{type:mime})),name:'Gun-ZONE-3-kills-'+n+'-'+Date.now()+'.'+ext});r.links.sort((a,b)=>a.n-b.n);\n  } finally { if(rec && rec.state!=='inactive')rec.stop();stream.getTracks().forEach(t=>t.stop()); }\n}\nfunction killEnt(v, a, weapon, head, dir, life) {")
replace("src/09-game.js", "      PL.bestStreak = Math.max", "      if (a === PL.ent) tripleKill(v);\n      PL.bestStreak = Math.max")
replace("src/09-game.js", "renderFrame(dt); pfrLap(6);", "renderFrame(dt); tripleFrame(performance.now()); pfrLap(6);")
replace("src/09-game.js", "function startMatch(opt = {}) {", "function startMatch(opt = {}) {\n  tripleReset();")

# Imported chibi soldier, available to every profile.
import base64, gzip
chibi_json = gzip.decompress(base64.b64decode((ROOT / "assets/chibi-mesh.gz.b64").read_bytes())).decode()
replace("src/06ga-tenues.js", "const SKIN_REL =", "\nSKINS.chibi = { ...SKINS.assault, name: 'AZONE Chibi', role: 'Chiến binh tí hon', tone: [[1,1,1],[0.8,0.78,0.78]] };\nSKIN_IDS.push('chibi');\nconst chibiData = CHIBI_JSON;\nfunction chibiBytes(s) { return Uint8Array.from(atob(s), c => c.charCodeAt(0)); }\nlet chibiMap;\nfunction chibiMaterial(mode) {\n  if (!chibiMap) {\n    const pixels = chibiBytes(chibiData.atlas), palette = chibiBytes(chibiData.palette);\n    const rgba = new Uint8Array(pixels.length * 4);\n    for (let i=0;i<pixels.length;i++) {\n      const k=pixels[i]*3;\n      rgba.set([palette[k],palette[k+1],palette[k+2],255],4*i);\n    }\n    chibiMap = new THREE.DataTexture(rgba,512,512);\n    chibiMap.encoding = THREE.sRGBEncoding;\n    chibiMap.generateMipmaps = true;\n    chibiMap.minFilter = THREE.LinearMipmapLinearFilter;\n    chibiMap.magFilter = THREE.LinearFilter;\n    chibiMap.needsUpdate = true;\n  }\n  const m = new THREE.MeshStandardMaterial({map:chibiMap, roughness:0.85});\n  m.userData.skU = {tag:{value:new THREE.Color()},glow:{value:0},neon:{value:0}};\n  if (mode === 'tp') volumeLit(m);\n  return m;\n}\nfunction chibiGeometry() {\n  if (SOLDIER_GEOS.chibi) return SOLDIER_GEOS.chibi;\n  const raw = new Int16Array(chibiBytes(chibiData.p).buffer);\n  const reference = soldierGeometry('assault','hi');\n  if (!reference.boundingBox) reference.computeBoundingBox();\n  const bounds = reference.boundingBox;\n  let foot = Infinity, top = -Infinity;\n  for (let i=1;i<raw.length;i+=3) { foot=Math.min(foot,raw[i]); top=Math.max(top,raw[i]); }\n  const scale=(bounds.max.y-bounds.min.y)/(top-foot);\n  const p=Float32Array.from(raw,(n,i)=>i%3===1 ? bounds.min.y+(n-foot)*scale : -n*scale);\n  const count=p.length/3, bones=new Uint16Array(count*4), weights=new Float32Array(count*4);\n  for(let i=0;i<count;i++){\n    const h=raw[i*3+1]/30000, side=SIDE_B(p[i*3]), k=i*4;\n    const levels=[[0,side.ft],[0.09,side.sh],[0.18,side.th],[0.25,SB.PEL],[0.36,SB.CHE],[0.49,SB.HEA]];\n    let n=0; while(n+1<levels.length && h>=levels[n+1][0]) n++;\n    const a=levels[n], b=levels[Math.min(n+1,levels.length-1)];\n    const f=b===a?0:Math.max(0,(h-a[0])/(b[0]-a[0]));\n    bones[k]=a[1]; bones[k+1]=b[1]; weights[k]=1-f; weights[k+1]=f;\n  }\n  const g = new THREE.BufferGeometry();\n  g.setAttribute('position',new THREE.BufferAttribute(p,3));\n  g.setAttribute('skinIndex',new THREE.BufferAttribute(bones,4));\n  g.setAttribute('skinWeight',new THREE.BufferAttribute(weights,4));\n  g.setAttribute('uv',new THREE.BufferAttribute(new Uint16Array(chibiBytes(chibiData.uv).buffer),2,true));\n  g.setIndex(new THREE.BufferAttribute(new Uint16Array(chibiBytes(chibiData.i).buffer),1));\n  g.computeVertexNormals();\n  g.boundingSphere = new THREE.Sphere(new V3(0,0.1,0),1.6);\n  g.userData.shared=true;\n  return SOLDIER_GEOS.chibi=g;\n}\n\nconst SKIN_REL =".replace("CHIBI_JSON", chibi_json))
replace("src/06g-body.js", "function soldierGeometry(skin, lod) {", "function soldierGeometry(skin, lod) {\n  if (skin === 'chibi') return chibiGeometry();")
replace("src/06e-gear.js", "function gearMaterial(skin, mode) {", "function gearMaterial(skin, mode) {\n  if (skin === 'chibi' && mode !== 'fp') return chibiMaterial(mode);")

# AZONE bots wear Chibi at spawn and after each map load.
replace("src/07-bots.js", "b.skin = skinOfWeapon(def);", "b.skin = b.team === 0 ? (b.skin && hasKey(jinnaColors,b.skin) ? b.skin : 'jinna') : 'shotgun';")

jinna_json=gzip.decompress(base64.b64decode((ROOT / "assets/jinna-mesh.gz.b64").read_bytes())).decode()
replace("src/06ga-tenues.js", "const SKIN_REL =", "\nconst jinnaData = JINNA_DATA;\nconst jinnaColors = {jinna:null,jinnaBlue:[0.07,0.36,0.85],jinnaGreen:[0.09,0.58,0.29],jinnaGold:[0.83,0.41,0.06],jinnaPlum:[0.60,0.13,0.53],jinnaRed:[0.86,0.06,0.08],jinnaPearl:[0.86,0.88,0.82],jinnaTeal:[0.04,0.73,0.76],jinnaOrange:[0.97,0.24,0.03],jinnaRose:[0.98,0.31,0.58]};\nfor (const id of Object.keys(jinnaColors)) SKINS[id]={...SKINS.assault,name:'Jinna',role:'Đặc nhiệm AZONE',tone:[[1,1,1],[0.84,0.82,0.82]]};\nSKIN_IDS.push('jinna');\nfunction jinnaGeometry(){\n  if(SOLDIER_GEOS.jinna) return SOLDIER_GEOS.jinna;\n  const d=jinnaData,read=(k,T)=>new T(chibiBytes(d[k]).buffer);\n  const g=new THREE.BufferGeometry();\n  const pos=Float32Array.from(read('p',Int16Array),v=>v/14000);\n  g.setAttribute('position',new THREE.BufferAttribute(pos,3));\n  g.setAttribute('uv',new THREE.BufferAttribute(read('uv',Float32Array),2));\n  g.setAttribute('skinIndex',new THREE.BufferAttribute(read('b',Uint8Array),4));\n  g.setAttribute('skinWeight',new THREE.BufferAttribute(read('w',Float32Array),4));\n  g.setAttribute('jinnaCloth',new THREE.BufferAttribute(read('m',Uint8Array),1));\n  g.setIndex(new THREE.BufferAttribute(read('i',Uint16Array),1));\n  g.computeVertexNormals();g.computeBoundingBox();\n  g.boundingSphere=new THREE.Sphere(new V3(0,0.1,0),1.6);g.userData.shared=true;\n  return SOLDIER_GEOS.jinna=g;\n}\nlet jinnaAtlas;\nfunction jinnaMaterial(id,mode){\n  if(!jinnaAtlas){\n    const tex=chibiBytes(jinnaData.tex),pal=chibiBytes(jinnaData.pal),rgba=new Uint8Array(tex.length*4);\n    for(let i=0;i<tex.length;i++){const k=tex[i]*3;rgba[i*4]=pal[k];rgba[i*4+1]=pal[k+1];rgba[i*4+2]=pal[k+2];rgba[i*4+3]=255;}\n    jinnaAtlas=new THREE.DataTexture(rgba,512,512);jinnaAtlas.encoding=THREE.sRGBEncoding;\n    jinnaAtlas.generateMipmaps=true;jinnaAtlas.minFilter=THREE.LinearMipmapLinearFilter;jinnaAtlas.magFilter=THREE.LinearFilter;jinnaAtlas.needsUpdate=true;\n  }\n  const m=new THREE.MeshStandardMaterial({map:jinnaAtlas,roughness:0.83,side:THREE.DoubleSide});\n  m.userData.skU={tag:{value:new THREE.Color()},glow:{value:0},neon:{value:0}};\n  if(mode==='tp')volumeLit(m);\n  const base=m.userData.patch, color=jinnaColors[id];\n  if(color){\n    m.defines={...m.defines,JINNA_CLOTH:1};\n    m.onBeforeCompile=m.userData.patch=(s)=>{\n      if(base)base(s);\n      s.uniforms.jinnaDye={value:new THREE.Vector3(...color)};\n      s.vertexShader='attribute float jinnaCloth; varying float clothAmount;\\n'+s.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\\nclothAmount=jinnaCloth;');\n      s.fragmentShader='uniform vec3 jinnaDye; varying float clothAmount;\\n'+s.fragmentShader.replace('#include <map_fragment>','#include <map_fragment>\\nfloat clothLight=dot(diffuseColor.rgb,vec3(0.30,0.59,0.11));diffuseColor.rgb=mix(diffuseColor.rgb,jinnaDye*(0.16+clothLight*1.4),clothAmount*0.92);');\n    };\n  }\n  return m;\n}\nconst jinnaVariants=Object.keys(jinnaColors).slice(1);\nlet jinnaNext=0,jinnaMine='jinna';\nconst jinnaAssignments=new Map();\nlet jinnaPalette=[];\nfunction jinnaMatchStart(){\n  jinnaNext=0;jinnaMine='jinna';jinnaAssignments.clear();\n  jinnaPalette=jinnaVariants.slice();\n  for(let i=jinnaPalette.length-1;i>0;i--){\n    const j=Math.floor(Math.random()*(i+1));\n    [jinnaPalette[i],jinnaPalette[j]]=[jinnaPalette[j],jinnaPalette[i]];\n  }\n}\nfunction jinnaSetMine(id){\n  if(jinnaMine===id)return;\n  jinnaMine=id;\n  if(PL.ent && PL.ent.model) soldierLook(PL.ent.model,skinOf(PL.ent),skinRel(PL.ent));\n  if(KC.body) soldierLook(KC.body,skinOf(PL.ent),skinRel(PL.ent));\n  if(MATCH.online) NET.flush=true;\n}\nfunction jinnaRoster(){\n  if(!PL.ent || (MATCH.online && NET.role!=='host'))return;\n  const users=new Map();\n  for(const e of entities){\n    if(e.off || (e.isRemote && e.remoteBot))continue;\n    if(e===PL.ent && skinMine()!=='jinna')continue;\n    if(e.isRemote && !hasKey(jinnaColors,e.skin))continue;\n    if(!e.isRemote && !e.isPlayer && e.team!==0)continue;\n    if(MATCH.online && !e.isPlayer && !e.isRemote && !e.netBot)continue;\n    const key=MATCH.online ? netIdOf(e) : String(e.id);\n    if(key)users.set(key,e);\n  }\n  for(const key of jinnaAssignments.keys())if(!users.has(key))jinnaAssignments.delete(key);\n  const used=new Set(jinnaAssignments.values());\n  for(const [key,e] of users){\n    let id=jinnaAssignments.get(key);\n    if(!id){id=jinnaPalette.find(color=>!used.has(color)) || 'jinna';used.add(id);jinnaAssignments.set(key,id);}\n    if(e===PL.ent)jinnaSetMine(id);\n    else if(!e.isRemote && e.skin!==id){e.skin=id;soldierLook(e.model,id,skinRel(e));}\n  }\n  if(skinMine()!=='jinna')jinnaSetMine('jinna');\n}\n\nconst SKIN_REL =".replace("JINNA_DATA",jinna_json))
replace("src/06ga-tenues.js", "e === PL.ent ? skinMine() : skinId(e.skin)", "e === PL.ent ? (skinMine()==='jinna' ? jinnaMine : skinMine()) : skinId(e.skin)")
replace("src/06g-body.js", "function soldierGeometry(skin, lod) {", "function soldierGeometry(skin, lod) {\n  if(hasKey(jinnaColors,skin))return jinnaGeometry();")
replace("src/06e-gear.js", "function gearMaterial(skin, mode) {", "function gearMaterial(skin, mode) {\n  if(mode!=='fp' && hasKey(jinnaColors,skin))return jinnaMaterial(skin,mode);")
replace("src/09-game.js", "function startMatch(opt = {}) {", "function startMatch(opt = {}) {\n  jinnaMatchStart();")
replace("src/09-game.js", "  spawnEntity(PL.ent);\n", "  jinnaRoster();\n  spawnEntity(PL.ent);\n")
replace("src/09i-modes.js", "function modeUpdate(dt) {", "function modeUpdate(dt) {\n  jinnaNext-=dt;if(jinnaNext<=0){jinnaNext=.35;jinnaRoster();}")
replace("src/09c-net.js", "  spawnEntity(b);\n}\nfunction netBotOff", "  jinnaRoster();\n  spawnEntity(b);\n}\nfunction netBotOff")

replace("src/01-core.js", "skin: 'assault', lang:", "skin: 'auto', lang:")
replace("src/01-core.js", "Object.assign(Settings, s);", "if(s.skin==='assault' && !s.skinPicked) s.skin='auto'; Object.assign(Settings, s);")
replace("src/09u-tenues.js", "  Settings.skin = s; saveSettings();", "  Settings.skinPicked = true; Settings.skin = s; saveSettings();")
replace("src/06s-defis.js", "const s = skinId(Settings.skin); return skinUnlocked(s)", "if(!['jinna','shotgun'].includes(Settings.skin)) return (!PL.ent || PL.ent.team===0) ? 'jinna' : 'shotgun'; const s = skinId(Settings.skin); return skinUnlocked(s)")
replace("src/09u-tenues.js", "if (s === skinMine() && s === skinId(Settings.skin))", "if (Settings.skinPicked && s === skinMine() && s === skinId(Settings.skin))")
replace("src/09c-net.js", "  const dr = fpvPub(e);", "  if(me && NET.role==='host') p.jc=Array.from(jinnaAssignments).filter(([key])=>NET.players.has(key));\n  const dr = fpvPub(e);")
replace("src/09c-net.js", "  let e = NET.remotes.get(id); if (!e) e = netMakeRemote(id, P);", "  if(NET.role==='client' && id===NET.hostId && Array.isArray(P.jc) && PL.ent){\n    const mine=P.jc.find(row=>Array.isArray(row) && row[0]===NET.me && jinnaVariants.includes(row[1]));\n    if(mine && skinMine()==='jinna')jinnaSetMine(mine[1]);\n  }\n  let e = NET.remotes.get(id); if (!e) e = netMakeRemote(id, P);")

replace("src/09u-tenues.js","const skinListed = () => SKIN_ALL.concat(skinOwned());","const skinListed = () => ['jinna','shotgun'];")

wardrobe=Path('src/09u-tenues.js')
wardrobe_text=wardrobe.read_text()
start=wardrobe_text.index('function skinCardsHtml() {')
end=wardrobe_text.index('\n}',start)+2
wardrobe.write_text(wardrobe_text[:start]+"function skinCardsHtml() { return skinListed().map(skinCardHtml).join(''); }"+wardrobe_text[end:])

jinna_low=gzip.decompress(base64.b64decode((ROOT / "assets/jinna-lo.b64").read_bytes())).decode()
replace("src/06ga-tenues.js","const jinnaData =", "const jinnaLow="+jinna_low+";\nconst jinnaData=")
replace("src/06ga-tenues.js","function jinnaGeometry(){","function jinnaGeometry(lod){\n  const key='jinna'+lod;")
replace("src/06ga-tenues.js","if(SOLDIER_GEOS.jinna) return SOLDIER_GEOS.jinna;","if(SOLDIER_GEOS[key])return SOLDIER_GEOS[key];")
replace("src/06ga-tenues.js","const d=jinnaData,read=","const d=lod==='lo'?jinnaLow:jinnaData,read=")
replace("src/06ga-tenues.js","return SOLDIER_GEOS.jinna=g;","return SOLDIER_GEOS[key]=g;")
replace("src/06g-body.js","return jinnaGeometry();","return jinnaGeometry(lod);")

replace("src/06ga-tenues.js","const SKIN_REL =", "SKINS.shotgun.name='Chiến binh áo choàng';\nSKINS.shotgun.role='Nhân vật gốc · Đội đối thủ';\nconst SKIN_REL =")
replace("src/01-core.js","Object.assign(Settings, s);","if(typeof s.skin==='string' && (s.skin==='cr7' || s.skin.startsWith('cr7_'))) s.skin='shotgun'; Object.assign(Settings, s);")

TACTICAL_MODULE="/* AZONE tactical equipment: one explosive and one smoke mine per life. */\nconst AZTACT = { mines: [], selected: '', seq: 0, hud: null };\nfunction azCaptain(e) {\n  if (!e || MATCH.mode === 'ffa') return false;\n  if (!MATCH.online) return e === entities.filter(o=>!o.off && o.team===e.team).sort((a,b)=>Number(b.isPlayer)-Number(a.isPlayer)||a.id-b.id)[0];\n  const people=[...NET.players.values()].filter(p=>p.ig && p.t===e.team).sort((a,b)=>Number(b.id===NET.hostId)-Number(a.id===NET.hostId)||a.id.localeCompare(b.id));\n  return people.length ? netIdOf(e)===people[0].id : e===entities.filter(o=>!o.off && o.team===e.team).sort((a,b)=>String(netIdOf(a)).localeCompare(String(netIdOf(b))))[0];\n}\nfunction azResetLife(e) {\n  e.azStock={frag:1,smoke:1}; e.azDroneUsed=false;\n  for(const m of AZTACT.mines.slice()) if(m.owner===e) azMineRemove(m);\n  if(e===PL.ent) AZTACT.selected='';\n}\nfunction azMineRemove(m) { scene.remove(m.mesh); m.mesh.geometry.dispose(); m.mesh.material.dispose(); const i=AZTACT.mines.indexOf(m);if(i>=0)AZTACT.mines.splice(i,1); }\nfunction azTacticalClear(){for(const m of AZTACT.mines.slice())azMineRemove(m); AZTACT.selected='';if(AZTACT.hud)AZTACT.hud.style.display='none';}\nfunction azMineAdd(owner,type,p,id) {\n  if(AZTACT.mines.some(m=>m.owner===owner&&m.id===id))return;\n  const mesh=new THREE.Mesh(new THREE.CylinderGeometry(.18,.21,.09,12),new THREE.MeshStandardMaterial({color:type==='smoke'?0xb6c6ca:0x586333,roughness:.85}));\n  mesh.position.copy(p);scene.add(mesh);AZTACT.mines.push({owner,type,p:p.clone(),id,mesh,arm:MATCH.time+1.2});\n}\nfunction azPlaceMine(e,type) {\n  if(!e.alive || !e.onGround || !e.azStock?.[type] || (e===PL.ent && (PILOT.d || MECHA_P.me)))return false;\n  const p=e.pos.clone();p.y=groundHeight(p.x,p.z,p.y+.2)+.06;\n  if(Math.abs(p.y-e.pos.y)>1)return false;\n  e.azStock[type]--;const id=++AZTACT.seq;azMineAdd(e,type,p,id);\n  if(MATCH.online)netEvent({k:'azmine',ty:type,x:p.x,y:p.y,z:p.z,id},e);\n  if(e===PL.ent)hudMsg(type==='smoke'?'Đã đặt mìn khói':'Đã đặt mìn nổ','ally',1.5);\n  return true;\n}\nfunction azMineBurst(m) { if(m.type==='smoke')smokeStart(m.p,m.owner);else explode(m.p,m.owner,'Mìn nổ',5,140,-1);azMineRemove(m); }\nfunction azMineEvent(e,ev){\n  if(ev.k==='azmine'){\n    if(!e.alive || !['frag','smoke'].includes(ev.ty) || !Number.isSafeInteger(ev.id) || ![ev.x,ev.y,ev.z].every(Number.isFinite))return;\n    const p=new V3(ev.x,ev.y,ev.z);if(p.distanceTo(e.pos)>4 || AZTACT.mines.filter(m=>m.owner===e&&m.type===ev.ty).length)return;\n    azMineAdd(e,ev.ty,p,ev.id);\n  }else if(ev.k==='azboom') {const m=AZTACT.mines.find(m=>m.owner===e&&m.id===ev.id);if(m)azMineBurst(m);}\n}\nfunction azDroneLaunch(){\n  const e=PL.ent;if(!e.alive || PILOT.d || MECHA_P.me)return;\n  if(!azCaptain(e)){hudMsg('Drone chỉ dành cho trưởng team','neutral',2);return;}\n  if(e.azDroneUsed){hudMsg('Đã dùng drone trong lượt sống này','neutral',2);return;}\n  AZTACT.selected='';fpvLaunch(e);\n}\nfunction azTacticalKey(c){\n  if(!PL.ent.alive)return false;\n  if(c==='Digit9'){azDroneLaunch();return true;}\n  if(PILOT.d && c==='KeyB'){PILOT.d.ai=!PILOT.d.ai;PL.yaw=PILOT.d.yaw;PL.pitch=PILOT.d.pitch;return true;}\n  if(c==='Digit8'&&!PILOT.d){AZTACT.selected=AZTACT.selected==='frag'?'smoke':'frag';hudMsg('Chọn '+(AZTACT.selected==='smoke'?'mìn khói':'mìn nổ')+' · Chuột trái đặt · 8 đổi loại','ally',2);return true;}\n  if(['Digit1','Digit2','Digit3','KeyQ','KeyF','KeyG'].includes(c))AZTACT.selected='';\n  return false;\n}\nfunction azTacticalTick(dt){\n  if(MATCH.state!=='playing')return;\n  for(const m of AZTACT.mines.slice()){\n    if(m.owner.off || !m.owner.alive){azMineRemove(m);continue;}\n    if(MATCH.online && !netIsLocal(m.owner))continue;\n    if(MATCH.time<m.arm)continue;\n    if(entities.some(e=>e.alive&&!e.off&&!allied(e,m.owner)&&e.pos.distanceToSquared(m.p)<2.25&&lineClear(m.p.clone().add(new V3(0,.25,0)),entChest(e,new V3())))){\n      if(MATCH.online)netEvent({k:'azboom',id:m.id},m.owner);azMineBurst(m);\n    }\n  }\n  // Bots receive the same two charges and place them only on the simulation owner.\n  for(const e of entities)if(!e.isPlayer&&!e.isRemote&&!e.off&&e.alive&&e.onGround&&(!MATCH.online||netIsLocal(e))&&e.target&&e.target.alive){\n    const age=MATCH.time-e.spawnAt;if(age>8&&e.azStock?.frag&&e.pos.distanceTo(e.target.pos)<14)azPlaceMine(e,'frag');\n    if(age>12&&e.health<60&&e.azStock?.smoke)azPlaceMine(e,'smoke');\n  }\n  if(!AZTACT.hud){const el=document.createElement('div');el.style.cssText='position:fixed;left:50%;bottom:12%;transform:translateX(-50%);color:#eef4ed;background:#101b22c9;border:1px solid #afc8b977;border-radius:8px;padding:9px 16px;text-align:center;font:13px sans-serif;pointer-events:none;z-index:30;max-width:85vw;white-space:pre-line';const label=document.createElement('div');el.append(label);AZTACT.label=label;const controls=document.createElement('div');controls.style.cssText='display:flex;justify-content:center;gap:8px;margin-top:8px';for(const [title,fn] of [['B · TỰ ĐỘNG / BAY TAY',()=>{if(PILOT.d)azTacticalKey('KeyB');}],['PHÁT NỔ',()=>{if(PILOT.d)PILOT.d.boom=true;}]]){const btn=document.createElement('button');btn.textContent=title;btn.style.cssText='pointer-events:auto;padding:8px 12px;color:white;background:#273c43;border:1px solid #b6c6ca;border-radius:4px';btn.addEventListener('pointerdown',ev=>{ev.preventDefault();ev.stopPropagation();fn();});controls.append(btn);}el.append(controls);AZTACT.controls=controls;$('hud').append(el);AZTACT.hud=el;}\n  const d=PILOT.d,stock=PL.ent.azStock||{};AZTACT.hud.style.display=PL.ent.alive?'block':'none';\n  AZTACT.controls.style.display=d?'flex':'none';\n  AZTACT.label.textContent=d?'╲  AZONE • KHOANG LÁI FPV  ╱\\n'+(d.ai?'TỰ ĐỘNG TÌM MỤC TIÊU':'ĐIỀU KHIỂN TAY')+' · B đổi chế độ\\nWASD bay · Space lên · Ctrl xuống · Shift tăng tốc\\nChuột trái: PHÁT NỔ · Cao '+Math.round(d.pos.y-groundHeight(d.pos.x,d.pos.z,d.pos.y))+' m': '8 · Mìn nổ '+(stock.frag||0)+' | Mìn khói '+(stock.smoke||0)+(AZTACT.selected?' • Đang chọn '+(AZTACT.selected==='frag'?'mìn nổ':'mìn khói')+' · Chuột trái đặt':'')+(azCaptain(PL.ent)?'\\nTRƯỞNG TEAM · 9 Drone '+(PL.ent.azDroneUsed?'(đã dùng)':'(sẵn sàng)'):'');\n}\n"
# AZONE commander drone and per-life mines.
Path('src/08h-azone-tactical.js').write_text(TACTICAL_MODULE)
replace('src/07-bots.js', 'function spawnEntity(e) {', 'function spawnEntity(e) {\n  azResetLife(e);')
replace('src/09i-modes.js','function modeStart(mode) {','function modeStart(mode) {\n  azTacticalClear();')
replace('src/09i-modes.js','function modeEnd() {','function modeEnd() { azTacticalClear();')
replace('src/09i-modes.js','function modeUpdate(dt) {','function modeUpdate(dt) {\n  azTacticalTick(dt);')
replace('src/09c-net.js', "  if (!ev || typeof ev !== 'object') return;", "  if (!ev || typeof ev !== 'object') return;\n  if(ev.k==='azmine'||ev.k==='azboom'){azMineEvent(e,ev);return;}")
replace('src/08-player.js', '  if (PILOT.d) return;', '  if (azTacticalKey(c)) return;\n  if (PILOT.d) return;')
replace('src/08-player.js', 'function updatePlayer(dt, now) {', "function updatePlayer(dt, now) {\n  if(AZTACT.selected && PL.ent.alive && !PILOT.d){if(PL.queued)azPlaceMine(PL.ent,AZTACT.selected);PL.queued=false;PL.held=false;}")
replace('src/08e-fpv.js','function fpvLaunch(owner) {', "function fpvLaunch(owner) {\n  if(!azCaptain(owner)||owner.azDroneUsed||!owner.alive||fpvOf(owner))return;\n  owner.azDroneUsed=true;")
replace('src/08e-fpv.js', "d.in.up = (KEYS.Space ? 1 : 0)", "d.in.up = (jumpHeld() ? 1 : 0)")
replace('src/08e-fpv.js', "TOUCH.sprint : !!KEYS.ShiftLeft", "TOUCH.sprint : sprintHeld()")
replace('src/08e-fpv.js', '  d.yaw = PL.yaw; d.pitch = PL.pitch;', '  if(!d.ai){d.yaw = PL.yaw; d.pitch = PL.pitch;}else{PL.yaw=d.yaw;PL.pitch=d.pitch;}')
replace('src/08e-fpv.js', 'if (d.ai) fpvAi(d, dt);', "if (d.ai) fpvAi(d, dt);\n  if(d.local && d.owner===PL.ent && (!d.owner.alive || !azCaptain(d.owner))){fpvEnd(d,false);return;}\n  if(d.ai && d.tgt && d.pos.distanceTo(entChest(d.tgt,new V3()))<1.5 && lineClear(d.pos,entChest(d.tgt,new V3())))d.boom=true;")
replace('src/08e-fpv.js', "  if (fpvOf(owner)) return;", "  if (fpvOf(owner)) return;")
replace('src/08a-binds.js', 'const BIND_DEFS = [', "const BIND_DEFS = [\n  ['azmine','Digit8','Chọn mìn / đổi mìn khói'], ['azdrone','Digit9','Drone trưởng team'], ['azauto','KeyB','Drone: tự động / bay tay'],")
replace('src/08-player.js','PL.nades = C.nades;', 'PL.nades = 0;')
replace('src/07-bots.js','e.nades = NADE_COUNT;', 'e.nades = 0;')


# Drone rules: invulnerable, unlimited flight, explicit detonation only.
replace('src/08e-fpv.js', "if(d.local && d.owner===PL.ent && (!d.owner.alive || !azCaptain(d.owner))){fpvEnd(d,false);return;}", "if(!d.owner.alive){d.ai=false;d.vel.set(0,0,0);d.in.fw=d.in.st=d.in.up=0;return;}")
replace('src/08e-fpv.js', "if(d.ai && d.tgt && d.pos.distanceTo(entChest(d.tgt,new V3()))<1.5 && lineClear(d.pos,entChest(d.tgt,new V3())))d.boom=true;", "")
replace('src/08e-fpv.js', "if (d.boom || d.t >= FPV.life || !d.owner.alive && !d.ai) { fpvEnd(d, d.owner.alive || d.boom); return; }", "if (d.boom) { fpvEnd(d, true); return; }")
replace('src/08e-fpv.js', "if (vn > FPV.crash) { d.pos.copy(to); fpvEnd(d, true); return; }", "// Hard impacts slide/stop; never detonate.")
replace('src/08e-fpv.js', "if (h === FPV_BOOM) { d.pos.copy(to); fpvEnd(d, true); return; }", "if (h === FPV_BOOM) { d.vel.set(0,0,0); return; }")
replace('src/08e-fpv.js', "function fpvDamage(d, dmg, shooter) {", "function fpvDamage(d, dmg, shooter) { return;")
replace('src/08e-fpv.js', "function fpvNetHit(owner, dmg) {", "function fpvNetHit(owner, dmg) { return;")
replace('src/08e-fpv.js', "function fpvBotsShoot(dt) {", "function fpvBotsShoot(dt) { return;")
replace('src/08e-fpv.js', "function fpvEnd(d, boom, send = d.local) {", "function fpvEnd(d, boom, send = d.local) {\n  if(!boom || (d.local && !d.boom))return;")
replace('src/08e-fpv.js', "const d = PILOT.d, left = clamp(1 - d.t / FPV.life, 0, 1);", "const d = PILOT.d, left = 1;")
replace('src/08e-fpv.js', "if (!Array.isArray(a) || a.length < 5 || !e.alive) return;", "if (!Array.isArray(a) || a.length < 5) return;")
replace('src/08e-fpv.js', "function fpvLeave() {", "function fpvLeave() {\n  if(PILOT.d){PILOT.d.mesh.visible=true;PILOT.d.ai=false;PILOT.d.vel.set(0,0,0);PILOT.d.in.fw=PILOT.d.in.st=PILOT.d.in.up=0;}")
replace('src/08h-azone-tactical.js', "e.azDroneUsed=false;", "e.azDroneUsed=!!fpvOf(e);")
replace('src/08h-azone-tactical.js', "if(e.azDroneUsed){hudMsg", "const existing=fpvOf(e);if(existing){PILOT.d=existing;PILOT.yaw=PL.yaw;PILOT.pitch=PL.pitch;PL.yaw=existing.yaw;PL.pitch=existing.pitch;existing.mesh.visible=false;PL.held=PL.queued=false;$('hud').classList.add('fpv');fpvHudText();return;}\n  if(e.azDroneUsed){hudMsg")
replace('src/08h-azone-tactical.js', "AZONE • KHOANG LÁI FPV", "AZONE • FPV • BẤT TỬ • PIN ∞")
