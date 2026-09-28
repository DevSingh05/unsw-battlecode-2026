#!/usr/bin/env python3
"""Compare the DRAGON (start) lines in replays with the reference map files; flags team-swapped layouts.
    python3 notes/tools/v16diag/layouts.py replays/v16
"""
import sys, os, json, glob, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..'))
import replay_decode as R
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
ref = {}
for f in glob.glob(os.path.join(ROOT, 'notes/maps/*.map')):
    txt = open(f).read(); name = re.search(r'MAP_NAME (.*)', txt)
    if not name: continue
    ref.setdefault(name.group(1).strip(), [l.split() for l in txt.splitlines() if l.startswith('DRAGON')])
d = sys.argv[1]
led = {g['game']: g for g in json.load(open(os.path.join(d, 'ledger.json')))} if os.path.exists(os.path.join(d, 'ledger.json')) else {}
for f in sorted(glob.glob(os.path.join(d, '*.replay'))):
    gid = int(os.path.basename(f).split('.')[0])
    o = R.load(f); txt = o['map']; name = re.search(r'MAP_NAME (.*)', txt).group(1).strip()
    dr = [l.split() for l in txt.splitlines() if l.startswith('DRAGON')]
    r = ref.get(name)
    if r is None: st = 'noref'
    elif dr == r: st = 'same'
    elif [x[2:] for x in dr] == [x[2:] for x in r]: st = 'TEAMSWAP'
    else: st = 'different'
    g = led.get(gid, {})
    print(gid, name, st, g.get('side'), g.get('win'))
