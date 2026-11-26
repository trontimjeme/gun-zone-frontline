"""Install the independent school map into the upstream build workspace."""
from pathlib import Path
import json, math, shutil
from PIL import Image, ImageDraw

source = Path(__file__).resolve().parent / "assets" / "Truong8x"
dest = Path("dist/truong8x")
meshes, boxes = json.loads((source / "map.json").read_text())
teams = json.loads((source / "spawn_points.json").read_text())["teams"]
assert len(meshes) == 17 and len(boxes) == 30116
for key, pos, uv, indices in meshes:
    assert key.startswith("textures/") and Path(key).name == key.split("/")[1] and (source / key).is_file()
    assert len(pos) == len(uv) and len(indices) % 3 == 0
    assert min(indices) >= 0 and max(indices) < len(pos)
    assert all(len(p)==3 and all(math.isfinite(x) for x in p) for p in pos)
    assert all(len(p)==2 and all(math.isfinite(x) for x in p) for p in uv)
assert all(len(b)==6 and all(math.isfinite(x) for x in b) and b[0]<b[1] and b[2]<b[3] and b[4]<b[5] for b in boxes)
assert len(teams["CT"]) == len(teams["T"]) == 5
dest.mkdir(parents=True, exist_ok=True)
# Weld glass vertices at UV seams and split into disconnected clusters.
_, gp, guv, gi = next(row for row in meshes if row[0] == "textures/italy_blue_glass.png")
parent = list(range(len(gp)))
def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i
def union(a,b):
    a,b = find(a),find(b)
    if a != b: parent[a] = b
seen = {}
for i,p in enumerate(gp):
    k = tuple(round(x,4) for x in p)
    if k in seen: union(i,seen[k])
    else: seen[k] = i
for i in range(0,len(gi),3):
    a,b,c = gi[i:i+3]
    union(a,b); union(a,c)
groups = {}
for i in range(0,len(gi),3):
    groups.setdefault(find(gi[i]),[]).extend(gi[i:i+3])
panes = []
claimed = set()
for inds in groups.values():
    vertices = [gp[i] for i in set(inds)]
    lo = [min(p[a] for p in vertices) for a in range(3)]
    hi = [max(p[a] for p in vertices) for a in range(3)]
    size = sorted(h-l for l,h in zip(lo,hi))
    assert size[0] <= .12 and size[1] >= .1 and size[2] <= 4, "Unexpected glass component"
    # Match thin collision boxes within glass bounds plus 3.1cm; preserve frames.
    ids = [i for i,b in enumerate(boxes) if all(b[2*a] >= lo[a]-.031 and b[2*a+1] <= hi[a]+.031 for a in range(3))]
    assert ids and not claimed.intersection(ids), "Ambiguous glass collision"
    claimed.update(ids)
    panes.append([inds,ids])
assert len(panes)==94 and len(claimed)==218 and sum(len(p[0]) for p in panes)==len(gi)
(dest / "map.json").write_text(json.dumps([meshes,boxes,panes],separators=(",",":")))
print(f"Truong8x: {len(panes)} breakable glass clusters; {len(claimed)} glass collision boxes; adjacent frames retained.")
shutil.copytree(source / "textures", dest / "textures", dirs_exist_ok=True)
shutil.copy2(source / "spawn_points.json", dest / "spawn_points.json")
# Actual overhead schematic, not a reused Italy thumbnail.
im=Image.new("RGB",(960,540),(40,47,45))
d=ImageDraw.Draw(im)
def point(x,z): return (int(480+x*9.5),int(270+(z+.5)*9.5))
for x0,x1,y0,y1,z0,z1 in sorted(boxes,key=lambda b:b[3]):
    if y1<.7: continue
    c=min(180,85+int(y1*5))
    d.rectangle([point(x0,z0),point(x1,z1)],fill=(c,int(c*.84),int(c*.66)))
for team,color in [("CT",(80,156,240)),("T",(235,130,66))]:
    for x,y,z in teams[team]:
        u,v=point(x,z);d.ellipse((u-5,v-5,u+5,v+5),fill=color)
Path("assets/maps").mkdir(parents=True,exist_ok=True)
im.save("assets/maps/truong8x.webp",quality=88)

def patch(path, old, new):
    p=Path(path); s=p.read_text()
    if s.count(old)!=1: raise RuntimeError(f"Expected one patch target in {path}: {old}")
    p.write_text(s.replace(old,new,1))

js=r"""
const truong8xBases=__BASES__;
let truong8xGlass=null;
function truong8xDrawGlass(){
  const g=truong8xGlass;if(!g||!g.geometry)return;
  const attr=g.geometry.index;let n=0;
  for(const p of g.panes)if(!p.broken){attr.array.set(p.indices,n);n+=p.indices.length;}
  g.geometry.setDrawRange(0,n);attr.needsUpdate=true;
}
function truong8xBreakPane(id){
  const g=truong8xGlass;if(CURMAP.id!=='truong8x'||!g||!Number.isInteger(id)||id<0||id>=g.panes.length)return false;
  const p=g.panes[id];if(p.broken)return false;p.broken=true;
  for(const c of p.colliders){c.noRay=true;c.ray=true;c.azGlassBroken=true;}
  truong8xDrawGlass();return true;
}
function truong8xBreakAt(hit,shooter){
  const g=truong8xGlass;if(CURMAP.id!=='truong8x'||!g)return;
  for(let i=0;i<g.panes.length;i++){
    const p=g.panes[i];if(p.broken)continue;
    if(p.colliders.some(c=>hit.x>=c.x0-.015&&hit.x<=c.x1+.015&&hit.y>=c.y0-.015&&hit.y<=c.y1+.015&&hit.z>=c.z0-.015&&hit.z<=c.z1+.015)){
      if(truong8xBreakPane(i)&&MATCH.online&&netIsLocal(shooter))netEvent({k:'azglass',pane:i},shooter);
      return;
    }
  }
}
function truong8xResetGlass(){
  const g=truong8xGlass;if(!g)return;
  for(const p of g.panes){p.broken=false;for(const c of p.colliders){c.noRay=false;c.ray=false;c.azGlassBroken=false;}}
  truong8xDrawGlass();
}
function truong8xPlaceTeams(){
  for(let team=0;team<2;team++){
    const slots=[];
    const bases=truong8xBases[team];
    for(const [x,y,z] of [...bases,...bases.map(([x,y,z])=>[x+(team?-2:2),y,z])]){
      let best=-1,score=Infinity;
      for(let i=0;i<NAV.count;i++){
        if(NAV.comp[i]!==NAV.mainComp)continue;
        const nx=NAV.nx[i],nz=NAV.nz[i],ny=NAV.ny[i];
        if(team===0?nx>=0:nx<=0)continue;
        if(slots.some(([sx,sz])=>(sx-nx)**2+(sz-nz)**2<2.25))continue;
        const v=(nx-x)**2+(nz-z)**2+4*(ny-y)**2;
        if(v<score){score=v;best=i;}
      }
      if(best>=0)slots.push([NAV.nx[best],NAV.nz[best]]);
    }
    if(!slots.length)throw new Error('Map Trường 8x: không có điểm xuất phát hợp lệ cho đội '+team);
    SPAWNS[team]=slots;
  }
}
MAPS.push({id:'truong8x',name:'Map Trường 8x',tag:'Hồi ức sân trường',desc:'Sân trường và dãy lớp học · hai đội xuất phát ở hai đầu bản đồ.',nostalgia:'Hồi ức sân trường 8x, 9x',ok:true});
MAP_DEFS.truong8x={
  type:'mid',bounds:{x0:-45,x1:45,z0:-28,z1:27},
  splat:{x0:-48,z0:-30,w:96,d:60,ppm:4},
  textures:MAP_DEFS.sable.textures,skyPhoto:{...MAP_DEFS.italy.skyPhoto},atmo:{...MAP_DEFS.italy.atmo},
  spawns:truong8xBases[0].map(([x,y,z])=>[x,z]),
  poi:[[0,0,0,'M']],zones:[['Sân trường',-45,45,-28,27]],
  lane:x=>x < -15?'L':x>15?'E':'M',
  sniper:[0,0,0],coverZ:25,heli:[45,27],cam:52,surface:()=> 'concrete',
  async build(){
    const res=await fetch('truong8x/map.json');
    if(!res.ok)throw new Error('Không tải được Map Trường 8x: '+res.status);
    const [meshes,boxes,panes]=await res.json();
    truong8xGlass={geometry:null,panes:panes.map(([indices,ids])=>({indices,ids,broken:false,colliders:[]}))};
    const glassBoxes=new Map();for(let i=0;i<panes.length;i++)for(const j of panes[i][1])glassBoxes.set(j,i);
    const loader=new THREE.TextureLoader(),mats=new Map();
    await Promise.all(meshes.map(async ([id])=>{
      const tex=await loader.loadAsync('truong8x/'+id);
      tex.flipY=false;tex.wrapS=tex.wrapT=THREE.RepeatWrapping;tex.encoding=THREE.sRGBEncoding;
      const isGlass=id==='textures/italy_blue_glass.png';
      const mat=new THREE.MeshStandardMaterial(isGlass?{map:tex,color:0xc6e3f0,roughness:.12,metalness:.15,envMapIntensity:1.25,transparent:true,opacity:.38,depthWrite:false,side:THREE.DoubleSide}:{map:tex,roughness:1,metalness:0,side:THREE.DoubleSide});
      if(isGlass)mat.forceSinglePass=true;
      mat.addEventListener('dispose',()=>tex.dispose());mats.set(id,mat);
    }));
    for(const [id,pos,uv,indices] of meshes){
      const geom=new THREE.BufferGeometry();
      geom.setAttribute('position',new THREE.Float32BufferAttribute(pos.flat(),3));
      geom.setAttribute('uv',new THREE.Float32BufferAttribute(uv.flat(),2));
      geom.setIndex(indices);geom.computeVertexNormals();geom.computeBoundingSphere();
      const mesh=new THREE.Mesh(geom,mats.get(id));mesh.receiveShadow=true;mapAdd(mesh);
      if(id==='textures/italy_blue_glass.png'){truong8xGlass.geometry=geom;geom.index.setUsage(THREE.DynamicDrawUsage);mesh.receiveShadow=false;}
    }
    for(let j=0;j<boxes.length;j++){
      const [x0,x1,y0,y1,z0,z1]=boxes[j],pane=glassBoxes.get(j);
      const c={x0,x1,y0,y1,z0,z1,m:pane===undefined?'stone':'glass',ray:false};
      if(pane!==undefined){c.azGlassPane=pane;truong8xGlass.panes[pane].colliders.push(c);}
      COL.push(c);
    }
  }
};
"""
p=Path("src/02yz-italy.js")
p.write_text(p.read_text()+"\n"+js.replace("__BASES__",json.dumps([teams["CT"],teams["T"]])))
patch("src/09a-loading.js","if (id === 'italy' || id === 'csdrone') italyPlaceTeams();","if (id === 'italy' || id === 'csdrone') italyPlaceTeams(); else if (id === 'truong8x') truong8xPlaceTeams();")
patch("src/02-relief.js","const gy0 = (x, z) =>","const gy0 = (x, z) => CURMAP.id === 'truong8x' ? -0.5 :")
patch("src/01-core.js","['italy', 'simoun'].includes(Settings.map)","['italy', 'simoun', 'csdrone', 'truong8x'].includes(Settings.map)")
patch("src/09e-menus.js","MAPS.filter(m=>m.id==='italy'||m.id==='csdrone')","MAPS.filter(m=>m.id==='italy'||m.id==='csdrone'||m.id==='truong8x')")
patch("src/09e-menus.js","title.textContent=m.id==='csdrone'?'CS DRONE':'CS ITALY 1.6'","title.textContent=m.id==='truong8x'?'MAP TRƯỜNG 8X':m.id==='csdrone'?'CS DRONE':'CS ITALY 1.6'")
patch("src/09e-menus.js","(m.id==='csdrone'?'CS DRONE':'CS ITALY')","(m.id==='truong8x'?'TRƯỜNG 8X':m.id==='csdrone'?'CS DRONE':'CS ITALY')")
# Ignore broken pane boxes in all spatial queries, and only break on real bullet impacts.
patch("src/02-map.js","_qarr.push(COL[i]);","if(!COL[i].azGlassBroken)_qarr.push(COL[i]);")
patch("src/07-bots.js","impactFx(end, wn, wm, def.fam === 'sniper');","if(wm==='glass'&&CURMAP.id==='truong8x')truong8xBreakAt(end,shooter);\n    impactFx(end, wn, wm, def.fam === 'sniper');")
patch("src/09c-net.js","} else if (ev.k === 'prop') {","} else if (ev.k === 'azglass') {\n    if(CURMAP.id==='truong8x'&&e.alive)truong8xBreakPane(ev.pane);\n  } else if (ev.k === 'prop') {")
patch("src/09a-loading.js","function mapUnload() {","function mapUnload() {\n  truong8xGlass=null;")
patch("src/09-game.js","function startMatch(opt = {}) {","function startMatch(opt = {}) {\n  if(CURMAP.id==='truong8x')truong8xResetGlass();")
print("Truong8x: validated 17 mesh batches, 30116 collision boxes, 10 source spawns; installed Italy HDRI and breakable glass.")
