"""Consolidation mechanism metrics per team from local replays.
usage: python3 notes/consolidation/metrics.py REPLAY [REPLAY...]   (run from the project root)
Per team: units r400/450/500, king share of team length r450/r499, longest r499,
feed deaths (own HitSelf deaths r>=300, L<=5, with a longer ally head within 3) and what happened to their pearls."""
import os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame'))
import sim2

def at(rounds, r):
    best = None
    for rr, snap in rounds:
        if rr <= r: best = snap
    return best

for p in sys.argv[1:]:
    S = sim2.simulate(p)
    print(os.path.basename(p), S['result'].get('winner') if isinstance(S['result'], dict) else S['result'], 'last', S['last_round'])
    kings = {rr: {T: snap[T]['king'] for T in 'AB'} for rr, snap in S['rounds']}
    for T in 'AB':
        row = []
        for r in (350, 400, 450, 500):
            s = at(S['rounds'], r); row.append(s[T]['n'] if s else '-')
        sh = []
        for r in (450, 499):
            s = at(S['rounds'], r)
            sh.append('%.2f' % (s[T]['max'] / max(1, s[T]['total'])) if s else '-')
        s499 = at(S['rounds'], 499)
        feeds = [d for d in S['deaths'] if d['team'] == T and d['round'] >= 300 and d['reason'] == 'HitSelf' and d['len'] <= 5
                 and d.get('ally_near') and d['ally_near'][2] <= 3 and d['ally_near'][1] >= d['len'] + 2]
        fid = {d['id'] for d in feeds}
        drop = sum((d['len'] + 1) // 2 for d in feeds)
        eat_team = eat_king = eat_big = eat_enemy = 0
        for e in S['eats']:
            c = e['corpse']
            if not c or c[0] not in fid: continue
            if e['team'] != T: eat_enemy += 1; continue
            eat_team += 1
            k = kings.get(e['round'], {}).get(T)
            if e['id'] == k: eat_king += 1
            if (e['len'] or 0) >= 10: eat_big += 1
        top = s499[T]['lens'][:4] if s499 else []
        print('  %s units r350/400/450/500 %s | king share r450/r499 %s | longest r499 %s top4 %s total %s' % (
            T, row, sh, s499[T]['max'] if s499 else '-', top, s499[T]['total'] if s499 else '-'))
        print('     feed deaths %d (pearls %d): eaten by team %d, by team-longest %d, by L10+ %d, by enemy %d' % (
            len(feeds), drop, eat_team, eat_king, eat_big, eat_enemy))
        late_splits = sum(1 for x in S['splits'] if x['team'] == T and x['round'] >= 330)
        print('     splits r330+: %d' % late_splits)
