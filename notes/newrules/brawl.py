"""Brawl/queen detail per replay: queen fate, head-on kills by mover length/steps. Usage: python3 brawl.py r.replay ..."""
import sys, os, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'midgame'))
import sim2
for p in sys.argv[1:]:
    g = sim2.simulate(p); res = g['result']
    print(f"== {os.path.basename(p)} end r{g['last_round']} {res.get('endReason')} win={res.get('winner')}")
    for q in (0, 1):
        d = [x for x in g['deaths'] if x['id'] == q]
        T = g['team'][q]
        print(f"  queen {q} team {T}: " + (f"died r{d[0]['round']} {d[0]['reason']} L{d[0].get('len')}" if d else f"ALIVE len {len(g['body'][q])}"))
    for T in 'AB':
        mv = [x for x in g['moves'] if x['team'] == T and x['killed']]
        enemy_kills = [(x['len_before'], x['steps'], x['died'] is not None) for x in mv for k in x['killed'] if k[1] != T]
        c = collections.Counter((min(L, 9), s, died) for L, s, died in enemy_kills)
        print(f"  {T} kills by mover (L,steps,mover died): {dict(sorted(c.items()))}")
