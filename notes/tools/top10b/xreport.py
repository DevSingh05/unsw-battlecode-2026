"""Report from crossing.pkl: per map/group crossing rate, fatality, exit occupancy, and mouth-tile occupancy."""
import pickle, collections, os
H = os.path.dirname(os.path.abspath(__file__))
d = pickle.load(open(os.path.join(H, 'crossing.pkl'), 'rb')); X = d['x']
ng = collections.Counter()
for tag, oc, mf in d['occ']: ng[(tag['grp'], tag['map'])] += 1
for mp in ('Default', 'Portals', 'Schooltime', 'Trauma', 'Autarky', 'Queen Of Spades', 'Slithery Fight', 'Trophy', 'Prisoners Dilemma'):
    print('=====', mp)
    for g in ('top', 'peer', 'us', 'usopp'):
        xs = [x for x in X if x['grp'] == g and x['map'] == mp]
        n = ng[(g, mp)]
        if not xs or not n: continue
        dead = [x for x in xs if x['died']]
        occ = collections.Counter(x['exit_occ'] for x in xs)
        print(f"{g:6s} g={n} cross/g={len(xs)/n:.0f} fatal%={100*len(dead)/len(xs):.1f} fatal/g={len(dead)/n:.1f} exitOcc%={100*(1-occ['none']/len(xs)):.1f} "
              f"pingpong%={100*sum(x['pingpong'] for x in xs)/len(xs):.0f} own1={sum(x['own1'] for x in xs)/len(xs):.2f} ownh3={sum(x['ownh3'] for x in xs)/len(xs):.2f} L>=5%={100*sum(x['L']>=5 for x in xs)/len(xs):.0f} sprint%={100*sum(x['steps']>1 for x in xs)/len(xs):.0f}")
        print('       exit occupant per game', {k: round(v / n, 1) for k, v in occ.items() if k != 'none'}, ' fatal w/ exit occupied/g', round(sum(1 for x in dead if x['exit_occ'] != 'none') / n, 1))
        b = collections.defaultdict(lambda: [0, 0])
        for x in xs:
            if x['exit_occ'] != 'none': continue
            k = min(x['own1'], 3); b[k][0] += 1; b[k][1] += x['died'] is not None
        print('       exit free: (cross/g, fatal%) by own segs within 1 of exit', {k: (round(v[0] / n), round(100 * v[1] / v[0])) for k, v in sorted(b.items())})
agg = collections.defaultdict(lambda: [0, 0, 0, 0])
for tag, oc, mf in d['occ']:
    if not oc: continue
    a = agg[(tag['map'], tag['grp'])]; a[0] += oc[0]; a[1] += oc[1]; a[2] += mf; a[3] += 1
print('\nmouth-tile occupancy (share of own segments on tiles next to a portal edge, vs share of map that is mouth)')
for k in sorted(agg):
    a = agg[k]; print(f'{k[0][:14]:14s} {k[1]:6s} seg share {a[0]/a[1]:.3f} map frac {a[2]/a[3]:.3f} ratio {(a[0]/a[1])/(a[2]/a[3]):.2f}')
