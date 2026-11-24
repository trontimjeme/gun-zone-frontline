#!/bin/sh
set -eu
root=$(pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
revision=31ca050d8ce59f4885c01a3237f68cdf186c9b60
if [ -f upstream/build.py ]; then
  cp -R upstream/. "$work/"
else
  curl -fsSL "https://codeload.github.com/BenDBSS/Riposte-Frontline-Source/tar.gz/$revision" | tar -xz --strip-components=1 -C "$work"
fi
cp azone-logo.png "$work/"
cd "$work"
if ! python3 -c 'import PIL' 2>/dev/null; then
  python3 -m pip install --target "$work/vendor" Pillow==11.3.0
  export PYTHONPATH="$work/vendor"
fi
python3 "$root/brand.py"
python3 "$root/localize.py"
python3 "$root/hide_equipment_tutorial.py"
python3 "$root/italy_real.py"
python3 "$root/cs_italy_style.py"
python3 "$root/pulse_h03.py"
curl -fsSL --retry 3 https://texas-eta.vercel.app/audio/theme.mp3 -o dist/menu-theme.mp3
echo '218b40825e8f5a56ed2a65558cd958b2378b45fdf1fa8fa2d5e90082fa207f5b  dist/menu-theme.mp3' | sha256sum -c -
python3 "$root/restore_native_mobile.py"
python3 build.py
cp dist/riposte-frontline.html dist/index.html
python3 "$root/restore_native_mobile.py"
cp LICENSE NOTICE.md assets/sfx/credits.json dist/
mkdir -p "$root/dist"
cp -R dist/. "$root/dist/"
