/* Shared, data-only interchange between AZONE Editor and Gun Zone Solo. */
const AZMapFile = (() => {
  const materials = { wall: '#c7a274', roof: '#9f5140', floor: '#a59a82', building: '#bb906b' };
  const validVec = (v, count, limit) => Array.isArray(v) && v.length === count &&
    v.every(x => Number.isFinite(x) && Math.abs(x) <= limit);
  const positive = (v, fallback) => Number.isFinite(v) && v > 0 ? v : fallback;
  const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
  const number = value => Number.isFinite(value) ? value : 0;

  function extents(boxes) {
    const bounds = {x0: Infinity, x1: -Infinity, z0: Infinity, z1: -Infinity};
    for (const b of boxes) {
      const [x, , z] = b.position, [w, , d] = b.size;
      const c = Math.abs(Math.cos(b.yaw)), s = Math.abs(Math.sin(b.yaw));
      const dx = (c*w+s*d)/2, dz = (s*w+c*d)/2;
      bounds.x0 = Math.min(bounds.x0, x-dx);
      bounds.x1 = Math.max(bounds.x1, x+dx);
      bounds.z0 = Math.min(bounds.z0, z-dz);
      bounds.z1 = Math.max(bounds.z1, z+dz);
    }
    return bounds;
  }

  function validate(data) {
    if (data?.format !== 'azone-gun-zone-map' || data.version !== 1 || data.units !== 'meters' ||
        !Array.isArray(data.boxes) || !data.boxes.length || data.boxes.length > 600) {
      throw new Error('Cần file map AZONE v1 có từ 1 đến 600 khối.');
    }
    const boxes = data.boxes.map(b => {
      if (!validVec(b?.position, 3, 100) || !validVec(b?.size, 3, 100) || b.size.some(x => x < .025) ||
          !Number.isFinite(b.yaw) || Math.abs(b.yaw) > 100 || !Object.hasOwn(materials, b.kind)) {
        throw new Error('Khối map có kích thước, tọa độ, góc hoặc vật liệu không hợp lệ.');
      }
      return { position: b.position.slice(), size: b.size.slice(), yaw: b.yaw, kind: b.kind };
    });
    const b = extents(boxes);
    if (b.x1-b.x0 > 106 || b.z1-b.z0 > 106) throw new Error('Kích thước map vượt quá 106 m trên trục X hoặc Z.');
    return { format: 'azone-gun-zone-map', version: 1, units: 'meters', boxes };
  }

  // Pascal uses X/Z wall points and wall-local opening positions measured from the start.
  function fromPascal(data) {
    const nodes = data?.nodes;
    if (!nodes || typeof nodes !== 'object' || !Array.isArray(data.rootNodeIds) ||
        Object.keys(nodes).length > 2000) throw new Error('JSON không phải cảnh Pascal hợp lệ.');
    const boxes = [];
    const visited = new Set();
    const get = id => typeof id === 'string' && Object.hasOwn(nodes, id) ? nodes[id] : null;
    const shift = (p, x, y, z, yaw = 0) => [
      p[0] + x * Math.cos(p[3]) + z * Math.sin(p[3]), p[1] + y,
      p[2] - x * Math.sin(p[3]) + z * Math.cos(p[3]), p[3] + yaw
    ];
    function add(p, w, h, d, kind) {
      if (Math.min(w, h, d) < .025) return;
      if (boxes.length >= 600) throw new Error('Cảnh vượt giới hạn 600 khối.');
      boxes.push({ position: p.slice(0, 3), size: [w, h, d], yaw: p[3], kind });
    }
    function visit(id, p, levelHeight, depth) {
      if (depth > 30 || visited.has(id)) throw new Error('Cây cảnh Pascal bị lặp hoặc quá sâu.');
      const n = get(id);
      if (!n || n.visible === false) return;
      visited.add(id);
      const children = Array.isArray(n.children) ? n.children : [];
      const pos = validVec(n.position, 3, 100) ? n.position : [0, 0, 0];
      const yaw = number(Array.isArray(n.rotation) ? n.rotation[1] : n.rotation);
      if (n.type === 'building' || n.type === 'roof' || n.type === 'roof-segment') p = shift(p, ...pos, yaw);
      if (n.type === 'level') {
        p = shift(p, 0, number(n.baseElevation), 0);
        levelHeight = positive(n.height, 3);
      }
      if (n.type === 'wall' && validVec(n.start, 2, 100) && validVec(n.end, 2, 100)) {
        const [x, z] = n.start;
        const dx = n.end[0] - x, dz = n.end[1] - z;
        const length = Math.hypot(dx, dz), height = positive(n.height, levelHeight);
        const frame = shift(p, x, 0, z, -Math.atan2(dz, dx));
        const thickness = positive(n.thickness, .23);
        const openings = children.map(get).filter(o => o?.visible !== false &&
          (o?.type === 'door' || o?.type === 'window') && validVec(o.position, 3, 100) &&
          Number.isFinite(o.width) && o.width > 0 && Number.isFinite(o.height) && o.height > 0).map(o => [
            clamp(o.position[0] - o.width / 2, 0, length), clamp(o.position[0] + o.width / 2, 0, length),
            clamp(o.position[1] - o.height / 2, 0, height), clamp(o.position[1] + o.height / 2, 0, height)
          ]);
        const cutsX = [...new Set([0, length, ...openings.flatMap(o => o.slice(0, 2))])].sort((a,b) => a-b);
        const cutsY = [...new Set([0, height, ...openings.flatMap(o => o.slice(2))])].sort((a,b) => a-b);
        if (cutsX.length * cutsY.length > 2400) throw new Error('Tường có quá nhiều lỗ mở.');
        for (let i = 1; i < cutsX.length; i++) for (let j = 1; j < cutsY.length; j++) {
          const a = cutsX[i - 1], b = cutsX[i], c = cutsY[j - 1], d = cutsY[j];
          const mx = (a+b)/2, my = (c+d)/2;
          if (!openings.some(o => mx > o[0] && mx < o[1] && my > o[2] && my < o[3])) {
            add(shift(frame, mx, c, 0), b-a, d-c, thickness, 'wall');
          }
        }
      }
      if (n.type === 'roof-segment') {
        const overhang = positive(n.overhang, 0) * 2;
        add(p, positive(n.width, 4) + overhang, positive(n.deckThickness, .18), positive(n.depth, 4) + overhang, 'roof');
      }
      if ((n.type === 'slab' || n.type === 'floor') && Array.isArray(n.polygon?.points) &&
          n.polygon.points.length >= 3 && n.polygon.points.length <= 200 &&
          n.polygon.points.every(v => validVec(v, 2, 100))) {
        const xs = n.polygon.points.map(point => point[0]), zs = n.polygon.points.map(point => point[1]);
        const x0 = Math.min(...xs), x1 = Math.max(...xs), z0 = Math.min(...zs), z1 = Math.max(...zs);
        add(shift(p, (x0+x1)/2, 0, (z0+z1)/2), x1-x0, positive(n.thickness, .18), z1-z0, 'floor');
      }
      for (const child of children) visit(child, p, levelHeight, depth + 1);
    }
    for (const root of data.rootNodeIds) visit(root, [0, 0, 0, 0], 3, 0);
    return validate({ format: 'azone-gun-zone-map', version: 1, units: 'meters', boxes });
  }

  async function read(file) {
    if (!file || file.size > 2 * 1024 * 1024) throw new Error('File JSON phải nhỏ hơn hoặc bằng 2 MB.');
    try { return JSON.parse(await file.text()); }
    catch { throw new Error('Không đọc được JSON. Kiểm tra lại định dạng file.'); }
  }
  return { validate, fromPascal, read, materials, extents };
})();
