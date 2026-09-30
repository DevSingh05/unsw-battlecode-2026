#!/usr/bin/env python3
"""Dead-end pocket entry accounting (lineage-aware) for server or local replays.

usage (from project root):
  python3 notes/slithery_pockets/entries2.py 656999:B 656725:A ...        (server ids, our side letter)
  python3 notes/slithery_pockets/entries2.py path/to/x.replay:A ...       (local replays)
  add --by to break entries down by (pocket size, pearl tiles, len in, gated?)

An entry = one of the team's heads moves from a core tile onto a pocket tile (leaf-pruned static graph).
The entry's lineage = the diver plus children born from it (or from its descendants) while their head is
inside. Length OUT = lengths of lineage members at the moment their head leaves the pocket (children born
with their head already outside count at birth). net = out - lenIn. Pearls = pocket-tile eats by members.
gated = pocket component smaller than lenIn+3 tiles (the bot's area<need test, where pump/factory decides).
"""
import sys, os, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate


def pockets(m):
    nb = {}
    for x in range(m.w):
        for y in range(m.h):
            t = (x, y); nb[t] = {m.step(t, d) for d in 'NESW'} - {None}
    deg = {t: len(v) for t, v in nb.items()}; rem = set(); q = [t for t, d in deg.items() if d <= 1]
    while q:
        nq = []
        for t in q:
            if t in rem: continue
            rem.add(t)
            for u in nb[t]:
                if u in rem: continue
                deg[u] -= 1
                if deg[u] <= 1: nq.append(u)
        q = nq
    return rem


def comps(m, PK):
    cid = {}
    for t in PK:
        if t in cid: continue
        st = [t]; cid[t] = t
        while st:
            u = st.pop()
            for d in 'NESW':
                v = m.step(u, d)
                if v in PK and v not in cid: cid[v] = t; st.append(v)
    return cid


def analyse(path, us, agg, byk):
    G = simulate(path); m = G['map']; PK = pockets(m); cid = comps(m, PK)
    size = collections.Counter(cid.values())
    ptiles = collections.Counter(cid[t] for t in PK if (m.tiles.get(t) or (0, 0))[0] > 0)
    eats = collections.Counter((e['id'], e['round']) for e in G['eats'] if e['tile'] in PK)
    kids = collections.defaultdict(list)
    for s in G['splits']: kids[(s['parent'], s['round'])].append(s['child'])
    dlen = {d['id']: d['len'] for d in G['deaths']}
    R = G['rounds']; prev = {}
    member = {}   # id -> entry record
    alleats = collections.Counter((e['id'], e['round']) for e in G['eats'] if e['tile'] not in PK)
    for r, snap in R:
        H = snap['heads']
        for j, (t, L, T) in H.items():
            if t not in PK and L <= 3 and j not in member:
                who = 'us' if T == us else 'them'; agg[who]['openT'] += 1; agg[who]['openE'] += alleats[(j, r)]
        for e in set(member.values()) if False else {id(v): v for v in member.values()}.values():
            e['mt'] = e.get('mt', 0) + e['n']
        # births
        for j in list(member):
            for c in kids.get((j, r), []):
                e = member[j]; e['sp'] += 1
                if c in H and H[c][0] in PK: member[c] = e; e['n'] += 1
                elif c in H: e['out'] += H[c][1]
        for j, (t, L, T) in H.items():
            who = 'us' if T == us else 'them'
            if j in member:
                e = member[j]; e['ate'] += eats[(j, r)]
                if t not in PK:
                    e['out'] += L; e['n'] -= 1; del member[j]
                    if e['n'] == 0: close(e, agg, byk)
                continue
            p = prev.get(j)
            if t in PK and p is not None and p not in PK:
                c = cid[t]
                a = eats[(j, r)]
                e = {'who': who, 'r': r, 'id': j, 'lenIn': L - a, 'ate': a, 'sp': 0, 'units': snap[T]['n'], 'out': 0, 'n': 1, 'dead': [],
                     'key': (size[c], ptiles[c], L - a, 'G' if size[c] < L - a + 3 else 'u')}
                member[j] = e
        for j in list(member):
            if j not in H:
                e = member.pop(j); e['n'] -= 1; e['dead'].append(dlen.get(j, 0))
                if e['n'] == 0: close(e, agg, byk)
        prev = {j: v[0] for j, v in H.items()}
    agg['us']['games'] += 1; agg['them']['games'] += 1
    for e in set(map(id, member.values())):
        pass


def close(e, agg, byk):
    a = agg[e['who']]; a['entries'] += 1; a['lenIn'] += e['lenIn']; a['ate'] += e['ate']
    a['out'] += e['out']; a['net'] += e['out'] - e['lenIn']
    for L in e['dead']:
        a['dead'] += 1; a['deadlen'] += L; a[f'dead{min(L, 5)}'] += 1
    if e['out'] == 0: a['wiped'] += 1
    cyc = 'cyc' if e['sp'] else 'nosplit'
    a[cyc] += 1; a[cyc + '_net'] += e['out'] - e['lenIn']; a[cyc + '_ate'] += e['ate']
    cap = 'atcap' if e['units'] >= 60 else 'free'
    a[cap] += 1; a[cap + '_net'] += e['out'] - e['lenIn']
    a['mt'] += e.get('mt', 0); a[cyc + '_mt'] += e.get('mt', 0)
    e['key'] = e['key'] + (cyc,)
    if LIST and e['who'] == 'us': print('ENTRY', e['r'], e['id'], e['key'], 'ate', e['ate'], 'out', e['out'], 'dead', e['dead'])
    b = byk[(e['who'], e['key'])]; b['n'] += 1; b['net'] += e['out'] - e['lenIn']; b['ate'] += e['ate']; b['dead'] += len(e['dead'])


LIST = '--list' in sys.argv


def main():
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    agg = {'us': collections.Counter(), 'them': collections.Counter()}
    byk = collections.defaultdict(collections.Counter)
    for x in args:
        p, _, us = x.rpartition(':')
        if p.isdigit(): p = os.path.join(ROOT, f'replays/auto/games/{p}.replay')
        analyse(p, us, agg, byk)
    for who in ('us', 'them'):
        a = agg[who]; n = max(1, a['games']); E = max(1, a['entries'])
        print(f"{who:4s} games {a['games']} entries/g {a['entries']/n:6.1f} lenIn {a['lenIn']/E:4.2f} pearls/entry {a['ate']/E:4.2f}"
              f" net/entry {a['net']/E:+5.2f} net/g {a['net']/n:+6.1f} deadInside/g {a['dead']/n:5.1f}"
              f" (L2 {a['dead2']/n:.1f} L3 {a['dead3']/n:.1f} L4 {a['dead4']/n:.1f} L5+ {a['dead5']/n:.1f}) wiped/g {a['wiped']/n:.1f}")
        print(f"      open-field L<=3 eats/turn {a['openE']/max(1,a['openT']):.3f}  dive member-turns/entry {a['mt']/E:.2f} -> net per member-turn {a['net']/max(1,a['mt']):+.3f}; cycles {a['cyc_net']/max(1,a['cyc_mt']):+.3f}/turn")
        print('      ' + '  '.join(f"{c}: {a[c]/n:5.1f}/g net/e {a[c + '_net']/max(1, a[c]):+5.2f}" for c in ('cyc', 'nosplit', 'atcap', 'free')))
    if '--by' in sys.argv:
        print('who  size ptiles lenIn gated cycle    n/g  net/e  ate/e dead/e')
        n = max(1, agg['us']['games'])
        for (who, k), b in sorted(byk.items(), key=lambda kv: -kv[1]['n']):
            if b['n'] / n < 0.5: continue
            print(f"{who:4s} {k[0]:4d} {k[1]:6d} {k[2]:5d} {k[3]:5s} {k[4]:7s} {b['n']/n:5.1f} {b['net']/b['n']:+6.2f} {b['ate']/b['n']:6.2f} {b['dead']/b['n']:6.2f}")


if __name__ == '__main__':
    main()
