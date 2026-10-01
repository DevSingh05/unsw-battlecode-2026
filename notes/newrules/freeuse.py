"""Per-team free-step usage in replays. Usage: python3 freeuse.py r1.replay ... (prints one block per game)."""
import sys, os, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'midgame'))
import sim2
F = lambda L: (L + 3) // 4
for p in sys.argv[1:]:
    g = sim2.simulate(p); m = g['map']; res = g['result']
    print(f"== {os.path.basename(p)} {m.name} end r{g['last_round']} {res.get('endReason')} win={res.get('winner')} A={res['A']} B={res['B']}")
    for T in 'AB':
        mv = [x for x in g['moves'] if x['team'] == T and not x.get('suicide')]
        big = [x for x in mv if x['len_before'] >= 5]
        multi = [x for x in big if x['steps'] >= 2]
        paid = [x for x in mv if x['steps'] > F(x['len_before'])]
        ate = sum(x.get('ate', 0) for x in big)
        lb = collections.Counter(min(x['len_before'], 13) for x in mv)
        sp = [s for s in g['splits'] if s['team'] == T] if g['splits'] and 'team' in g['splits'][0] else []
        de = [d for d in g['deaths'] if d['team'] == T]
        dr = collections.Counter(d['reason'] for d in de)
        # kills we made where the killer moved >=2 steps (free-step rams)
        rams = [x for x in mv if x['killed'] and x['steps'] >= 2]
        snaps = {r: s[T] for r, s in g['rounds'] if r in (10, 25, 50, 100, 200, 300, 400) or r == g['last_round']}
        print(f"  {T}: turns={len(mv)} L>=5 turns={len(big)} multistep={len(multi)} ({len(multi)/max(1,len(big)):.0%}) pearls by L>=5={ate} ({ate/max(1,len(big)):.2f}/turn) paid-step turns={len(paid)} 2+step kills={len(rams)}")
        print(f"     len hist(turns) {dict(sorted(lb.items()))}")
        print(f"     deaths {dict(dr)}  splits={len(sp)} {[ (s.get('round'), s.get('L'), s.get('k')) for s in sp[:8]]}")
        print(f"     (n,max,tot) " + ' '.join(f"r{r}:{v['n']},{v['max']},{v['total']}" for r, v in snaps.items()))
