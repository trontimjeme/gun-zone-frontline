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
