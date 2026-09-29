"""Shared helpers for the Devil forensics (read-only over replays).
    from common import games, sim, render
"""
import os, sys, json, pickle, functools
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate, Map  # noqa
GDIR = os.path.join(ROOT, 'replays/auto/games')
TOP15 = None
REFMAP = Map(open(os.path.join(ROOT, 'maps/devil.map')).read())


def games(mapname='Devil'):
    L = json.load(open(os.path.join(GDIR, 'ledger.json')))
    out = []
    for g in L:
        if g['map'] != mapname: continue
        p = os.path.join(GDIR, '%d.replay' % g['game'])
        if os.path.exists(p): out.append(dict(g, path=p))
    return out


@functools.lru_cache(maxsize=8)
def sim(gid):
    p = os.path.join(GDIR, '%d.replay' % gid)
    cache = os.path.join(HERE, 'cache', '%d.pkl' % gid)
    if os.path.exists(cache):
        return pickle.load(open(cache, 'rb'))
    S = simulate(p)
    S.pop('map', None)
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    pickle.dump(S, open(cache, 'wb'))
    return S


def state(gid, rnd, did):
    """board right before dragon did acts in round rnd"""
    return simulate(os.path.join(GDIR, '%d.replay' % gid), stop=(rnd, did))


def render(S, us, box=None, mark=None):
    """ASCII: '|' kelp west/east edges, '-' kelp on north edge line. Hot tiles (gap 1) 'h', gap30 ':' ;
    pearls '*'; our heads = id digit via label table; U/u us, E/e enemy.  Returns text."""
    m = S['map']; ref = REFMAP
    occ = {}
    for j, b in S['body'].items():
        for k, t in enumerate(b): occ[t] = (j, k)
    x0, x1, y0, y1 = box if box else (0, m.w - 1, 0, m.h - 1)
    out = ['     ' + ''.join('%-2d' % (x % 100) if x % 2 == 0 else '  ' for x in range(x0, x1 + 1))]
    labels = []
    for y in range(y0, y1 + 1):
        top = '     '; row = '%3d  ' % y
        for x in range(x0, x1 + 1):
            kh = m.edges.get(('H', x, y), (0, -1))[0] == 1
            top += ('--' if kh else '  ')
            kv = m.edges.get(('V', x, y), (0, -1))[0] == 1
            t = (x, y)
            if t in occ:
                j, k = occ[t]
                mine = S['team'][j] == us
                c = ('U' if mine else 'E') if k == 0 else ('u' if mine else 'e')
                if k == 0: labels.append((j, t))
            elif t in S['pearls']: c = '*'
            else:
                gp = ref.tiles.get(t, (0, 0))[1]
                c = 'h' if gp == 1 else (':' if gp == 30 else '.')
                if gp == 0: c = ' '
            if mark and t in mark: c = mark[t]
            row += ('|' if kv else ' ') + c
        out.append(top); out.append(row)
    heads = []
    for j, t in sorted(labels):
        mine = S['team'][j] == us
        heads.append('%s%d L%d@%s' % ('us' if mine else 'EN', j, len(S['body'][j]), t))
    out.append('heads: ' + ', '.join(heads))
    return '\n'.join(out)


def board_at(gid, rnd):
    """board at the start of round rnd (right before the lowest-id living dragon acts)"""
    S = sim(gid)
    snap = dict(S['rounds'])
    prev = snap.get(rnd - 1) or snap[max(k for k in snap if k < rnd)]
    for j in sorted(prev['heads']):
        st = state(gid, rnd, j)
        if 'pearls' in st: return st
    raise ValueError('no state')
