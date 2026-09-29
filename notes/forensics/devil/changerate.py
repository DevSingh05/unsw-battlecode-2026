#!/usr/bin/env python3
"""How often does a patched binary decide differently from v29 on the SAME reconstructed inputs?
Replays whole lives of up to N of our dragons per game (first 150 rounds) through both binaries and compares
the per-round decision lines ('-> X'). Also reports, for changed decisions, how many had a BOX/HOME line.
    python3 notes/forensics/devil/changerate.py BIN_A BIN_B [games...] [--per 6]
"""
import sys, os, re, random, collections
from common import games, sim, GDIR, ROOT
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
import botview as BV

args = [a for a in sys.argv[1:] if not a.startswith('--')]
per = 6
if '--per' in sys.argv: per = int(sys.argv[sys.argv.index('--per') + 1]); args = [a for a in args if a != str(per)]
A, B = args[0], args[1]
gids = [int(x) for x in args[2:]] or [g['game'] for g in games()]
G = {g['game']: g for g in games()}
random.seed(1)


def decisions(binary, did, turns):
    outs, dbg = BV.run_bot(binary, did, turns)
    d = {}
    for blk in re.split(r'\n(?=R\d+ id=)', dbg):
        mm = re.match(r'R(\d+) ', blk)
        if not mm: continue
        ar = re.findall(r'-> (.*)', blk)
        d[int(mm.group(1))] = (ar[-1].strip() if ar else 'split/ram/other', blk)
    return d


tot = collections.Counter()
for gid in gids:
    g = G[gid]; S = sim(gid); us = g['side']
    born = S['born']; death = {d['id']: d['round'] for d in S['deaths']}
    ours = [j for j in S['team'] if S['team'][j] == us and born.get(j, 0) < 120]
    random.shuffle(ours)
    for did in ours[:per]:
        b = born.get(did, 0); e = min(death.get(did, 150), 150)
        if e - b < 3: continue
        path = os.path.join(GDIR, '%d.replay' % gid)
        try:
            m, turns = BV.capture(path, did, b, e)
        except Exception as ex:
            continue
        if not turns: continue
        da = decisions(A, did, turns); db = decisions(B, did, turns)
        for r in da:
            if r not in db: continue
            tot['n'] += 1
            if da[r][0] != db[r][0]:
                tot['changed'] += 1
                if 'BOX' in da[r][1]: tot['changed_with_box'] += 1
                if 'HOME' in db[r][1]: tot['changed_with_home'] += 1
            if 'BOX' in da[r][1]: tot['box_present'] += 1
    print(gid, dict(tot), flush=True)
print('change rate %.1f%% (%d of %d)' % (100 * tot['changed'] / max(1, tot['n']), tot['changed'], tot['n']))
