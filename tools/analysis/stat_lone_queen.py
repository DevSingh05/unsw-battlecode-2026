import json,sys
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/r2/builder/mech/'
for tag in sys.argv[1:]:
    rows=[r for r in json.load(open(S+tag+'.json')) if 'err' not in r]
    n=len(rows); w=sum(r['win'] for r in rows)
    oqd=sum(1 for r in rows if r['our_q']); tqd=sum(1 for r in rows if r['their_q'])
    tq_headon=sum(1 for r in rows if r['their_q'] and r['their_q']['reason']=='HitHeadToHead')
    late=sum(1 for r in rows if r['their_q'] and r['their_q']['reason']=='HitHeadToHead' and r['our_q'] and r['their_q']['round']>r['our_q']['round'])
    r500=[r for r in rows if '500' in (r['res'] or '')]
    lostq=sum(1 for r in r500 if (not r['win']) and r['our_q'] and not r['their_q'])
    print(f"{tag}: n={n} wins={w} ourQdead={oqd} theirQdead={tqd} theirQ_headon={tq_headon} theirQ_headon_after_ours_died={late} r500games={len(r500)} r500loss_ourQdead_theirsAlive={lostq} cpu={max(r['cpu'] or 0 for r in rows)}")
