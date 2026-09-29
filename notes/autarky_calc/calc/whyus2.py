"""All our non-entries: our head on a mouth tile (or adjacent to it with the mouth free), pocket empty & >=2 pearls, next move not into the pocket.
Re-run v29 and classify: POCKET enemy veto / POCKET YES but outscored / pocket cand absent / bot disagrees."""
import sys, os, collections, pickle
from common import *
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
import botview as BV
BIN = sys.argv[1]
E = pickle.load(open(os.path.join(H, 'episodes.pkl'), 'rb'))
res = collections.Counter(); rows = []
for gm in GAMES:
    if gm['us'] is None: continue
    g = sim(gm['gid']); R = dict(g['rounds']); c = gm['calc']
    for mv in g['moves']:
        if mv['team'] == c: continue
        S = R.get(mv['round'] - 1)
        if not S: continue
        h = mv['head']
        for p in range(4):
            if h != MOUTH[p]: continue
            if any(any(pocket_of(s) == p for s in bd) for bd in S['bodies'].values()): continue
            pe = sum(1 for t in S['pearls'] if pocket_of(t) == p)
            if pe < 2: continue
            if mv.get('head_after') and pocket_of(mv['head_after']) == p: res['entered'] += 1; continue
            en = min((mdist(hh, MOUTH[p]) for (hh, L, TT) in S['heads'].values() if TT == c), default=99)
            did = mv['id']; R0 = mv['round']
            r_from = max(g['born'].get(did, 0), R0 - 40)
            try:
                m, turns = BV.capture(gm['path'], did, r_from, R0)
                outs, dbg = BV.run_bot(BIN, did, turns)
                pr = BV.parse_last(dbg, R0)
            except Exception as ex:
                res['err'] += 1; continue
            raw = pr['raw'] if pr else ''
            pk = [l for l in raw.splitlines() if 'POCKET' in l]
            cands = pr['cands'] if pr else {}
            intoP = [k for k, v in cands.items() if pocket_of(v['t']) == p]
            best = max(cands.items(), key=lambda kv: kv[1]['score'])[0] if cands else None
            if not intoP: why = 'no pocket candidate (blocked/backwards)'
            elif any('enemy' in l for l in pk): why = 'POCKET enemy veto'
            elif any('YES' in l for l in pk): why = 'POCKET YES but another move scored higher'
            elif pk: why = 'POCKET other: ' + pk[0].split('POCKET')[1][:30]
            else: why = 'pocket cand scored lower (no POCKET line)'
            res[why] += 1
            rows.append((gm['gid'], R0, did, why, en, {k: round(v['score'], 1) for k, v in cands.items()}, intoP, outs[-1] if outs else None, mv['act']))
for k, v in res.most_common(): print('%4d  %s' % (v, k))
for r in rows: print(r)
pickle.dump(rows, open(os.path.join(H, 'whyus2.pkl'), 'wb'))
