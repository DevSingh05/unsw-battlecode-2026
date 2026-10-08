# Cutlery deep dive: how they play maps they have never seen (8 Oct, IN PROGRESS: paused 12:21 EDT)

Status: the analysis is done. The prototype is built. **The unseen_eval of the prototype was started and then paused
(SIGSTOPped) before it printed any set, so there are no win numbers yet.** Resume steps are in
`work/top4b/cutlery/PROGRESS.md`. Nothing in `bot/` or `variants/` was touched, nothing was submitted and nothing was challenged.

## 0. Data and tools (all durable)
- **Sprint replays, unseen maps for every team at the time:** `replays/cutlery_sprint/`, all 9 Cutlery battles, 63 games
  (`meta.json`).
  - Old rules: 1 free step.
  - Opponents: UIUC1234, Just Reboot Normalize, winner or quitter, wawow830, Deer Park, ddabap, calc, cheji bt, PPP.
- **Current build:** `replays/top4_cutlery/` (60 games: 10 vs b4/kf1, 50 vs top teams).
- **5 Oct build:** `replays/vib_oct5/` (78 games: 55 vs us, 23 vs top teams).
- **Our unknown-map behaviour:** `work/top4b/cutlery/blind_b4/`, b4 with `-DNO_KNOWN_MAPS=1` in self-play on 21 maps (17 official
  + 4 real_gen), seed 975000.
- **Scripts** in `work/top4b/cutlery/scripts/`:
  - `deep.py`: per-decision replay pass. It keeps the decision-time pearls, bodies and heads and records portal crossings,
    paid moves, kill opportunities (BFS kamikaze reach, with pearls refunding paid steps), approach and the opening.
  - `agg.py` and `report.py`: the tables. `mouth.py`: crossing propensity at portal mouths. `label.py`: team labels.
  - `dl_sprint.py`, `blind_games.py`, `mech_games.py`.
- **Caveat:** the `deep_*.pkl` files assumed queen id 0 = team A. That is false on some maps (Devil, for one), so the queen-only
  stats below are approximate. Portal, lunge and kill stats are unaffected. The fix is in `deep.py`, and the `deep2_*.pkl`
  re-run was paused mid-way.

## 1. Cutlery's policy rules (Cutlery-side; "S" = Sprint/unseen maps, "C" = current build)

### 1.1 Portals and exploration
- **Rule P1: an unknown portal is a door they take.**
  - When a Cutlery unit stands on the mouth of a portal pair the team has never crossed, its next move goes through it
    **64.5% of the time** (S, 369/572). Current build: 30-76% depending on food in view.
  - Top Sprint opponents: 61%. **Our b4 blind: 4.3% (124/2905).**
  - At pairs the team has already crossed, the rate is neutral: 35% (S), 33% (C), us blind 18%.
- **Rule P2: no hunger gate and no food gate.**
  - Crossing rate does not depend on hunger (<5 / <20 / 20+: 34 / 38 / 35%) or on the round.
  - Visible pearls on their own side don't stop it (S: vp 0 / 1-2 / 3+ = 64 / 43 / 80%).
  - First crossers have a median hunger of 10, and 58-61% of them had pearls in view on their own side.
- **Rule P3: who crosses.**
  - First crossings of each pair are made by L2 (66%), L3 (28%), L4 (4%). The queen makes 1-2%.
  - Never on a paid step (0%). Rarely with an enemy head within 3 (11-21%).
- **Timing.** Median first crossing r8 (S) / r10 (C). Ours blind: r73.
  - On Sprint maps, Cutlery first crossings by map: Australia r4, Islands r1, Stripes r8, AUNSW r31, Maze r50.
  - Ours blind on the same maps: r154 / r121 / r15 / r109 / r114.
- **Volume.** Crossings by r100: S 31 per game, C 18. Ours blind: **0** (median; 7.5 per whole game).
  - Units that crossed by r100: 17 (S) vs our 0.
  - Pairs used by r100: 5 of 8 vs our 0 of 7.
- **On the other side.**
  - 44-56% eat within 10 rounds; 1.8-1.9 eats in 20 rounds (units that stayed at the mouth: 0.8-1.5).
  - 22-28% come back through the same pair within 20 rounds.
  - 41-51% are dead within 20 rounds, about half of them by NoValidAction (their stuck-unit recycling) and half head-on.
  - Our blind crossers die as often (55-57%), but 29% of them by HitSelf/HitWall: L2-3 units boxed in a pocket after the
    crossing, with 0 exits.

### 1.2 Kills and the "swarm"
- **Rule K1: kamikaze reach is capped at 3 steps.** We cap at 2. This is the one structural difference.
- **Take rate per kill opportunity** (a visible enemy head reachable this turn), same 55 games, Cutlery vs us (vib5 set):

  | condition | Cutlery | us |
  |---|---|---|
  | 1 step | 47% | 45% |
  | 2 steps | 29% | 34% |
  | **3 steps** | **18%** | **1%** |
  | 4+ steps | 0% | 0% |
  | 2 paid steps needed | 19% | 1% |
  | own L2 | 49-56% | 27-39% |
  | own L3 | 35-39% | 30-33% |
  | **own L4** | **19%** | **7-8%** |
  | own L5-8 | 4% | 0-1% |
  | own L9+ | 0% | 0% |
  | victim at least as long as the attacker | 40-46% | 27-32% |
  | victim shorter than the attacker | 8-9% | 10-16% |
  | local numbers: negative | 10% | 9-10% |
  | local numbers: 0 | 16-20% | 17% |
  | local numbers: +1-2 | 21-29% | 22-27% |
  | local numbers: +3 or more | 35-46% | 33-42% |
  | rounds < 60 | 39-46% | 25-30% |
  | rounds 300+ | 11-12% | 11-14% |

- **Who makes the 3-step kills:**
  - Killers: L3 50% (with 1-2 pearls on the path paying the extra step), L4 24-34%, L5 8-18%.
  - Victims: mostly L2-3.
  - Local advantage was positive in 56-62% of them.
- **Volume.** Kills per game 34-39 vs our 26-29. 3-step kills are 7-10 per game; ours are about 0.
- **Rule K2: there is no hunt or swarm movement.** Approach behaviour is identical to ours:
  - Non-queen moves with an enemy head in view end closer 39-41% and farther 58-60% of the time. Ours: 38-39% / 61%.
  - Engaged share (enemy head within 5) is the same or lower: Cutlery 34-45%, us 35-51%.
- **Eliminations are mop-ups decided by r100 economy.**
  - In Sprint elimination wins, units at r100 were 62 vs 6, 63 vs 1, 16 vs 0, 64 vs 10.
  - The last enemy units die one per distinct Cutlery attacker (1-for-1 head-on trades).
  - The "swarm" = more units (from portal food) plus 3-step reach plus 1-for-1 trades whenever local numbers are positive.

### 1.3 Paid moves other than kills
- **Rule L1: eat-lunges only when net length is at least 0.**
  - 9-17 per game (ours 0). 85-92% have net length ≥ 0, and pearls cover 1.2 per paid step.
  - Usual patterns: "10" (eat on the free step, then one paid step: +1-1 = 0, a free reposition), "11" (net +1),
    "01" (reach a pearl 2 tiles away a turn early).
  - Done by L2-3 (S also L5-12). An enemy head within 3 in only 24-35%, so this is tempo, not racing.
- **Rule L2: the other paid moves are escapes.** 9-27 per game; 59-69% of them start from a head with ≤ 1 free exit.
- **Multi-step free moves:** 548-857 per game vs our 244-280 (C vs us in the same games). Their mid-size units use their free
  steps 2-3x more often.

### 1.4 Opening (r1-60)
- **Queen split.** The queen splits as soon as she can: r0 at L5 on Sprint spawns; r8-9 at L4 now. Ours (blind): r29, L7.
- **Units at r30/r60:**
  - Cutlery: 11/18 (S) and 7.5/13 (C).
  - Sprint opponents: 8/12. Ours blind: 8.5/13.5.
  - Same Sprint maps, Cutlery vs our blind: Australia 14/22 vs 13.5/17.5; Islands 20/41 vs 16/29; AUNSW 27/51 vs 18.5/40.5.
- **Eats by r100 on those maps:** Australia 177 vs 104, Islands 276 vs 240, AUNSW 380 vs 280, Stripes 103 vs 48.
- **First portal crossing:** r8. First kill: r35-56.
- **Early trading:** by r60 they make 2-2.8 kills and lose 3-4.6 units head-on per game. They trade early and cheaply.

## 2. Our unknown-map behaviour (b4 code, `bot/main.cpp`)
- **Portals.**
  - An unknown portal is kelp (`observeEdges`, `nxt=-1`).
  - It is crossed only through:
    - UNK_EXPLORE desire: a sealed region (portal-free region < 0.7 N) plus hunger ≥ 3;
    - UNK_PORTAL_EXPLORE: L ≤ 4 non-queens with no walkable food within 16 for 25 rounds, rationed 1 in 4 by id slot, no ally
      within 3;
    - UNK_SCARCE_FIX: path use once rich portal-only food is seen;
    - UNK_PORTAL_ESCAPE: the all-lethal fallback.
  - Every crossing is a knock: sonar on arrival at the mouth, then cross on a clean echo.
  - learnDest links are kept out of `nxt`.
- **Rams** (`tryRam`): 1-2 steps only (`d1`, `d2`). The queen kill (QKILL) uses the full K. The ram guard asks for local
  numbers on small boards and units ≥ 8 elsewhere.
- **Paid steps:** never used for food. The free-path search uses free steps only.
- **King:** UNK_KING seed r250 / feed r300 (crown early at 62 units). Cutlery's first L10 is at r123-134, L20 at r231-268.
- **Side finding: our queen does cross unknown portals.**
  - b4 blind: our queen took a never-crossed portal on 21% of her mouth turns (6/28), our workers on 4%.
  - She crossed by r100 in 8 of 36 blind team-games, and all 8 died by r150 (16 of the 28 that did not cross).
  - Cutlery's queen makes 1% of first crossings. Crossing queens die early for every team, so this is partly selection.
  - qf1's UNK_PORTAL_SIDES=2 covers only the neck-portal suicide.

## 3. The differences that most likely cost us on unseen maps
1. **We barely cross unknown portals.** Never-crossed mouth 4% vs 64%, first crossing r73 vs r8, 0 vs 31 crossings by r100.
   - This is the only gap that is specific to unseen maps. On known maps we cross like them (US-cur x100 22 vs C 18).
   - The cost is food: Sprint maps eats100 177/276/380 vs our blind 104/240/280, and the early unit lead that turns into their
     eliminations.
2. **Kamikaze reach 3 vs 2.** Cutlery takes 15-18% of 3-step chances; we take 0-1%. That is 7-10 kills per game.
   - Map-independent, so it doesn't explain unseen-specific losses.
   - The all-maps version (v64 LUNGE34, 3-4 step lunges) lost -6.8 pp on the server.
3. **Tempo.** Eat-lunges at net ≥ 0 and 2-3x more multi-step free moves, so units cover the map faster. Map-independent.
   No prototype.

## 4. Prototype (gated on `World::neverKnown()`; work/top4b/cutlery)
- **`bot/`** = current `bot/` (b4 + qf1 flags, all off) + **UNK_XP** (prototype default 1).
  - Small non-queens (L ≤ 4, from r3) always carry explore desire on never-identified maps, except for 10 rounds after their
    own last explore crossing.
  - The existing machinery does the rest: door lure, knock, cross on a clean echo, learnDest.
  - +20 crossing score bonus. Learned links stay out of `nxt`.
- **Mechanism, 4 blind games vs b4 (seed 976000, `mech_xp/`):** never-crossed mouth crossing 47% (b4 4.6%); crossings by
  r100 35-92 vs 0-29.
  - Results: 1 W (Portals, eats 1601 vs 652), 3 L (Stripes elimination at r127, Islands, rt2028_00). Eats were lower on Islands
    and rt2028_00.
  - Too few games to judge, but **an early warning that copying P1 alone may not help our bot.** It matches the history of
    LEARN_PORTALS and eager UPE.
- **`bot_l3/`** = the same with UNK_XP 0 + **UNK_LUNGE3** (prototype default 1): 3-step `tryRam` paths for non-queens L ≤ 5
  (an L3 needs a pearl on the way), same worth and guard rules. Built (compiles); not run.
- **Eval:** `python3 tools/unseen_eval.py work/top4b/cutlery/bot --base variants/b4 --seeds 1 --jobs 2 --seed-base 974000
  --sets real,realhold,blind17` (UNK_XP=1).
  - Output goes to `work/top4b/cutlery/ue_xp1_974000.txt`.
  - **Paused before any set finished: no numbers.**
