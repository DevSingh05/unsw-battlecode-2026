"""Why don't our small dragons dive into pockets? Re-run the v28 binary on reconstructed views of our L2-3 dragons
standing on/next to a pocket entry tile (with a pearl in the pocket) that did NOT step in, and collect the bot's
POCKET debug reason + the candidate scores.  python3 whynot.py BIN [N=40] [grp=us-L-strong|us-W]
"""
import os, sys, re, pickle, random, collections
H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(H, '../midgame')); sys.path.insert(0, H); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
import sim2, collect, botview as BV
binp = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 40; want = sys.argv[3] if len(sys.argv) > 3 else 'L'
R = pickle.load(open(os.path.join(H, 'games.pkl'), 'rb'))
paths = {g['gid']: g['path'] for g in collect.games()}
cases = []
for r in R:
    if r['grp'] != 'us': continue
    strong = r['oppelo'] >= 1940
    if want == 'L' and (r['win'] or not strong): continue
    if want == 'W' and not r['win']: continue
    S = sim2.simulate(paths[r['gid']]); m = S['map']; PK = collect.pockets(m)
    entry = {t: u for u in PK for d in 'NESW' for t in [m.step(u, d)] if t is not None and t not in PK}  # mouth tile -> first pocket tile
    rounds = dict(S['rounds'])
    for x in S['moves']:
        if x['team'] != r['T'] or not (40 <= x['round'] <= 220) or x.get('suicide') or x['len_before'] > 3: continue
        if x['head'] not in entry or x.get('head_after') in PK: continue
        cases.append((r['gid'], x['id'], x['round'], x['head'], entry[x['head']]))
random.seed(1); random.shuffle(cases)
print('candidate non-entries', len(cases))
reasons = collections.Counter(); rows = []
for gid, i, rnd, head, first in cases[:N]:
    m, turns = BV.capture(paths[gid], i, rnd - 30, rnd)
    if not turns or turns[-1]['round'] != rnd: continue
    outs, dbg = BV.run_bot(binp, i, turns)
    pr = BV.parse_last(dbg, rnd)
    if not pr: continue
    why = re.findall(r'POCKET (\w+)', pr['raw'])
    dirs = {v['t']: k for k, v in pr['cands'].items()}
    into = dirs.get(first)
    c = pr['cands'].get(into) if into else None
    key = why[-1] if why else ('no-cand(occupied)' if into is None else 'not-evaluated')
    reasons[key] += 1
    rows.append((gid, i, rnd, head, first, why, into, c and round(c['score'], 1), {k: round(v['score'], 1) for k, v in pr['cands'].items()}, outs[-1] if outs else None, turns[-1].get('act')))
    print(gid, i, rnd, head, '->', first, 'why', why, 'into', into, c and round(c['score'], 1), {k: round(v['score'], 1) for k, v in pr['cands'].items()}, 'bot', outs[-1] if outs else None, flush=True)
print(reasons.most_common())
pickle.dump(rows, open(os.path.join(H, 'whynot_%s.pkl' % want), 'wb'))
