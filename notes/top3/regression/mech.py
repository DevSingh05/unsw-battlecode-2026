"""Re-run every one of OUR dragons' reconstructed per-turn inputs (notes/autarky_calc/jam/lifeview.py) through
several binaries and record decisions. usage (project root):
  python3 notes/top3/regression/mech.py GAME SIDE name=BIN ...   -> notes/top3/regression/mech/<GAME>_<name>.pkl"""
import os, sys, pickle, time
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/autarky_calc/jam'))
import lifeview as LV
g = int(sys.argv[1]); side = sys.argv[2]
LV.GAMES[g] = side
LV.path = lambda gg: os.path.join(ROOT, 'replays/regcheck/%d.replay' % gg)
bins = dict(a.split('=', 1) for a in sys.argv[3:])
os.makedirs(os.path.join(H, 'mech'), exist_ok=True)
t0 = time.time(); m, lives = LV.capture_all(g)
for name, b in bins.items():
    fp = os.path.join(H, 'mech', '%d_%s.pkl' % (g, name))
    if os.path.exists(fp): continue
    res = {}; agree = tot = 0
    for i, turns in sorted(lives.items()):
        res[i] = LV.run_life(b, g, i, turns, m.w, m.h)
        for x in res[i]:
            tot += 1; agree += x['real'] == x['bot']
    pickle.dump(res, open(fp, 'wb'))
    print(g, name, 'lives', len(res), 'turns', tot, 'agree-real %.4f' % (agree / max(1, tot)), '%.0fs' % (time.time() - t0), flush=True)
