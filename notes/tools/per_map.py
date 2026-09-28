"""Per-map outcome table + phase-2 start (first round team max length >= 10) per team."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_cache import load_all
from collections import defaultdict, Counter
import statistics as st
gs=load_all()
bym=defaultdict(list)
for g in gs: bym[g['map'].name].append(g)
print('map | games | elim | end rnd (median) | winner longest (roundLimit) | winner units@end | loser longest | winner peak units')
for mp,G in sorted(bym.items()):
    el=[g for g in G if g['result']['endReason']=='teamEliminated']
    rl=[g for g in G if g['result']['endReason']=='roundLimit']
    wl=[g['result'][g['result']['winner']]['longest'] for g in rl if g['result']['winner']]
    ll=[g['result']['B' if g['result']['winner']=='A' else 'A']['longest'] for g in rl if g['result']['winner']]
    wu=[g['result'][g['result']['winner']]['dragonCount'] for g in G if g['result']['winner']]
    pk=[max(snap[g['result']['winner']]['n'] for r,snap in g['rounds']) for g in G if g['result']['winner']]
    ends=[g['last_round']+1 for g in G]
    print(f"{mp} | {len(G)} | {len(el)} | {st.median(ends)} ({min(ends)}-{max(ends)}) | {sorted(wl)} | {sorted(wu)} | {sorted(ll)} | {sorted(pk)}")
print('\n# phase-2 start: first round (>=30) where team longest >= 10, per team; also >=20')
ph=defaultdict(list)
for g in gs:
    for s in 'AB':
        T=g['names'][s]
        r10=next((r for r,snap in g['rounds'] if r>=30 and snap[s]['max']>=10),None)
        r20=next((r for r,snap in g['rounds'] if r>=30 and snap[s]['max']>=20),None)
        ph[T].append((g['map'].name[:10],r10,r20))
for T,v in ph.items(): print(T, sorted(v,key=lambda x:(x[1] is None, x[1] or 0)))
