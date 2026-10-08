import json,sys
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/r2/builder/mech/'
for tag in sys.argv[1:]:
    rows=[r for r in json.load(open(S+tag+'.json')) if 'err' not in r]
    n=len(rows); w=sum(r['win'] for r in rows)
    qd=[r['our_q'] for r in rows if r['our_q']]
    def ally(q): return any(isinstance(v,(list,tuple)) and v[0]=='ally' for v in (q.get('nbrs') or {}).values())
    shed=[q for q in qd if q['len']<=3]
    by={}
    for q in qd: by[q['reason']]=by.get(q['reason'],0)+1
    f=lambda k: sum(r.get(k,0) or 0 for r in rows)/n
    print(f"{tag}: n={n} wins={w} ourQdead={len(qd)} (L<=3: {len(shed)}, with ally nbr: {sum(ally(q) for q in qd)}, L<=3&ally: {sum(ally(q) for q in shed)}) by reason {by} | qAlive@end={n-len(qd)} | tot100={f('tot100'):.1f} tot300={f('tot300'):.1f} n50={f('n50'):.1f} stillborn/g={f('stillborn'):.1f} sb100={f('stillborn100'):.1f} cpu={max(r['cpu'] or 0 for r in rows)}")
