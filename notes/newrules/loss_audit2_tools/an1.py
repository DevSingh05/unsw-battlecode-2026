import json,collections,sys
R=json.load(open(sys.argv[1]))
L=[r for r in R if r['s']==0]
def top(c): return c.split(':')[0]
for ver in ('v55','v61','all'):
  S=[r for r in L if ver=='all' or r['ver']==ver]
  for t in (True,False):
    s=[r for r in S if r['top10']==t]
    c=collections.Counter(top(r['cause']) for r in s)
    print(ver,'top10' if t else 'rest ',len(s),{k:f"{v} ({100*v/len(s):.0f}%)" for k,v in c.most_common()})
print()
# queen death modes in r500_queen_dead and both dead
for cat in ('r500_queen_dead','r500_both_dead_longest','eliminated'):
  s=[r for r in L if top(r['cause'])==cat]
  c=collections.Counter(r['qd'].get('mode','alive') for r in s)
  print(cat,len(s),c.most_common())
  rds=sorted(r['qd'].get('round',999) for r in s)
  import statistics
  print('  our queen death round quartiles',[rds[int(len(rds)*q)] for q in (0.1,.25,.5,.75,.9)] if rds else '')
  print('  died<=30:',sum(1 for x in rds if x<=30),' <=100:',sum(1 for x in rds if x<=100),' >100:',sum(1 for x in rds if 100<x<999))
print()
maps=sorted({r['map'] for r in R})
print(f"{'map':18s} n  elim qdead(early<=100) both_dead q_shorter")
for m in maps:
  s=[r for r in L if r['map']==m]
  c=collections.Counter(top(r['cause']) for r in s)
  e=sum(1 for r in s if top(r['cause'])=='r500_queen_dead' and r['qd'].get('round',999)<=100)
  print(f"{m:18s} {len(s):2d} {c['eliminated']:4d} {c['r500_queen_dead']:4d}({e}) {c['r500_both_dead_longest']:6d} {c['r500_queen_shorter']:6d}   top10 {sum(r['top10'] for r in s)}")
