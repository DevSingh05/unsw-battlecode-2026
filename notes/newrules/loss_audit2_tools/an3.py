import json,collections,sys,statistics as st
R=json.load(open(sys.argv[1]))
L=[r for r in R if r['s']==0]; W=[r for r in R if r['s']==1]
top=lambda c:c.split(':')[0]
print("r500 queen-dead losses: final total us/them, longest us/them, their queen len")
s=[r for r in L if top(r['cause'])=='r500_queen_dead']
ahead=sum(1 for r in s if r['us_final']['total']>r['th_final']['total'])
lng=sum(1 for r in s if r['us_final']['longest']>r['th_final']['longest'])
print(f" n={len(s)} our total ahead in {ahead}, our longest ahead in {lng}; median their queen len {st.median(r['tqd']['len'] for r in s)}")
print(" by map: ahead-on-total / n  (their-queen-len list)")
bym=collections.defaultdict(list)
for r in s: bym[r['map']].append(r)
for m,l in sorted(bym.items()): print(f"   {m:18s} {sum(1 for r in l if r['us_final']['total']>r['th_final']['total'])}/{len(l)} tq {[r['tqd']['len'] for r in l]}")
print("\nboth dead, longest lost: our longest vs theirs")
s=[r for r in L if top(r['cause'])=='r500_both_dead_longest']
for r in s: pass
print(' ', ' '.join(f"{r['map'][:5]}:{r['us_final']['longest']}v{r['th_final']['longest']}(t{r['us_final']['total']}v{r['th_final']['total']})" for r in s))
print(f" our total ahead {sum(1 for r in s if r['us_final']['total']>r['th_final']['total'])}/{len(s)}; their queen died r median {st.median(r['tqd']['round'] for r in s)} ours {st.median(r['qd']['round'] for r in s)}")
print("\nqueen shorter (both alive):")
s=[r for r in L if top(r['cause'])=='r500_queen_shorter']
print(' ', ' '.join(f"{r['map'][:5]}:q{r['qd']['len']}v{r['tqd']['len']}(max{r['qmax']})" for r in s))
print("\nWINS sample: queen fate")
c=collections.Counter(('alive' if r['qd'].get('alive') else ('E' if r['qd']['round']<=100 else 'L')+':'+r['qd']['mode'].replace('+trapsplit','+TS')) for r in W)
print(' ',c.most_common())
c=collections.Counter(('tq_alive' if r['tqd'].get('alive') else 'tq_dead') for r in W); print(' ',c, 'ends',collections.Counter(r['end'] for r in W))
print("\nLOSSES overall our queen alive at end:",sum(1 for r in L if r['qd'].get('alive')),"/",len(L))
print("their queen alive in losses:",sum(1 for r in L if r['tqd'].get('alive')))
print("\nEliminated: gap round (their total>=1.5x+10), elim round, by map")
s=[r for r in L if top(r['cause'])=='eliminated']
bym=collections.defaultdict(list)
for r in s: bym[r['map']].append(r)
for m,l in sorted(bym.items()):
  print(f"   {m:18s} n{len(l)} gap {sorted(r['gap'] or 999 for r in l)} end {sorted(r['last'] for r in l)}")
