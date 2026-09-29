# External knowledge: general snake-game AI vs our bot (28 Sep 2026)

Track: what winning Battlesnake / Hungry Geese / Tron / Loong bots do that transfers to UNSEEN maps, compared with
`bot/main.cpp decide()` (v24). Read-only research; no games were run.

## 1. Sources and what they say

| Source | Architecture | Lesson that transfers |
|---|---|---|
| Battlesnake docs "Useful algorithms"; coreyja "Minimax in Battlesnake"; RBC 2022 winner (minimax + alpha-beta); "Orion's Fang" (paranoid minimax, depth 7, flood fill + edge control) | Shallow adversarial tree search over simultaneous moves (paranoid or Max-N), leaf = flood fill / Voronoi area-control score | Area control is the leaf evaluation; search only a few plies; **model only nearby opponents** |
| "Adversarial N-player Search using Locality for the Game of Battlesnake" (GI paper, dl.gi.de) | Paranoid vs Best-Reply Search (BRS) vs Max-N, **opponents chosen by L1 distance ≤ search depth** | Opponents farther than the horizon can't interact; picking only the close ones makes adversarial search cheap enough |
| a1k0n, Google AI Challenge 2010 (Tron) winner postmortem | Alpha-beta + iterative deepening; eval = Voronoi territory (nodes + edges regression from 11.7k games) + **articulation points / tree of chambers**; separated endgame = greedy space filling | "A better evaluation beats deeper search"; territory must be counted per chamber: space behind a door the opponent reaches first is not yours |
| Kaggle Hungry Geese (2021) 2nd/3rd/6th/7th/11th writeups (HandyRL, behaviour cloning + RL + MCTS with decoupled UCT) | NN policy/value + MCTS; heads colliding kills both (like ours) | Winners are NN+search, not reproducible here (no training infra, 100M pts/turn, 64 processes). Their hand features are the useful part: flood fill, food distance, *opponent head next to food*, *opponent tail position*, and each opponent's number of safe moves (a goose with one legal move is predictable) |
| Loong blog (notes/13, over-yonder.tech; still posts 0-18) | HSM/utility with hard-filtered fatal moves; role election via sonar | All their unseen-map gain came from not stepping blind through portals; blanket caution (friendly berth, flat portal penalties) loses; coil+forage their best tactic (80-45) but starved on big sparse boards |

Sources: [Battlesnake useful algorithms](https://docs.battlesnake.com/guides/useful-algorithms),
[coreyja minimax](https://coreyja.com/posts/BattlesnakeMinimax/Minimax%20in%20Battlesnake/),
[locality search paper](https://dl.gi.de/server/api/core/bitstreams/358e228c-0917-4849-a4fe-40d155c3232c/content),
[a1k0n Tron postmortem](https://www.a1k0n.net/2010/03/04/google-ai-postmortem.html),
[Hungry Geese 3rd place deck](https://speakerdeck.com/hoxomaxwell/kaggle-hungry-geese),
[HG 11th place](https://www.kaggle.com/competitions/hungry-geese/writeups/the-wisdom-of-manjushri-if-three-ducks-approach-11),
[HG 2nd place](https://www.kaggle.com/competitions/hungry-geese/writeups/goosebumps-goosebumps-solution-2nd-place),
[awesome-battlesnake](https://github.com/xtagon/awesome-battlesnake), [Loong](https://over-yonder.tech/games/loong/).

## 2. What we already have (don't re-propose)

Mapping the standard snake-AI toolkit onto v24:

| Standard technique | Our version | Status |
|---|---|---|
| Flood fill for space | `bfsFrom()`: time-aware BFS using `freeT` (segments vacate on schedule = "tail release") | have it, better than most Battlesnake bots |
| Voronoi area | `VORONOI_AREA=1`: counts tiles we reach strictly before any other head | have it (but see the tie bug, P2) |
| Self-trap look-ahead | `surviveDepth()`: exact own-body DFS, 12 plies, eats (DFS_EATS), split escape | have it; better than a flood fill for small L |
| Head-to-head avoidance | `threatAt` via `computeThreats()` (reach = visible len-1, capped), TAIL_THREAT, THREAT_TAIL_UNKNOWN | have it, binary |
| Kill moves | `tryRam()` 1-2 step, RAM_GUARD(_LOCAL), `boxEffect()` (enemy head left with 0 exits) | have it, 1-ply only |
| Big-snake escape | KING_ESCAPE (2/3-step sprint or reverse split) | have it |
| Tail chasing / coiling | none (Loong KING_COIL idea in notes/13 never built) | missing, low priority |
| Adversarial search | **none**: every enemy is a static threat map; nobody "moves" in our look-ahead | **missing** |
| Chamber / articulation analysis | none (KING_CORRIDOR_PENALTY is a crude proxy, neutral) | missing |
| Move-order reasoning | none: ties at equal distance treated as lost | **bug-level gap** |

The rejected list (LEARN_PORTALS, UNK_SIZE_PARAMS, INFER_SYM, PEARL_DISTRUST, UNK_PRIOR, EAT_SPRINT,
PORTAL_ALLY_COST, SMALL_SPRINT_THREAT, KING_CORRIDOR_PENALTY, KING_SURVIVE_DEPTH=24) is about map knowledge or
blanket caution. None of the proposals below adds knowledge about the map or adds a flat penalty. They change how
we reason about *other heads*: when they arrive, what they can do next, which space they can take from us. None of
them depends on `w.known`, so they work the same on unseen maps.

One direct read-across from the rejected list: SMALL_SPRINT_THREAT (smalls more timid) scored **0.20**. That is a
big signal that small-dragon caution is expensive. The opposite direction (less timid, better calibrated) has
never been tested; see P4.

## 3. Proposals (ranked by my estimate of value on unseen maps)

### P1. `REPLY_SEARCH`: locality-limited best-reply look-ahead for big dragons

**What.** The Battlesnake paper's idea: adversarial search restricted to heads within L1 distance of the horizon.
Here we use a 2-ply Best-Reply Search: our move, then each nearby enemy head's 1-step reply taken **one at a
time** (BRS; paranoid over all heads jointly is too pessimistic, as blanket caution always was for us). Then run
our existing `surviveDepth()` against the resulting board. The worst case over replies becomes the move's
survival figure.

**Why it's missing.** `surviveDepth()` lets other dragons' bodies vacate (`freeOther`), but it treats enemy
**heads as frozen**. It never considers that a head 1-2 tiles away can step into our only exit corridor. Such a
head needn't ram us; if it just parks its head there (or its neck, next turn), a length-15 king in a 2-wide lane
is dead. `threatAt` only flags the tiles a head can *enter*. It doesn't ask "if it enters X, can we still get
out?". `boxEffect()` asks exactly that question, but only offensively and only with 0 exits.

**Evidence.**
- notes/16: our L≥10 king dies 0.57×/game vs 0.22 for the top teams (trapped 0.17, rammed 0.23, blind portal
  0.11; the portal part is now guarded).
- notes/18: 65 of 111 big-dragon rams were cause A, "every 1-step move threatened". That state is reached one or
  two moves *before* the ram, and a reply-aware look-ahead can see it coming.
- notes/10: Schooltime big dragons suffered 42 trapped self-hits with 0 exits. Maze and room maps are 2 of 7
  kelp styles in the devs' generator, so corridors are common on unseen maps.
- a1k0n/Tron and every top Battlesnake bot search at least the opponent's next move. We are the only design in
  this list that doesn't.

**Where.** In `decide()`, inside the direction loop, right after `int depth = surviveDepth(t, wantDepth);`
(~line 2379), plus a node cap parameter on `surviveDepth`.

```cpp
// params.hpp
#ifndef REPLY_SEARCH
#define REPLY_SEARCH 0
#endif
#ifndef REPLY_MIN_LEN          // only dragons worth protecting
#define REPLY_MIN_LEN 8
#endif
#ifndef REPLY_RADIUS           // L1 radius (from t) of heads we let reply
#define REPLY_RADIUS 3
#endif
#ifndef REPLY_DEPTH
#define REPLY_DEPTH 10
#endif
#ifndef REPLY_PEN
#define REPLY_PEN 120.0
#endif

// main.cpp: make the 60000 node cap in surviveDepth a member `int nodeCap = 60000;`

// decide(), after depth is computed for candidate t (and only if depth passed):
if (REPLY_SEARCH && myLen >= REPLY_MIN_LEN && depth >= std::min(wantDepth, REPLY_DEPTH))
{
    int worst = REPLY_DEPTH;
    int saveCap = nodeCap; nodeCap = 6000;          // ~9 sims x 6k nodes: a few M points
    for (auto& e : segs)
    {
        if (!e.head || e.team == w.myTeam || wrapDist(e.tile, t) > REPLY_RADIUS) continue;
        for (int d2 = 0; d2 < 4; d2++)
        {
            int m = step(e.tile, d2);
            if (m < 0 || m == t) continue;                    // m==t is a ram: threatAt covers it
            if (occId[m] >= 0 && freeT[m] > 1) continue;      // enemy can't go there
            if (exitsOf(m, t) == 0) continue;                 // suicidal reply: ignore (BRS, not paranoid)
            bodyCnt[m]++;                                     // head lands on m and stays >=2 turns (neck)
            int dd = surviveDepth(t, REPLY_DEPTH);
            bodyCnt[m]--;
            worst = std::min(worst, dd);
        }
    }
    nodeCap = saveCap;
    if (worst < REPLY_DEPTH)
        score -= REPLY_PEN * (REPLY_DEPTH - worst) / REPLY_DEPTH;
}
```

Notes:
- `bodyCnt` must already be sized (`surviveDepth` sizes it on its first call, and it always runs just before this
  block). `surviveDepth` leaves `bodyCnt` at 0 on exit, so the ++/-- pair is safe.
- Holding `m` blocked for the whole DFS is slightly paranoid (the head moves on). That is fine: its body trails
  behind it for ≥ its length in turns.
- Optional 2nd stage: also let *ally* heads with a higher ID than ours reply (they move after us this round and
  can wall us in by accident; 13 ally head-ons/g for the top teams show this is real).
- The same worst-case figure can feed `tryKingEscape()`: trigger escape when `worst < 4` on the best move, not
  only when `threatAt > 0`.

**Expected effect.** Fewer king/big-dragon trapped and cornered deaths, especially on maze, room and divide maps.
It only fires for L≥8, i.e. about 1-3 dragons per team, so the CPU cost is negligible (≤ ~5M points). Estimate
+2-5% win rate on unseen maps with corridors, ~0 on open maps.

**Risks.** Over-caution for the king (the historical failure mode). BRS with non-suicidal replies only, and a
penalty rather than a veto, should limit it. The king may also get pushed away from feeders; check that king
length at r500 doesn't drop.

**Test plan.** Mechanism first: BOTDBG on maps/lesson maze_a/maze_b/fountain_b + gen maze-style maps. Count king
(L≥8) deaths per game by cause, with and without the flag (tools/deaths.py). Then paired pool on gen + blind +
lesson (≥120 games each vs v24), holdout genhold last. Also sweep REPLY_MIN_LEN {8, 6} and REPLY_PEN {60, 120}.
Accept if pooled unseen ≥ 0.53 and ranked-map regression ≥ 0.48.

---

### P2. `TURN_ORDER_TIES`: resolve equal-distance races by the real move order

**What.** Hungry Geese and Battlesnake are simultaneous-move games, where equal-distance races are coin flips or
collisions. **Ours is sequential by ID, and the maths gives a clean rule.** Take a head at BFS distance k from a
tile, with our arrival at step s (s=1 is this turn):
- **Higher-ID** head: it hasn't moved this round, so its step k is in round r+k-1, *after* our slot.
- **Lower-ID** head: it already moved this round, so its step k is in round r+k, *before* our slot.
- Either way, **we get there first iff s ≤ k**.

The code treats ties as lost in two places:
- `pearlValue()`: `od == s → v *= 0.55`. That is a 45% haircut on pearls we actually win.
- `bfsFrom()` Voronoi area: `du < otherDist[u]`. Tiles we reach first on a tie are counted as the enemy's (the
  same applies to `VORONOI_BLOCK`).

The rule also holds between allies. Each dragon evaluates at its own slot, so exactly one of two allies computes
"I'm first" for a given tile. No double-chasing is introduced.

**Evidence.** Pure arithmetic from the execution order (notes/01 §3). Contested eats: top teams 24% vs us 19%
(notes/14). EAT_SPRINT failed because sprinting costs length. This change costs nothing: it only stops
undervaluing pearls we already win by walking.

**Where.**
- `pearlValue()` (~line 1003).
- `bfsFrom()` (~line 1030 and 1046).
- Optionally `computeOtherDist()`: store `otherIsEnemy[v]`, so an enemy tie can keep a small head-on risk factor.

```cpp
#ifndef TURN_ORDER_TIES
#define TURN_ORDER_TIES 0
#endif
#ifndef TIE_ENEMY_KEEP     // enemy could step onto our head right after: small risk haircut
#define TIE_ENEMY_KEEP 0.85
#endif
// computeOtherDist(): also fill otherEnemy[v] = 1 if an enemy head attains the min distance (ties -> enemy)
// pearlValue():
int od = otherDist[t];
if (od < s)       v *= 0.25;
else if (od == s) v *= TURN_ORDER_TIES ? (otherEnemy[t] ? TIE_ENEMY_KEEP : 1.0) : 0.55;
// bfsFrom():
if (!VORONOI_AREA || (TURN_ORDER_TIES ? du <= otherDist[u] : du < otherDist[u])) area++;
...
if (VORONOI_BLOCK && otherDist[v] < du + 1) continue;   // already correct: blocks only strict losses
```

**Expected effect.** Small but global: dragons take ~1-in-5 more contested pearls and see slightly more room near
enemies. The threat penalty still guards the head-on risk, since `threatAt[t]` is independent of this change.
Estimate +1-3%, map-agnostic.

**Risks.** More small dragons eat next to enemy heads, so there are more 1-for-1 head-ons (roughly neutral per
notes/14). With RAM_GUARD_LOCAL active this is fine. Possible interaction with feeding/king code that reads
`area`.

**Test plan.** Cheapest item here: run it first. Paired: gen + blind + lesson (120+ each) vs v24. Mechanism
check: contested-eat share (notes/tools/midgame analyze.py) should rise toward 24%, with small-dragon head-on
deaths per game not rising by more than ~10%.

---

### P3. `TRAP_ENEMY`: Voronoi cut-off offense (Tron's territory eval, turned outward)

**What.** Generalise `boxEffect()` from "the enemy head has 0 exits after our move" to "the enemy head's
*reachable area* after our move is smaller than its length". Our head plus our body (with its vacate schedule) is
a wall. Tron bots win almost every game this way: they pick the move that shrinks the opponent's Voronoi region.
The kill doesn't need a ram (1-for-1). The enemy hits kelp or bodies on its own, and a long enemy drops ⌈L/2⌉
pearls next to us.

**Why it matters.** At r500 the longest dragon wins. Killing the enemy's long dragon without losing ours
(unlike `tryRam`) is the single most valuable event in a round-limit game. boxEffect only sees the last move of
such a kill (0 exits); most corridor kills need our head to close the door 2-5 tiles away while the enemy is
still inside.

**Where.**
- `boxEffect()` (~line 1230), or a new `double trapEffect(int t)` added to the score next to it.
- Reuses a variant of `bfsFrom` with a caller-supplied source and blocked set.

```cpp
#ifndef TRAP_ENEMY
#define TRAP_ENEMY 0
#endif
#ifndef TRAP_MIN_ENEMY_LEN
#define TRAP_MIN_ENEMY_LEN 4
#endif
// time-aware reachable-area count from head h, pretending tile t (our new head) is occupied;
// enemy moves on its own clock: tile v enterable at its step k if freeT[v] <= k (freeT is on our clock,
// off by <=1: fine for a heuristic); our head at t stays blocked for our length.
int areaFrom(int h, int blockTile, int cap);
double trapEffect(int t)
{
    double e = 0;
    for (auto& s : segs)
    {
        if (!s.head || s.team == w.myTeam || wrapDist(s.tile, t) > 4) continue;
        int L = enemyVisibleLength(s.id);          // lower bound; tail may be out of view
        if (L < TRAP_MIN_ENEMY_LEN) continue;
        int before = areaFrom(s.tile, -1, L + 4);
        int after  = areaFrom(s.tile, t,  L + 4);
        if (before >= L + 2 && after < L + 1)      // our move turns its region into a coffin
            e += 20.0 + 3.0 * L;                   // dropped pearls ~ L/2 -> ~10*L/2 in pearl units
    }
    return e;
}
// decide() score loop:  if (TRAP_ENEMY) score += trapEffect(t);   (only when depth >= wantDepth: never trade our life)
```

Cost: ≤ a few heads × 2 BFS of ≤ ~L+4 tiles each, which is trivial.

**Expected effect.**
- Occasional free kills of mid/long enemy dragons in corridors and against walls.
- Mostly relevant on room/maze/divide unseen maps and in endgames (enemy king foraging along kelp).
- Estimate +1-3%. It also denies space to enemy pumpers at pocket mouths.

**Risks.**
- Enemy length is a visible lower bound: with the tail out of view, the enemy is longer than we think, so a trap
  looks less likely than it is. That errs on the safe side.
- The enemy can split to escape (reverse split), so trapped L≥4 enemies aren't guaranteed kills. The bonus is
  modest.
- Our head gets closer to an enemy head. The threat penalty still applies, and our life is never traded (gate
  on `depth >= wantDepth`).

**Test plan.**
- Mechanism: count enemy deaths "HitWall/HitSelf/HitOtherBody-into-our-body" with our head within 4, per game
  (deaths.py), flag on vs off.
- Paired pool gen + blind + lesson; also lesson peel_a/peel_b/famine_b (big enemy bodies) as a targeted check.

---

### P4. `PROB_THREAT`: calibrated small-dragon threat (Hungry Geese safe-move counting)

**What.**
- Today any tile an enemy head can enter costs a small dragon a flat `SMALL_THREAT_PEN = 12` (≈1.2 pearls) per
  move, whatever the enemy's situation.
- Hungry Geese feature engineering (3rd place: features for opponent head next to food, opponent safe moves)
  and standard Battlesnake practice weight a head's next tile by how *likely* the head is to go there:
  - a head with 1 safe move goes there with certainty;
  - a head with 3 open moves and a pearl on another side will probably go for the pearl;
  - a head adjacent to a pearl eats it (a Hungry Geese feature).
- Deliberate rammers break pure probability, so keep a floor.

**Evidence.**
- SMALL_SPRINT_THREAT (more timid) crashed to 0.20 overall. Small-dragon caution is very expensive in this game.
- Top teams approach enemy heads 29% of the time vs our 25%, and contest 24% vs 19% of eats (notes/14).
- The flat penalty has never been swept down (the v3 sweep list doesn't include it).

**Where.** `computeThreats()` (~line 1744) builds `threatAt` as a count. Add a parallel `std::vector<float>
threatP` and use it in the score loop at `if (threat > 0) score -= ...` for `myLen < 6` only. Kings keep the
binary rule.

```cpp
#ifndef PROB_THREAT
#define PROB_THREAT 0
#endif
#ifndef PROB_THREAT_FLOOR   // chance a head rams deliberately regardless of its options
#define PROB_THREAT_FLOOR 0.3
#endif
// in computeThreats(), for each enemy head s (1-step reach only):
int opts[4], k = 0; bool pearlNext = false; int pearlTile = -1;
for (int d = 0; d < 4; d++) {
    int v = step(s.tile, d);
    if (v < 0 || (occId[v] >= 0 && freeT[v] > 1)) continue;
    opts[k++] = v;
    if (visible[v] && w.pearlMem[v]) { pearlNext = true; pearlTile = v; }
}
for (int i = 0; i < k; i++) {
    double p = 1.0 / k;
    if (pearlNext) p = (opts[i] == pearlTile) ? 0.8 : 0.2 / std::max(1, k - 1);
    threatP[opts[i]] = std::max<double>(threatP[opts[i]], std::max(PROB_THREAT_FLOOR, p));
}
// score loop, small dragons:
if (PROB_THREAT && myLen < 6 && threat > 0)
    score -= SMALL_THREAT_PEN * 2.0 * threatP[t] * (units <= LAST_FEW_UNITS ? LAST_FEW_MULT : 1.0);  // replaces flat pen
```

The ×2 keeps the average about equal: a typical head has ~2-3 options, so p≈0.4-0.5. The result:
- forced tiles (p=1) cost about 24, twice today's penalty;
- "the enemy will go for its pearl on the other side" tiles cost about 7.

**Expected effect.** Small dragons forage closer to enemy heads when the enemy is predictably busy, and avoid
forced-collision tiles more. Estimate +1-3%; it could also be 0.

**Risks.**
- Opponents' rammers don't follow the model. The floor handles that; sweep PROB_THREAT_FLOOR {0.3, 0.5}.
- Needs a control: run SMALL_THREAT_PEN {8, 6} flat too. If a flat drop does as well, keep the simpler one.

**Test plan.**
- Paired pool on gen + blind + lesson with 3 arms: PROB_THREAT=1; SMALL_THREAT_PEN=8; SMALL_THREAT_PEN=6.
- Watch small-dragon head-on deaths/game and eats r60-350.
- Server A/B on Default/Autarky only if local ≥ 0.53.

---

### P5. `DOOR_AREA`: chamber-aware space for big dragons (Tron articulation points, cheap form)

**What.**
- a1k0n's key eval idea: space behind an articulation point (a door) only counts if you control the door.
- `VORONOI_AREA` counts every tile we reach strictly first, **even when the path to it runs through tiles an
  enemy reaches first**. In open fields that doesn't matter, because there's always a way around. Behind a
  1-2-wide door it matters a lot: an enemy head that gets to the door first closes the whole room.
- The cheap equivalent without Tarjan: for L≥8 also compute the area with *path-blocking* Voronoi. Expansion
  can't pass tiles another head reaches strictly first; that is the existing `VORONOI_BLOCK` rule, applied only
  to big dragons and only to the need check.
- The difference between the two areas is exactly the space that sits behind contested doors.

**Where.** `decide()` score loop, next to `if (area < need && !pump)`. `bfsFrom` gains a `bool block` argument
in place of the compile-time `VORONOI_BLOCK`.

```cpp
#ifndef DOOR_AREA
#define DOOR_AREA 0
#endif
#ifndef DOOR_MIN_LEN
#define DOOR_MIN_LEN 8
#endif
if (DOOR_AREA && myLen >= DOOR_MIN_LEN && area >= need)
{
    double pp2; int area2;
    bfsFromBlocked(t, pp2, area2);           // same BFS, 'otherDist[v] < du+1 -> skip' on
    if (area2 < need)
        score -= 0.5 * AREA_WEIGHT * (need - area2) / need;   // half the normal area penalty
}
```

The full version is Tarjan's articulation points on the BFS subgraph (≤4096 tiles, O(N)). It would give
per-chamber sizes and the door tiles, and would enable a "don't park the king's body across a door" rule. Only
worth building if the cheap version shows a mechanism effect.

**Note.** `VORONOI_BLOCK` exists but I found no journal entry testing it. It applied to *all* dragons and
replaced the area, so a negative result there (if any) wouldn't cover this narrower use.

**Expected effect.** Kings stop entering rooms whose door an enemy (or ally) head reaches first. It targets the
trapped-king deaths (0.17/g) on room/maze maps. Estimate +0-2%. It overlaps with P1: test P1 first and this one
on top.

**Risks.** Over-caution for the king on crowded maps (allies count as "other heads" in `otherDist`, so a feeder
next to the door blocks it). Consider restricting `otherDist` for this BFS to enemy heads only.

**Test plan.** Same pool as P1, on top of P1 if P1 is accepted. Lesson maps fountain_b (gated ring), vault_*,
maze_*; gen maps with rooms/maze/divide style.

## 4. Considered and not recommended

- **Full minimax/MCTS, or NN policies (Hungry Geese winners).** No training pipeline, and 64 independent
  processes with 7×7 vision. Opponent state beyond the window is unknown, so deep search has nothing to search.
  The locality-limited BRS (P1) is the part of this family that fits.
- **KING_COIL (Loong).** It gave +35 net only against their own weaker bot, starved on big sparse boards, and our
  king is fed from ahead by feeders. Low expected value; revisit only for famine-type maps.
- **Sonar map gossip / SPLIT_HANDOFF (notes/13 #4-5).** On unseen maps the knowledge worth sharing is portals
  (usage currently rejected) and pearl timers (don't fit in 64 bits). Low value until portal usage is solved.
- **Territory-difference term in open play (Voronoi as a positive score).** Our spacing already matches the top
  teams (notes/14 §4). SPREAD_GENERIC was estimated low.
- **Probabilistic enemy pearl-race model beyond ties.** Needs enemy intent; P2+P4 capture the cheap part.

## 5. Suggested order for the main agent

1. P2 TURN_ORDER_TIES: tiny diff, principled; run first.
2. P1 REPLY_SEARCH: highest ceiling. Do the mechanism check (king deaths by cause) before win rate.
3. P4 PROB_THREAT, with the flat SMALL_THREAT_PEN controls in the same batch.
4. P3 TRAP_ENEMY.
5. P5 DOOR_AREA on top of P1.

All flags default 0 and are additive; none touches map modules or `w.known` paths.
