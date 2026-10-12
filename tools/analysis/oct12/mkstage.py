#!/usr/bin/env python3
"""mkstage.py NAME [FLAG=VAL ...] [--src DIR]: staged build = copy of SRC (default bot/) with #define lines
prepended to params.hpp, in work/oct12/stage/NAME. main.cpp gets a last-line stamp because the unswbc build cache keys
on the directory name plus .c/.cpp contents only (a header-only change would reuse a stale wasm).

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct12/mkstage.py kn2a QE_KR=2 UNK_PORTAL_SIDES=2 QUAL_KNOWN=0x3FFF"""
import hashlib
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
args = sys.argv[1:]
src = ROOT / "bot"
if "--src" in args:
    i = args.index("--src")
    src = ROOT / args[i + 1]
    del args[i:i + 2]
name, flags = args[0], args[1:]
dst = ROOT / "work/oct12/stage" / name
dst.mkdir(parents=True, exist_ok=True)
for f in src.iterdir():
    if f.name in (".unswbc-build", "main.cpp.orig", ".DS_Store"):
        continue
    if f.is_dir():
        shutil.copytree(f, dst / f.name, dirs_exist_ok=True)
    else:
        shutil.copy2(f, dst / f.name)
hdr = f"// STAGED BUILD {name}: {' '.join(flags)}\n" + "".join(f"#define {kv.split('=')[0]} {kv.split('=')[1]}\n" for kv in flags)
(dst / "params.hpp").write_text(hdr + (src / "params.hpp").read_text())
h = hashlib.sha1()
for f in sorted(dst.rglob("*.hpp")):
    h.update(f.read_bytes())
main = (src / "main.cpp").read_text()
if not main.endswith("\n"):
    main += "\n"
(dst / "main.cpp").write_text(main + f"// stage {name}: {' '.join(flags)}; headers sha1 {h.hexdigest()[:12]}\n")
print(dst)
