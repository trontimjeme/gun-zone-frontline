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
maps = {"Khamsin":"ANH HÙNG THỜI LOẠN","Val-Blanc":"Ga Núi Tuyết","Kervénec":"Cảng Hoàng Hôn","Hortus":"Vườn Bách Thảo","Meltem":"Đảo Gió","Tephra":"Trạm Núi Lửa","Stratus":"Quần Đảo Trên Mây","Simoun":"Biển Cát","French Dream":"Khu Ngoại Ô"}
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

Path('src/02yz-italy.js').write_text("MAPS.push({id:'italy', name:'CS_Italy 1.6',tag:'Làng Ý',desc:'Những ngõ hẹp và quảng trường của CS_Italy.',ok:true});\nconst italyBases=[\n[[-19,47],[-15,49],[-15,46],[-18,50],[-21,43],[-17,43],[-13,43],[-27,47],[-13,50],[-27,50]],\n[[7,-55],[11,-53],[6,-52],[10,-50],[3,-50],[10,-62],[24,-52],[16,-51],[4,-59],[3,-56]]];\nconst italyHeights=new Map();\nfunction italyPlaceTeams(){\n  italyHeights.clear();\n  for(let team=0;team<2;team++){\n    const slots=[];\n    for(const [x,z] of italyBases[team]){\n      let best=-1,score=Infinity;\n      const height=team?9.32:3;\n      for(let i=0;i<NAV.count;i++){\n        if(NAV.comp[i]!==NAV.mainComp)continue;\n        const nx=NAV.nx[i], nz=NAV.nz[i];\n        const d=(nx-x)**2+(nz-z)**2+4*(NAV.ny[i]-height)**2;\n        if(d>=score || slots.some(([sx,sz])=>(sx-nx)**2+(sz-nz)**2<2.25))continue;\n        best=i;score=d;\n      }\n      if(best<0)throw new Error('Thiếu điểm xuất phát trên đường đi của bot');\n      const sx=NAV.nx[best],sz=NAV.nz[best];\n      slots.push([sx,sz]);italyHeights.set(sx+','+sz,NAV.ny[best]);\n    }\n    SPAWNS[team]=slots;\n  }\n}\nMAP_DEFS.italy={\n type:'mid',bounds:{x0:-44,x1:31,z0:-67,z1:67},splat:{x0:-48,z0:-72,w:88,d:144,ppm:4},\n textures:MAP_DEFS.sable.textures,atmo:ATMO_SABLE,void:{kill:-4},spawns:italyBases[0],\n poi:[[-18,3,46,'M'],[8,9.32,-54,'M']],zones:[['Phố cổ',-44,31,-67,67]],lane:x=>x < -15?'L':x>5?'E':'M',\n sniper:[-18,3,46],coverZ:60,heli:[44,65],cam:64,surface:()=> 'concrete',\n async build(){\n   const response=await fetch('italy/map.json');\n   if(!response.ok)throw new Error('Không tải được CS_Italy');\n   const [meshes,boxes]=await response.json();\n   const loader=new THREE.TextureLoader(), mats=new Map();\n   await Promise.all([...new Set(meshes.map(row=>row[0]))].map(async id=>{\n     const tex=await loader.loadAsync('italy/'+id+'.png');\n     tex.flipY=false;tex.wrapS=tex.wrapT=THREE.RepeatWrapping;tex.encoding=THREE.sRGBEncoding;\n     const mat=new THREE.MeshLambertMaterial({map:tex,side:THREE.DoubleSide,alphaTest:0.48});\n     mat.addEventListener('dispose',()=>tex.dispose());mats.set(id,mat);\n   }));\n   for(const [id,pos,uv,indices] of meshes){\n     const geom=new THREE.BufferGeometry();\n     geom.setAttribute('position',new THREE.Float32BufferAttribute(pos.flat(),3));\n     geom.setAttribute('uv',new THREE.Float32BufferAttribute(uv.flat(),2));\n     geom.setIndex(indices);geom.computeVertexNormals();\n     const mesh=new THREE.Mesh(geom,mats.get(id));mesh.receiveShadow=true;mapAdd(mesh);\n   }\n   for(const [x0,x1,y0,y1,z0,z1] of boxes)COL.push({x0,x1,y0,y1,z0,z1,m:'stone',ray:false});\n }\n};\n")
replace("src/09a-loading.js", "def.build(); tissusBuild();", "await def.build(); tissusBuild();")
replace("src/09a-loading.js", "buildNav(); buildCovers();", "buildNav(); if (id === 'italy') italyPlaceTeams(); buildCovers();")
replace("src/02-relief.js", "const gy0 = (x, z) => (RELIEF.on ? reliefAt(x, z) : 0);", "const gy0 = (x, z) => CURMAP.id === 'italy' ? (italyHeights.get(x + ',' + z) || 0) : (RELIEF.on ? reliefAt(x, z) : 0);")
