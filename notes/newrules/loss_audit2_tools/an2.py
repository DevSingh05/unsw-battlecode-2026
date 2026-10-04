import json,collections,sys
R=json.load(open(sys.argv[1]))
L=[r for r in R if r['s']==0]
W=[r for r in R if r['s']==1]
top=lambda c:c.split(':')[0]
Q=[r for r in L if top(r['cause']) in('r500_queen_dead','r500_both_dead_longest')]
print("queen-death r500 losses by map x mode x phase(<=100/>100)")
c=collections.Counter((r['map'],r['qd']['mode'].replace('+trapsplit','+TS'),'E' if r['qd']['round']<=100 else 'L') for r in Q)
bym=collections.defaultdict(list)
for (m,mo,ph),n in c.items(): bym[m].append(f"{mo}/{ph}:{n}")
for m in sorted(bym): print(f"  {m:18s}",' '.join(sorted(bym[m])))
print("\nH2H_by_enemy details (killer_len, steps?, qlen, round):")
for r in Q:
  q=r['qd']
  if q['mode']=='H2H_by_enemy': print(f"  {r['map'][:10]:10s} r{q['round']:3d} qL{q['len']} kL{q['killer_len']} en{q['enemy_near']} al{q['ally_near']} top10={r['top10']} opp={r['opp'][:14]}")
print("\ntrapsplit details:")
for r in Q:
  q=r['qd']
  if 'trapsplit' in q['mode']: print(f"  {r['map'][:10]:10s} r{q['round']:3d} qL{q['len']} {q['mode']} splits{q['splits']} nbrs={q['nbrs']}")
