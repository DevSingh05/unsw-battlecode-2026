"""Mechanism check: re-run every one of our dragons' reconstructed lives (jam/lifeview.py inputs) through
several binaries; save decisions per binary.   python3 mech.py GAME name=BIN [name=BIN ...]"""
import os, sys, pickle, time
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '../jam'))
import lifeview as LV
g = int(sys.argv[1]); bins = dict(a.split('=', 1) for a in sys.argv[2:])
t0 = time.time(); m, lives = LV.capture_all(g); print('captured', len(lives), '%.0fs' % (time.time() - t0), flush=True)
for name, b in bins.items():
    res = {}; agree = tot = 0
    for i, turns in sorted(lives.items()):
        res[i] = LV.run_life(b, g, i, turns, m.w, m.h)
        for x in res[i]:
            tot += 1; agree += x['real'] == x['bot']
    pickle.dump(res, open(os.path.join(H, 'mech_%d_%s.pkl' % (g, name)), 'wb'))
    print(g, name, 'turns', tot, 'agree %.3f' % (agree / tot), '%.0fs' % (time.time() - t0), flush=True)
