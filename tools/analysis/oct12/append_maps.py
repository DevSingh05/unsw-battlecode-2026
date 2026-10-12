#!/usr/bin/env python3
"""append_maps.py (historical, already applied on 12 Oct): how bot/maps_data.hpp got its 14 Qualifier maps. It builds
maps_data.hpp = the 33-entry file (all entries byte-identical, same order) with the 14 Qualifier maps (bundled in maps/
by unswbc 1.2.11) APPENDED as MAP33..MAP46. It needs the 33-entry file as input (variants/qf1/maps_data.hpp), so it
will refuse to run on today's 47-entry bot/maps_data.hpp. Output goes to work/oct12/appended/.

Run from the project root:  python3 tools/analysis/oct12/append_maps.py
Uses tools/genmaps.py parse() (same tables as every existing entry). Appending keeps every old map's candidate
order, so on an old map candidates.front() / identifyByStart still pick the old entry first.
Also stamps main.cpp's last line with the hash of maps_data.hpp: the unswbc build cache keys on the directory name
plus .c/.cpp contents only, so a header-only change would otherwise reuse a stale wasm."""
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from genmaps import parse  # noqa: E402

NEW = ["athena", "atlantis", "caution", "detention", "ezam", "hive", "maelstrom", "metro", "ouroboros", "thermopylae",
       "troll_australia", "trolley_problem", "trolley_problem_buffed", "whale_song"]
SYM = {"none": 0, "x": 1, "y": 2, "xy": 3}
SRC = ROOT / "variants" / "qf1" / "maps_data.hpp"
OUT = ROOT / "work" / "oct12" / "appended" / "maps_data.hpp"
MAIN = OUT.parent / "main.cpp"


def main():
    text = SRC.read_text()
    lines = text.split("\n")
    i_struct = next(i for i, l in enumerate(lines) if l.startswith("struct KnownMap {"))
    i_end = next(i for i, l in enumerate(lines) if l == "};" and i > i_struct)
    i_count = next(i for i, l in enumerate(lines) if l.startswith("static const int KNOWN_MAP_COUNT = "))
    n_old = int(re.search(r"= (\d+);", lines[i_count]).group(1))
    rows = [l for l in lines[i_struct + 2:i_end] if l.strip().startswith('{"')]
    assert len(rows) == n_old == 33, (len(rows), n_old)
    arrays, entries = [], []
    for k, stem in enumerate(NEW):
        m = parse(ROOT / "maps" / f"{stem}.map")
        i = n_old + k
        arrays.append(f"// {m['name']} {m['w']}x{m['h']}")
        arrays.append(f"static const int16_t MAP{i}_NXT[] = {{{','.join(map(str, m['nxt']))}}};")
        arrays.append(f"static const uint16_t MAP{i}_GMIN[] = {{{','.join(map(str, m['gmin']))}}};")
        arrays.append(f"static const uint16_t MAP{i}_GMAX[] = {{{','.join(map(str, m['gmax']))}}};")
        flat = []
        for team, pts in m["dragons"]:
            flat += [team, len(pts), pts[0][0], pts[0][1]]
        arrays.append(f"static const int16_t MAP{i}_DRAGONS[] = {{{','.join(map(str, flat)) or '0'}}};")
        nm = m["name"].replace('"', "")
        entries.append(f'  {{"{nm}", {m["w"]}, {m["h"]}, {SYM[m["sym"]]}, {m["unit_limit"]}, {len(m["dragons"])},'
                       f" MAP{i}_NXT, MAP{i}_GMIN, MAP{i}_GMAX, MAP{i}_DRAGONS}},")
    # old arrays end with a blank line before the struct
    assert lines[i_struct - 1] == ""
    out = (lines[:i_struct - 1] + ["// ---- appended by work/kn1/append_maps.py: the 14 Qualifier maps (unswbc 1.2.11 maps/)"]
           + arrays + lines[i_struct - 1:i_end] + entries + lines[i_end:i_count]
           + [f"static const int KNOWN_MAP_COUNT = {n_old + len(NEW)};"] + lines[i_count + 1:])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out))
    # sanity: every old line is still there, in order
    old_set = lines
    new_lines = OUT.read_text().split("\n")
    it = iter(new_lines)
    for l in old_set:
        if l.startswith("static const int KNOWN_MAP_COUNT"):
            continue
        assert any(l == x for x in it), f"old line lost: {l[:80]}"
    h = hashlib.sha1(OUT.read_bytes()).hexdigest()[:12]
    if not MAIN.exists():
        print(f"wrote {OUT}, sha1 {h}")
        return
    mt = MAIN.read_text()
    mt = re.sub(r"\n// kn1 stage: .*\n?$", "\n", mt)
    if not mt.endswith("\n"):
        mt += "\n"
    MAIN.write_text(mt + f"// kn1 stage: bot/ + QE_KR 2 + UNK_PORTAL_SIDES 2 + 14 maps appended; maps_data sha1 {h}\n")
    print(f"wrote {OUT} ({n_old} + {len(NEW)} = {n_old + len(NEW)} maps, {OUT.stat().st_size // 1024} KB), sha1 {h}")


if __name__ == "__main__":
    main()
