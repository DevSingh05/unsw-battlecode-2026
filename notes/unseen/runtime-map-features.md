# Runtime adaptation to map features (track: runtime-map-features)

28 Sep 2026. Read-only study; no games run. Question: on an unseen map (`w.known == nullptr`) the bot uses
the global `RuntimeParams` defaults. Which map features can a dragon measure at runtime, which per-map choices
in `applyMapParams()` follow from them, and what small rule set should unseen maps get instead?

Scripts (read-only, light CPU):
- `notes/unseen/tools/map_features.py maps/*.map`: static features of any .map, split into whole-map truth and
  what team A's dragons see at round 0 (`v_*` columns). `--csv` for a table.
- `notes/unseen/tools/contact_by_map.py notes/replays/top10b 4`: per map, the share of a team's dragons with a
  reachable enemy head (walking distance <= 3 through kelp/portals, and inside the 7x7 view) per round window,
  plus winner unit curves. Used on the 85 top-10 games from notes/16 (16 s).

## 1. Short answer

1. **The unseen-map default is the minority row of the table.** Unknown maps run `KING_DECLARE=0`, which is
   the setting of only Devil and Trophy. The other 8 ranked maps all run `kingDeclare=1`, 5 of them with the seed
   round in 330-380. On Devil and Trophy, top games end by elimination at a median of r137/r165. A king seeded
   at r350 is then close to a no-op there (section 4.1). So the median row (KD=1, KS=350, FS=330, SS=350,
   reserve 4) is a better unseen default than the Devil/Trophy row. No feature is needed for that.
2. **King timing is the only per-map choice that clearly follows a measurable feature.** Early kings
   (seed 170-250) are right on maps where dragons rarely meet enemies (Trauma, Slithery, Portals: <=2.5% of
   dragon-turns have a reachable enemy head within 3) or where the board is huge (Schooltime, 2400 tiles).
   Everything else uses about 350. A dragon can measure "I have not had an enemy head within reach for N turns"
   by itself, with no sonar. The team-wide "units at the cap" signal (UNIT_COUNT vs UNIT_LIMIT) marks the
   same maps: top winners hit the cap on Slithery by r100 and Schooltime by r125, and have a >=10 king by
   r112/r140.
3. **Ram guard follows board size.** On the three small contact maps (Devil 512, Dilemma 512, Trophy 625),
   guard=1 was bad (0.25 on Devil/Trophy) and weaker guards won. On the three medium maps (QoS 875, Autarky 972,
   Default 1024), guard=1 won at 0.75-0.79. Rule: `N <= 750 -> ramGuard = 2` (local odds only).
4. **Crowding penalty follows dead-end density, not portals or size.** crowd=3 helped on Schooltime, Portals,
   Trauma and QoS, was neutral on Slithery, and hurt on Devil and Dilemma. Dead-end tiles (one open side) are
   1.8-9.8% of tiles on the maps where it helped, 1.9% on Slithery, and <=0.8% on every map where it hurt or
   was not used. A dragon sees every edge of its 7x7 view, so it can count dead ends locally.
5. **Pearl features, starting count, starting length and portal count predict nothing in the table.**
   Hot-tile maps (hot share >= 0.9) include both elimination maps (Devil, Dilemma) and pure growth maps (Portals,
   Slithery), so no rule is built on them.
6. **Test-set warning.** `maps/gen` is 72% boards of <=750 tiles and only 6/40 are >=1500 (genhold 11/40, lesson
   4/24). A change that only fires on big boards is diluted 5-7x in the pooled unseen score. This is the likely
   reason UNK_SIZE_PARAMS read as "neutral" (section 4.2). Evaluate each rule on the subset where it fires and
   check that play is byte-identical elsewhere.

## 2. What a dragon can measure, and when

| feature | available | shared how | notes |
|---|---|---|---|
| W, H, N = W*H | init block, every process (children too) | free | exact |
| UNIT_LIMIT | init block | free | exact; ranked maps all 64 |
| units (own team) | every turn, `UNIT_COUNT` | free, team-wide truth | the only free team-wide dynamic signal |
| round | every turn | free | |
| own start length / start count | round 0 only, original dragons | not to children | Dilemma/Autarky/Slithery start long (11/14/25) |
| kelp / dead ends / corridors in view | every turn: all 4 edges of all 49 view tiles are in the input | local | exact for the view; map-level needs memory (children start blank) |
| portals in view | every turn | local | destination unknown on unseen maps |
| pearl tile density, countdowns | every turn (`pearlIn`, -1 = barren) | local | a round-0 countdown is a draw from U[min,max] |
| enemy heads within reach | every turn (vision + `threatDist` BFS) | local | walls handled by BFS |
| enemy presence at range | ECHOES (only on rays we send) | local | direction-ambiguous totals |

Children are separate processes with no map memory, and 70-90% of dragons at any time are children
(median feeder age is 20-47 rounds, notes/11). Any rule should therefore depend on (a) N, UNIT_LIMIT, units and
round, which every dragon knows exactly, or (b) the dragon's own recent view. Then no sonar is needed and every
dragon agrees without coordination. None of the proposals below needs new sonar messages.

## 3. The ranked maps: features vs the live choices

Static features (`map_features.py`; hot = gmax <= 10; dead = tiles with exactly 1 open side;
startDist = walking distance from an A head to the nearest B segment):

| map | N | starts/team (max len) | kelp | portal pairs | dead % | pearls/round | hot share | startDist | top-game elim % | live KD / KS / SS / FS | crowd | ram guard |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Devil | 512 | 3 (4) | .24 | 0 | 0 | 19.6 | .92 | 31 | 71-100 | 0 / - / 350 / 330 | 0 | 2 (was 0) |
| Dilemma | 512 | 3 (11) | .13 | 8 | 0.8 | 12.3 | .98 | 5 | 75 | 1 / 350 / 350 / 330 | 0 | 2 |
| Portals | 512 | 3 (3) | .28 | 40 | 9.8 | 25.5 | 1.0 | disconnected | 0 | 1 / 250 / 360 / 300 | 3 | 1 (moot) |
| Trophy | 625 | 2 (3) | .07 | 2 | 0.2 | 2.4 | 0 | 7 | 100 | 0 / - / 350 / 330 | 0 | 0 |
| QoS | 875 | 2 (3) | .17 | 4 | 1.8 | 2.1 | 0 | 24 | 71-90 | 1 / 330 / 420 / 400 | 3 | 1 |
| Autarky | 972 | 6 (14) | .11 | 16 | 0.4 | 10.4 | .93 | 5 | 50-67 | 1 / 380 / 350 / 330 | 0 | 1 |
| Default | 1024 | 4 (4) | .11 | 24 | 0 | 1.6 | 0 | 2 | 30-42 | 1 / 350 / 350 / 330 | 0 | 1 |
| Trauma | 1152 | 2 (4) | .25 | 12 | 3.3 | 13.3 | .90 | 98 | 0 | 1 / 450* / 350 / 330 | 3 | 1 |
| Slithery | 1701 | 7 (25) | .15 | 4 | 1.9 | 60.0 | .99 | 3 | 0 | 1 / 170 / 370 / 250 | 0 (3 was neutral) | 1 |
| Schooltime | 2400 | 3 (4) | .19 | 24 | 2.3 | 7.6 (3.1 layout B) | 0 | 6 | 14-20 | 1 / 200 / 340 / 260 | 3 | 1 |

\* Trauma's 450 serves the Trauma factory module. notes/08's module-free recommendation was 275, and top
winners reach a length-10 king at r307.

Runtime contact (`contact_by_map.py`, 85 top-10 games from notes/16, both teams): the share of dragon-turns with
a reachable enemy head within 3.

| map | r1-50 | 51-100 | 101-200 | 201-300 | 301-400 | winner units r100 / 150 / 200 | winner longest >= 10 at (notes/08) |
|---|---|---|---|---|---|---|---|
| Portals | 0 | 0 | 0 | 0 | 0 | 24 / 34 / 33 | 374 |
| Trauma | 0 | 0 | 1.1 | 2.0 | 0.7 | 24 / 36 / 37 | 307 |
| Slithery | 2.7 | 3.5 | 2.5 | 1.9 | 2.4 | **61 / 63 / 64** (cap) | **112** |
| Autarky | 11.9 | 15.3 | 9.3 | 6.3 | 4.4 | 24 / 41 / 44 | ~400 |
| Devil | 14.6 | 11.8 | 7.4 | 6.2 | 10.1 | 21 / 36 / 36 | never |
| Schooltime | 7.3 | 5.9 | 9.0 | 10.2 | 7.6 | 33 / 34 / 41 (cap by 125 in notes/08) | **140** |
| QoS | 2.7 | 7.5 | 11.4 | 15.4 | 10.8 | 12 / 16 / 22 | (late) |
| Dilemma | 26.5 | 17.1 | 14.6 | 8.9 | 1.3 | 12 / 12 / 25 | 215 |
| Default | 10.4 | 8.6 | 15.3 | 14.0 | 9.2 | 18 / 26 / 34 | 385 |
| Trophy | 8.7 | 18.5 | 21.8 | 21.9 | 26.5 | 34 / 45 / 49 | never |

(Chebyshev-in-view alone is misleading: Portals shows 35-67% "contact" across the dividing kelp. Use walking
distance, i.e. the bot's own `threatDist`.)

### Reading the table, rule by rule

**KD (build a king at all).** 8/10 yes. The two "no" maps are the fastest eliminations (median r137 Devil,
r165 Trophy). Before `kingSeedRound`, KD=1 with V2 changes only one thing: dragons of length >= 10 keep 3-4
tiles from enemy heads (`decide()`, the `KING_V2 && RP.kingDeclare && (kingSelf || myLen >= 10)` block). That
is the top teams' rule anyway (notes/11: winners' kings spend 0-3% of time within 3 of enemy heads). Verdict:
**map-invariant, set KD=1 on unseen maps.**

**KS (seed round).** Values: 170 (Sli), 200 (Sch), 250 (Por), 330 (QoS), 350 (Def, Dil), 380 (Aut),
450/275 (Tra). They sort into two groups:
- early (170-275): Slithery, Schooltime, Portals, Trauma. These have contact <= 2.5% (Por/Tra/Sli), or N >= 1500
  (Sch/Sli), or the team at the unit cap by r100-125 (Sli/Sch).
- about 350: everything with contact >= 6% and N <= 1024.

No map has low contact and a late seed. Autarky is the borderline case: contact falls to 4-6% after r200, and
it is still 380. So a quiet-based rule must use a strict threshold, and the r350 fallback keeps Autarky
unchanged. **Feature-driven: contact / saturation / size -> early seed, else 350.**

**FS (feed start) and SS (split stop).** Across the V2 rows, FS = KS + 50..80 (Sch 200->260, Sli 170->250,
Por 250->300, QoS 330->400). SS is 340-420 regardless of KS, and LATE_SPLIT_ROUND=450 already keeps small
dragons splitting. **FS follows KS (FS ~ KS + 70); SS is map-invariant (keep 350).**

**Feed reserve.** 3-4 everywhere. **Map-invariant (keep 4).**

**Ram guard.** Small contact maps (<= 625) want a weaker guard: Devil/Trophy 0.25 with guard=1, Devil local
guard 0.70/0.58, Dilemma local 0.50. Medium maps (875-1024) want guard=1 (0.75-0.79). There is no ranked map
between 625 and 875, so any threshold in that gap fits. Mechanism: guard=1 refuses even trades while
`units < RAM_MIN_UNITS (8)`. Maps that start with 2-3 dragons each and meet at once (Dilemma first contact r2)
decide the game inside that window. **Feature-driven by N.** Evidence: 3 maps on each side, with a clear
mechanism.

**Crowd.** Helped: Sch, Por, Tra, QoS (per-map test 0.674 vs 0.597, 144 games). Hurt: Devil, Dilemma. Neutral:
Slithery (0.53 vs 0.56). Global crowd=3 was 0.49. Portal count doesn't separate (Dilemma 8 hurt, QoS 4 helped),
and size doesn't either. Dead-end share does:
- helped: 9.8 (Por), 3.3 (Tra), 2.3 (Sch), 1.8 (QoS);
- neutral: 1.9 (Sli);
- hurt or unused: 0.8 (Dil), 0.4 (Aut), 0.2 (Tro), 0 (Dev, Def).

Mechanism: in maze-like areas nearby allies block each other's only exit (notes/09/15: trapped self-hits in
Schooltime maze rows). **Feature-driven, but only 5 maps behind it, and those tests had known portals.** Lower
confidence.

**kingPortal / kingKeepExtra / lateFeed / keepLen / escapeHotOnly.** kingPortal=100 is already global. The
others are single-map patches (Sch keep +1, Trauma late feed with its module, Dilemma keepLen rejected 0/36).
**Leave at defaults.** No feature supports generalising them.

**Things that look like features but predict nothing.** Pearl rate and hot share: Devil (elim) and
Portals/Slithery (growth) are all hot-share ~1. Starting length: long starters on Dilemma (elim), Autarky
(mixed) and Slithery (growth), and keeping them long was rejected (PM_DIL_KEEP 0/36). Start count: 2-7 with no
pattern. Kelp density: Devil .24, Trauma .25, Portals .28 span all classes. Round-0 pearl view (`v_rate1k`):
noisy, and it doesn't separate classes either.

## 4. Why earlier related attempts don't settle this

### 4.1 KD=1 on Devil/Trophy-like maps
It was never tested directly: PM_DEVIL_KD / PM_TROPHY_KD were set from notes/08's advice. The g2 run (per-map
KING_DECLARE seeds + ram guard, 0.650 vs 0.531 for ram guard alone, v6) is the only evidence that per-map KD=1
helps. It is confounded with the seed values, but +0.12 over 10 maps is large. The risk on combat maps is small
because the seed round is after most eliminations.

### 4.2 UNK_SIZE_PARAMS was "neutral" (0.475 / 0.525 / 0.488)
It set KD=1, KS=250, SS=360, FS=300 only for N >= 1000. That touches 8/40 gen maps, 4/10 blind maps (Default,
Trauma, Slithery, Schooltime) and 12/24 lesson maps. Two of those 8 gen maps have pearl rate ~0, where no king
can grow. So even a real +0.10 on the maps it touches is about +0.02 pooled, far below what 80-160 games can
detect. It also applied KS=250 to Default (1024, contact 9-15%), where the tuned value is 350, so part of the
blind set got a worse setting. It says nothing about KD=1 at KS=350 and little about early kings on truly big
or quiet maps. **Do not read it as "king timing doesn't matter on unseen maps".**

### 4.3 Things not re-proposed
LEARN_PORTALS, INFER_SYM, PEARL_DISTRUST, UNK_PRIOR, EAT_SPRINT, PORTAL_ALLY_COST, SMALL_SPRINT_THREAT and
KEEP_LEN are all outside this track's rules. Nothing below touches pearl priors, portals or sprinting.

## 5. Proposed rules (all gated on `!w.known`, so ladder play is identical)

All values are set once per process in one new function `applyUnknownParams()`. It is called where the
UNK_SIZE_PARAMS block sits (main.cpp ~761): `if (!w.known && !unkParamsSet)`. `adopt()` still resets RP
through `applyMapParams()` if a child later identifies a known map, so known maps are never affected. Per-turn
parts (quiet counter, dead-end EMA) live in the analysis step.

### P1. UNK_KING_BASE: the median ranked row on unseen maps (highest value per effort)
```cpp
// params.hpp
#ifndef UNK_KING_BASE
#define UNK_KING_BASE 0
#endif
#ifndef UNK_BASE_KS
#define UNK_BASE_KS 350
#endif
// main.cpp, applyUnknownParams()
if (UNK_KING_BASE) {
    RP.kingDeclare = 1;
    RP.kingSeedRound = UNK_BASE_KS;   // Default/Dilemma row; QoS 330, Autarky 380
    // SS 350, FS 330, feedReserve 4 stay at the globals (same as the Default/Dilemma rows)
}
```
- Evidence: 8/10 ranked maps use KD=1; KS=350 is the median of the non-early rows; g2 +0.12 (confounded).
  On the 2 KD=0 maps the games end before r350.
- Expected: on unseen maps that reach r500 (most maps above ~900 tiles), a protected candidate from r350, V2
  feeding rules, and big-dragon keep-away from enemy heads. Wins on longest-dragon tiebreaks. Near-zero effect on
  fast elimination maps.
- Risk: the V2 feed branch keeps `units > feedReserve` and caps feeder length at 3 until r380 (non-V2 allowed
  any length). This is the same code that runs on Default/Dilemma now, so it is well exercised.

### P2. UNK_EARLY_KING: seed early when the dragon is quiet or the team is saturated (needs P1)
Two triggers. The flag value selects them: 1 = quiet, 2 = saturation, 3 = both.
```cpp
// params.hpp: UNK_EARLY_KING 0, QK_ROUND 170, QK_QUIET 50, QK_RADIUS 4, SAT_ROUND 110, SAT_MARGIN 2, QK_FEED 260
// member state
int lastContactRound = -1, bornRound = -1;
// per turn, after computeThreats() (or in analyse(); needs step() only):
if (bornRound < 0) bornRound = round;
if (!w.known && UNK_EARLY_KING) {
    // walking BFS <= QK_RADIUS from my head; any visible enemy head reached = contact
    if (enemyHeadWithin(myHead, QK_RADIUS)) lastContactRound = round;
}
// updateKingship(), V2 branch, replace the seed test:
int seed = RP.kingSeedRound;
if (!w.known && RP.kingDeclare) {
    int quietFor = round - std::max(lastContactRound, bornRound);
    if ((UNK_EARLY_KING & 1) && quietFor >= QK_QUIET) seed = std::min(seed, QK_ROUND);
    if ((UNK_EARLY_KING & 2) && units >= w.unitLimit - SAT_MARGIN) seed = std::min(seed, std::max(SAT_ROUND, round));
}
if (round >= seed && freshKings(-1) < 2 && myLen >= 3 && rng.uni() < KING_DECLARE_P) kingSelf = true;
// feedPhase(): feed starts early behind an early king that is actually growing
bool feedPhase() const {
    if (!w.known && UNK_EARLY_KING && kingId >= 0 && kingLen >= 12 && round >= QK_FEED) return true;
    return round >= RP.feedStart;
}
```
- Evidence: in top games, the maps with <= 2.5% reachable contact (Portals, Trauma, Slithery) all get tuned
  seeds of 170-275, and their winners' kings grow early. Saturation marks Slithery (61 units at r100) and
  Schooltime (cap by 125), whose winners reach L10 at r112/r140. Autarky, Default, Devil, QoS, Dilemma and
  Trophy run at 4-27% contact and never saturate in the top10b sample, so they stay at 350. Per dragon,
  "quiet >= 50 turns" also picks *where* to grow a king: the notes/11 winners' kings keep >= 4 from enemy heads
  0-3% of the time.
- The quiet trigger is per dragon, so only dragons in safe pockets volunteer. The `freshKings(-1) < 2` cap and
  sonar step-down (V2) still limit the team to 2 candidates. No new sonar is needed.
- Expected: king >= 10 by about r250 instead of about r400 on quiet or saturated unseen maps. That is worth the
  tiebreak on growth maps (top vs us final king 36 vs 28, notes/16).
- Risk: early candidates stop splitting and lose harvest heads. On a map that turns violent later (contact
  rising after r200), an early king is a target. KING_ESCAPE and the keep-away help. Watch for more L>=10
  deaths.

### P3. UNK_SMALL_RAMGUARD: local-odds ram guard on small boards
```cpp
// params.hpp: UNK_SMALL_RAMGUARD 0, UNK_SMALL_N 750
if (UNK_SMALL_RAMGUARD && w.N <= UNK_SMALL_N) RP.ramGuard = 2; // drop the units<8 gate, keep local odds
```
- Evidence: Devil and Trophy lost with guard=1 (0.25); Devil local=2 won 0.70/0.58; Dilemma local=2 0.50.
  Medium maps won with guard=1 (0.75-0.79). The unused gap is 625-875, so 750 sits in the middle.
- Fires on 29/40 gen, 21/40 genhold, 7/24 lesson (brawl_a/b, rush_a, famine_a, fountain_a, pockets_a,
  vault_a), and 4/10 blind (Devil, Dilemma, Trophy, Portals).
- Expected: more early even trades while the team is still at 2-7 units on crowded boards, where top winners
  convert a unit lead into elimination (Trophy 30 vs 9 at r100). Small but broad.
- Risk: more even trades when behind on units globally (the local-odds check stays). `RAM_GUARD_LOCAL=2`
  (global) was never measured, so it is untested on medium maps. The size gate keeps those unchanged.

### P4. Re-test the existing UNK_SIZE_PARAMS with Schooltime/Slithery values (no code)
`-DUNK_SIZE_PARAMS=1 -DUNK_BIG_TILES=1500 -DUNK_KS=190 -DUNK_SS=350 -DUNK_FS=260` (plus P1). This is a
size-only fallback in case P2's triggers misfire. Judge it on the >=1500-tile maps only (6 gen + 11 genhold + 4
lesson + Schooltime/Slithery blind). The earlier neutral result is explained by dilution and by KS=250 on
Default (section 4.2).

### P5. UNK_CROWD_DEADEND: crowding penalty where the dragon is in a maze
```cpp
// params.hpp: UNK_CROWD_DEADEND 0, CD_THRESH 0.7, CD_VALUE 3.0
double deadEma = 0;               // member
// per turn, after observeEdges(): count view tiles with exactly one open side
int dead = 0;
for (int i = 0; i < 49; i++) { int t = w.idx(in.tx[i], in.ty[i]); int o = 0;
    for (int d = 0; d < 4; d++) if (step(t, d) >= 0) o++;
    if (o == 1) dead++; }
deadEma = (round == bornRound) ? dead : 0.9 * deadEma + 0.1 * dead;
if (!w.known && UNK_CROWD_DEADEND) RP.crowd = deadEma >= CD_THRESH ? CD_VALUE : CROWD_PENALTY;
```
- Evidence: expected dead ends per 7x7 view (dead% x 49) are Portals 4.8, Trauma 1.6, Schooltime 1.1, QoS 0.9
  (crowd helped); Slithery 0.9 (neutral); Dilemma 0.4, Autarky 0.2, Trophy 0.1, Devil 0, Default 0 (hurt or
  unused). A threshold of 0.7 splits them.
- Expected: fewer mutual traps in mazes (maze_a/b, pockets, Loong "maze" style). Per dragon, so it adapts
  within a map.
- Risk: the evidence comes from 5 maps with *known* portals; it may not transfer. Pocket-pump maps
  (pockets_a has 48 dead ends) want allies near pockets, and the crowd penalty may fight POCKET_PUMP. Lowest
  confidence of the five.

## 6. Test plan for the main agent

Baseline: v24. Every flag is inert on known maps, so `ladder` should be byte-identical (check 1 seed, not a
full set).
1. P1 alone: `unseen_eval.py "bot:-DUNK_KING_BASE=1" --base variants/v24 --sets gen,blind,lesson`. Report per
   set. Also report the subset N >= 900 (maps that tend to reach r500); the effect should be concentrated there.
   Mechanism check: final longest at r500 in round-limit games (tools/deaths.py), candidate vs baseline.
2. P1+P2 (flag 3), then 1 and 2 separately if 3 wins. Evaluate on the maps where triggers fire:
   - blind: Trauma, Slithery, Schooltime, Portals;
   - lesson: open_a/b, islands_a/b, maze_b, vault_b, fountain_b;
   - gen/genhold: >=1000 tiles with pearl rate > 5.
   Log (BOTDBG or an indicator) the first declare round per game. It should be ~170-220 on those maps and ~350
   on Default/Autarky/Dilemma blind.
3. P3 on N <= 750: brawl/rush/famine/fountain_a/pockets_a lesson + gen small + blind Devil/Dilemma/Trophy. Also
   confirm identical play on N > 750.
4. P4 only if P2 fails, on >=1500-tile maps.
5. P5 last, on maze_a/b, pockets_a/b and blind Schooltime/Trauma/Portals/QoS, with a guard run on blind
   Devil/Dilemma.
6. Holdout (genhold) only once for the final combo. Server A/B is not informative for unseen-map rules; ranked
   maps use the known path.

## 7. Map-invariant choices (set globally, don't adapt)
SPLIT_STOP 350 (with LATE_SPLIT_ROUND 450), FEED_RESERVE 4, KING_PORTAL_PENALTY 100, KING_V2 feeding rules,
kingKeepExtra 0, KEEP_LEN 0, ESCAPE_HOT_ONLY 0, PEARL_GAMMA and split size. FS is not independent: tie it to the
seed (FS ~ KS + 70), which P2's `QK_FEED` does.
