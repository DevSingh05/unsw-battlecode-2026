#!/usr/bin/env python3
"""Re-run bot binaries on the exact views of rams WE initiated on MAP (losses by default) and report what each
binary does there.  python3 notes/tools/devdil/rambot.py MAP BIN_BASE BIN_VARIANT [W|L|all] [local_OUT|all]"""
import os, sys, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
from sim2 import simulate
import botview as BV
GS = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
M, B0, B1 = sys.argv[1], sys.argv[2], sys.argv[3]
RES = sys.argv[4] if len(sys.argv) > 4 else 'L'; LOC = sys.argv[5] if len(sys.argv) > 5 else 'local_OUT'
C = collections.Counter()
for g in GS:
    if not g['map'].startswith(M) or (RES != 'all' and ('W' if g['win'] else 'L') != RES): continue
    S = simulate(g['path']); us = g['us']; m = S['map']
    for d in S['deaths']:
        if d['reason'] != 'HitHeadToHead' or 'victim' not in d or d['team'] != us or d['victim_team'] == us: continue
        st = simulate(g['path'], stop=(d['round'], d['id']))
        if 'act' not in st: continue
        me = st['body'][d['id']][0]
        others = sum(1 for j, b in st['body'].items() if j != d['id'] and st['team'][j] == us and m.cheb(b[0], me) <= 3)
        enem = sum(1 for j, b in st['body'].items() if st['team'][j] != us and m.cheb(b[0], me) <= 3)
        if LOC == 'local_OUT' and others >= enem: continue
        r0 = max(S['born'].get(d['id'], 0), d['round'] - 40)
        mm, turns = BV.capture(g['path'], d['id'], r0, d['round'])
        if not turns or turns[-1]['round'] != d['round']: C['skip'] += 1; continue
        o0, _ = BV.run_bot(B0, d['id'], turns); o1, dbg1 = BV.run_bot(B1, d['id'], turns)
        a0 = o0[-1] if o0 else None; a1 = o1[-1] if o1 else None
        real = 'MOVE ' + ''.join(st['act'].get('move', [])) if 'move' in st['act'] else str(st['act'])
        C['n'] += 1; C['base_matches_real'] += (a0 == real); C['variant_same'] += (a1 == a0)
        blk = [b for b in dbg1.split('\nR') if b.startswith('%d ' % d['round']) or b.startswith('R%d ' % d['round'])]
        thr = ''
        if blk and a1 and a1.startswith('MOVE') and len(a1) == 6:
            import re
            mt = re.search(r'cand %s t=\S+ pearls=\S+ area=\d+ depth=\d+ threat=(\d+)' % a1[5], blk[-1])
            thr = mt.group(1) if mt else '?'
            C['variant_threat>0'] += (thr not in ('0', '?', ''))
        print(g['game'], d['round'], 'id', d['id'], 'L%d vs L%d' % (d['len'], d['victim_len']), 'local us %d+1 vs %d' % (others, enem), '| real', real, '| base', a0, '| variant', a1, 'threat', thr)
print(dict(C))
