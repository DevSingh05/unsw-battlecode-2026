from common import *
import collections, statistics as st
for grp in ('us', 'oth'):
    X = collections.defaultdict(list); sprint = collections.Counter(); bodyk = collections.Counter()
    for gm in GAMES:
        if (gm['us'] is not None) != (grp == 'us'): continue
        g = sim(gm['gid']); c = gm['calc']
        mv = {(m['round'], m['id']): m for m in g['moves']}
        for d in g['deaths']:
            if d['reason'] == 'HitHeadToHead' and d.get('killer') is not None and d['killer_team'] != d['team']:
                ini = 'calc' if d['killer_team'] == c else 'opp'
                X[ini].append((d['killer_len'], d['len']))
                m = mv.get((d['round'], d['killer']))
                if m: sprint[(ini, m['steps'])] += 1
            if d['reason'] == 'HitOtherBody' and d.get('hit') and d['hit']['team'] != d['team']:
                # victim ran into enemy body: credit body owner
                bodyk['calc body' if d['hit']['team'] == c else 'opp body'] += 1
    for k, v in X.items():
        print(grp, k, 'head-ons initiated', len(v), 'initiator L mean %.2f victim L mean %.2f' % (st.mean(a for a, b in v), st.mean(b for a, b in v)), 'victim longer %d, shorter %d' % (sum(b > a for a, b in v), sum(b < a for a, b in v)))
    print(grp, 'steps', dict(sprint), 'body kills', dict(bodyk))
