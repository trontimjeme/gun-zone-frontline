"""Convert the uploaded Doi Khang COLLADA scene during the production build."""
from pathlib import Path
import json, math, shutil, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
source=Path(__file__).resolve().parent/"assets/GUNZONE_DOI_KHANG_ASSETS"
dest=Path("dist/truong8x")
dest.mkdir(parents=True,exist_ok=True)
(dest/"textures").mkdir(exist_ok=True)
root=ET.parse(source/"doi-khang.dae").getroot()
ns={"c":root.tag.split("}")[0][1:]}
def q(e,s): return e.find(s,ns)
def qa(e,s): return e.findall(s,ns)
ids={e.get("id"):e for e in root.iter() if e.get("id")}
def ref(s): return ids[s.lstrip("#")]
def mul(a,b): return [sum(a[i*4+k]*b[k*4+j] for k in range(4)) for i in range(4) for j in range(4)]
I=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
scale=float(q(root,"c:asset/c:unit").get("meter"))
assert q(root,"c:asset/c:up_axis").text.strip()=="Z_UP"
materials={}
for m in qa(root,"c:library_materials/c:material"):
    fx=ref(q(m,"c:instance_effect").get("url"))
    d=q(fx,".//c:diffuse")
    color=q(d,"c:color")
    tex=q(d,"c:texture")
    key="textures/"+m.get("id")+".png"
    if tex is not None:
        key="textures/Brick_Tumbled.jpg"
        shutil.copy2(source/"Brick_Tumbled.jpg",dest/key)
    else:
        rgb=tuple(max(0,min(255,round(float(v)*255))) for v in color.text.split()[:3]) if color is not None else (170,170,170)
        Image.new("RGB",(8,8),rgb).save(dest/key)
    materials[m.get("id")]=key
meshes_by_key={}
boxes=[]
def array(s):
    a=q(s,"c:float_array"); ac=q(s,"c:technique_common/c:accessor")
    v=list(map(float,a.text.split())); stride=int(ac.get("stride","1")); off=int(ac.get("offset","0"))
    return [v[off+i*stride:off+(i+1)*stride] for i in range(int(ac.get("count")))]
cache={}
def geometry(g):
    if g.get("id") in cache:return cache[g.get("id")]
    mesh=q(g,"c:mesh"); out=[]
    for t in qa(mesh,"c:triangles"):
        inputs=qa(t,"c:input"); stride=max(int(i.get("offset","0")) for i in inputs)+1
        vi=next(i for i in inputs if i.get("semantic")=="VERTEX")
        pi=next(i for i in qa(ref(vi.get("source")),"c:input") if i.get("semantic")=="POSITION")
        pos=array(ref(pi.get("source")))
        ui=next((i for i in inputs if i.get("semantic")=="TEXCOORD"),None)
        uv=array(ref(ui.get("source"))) if ui is not None else None
        idx=list(map(int,q(t,"c:p").text.split()))
        out.append((t.get("material"),pos,uv,idx,stride,int(vi.get("offset","0")),int(ui.get("offset","0")) if ui is not None else 0))
    cache[g.get("id")]=out
    return out
def walk(node,parent,depth=0):
    assert depth<100
    mat=q(node,"c:matrix")
    world=mul(parent,list(map(float,mat.text.split()))) if mat is not None else parent
    for inst in qa(node,"c:instance_geometry"):
        binds={m.get("symbol"):materials[m.get("target").lstrip("#")] for m in qa(inst,".//c:instance_material")}
        for sym,pos,uv,idx,stride,vo,uo in geometry(ref(inst.get("url"))):
            key=binds[sym]
            row=meshes_by_key.setdefault(key,[key,[],[],[]])
            for start in range(0,len(idx),stride*3):
                pts=[]
                for k in range(3):
                    j=start+k*stride; p=pos[idx[j+vo]]
                    x,y,z=[sum(world[a*4+b]*p[b] for b in range(3))+world[a*4+3] for a in range(3)]
                    p=[x*scale,z*scale,-y*scale]
                    pts.append(p)
                    row[3].append(len(row[1]));row[1].append(p)
                    row[2].append(uv[idx[j+uo]][:2] if uv is not None else [p[0],p[2]])
                lo=[min(p[a] for p in pts) for a in range(3)]
                hi=[max(p[a] for p in pts) for a in range(3)]
                # Axis-aligned surfaces become thin colliders; sloped surfaces use
                # triangle bounding boxes, which are conservative approximations.
                if sum((hi[a]-lo[a])>.001 for a in range(3))>=2:
                    boxes.append([v for a in range(3) for v in (lo[a]-.015,hi[a]+.015)])
    for child in qa(node,"c:node"):walk(child,world,depth+1)
    for inst in qa(node,"c:instance_node"):walk(ref(inst.get("url")),world,depth+1)
scene=ref(q(root,"c:scene/c:instance_visual_scene").get("url"))
for node in qa(scene,"c:node"):walk(node,I)
meshes=list(meshes_by_key.values())
assert meshes and boxes
points=[p for row in meshes for p in row[1]]
lo=[min(p[a] for p in points) for a in range(3)]
hi=[max(p[a] for p in points) for a in range(3)]
cx=(lo[0]+hi[0])/2;cz=(lo[2]+hi[2])/2
for p in points:p[0]-=cx;p[2]-=cz
for b in boxes:
    b[0]-=cx;b[1]-=cx;b[4]-=cz;b[5]-=cz
# Deduplicate identical collider bounds.
boxes=[list(b) for b in dict.fromkeys(tuple(round(v,4) for v in b) for b in boxes)]
hx=(hi[0]-lo[0])/2;hz=(hi[2]-lo[2])/2
assert hx>2 and hz>2
hx=math.ceil(hx)
hz=math.ceil(hz)
bounds={"x0":-hx-1,"x1":hx+1,"z0":-hz-1,"z1":hz+1}
assert all(isinstance(v,int) for v in bounds.values())
assert (2*hx+2)*(2*hz+2)<250000, 'Map navigation grid too large'
teams={t:[[sign*hx*.7,0,hz*f] for f in (-.4,-.2,0,.2,.4)] for t,sign in (("CT",-1),("T",1))}
(dest/"map.json").write_text(json.dumps([meshes,boxes,[]],separators=(",",":")))
(dest/"spawn_points.json").write_text(json.dumps({"teams":teams}))
im=Image.new("RGB",(960,540),(40,47,45))
d=ImageDraw.Draw(im)
s=min(440/hx,240/hz)
for x0,x1,y0,y1,z0,z1 in sorted(boxes,key=lambda b:b[3]):
    if y1<.1:continue
    c=max(60,min(180,85+int(y1*5)))
    d.rectangle((480+x0*s,270+z0*s,480+x1*s,270+z1*s),fill=(c,int(c*.84),int(c*.66)))
Path("assets/maps").mkdir(parents=True,exist_ok=True)
im.save("assets/maps/truong8x.webp",quality=88)
print("DOI KHANG",len(meshes),len(boxes),bounds)

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
let truong8xSpawnFloors=null;
function truong8xBuildSpawnFloors(){
  const sizes=new Map();
  for(let i=0;i<NAV.count;i++)sizes.set(NAV.comp[i],(sizes.get(NAV.comp[i])||0)+1);
  truong8xSpawnFloors=[[],[],[]];
  for(let i=0;i<NAV.count;i++){
    const x=NAV.nx[i],y=NAV.ny[i],z=NAV.nz[i];
    if(sizes.get(NAV.comp[i])<20)continue;
    const f=y<1?0:y<5?1:2;
    if(f>=0&&NAV.adjStart[i+1]-NAV.adjStart[i]>=2)truong8xSpawnFloors[f].push(i);
  }
  console.info('Truong8x spawn floor nodes',truong8xSpawnFloors.map(a=>a.length));
}
function truong8xRandomSpawn(e){
  if(!truong8xSpawnFloors)return null;
  const ctx=spawnCtx(e),team=spawnBase(e.team);
  const floors=truong8xSpawnFloors.filter(a=>a.length);
  // Randomize floor first rather than favoring the floor with the most nodes.
  for(let pass=0;pass<2;pass++){
    const order=floors.slice();
    for(let k=order.length-1;k>0;k--){const j=Math.floor(Math.random()*(k+1));[order[j],order[k]]=[order[k],order[j]];}
    for(const floor of order){
      for(let k=0;k<Math.min(80,floor.length*2);k++){
        const i=floor[Math.floor(Math.random()*floor.length)],x=NAV.nx[i],y=NAV.ny[i],z=NAV.nz[i];
        if(MATCH.mode!=='ffa'&&(team===0?x> -2:x<2))continue;
        if(entities.some(o=>o!==e&&o.alive&&!o.off&&Math.abs(o.pos.y-y)<1.8&&Math.hypot(o.pos.x-x,o.pos.z-z)<2))continue;
        if(ctx.foes.some(o=>Math.abs(o.pos.y-y)<2.5&&Math.hypot(o.pos.x-x,o.pos.z-z)<6))continue;
        if(!pass&&spawnSeen(ctx,x,z,y))continue;
        return new V3(x,y,z);
      }
    }
  }
  return null;
}
function truong8xPlaceTeams(){
  truong8xBuildSpawnFloors();
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
    if(!slots.length)throw new Error('Map Đối Kháng: không có điểm xuất phát hợp lệ cho đội '+team);
    SPAWNS[team]=slots;
  }
}
MAPS.push({id:'truong8x',name:'Map Đối Kháng',tag:'Đối kháng',desc:'Map mới · hai đội đối kháng.',nostalgia:'Map Đối Kháng',ok:true});
MAP_DEFS.truong8x={
  type:'mid',bounds:__BOUNDS__,
  splat:__SPLAT__,
  textures:MAP_DEFS.sable.textures,skyPhoto:{...MAP_DEFS.italy.skyPhoto},atmo:{...MAP_DEFS.italy.atmo},
  spawns:truong8xBases[0].map(([x,y,z])=>[x,z]),
  poi:[[0,0,0,'M']],zones:[['Đối kháng',__ZONE__]],
  lane:x=>x < -15?'L':x>15?'E':'M',
  sniper:[0,0,0],coverZ:25,heli:[45,27],cam:52,surface:()=> 'concrete',
  async build(){
    const res=await fetch('truong8x/map.json');
    if(!res.ok)throw new Error('Không tải được Map Đối Kháng: '+res.status);
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
p.write_text(p.read_text()+"\n"+js.replace("__BASES__",json.dumps([teams["CT"],teams["T"]])).replace("__BOUNDS__",json.dumps(bounds)).replace("__SPLAT__",json.dumps(dict(x0=-hx-2,z0=-hz-2,w=2*hx+4,d=2*hz+4,ppm=4))).replace("__ZONE__",','.join(map(str,[-hx,hx,-hz,hz]))))
patch("src/09a-loading.js","if (id === 'italy' || id === 'csdrone') italyPlaceTeams();","if (id === 'italy' || id === 'csdrone') italyPlaceTeams(); else if (id === 'truong8x') truong8xPlaceTeams();")
patch("src/02-relief.js","const gy0 = (x, z) =>","const gy0 = (x, z) => CURMAP.id === 'truong8x' ? -0.5 :")
patch("src/01-core.js","['italy', 'simoun'].includes(Settings.map)","['italy', 'simoun', 'csdrone', 'truong8x'].includes(Settings.map)")
patch("src/09e-menus.js","MAPS.filter(m=>m.id==='italy'||m.id==='csdrone')","MAPS.filter(m=>m.id==='italy'||m.id==='csdrone'||m.id==='truong8x')")
patch("src/09e-menus.js","title.textContent=m.id==='csdrone'?'CS DRONE':'CS ITALY 1.6'","title.textContent=m.id==='truong8x'?'MAP ĐỐI KHÁNG':m.id==='csdrone'?'CS DRONE':'CS ITALY 1.6'")
patch("src/09e-menus.js","(m.id==='csdrone'?'CS DRONE':'CS ITALY')","(m.id==='truong8x'?'ĐỐI KHÁNG':m.id==='csdrone'?'CS DRONE':'CS ITALY')")
# Ignore broken pane boxes in all spatial queries, and only break on real bullet impacts.
patch("src/02-map.js","_qarr.push(COL[i]);","if(!COL[i].azGlassBroken)_qarr.push(COL[i]);")
patch("src/07-bots.js","impactFx(end, wn, wm, def.fam === 'sniper');","if(wm==='glass'&&CURMAP.id==='truong8x')truong8xBreakAt(end,shooter);\n    impactFx(end, wn, wm, def.fam === 'sniper');")
patch("src/09c-net.js","} else if (ev.k === 'prop') {","} else if (ev.k === 'azglass') {\n    if(CURMAP.id==='truong8x'&&e.alive)truong8xBreakPane(ev.pane);\n  } else if (ev.k === 'prop') {")
patch("src/09a-loading.js","function mapUnload() {","function mapUnload() {\n  truong8xGlass=null;truong8xSpawnFloors=null;")
patch("src/09-game.js","function startMatch(opt = {}) {","function startMatch(opt = {}) {\n  if(CURMAP.id==='truong8x')truong8xResetGlass();")

# Force the CPU/GPU text overlay off globally without touching dynamic resolution.
p=Path("shell.html")
p.write_text(p.read_text().replace("</style>","#perf{display:none!important}</style>",1))
patch("src/09-game.js","if (Settings.perf) updatePerfHud();","if (false) updatePerfHud();")
patch("src/09zo-perfs.js","PFR.on = !!Settings.perf;","PFR.on = false;")
patch("src/09i-modes.js","function chooseSpawn(e) {","function chooseSpawn(e) {\n  if(CURMAP.id==='truong8x'){const p=truong8xRandomSpawn(e);if(p)return p;}")

print("Truong8x: installed open entrances, multi-floor random spawns, Italy HDRI, breakable glass and hidden performance HUD.")
