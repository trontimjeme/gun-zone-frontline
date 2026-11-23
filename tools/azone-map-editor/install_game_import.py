"""Install the editor interchange and Solo-only map importer in the pinned game."""
from pathlib import Path

root = Path(__file__).resolve().parents[2]
editor = root / "experiments/pascal-italy-demo"
Path("src/02zz-azone-import.js").write_text(
    (editor / "map-format.js").read_text() + "\n" + (editor / "game-import.js").read_text()
)

def replace(path, before, after):
    path = Path("src") / path
    source = path.read_text()
    if source.count(before) != 1:
        raise ValueError(f"Unexpected pinned source in {path}: {before}")
    path.write_text(source.replace(before, after, 1))

replace("02-map.js", "=> MAPS.find((m) => m.id === id && m.ok) || MAPS[0];",
        "=> (id === AZ_LOCAL_MAP && azLocalInfo) || MAPS.find((m) => m.id === id && m.ok) || MAPS[0];")
replace("09e-menus.js", "const rows = [ // la carte et les paramètres sont dans l'encart, sous le menu",
        "const rows = [azMapImportRow(), // Solo-only map import")
replace("09c-net.js", "const map = mapById(c.map).id, mode =",
        "const map = mapById(c.map === AZ_LOCAL_MAP ? 'italy' : c.map).id, mode =")
