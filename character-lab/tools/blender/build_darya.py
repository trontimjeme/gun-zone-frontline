"""AZONE Darya motion prototype. Run: blender -b -t 2 --python tools/blender/build_darya.py
Original procedural model, no third-party character assets. Blender 4.3+.
"""
import bpy, math, os, json
from mathutils import Vector, Matrix, Quaternion

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
OUT = os.path.join(ROOT, 'public/models/darya')
os.makedirs(OUT, exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0, rough=.75):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metallic; p.inputs['Roughness'].default_value=rough
    return m
sand=mat('Sand linen',(.48,.39,.27)); dark=mat('Charcoal cloth',(.065,.076,.080))
leather=mat('Oiled leather',(.105,.055,.027)); bronze=mat('Antique bronze',(.46,.28,.105),.72,.36)
teal=mat('Petrol silk',(.035,.19,.19)); skin=mat('Olive skin',(.43,.26,.16))
steel=mat('Tempered steel',(.42,.49,.53),.85,.25); black=mat('Blackened steel',(.025,.032,.035),.65,.4)
eye=mat('Eyes',(.024,.018,.011),0,.3); white=mat('Eye whites',(.52,.47,.35))
pieces=[]; weights={}; weapon_parts={'Dagger':[], 'Rifle':[]}

def finish(o,name,m,bone=None,weapon=None):
    o.name=name; o.data.materials.append(m)
    if o.type=='MESH':
        for p in o.data.polygons: p.use_smooth=True
    pieces.append(o)
    if bone: weights[o.name]=bone
    if weapon: weapon_parts[weapon].append(o)
    return o

def oval(name, loc, scale, m, bone, weapon=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,location=loc)
    o=bpy.context.object; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,m,bone,weapon)

def box(name,loc,scale,m,bone,weapon=None,bevel=.015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Soft edges','BEVEL');mod.width=bevel;mod.segments=2
        bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    return finish(o,name,m,bone,weapon)

def mesh(name,verts,faces,m,bone,weapon=None):
    d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update()
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o)
    return finish(o,name,m,bone,weapon)

def rod(name,a,b,r,m,bone,weapon=None,r2=None):
    a,b=Vector(a),Vector(b);delta=b-a
    bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=r,radius2=r if r2 is None else r2,depth=delta.length,location=(a+b)/2)
    o=bpy.context.object;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    return finish(o,name,m,bone,weapon)

def line(name,points,r,m,bone):
    for i in range(len(points)-1):rod(name+str(i),points[i],points[i+1],r,m,bone)

# Anatomical rest rig, origin at feet, meters, front -Y.
bpy.ops.object.armature_add();rig=bpy.context.object;rig.name='Darya_Rig'
bpy.ops.object.mode_set(mode='EDIT');rig.data.edit_bones.remove(rig.data.edit_bones[0])
bones={}
def bone(name,a,b,parent=None):
    e=rig.data.edit_bones.new(name);e.head=a;e.tail=b
    if parent:e.parent=rig.data.edit_bones[parent]
    bones[name]=(a,b)
bone('Root',(0,0,0),(0,0,.2))
bone('Hips',(0,0,.91),(0,0,1.04),'Root')
bone('Spine',(0,0,1.04),(0,0,1.25),'Hips')
bone('Chest',(0,0,1.25),(0,0,1.49),'Spine')
bone('Neck',(0,0,1.49),(0,0,1.59),'Chest')
bone('Head',(0,0,1.59),(0,0,1.84),'Neck')
for side,s in [('L',-1),('R',1)]:
    bone('UpperArm.'+side,(s*.265,0,1.44),(s*.34,0,1.16),'Chest')
    bone('Forearm.'+side,(s*.34,0,1.16),(s*.37,0,.94),'UpperArm.'+side)
    bone('Hand.'+side,(s*.37,0,.94),(s*.37,0,.84),'Forearm.'+side)
    bone('Thigh.'+side,(s*.12,0,.96),(s*.14,0,.55),'Hips')
    bone('Shin.'+side,(s*.14,0,.55),(s*.14,0,.14),'Thigh.'+side)
    bone('Foot.'+side,(s*.14,0,.14),(s*.14,-.17,.09),'Shin.'+side)
bpy.ops.object.mode_set(mode='OBJECT')

oval('Pelvis',(0,0,.95),(.23,.14,.17),dark,'Hips')
oval('Tailored torso',(0,0,1.25),(.265,.15,.29),dark,'Chest')
oval('Waist',(0,0,1.06),(.22,.14,.17),dark,'Spine')
for z in [1.035,1.065,1.095]:
    oval('Teal sash',(0,-.001,z),(.239,.155,.039),teal,'Spine')
box('Leather belt',(0,-.005,1.00),(.47,.30,.05),leather,'Hips')
box('Bronze buckle',(0,-.163,1.00),(.074,.025,.055),bronze,'Hips',bevel=.006)
# Layered skirt panels, split for leg clearance, with bronze borders.
for s in [-1,1]:
    v=[(s*.015,-.148,1.02),(s*.22,-.105,1.02),(s*.255,-.13,.70),(s*.075,-.17,.64)]
    mesh('Split tunic',v,[(0,1,2,3)],dark,'Hips')
    line('Tunic piping',[v[1],v[2],v[3]],.007,bronze,'Hips')
    mesh('Side skirt',[(s*.22,-.10,1.02),(s*.22,.12,1.02),(s*.27,.12,.72),(s*.255,-.13,.70)],[(0,1,2,3)],dark,'Hips')
mesh('Sash tails',[(-.12,-.169,1.08),(-.045,-.172,1.08),(-.04,-.20,.64),(-.12,-.19,.69)],[(0,1,2,3)],teal,'Hips')
line('Cross chest leather strap',[(-.23,-.115,1.48),(-.13,-.16,1.32),(.05,-.166,1.12)],.026,leather,'Chest')
line('Strap stitching',[(-.215,-.137,1.48),(-.115,-.182,1.32),(.065,-.188,1.12)],.004,bronze,'Chest')
for side,s in [('L',-1),('R',1)]:
    thigh='Thigh.'+side;shin='Shin.'+side;foot='Foot.'+side
    rod('Trousers thigh',(s*.12,0,.94),(s*.14,0,.55),.107,dark,thigh,r2=.082)
    rod('Trousers calf',(s*.14,0,.55),(s*.14,0,.15),.084,dark,shin,r2=.055)
    oval('Knee',(s*.14,-.01,.55),(.084,.087,.09),dark,shin)
    rod('Tall boot',(s*.14,0,.14),(s*.14,0,.36),.075,leather,shin,r2=.09)
    oval('Boot toe',(s*.14,-.072,.085),(.09,.16,.075),leather,foot)
    box('Boot sole',(s*.14,-.07,.036),(.18,.30,.035),black,foot,bevel=.009)
    for z in [.18,.24,.30]:box('Boot strap',(s*.14,-.078,z),(.15,.024,.022),bronze,shin,bevel=.004)
    upper='UpperArm.'+side;fore='Forearm.'+side;hand='Hand.'+side
    oval('Shoulder',(s*.265,0,1.43),(.105,.116,.115),dark,upper)
    rod('Sleeve',(s*.27,0,1.43),(s*.34,0,1.17),.097,dark,upper,r2=.072)
    rod('Forearm',(s*.34,0,1.16),(s*.37,0,.94),.065,skin,fore,r2=.045)
    rod('Bracer',(s*.345,0,1.11),(s*.365,0,.97),.069,leather,fore,r2=.058)
    for z in [1.00,1.08]:box('Bracer bronze band',(s*.36,-.062,z),(.09,.018,.015),bronze,fore,bevel=.002)
    oval('Glove palm',(s*.37,-.005,.90),(.052,.044,.061),leather,hand)
    for i in range(4):
        x=s*.37+(i-1.5)*.021
        rod('Finger',(x,-.026,.887),(x,-.040,.844),.011,skin,hand)
    oval('Thumb',(s*.325,-.036,.904),(.018,.022,.034),skin,hand)
rod('Neck',(0,0,1.47),(0,0,1.62),.072,skin,'Neck')
oval('Head sculpt',(0,-.008,1.71),(.115,.105,.155),skin,'Head')
oval('Jaw',(0,-.045,1.64),(.085,.08,.08),skin,'Head')
oval('Nose',(0,-.116,1.71),(.027,.037,.045),skin,'Head')
for s in [-1,1]:
    oval('Eye white',(s*.045,-.104,1.755),(.029,.014,.011),white,'Head')
    oval('Iris',(s*.045,-.117,1.755),(.009,.005,.009),eye,'Head')
    line('Brow',[(s*.019,-.115,1.779),(s*.071,-.106,1.785)],.008,dark,'Head')
# Open-front hood: layered shell, facial opening kept visible.
verts=[];faces=[];N=32
levels=[(1.48,.19,.15),(1.59,.155,.14),(1.74,.155,.14),(1.86,.13,.115),(1.92,.04,.06)]
for z,rx,ry in levels:
    for j in range(N):
        a=2*math.pi*j/N;verts.append((rx*math.sin(a),ry*math.cos(a)+.025,z))
for k in range(len(levels)-1):
    for j in range(N):
        a=2*math.pi*(j+.5)/N
        if k<3 and abs(a-math.pi)<.82:continue
        faces.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
faces.append(tuple((len(levels)-1)*N+j for j in range(N)))
hood=mesh('Open hood',verts,faces,sand,'Head')
mod=hood.modifiers.new('Fabric thickness','SOLIDIFY');mod.thickness=.008
bpy.context.view_layer.objects.active=hood;bpy.ops.object.modifier_apply(modifier=mod.name)
line('Hood bronze seam',[(-.13,-.07,1.56),(-.13,-.08,1.77),(-.095,-.08,1.86),(0,-.055,1.915),(.095,-.08,1.86),(.13,-.08,1.77),(.13,-.07,1.56)],.007,bronze,'Head')
oval('Face veil',(0,-.098,1.645),(.119,.051,.080),sand,'Head')
for z in [1.60,1.63,1.66]:line('Veil folds',[(-.095,-.125,z),(.005,-.151,z-.008),(.095,-.125,z+.009)],.005,sand,'Head')
for z,r in [(1.49,.18),(1.52,.16),(1.55,.14)]:
    oval('Scarf wrap',(0,0,z),(r,.14,.035),sand,'Neck')
mesh('Shoulder scarf',[(-.22,.06,1.51),(.17,.11,1.51),(.20,.19,1.15),(-.19,.20,1.22)],[(0,1,2,3)],sand,'Chest')

# Weapon meshes authored in hand rest coordinates and bound to right hand.
x=.37;y=-.045;z=.865
rod('Dagger wrapped grip',(x,y,z+.025),(x,y,z-.095),.021,leather,'Hand.R','Dagger')
oval('Dagger pommel',(x,y,z+.03),(.028,.026,.02),bronze,'Hand.R','Dagger')
box('Dagger crescent guard',(x,y,z-.10),(.13,.042,.022),bronze,'Hand.R','Dagger',bevel=.008)
# Curved, tapered, double-bevel blade. Length 0.32m.
verts=[];faces=[];steps=18
for i in range(steps+1):
    t=i/steps;cx=x+.105*t*t;zz=z-.12-.31*t;w=.031*(1-t)**.6
    verts.extend([(cx-w,y,zz),(cx,y-.009*(1-t),zz),(cx+w,y,zz),(cx,y+.009*(1-t),zz)])
for i in range(steps):
    for j in range(4):faces.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
mesh('Curved Persian blade',verts,faces,steel,'Hand.R','Dagger')
for t in [.2,.4,.6,.8]:
    cx=x+.105*t*t;zz=z-.12-.31*t
    oval('Blade bronze inlay',(cx,y-.010,zz),(.003,.002,.007),bronze,'Hand.R','Dagger')
# Carbine, downwards in rest; arm pose rotates muzzle forward.
box('Rifle receiver',(x,y-.015,z-.08),(.068,.095,.25),black,'Hand.R','Rifle')
box('Rifle stock',(x,y+.012,z+.14),(.066,.10,.19),leather,'Hand.R','Rifle')
box('Rifle handguard',(x,y-.01,z-.29),(.071,.09,.18),dark,'Hand.R','Rifle')
rod('Rifle barrel',(x,y-.01,z-.38),(x,y-.01,z-.56),.014,black,'Hand.R','Rifle')
box('Rifle magazine',(x,y+.09,z-.13),(.055,.16,.085),black,'Hand.R','Rifle')
box('Rifle grip',(x,y+.09,z+.006),(.05,.13,.06),leather,'Hand.R','Rifle')
for zz in [z-.33,z-.22,z-.11]:box('Rifle rail',(x,y-.063,zz),(.071,.015,.04),bronze,'Hand.R','Rifle',bevel=.002)

# Join body by bone to reduce draw calls; weapon variants each remain named.
body=[o for o in pieces if not any(o in arr for arr in weapon_parts.values())]
for o in pieces:
    vg=o.vertex_groups.new(name=weights[o.name]);vg.add(list(range(len(o.data.vertices))),1,'REPLACE')
def join(objects,name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
    o.parent=rig;mod=o.modifiers.new('Darya skin','ARMATURE');mod.object=rig
    return o
body=join(body,'Darya_Body')
dagger=join(weapon_parts['Dagger'],'Dagger');rifle=join(weapon_parts['Rifle'],'Rifle')
for m in bpy.data.materials:
    m.use_backface_culling=False

scene=bpy.context.scene;scene.render.fps=30
clips={}
def reset():
    for p in rig.pose.bones:p.rotation_mode='XYZ';p.rotation_euler=(0,0,0);p.location=(0,0,0)
def pose(t,kind):
    reset();p=rig.pose.bones
    gun=kind in ['RifleIdle','RifleWalk','Fire','Reload']
    p['UpperArm.R'].rotation_euler.x=-1.10 if gun else -.45
    p['Forearm.R'].rotation_euler.x=-.47 if gun else -.65
    p['UpperArm.L'].rotation_euler.x=-1.25 if gun else -.35
    p['UpperArm.L'].rotation_euler.z=.45 if gun else -.12
    p['Forearm.L'].rotation_euler.x=-.35 if gun else -.6
    p['Forearm.L'].rotation_euler.z=.46 if gun else 0
    p['UpperArm.R'].rotation_euler.z=-.25 if gun else .08
    p['Chest'].rotation_euler.x=.012*math.sin(t*2*math.pi)
    if kind in ['Walk','Run','RifleWalk']:
        wave=math.sin(t*2*math.pi);amp=.65 if kind=='Run' else .38
        for side,s in [('L',1),('R',-1)]:
            p['Thigh.'+side].rotation_euler.x=amp*wave*s
            p['Shin.'+side].rotation_euler.x=-max(0,wave*s)*amp*1.25
            p['Foot.'+side].rotation_euler.x=.12*wave*s
        p['Hips'].location.y=.018*abs(wave)
        p['Chest'].rotation_euler.x=-.12 if kind=='Run' else -.025
    if kind=='Crouch':
        p['Hips'].location.y=-.30;p['Thigh.L'].rotation_euler.x=.75;p['Thigh.R'].rotation_euler.x=.75
        p['Shin.L'].rotation_euler.x=-1.3;p['Shin.R'].rotation_euler.x=-1.3;p['Chest'].rotation_euler.x=-.18
    if kind=='Jump':
        h=math.sin(t*math.pi);p['Root'].location.y=.42*h
        p['Thigh.L'].rotation_euler.x=.5*h;p['Thigh.R'].rotation_euler.x=.35*h
        p['Shin.L'].rotation_euler.x=-.8*h;p['Shin.R'].rotation_euler.x=-.6*h
    if kind=='KnifeSlash':
        swing=math.sin(t*math.pi);p['UpperArm.R'].rotation_euler.z=.08-1.3*swing
        p['UpperArm.R'].rotation_euler.x=-.45-1.0*swing;p['Chest'].rotation_euler.z=-.3*swing
    if kind=='Fire':p['Forearm.R'].rotation_euler.x-=.12*max(0,math.sin(t*math.pi*4));p['Chest'].rotation_euler.x+=.035*math.sin(t*math.pi*4)
    if gun:
        # Analytic two-bone reach: both palms contact the rifle instead of floating.
        bpy.context.view_layer.update()
        for side, target in [('R',(.08,-.20,1.25)),('L',(.04,-.34,1.25))]:
            target=Vector(target)
            if kind=='Reload' and side=='L':target+=Vector((-.08,.07,-.12))*math.sin(t*math.pi)
            if kind=='Fire':target.y+=.014*max(0,math.sin(t*math.pi*4))
            upper=p['UpperArm.'+side];fore=p['Forearm.'+side];hand=p['Hand.'+side]
            a=upper.head.copy();delta=target-a;d=delta.length;direction=delta.normalized()
            l1=upper.bone.length;l2=fore.bone.length;d=min(d,l1+l2-.001)
            target=a+direction*d
            along=(l1*l1-l2*l2+d*d)/(2*d);height=math.sqrt(max(0,l1*l1-along*along))
            outward=Vector((-1 if side=='L' else 1,0,-.8));outward=(outward-direction*outward.dot(direction)).normalized()
            elbow=a+direction*along+outward*height
            upper.matrix=Matrix.Translation(a)@(elbow-a).to_track_quat('Y','Z').to_matrix().to_4x4()
            bpy.context.view_layer.update()
            fore.matrix=Matrix.Translation(elbow)@(target-elbow).to_track_quat('Y','Z').to_matrix().to_4x4()
            bpy.context.view_layer.update()
            hand.matrix=Matrix.Translation(target)@Quaternion((1,0,0),-math.pi/2).to_matrix().to_4x4()@hand.bone.matrix_local.to_quaternion().to_matrix().to_4x4()
            bpy.context.view_layer.update()
for name,duration in [('Idle',2),('Walk',1),('Run',.7),('Crouch',2),('Jump',1),('KnifeSlash',.55),('RifleIdle',2),('RifleWalk',1),('Fire',.3),('Reload',1.8)]:
    action=bpy.data.actions.new(name);rig.animation_data_create();rig.animation_data.action=action
    frames=round(duration*30)
    for f in range(frames+1):
        pose(f/frames,name)
        for p in rig.pose.bones:
            p.keyframe_insert('rotation_euler',frame=f+1,group=p.name);p.keyframe_insert('location',frame=f+1,group=p.name)
    action.use_fake_user=True;clips[name]=duration
    # glTF exporter uses separate named NLA tracks for each action.
    track=rig.animation_data.nla_tracks.new();track.name=name
    strip=track.strips.new(name,1,action);track.mute=True
rig.animation_data.action=None;reset();pose(0,'Idle')
scene.frame_start=1;scene.frame_end=60
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Darya_v0.1.blend'), compress=True)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,'darya.glb'),export_format='GLB',export_animations=True,export_animation_mode='NLA_TRACKS',export_nla_strips=True,export_frame_range=False,export_force_sampling=True,export_yup=True)
report={'version':'0.1.0','stage':'motion blockout','height_m':1.92,'clips':clips,'bones':len(rig.data.bones),'vertices':sum(len(o.data.vertices) for o in [body,dagger,rifle]),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in [body,dagger,rifle]),'note':'Rigid segment skinning; cloth/fingers not simulated. Original procedural prototype, not final concept fidelity.'}
with open(os.path.join(OUT,'manifest.json'),'w') as f:json.dump(report,f,indent=2)
print('DARYA_REPORT',json.dumps(report))
