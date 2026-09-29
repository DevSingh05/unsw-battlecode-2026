#!/usr/bin/env python3
"""Sample crown drops in the MAIN area with a free neighbour (per replay) and re-run the debug bot to see why it split.
   python3 notes/forensics/portals/why_main.py BIN [N]"""
import json, os, sys, collections, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
import cap
from crownwhere import cls  # noqa
B = sys.argv[1]; NMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 25
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
games = sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994 and not x['win'])
C = collections.Counter(); done = 0
for gid in games:
    if done >= NMAX: break
    g = led[gid]; T = g['side']
    S = simulate(os.path.join(GD, '%d.replay' % gid))
    kr = collections.defaultdict(set)
    for s in S['sonars']:
        if s['team'] != T: continue
        x = s['value'] & ((1 << 43) - 1); L = (x >> 12) & 255; hop = (x >> 30) & 3; kid = (x >> 20) & 1023
        if hop == 0 and kid == (s['id'] & 1023) and L >= 2: kr[s['id']].add(s['round'])
    heads = collections.defaultdict(dict)
    for a in S['moves']:
        if a.get('head_after'): heads[a['id']][a['round']] = a['head_after']
    picked = 0
    for s in S['splits']:
        if picked >= 2 or done >= NMAX: break
        if s['team'] != T or s['L'] < 6 or s['exits'] == 0 or not any(s['round'] - 3 <= r <= s['round'] for r in kr.get(s['parent'], ())): continue
        hs = heads[s['parent']]; prev = [r for r in hs if r < s['round']]
        if not prev or cls(hs[max(prev)]) != 'main': continue
        r0 = max(S['born'][s['parent']], s['round'] - 120)
        m, turns = cap.capture(gid, s['parent'], r0, s['round'])
        if not turns or turns[-1]['round'] != s['round']: continue
        blocks, dbg = cap.run_full(B, s['parent'], turns)
        bl = [b for b in re.split(r'\n(?=R\d+ id=)', dbg) if b.startswith('R%d ' % s['round'])]
        bl = bl[-1] if bl else ''
        arrow = ' / '.join(re.findall(r'-> (.*)', bl))
        cands = ' '.join('%s:a%s/d%s/%s' % (c[0], c[1], c[2], c[3]) for c in re.findall(r'cand (\w) t=\S+ pearls=\S+ area=(\d+) depth=(\d+) threat=\d+ freeT=\d+ score=([-\d.e+]+)', bl))
        echo = ' '.join(l.strip() for l in bl.split('\n') if 'ECHODIR' in l)
        bot = next((l for l in blocks[-1] if l.startswith(('MOVE', 'SPLIT'))), '?')
        print('%d r%d id%d L%d k=%d exits=%d head=%s | bot %s (%s) | %s | %s' % (gid, s['round'], s['parent'], s['L'], s['k'], s['exits'], hs[max(prev)], bot, arrow, cands, echo[:160]), flush=True)
        C[arrow] += 1; picked += 1; done += 1
print(C)
