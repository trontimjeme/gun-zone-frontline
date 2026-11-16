from pathlib import Path
from PIL import Image
import os, re, shutil

logo = Image.open("azone-logo.png").convert("RGB")
logo.save("assets/logo.webp", lossless=True)
mark = logo.crop((3, 3, 39, 39))
for path in [*Path("assets/icon").glob("*"), *Path("assets/deck").glob("*"), Path("assets/apercu.jpg")]:
    if path.suffix not in {".ico", ".png", ".jpg"}:
        continue
    size = Image.open(path).size
    canvas = Image.new("RGB", size, logo.getpixel((0, 0)))
    art = mark if size[0] == size[1] else logo
    ratio = min(size[0] / art.width, size[1] / art.height) * 0.9
    art = art.resize(tuple(max(1, round(v * ratio)) for v in art.size), Image.Resampling.LANCZOS)
    canvas.paste(art, tuple((a-b)//2 for a,b in zip(size,art.size)))
    canvas.save(path)
for path in [Path("shell.html"), Path("build.py"), Path("assets/deck/installer.sh"), Path("i18n/en.txt"), *Path("src").glob("*.js")]:
    s = path.read_text()
    s = re.sub("Riposte: Frontline", "Gun ZONE", s, flags=re.I)
    s = s.replace('"short_name":"Riposte"', '"short_name":"Gun ZONE"').replace("www.playriposte.com", "gun-zone-frontline.vercel.app")
    if path.name == "05-audio.js":
        s = re.sub(r"const HIT_SAMPLE = '[^']*'", "const HIT_SAMPLE = 'AAAAAA=='", s)
    path.write_text(s)
for path in [*Path("assets/anim").glob("clips.*"), *Path("assets/sfx/fin").glob("*.mp3"), Path("dist/menu-theme.mp3")]:
    path.unlink(missing_ok=True)
Path("assets/rankup.mp3").write_bytes(b"")

def edit_source(file, old, new):
    path = Path("src") / file
    content = path.read_text()
    if content.count(old) != 1:
        raise ValueError(f"Unexpected source in {file}")
    path.write_text(content.replace(old, new))

edit_source("07-bots.js", "const BOT_NAMES = [\n  ['Dubois', 'Keller', 'Marchetti', 'Okafor', 'Novak'],", """const azoneRoster = ['AZONE TUẤN ANH', 'AZONE HÀ J', 'AZONE MINH CẬN', 'AZONE MINH CON',
  'AZONE TÙNG CẤU', 'AZONE GIANG', 'AZONE VUI', 'AZONE MY'];
for (let i = azoneRoster.length - 1; i > 0; i--) {
  const j = Math.floor(Math.random() * (i + 1));
  [azoneRoster[i], azoneRoster[j]] = [azoneRoster[j], azoneRoster[i]];
}
const BOT_NAMES = [
  azoneRoster.slice(0, 5),""")
edit_source("07-bots.js", "const TEAM_NAMES = ['Alpha', 'Bravo'];", "const TEAM_NAMES = ['AZONE', 'Bravo'];")
edit_source("09e-menus.js", "const SOLO_PAGES = {", """function soloNameRow() {
  const input = document.createElement('input');
  input.maxLength = 16;
  input.autocomplete = 'nickname';
  input.placeholder = 'Nhập tên của bạn';
  input.value = NET.nick;
  input.setAttribute('aria-label', 'Đặt tên người chơi');
  input.addEventListener('change', () => {
    const field = $('netName');
    field.value = input.value.normalize('NFC');
    field.dispatchEvent(new Event('change'));
    input.value = NET.nick;
    PL.ent.name = NET.nick;
    renderSolo();
  });
  return { k: 'text', key: 'soloName', label: 'Đặt tên người chơi', input };
}
const SOLO_PAGES = {""")
edit_source("09e-menus.js", "if (netInLobby()) rows.push({ k: 'note', text: SRV.on", "if (!ACCT.user) rows.unshift(soloNameRow());\n    if (netInLobby()) rows.push({ k: 'note', text: SRV.on")
edit_source("09-game.js", "for (let i = 0; i < 5; i++) makeBot", "PL.ent.name = NET.nick || _t('Vous');\n    for (let i = 0; i < 5; i++) makeBot")

# Shared in-match HUD for desktop and touch.
hud_style = """<style>
#killfeed,body.touch #killfeed{left:auto;right:max(12px,env(safe-area-inset-right));top:max(12px,env(safe-area-inset-top));align-items:flex-end;pointer-events:none}
#hitmarker.head::after{content:'💀';position:absolute;left:0;top:0;transform:translate(-50%,-50%);font:30vmin/1 'Segoe UI Emoji','Apple Color Emoji',sans-serif;filter:grayscale(1) brightness(1.65);opacity:.29;pointer-events:none}
</style>"""
shell = Path("shell.html")
shell.write_text(shell.read_text().replace("</head>", hud_style + "</head>", 1))
