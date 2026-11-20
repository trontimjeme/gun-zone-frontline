"""Hide the persistent equipment-key tutorial while preserving drone cockpit HUD."""
from pathlib import Path
p=Path("src/08h-azone-tactical.js")
s=p.read_text()
old="AZTACT.hud.style.display=PL.ent.alive?'block':'none';"
new="AZTACT.hud.style.display=(PL.ent.alive&&!!PILOT.d)?'block':'none';"
assert s.count(old)==1, "Tactical HUD signature changed; refusing unsafe patch"
p.write_text(s.replace(old,new))
print("Persistent weapon tutorial hidden; FPV drone status retained.")
