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
