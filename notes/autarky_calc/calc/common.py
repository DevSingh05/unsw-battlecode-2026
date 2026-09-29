import os, sys, pickle
H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/autarky')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2, collect
sys.path.insert(0, H)
import simfull
CACHE = os.path.join(H, 'cache')
os.makedirs(CACHE, exist_ok=True)

# (gid, path, calc side, opponent name)
OURS = [(625768, 'B'), (617872, 'A'), (612737, 'A'), (608221, 'A')]  # our side
GAMES = []
for g, us in OURS:
    GAMES.append(dict(gid=g, path=os.path.join(ROOT, 'replays/auto/games/%d.replay' % g), calc='B' if us == 'A' else 'A', opp='US', us=us))
OTHER = [('notes/replays/autarky', 608782, 'A', 'cheji bt'), ('notes/replays/autarky', 608792, 'B', 'cheji bt'),
         ('notes/replays/autarky', 608822, 'B', '天天开心'), ('notes/replays/autarky', 607083, 'B', 'SSS'),
         ('notes/replays/autarky', 607063, 'B', 'SSS'), ('notes/replays/midgame', 500988, 'A', 'dev test 1'),
         ('notes/replays/midgame', 500689, 'B', 'cheji bt'), ('notes/replays/midgame', 499807, 'A', 'Sabotage-d'),
         ('notes/replays/midgame', 499787, 'A', 'SSS')]
for d, g, c, o in OTHER:
    GAMES.append(dict(gid=g, path=os.path.join(ROOT, d, '%d.replay' % g), calc=c, opp=o, us=None))


def sim(gid):
    p = os.path.join(CACHE, '%d.pkl' % gid)
    if os.path.exists(p):
        return pickle.load(open(p, 'rb'))
    gm = [x for x in GAMES if x['gid'] == gid][0]
    g = simfull.simulate(gm['path'])
    pickle.dump(g, open(p, 'wb'))
    return g


MAPF = None
def realmap():
    global MAPF
    if MAPF is None:
        MAPF = sim2.Map(open(os.path.join(ROOT, 'maps/autarky.map')).read())
    return MAPF

PK = None
def pockets():
    global PK
    if PK is None:
        PK = collect.pockets(realmap())
    return PK
MOUTH = [(18, 3), (35, 3), (18, 14), (35, 14)]
def pocket_of(t):
    x, y = t
    if t not in pockets(): return None
    return (0 if x < 27 else 1) + (0 if y < 9 else 2)
def mdist(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])
