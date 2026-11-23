const AZ_LOCAL_MAP = 'azone_local';
let azLocalInfo = null;

function azGameMap(data) {
  const {boxes} = AZMapFile.validate(data);
  const bounds = AZMapFile.extents(boxes);
  const cx = (bounds.x0+bounds.x1)/2, cz = (bounds.z0+bounds.z1)/2;
  const rx = Math.max(12, Math.ceil((bounds.x1-bounds.x0)/2)+5);
  const rz = Math.max(12, Math.ceil((bounds.z1-bounds.z0)/2)+5);
  if (rx > 58 || rz > 58) throw new Error('Kích thước map vượt quá 106 m trên trục X hoặc Z.');
  const materials = {wall:'plaster', roof:'rooftiles', floor:'pavers', building:'brick'};
  const spawns = Array.from({length: 12}, (_, i) => [((i % 6)-2.5)*2.5, rz-2-Math.floor(i/6)*2]);
  const base = MAP_DEFS.sable;
  return {
    type:'mid', atmo:base.atmo,
    bounds:{x0:-rx,x1:rx,z0:-rz,z1:rz},
    splat:{x0:-rx-10,z0:-rz-10,w:2*rx+20,d:2*rz+20,ppm:2},
    textures:['plaster','rooftiles','pavers','brick'],
    build() {
      DECOR.save().world(1);
      DECOR.plane('pavers', 2*rx+4, 2*rz+4);
      DECOR.restore();
      for (const b of boxes) {
        const [x,y,z] = b.position;
        boxC(materials[b.kind], x-cx, y, z-cz, ...b.size, {rot:b.yaw});
      }
      box('pavers',-rx-.4,rx+.4,0,2.6,-rz-.4,-rz);
      box('pavers',-rx-.4,rx+.4,0,2.6,rz,rz+.4);
      box('pavers',-rx-.4,-rx,0,2.6,-rz,rz);
      box('pavers',rx,rx+.4,0,2.6,-rz,rz);
    },
    spawns, poi:[], zones:[], lane:()=> 'M', coverZ:rz-4, heli:[rx,rz], cam:Math.max(rx,rz), surface:()=> 'concrete'
  };
}

function azMapImportRow() {
  const wrapper = document.createElement('div');
  wrapper.style.gridColumn = '1 / -1';
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json,application/json';
  input.hidden = true;
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'btn';
  button.textContent = 'Nạp file map AZONE · Solo';
  const feedback = document.createElement('p');
  feedback.setAttribute('role', 'status');
  button.onclick = () => input.click();
  input.onchange = async () => {
    if (!input.files.length) return;
    button.disabled = true;
    try {
      const definition = azGameMap(await AZMapFile.read(input.files[0]));
      if (MAPL.jobId === AZ_LOCAL_MAP && MAPL.job) await MAPL.job.catch(() => {});
      if (MAPL.id === AZ_LOCAL_MAP) mapRelease();
      MAP_DEFS[AZ_LOCAL_MAP] = definition;
      azLocalInfo = {id:AZ_LOCAL_MAP, name:'Map AZONE đã nạp', tag:'Solo', desc:'Map dựng từ file AZONE trên thiết bị này.', ok:true};
      Settings.map = AZ_LOCAL_MAP;
      Settings.mode = 'tdm';
      renderSolo();
    } catch (error) {
      feedback.textContent = error.message;
    } finally {
      input.value = '';
      button.disabled = false;
    }
  };
  wrapper.append(button, input, feedback);
  return {k:'node',key:'azone-map-import',node:wrapper};
}
