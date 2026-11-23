# Pascal Editor → Gun ZONE: integration assessment and implementation plan

Status: **proposal / integration preparation only**. No game runtime, production maps, controls, or deployments are changed.

Source: https://github.com/pascalorg/editor (MIT). Pascal is a browser-based architectural modeller with an extensible scene graph, React viewer/editor packages, local CLI, and MCP. It is **not** a drop-in Counter-Strike/FPS map editor.

## Why this belongs in a separate map-authoring workflow

Use Pascal to author static architecture (walls, slabs, doors, windows and building masses), not to replace the FPS rendering engine. Existing CS Italy assets remain intact; export into a **new** map ID (e.g. `ITALY_REAL`) only after verification.

## Integration boundaries

1. **Authoring**: independently run Pascal Editor or embed `@pascal-app/editor` in a separate React-compatible tool. The documented package set is:
   `@pascal-app/core`, `@pascal-app/viewer`, `@pascal-app/editor`, `@pascal-app/nodes`.
   Bootstrap the built-in nodes with `loadPlugin(builtinPlugin)` before rendering.
2. **Export adapter** (to be implemented): identify the actual Pascal scene schema/version and write a **versioned** conversion layer. Transform site/building/world coordinates into the game's coordinate system. Apply unit scaling using a known measurement from the existing `cs1.6.skp` reference, not guessed dimensions. Retain node IDs/source metadata.
3. **Game assets**: triangulate/build meshes, generate UVs/material identifiers, reduce draw calls and polygon counts, create level-of-detail meshes as needed. Produce colliders, navigation metadata, spawn points, triggers, lighting and occlusion using the game engine's native pipeline. Never assume Pascal scene data contains these FPS-specific features.
4. **Validation**: enforce finite transforms, supported types, valid triangles, nonzero scales, safe asset paths and world bounds. Compare known distances against the CS Italy reference. Confirm playable mobile FPS and map loading on iPhone.
5. **Release**: add a separate map selection option, preserve existing `CS_ITALY`, build/test preview deployment, only then consider merge/deploy with explicit approval.

## Integration experiment

Run Pascal independently (requires supported Node version; see upstream docs):

```sh
npx @pascal-app/cli editor
```

Or self-host Pascal with persistent SQLite data and an admin password, rather than trying to operate its Docker/SQLite server as a stateless Vercel function.

For React-based authoring tools, install the published packages:

```sh
npm install @pascal-app/core @pascal-app/viewer @pascal-app/editor @pascal-app/nodes
```

For AI agent editing, Pascal provides local MCP via `pascal mcp connect` or hosted MCP at `https://editor.pascal.app/api/mcp` (hosted authentication required). Keep credentials server-side.

## Work needed before functional integration

- Identify the actual build system and runtime module locations for Gun ZONE; the repository root does not expose a `package.json` through the GitHub Contents API.
- Obtain a sample Pascal scene export and confirm its exact schema, geometry accessors and coordinate system.
- Inspect the current game's map loader, collision format and material loading conventions.
- Implement adapter plus tests against real sample exports; add preview-only integration.
- Validate 1:1 spatial consistency against the provided CS Italy SketchUp model.

## Licensing and limitations

Pascal Editor is MIT licensed: retain copyright and license notices when distributing source or copied code. Hosted Pascal services have distinct account terms. Pascal's architectural tools do not automatically produce SketchUp `.skp` files or game-ready maps. Do not promise 100% map similarity, photorealism, or mobile performance without validation.

Upstream documentation: https://github.com/pascalorg/editor/blob/main/README.md
