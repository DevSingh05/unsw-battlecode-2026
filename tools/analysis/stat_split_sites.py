import json,sys,re
from collections import Counter,defaultdict
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/r2/builder/mech/'
for tag in sys.argv[1:]:
    rows=[r for r in json.load(open(S+tag+'.json')) if 'err' not in r]
    n=len(rows)
    site=Counter(); sb=Counter(); sb100=Counter(); sblen=Counter(); exitflag=Counter(); sbexit=Counter()
    for r in rows:
        ev={}
        for t in r.get('r2',[]):
            m=re.match(r'r2 (sp\w+) r(\d+) id(\d+) L(\d+) v(-?\d+)',t)
            if m: ev[(int(m.group(2)),int(m.group(3)))]=(m.group(1),int(m.group(5)))
        for (rd,pid),(s,v) in ev.items():
            site[s]+=1
            if s.startswith('spD'): exitflag[(s,v%100)]+=1
        for rd,k,pid in r['sb_list']:
            s,v=ev.get((rd,pid),('other(map/unknown)',0))
            sb[s]+=1; sblen[s]+=k
            if rd<=100: sb100[s]+=1
            if s.startswith('spD'): sbexit[(s,v%100)]+=1
    f=lambda k: sum(r.get(k,0) or 0 for r in rows)/n
    print(f"== {tag}: n={n} wins={sum(r['win'] for r in rows)} splits/g={f('splits'):.1f} stillborn/g={f('stillborn'):.1f} sb_by_r100/g={f('stillborn100'):.1f} (len {f('stillborn_len100'):.1f}) n50={f('n50'):.1f} n100={f('n100'):.1f} tot100={f('tot100'):.1f} tot200={f('tot200'):.1f} tot300={f('tot300'):.1f} cpu={max(r['cpu'] or 0 for r in rows)}")
    for s in sorted(site, key=lambda s:-sb[s]):
        print(f"   {s:8s} splits/g {site[s]/n:6.1f}  stillborn/g {sb[s]/n:5.1f} ({100*sb[s]/max(1,site[s]):.0f}%)  by r100/g {sb100[s]/n:4.1f}  len/g {sblen[s]/n:5.1f}")
    for s in sb:
        if s not in site: print(f"   {s}: stillborn/g {sb[s]/n:.1f}")
    print('   growth split by tailHasExit flag (site,flag): splits', dict(exitflag), 'stillborn', dict(sbexit))
