#!/bin/sh
set -eu
revision=09e3e30da33d21df02d515b6500156ac427de444
destination=${1:?Usage: sh build-pascal.sh NEW_DIRECTORY}
if [ -e "$destination" ]; then echo "Destination must not exist" >&2; exit 1; fi
command -v git >/dev/null
command -v bun >/dev/null
command -v node >/dev/null
[ "$(bun --version)" = "1.4.4" ] || { echo "Bun 1.4.4 required" >&2; exit 1; }
mkdir -p "$destination"
git init "$destination"
cd "$destination"
git remote add origin https://github.com/pascalorg/editor.git
git fetch --depth=1 origin "$revision"
git checkout --detach FETCH_HEAD
[ "$(git rev-parse HEAD)" = "$revision" ]
node -e 'const p=require("./apps/editor/package.json"); for(const n of ["editor","viewer","core","nodes"]) if(!p.dependencies["@pascal-app/"+n]) throw Error(n+" missing")'
export CI=1
bun install --frozen-lockfile
bun run --cwd apps/editor check-types
bun run --cwd apps/editor test
# Normal Next build is required for upstream smoke (next start and image optimizer).
PASCAL_PORTABLE_BUILD=0 bun run --cwd apps/editor build
PASCAL_PORTABLE_BUILD=0 bun run --cwd apps/editor smoke
echo "Pascal build and server smoke passed; browser and GLB acceptance remain separate."
