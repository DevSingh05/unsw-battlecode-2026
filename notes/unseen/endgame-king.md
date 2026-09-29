# Endgame / king building that works on any map (track: endgame-king)

Written 2026-09-28 for the unseen-map push (Sprint 1 / Qualifiers are best-of-7 on unseen maps).
Scope: when and how to crown a king on an unknown map, how feeders should die, how to protect the
king, and the length/round schedule. Everything here is a proposal behind a new compile flag
(default 0). Nothing in `bot/` was touched.

## TL;DR

1. **On unknown maps v24 usually builds no king at all.** `RP.kingDeclare` is 0 unless the map is
   recognised, so the only way to become king is to reach length 8 (`KING_MIN_LEN`). But every
   dragon splits at 4 until r350, and small ones keep splitting until r450 (`LATE_SPLIT_ROUND`).
   On any map where the team stays under the 64-unit cap, nobody passes about 5 before r450, no
   beacon goes out, and nobody feeds.
   - Local v24 self-play, one seed: **23 of 46 round-limit team-games on gen/blind maps ended with
     the longest dragon at 3-7**, while those teams still held a total length of 50-100.
   - Blind Portals, Trauma and QoS: longest 4-7 at r500 on every seed tried (s11/s12/s13). The
     top-10 kings on those maps reach 41, 32 and 31.
   - Against any team that builds a king, those games are lost on the tiebreak.
   - Self-play hides this, because both sides are equally king-less, so the result is a coin flip.
2. **Just switching the king on (the old `UNK_SIZE_PARAMS` idea) fails in a specific way.** The
   untrottled "loose" feeding plus `feedReserve=4` burns the swarm down, and the opponent's
   swarm then kills the king.
   - Local check g2026_12: the declared-king side fed 32 dragons in r300-349 and went from 38
     units to 6 by r420. The enemy swarm (49 units) rammed its L31 king with an L2 and eliminated
     the team at r440.
   - g2026_28: an L9-11 king fed the team down to 3 units and was rammed at r498, which lost the
     game 5 vs 6.
   - This is why a crown on unknown maps needs a **throttle and a unit reserve**, not just the
     flag.
3. **On the ladder (known maps, where the king is on), the gap to the top-10 is conversion, not
   growth.** Round-limit games, v19+ vs top-10:
   - Final king 34.4 vs 38.2, but our team's total length at r500 is **121 vs 98**. We leave
     **86.6 length per game** in non-king dragons, against their 59.8.
   - Most of the difference sits in L2-7 dragons (25.3 vs 8.8 per game), a median **20 tiles**
     from the king at the end.
   - About **40% of our small dragons are out of beacon range** late in the game. At r430/r470,
     61%/59% of our L2-3 dragons were hit by any of our own sonar rays in the previous 8 rounds,
     against 89%/75% for the top-10.
4. **Feed deaths next to the king leak to our own small dragons.**
   - Deliberate deaths within 3 of the king: yield to the king **0.48 vs 0.67** (top), and
     **0.38 vs 0.23** of the drop is eaten by other allies.
   - In bursts (another feed death within 3 rounds) it is 0.46 (0.44 to allies) vs 0.67 (0.26).
   - Where the feeder dies still dominates everything: pearls dropped within 3 of the king head
     reach it 54-70% of the time, those further away 2-4%.

Proposals, ranked by my estimate of value (details and C++ sketches in section 5):

| # | flag | what |
|---|---|---|
| 1 | `UNK_KING` | map-agnostic crown on unknown maps (KING_V2 with an adaptive seed) plus a round-scheduled unit reserve |
| 2 | `FEED_QUEUE` (+ `FOOD_RESERVE`) | one feeder at a time, die only when the king's front is clear of food; non-king allies ignore pearls within 2-3 of the king |
| 3 | `KING_NET` | standing relay: every dragon that knows a fresh king re-broadcasts it; age-limited instead of hop-limited |
| 4 | `FEED_REACH` | endgame sweep from r440: any length feeds if it can reach the king in time; reserve steps down to 3 by r490 |
| 5 | `KING_LAST_STAND` | r470+: king and #2 candidate widen their enemy-keep radius and never cross portals blind |

1+2 must be tested together: 1 without 2 reproduces the g12/g28 failure. 3 and 4 are mostly
ladder/conversion gains and also help on unknown maps once 1 is on.

---

## 1. Data and tools

All scripts are in `notes/unseen/tools/` and are read-only on replays. They reuse
`notes/tools/midgame/sim2.py` and use a 4-process pool.

| script | what |
|---|---|
| `feedeff.py [jobs] [--redo]` | per round-limit team-game: king lineage curve, every own death from r250 and where its corpse pearls went (final king / other ally / enemy), feeder position relative to the king head and facing, orientation, lag. Caches `feedeff.pkl`. |
| `steal.py us\|top` | who eats corpse pearls dropped within 3 of the king: eater length, distance, recycled share |
| `leftover.py` | length left in non-king dragons at r500, by bucket, and distance to the king |
| `reach.py` | share of non-king dragons hit by any own sonar ray in the last 8 rounds, at r430/r470 |
| `kingdeath.py` | deaths of the team's longest dragon (L≥10) from r400 |
| `localking.py [glob]` | the same metrics for local replays (`notes/unseen/replays/king/*.replay`) |

**Samples.**
- **us**: 92 round-limit team-games from `replays/v19plus` plus `replays/ab_v20..v24` (v19-v24,
  known maps with modules).
- **top**: 45 round-limit team-games of top-10 teams from `notes/replays/top10b` (all 10 ranked
  maps).
- **local**: v24 vs v24 on 40 gen maps (seed 11), the 10 ranked maps with `NO_KNOWN_MAPS=1`
  (seed 11, plus 12/13 on 6 of them), and the 24 lesson maps (seed 11).
  - These were single sequential games (about 1-30 s each, one core) run to *observe the
    mechanism*, not to measure win rate. They are not a batch test.
  - Replays are in `notes/unseen/replays/king/`.
- **3 mechanism games**: `v24 + -DUNK_SIZE_PARAMS=1 -DUNK_BIG_TILES=0` (king declared on every
  unknown map) vs v24 on g2026_23/12/28 (`usp_*.replay`).

## 2. The unknown-map problem: no king

### 2.1 Why v24 has no king on an unseen map
- `applyMapParams` never runs, so `RP.kingDeclare=0`.
- `iAmKing()` is then `myLen >= KING_MIN_LEN(8) && myLen >= kingLen`. The beacon (`emitSonar`)
  and all feeding (`shouldFeed` needs `kingId >= 0`) depend on it.
- The split rule in `decide()` fires at length ≥4 while `round < 350`, or `round < 450 && myLen
  <= 5` (`LATE_SPLIT_ROUND`, `LATE_SPLIT_MAXLEN`). `bigLate` (don't split when big) is only set
  when `kingDeclare` is on.
- So unless the team is at the 64-unit cap (then splits are refused and dragons grow), **no
  dragon passes about 5 until r450**. With 50 rounds left and sparse pearls, it rarely reaches 8,
  and nothing is ever fed.

### 2.2 Evidence (local v24 self-play)
Round-limit team-games only. "king" is the final longest dragon's lineage; the values are its
length at r300/350/400/450/500.

| map (size) | total length r500 | units | longest r500 (A / B) |
|---|---|---|---|
| blind Portals 32×16, s11/s12/s13 | 51-78 | 20-28 | 5/4, 5/6, 5/6 |
| blind Trauma 48×24, s11/s12/s13 | 36-56 | 14-21 | 4/3, 5/4, 4/4 |
| blind QoS, s12 | 47 | 13 | 7/2 |
| g2026_23 36×12 | 92-99 | 28-29 | 6/7 |
| g2026_12 21×21 | 87-96 | 28 | 7/6 |
| g2026_00 37×12 | 82-106 | 17-25 | 11/15 |
| g2026_32 18×14 | 48-98 | 11-26 | 9/7 |
| g2026_06/09/13/19/20/29, famine_a/b (starving) | 5-25 | 2-8 | 2-5 |
| **with king** (at the 64 cap or rich): g16, g21, g30, g35, g37, g39, blind Schooltime/Slithery, most lesson maps | 200-800 | 30-60 | 20-114 |

- In 23 of 46 gen/blind round-limit team-games the longest dragon at r500 was ≤7.
- On the lesson maps, which are richer by design, kings form, and the outcome follows the king
  race: peel_b 59 v 5, vault_b 50 v 8, maze_b 43 v 11, islands_a 52 v 14.
- **For comparison, the top-10 kings at r500 on these ranked designs:** Portals 41.7, Trauma
  31.7, QoS 31, Autarky 38, Default 25.4, Dilemma 39.7.
- Our own ladder kings on the same maps with knowledge on: Portals 31, Trauma 50, Default 26.
  Those are all maps where the per-map table sets `kingDeclare=1`.

**Takeaway.** Eight of the ten ranked maps turn the king on through the per-map table. Only the
unknown default leaves it off, and that is exactly the case the tournament will play.

### 2.3 Why the earlier attempt (`UNK_SIZE_PARAMS`) was neutral, and what's different now
`UNK_SIZE_PARAMS` (KS 250, SS 360, FS 300, reserve 4, only when `w.N >= 1000`) scored
0.475/0.525/0.488. Three reasons:
1. **It fired on the wrong maps.** The king-less maps are mostly < 1000 tiles (g12 441, g23 432,
   g28 248, g32 252, Portals 512). The ≥1000-tile maps (g16/21/30/35/37/39) already grow kings
   via the unit cap.
2. **It inherited `KING_V2_LOOSE` feeding with `feedReserve=4`.**
   - g2026_12 (`usp_g2026_12_s11`): 32 feed deaths in r300-349 and 18 more in r350-399. Units went
     38 → 22 (r340) → 6 (r420) while the enemy stayed at 39-49.
   - Its king (L31) was rammed by an enemy L2 at r435, and the side was eliminated at r440.
   - g2026_28: fed to 3 units, and the L9 king was rammed by an L4 at r498, losing 5 vs 6.
   - g2026_23: the same flag won **37 vs 18**. The king idea works when the swarm survives.
3. **Self-play only half-rewards it.** v24's swarm (`RAM_MAX_OWN_LEN=3`, rams any head in reach)
   is a strong king-assassin. Real top teams kill kings only about 0.2 times per game (notes/16
   §5). The king-less failure mode costs nothing in self-play, but everything against a
   king-building team.

The new variant (P1) fires on **every** unknown map, keeps a round-scheduled unit reserve, and
depends on the P2 throttle.

## 3. Ladder endgame: where the king's length goes (us vs top-10, round-limit)

### 3.1 King growth and conversion

| | king r300 | r350 | r400 | r450 | r500 | team total r400 | r450 | r500 | units r450 | units r500 |
|---|---|---|---|---|---|---|---|---|---|---|
| top | 4.4 | 9.3 | 16.8 | 27.7 | **38.2** | 105.6 | 96.5 | **98.0** | 12.0 | 6.1 |
| us | 8.1 | 12.1 | 18.6 | 26.6 | **34.4** | 117.5 | 118.5 | **121.0** | 20.7 | 11.8 |

(These are means; medians are similar: r500 36 vs 33.)
- We are ahead until about r420, then fall behind.
- King share of team length at r500: 39% (top) vs 28% (us).
- Won on length: top 76% (mean margin +9.9); us 59% (+4.3). Our weak maps here are Autarky
  (0.36, king 27 vs 33) and Slithery (0.50).

**Own-corpse pearls eaten by the king, per 50 rounds (spawn / own corpse / enemy corpse):**

| | r300 | r350 | r400 | r450 |
|---|---|---|---|---|
| top | 1.6 / 3.9 / 0.0 | 2.3 / 5.8 / 0.2 | 2.9 / **9.1** / 0.3 | 4.2 / **7.9** / 0.3 |
| us | 2.4 / 2.5 / 0.1 | 3.3 / 3.9 / 0.2 | 3.1 / **5.5** / 0.5 | 3.8 / **5.4** / 0.4 |

We eat as many spawns as they do. The gap is own-corpse feeding from r400 on: 18.1 vs 26.1 per
game.

**Length left in non-king dragons at r500 (per game), with median distance to the king:**

| | L2-3 | L4-7 | L8-15 | L16+ | second-longest |
|---|---|---|---|---|---|
| top | 2.6 (18 tiles) | 6.2 (15) | 16.5 (21) | 34.5 (20) | 21.8 |
| us | **9.4** (21) | **15.9** (20) | 25.3 (21) | 36.0 (24) | 20.9 |

That is about 17 extra length in small and medium dragons far from the king. At 0.5 yield it is
worth +8 to the king, which covers the whole gap to the top-10.

### 3.2 Why the far dragons don't feed: beacon reach (`reach.py`)
Share of non-king dragons hit by *any* own sonar ray in the 8 rounds before r430 / r470. This is
an upper bound on "heard the king".

| | L2-3 | L4-7 | L8+ |
|---|---|---|---|
| top r430 / r470 | 0.89 / 0.75 | 0.92 / 0.89 | 0.96 / 0.95 |
| us r430 / r470 | **0.61 / 0.59** | 0.82 / 0.77 | 0.94 / 0.95 |

How the code relays today:
- It relays only when a message was *received this turn* (`haveRelay`), and only for
  `hop < KING_RELAY_HOPS (3)`.
- It drops messages older than 4 rounds.
- `kingId` expires after 12 rounds without news.

The top teams ping from about 90% of their dragons (notes/11: "the whole team's standing
relay"). A dragon that never hears the king never feeds: `shouldFeed` needs `kingId >= 0`.

### 3.3 Feed geometry and leaks (`feedeff.py`, `steal.py`)

**Yield (pearls reaching the king / pearls dropped) by distance from the king head at death:**

| | d1 | d2 | d3 | d4 | d5 | d6+ |
|---|---|---|---|---|---|---|
| top | 0.76 | 0.61 | 0.55 | 0.43 | 0.32 | ≈0.05 |
| us | 0.57 | 0.47 | 0.46 | **0.29** | 0.08 | ≈0.01 |

- By cell (deaths within 6): ahead 0.60 / 0.42, side 0.55 / 0.32, behind 0.27 / 0.10 (top /
  us).
- All corpse pearls within 3 of the king head at death: 0.70 / 0.54. Some within 3: 0.55 / 0.42.
  None: 0.04 / 0.02.
- Our `KING_V2_LOOSE` path lets feeders die at `dk` 2-4 and within 2 of the target. Much of our
  drop lands at d3-4: 1,587 of the 2,744 pearls dropped at d1-6 (58%), vs 595 of 1,392 (43%) for top.

**Orientation** (feeder facing vs king facing, deliberate deaths within 3):
- Head-on ≈ perpendicular for every length: top L2 0.76/0.76, L3 0.72/0.73; us L2 0.61/0.54, L3
  0.47/0.48.
- Same-direction (feeder is behind or beside, facing the same way) is worst for us: L3 0.36, L4+
  0.31.
- **So orientation isn't a lever; distance and leaks are.**

**Leaks to our own allies** (deliberate deaths within 3 of the king):
- Share of the drop eaten by another ally within 25 rounds: 0.38 for us (L3 head-on: 125 to the
  king vs 121 to allies), 0.23 for top.
- The eaters are L2 (38%), L3 (28%), L7+ (20%), i.e. queued feeders and passers-by. Only 32% of
  them later die near the king (top 48%).
- Bursts (another near-king feed death in the previous 3 rounds): us 0.46 yield / 0.44 to allies;
  top 0.67 / 0.26. Solo: 0.52 / 0.30 vs 0.62 / 0.20.
- Both teams burst equally often (about 5 per game). **We lose the burst pearls to our own
  queue.**

**Corpse parity.** A death drops ⌈L/2⌉ pearls, so the best possible yield per length is L2 0.50,
**L3 0.67**, L4 0.50, L5 0.60. Splitting an even-length feeder into L3s gains 1 pearl per 6
length. That is small; it's noted only because P4 might as well prefer odd lengths.

### 3.4 King deaths late (all games, `kingdeath.py`)
Deaths of the team's longest dragon (L≥10) from r400: us 0.08 per game (8 rammed at distance 1,
5 voluntary, 2 other); top 0.05. On known maps this is small now (KING_ESCAPE and V2 keep
distance). It matters more once P1 creates kings on unknown maps against a swarm (g12, g28).

## 4. Design: a map-agnostic endgame

Principle: use only signals every dragon has on any map.
- round
- `UNIT_COUNT` (identical for all our dragons each turn, so a memoryless team-wide schedule is
  possible)
- own length
- what is in the 7×7 view
- the king beacon

**Schedule** (defaults, to be swept):

| rounds | king candidates | everyone else |
|---|---|---|
| < seed (250, or 180 when `units >= 48`) | nobody | split at 4 as now |
| seed-300 | up to 2 candidates declare (V2: p=0.02 per turn, len ≥3, fewer than 2 fresh kings heard); they stop splitting, keep 3-4 from enemy heads, and U-turn-split only to escape | split at 4 until 350; ≤5 until 450 (LATE_SPLIT, unchanged) |
| 300-440 | king eats spawns plus **L2-3 feeders, one at a time** (P2), only while `units > reserve(round)` | queue ≥3 from the king; ignore pearls within 2-3 of the king head (P2) |
| 380-440 | | L≤6 may feed (as V2 now) |
| 440-490 | | **sweep (P4)**: any length feeds if `dist + 4 <= 497 - round`; reserve steps down to 3 |
| 470-500 | king and #2 widen the keep radius by 2 and ban blind portal steps (P5) | |

**Reserve schedule** (memoryless, same for all dragons):
`reserve(r) = max(RES_MIN, RES_HI - (r - 300) * (RES_HI - RES_MIN) / (490 - 300))`, with
`RES_HI=14`, `RES_MIN=3`.
- A dragon may feed only if `units > reserve(round)`.
- The top teams' units are 24 at r400, 12 at r450 and 6 at r500. This schedule allows 14 → 8 →
  3.
- Starving teams (units < 8) feed almost only in the last 30 rounds. That is right for them:
  they need the bodies to survive, and a small king at the end is enough to win 5 vs 3.

**How a feeder dies** (P2):
- Target the king's forward tiles `(1,0)`, `(2,0)`, `(0,±1)`, `(1,±1)` (the top teams' cells).
- Die only at `dk ≤ 2`, or at `dk = 3` when every corpse pearl tile (head and every second body
  segment the dragon knows) is within 3 of the king head. Never behind the king.
- Hold while any pearl lies within 2 of the king head, in front or beside it, and for at most 6
  rounds.
- Hold while another eligible ally head in view is closer to the king (tie → lower id).
- The kill move stays "step into own neck" (HitSelf), which keeps the pearls on the current body.

**Protecting the king:**
- The V2 keep-distance penalty and KING_ESCAPE already exist.
- P1's unit reserve keeps the swarm, which is the king's real protection: rams come from enemies
  that roam freely once we have fed our units away.
- P5 adds the r470+ caution.
- `tryRam` already skips kings in feed phase.

## 5. Proposals

### P1 `UNK_KING` (map-agnostic crown plus reserve schedule). Value: highest for unseen maps.
- **Where:** `Bot::analyse` next to the `UNK_SIZE_PARAMS` block (main.cpp ~761); `shouldFeed()`;
  params.hpp.
- **Sketch:**
```cpp
// params.hpp
#ifndef UNK_KING
#define UNK_KING 0
#endif
#ifndef UNK_KING_SEED        // candidates may declare from this round
#define UNK_KING_SEED 250
#endif
#ifndef UNK_KING_SEED_RICH   // ...or this round once the team is near the unit cap
#define UNK_KING_SEED_RICH 180
#endif
#ifndef UNK_KING_FEED
#define UNK_KING_FEED 300
#endif
#ifndef FEED_RES_HI
#define FEED_RES_HI 14
#endif
#ifndef FEED_RES_MIN
#define FEED_RES_MIN 3
#endif

// analyse(), after the UNK_SIZE_PARAMS block:
if (UNK_KING && !w.known && w.candidates.empty())
{
    if (!unkParamsSet)
    {
        unkParamsSet = true;
        RP.kingDeclare = 1;                 // KING_V2 path: 2 candidates, bigLate, keep-distance
        RP.kingSeedRound = UNK_KING_SEED;
        RP.feedStart = UNK_KING_FEED;
        RP.feedReserve = FEED_RES_MIN;      // the round schedule below does the real work
        // splitStopRound stays SPLIT_STOP_ROUND (350) and LATE_SPLIT stays on: we need the swarm
    }
    if (units >= 48 && RP.kingSeedRound > UNK_KING_SEED_RICH)
        RP.kingSeedRound = UNK_KING_SEED_RICH;  // rich map: kings emerge early (notes/11: r130-230)
}

// shouldFeed(), V2 branch: replace `units > RP.feedReserve` by `units > feedReserveNow()` when UNK_KING || FEED_QUEUE
int feedReserveNow() const
{
    if (!(UNK_KING && !w.known)) return RP.feedReserve;
    int r = std::clamp(round, 300, 490);
    return std::max(FEED_RES_MIN, FEED_RES_HI - (r - 300) * (FEED_RES_HI - FEED_RES_MIN) / 190);
}
```
- **Evidence:**
  - 23/46 local unknown round-limit team-games ended with a king ≤7 (§2.2).
  - Blind Portals/Trauma/QoS: 4-7 on every seed, vs top-10 kings of 31-42 on the same maps.
  - The declared king won g23 37 v 18, and lost g12/g28 only through unit collapse (§2.3).
- **Expected effect:**
  - Against real (king-building) opponents on unseen maps, it turns a certain tiebreak loss into
    a race in about half of round-limit games. That is the largest endgame lever for the
    tournament.
  - Against v24 in self-play: modest (+0.03 to +0.08 pooled unseen). Round-limit games with a
    surviving king are won by big margins, and the reserve stops the g12 collapse. Elimination
    maps are unchanged, since it is inactive before r250 or r180.
- **Risks:**
  - Kings rammed by v24's swarm. Mitigated by the reserve, P2 and P5.
  - Candidate stop-splitting reduces the r250-350 harvest a little (2 dragons only).
  - On maps recognised late (`w.candidates` non-empty), it doesn't fire.
- **Test:**
  - `unseen_eval.py "bot:-DUNK_KING=1 -DFEED_QUEUE=1 -DFOOD_RESERVE=2"` vs v24, sets
    gen,blind,lesson, plus holdout at the end. Ladder should be exactly 0.50: known maps are
    untouched.
  - Mechanism metrics with `notes/unseen/tools/localking.py` on saved replays (`arena.py
    --replays`):
    - (a) share of round-limit team-games with longest ≤7 at r500: expect ≈0.5 → <0.15;
    - (b) median longest at r500;
    - (c) elimination losses after r300: must not rise;
    - (d) units at r420 for the king side.
  - Sweep `UNK_KING_SEED` ∈ {200, 250, 300} and `FEED_RES_HI` ∈ {10, 14, 18}.
  - **Best real test:** a server A/B with a *blind* build (`-DNO_KNOWN_MAPS=1`) of v24 vs v24+P1+P2
    on Portals/Trauma/Default/Schooltime against the usual 10 peers. The ranked maps become
    "unseen" and the opponents are real king-builders. This needs the user's OK, because it
    means temporarily submitting a blind build.

### P2 `FEED_QUEUE` + `FOOD_RESERVE` (one feeder at a time; don't eat the king's food). Value: high (prerequisite for P1; ladder gain).
- **Where:** the KING_V2 feeding block at the top of `decide()` (main.cpp ~2259-2295);
  `pearlValue()` (~970).
- **Sketch:**
```cpp
#ifndef FEED_QUEUE
#define FEED_QUEUE 0
#endif
#ifndef FOOD_RESERVE      // radius (Manhattan) around a fresh king head that subordinates don't eat
#define FOOD_RESERVE 0
#endif
int feedHoldSince = -1;   // Bot member

// decide(), KING_V2 block, after dieNow is computed:
if (FEED_QUEUE && dieNow)
{
    int k = kingTile, f = kingDir;
    // (a) the king still has food in front of or beside it: wait (max 6 rounds)
    bool food = false;
    for (int i = 0; i < 49; i++)
    {
        int t = w.idx(in.tx[i], in.ty[i]);
        if (!w.pearlMem[t] || wrapDist(t, k) > 2) continue;
        int fx = /* forward component of t - k along f, wrapped */;
        if (fx >= 0) food = true;
    }
    if (food && (feedHoldSince < 0 || round - feedHoldSince <= 6)) { if (feedHoldSince < 0) feedHoldSince = round; dieNow = false; }
    // (b) another small ally head in view is closer to the king: it goes first
    int myKey = wrapDist(myHead, k) * 1024 + (w.myId & 1023);
    for (auto& o : segs)
        if (o.head && o.team == w.myTeam && o.id != w.myId && (o.id & 1023) != (kingId & 1023) &&
            enemyVisibleLength(o.id) + 2 <= kingLen && wrapDist(o.tile, k) <= 3 &&
            wrapDist(o.tile, k) * 1024 + (o.id & 1023) < myKey)
            dieNow = false;
    // (c) no d4 deaths: pearls further than 3 from the king head reach it < 30% of the time
    if (wrapDist(myHead, k) > 3) dieNow = false;
    if (dieNow) feedHoldSince = -1;
}

// pearlValue(), first line:
if (FOOD_RESERVE > 0 && kingId >= 0 && kingTile >= 0 && round - kingRound <= 2 && feedPhase() &&
    !iAmKing() && kingLen >= myLen + 2 && wrapDist(t, kingTile) <= FOOD_RESERVE)
    return 0; // the king's food
```
- **Evidence** (§3.3):
  - Near-king deliberate deaths: yield 0.48 vs 0.67. 0.38 of the drop goes to our other dragons
    (top 0.23); bursts 0.46 / 0.44 to allies.
  - d4 deaths reach the king 29% of the time. The loose rule puts a lot of our drop there.
  - g12: 32 feed deaths in 50 rounds.
- **Expected effect:**
  - Ladder: +3-5 king pearls per round-limit game (near-king drop about 17 per game × a
    0.48 → 0.62 yield gain, minus recycling).
  - Fewer wasted feeders, so more units survive for P4.
  - Needed so that P1 doesn't collapse the swarm.
- **Risks:**
  - The throttle slows feeding if the king parks next to a pearl it doesn't want. Hence the
    6-round cap and the front-and-side-only check.
  - The tie-break may starve feeding if a non-feeding small ally loiters within 3 of the king.
    It may be better to count only allies inside the king's forward half.
  - `KING_V2_LOOSE=1` was part of the accepted v8 package, not tested alone. Keep LOOSE and add
    the queue on top.
- **Test:**
  - Ladder `pool.py` vs v24 (the flag is active on 8/10 ranked maps) plus unseen with P1.
  - Mechanism: rerun `feedeff.py` on server A/B replays. Near-king yield should rise and the ally
    share fall.
  - Also a server batch on Schooltime/Slithery/Portals/Autarky, where king races decide games.

### P3 `KING_NET` (standing, age-limited relay). Value: medium-high (conversion; ladder and unseen).
- **Where:** `readMessages()` king-message loop (~1543-1592); `emitSonar()` (unchanged apart from
  using `relayMsg`).
- **Sketch:**
```cpp
#ifndef KING_NET
#define KING_NET 0
#endif
#ifndef KING_NET_AGE
#define KING_NET_AGE 6
#endif
// in the loop: accept older news
if (round - rnd > (KING_NET ? KING_NET_AGE : 4)) continue;
// relay regardless of hop (hop saturates at 3); freshness is bounded by the carried round
if ((KING_NET || hop < KING_RELAY_HOPS) && hop < bestHopRelay + (KING_NET ? 4 : 0) && id == (kingId & 1023)) { ... encodeKing(tile, len, id, std::min(hop + 1, 3), dir, rnd) ... }
// after the loop: standing relay, i.e. keep re-broadcasting the king we know
if (KING_NET && !haveRelay && kingId >= 0 && kingTile >= 0 && round - kingRound <= KING_NET_AGE && !iAmKing())
{
    relayMsg = encodeKing(kingTile, kingLen, kingId & 1023, 3, kingDir, kingRound);
    haveRelay = true;
}
```
(`kingRound` becomes the current round when we see the king ourselves, so the relay stays fresh
near the king.)
- **Evidence** (§3.1-3.2):
  - 39-41% of our L2-3 dragons late in the game were not hit by any own ray in 8 rounds (top
    11-25%).
  - Unconverted L2-7 length at r500: 25.3 vs 8.8 per game, a median 20 tiles from the king.
  - The top teams ping from about 90% of their dragons.
- **Expected effect:** +3-6 king length in round-limit games (more small dragons reach the king
  in r400-490). With P4 the gain lands in the last 60 rounds.
- **Risks:**
  - More feeders converge, so this needs P2.
  - More rays pollute `PORTAL_ECHO_GUARD` echo counts. Probing turns already skip relays
    (`PORTAL_PROBE_SOLO`), and body counts are zeroed when other rays are out.
  - Legacy path (unknown maps without P1): `FEED_MAX_LEN=1000` lets *any* length feed from r330,
    so wider reach also spreads the bad legacy merges. **Enable only together with P1** on
    unknown maps.
- **Test:**
  - Ladder pool plus unseen (with P1 and P2).
  - Mechanism: `reach.py` share (target ≥0.8 for L2-3 at r430) and `leftover.py` L2-7 length at
    r500 (target <15), on server A/B replays.

### P4 `FEED_REACH` (endgame sweep by time-to-reach). Value: medium.
- **Where:** `shouldFeed()`; the feed pull in the candidate loop.
- **Sketch:**
```cpp
#ifndef FEED_REACH
#define FEED_REACH 0
#endif
#ifndef FEED_REACH_ROUND
#define FEED_REACH_ROUND 440
#endif
// shouldFeed(), before the V2 branch:
if (FEED_REACH && RP.kingDeclare && round >= FEED_REACH_ROUND && kingId >= 0 && kingTile >= 0 &&
    round - kingRound <= 8 && kingLen >= myLen + 2 && !iAmKing() && !kingSelf)
{
    int reserve = std::max(FEED_RES_MIN, RP.feedReserve - (round - FEED_REACH_ROUND) / 15);
    int need = wrapDist(myHead, kingTile) + 4;           // walking plus queueing
    if (units > reserve && need <= 497 - round)
        return true;
    if (need > 497 - round)
        return false;                                     // can't make it: stay alive (tiebreak 2 = total length)
}
```
- Optional: an even-length feeder of 6+ within 4 of the king does `SPLIT 3` once, so both halves
  die as odd lengths. This is +1 pearl per 6 length, and the lowest priority part.
- **Evidence:**
  - The top teams' own-corpse king eats in r400-499 are 17.0 per game vs our 10.9.
  - L4-7 leftover at r500 is 15.9 vs 6.2.
  - A far dragon that can't arrive by r497 is worth more alive (total-length tiebreak and
    insurance) than dead on the way.
- **Expected effect:** +2-4 king length. It also stops pointless late suicides far from the king
  (our "deliberate deaths with 0 king pearls" are 65 per game vs 35, most of them pumps, but
  some are late).
- **Risks:**
  - A sweep lowers units in the last 50 rounds. The reserve schedule and P5 cover that.
  - Earlier tests of `KING_V2_MERGE_ROUND` 460/1000 were 0.45: moving the merge round alone
    hurts. This changes *who* merges (reachable ones), not *when*.
- **Test:** ladder pool plus unseen (with P1-P3); `leftover.py` and `feedeff.py` king-curve
  r450→r500.

### P5 `KING_LAST_STAND` (final-rounds caution). Value: low-medium (cheap insurance).
- **Where:** the KING_V2 keep-distance block in the candidate loop (~2402); the blind-portal
  penalty line (~2427).
- **Sketch:**
```cpp
#ifndef KING_LAST_STAND
#define KING_LAST_STAND 0
#endif
// keep block:
int keep = (myLen >= 15 ? 4 : 3) + RP.kingKeepExtra + ((KING_LAST_STAND && round >= 470) ? 2 : 0);
// blind portal step for the king or a candidate after r470:
if (KING_LAST_STAND && round >= 470 && (kingSelf || myLen >= 8) && !visible[t] && t != w.plainStep(myHead, d))
    score -= 1000.0;
```
- **Evidence:**
  - g2026_28: the L9-11 king was rammed at r498 by an L4 and the game was lost 5 vs 6.
  - Ladder: longest-dragon deaths from r400 are 0.08 per game (8 of 15 rammed at distance 1).
  - notes/16: blind crossings into allies killed 0.11 kings per game before the portal fixes.
- **Expected effect:** small on the ladder (about 0.03 games per game). Larger for P1 kings on
  unknown maps, which live among swarms.
- **Risk:** a more timid king eats less in the last 30 rounds (about 1-2 pearls).
- **Test:** only in combination with P1. Count longest-dragon deaths from r450 with
  `kingdeath.py` on the unseen replays.

## 6. Rejected or deprioritised ideas (and why)
- **Head-on feeder approach** (feeder faces the king so its body lies along the king's path):
  orientation made no measurable difference for L2-3 (§3.3). It only matters for L7+ merges,
  which are about 5% of feeders.
- **King-announced feed spot via beacon bits** (the king sends its planned tile 2 moves ahead):
  would need to steal round or checksum bits. The data says distance ≤3 already gives
  0.55-0.76, so the gain over P2 is small.
- **Candidate choice by eat rate** (dragons that eat fastest declare): plausible, since the top
  kings sit 1-4 tiles from rich tiles, but our spawn eats already match the top-10's (12.9 vs
  9.0 r350+). Try after P1 if kings form in poor spots.
- Not re-proposed: `UNK_SIZE_PARAMS` (see §2.3 for why P1 differs), `FEED_FRESH` (rare, 0.03
  per game), `KING_V2_MERGE_ROUND` changes.

## 7. Caveats
- Ladder samples: 92 us / 45 top round-limit team-games. The map mix differs (ours is heavy on
  Default/Schooltime).
- Local unknown-map evidence is one seed per map (three on blind Portals/Trauma) and self-play
  only.
- The 3 `UNK_SIZE_PARAMS` games are mechanism illustrations, not a win-rate measurement.
- "Hit by an own ray" in `reach.py` is an upper bound on hearing the king. The real gap is
  probably larger, since some rays are portal warnings.
- Self-play (`unseen_eval.py` vs v24) under-rewards P1: the baseline has no king to race.
  Weight the mechanism metrics (king ≤7 share, elimination losses) at least as much as the win
  rate, and prefer a blind server A/B if the user allows it.
