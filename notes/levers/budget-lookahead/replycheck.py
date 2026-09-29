#!/usr/bin/env python3
"""Mechanism check for REPLY_SEARCH on the 111 real big-dragon rams (notes/18, notes/tools/rams/rams.pkl).
For each ram, feeds our dragon's exact server views (R0-40..R0) to two binaries (base, candidate) with
BOTDBG on and compares every decision. Read-only over replays.
    python3 notes/levers/budget-lookahead/replycheck.py BASE_BIN CAND_BIN OUT.pkl
"""
import os, pickle, re, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
import botview as BV

def per_round(dbg):
    res = {}
    for b in re.split(r'\n(?=R\d+ id=)', dbg):
        m = re.match(r'R(\d+) id=\d+ len=(\d+)', b)
        if not m: continue
        rnd = int(m.group(1)); L = int(m.group(2))
        arrow = re.findall(r'-> (.*)', b)
        reps = {mm.group(1): (int(mm.group(2)), int(mm.group(3)), float(mm.group(4)))
                for mm in re.finditer(r'reply (\w) combos=(\d+) worst=(-?\d+) pen=([-\d.]+)', b)}
        cands = {mm.group(1): (int(mm.group(3)), float(mm.group(4))) for mm in
                 re.finditer(r'cand (\w) t=\(\d+,\d+\) pearls=[-\d.]+ area=\d+ depth=(\d+) threat=(\d+) freeT=\d+ score=([-\d.e+]+)', b)}
        res[rnd] = {'L': L, 'arrow': arrow[-1] if arrow else None, 'reply': reps, 'cands': cands}
    return res

def main():
    base, cand, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    import importlib.util, io, contextlib
    spec = importlib.util.spec_from_file_location('ramagg', os.path.join(ROOT, 'notes/tools/rams/agg.py'))
    agg = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(agg)  # classifies every ram (sets r['cat'])
    D = {'rams': agg.rams}
    out = {}
    for r in D['rams']:
        path = os.path.join(ROOT, 'replays', r['src'], '%d.replay' % r['game'])
        if not os.path.exists(path): continue
        m, turns = BV.capture(path, r['id'], r['R0'] - BV.WARM, r['R0'])
        if not turns or turns[-1]['round'] != r['R0']: continue
        ob, db = BV.run_bot(base, r['id'], turns)
        oc, dc = BV.run_bot(cand, r['id'], turns)
        key = (r['game'], r['round'], r['id'])
        out[key] = {'cat': r.get('cat'), 'map': r['map'], 'R0': r['R0'], 'base': per_round(db), 'cand': per_round(dc),
                    'real': [t.get('act') for t in turns[-4:]]}
        pb, pc = out[key]['base'], out[key]['cand']
        diffs = [rn for rn in pc if rn in pb and pb[rn]['arrow'] != pc[rn]['arrow']]
        print(key, r.get('cat'), 'diff rounds', [rn - r['R0'] for rn in diffs][-5:],
              'R0-1', pb.get(r['R0'] - 1, {}).get('arrow'), '->', pc.get(r['R0'] - 1, {}).get('arrow'),
              pc.get(r['R0'] - 1, {}).get('reply'), flush=True)
    pickle.dump(out, open(outp, 'wb'))

if __name__ == '__main__':
    main()
