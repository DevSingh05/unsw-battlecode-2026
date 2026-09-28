#!/usr/bin/env python3
"""Fine-grained classification of OUR deaths (and theirs) in the ch1 batch.

For every death: backwards move?, age (rounds since birth), split relation to the
dragon it collided with, our/their unit counts at that moment, feed phase, rams.

    python3 notes/tools/death_detail.py            # grouped tables
Cache: replays/ch1/deaths.pkl
"""
import collections, json, os, pickle, sys

sys.path.insert(0, os.path.dirname(__file__))
from replay_sim import simulate

DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'replays', 'ch1')


def classify(gid, us):
    g = simulate(os.path.join(DIR, f'{gid}.replay'))
    m = g['map']; par = g['parent_of']; born = g['born']
    snap = dict(g['rounds'])
    them = 'B' if us == 'A' else 'A'
    out = []
    # map (round, id) -> killer for H2H pairs
    for d in g['deaths']:
        T = d['team']; k = 'us' if T == us else 'them'
        r = d['round']
        s = snap.get(r - 1) or snap.get(r) or snap[min(snap)]
        rec = {'gid': gid, 'map': m.name, 'side': k, 'round': r, 'len': d['len'], 'reason': d['reason'], 'age': d['age'],
               'n_us': s[us]['n'], 'n_them': s[them]['n'], 'king_len': (d.get('king') or (0, 0, 99, 99))[1],
               'king_dist': (d.get('king') or (0, 0, 99, 99))[2], 'steps': d.get('steps', 0), 'failed': d.get('step_failed', 0)}
        mv = d.get('move') or ''
        body = d['body']
        if d['reason'] == 'HitSelf' and mv and d.get('step_failed'):
            dirc = mv[d['step_failed'] - 1]
            dest = m.step(body[0], dirc)
            rec['backward'] = len(body) > 1 and dest == body[1]
            rec['tail'] = dest == body[-1]
        other = None
        if d['reason'] == 'HitHeadToHead':
            other = d.get('killer') if 'killer' in d else d.get('victim')
            rec['role'] = 'victim' if 'killer' in d else 'mover'
            rec['other_team'] = 'us' if (d.get('killer_team') or d.get('victim_team')) == us else 'them'
            rec['other_len'] = d.get('killer_len') or d.get('victim_len')
        elif d['reason'] == 'HitOtherBody' and d.get('hit'):
            other = d['hit']['id']
            rec['other_team'] = 'us' if d['hit']['team'] == us else 'them'
            rec['other_len'] = d['hit']['len']; rec['seg'] = d['hit']['seg']
        if other is not None:
            i = d['id']
            rec['kin'] = par.get(i) == other or par.get(other) == i
            rec['sibling'] = par.get(i) is not None and par.get(i) == par.get(other)
            rec['other_age'] = r - born.get(other, 0)
            # through a portal? (distance from our head to the collided tile > 1 in plain geometry)
            if mv and d.get('step_failed'):
                dest = m.step(body[0], mv[d['step_failed'] - 1])
                rec['via_portal'] = dest is not None and m.dist(body[0], dest) > 1
        rec['feedphase'] = r >= 330
        out.append(rec)
    return out


def load():
    cache = os.path.join(DIR, 'deaths.pkl')
    summ = json.load(open(os.path.join(DIR, 'summary.json')))
    if os.path.exists(cache):
        return summ, pickle.load(open(cache, 'rb'))
    data = {s['id']: classify(s['id'], s['side']) for s in summ}
    pickle.dump(data, open(cache, 'wb'))
    return summ, data


def main():
    summ, data = load()
    groups = {'W': [], 'L-elim': [], 'L-round': []}
    for s in summ:
        groups['W' if s['win'] else ('L-elim' if s['end'] == 'teamEliminated' else 'L-round')].append(s['id'])
    for key, ids in groups.items():
        n = len(ids)
        D = [d for i in ids for d in data[i]]
        U = [d for d in D if d['side'] == 'us']; T = [d for d in D if d['side'] == 'them']
        print(f'\n===== {key} ({n} games)')
        for lab, S in (('us', U), ('them', T)):
            hs = [d for d in S if d['reason'] == 'HitSelf']
            pre = [d for d in hs if not d['feedphase']]
            post = [d for d in hs if d['feedphase']]
            feed = [d for d in post if d['king_dist'] <= 5 and d['king_len'] >= d['len'] + 2]
            print(f'  {lab}: HitSelf pre-330 {len(pre)/n:.1f}/g (backward {sum(1 for d in pre if d.get("backward"))/n:.1f}, '
                  f'into tail {sum(1 for d in pre if d.get("tail"))/n:.1f}, len2 {sum(1 for d in pre if d["len"]==2)/n:.1f}, age0 {sum(1 for d in pre if d["age"]==0)/n:.1f}); '
                  f'post-330 {len(post)/n:.1f}/g of which feeder-like {len(feed)/n:.1f}')
            fr = [d for d in S if d.get('other_team') == 'us' and lab == 'us' and d['reason'] != 'HitSelf']
            if lab == 'us':
                body = [d for d in fr if d['reason'] == 'HitOtherBody']
                h2h = [d for d in fr if d['reason'] == 'HitHeadToHead' and d['role'] == 'mover']
                for nm, S2 in (('friendly body', body), ('friendly h2h (pairs)', h2h)):
                    print(f'    {nm}: {len(S2)/n:.1f}/g kin {sum(1 for d in S2 if d.get("kin"))/n:.1f} sibling {sum(1 for d in S2 if d.get("sibling"))/n:.1f} '
                          f'via_portal {sum(1 for d in S2 if d.get("via_portal"))/n:.1f} other_age<=1 {sum(1 for d in S2 if d.get("other_age",9)<=1)/n:.1f} '
                          f'pre-330 {sum(1 for d in S2 if not d["feedphase"])/n:.1f} seg0-1(neck) {sum(1 for d in S2 if d.get("seg",9)<=1)/n:.1f} '
                          f'tailseg {sum(1 for d in S2 if d.get("seg",-1)==d.get("other_len",0)-1)/n:.1f}')
            rams = [d for d in S if d['reason'] == 'HitHeadToHead' and d.get('role') == 'mover' and d.get('other_team') != lab]
            if rams:
                behind = sum(1 for d in rams if (d['n_us'] < d['n_them']) == (lab == 'us'))
                sprint = sum(1 for d in rams if d['steps'] >= 2)
                mylen = sum(d['len'] for d in rams) / len(rams); ol = sum(d['other_len'] or 0 for d in rams) / len(rams)
                print(f'    rams by {lab}: {len(rams)/n:.1f}/g, while outnumbered {behind/n:.1f}, sprint {sprint/n:.1f}, avg own len {mylen:.1f} vs target {ol:.1f}, '
                      f'target len>=6 {sum(1 for d in rams if (d["other_len"] or 0)>=6)/n:.1f}')
            other = collections.Counter(d['reason'] for d in S)
            print(f'    all: {dict((a, round(b/n,1)) for a,b in other.most_common())}')
        # early: deaths before round 100
        for lab, S in (('us', U), ('them', T)):
            c = collections.Counter()
            for d in S:
                if d['round'] < 100:
                    k = d['reason']
                    if k == 'HitHeadToHead': k += '-' + d['role'] + '-' + d['other_team']
                    if k == 'HitOtherBody': k += '-' + str(d.get('other_team'))
                    c[k] += 1
            print(f'  <r100 {lab}:', {a: round(b / n, 1) for a, b in c.most_common()})


if __name__ == '__main__':
    main()
