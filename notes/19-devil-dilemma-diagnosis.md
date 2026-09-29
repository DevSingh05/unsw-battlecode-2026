# 19: Why we lose on Devil and Prisoners Dilemma (28 Sep 2026)

**Data.** Every Devil and Prisoners Dilemma (PD) game we have with v16-v22: 40 games, 12 Devil (6 W / 6 L) and 28 PD (18 W / 10 L).
- `replays/v19plus` (v21-v22, ledger): Devil 7, PD 8.
- `replays/v16` (ledger) and `replays/ab_v16` (summary): Devil 5, PD 20.
- Ranked since v19: Devil 2/5 (L 526495, 525111, 519645; W 530191, 524996), PD 2/5 (L 529865, 526492, 527846; W 530192, 525114).
- Top-10 comparison: 17 unique Devil and 20 unique PD games between top-10 teams and peers, from `notes/replays/top10b` and `notes/replays/permap` (already downloaded; no new API calls).

**Scripts** (read-only over replays; all in `notes/tools/devdil/`):
- `collect.py` builds `games.pkl`. `report.py [map]` prints the per-game table and the loss/win aggregates.
- `events.py GAME [maxr]` gives a death/split timeline. `windows.py GAME [w r0 r1]` gives per-window units, eats, splits and deaths.
- `board.py GAME ROUND [ID|-] [x0 x1 y0 y1]` prints an ASCII board just before dragon ID acts.
- `early.py MAP [R]`, `center.py`, `eattiles.py` summarise the opening.
- `ramharvest.py MAP` and `ramview.py MAP` cover head-on trades: who started them, local odds on the exact board, and who ate the corpses.
- `rammed.py MAP` shows how our dragons get rammed. `steprisk.py MAP [ver|-] [W|L] [maxr]` gives per-step ram risk by reach zone and local odds.
- `top10.py` runs the same mechanisms on top-10 games.
- `botrun.py`, `rambot.py`, `rammedbot.py` and `changerate.py` re-run compiled bot binaries on reconstructed views, via `notes/tools/rams/botview.py`.
- `v23_devdil_main.diff` and `v23_devdil_params.diff` hold the proposed flags, all default 0, as a patch against `variants/v22`.

**Definitions.**
- **local odds**: heads within Chebyshev 3 of our head, i.e. exactly what the bot sees. "Outnumbered" means allies other than us < enemies, target included. That is the same test `tryRam()` already uses.
- **r1 / r2 step**: a single-step move onto a tile an enemy head can reach with 1 step, or only with a 2-step sprint (enemy L≥3).
- **corpse net**: pearls from both corpses of a head-on that we ate, minus those the enemy ate.

**Caveat.** `sim2.py` counts original starters one segment too long until their first split, because the initial `dragonUpdate` events duplicate the head. The PD starter is L11, not 12, and Devil starters are L4. Split children and all death-cause numbers are unaffected.

---

## TL;DR: loss mechanisms

| # | mechanism | evidence | fix (new flag, default 0) |
|---|---|---|---|
| 1 | **Devil: we start even-length rams while locally outnumbered.** `PM_DEVIL_RG=0` switches off the whole ram guard, including its local-odds test. Each such ram is a 1-for-1 unit trade, and the enemy eats the corpses. | Devil losses: **14.0 outnumbered rams/g, corpse net −1.0 to −1.6 per ram** (−7 to −38 pearls per game). Every loss has it; wins have 4.8/g at about ±0. Locally-ok rams are **+1.22** each. Top-10 Devil winners: 1.5 outnumbered vs 16.3 ok rams/g. | `RAM_GUARD_LOCAL`: keep the local test and drop only `units < RAM_MIN_UNITS` (Devil + PD) |
| 2 | **PD: our small dragons walk into enemy ram reach when not locally ahead, mostly 2-step sprint reach that the bot doesn't model.** The enemy rams and harvests. We almost never ram first, because the guard needs 8 units and PD starts with 6. | PD losses: rammed 9.3/g (wins 2.0). **53% by 2-step sprints.** 86% of these followed our own step into reach, with a reach-free alternative 77-85% of the time. After their rams they eat 2.09 corpse pearls to our 0.55. | `SMALL_SPRINT_THREAT` (+ `RAM_GUARD_LOCAL` on PD) |
| 3 | **Pocket pump wastes one length per cycle.** The dragon splits 2 off at L4 one tile before the tip, eats the last pearl, and dies at L3. So a diver leaves as L2 = net 0 per cycle. | PD: **34 such L3 deaths/g** (1015 in 28 games). Our trapped deaths average L2.8, top-10 teams' L2.14. Game 529865 out-ate Shannon in every window for 260 rounds and still stayed at 6-8 units. The same pattern is general: Autarky 51/g, Portals 116/g, Slithery 188/g, opponents 2-28. | `PUMP_TIP_SPLIT` (general) |

Not a mechanism:
- **King timing and `keepLen`.** No Devil game reaches r260. PD reaches r500 in 5/28 games and our king wins 4 of those 5.
- **Map identification.** Starters recognise both maps on both layouts; checked with the v22 binary.
- **Start-layout swap.** See §5.

---

## 1. Records and timelines

Means; eliminated teams count as 0 after the end. Cells are us / them.

| | r50 units | r100 units | r200 units | r100 total | r200 total | max r100 | max r300 | how it ended |
|---|---|---|---|---|---|---|---|---|
| **Devil L (6)** | 6.0 / 9.5 | 3.2 / 16.7 | 0.3 / 24.7 | 8 / 43 | 1 / 64 | 1.7 / 3.7 | 0 / 4.2 | 6 eliminations at r57, 100, 106, 107, 221, 258 |
| **Devil W (6)** | 15.0 / 6.7 | 32.0 / 5.8 | 45.3 / 0.7 | 78 / 14 | 110 / 2 | 4.0 / 3.2 | 4 / 0 | 6 eliminations, r130-248 |
| **PD L (10)** | 5.2 / 6.0 | 3.9 / 6.1 | 2.5 / 9.3 | 10 / 16 | 6 / 25 | 1.8 / 4.6 | 0.6 / 4.8 | 9 eliminations (r30, 39, 56, 93, 153, 167, 175, 215, 393); 1 at r500, 18 v 24 (506773 vs Check Raise factory) |
| **PD W (18)** | 9.6 / 3.3 | 10.6 / 1.7 | 13.8 / 1.1 | 24 / 5 | 32 / 4 | 3.2 / 2.6 | 3.6 / 1.8 | 14 eliminations; 4 at r500 won 13v13, 16v2, 26v24, 27v10 |

- **Devil** is a pure swarm race. The longest dragon on either side never exceeds 4-5; the winner has 30-45 units by r100-200. Losses are even at r25 (7.7 v 7.8) and gone by r50-100.
- **PD** is a slower bleed. Units are even at r25 (5.6 v 5.7) and lost 1 at a time. Three v21 losses were eliminations by r30-56 (528519, 529247, 527846).

**Eats per game** (hot / spawn / corpse):

| | r0-50 us | r0-50 them | r50-100 us | r50-100 them | r100-200 us | r100-200 them |
|---|---|---|---|---|---|---|
| Devil L | 9 / 10 / 11 | 13 / 12 / 13 | 6 / 9 / 13 | 20 / 16 / **36** | 4 / 8 / 14 | 28 / 14 / **39** |
| Devil W | 16 / 23 / 19 | 11 / 8 / 6 | 45 / 35 / 68 | 10 / 6 / 13 | 90 / 60 / 156 | 9 / 5 / 18 |
| PD L | 12 / 1 / 16 | 11 / 1 / 16 | 6 / 3 / 14 | 7 / 1 / 11 | 8 / 5 / 16 | 11 / 7 / 17 |
| PD W | 14 / 4 / 28 | 11 / 2 / 13 | 13 / 4 / 26 | 4 / 0 / 5 | 17 / 10 / 35 | 7 / 1 / 9 |

- In Devil losses the enemy wins the **corpse** race 3:1 from r50.
- In PD losses the eats are about **even**, but the length doesn't turn into units (§3, mechanism 3).

**Deaths per game, r0-100** (length lost in brackets):

| | us | them |
|---|---|---|
| Devil L | we rammed 13.0 (37), rammed 4.3 (11), trapped 6.4 (13) | rammed 13.0 (36), trapped/no-action 13.3 (30), rammed us 4.3 (12) |
| Devil W | trapped 42.8 (96: the pump), we rammed 13.5 (38), rammed 2.8 (8) | rammed 13.5 (34), rammed us 2.8 (7) |
| PD L | trapped 14.8 (**42**), rammed 5.9 (14), we rammed 2.4 (6) | trapped 12.1 (**26**), rammed us 5.9 (16), rammed 2.4 (6) |
| PD W | trapped 22.9 (63), we rammed 6.2 (16), rammed 1.9 (5) | rammed 6.2 (16), trapped 11.9 (27) |

**Split counts.**
- Devil L: us 13 / 11 / 8 in r0-50 / 50-100 / 100-200, them 17 / 28 / 32.
- PD L: us 15 / 8 / 11, them 15 / 8 / 14.

**Ram trades are always 1 unit for 1 unit.** What decides them is who eats the corpses (§2).

---

## 2. Devil: how we lose (mechanism 1)

**The map.** The centre (x 14-17) holds all the fast food:
- the 1-wide tubes x=14 and x=17 (y 5-10), with hot tiles at y 7-8;
- the 2-wide dead ends (15-16, 0-2) and (15-16, 13-15), with hot tiles at the far end.

In wins we own the centre (10-15 heads there at r40-60 against 0-4) and eat 175 of our 207 r0-100 pearls in x 12-19. In 4 of 6 losses we held the centre *just as well* until r60 (`center.py`: 526495 5-8 heads v 1-3, and centre eats 35 v 23). We lost it through trades.

### What the trades look like (`ramview.py Devil`, exact board before our ram)

| our rams (started by us), Devil | rams/g | corpse pearls eaten per ram, us / them | net |
|---|---|---|---|
| losses, locally **outnumbered**, units < 8 | 9.5 | 0.79 / 2.37 | **−1.58** |
| losses, locally **outnumbered**, units ≥ 8 | 4.5 | 0.85 / 1.96 | **−1.11** |
| losses, locally ok | 6.1 | 2.0 / 1.2 | +0.76 |
| wins, locally outnumbered | 4.8 | 1.55 / 1.38 | +0.17 |
| wins, locally ok | 20.0 | 2.15 / 0.79 | **+1.36** |

Per game, outnumbered rams (net corpse pearls):

| game | result | outnumbered rams |
|---|---|---|
| 512105 | L | 11 (−20) |
| 515341 | L | 15 (−14) |
| 519645 | L | 22 (−38) |
| 525111 | L | 6 (−10) |
| 526495 | L | 18 (−31) |
| 528521 | L | 12 (−7) |
| wins | W | 1-10 each (−4 to +4) |

- Each outnumbered ram also trades one of our scarcer units for one of theirs.
- When the enemy starts the ram, they are locally ahead (local heads −1.53 for us) and eat 2.06 v 0.64.

**Key moment, 512105 (Drago et al, ranked, eliminated r100).** At r33 we have 7 units against 13. Board before our id1 moves (x 9-22, y 0-8; U/u us, E/e them, * pearl):
```
  3 |. E|.|. . U . . u u .|.|U u      us1 L3 @(17,4) sprints WS into EN23 L3 @(16,5)
  4 |. .|.|. . u u . U . .|.|. u      in view: 2 of our heads, 3 of theirs (EN8, EN23, EN20)
  5 |. .|.|. .|.|* E|U|. .|.|. .
  6 |. e|.|. .|.|e e|u|. .|.|. .
  7  . E e E .|E|e e|*|. . . U u
```
- Over r30-36 we start **6 rams in 7 rounds** (r33 id1, r34 id3, r35 id19, r36 id13, and more). Every one is outnumbered in view.
- The enemy eats 9 corpse pearls in r30-40 to our 3, and splits 7 times to our 1. Units go 9/11 → 3/10 → 2/16 (r50).

**Same pattern elsewhere.**
- 525111 (Stockfish, ranked): 6 outnumbered rams in r20-51; eliminated r57.
- 526495 (free trip, ranked) is the weakest example. We start 18 outnumbered rams over the game (net −31 pearls) but are still even at 11/13 units at r140. The r140-190 collapse (9/12 → 3/15 → 1/22) comes from 13 rams (only 3 outnumbered) and their harvest (corpse eats 20 v 46 in r150-190): a snowball, not one decision.

**Bot re-run** (`rambot.py Devil`): v22 reproduces **84/84** of these outnumbered ram decisions exactly. With the local-only guard (`-DPM_DEVIL_RG=1 -DRAM_MIN_UNITS=0`), 80/84 change; 13 of the new moves still land on a tile the bot scores as threatened.

### Why `PM_DEVIL_RG=0` exists, and why it's half right
- The v5-era pool test (journal 06:05) had RAM_GUARD at Devil/Trophy .25. That guard needs `units >= RAM_MIN_UNITS (8)`, and Devil starts at 6 units a side, so it blocked every early trade.
- The data agree that early even trades help **when locally ok** (+0.6 to +1.4 per ram).
- But switching the guard off also removed the local test, and that test is the part that matters.

---

## 3. Prisoners Dilemma: how we lose (mechanisms 2 and 3)

**The map.** Each side has a 1-wide column (x=14 for the left team, x=17 for the right) walled at y 0-3 and 12-15, with hot tiles at y 0-2 and 13-15: two 4-deep dead ends per column. The L11 starter lies in the column. The fight happens in the open diamond between the columns (x 9-22, y 4-11).

### Mechanism 2: we get rammed, and don't ram back

**How we get rammed** (`rammed.py Pris`, losses, 93 rams):
- 53% were **2-step sprints** (killer L2 41%, L3 53%).
- Our own last step put us in the killer's reach 86% of the time: 40% into 1-step reach, 46% into 2-step-only reach.
- A tile outside all reach was free 77% of the time (85% for 1-step).

**Why:**
- For dragons < `KING_MIN_LEN`, `computeThreats()` uses `MAX_THREAT_REACH = 1`, so sprint reach is invisible.
- The 1-step penalty (`SMALL_THREAT_PEN = 12`, about 1.2 pearls) is smaller than the pearl pull.

Per-step risk (`steprisk.py Pris - L 100`, PD losses, r<100, our L≤5 single steps):

| local odds | safe tile | r1 tile | r2 tile |
|---|---|---|---|
| ahead | 0.0% rammed (n=3981) | 16.7% (36) | 4.1% (122) |
| even | 0.2% | **60%** (10) | **19%** (47) |
| behind | 0.3% | **71%** (17) | **30%** (46) |

**How often we take r2 steps without being locally ahead:**
- us (all PD games): 10.6/game;
- top-10 PD winners: 4.5/game;
- top-10 PD losers: 6.6/game.

**The harvest follows local odds.** When they start the ram (9.3/g in losses), local heads are −1.09 for us and they eat 2.09 corpse pearls per trade to our 0.55.

**We almost never start one.** We start 3.3/g in losses and 7.9/g in wins, with corpse net +1.94 per ram in wins. The global guard wants `units >= 8`, and in PD losses we are below 8 nearly all game.
- In sampled r<100 contacts (enemy head within 2, locally ahead, units < 8), the local-only guard would ram in 23% (28/119).
- Top-10 PD winners start 5.3 locally-ok rams/g (+2.11 each) and 0.8 outnumbered.

**Key moment, 528519 (中国人不准飞, eliminated r30), r20.** Our us2 L3 at (15,10) is next to EN24 L3 at (16,10). The local test fails, 2 of our heads against 3 of theirs.
```
  9  . . . . u U * . . . . . . .      us2 steps N onto the pearl at (15,9): 2 steps from EN24,
 10  . . . . u . U E u . . .|. .      "safe" to the bot (1-step model).
 11  . .|. . . u u e U . . E|. .      EN24 (id 24 > 2, moves later this round) sprints NW -> ram.
```
- Our 16 deaths in r0-30 of this game: 9 rams **started by them** (most of them sprints: NE, WW, NW, ES, EN), 5 pump deaths and 2 rams of ours.

### Mechanism 3: the pump dies at L3

`POCKET_PUMP` sends a short dragon into the 4-deep column end. It then runs as follows:
1. It eats (x,2) and (x,1) and reaches L4.
2. The normal split branch fires at `myLen >= 4` and gives off a 2-long child.
3. The 2-long parent eats (x,0), becomes L3, can't split (needs 4), and dies trapped.
4. Its two corpse pearls land on hot tiles (x,0) and (x,2). Those tiles spawn every round anyway, so the pearls just block spawns.

A diver that went in at L2 comes out as an L2 child: **net 0 per cycle**. Splitting at the tip instead (child L3 leaves, 2-long head dies) is +1 per cycle, the minimum possible loss.

Counts (`top10.py` / inline scan):

| | L3 deaths after a split at L4 (per game) | mean trapped-death length |
|---|---|---|
| PD, us | **34** (1015 over 28 games) | 2.8 |
| PD, top-10 winners | 4.3 | 2.14 |
| PD, top-10 losers | 1.4 | 2.05 |

The same pattern on other maps, v19plus, per game:

| map | us | them |
|---|---|---|
| Autarky | **51** | 2.9 |
| Portals | 116 | 27 |
| Slithery | 188 | 28 |
| Schooltime | 13 | 3.8 |
| Trauma | 10.5 | 1.9 |
| Devil | 4.1 | 3.3 |
| Default | 1.2 | 0.6 |

**Example, 529865 (Shannon, ranked, lost r393).**
- For r0-260 we out-eat them in every 20-round window (e.g. r100-160: hot 20 / corpse 36 against 0 / 4).
- We still sit at 6-8 units and 12-20 total: 5-8 pump deaths per window burn what we eat.
- From r260 their rams (RRR) finish a team that never grew.

**Bot re-run** (`botrun.py` on 506743 id6 r2, a real L4 split at (17,1), plus a fabricated next state):
- v22 splits 2 at (17,1).
- The patched bot moves N and eats at the tip. Next turn it outputs `SPLIT 3`, so an L3 leaves and a 2-long head dies.

---

## 4. Top-10 play on these maps (`top10.py`; notes/08)

| per game | Devil W | Devil L | PD W | PD L |
|---|---|---|---|---|
| units at r100 | 27.4 | 5.5 | 7.9 | 2.9 |
| hot eats | 196 | 36 | 77 | 62 |
| rams started, locally ok (corpse net each) | 16.3 (+1.58) | 5.9 (+0.61) | 5.3 (+2.11) | 1.4 (+0.66) |
| rams started, outnumbered (corpse net each) | **1.5** (+1.00) | **5.5** (−0.78) | 0.8 | 1.3 (−0.69) |
| trapped-death mean length | 2.30 | 2.34 | 2.14 | 2.05 |

Summary for these two maps:
- **Top teams start rams only when locally ahead.** Their losers are the ones who start them when outnumbered, as we do on Devil.
- **They step into reach less.** PD winners take r1/r2 steps with an enemy in view when not locally ahead 3.1 / 4.5 times a game; losers 7.0 / 6.6. When they do, they are rammed 29% / 7% of the time (winners) and 38% / 19% (losers).
- **They pump at L2.**
- **Neither map sees kings or feeding** (notes/08: Devil winners never above 4-5; PD winners' longest is about 6 at r300).

---

## 5. Per-map settings: do they still make sense?

| setting | now | verdict |
|---|---|---|
| Devil `PM_DEVIL_RG=0` (ram guard off) | on since v6 | **Half right.** Dropping `units >= 8` is right: Devil starts 6 v 6, and early locally-ok trades are +. Dropping the local-odds test is what loses Devil (§2). Replace with guard mode 2 (local only). |
| PD ram guard (global `RAM_GUARD=1`, `RAM_MIN_UNITS=8`) | default | **Wrong for PD.** It starts at 6 units and loss games stay < 8, so we never take locally favourable even trades while the enemy takes theirs. Mode 2 again. |
| PD `PM_DIL_KEEP=-1` | `RP.keepLen` stays `KEEP_LEN=0`, so the path is **inactive** | Keep it off. KEEP 8 went 0/36 locally (journal 16:23), and PD winners don't keep a long dragon. The code at `bot/main.cpp` ~2276 is dead on every map. |
| PD `PM_DIL_KD=1`, `PM_DIL_KS=350` | king from r350 | Leave it. It only matters in the 5/28 round-limit games, where our king wins 4 (13-27 long). |
| Devil KD / SS / FS (defaults) | | Irrelevant. Every Devil game (12/12) ends by r258. |
| `LATE_SPLIT_ROUND=450`, `KING_ESCAPE`, `THREAT_TAIL_UNKNOWN` (v21-v22) | | No effect before r350 or for L < 8. v21 PD 3/8 against v16 15/20 comes with the same opening and similar opponent Elo (1830 v 1856). I found no code cause, and the samples are small. |

**Start-layout swap.** All 6 Devil losses were on the swapped layout (swapped 2-6, standard 4-0; Fisher p ≈ 0.03 but n = 12). v21 PD swapped went 0-3.
- I checked the v22 binary on swapped and standard starters: both print `map=Devil` from round 0, `FRAME_FIX` sets the frame, and the Devil and Dilemma modules are empty.
- Move order follows position, not letter: the left team always has ids 0, 2, 4. The swap therefore changes nothing mechanical for these maps. Treat it as opponent mix unless it keeps showing up.

---

## 6. Fixes (all new flags default 0; patch = `notes/tools/devdil/v23_devdil_main.diff` + append `v23_devdil_params.diff` to `bot/params.hpp`)

The patch applies to the current `bot/main.cpp`, which now includes the notes/20 portal edits. I checked that it builds with every flag off and on. **With the flags off, 139/139 sampled decisions are identical to v22.**

### F1 `RAM_GUARD_LOCAL`: mechanisms 1 and 2
`applyMapParams()` (`bot/main.cpp` ~110), then `tryRam()` (~1992):
```cpp
// params.hpp
#ifndef RAM_GUARD_LOCAL      // 1 = Devil + Prisoners Dilemma, 2 = every map
#define RAM_GUARD_LOCAL 0
#endif
// applyMapParams(), before the PM_DIL_KEEP line
if ((RAM_GUARD_LOCAL == 1 && (n == "Devil" || n == "Prisoners Dilemma")) || RAM_GUARD_LOCAL == 2)
    RP.ramGuard = 2; // local odds only
// tryRam()
if ((RP.ramGuard != 2 && units < RAM_MIN_UNITS) || allyHeads < enemyHeads + 1)
    worth = false;
```
- **Effect on Devil:** it drops the ~14/g outnumbered rams in losses (−1.0 to −1.6 corpse pearls each) and ~5/g in wins (about ±0). It keeps the +1.2 locally-ok rams.
- **Effect on PD:** it lets locally-ahead even trades through (in 23% of early contacts).
- **Mechanism check:** after a batch, run `ramview.py Devil`. The outnumbered rows should go to ~0, and PD "we started" rams should go from 3-8 up.
- `=2` is for a later general test: Default, QoS and Autarky already use mode 1, and Trophy also has the guard off.

### F2 `SMALL_SPRINT_THREAT`: mechanism 2
`computeThreats()` (~1739) and the move score (~2326):
```cpp
// members
std::vector<int> sprintThreatAt; int localAllies = 0, localEnemies = 0;
// computeThreats(), if SMALL_SPRINT_THREAT: count heads in view; for each enemy head with visible len >= 3
// and myLen < KING_MIN_LEN: for d1 with a = step(head,d1) free (freeT[a] <= 1), for d2: sprintThreatAt[step(a,d2)]++
// move scoring
bool outnum = SMALL_SPRINT_THREAT && myLen < 6 && localAllies <= localEnemies;
if (threat > 0)
    score -= (myLen >= 6 ? 25.0 + 4.0 * myLen : (outnum ? SMALL_THREAT_PEN_OUT /*30*/ : SMALL_THREAT_PEN))
             * (units <= LAST_FEW_UNITS ? LAST_FEW_MULT : 1.0);
else if (outnum && sprintThreatAt[t] > 0)
    score -= SMALL_SPRINT_PEN /*10*/ * (units <= LAST_FEW_UNITS ? LAST_FEW_MULT : 1.0);
```
- **Why these weights.** When not ahead, a ram costs the dragon (~2.5) plus the corpse race (~1.5), about 4 pearls = 40 points. P(rammed) is 60-70% on r1 and 19-30% on r2, so the expected costs are about 25 and 8.
- **When locally ahead nothing changes:** a trade there is favourable.
- **Bot re-run** (`rammedbot.py`): on the real decisions before 85 PD-loss rams, landings inside the killer's reach go **75 → 44**; on Devil losses 32 → 21. Across random not-ahead contact decisions it changes only 5-8% of moves (`changerate.py`), so it is targeted.

### F3 `PUMP_TIP_SPLIT`: mechanism 3 (general)
Split branch (~2288), the split size (~2292) and the pump test in scoring (~2317):
```cpp
int holdTile = -1;   // inside a dead end with a pearl next to us: eat on, split at the tip
if (PUMP_TIP_SPLIT && myLen >= 4 && myLen <= 6 && !threatened && tailHasExit(myLen - 2))
    for (d...) { t = step(myHead,d); skip if blocked or no (pearl | hot tile);
                 bfsFrom(t, pp, area, myLen + 3); if (area < myLen + 3) holdTile = t; }
if (holdTile < 0 && /* existing split condition */) {
    int k = ...;                                    // 2
    if (PUMP_TIP_SPLIT && headExits == 0 && tailHasExit(myLen - 2))
        k = myLen - 2;                              // child takes the bulk out, 2-long head dies
    ...
}
bool pump = POCKET_PUMP && area < need && (t == holdTile || pocketWorthPumping(t));
```
- **Effect:** +1 length per pump cycle. That is 34 cycles/g on PD, about 51 on Autarky, and more on Portals and Slithery, if the modules there use the same path.
- **Mechanism check:** after a batch, the L3-after-split deaths (`top10.py`-style scan) should fall toward 2-4/g, and mean trapped-death length toward 2.1.

---

## 7. Test plan

Self-play can't measure these, because v22 v v22 has the same guard and the same pump. Suggested server A/B (ask first):
1. **v22 + F1 + F2** against 10 peers on Devil and PD (20 games). Judge on:
   - outnumbered rams per game (target ~0);
   - PD rammed/g (9.3 in losses);
   - units at r100 against the §1 table.
2. **F3 alone** against 10 peers on PD and Autarky. Judge on L3 pump deaths per game and total length at r100/r200. Then run the unseen suites (gen/lesson): F3 is general, so check it doesn't hurt maps with long pockets.
3. If F1 holds, test `RAM_GUARD_LOCAL=2` on Default/Autarky/Trophy. Default and Autarky already have mode 1 there; the question is whether dropping `RAM_MIN_UNITS` helps.

Minor, not fixed:
- On Devil, reverse splits in the 2-wide dead ends sometimes birth a 2-long child with no exit, which dies at age 0 (e.g. 526495 r67-96, "exits0" splits). This costs 1 pearl each, and `tailHasExit()` apparently counts a tile the parent still occupies.
- It happens about 12/g in Devil wins. Worth a look after F3.
