#!/usr/bin/env python3
"""Why don't our big non-king dragons feed? Re-runs the FEEDDBG build of v29 (v29dbg_patch.py) on our
top-N dragons alive at round R0 (default 440) of every Schooltime game, from birth to the end, and
classifies each of their turns in r>=R0:
  feeding          : shouldFeed() true
  stubborn         : kingSelf and a fresh (<=8 rounds) king >= myLen+2 was heard (KING_V2 needs TWO)
  deaf_self        : believes it is the king (iAmKing) with no longer fresh king heard
  heard_small_only : heard a king, but not one >= myLen+2
  other
    python3 notes/forensics/schooltime/kingstate.py BIN [R0] [TOPN] [A|B]"""
import os, sys, re, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from botrun import run
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
BIN = sys.argv[1]; R0 = int(sys.argv[2]) if len(sys.argv) > 2 else 440
TOPN = int(sys.argv[3]) if len(sys.argv) > 3 else 4; LAY = sys.argv[4] if len(sys.argv) > 4 else 'A'
def lay(D): return 'A' if D['poolspawns'] > 20 else 'B'
FD = re.compile(r'R(\d+) id=\d+ len=(\d+).*?\n(?:.*\n)*?\s+FEEDDBG feeding=(\d) kingId=(-?\d+) kingLen=(\d+) kingTile=\S+ age=(-?\d+) target=\S+ units=\d+ kingSelf=(\d) iAmKing=(\d) myLen=(\d+)')
out = collections.defaultdict(collections.Counter)
for gid, D in sorted(G.items()):
    if lay(D) != LAY or R0 not in D['tl']: continue
    us = D['us']; last = max(D['tl'])
    hs = D['tl'][R0]['heads']
    top = sorted(((L, j) for j, (h, L, T) in hs.items() if T == us), reverse=True)[:TOPN]
    key = 'W' if D['win'] else 'L'
    for rank, (L, j) in enumerate(top):
        b = D['born'].get(j, 0)
        dead = [d['round'] for d in D['deaths'] if d['id'] == j]
        r1 = min(dead[0] if dead else last, last)
        try:
            turns, outs, dbg = run(BIN, gid, j, b, r1)
        except Exception as ex:
            print('fail', gid, j, ex); continue
        cnt = collections.Counter()
        for blk in re.split(r'\n(?=R\d+ id=)', dbg):
            m = re.match(r'R(\d+) ', blk)
            f = re.search(r'FEEDDBG feeding=(\d) kingId=(-?\d+) kingLen=(\d+) kingTile=\S+ age=(-?\d+) target=\S+ units=\d+ kingSelf=(\d) iAmKing=(\d) myLen=(\d+)', blk)
            if not m or not f or int(m.group(1)) < R0: continue
            feeding, kid, klen, age, kself, iak, mylen = map(int, f.groups())
            fresh = kid >= 0 and age <= 8
            if feeding: c = 'feeding'
            elif kself and fresh and klen >= mylen + 2: c = 'stubborn'
            elif iak and not (fresh and klen >= mylen + 2): c = 'deaf_self'
            elif fresh and klen < mylen + 2: c = 'heard_small_only'
            else: c = 'other'
            cnt[c] += 1
        tot = sum(cnt.values())
        out[(key, rank)].update(cnt)
        print(gid, key, 'rank%d id%d L%d@r%d born%d' % (rank + 1, j, L, R0, b), dict(cnt), flush=True)
print()
for k in sorted(out):
    c = out[k]; t = sum(c.values())
    print(k, 'turns %d' % t, ' '.join('%s %.0f%%' % (x, 100 * c[x] / t) for x in ('feeding', 'stubborn', 'deaf_self', 'heard_small_only', 'other')))
