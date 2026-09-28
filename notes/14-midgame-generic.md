# 14 - Generic mid-game behaviours (r60-350): top-10 vs us

**Question:** what do the current top-10 teams do in the mid-game (rounds 60-350) that we don't? Only rules that carry over to unseen maps count, so every finding is stated in terms a dragon can see or measure.

**Short answer.** Two things matter; the rest is noise.
1. **Pocket pumping** (dead-end harvesting). Almost every team, top-10 or not, harvests 1-wide dead-end pockets with a reverse-split exit. The routine:
   - a length-2/3 dragon walks in and eats down the corridor;
   - at the tip, with 0 exits, it does `SPLIT L-2` so that the rear part leaves as a new dragon facing outward;
   - the length-2 front suicides into the kelp and leaves 1 pearl for the next diver.

   We never do it: 0.1% of our eats come from pockets, against 33-43% for everyone else on Autarky. That explains our Autarky harvest gap (161 vs 270 eats per game).
2. **Portal discipline.** On Default we cross portals 4.7× as often as the top teams and die on 18% of crossings, mostly into our own dragons on the blind exit side. That costs about 60 dragons per game. This only happens on known maps: on unknown maps our bot treats portals as kelp. It matters for the ladder, and for any future LEARN_PORTALS attempt.

Everything else is about the same for top teams and us: length mix, split rule, spacing, corpse race, approach/flee, behaviour when outnumbered, and sprint use (roughly). Details are in section 4.

## 1. Data

- **Top-10 games.** 42 games from 28 Sep, 15:15-15:41 UTC. Each has a current top-10 team (leaderboard: Cutlery, cheji bt, 中国必须人能飞, forgot to mention, calc, 龙虎豹, SKKU, SSS, Sabotage-d, bread first search) against an opponent rated ≥1850.
  - 7 games per map on Default, Autarky, Devil, Trophy, Prisoners Dilemma and Trauma.
  - Stored in `notes/replays/midgame/*.replay`, with `index.json`.
  - Most games are calc, SKKU, cheji bt, Stockfish and 𓎼𓃭𓅱𓂋𓇌; Cutlery, SSS and Sabotage-d have 2-4 games each.
- **Our games.** 58 v15 ladder games (`replays/v15`, excluding Trauma, which runs our map module) and 30 A/B baseline games (`replays/ab_base`, Default+Autarky).
  - Our side comes from `ledger.json`, or by matching the `summary.json` result.
- **Groups.** `top` = a top-10 team; `topopp` = its opponent; `us`; `usopp` = our opponents (ranks about 20-70).
  - Default, Autarky and Trauma usually run to round 500.
  - Devil, Trophy and Prisoners Dilemma usually end in elimination before r200, so they tell us little about the mid-game.
- **Tools** (in `notes/tools/midgame/`):
  - `fetch.py`
  - `sim2.py`: replay_sim plus per-round head positions, enemy/ally distance at each eat, pearl appearances, the head after each move, and `simulate(path, stop=(round,id))` to freeze the state at a given turn.
  - `analyze.py`, which writes `metrics.pkl`
  - `agg.py [maps]`
  - `deaths.py`, `trapped.py`, `pockets.py`, `pump_detail.py`, `portals.py`, `show.py` (ASCII local view)
- Unless stated otherwise, the window is r60-350. Death and portal counts use r60-320, to stay clear of our feeding from r330.

## 2. Finding 1: pocket pumping (dead-end hot-tile harvesting)

**Pocket tiles.** These are the tiles removed by repeatedly pruning tiles with ≤1 open neighbour (the kelp graph, with portals counted as open).
- Autarky, Prisoners Dilemma and Trophy have 16, 16 and 1 pocket tiles; Trauma has 78; Default and Devil have none.
- On Autarky and Prisoners Dilemma the pocket tiles are **gap (1,1) hot tiles**: a pearl every round. Map makers put fast spawns at the ends of dead ends.
- Unseen maps have them too: 22 of 40 `maps/gen` maps and 22 of 40 `maps/genhold` maps have pockets (2-132 tiles).

| r60-320 | Autarky top | Autarky topopp | Autarky **us** | Autarky usopp | PD top | PD us | Trauma top |
|---|---|---|---|---|---|---|---|
| eats per game | 221 | 259 | **161** | 270 | 35 | 25 | 331 |
| eats taken in pockets | 73 (33%) | 96 (37%) | **0.2 (0.1%)** | 117 (43%) | 29 (82%) | 5 (21%) | 100 (30%) |
| pump cycles per game (split with ≤1 exit, parent dead within 3 rounds) | 26 | 33 | **2.3** | 47 | 9.5 | 1.7 | 29 |
| trapped deaths per game (no free neighbour) | 29.5 | 38 | 6.5 | 52 | | | |

**Who pumps.** Pump cycles per team per Autarky game: calc 13-61, cheji bt 25-61, SKKU 5-25, Sabotage-d 16, SSS 13, 中国必须人能飞 19, dev test 1 58, tungtung67 93-135, EternalWisdom 135, Deer Park 98. **Us: 0-9.**

**What a cycle looks like** (651 top-10 cycles; `pump_detail.py`):
- **Entry.**
  - The diver is length 2 (59%) or 3 (40%).
  - The nearest enemy head is ≥4 away 91% of the time (median 8+).
  - The pocket is empty of our own dragons 65% of the time. In 28% one ally is already inside, so divers queue.
- **Inside.** The diver eats the corridor pearls and reaches length 4-6 (mean 4.7) at the tip.
- **Split.** At the tip (depth 1 in 88% of cycles; 0 free exits in 84%) it plays `SPLIT L-2` (97%). The child is the rear L-2 segments: its head is the old tail, near the mouth, facing out, and it walks away.
- **Parent.** The length-2 parent at the tip dies next turn: HitWall 61%, HitSelf 20%, NoValidAction 16%. That drops 1 pearl on the tip, and 87% of those pearls are eaten by our own next diver within 10 rounds.
- **Example.** Game 500988 (calc, Autarky), dragon 31:
  - r75-77: enters (18,2)→(18,1)→(18,0), eating 3 pearls (length 3→6).
  - r78: at the (19,0) tip, `SPLIT 4`.
  - r79: the parent (length 2) dies into kelp.
  - r79-83: the next diver (86) repeats the cycle.
- **Economics.** A length-2 dragon goes in and a length 3-4 dragon comes out, plus 1 pearl left for the next diver. That is about +2 length per 5-6 rounds, against 0.05 pearls per dragon-turn in open foraging: roughly 7× the open-field rate.
- **Mouth fights are a wash.** Head-on deaths within 3 of a pocket are about 9.5 per game for both sides on Autarky, so guarding a pocket mouth is not a lever.

**Why we don't pump (bot/main.cpp).**
- Entering a pocket fails the 12-deep `surviveDepth` check. The `escapes()` shortcut (ESCAPE_SPLIT) only helps if the pearls are already there during the simulation.
- On top of that, the `area < myLen+3` penalty applies.
- Opponents also usually hold the pockets already, so remembered pearls are gone by the time we would arrive.
- The trapped reverse split already exists (`SPLIT myLen-2` when trapped), so the exit half of the routine is in place. The missing half is deliberately going in.

## 3. Finding 2: blind portal crossings kill our own dragons (known maps)

| r60-320 | crossings per game | % of moves | deaths per crossing | exit has 0 / 1 / 2+ own heads within 3 → death rate |
|---|---|---|---|---|
| Default top | 71 | 1.3% | 10% | 9% / 8% / 13% |
| Default **us** | **338** | **6.7%** | **18%** (≈60 deaths/game: 44 HitOtherBody, 9 HitSelf, 6 head-on) | 5% / **20%** / **32%** |
| Default usopp | 90 | 2.2% | 13% | 6% / 11% / 21% |
| Trophy top | 13 | 0.3% | 25% | |
| Trophy **us** | 45 | 1.1% | **32%** (13 ally-body deaths/game) | 14% / 15% / 37% |
| Autarky / Trauma top | 61 / 86 | 1.3-1.5% | 6-7% | 1% / 16% / 14% |

- 30% of our Default crossings re-cross within 4 rounds (102 per game, against 6 for the top teams). That is ping-pong between pearls on both sides.
- Almost every crossing is blind: the exit is outside the Chebyshev-3 window, and vision doesn't pass through portals.
- The result: on Default our units are 22/20/12 at r200/300/350, against the top's 29.5/33/33. We are eliminated in 58% of our Default games, and our r60-320 deaths include 39 ally-body collisions per game (top: 4). Examples: 499377 (107), 500723 (95), 500758 (91), 465084 (83).
- **Generic reading:**
  - The risk of a blind crossing scales with how many of our own heads are near the exit (5% → 32%).
  - Top teams cross in about 1.3% of moves.
  - On unknown maps our bot treats unknown portals as kelp (LEARN_PORTALS=0), so there it is already conservative. This is also a likely reason LEARN_PORTALS tested 0.45.

## 4. Things that are **not** different (don't chase them)

- **Length mix.** Every group is ≥87% length ≤3 through r350, and nobody has dragons ≥7 before r350. There are no mid-size workers.
  - Top teams keep 6-11% of dragons at length 4-6 at r250-350, against our 0-2%. These are the pump divers.
  - Units at r100/200/300: top 16/24/31, us 17/22.5/22 (medians over 5 maps). The gap comes from Default's portal deaths; on Autarky it is 25.5 vs 26.
- **Split rule.** Normal splits (≥2 exits) are 92% at length 4, and 97% of them have a length-2 child (`SPLIT 2`), for top teams, their opponents and ours alike (us: 99.5%). The top teams' L5-7 splits are almost all pump reverse splits. **Keep SPLIT_LEN 4 / child 2.**
- **Spacing.** Median distance to the nearest own head is 3-4 for every group. On Autarky we clump a little more: own head ≤2 away 33% of the time, against 24%.
- **Corpses.**
  - Own corpses: 75% are eaten by the owner's team, for top teams and for us.
  - Enemy corpses: 22-26% are eaten by the other team, median 3-4 rounds after the death.
- **Small dragons near enemy heads** (L≤4, enemy head ≤3 away).
  - Top teams approach 29%, flee 67% and ram 3.6% of the time; we approach 25%, flee 72% and ram 3.0%.
  - Death within 5 rounds: 26% after approaching (us 23%), 14% after fleeing (us 13%).
- **Outnumbered locally** (more enemy heads than own within 4). Death within 5 rounds: 25% for top teams vs 20% for us. The fraction that moves away is 0.23 for both. No special retreat or cluster rule shows up.
- **Contested eats** (enemy head ≤3 from the pearl): 24% for top teams vs 19% for us overall. On Trophy the gap is wider (27% vs 16%; nearest-enemy median 6 vs 9), but those games are confounded by weak opponents.
- **Sprints.** Sprints are 0.2% of moves for everyone.
  - Top teams, per game: 17 sprints, of which 9.7 are kills, 3.5 eat pearls (1.4 of them eat 2 pearls) and 1.4 are escapes.
  - Us: 12 sprints per game, all of them rams. The difference is worth about 3-5 pearls per game.
- **Fast tiles.** Outside pockets they can't be inferred: replays hide the gaps, and appearance counts follow harvesting.

## 5. Changes for our utility bot (each a new `#define`, default 0), ranked

1. **`POCKET_PUMP`**. Deliberate dead-end harvesting.
   - **Trigger.**
     - Our length is 2-3.
     - A move leads into a pocket, meaning its reachable area without going back through the entrance is ≤ 2L+4. Use the known or observed kelp edges in the window, with unknown edges counted as open.
     - Pearls visible, or remembered with countdown ≤ distance, along the pocket add up to at least 4-L. The dragon must be able to reach length ≥4 at the tip.
     - No enemy head within 3 of the entrance.
     - At most 1 own head already inside.
   - **Action.**
     - Waive the `surviveDepth` and area penalties for that move.
     - At the tip with 0 exits and L≥4, `SPLIT L-2`, using the existing trapped reverse split.
     - A length-2 dragon with no exits dies into kelp or its own neck. Add a small bonus (+2 per visible pocket pearl) so allies queue at the mouth.
   - **Expected effect.**
     - On pocket maps: +25-45% eats in r60-320 (Autarky from 161 toward about 230).
     - On pocket-free maps it never fires. Check it has 0 effect on Default/Devil.
2. **`POCKET_PUMP_HOT`** (variant of 1). Require that at least 1 pocket tile has a visible countdown ≤2 or has been seen to respawn. Pump only real factories, not dead ends with a single pearl. Test it against 1.
3. **`PORTAL_ALLY_COST`**. A blind crossing (exit tile not visible) costs `a + b·(own heads remembered or sonar-reported within 3 of the exit in the last 5 rounds)`, and crossing back within 4 rounds costs `c` more. Start with a=2, b=6, c=10 pearl-units (10 per pearl in our score).
   - **Expected effect.** Default crossings drop from 338 to about 80 per game and ally-portal deaths from about 50 to 10. Units at r300 about +8.
   - It also lets LEARN_PORTALS=1 be re-tested on unknown maps, with the cost on.
   - Earlier flat penalties hurt on Portals/Slithery. Keep this one ally-scaled, and check those two maps don't regress.
4. **`SPRINT_EAT2`**.
   - **Trigger.** A 2-step sprint whose first step eats and whose second step also eats (net +1, and it takes a contested pearl) or ends ≥2 further from an enemy head that is ≤2 away. Both tiles must pass the usual survival checks.
   - **Evidence.** Top teams do 3.5 eating and 1.4 escape sprints per game; we do 0.
   - **Expected effect.** Small, about +3 pearls per game. EAT_SPRINT (any contested pearl) was 0.46, so keep this narrow.
5. **`SMALL_CONTEST`**. For L≤3, scale SMALL_THREAT_PEN by 0.5 when own heads ≥ enemy heads within 4 (local numerical parity).
   - **Evidence.** Top teams forage closer to enemies: 24% vs 19% contested eats, and on Trophy an enemy-head median of 6 vs 9. Small dragons trade 1-for-1 anyway.
   - Moderate confidence.
6. **`SPREAD_GENERIC`**. Enable the crowd penalty (`RP.crowd`, about 2 per own head within 2) on all maps, and in unknown-map mode.
   - **Evidence.** On Autarky our heads are ≤2 apart 33% of the time, against 24% for top teams.
   - Low expected gain. It also makes more pocket mouths free.

## 6. Testing without overfitting

- **Primary set.**
  - `maps/gen` (the 22 of 40 maps with pockets matter for 1-2; the rest are the regression set).
  - The ranked maps with `-DNO_KNOWN_MAPS=1`. Autarky, Prisoners Dilemma and Trauma give real hot-tile pockets; with that flag the Trauma module is off too.
  - Run paired seeds, candidate vs v15, at least 80 games per flag.
- **Mechanism check before win rate.** Run `notes/tools/midgame/pockets.py` and `portals.py` on the local replays. POCKET_PUMP must lift the pocket-eat share from about 0 to 20%+ on the pocket maps, and leave it at 0 on the others. PORTAL_ALLY_COST must cut crossings and the death rate per crossing.
- **Held out.** Use `maps/genhold` only for the final accept/reject. Don't generate pocket-rich "lesson" maps just to tune thresholds: that tunes to our generator.
- **Ladder check.** Server A/B on Autarky (pumping) and Default (portals) against the 15 peer teams, compared with the ab_base baseline (15/30).
