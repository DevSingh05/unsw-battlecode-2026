"""Per-game, per-side deep profile for the dev test 1 study (5 Oct). Reads replays/top4_horse/sample.json,
writes scratch dev5/prof.pkl: {gid: {'meta':..., 'A':row, 'B':row}} with row = dict of features (see below).
Team label per side: DEV, VIB, FTM, SSS, Sponge, or our build name (q1/f1/h1/amb) from upload windows.
usage (from project root): python3 notes/top5/new_rules_tools/prof_dev5.py"""
import sys, json, pickle, math, os, collections, datetime as dt
sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD = '/Users/devsingh/Developer/UNSW_Battlecode/replays/top4_horse/'
S = '/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/top4/horse/'
SHORT = {842: 'HORSE', 157: 'larp', 998: 'gru', 742: 'ImagineW', 545: 'DEV', 306: 'VIB', 264: 'FTM', 91: 'SSS', 213: 'Sponge', 454: 'aAah', 55: 'glyph', 952: 'US'}
UPL = [('2026-10-05T14:25:43', 'b3'), ('2026-10-06T03:04:27', 'v1'), ('2026-10-06T05:09:40', 'pb2'), ('2026-10-06T15:38:28', 'b4'), ('2026-10-06T16:49:10', 'kf1'), ('2026-10-07T19:26:05', 'b4')]


def usver(at):
    t = dt.datetime.fromisoformat(at[:19]); name = 'old'
    for u, n in UPL:
        tu = dt.datetime.fromisoformat(u)
        if t >= tu: name = n if (t - tu).total_seconds() >= 300 else 'amb'
    return name


def lcls(L): return 'L2' if L <= 2 else 'L3' if L == 3 else 'L4-7' if L <= 7 else 'L8+'
def bkt(r): return 0 if r < 50 else 1 if r < 100 else 2 if r < 200 else 3 if r < 300 else 4 if r < 400 else 5
BK = ['r0-49', 'r50-99', 'r100-199', 'r200-299', 'r300-399', 'r400-500']
CK = (10, 25, 50, 75, 100, 150, 200, 250, 300, 350, 400, 450, 500)


def side_row(g, m, T, E, qi, eq, rd, last):
    r = {}
    rounds = g['rounds']
    # economy curves
    def at(k, key, t=T):
        s = rd.get(min(k, last)); return s[t][key] if s else None
    for key in ('n', 'total', 'max'):
        r[key] = {k: at(k, key) for k in CK}
        r['e' + key] = {k: at(k, key, E) for k in CK}
    # unit-round length mix per bucket
    mix = collections.defaultdict(collections.Counter)
    nkings = {}
    for k, s in rounds:
        for L in s[T]['lens']: mix[bkt(k)][lcls(L)] += 1
        if k in (100, 200, 300, 400, 500) or k == last:
            nkings[k] = (sum(1 for L in s[T]['lens'] if L >= 10), sum(1 for L in s[T]['lens'] if L >= 20), sum(1 for L in s[T]['lens'] if L >= 8))
    r['mix'] = {b: dict(c) for b, c in mix.items()}; r['nkings'] = nkings
    for th in (5, 8, 10, 15, 20, 30, 40):
        r[f'first{th}'] = next((k for k, s in rounds if s[T]['max'] >= th), None)
    # splits
    born = {x['child']: x['round'] for x in g['splits'] if x['team'] == T}
    dd = {x['id']: x for x in g['deaths']}
    sp = []
    for x in g['splits']:
        if x['team'] != T: continue
        c = x['child']; d = dd.get(c)
        life = (d['round'] - x['round']) if d else last - x['round'] + 1
        sp.append((x['round'], x['L'], x['k'], x['parent'] == qi, x['exits'], x['enemy_dist'], life, d['reason'] if d else None))
    r['splits'] = sp
    # deaths (own)
    dl = []
    for x in g['deaths']:
        if x['team'] != T: continue
        kg = x.get('king')
        dl.append({'round': x['round'], 'id': x['id'], 'len': x['len'], 'reason': x['reason'], 'q': x['id'] == qi,
                   'kingd': kg[2] if kg else None, 'kinglen': kg[1] if kg else None, 'kingid': kg[0] if kg else None,
                   'en': x.get('enemy_near'), 'killer_len': x.get('killer_len'), 'killer': x.get('killer'), 'head': x['head'], 'move': x.get('move'),
                   'actor_self': x['actor'] == x['id'], 'age': x['age']})
    r['deaths'] = dl
    # corpse pearl fate: eats of pearls from our corpses / enemy corpses
    ce = []
    for e in g['eats']:
        if not e['corpse']: continue
        did, dteam, drnd, dlen = e['corpse']
        if dteam != T and e['team'] != T: continue
        s = rd.get(e['round'] - 1) or rd.get(e['round'])
        king = s[e['team']]['king'] if s else None
        ce.append({'round': e['round'], 'src_team': 'own' if dteam == T else 'en', 'eater_team': 'own' if e['team'] == T else 'en',
                   'eater_is_king': e['id'] == king, 'eater_q': e['id'] in (0, 1), 'eater_len': e['len'], 'delay': e['round'] - drnd, 'src_len': dlen})
    r['corpse_eats'] = ce
    # all eats by our side: fresh / corpse own / corpse en by bucket and by length class
    ec = collections.Counter()
    for e in g['eats']:
        if e['team'] != T: continue
        kind = 'fresh' if not e['corpse'] else ('cown' if e['corpse'][1] == T else 'cen')
        ec[(bkt(e['round']), kind)] += 1
        if e['len']: ec[('cls', lcls(e['len']), kind)] += 1
    r['eats'] = dict(ec)
    # queen
    qs = [(x['round'], x['L'], x['k'], x['exits']) for x in g['splits'] if x['parent'] == qi]
    r['q_splits'] = qs
    r['q_len'] = {k: (rd[min(k, last)][T]['ids'].get(qi, 0)) for k in CK}
    r['q_isking'] = {k: (rd[min(k, last)][T]['king'] == qi) for k in (100, 200, 300, 400, 500)}
    qd = dd.get(qi)
    if qd:
        st = None
        if 'killer' in qd:
            mv = [a for a in g['moves'] if a['id'] == qd['killer'] and a['round'] == qd['round']]
            st = mv[0]['steps'] if mv else None
        r['q_death'] = (qd['round'], qd['reason'], qd['len'], qd.get('killer_len') or qd.get('victim_len'), st, qd.get('killer_team') or qd.get('victim_team'))
    else: r['q_death'] = None
    spawn = m.dragons[qi][1][0]; espawn = m.dragons[eq][1][0]
    qpos = collections.defaultdict(list); qen = collections.defaultdict(list); qal = collections.defaultdict(list)
    for k, s in rounds:
        if qi not in s['heads'] or k % 5: continue
        h = s['heads'][qi][0]; b = 0 if k < 100 else 1 if k < 300 else 2
        qpos[b].append(m.dist(h, spawn))
        eh = [m.dist(h, v[0]) for j, v in s['heads'].items() if v[2] == E]
        if eh: qen[b].append(min(eh))
        qal[b].append(sum(1 for j, v in s['heads'].items() if v[2] == T and j != qi and m.dist(h, v[0]) <= 4))
    av = lambda a: round(sum(a) / len(a), 1) if a else None
    r['q_spawnd'] = {b: av(v) for b, v in qpos.items()}; r['q_enemyd'] = {b: av(v) for b, v in qen.items()}; r['q_allies4'] = {b: av(v) for b, v in qal.items()}
    qe = [e for e in g['eats'] if e['id'] == qi]
    r['q_eats'] = (len(qe), sum(1 for e in qe if e['corpse'] and e['corpse'][1] == T), sum(1 for e in qe if not e['corpse']))
    # moves: steps hist, paid moves, kills
    mv = [a for a in g['moves'] if a['team'] == T and 'move' in a['act']]
    r['steps'] = dict(collections.Counter((lcls(a['len_before']), min(a['steps'], 6)) for a in mv))
    kills = []
    for a in mv:
        ks = [k for k in a['killed'] if k[1] != T]
        if not ks: continue
        L = a['len_before']; F = math.ceil(L / 4); paid = max(0, a['steps'] - F)
        for k in ks:
            vid, vteam, vlen = k
            # approach: distance killer head -> victim head at end of rounds r-1..r-4
            ap = []
            for back in (1, 2, 3, 4, 6):
                s = rd.get(a['round'] - back)
                if s and a['id'] in s['heads'] and vid in s['heads']: ap.append(m.dist(s['heads'][a['id']][0], s['heads'][vid][0]))
                else: ap.append(None)
            s0 = rd.get(a['round'] - 1); king_e = s0[E]['king'] if s0 else None
            kills.append({'round': a['round'], 'kl': L, 'steps': a['steps'], 'paid': paid, 'ate': a['ate'], 'vlen': vlen, 'vq': vid == eq,
                          'vking': vid == king_e, 'killer_q': a['id'] == qi, 'approach': ap, 'mutual': a['died'] == 'HitHeadToHead'})
    r['kills'] = kills
    # body kills: enemy died moving into our body
    r['body_kills'] = sum(1 for x in g['deaths'] if x['team'] == E and x['reason'] == 'HitOtherBody' and x['hit'] and x['hit']['team'] == T)
    r['body_kills_q'] = sum(1 for x in g['deaths'] if x['team'] == E and x['id'] == eq and x['reason'] == 'HitOtherBody' and x['hit'] and x['hit']['team'] == T)
    # paid moves without kill
    r['paid_nokill'] = sum(1 for a in mv if a['steps'] > math.ceil(a['len_before'] / 4) and not a['killed'])
    r['paid_nokill_eat'] = sum(1 for a in mv if a['steps'] > math.ceil(a['len_before'] / 4) and not a['killed'] and a['ate'])
    # portals
    portal = set(e for e, (k, p) in m.edges.items() if k == 2)
    pc = 0
    if portal:
        for a in mv:
            p = a['head']
            for d in a['act']['move']:
                if m.side_edge(p, d) in portal: pc += 1
                n = m.step(p, d)
                if n is None: break
                p = n
    r['portal'] = pc if portal else None
    # opening snapshot: head positions relative to spawns
    op = {}
    for k in (10, 20, 30, 45, 60):
        s = rd.get(k)
        if not s: continue
        hs = [v for j, v in s['heads'].items() if v[2] == T]
        op[k] = {'n': len(hs), 'tot': s[T]['total'], 'own': sum(1 for v in hs if m.dist(v[0], spawn) < m.dist(v[0], espawn)),
                 'en': sum(1 for v in hs if m.dist(v[0], spawn) > m.dist(v[0], espawn)), 'lens': sorted([v[1] for v in hs], reverse=True)[:5]}
    r['open'] = op
    r['final'] = (rd[last][T]['ids'].get(qi, 0), rd[last][T]['max'], rd[last][T]['total'], rd[last][T]['n'])
    return r


def analyse(gm):
    g = sim2.simulate(RD + f"{gm['id']}.replay"); m = g['map']; last = g['last_round']
    rw = g['result']['winner']
    if rw is None: return None
    aw = gm['winner']
    flip = not ((rw == 'A') == (aw == 'a'))
    lab = {}
    for side, key in (('A', 'a'), ('B', 'b')):
        tm = gm[key] if not flip else gm['b' if key == 'a' else 'a']
        nm = SHORT.get(tm['id'], tm['name'])
        if nm == 'US': nm = usver(gm['at'])
        lab[side] = nm
    rd = dict(g['rounds'])
    q = {g['team'][0]: 0, g['team'][1]: 1}
    out = {'meta': {'gid': gm['id'], 'at': gm['at'], 'map': m.name, 'ranked': gm['ranked'], 'winner': rw, 'reason': g['result'].get('endReason'), 'last': last, 'lab': lab}}
    for T in 'AB':
        E = 'B' if T == 'A' else 'A'
        out[T] = side_row(g, m, T, E, q[T], q[E], rd, last)
    return out


if __name__ == '__main__':
    G = json.load(open(RD + 'sample.json'))
    cache = S + 'prof.pkl'
    rows = pickle.load(open(cache, 'rb')) if os.path.exists(cache) else {}
    for gm in G:
        if gm['id'] in rows or not os.path.exists(RD + f"{gm['id']}.replay"): continue
        try: rows[gm['id']] = analyse(gm)
        except Exception as e:
            import traceback; traceback.print_exc(); print('fail', gm['id'], e); rows[gm['id']] = None
        pickle.dump(rows, open(cache, 'wb'))
    print(len(rows))
