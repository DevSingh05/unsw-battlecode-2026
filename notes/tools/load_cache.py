"""Load cached simulations (built by analyze_top.py) with team names attached."""
import os, glob, json, pickle
RD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../replays')
def load_all():
    idx = {m['id']: m for m in json.load(open(os.path.join(RD, 'index.json')))}
    gs = []
    for f in sorted(glob.glob(os.path.join(RD, '*.replay.sim.pkl'))):
        g = pickle.load(open(f, 'rb')); mid = int(os.path.basename(f).split('.')[0])
        g['id'] = mid; g['names'] = {'A': idx[mid]['a']['name'], 'B': idx[mid]['b']['name']}; gs.append(g)
    return gs
