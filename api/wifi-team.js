const { createHash } = require('node:crypto');
const { isIP } = require('node:net');

module.exports = (req, res) => {
  res.setHeader('Cache-Control', 'private, no-store');
  const ip = String(req.headers['x-vercel-forwarded-for'] || req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  if (!isIP(ip)) return res.status(503).json({error:'Không xác định được mạng.'});
  const network = isIP(ip) === 6 ? ipv6Prefix(ip) : ip;
  const team = createHash('sha256').update('gun-zone-wifi-v1/' + network).digest('hex').slice(0,32);
  res.json({team});
};

function ipv6Prefix(ip) {
  const [left, right = ''] = new URL('http://[' + ip + ']').hostname.slice(1,-1).split('::');
  const a = left ? left.split(':') : [], b = right ? right.split(':') : [];
  return [...a, ...Array(8-a.length-b.length).fill('0'), ...b].slice(0,4).join(':');
}
