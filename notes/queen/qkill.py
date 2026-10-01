"""For queen head-to-head deaths: killer start distance, killer length, reach; spawn openness. usage: qkill.py <dir>"""
import sys, os, glob, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'midgame'))
import sim2
def reach(L): return -(-L // 4) + max(0, L - 2)  # free ceil(L/4) + paid steps down to len 2
def region(m, p, R=4):  # tiles within R steps (kelp only), local openness
    seen = {p}; fr = [p]
    for _ in range(R):
        nf = []
        for q in fr:
            for d in 'NESW':
                t = m.step(q, d)
                if t and t not in seen: seen.add(t); nf.append(t)
        fr = nf
    return len(seen)
done = set()
for p in sorted(glob.glob(os.path.join(sys.argv[1], 'v3*_s?.replay'))):
    tag = os.path.basename(p)[:-7]; g = sim2.simulate(p); m = g['map']
    if m.name not in done:
        done.add(m.name)
        for q in (0, 1):
            h = m.dragons[q][1][0]
            print(f"SPAWN {m.name} q{q} head{h} deg{sum(1 for d in 'NESW' if m.step(h,d))} open4={region(m,h)} (open4 of empty tile=41) nearest enemy head d={min(m.dist(h, m.dragons[j][1][0]) for j in range(len(m.dragons)) if m.dragons[j][0]!=m.dragons[q][0])}")
    for d in g['deaths']:
        if d['id'] not in (0, 1) or d['reason'] != 'HitHeadToHead': continue
        if 'killer' in d:
            k = d['killer']; mv = [x for x in g['moves'] if x['round'] == d['round'] and x['id'] == k]
            if mv:
                mv = mv[-1]; dist = m.dist(mv['head'], d['head'])
                print(f"{tag:26} q{d['id']} L{d['len']} r{d['round']} KILLED_BY {'ally' if d['killer_team']==d['team'] else 'enemy'} L{mv['len_before']} start_dist={dist} steps={mv['steps']} reach={reach(mv['len_before'])}")
        elif 'victim' in d:
            mv = [x for x in g['moves'] if x['round'] == d['round'] and x['id'] == d['id']]
            mv = mv[-1] if mv else {}
            print(f"{tag:26} q{d['id']} L{d['len']} r{d['round']} QUEEN_MOVED_INTO {'ally' if d['victim_team']==d['team'] else 'enemy'} head L{d['victim_len']} steps={mv.get('steps')}")
