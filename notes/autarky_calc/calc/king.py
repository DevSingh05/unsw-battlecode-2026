from common import *
import collections
for gid in (625768, 617872, 608782, 500988, 607063, 500689):
    gm = [x for x in GAMES if x['gid'] == gid][0]; g = sim(gid); c = gm['calc']; R = dict(g['rounds'])
    last = g['last_round']
    fin = R[last][c]
    k = fin['king'] if fin['n'] else None
    # the dragon that was longest at end, else at last available
    traj = []
    for r in range(250, last + 1, 25):
        S = R.get(r)
        if S and S[c]['n']:
            kk = S[c]['king']; traj.append('r%d:id%d L%d u%d' % (r, kk, S[c]['max'], S[c]['n']))
    print(gid, gm['opp'][:10], ' | '.join(traj))
    kid = R[last][c]['king'] if R[last][c]['n'] else None
    if kid is None: continue
    # lineage of king: ancestors
    anc = [kid]; p = kid
    while p in g['parent_of']: p = g['parent_of'][p]; anc.append(p)
    print('   final king', kid, 'born r%d' % g['born'][kid], 'ancestors', anc[:6])
    ke = [e for e in g['eats'] if e['id'] == kid]
    src = collections.Counter()
    for e in ke:
        if e['corpse']:
            src['corpse_own' if e['corpse'][1] == c else 'corpse_enemy'] += 1
        elif pocket_of(e['tile']) is not None: src['pocket'] += 1
        else: src['open'] += 1
    print('   king eats by source', dict(src), 'first eat r%d' % (ke[0]['round'] if ke else -1))
    # feeder deaths near king after r350
    fd = collections.Counter(); sonar = sum(1 for s in g['sonars'] if s['team'] == c)
    for d in g['deaths']:
        if d['team'] == c and d['round'] >= 300 and d['reason'] in ('NoValidAction', 'HitWall', 'HitSelf'):
            S = R.get(d['round'] - 1)
            if S and kid in S['heads']:
                dk = mdist(d['head'], S['heads'][kid][0])
                fd[('near king<=3' if dk <= 3 else 'far', d['reason'][:6], 'inpocket' if pocket_of(d['head']) is not None else 'open')] += 1
    print('   calc self-deaths r>=300:', dict(fd.most_common()), 'calc sonar pings total', sonar)
    # when does king seed start: first round calc max>=8
    r8 = next((r for r, S in g['rounds'] if S[c]['max'] >= 8 and r > 30), None)
    print('   first round calc longest>=8 (after r30):', r8)
