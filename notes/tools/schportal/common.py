"""Shared helpers for notes/tools/schportal (notes/20)."""
import functools
import pathlib
import pickle
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(ROOT / "notes/tools/midgame"))
sys.path.insert(0, str(ROOT / "notes/tools"))
import replay_decode as R  # noqa: E402
import sim2  # noqa: E402

OPP = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
DV = sim2.DV
_M = {}


def load(name):
    G = pickle.load(open(HERE / f'{name}.pkl', 'rb'))
    src = 'ab_v22' if name.startswith('ab_v22') else 'v19plus'
    if 'm' not in _M:
        _M['m'] = sim2.Map(R.load(str(ROOT / 'replays' / src / f"{G[0]['gid']}.replay"))['map'])
    return G, _M['m']


def NG_of(G):
    return len(G)


def fatal(r):
    return r['died'] is not None and r['died_step'] == r['k']


def hitclass(r):
    h = r['hit']
    if h is None:
        return 'unknown:' + str(r['died'])
    j, seg, tm, L = h
    if j == 'self':
        return 'self'
    own = 'ally' if tm == r['team'] else 'enemy'
    if r['died'] == 'HitHeadToHead':
        return own + '_headon'
    return own + ('_neck' if seg == 1 else '_body')


POOL = {(x, y) for x in range(27, 33) for y in range(34, 39)} - {(27, 34), (32, 34), (27, 38), (32, 38)}


@functools.lru_cache(maxsize=None)
def _tables():
    m = _M['m']
    INF = 1 << 20
    rev = {}
    for x in range(m.w):
        for y in range(m.h):
            for d in 'NESW':
                v = m.step((x, y), d)
                if v is not None:
                    rev.setdefault(v, []).append((x, y))
    D = {t: 0 for t in POOL}
    q = list(POOL)
    for u in q:
        for p in rev.get(u, []):
            if p not in D:
                D[p] = D[u] + 1; q.append(p)
    Y = {(29, 36)}; q = [(29, 36)]
    for u in q:
        for d in 'NESW':
            v = m.step(u, d)
            if v is not None and v == m.wrap(u[0] + DV[d][0], u[1] + DV[d][1]) and v not in Y:
                Y.add(v); q.append(v)
    return D, Y, INF


def schD(t):
    D, Y, INF = _tables()
    return D.get(t, INF)


def yard(t):
    return t in _tables()[1]


def ray_desc(r):
    """What the crosser's own ray through this portal saw last round: kind + where."""
    p = r['myping']
    if p is None:
        return 'no ray'
    hk = p['hitKind'] or 'none'
    if hk in ('kelp', 'none'):
        return 'clean'
    if p['hitId'] == r['id']:
        return 'own body'
    where = 'AT exit' if p['end'] == r['exit'] else 'beyond'
    return f'{hk} {where}'


def short_path(m, x, d, rng):
    y = x
    for _ in range(rng + 1):
        y = m.step(y, d)
        if y is None:
            return True
    return False


def guard_inputs(m, r):
    pr = r['prevpings']
    warn = [p for p in pr if p['origin'] == r['ent'] and p['thru']]
    mask = {p['dir'] for p in warn}
    heads = sum(p['hitKind'] in ('allyHead', 'enemyHead') for p in pr)
    bodies = sum(p['hitKind'] in ('ally', 'enemy') for p in pr)
    return dict(warn=warn, mask=mask, nrays=len(pr), heads=heads, bodies_raw=bodies,
                bodies=0 if len(pr) > len(mask) else bodies)


def guard(m, r, rng=3, mode=2):
    """Replay v22 PORTAL_ECHO_GUARD for crossing r. Returns dict(block, why, ray)."""
    ray = ray_desc(r)
    if len(r['move']) > 1:
        return dict(block=False, why='no probe: sprint crossing', ray=ray)
    if r['age'] == 0:
        return dict(block=False, why='no probe: newborn', ray=ray)
    pa = r['prev_act']
    if pa is None or pa[0] != r['round'] - 1:
        return dict(block=False, why='no probe: no turn last round', ray=ray)
    if pa[1] > 1:
        return dict(block=False, why='no probe: last turn was a sprint', ray=ray)
    gi = guard_inputs(m, r)
    if r['dir'] not in gi['mask']:
        return dict(block=False, why='no probe: no ray through this portal (%s)' % ('split' if pa[2] else 'move/other'), ray=ray)
    if r['sighted']:
        return dict(block=False, why='exit in view (guard skipped)', ray=ray)
    sp = short_path(m, r['exit'], r['dir'], rng)
    blk = gi['heads'] > 0 or (mode >= 2 and gi['bodies'] > 0 and sp)
    if blk:
        return dict(block=True, why='GUARD BLOCKS (crossed anyway)', ray=ray)
    if ray == 'clean':
        why = 'echo clean (arrived after our ray)'
    elif ray == 'own body':
        why = 'ray hit own body'
    elif gi['bodies_raw'] > 0 and gi['bodies'] == 0 and sp:
        why = 'body echo zeroed by extra (king/relay) rays'
    elif gi['bodies_raw'] > 0 and not sp:
        why = 'body echo, long path (shortPath false)'
    else:
        why = 'other'
    return dict(block=False, why=why, ray=ray, sp=sp)
