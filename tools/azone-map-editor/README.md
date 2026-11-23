# AZONE 3D MAP EDITOR — Phase 1

This directory is the integration workspace for Pascal Editor and Gun Zone. **It does not replace the game renderer.** This is a development bootstrap, not yet a deployed AZONE UI.

## Fastest verified way to launch the upstream editor locally

Requirements: supported Node.js version; verify [Pascal's current README](https://github.com/pascalorg/editor#readme).

```sh
npx @pascal-app/cli editor
```

This starts an actual Pascal 3D editor with local project persistence, avoiding reimplementation. For a standalone AZONE Next.js host, consume the upstream published components `@pascal-app/core`, `@pascal-app/viewer`, `@pascal-app/editor`, `@pascal-app/nodes` and read the concrete host API in [packages/editor/README.md](https://github.com/pascalorg/editor/blob/main/packages/editor/README.md). It documents `<Editor layoutVersion="v2" projectId={...} onLoad={...} onSave={...} />`.

## Stage gates

1. Verify editor launches and can save/load a simple scene.
2. Capture one authentic GLB scene and its source units. No hardcoded map scale.
3. Generate a Gun Zone export manifest using `map-manifest.schema.json`; validate with `validate_map.py`.
4. Implement the game-specific scene importer only once the actual runtime collision/geometry contract is inspected.
5. Match dimensions to original CS Italy SketchUp reference `cs1.6.skp`; do not reuse Sable geometry.
6. Test separately, keeping all original maps and iPhone controls untouched.

## Example manifest validation

```sh
python3 tools/azone-map-editor/validate_map.py tools/azone-map-editor/example.map.json
```

This **does not** import geometry into Gun Zone: it checks the portability/structural data contract before the importer is written.
