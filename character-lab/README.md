# DARYA • AZONE character lab v0.1

Demo path after branch preview deployment: `/darya/`.

This is an isolated character/animation review room. It does not replace the live game's character or change gameplay, damage, skill logic, network code, or upstream revision.

## Included

Original Persian-inspired motion blockout: hood, face veil, split charcoal tunic, teal sash, bronze trim, leather bracers/boots. Editable Blender source, 18-bone rig, separate skinned curved dagger and proxy rifle.

Ten clips: Idle, Walk, Run, Crouch, Jump, KnifeSlash, RifleIdle, RifleWalk, Fire, Reload. The lab provides orbit/touch camera, front/rear/detail views, equipment switching, crossfades, single-shot return to idle, pause, speed selection and download of the Blender source.

Keyboard shortcuts: 1 knife; 2 rifle; W walk; Shift run; C crouch; Space jump; F slash/fire; R reload. All movement is in place.

## Development

From this folder: `npm ci`, `npm run verify`, `npm run build`.

Rebuild model: `blender -b -t 2 --python tools/blender/build_darya.py`.

After building, copy `dist/` into `../darya-demo/`, rename `darya.html` to `index.html`, and retain `THREE-LICENSE.txt`. The root build copies the prebuilt lab into `dist/darya/` without adding an npm step to the existing Python game build. Base URL is `/darya/`.

## Verification and remaining review

TypeScript/Vite production build passed. `scripts/verify-darya.mjs` loads the real GLB with Three.js, checks all ten named clips, verifies skinned meshes and samples deformed vertices for finite/non-exploded positions. Run and jump tracks are checked for motion. Blender renders were used to inspect idle and rifle poses; two-bone reach adjusts both hands for rifle contact.

Local interactive browser QA was blocked: local Chromium could not create its process socket, and the cloud browser could not reach the local server. Desktop/iPhone UI, animation transitions and visual acceptance still require review on the preview deployment.

This is a visibly simplified procedural motion prototype, not final photorealistic concept fidelity. Skinning uses rigid segments. No image PBR textures, fabric physics, facial/finger animation, FPS arms, foot IK, hit zones, network sync or actual combat skill implementation yet. Rifle is a proxy; Reload is a reach gesture without a detachable-magazine sequence. No collision or live combat correctness is claimed.

Blender units are meters and glTF is Y-up, forward +Z; adapt facing and hit zones when integrating into actual gameplay. Existing upstream license/credits remain unchanged. The prebuilt bundle includes Three.js under MIT (`darya-demo/THREE-LICENSE.txt`).
