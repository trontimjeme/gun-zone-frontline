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
python3 build.py
cp dist/riposte-frontline.html dist/index.html
cp LICENSE NOTICE.md assets/sfx/credits.json dist/
mkdir -p "$root/dist"
cp -R dist/. "$root/dist/"
