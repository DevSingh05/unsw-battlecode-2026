#!/usr/bin/env python3
"""Timeline of one replay for loss narratives.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 work/gfloss/narr/timeline.py <gameId> <ourSide A|B>
Prints per-checkpoint unit/total/longest/queen for both sides, kings (longest unit) over time with their eats and
feed-eats (pearls from own-team corpses), deaths per 50-round bin by cause and length lost, queen paths and deaths,
and the biggest single deaths.
"""
import collections
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "notes" / "tools"))
import replay_sim as RS  # noqa: E402

CK = (10, 25, 50, 75, 100, 150, 200, 250, 300, 350, 400, 450, 500)


def dmode(d, T):
    r = d["reason"]
    if r == "HitHeadToHead":
        if d.get("killer_team") and d.get("killer") != d["id"]:
            return "ram_by_" + ("ally" if d["killer_team"] == T else "enemy")
        if d.get("victim_team"):
            return "rammed_" + ("ally" if d["victim_team"] == T else "enemy")
        return "H2H?"
    if r == "HitOtherBody":
        h = d.get("hit")
        return "Body_" + (("ally" if h["team"] == T else "enemy") if h else "?")
    return r


def snap_at(g, r):
    best = g["rounds"][0][1]
    for rr, x in g["rounds"]:
        if rr <= r:
            best = x
        else:
            break
    return best


def main():
    gid, us = sys.argv[1], sys.argv[2]
    th = "B" if us == "A" else "A"
    g = RS.simulate(str((pathlib.Path(gid) if gid.endswith(".replay") else ROOT / "work" / "oct12" / "replays" / f"{gid}.replay")))
    m = g["map"]
    uq = 0 if g["team"][0] == us else 1
    tq = 1 - uq
    lab = {us: "US", th: "TH"}
    print(f"== {gid} map {m.name} {m.w}x{m.h} sym {m.sym} result {g['result']} last {g['last_round']}")
    print(f"   our queen id {uq} spawn {m.dragons[uq][1][0]} ; their queen id {tq} spawn {m.dragons[tq][1][0]}")
    # checkpoints
    for r in CK:
        if r > g["last_round"] + 1:
            break
        s = snap_at(g, r)
        out = []
        for T in (us, th):
            q = uq if T == us else tq
            x = s[T]
            out.append(f"{lab[T]} n{x['n']:3d} tot{x['total']:4d} max{x['max']:3d}(id{x['king']}) q{x['ids'].get(q, 0):3d} "
                       f"top{x['lens'][:5]} small<=4:{sum(1 for L in x['lens'] if L <= 4)}")
        print(f"r{r:3d} " + " || ".join(out))
    # kings over time
    print("-- kings (longest unit) by checkpoint and their growth")
    kings = {us: set(), th: set()}
    for r in CK:
        if r > g["last_round"] + 1:
            break
        s = snap_at(g, r)
        for T in (us, th):
            if s[T]["king"] is not None:
                kings[T].add(s[T]["king"])
    death = {d["id"]: d for d in g["deaths"]}
    for T in (us, th):
        for k in sorted(kings[T]):
            e = [x for x in g["eats"] if x["id"] == k]
            byb = collections.Counter((x["round"] // 50) * 50 for x in e)
            feed = sum(1 for x in e if x["corpse"] and x["corpse"][1] == T)
            enemyc = sum(1 for x in e if x["corpse"] and x["corpse"][1] != T)
            dd = death.get(k)
            ds = f"died r{dd['round']} L{dd['len']} {dmode(dd, T)} killer_len {dd.get('killer_len')}" if dd else "alive"
            print(f"  {lab[T]} king id{k} born r{g['born'].get(k)} eats {len(e)} (own-corpse {feed}, enemy-corpse {enemyc}) "
                  f"by bin {dict(sorted(byb.items()))} ; {ds}")
    # deaths per bin
    print("-- deaths per 50-round bin: cause count/length")
    for T in (us, th):
        B = collections.defaultdict(lambda: collections.Counter())
        BL = collections.defaultdict(lambda: collections.Counter())
        for d in g["deaths"]:
            if d["team"] != T:
                continue
            b = (d["round"] // 50) * 50
            md = dmode(d, T)
            B[b][md] += 1
            BL[b][md] += d["len"]
        for b in sorted(B):
            print(f"  {lab[T]} r{b:3d}-{b + 49}: " + ", ".join(f"{k} {B[b][k]}/{BL[b][k]}" for k in sorted(B[b])))
    # eats per bin and feeds
    print("-- eats per 50 bin (all / own-corpse / enemy-corpse)")
    for T in (us, th):
        E = collections.defaultdict(lambda: [0, 0, 0])
        for x in g["eats"]:
            if x["team"] != T:
                continue
            b = (x["round"] // 50) * 50
            E[b][0] += 1
            if x["corpse"]:
                E[b][1 if x["corpse"][1] == T else 2] += 1
        print(f"  {lab[T]} " + " ".join(f"{b}:{v[0]}/{v[1]}/{v[2]}" for b, v in sorted(E.items())))
    # queens
    for q, T in ((uq, us), (tq, th)):
        mv = [x for x in g["moves"] if x["id"] == q]
        path = [(x["round"], tuple(x["head"]), x["len_before"]) for x in mv if x["round"] % 15 == 0]
        sp = [(x["round"], x["L"], x["k"], x["exits"]) for x in g["splits"] if x["parent"] == q]
        e = [x for x in g["eats"] if x["id"] == q]
        print(f"-- {lab[T]} queen id{q}: splits(round,L,k,exits) {sp[:20]}{'...' if len(sp) > 20 else ''}; eats {len(e)}")
        print(f"   path(round,head,len) {path}")
        d = death.get(q)
        if d:
            print(f"   DIED r{d['round']} L{d['len']} {dmode(d, T)} killer {d.get('killer')} killer_len {d.get('killer_len')} "
                  f"move {d.get('move')} nbrs {d.get('nbrs')} enemy_near {d.get('enemy_near')} ally_near {d.get('ally_near')} "
                  f"king {d.get('king')} hit {d.get('hit')} head {d['head']}")
    # biggest deaths
    print("-- biggest deaths (L>=10)")
    for d in sorted(g["deaths"], key=lambda d: d["round"]):
        if d["len"] >= 10:
            T = d["team"]
            print(f"  r{d['round']} {lab[T]} id{d['id']} L{d['len']} {dmode(d, T)} killer {d.get('killer')} "
                  f"klen {d.get('killer_len')} enemy_near {d.get('enemy_near')} nbrs {d.get('nbrs')}")


if __name__ == "__main__":
    main()
