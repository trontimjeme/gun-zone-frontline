#!/usr/bin/env python3
"""Validate the safe intermediate AZONE map manifest (not a game importer)."""
import json
import math
import pathlib
import re
import sys

MAP_ID = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
TEAMS = {"T", "CT"}

def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ["root must be a JSON object"]
    if data.get("schemaVersion") != 1:
        errors.append("schemaVersion must be 1")
    map_id = data.get("mapId")
    if not isinstance(map_id, str) or not MAP_ID.fullmatch(map_id):
        errors.append("mapId must be lowercase snake_case, 2-64 chars")
    if data.get("units") != "meters":
        errors.append("units must be meters; convert explicitly before export")
    geo = data.get("geometry")
    if not isinstance(geo, dict):
        errors.append("geometry object required")
    else:
        p = geo.get("glb")
        if not isinstance(p, str) or not p.endswith(".glb") or pathlib.PurePosixPath(p).is_absolute() or ".." in pathlib.PurePosixPath(p).parts or "\\" in p or p.startswith("/"):
            errors.append("geometry.glb must be a relative safe .glb path")
        scale = geo.get("scaleToMeters")
        if isinstance(scale, bool) or not isinstance(scale, (float, int)) or not math.isfinite(scale) or scale <= 0:
            errors.append("geometry.scaleToMeters must be finite and positive")
    spawns = data.get("spawns")
    if not isinstance(spawns, list):
        errors.append("spawns must be an array")
    else:
        ids = set()
        for i, s in enumerate(spawns):
            label = f"spawns[{i}]"
            if not isinstance(s, dict):
                errors.append(f"{label} must be an object")
                continue
            sid = s.get("id")
            if not isinstance(sid, str) or not MAP_ID.fullmatch(sid) or sid in ids:
                errors.append(f"{label}.id must be unique safe identifier")
            ids.add(sid)
            if s.get("team") not in TEAMS:
                errors.append(f"{label}.team must be T or CT")
            pos = s.get("position")
            if not isinstance(pos, list) or len(pos) != 3 or any(isinstance(x, bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in pos):
                errors.append(f"{label}.position must contain 3 finite coordinates")
            yaw = s.get("yawDegrees")
            if isinstance(yaw,bool) or not isinstance(yaw,(int,float)) or not math.isfinite(yaw):
                errors.append(f"{label}.yawDegrees must be finite")
    return errors

def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_map.py <manifest.json>", file=sys.stderr)
        return 2
    try:
        data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"Cannot load manifest: {e}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        for e in errors: print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"PASS: {data['mapId']} manifest validated (structure only, not a playable map)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
