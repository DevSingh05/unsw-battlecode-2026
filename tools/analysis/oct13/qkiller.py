#!/usr/bin/env python3
"""qkiller.py REPLAY [TEAM]: for each queen death by head-on, the killer: id, length, birth round, where it was every
5 rounds for the 40 rounds before, how many steps its last move had, and what the queen could see the round before.
Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/qkiller.py work/oct12/replays/1852128.replay"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "notes" / "tools"))
import replay_sim as RS  # noqa: E402


def main():
    o = RS.R.load(sys.argv[1])
    m = RS.Map(o["map"])
    body = {i: [tuple(p) for p in pts] for i, (t, pts) in enumerate(m.dragons)}
    team = {i: "AB"[t] for i, (t, pts) in enumerate(m.dragons)}
    born = {i: 0 for i in body}
    alive = set(body)
    hist = {}  # id -> [(round, head, len)]
    rnd = 0
    actor = None
    last_steps = {}
    for e in o["events"]:
        t = e["t"]
        if t == "roundStart":
            for i in alive:
                hist.setdefault(i, []).append((rnd, body[i][0], len(body[i])))
            rnd = e["round"]
        elif t == "turnStart":
            actor = e["id"]
        elif t == "dragonAction":
            a = e["action"] or {}
            last_steps[e["id"]] = len(a.get("move", [])) if "move" in a else 0
        elif t == "dragonUpdate":
            b = body[e["id"]]
            h = tuple(e["head"])
            if b[0] != h:
                b.insert(0, h)
            tl = tuple(e["tail"])
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif t == "dragonSplit":
            body[e["parent"]] = [tuple(x) for x in e["parentBody"]]
            body[e["child"]] = [tuple(x) for x in e["childBody"]]
            team[e["child"]] = e["team"]
            born[e["child"]] = rnd
            alive.add(e["child"])
        elif t == "dragonDeath":
            i = e["id"]
            if i in (0, 1) and e["reason"] == "HitHeadToHead":
                k = actor
                qh = hist[i][-1] if hist.get(i) else None
                print(f"queen {i} (team {team[i]}) died r{rnd} at {body[i][0]} L{len(body[i])}; " +
                      (f"killer {k} team {team[k]} L{hist[k][-1][2] if hist.get(k) else '?'} born r{born[k]}, last move {last_steps.get(k)} steps" if k != i else "she moved into a head"))
                if k != i and hist.get(k):
                    tr = [x for x in hist[k] if x[0] >= rnd - 40 and (rnd - x[0]) % 5 == 0]
                    print("   killer path: " + "  ".join(f"r{r}{h}L{L}(d{m.dist(h, qh[1]) if qh else '?'})" for r, h, L in tr))
                if qh:
                    seen = [(j, team[j], hist[j][-1][1], hist[j][-1][2]) for j in alive if j != i and team[j] != team[i] and hist.get(j) and m.cheb(hist[j][-1][1], qh[1]) <= 3]
                    print(f"   enemy heads in her 7x7 view at the start of r{rnd}: {seen}")
            alive.discard(i)


if __name__ == "__main__":
    main()
