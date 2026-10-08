import json,sys
from collections import Counter
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/r2/builder/mech/'
for tag in sys.argv[1:]:
    rows=[r for r in json.load(open(S+tag+'.json')) if 'err' not in r]
    n=len(rows)
    ram=[x for r in rows for x in r['ram8']]
    late=[x for x in ram if x[0]>=440]
    f=lambda k: sum(r.get(k,0) or 0 for r in rows)/n
    c=Counter()
    for r in rows:
        for k,v in (r.get('r2n') or {}).items():
            if k.startswith('eg'): c[k]+=v
    qlate=sum(1 for r in rows if r['our_q'] and r['our_q']['round']>=470)
    print(f"{tag}: n={n} wins={sum(r['win'] for r in rows)} head-on rams suffered by our L>=8: {len(ram)} (r>=440: {len(late)}, L>=20: {sum(1 for x in ram if x[1]>=20)}) | our queen deaths r>=470: {qlate} | tot100={f('tot100'):.1f} tot300={f('tot300'):.1f} max300={f('max300'):.1f} max499={f('max499'):.1f} tot499={f('tot499'):.1f} | eg events {dict(c)} | cpu={max(r['cpu'] or 0 for r in rows)}")
