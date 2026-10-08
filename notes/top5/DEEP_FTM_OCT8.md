# FTM deep dive (8 Oct): queen policy and small-map economy

Written 8 Oct 15:00-17:00 EDT. Read-only study plus one local prototype. Nothing submitted, no challenges, no Discord
or browser. bot/ and variants/ untouched. Builds on TOP4_FTM_OCT8.md and FTM_OCT5.md.
Scratch, scripts and raw output: `work/top4b/ftm/` (see PROGRESS.md there).

## TL;DR
- **FTM's queen policy is simple and map-free.** Before her crown (about r210-260) she is L2-3 on 87% of her turns
  and splits 2 off at L4, keeping L2. She refuses pockets and dead ends, never starts a head-on, almost never
  sprints, and never dies by her own body.
  - From about r210 on every map, L2-3 feeders kill themselves next to her (NoValidAction). She eats each drop within
    about 2 rounds and reaches L10 by r208-260.
- **Our queen dies by her own hand in 40 of 153 clean games (26%); theirs in 5 of 198 (2.5%).**
  - 38 of our 40 had a boxed turn (no legal move) in the 12 rounds before death.
  - 36 of the 40 had a split in those same 12 rounds. This is the QBOX/QBOX_K2 shed chain: L5, no move, SPLIT 2,
    L3, no move, dead.
  - 29 of the 40 were L5 or longer within the last 30 rounds.
  - 6 of the 40 are the Stripes r13 deaths, which are the vault pump working as designed.
- **Three quantified differences, all in the queen's own rules:**
  1. QG_MIN=5 floor. We are L4-6 on 57% of turns and box at L5-8 (71 of 91 box events); FTM is L2-3.
  2. Pocket entries. When an open alternative exists, we take a pocket 40% of the time; FTM 10%.
  3. QS_EARLY_RAM. Our queen started 9 head-ons (both die); FTM's started 0.
- **Prototype FTMQ** (floor 2 plus pocket veto, never-identified maps only, until r300; `work/top4b/ftm/bot`):
  pooled vs b4 is **.478** (972000) and **.469** (977000), so 216/456 = .474. That is below the .48 bar.
  - Variant floor 3 plus veto: .500 and .500.
  - Variant pocket veto alone: .482 (972000).
  - Locally the floor-2 queen boxes far less (35 v 55 box events), but self-deaths don't drop (17 v 14). Allies seal
    the small queen instead. Floor 3: 12 v 14 self-deaths, but 20 v 18 enemy kills.
  - **No ship.** Nothing here beats qf1.
- **Small maps:** both teams use the same split rule (split 2 off at L4). FTM's r0-100 lead is 1.5-2x more eats and
  splits, carried by more unit-turns: Autarky 117 v 78 eats, Trophy 92 v 52, weakhold 80 v 44, Devil 140 v 78,
  TD 62 v 35. Default and QoS are even. FTM loses more L2s to boxes, not fewer: its foragers are disposable.

## 1. Data and method
- 198 FTM-vs-us replays: replays/top4_ftm 137 (6-8 Oct) and replays/ftm_oct5 61 (4-5 Oct). Sides come from
  replays/ab_server/games.json.
- Our side, "US": 153 games. The 45 played 7 Oct 04:00-19:30 UTC are dropped, because v61 may have played them
  (TOP4_FTM_OCT8 attribution warning). The rest are b3/cm1/b4/kf1, which share QG_MIN, QBOX/QBOX_K2, QSPLIT_ROOM and
  QS_EARLY_RAM.
- `qtrace.py` rebuilds every queen turn of both queens, r0-500. For each legal first step it records:
  - the static flood area, with and without portals (bodies as walls);
  - the onward free degree;
  - the BFS distance from every enemy head, and whether that head's kamikaze reach K(L) = ceil(L/4) + (L-2) covers
    the tile;
  - pearl, portal, and spawn distance.

  It also records the action taken, eats with their corpse source, splits and deaths. `agg.py`, `selfd.py`,
  `econ.py`, `feed.py`, `games12.py`, `units.py` and `nva.py` are the read-outs.
- "Pocket" means a tile whose static flood area is 8 or less. "Danger" means a tile inside some enemy head's
  kamikaze reach, or next to an enemy head. A risk counts as "available" only on turns where a non-risky legal
  step also existed.

## 2. FTM's queen policy as explicit rules (198 games)
| # | rule | FTM | ours (153) |
|---|---|---|---|
| Q1 | size before the crown: share of turns at L2-3, r10-249 | **87.5%** (L4 6.4%) | 35% (L4-6 57%) |
| Q2 | split trigger: at L4, SPLIT 2, keep 2 (r6-249 median L4, keep 2); per-turn split rate at L4 | 17% | 1% at L4-6, 52% at L7 (keeps 5 = QG_MIN) |
| Q3 | max length in the r25/50/100/200 snapshots | **4** | 7-10 |
| Q4 | opening shed: first queen split in r0-1 | 102/198 | 17/153 |
| Q4 | opening shed on Slithery | L26 to L3 by r10-11, 2 per round | stops at L5 (QBOX_K2) |
| Q5 | pocket (area 8 or less) taken when an open step exists, r0-100 | **9.9%** (71/719) | 39.9% (314/786) |
| Q5 | same, area 20 or less | 12% | 40% |
| Q5 | dead end (0 onward exits) taken | 3.6% (10/278) | 22% (46/207) |
| Q6 | danger tile taken when a safe one exists, r0-100 | **18.7%** (58/310) | 44% (73/165) |
| Q7 | queen starts a head-on (both die) | **0/198** | 9/153 (victims L2-3; 4 W / 5 L) |
| Q8 | 2+ step moves r0-100 (paid or free sprints) | 23 of 17,100 (0.1%) | 1,324 of 10,828 (12%) |
| Q9 | portal step taken when a non-portal step exists, r0-100 | 19% (24/124) | 35% (92/263) |
| Q10 | roaming: mean spawn BFS distance r0-50 / r50-100 / r100-200 | 10.7 / 9.6 / 4.3 | 8.1 / 9.3 / 5.1 |
| Q10 | roaming: max distance (median game) | 17-19 | 11-13 |
| Q11 | crown: first round at L10 or more (alive queen) | r208-260 on 12 map types | Maze/Portals/Trauma, plus 5 games on AUNSW/Islands/Slithery |
| Q12 | feed: own-corpse eats by the queen per game, r200-299 / r300+ | 6.1 / 9.1 | 0.6 / 6.0 |

Notes on the rules:
- **Q10, roaming is not the difference.** FTM's queen forages as far as ours before r100 (Trophy max 27, weakhold 45),
  and both hover within about 5 of spawn from r100 to r200. "She stays near spawn" (TOP4_FTM_OCT8) is true only
  after r100.
- **"Move vs wait".** There is no wait action, so a queen either moves or splits. FTM's queen "waits" only by
  splitting at L4. Otherwise she walks open ground: 2,645 of 17,100 of her moves before r100 were forced (one
  legal step), against 2,130 of 10,828 for ours.
- **Feeding.** 3,106 of the 3,193 own-corpse pearls the FTM queen eats come from NoValidAction deaths of L2-3 units
  (deliberate suicide next to her). The median delay from drop to eat is 2 rounds (p75 3). Ours: 4 (p75 6),
  mostly HitSelf feeders.
- **Deaths.**
  - FTM: 95 rammed by an enemy head (48 before r100), 4 NoValidAction boxes (L2-3), 1 allied head-on.
    0 HitSelf, 0 own-body.
  - Ours: 67 rammed by an enemy, 9 head-ons she started, 26 HitSelf, 11 into an ally body, 3 allied head-ons,
    1 into an enemy body.
    Enemy-caused deaths are 67/153 (44%) for us and 95/198 (48%) for FTM; the extra deaths are all self-caused.

## 3. Our queen's self-deaths (40/153) against the code
`selfd.py` lists all 40. The dominant shape is the box chain, for example 1416135 AUNSW:
`44:L6/1W 45:L6/1W 46:L6/0S2 47:L4/0S2 48:L2/0E dead`. Read each item as round:length/legal-moves then the action.
She walks a one-way corridor at L6, has 0 legal moves, QBOX splits 2, still 0, splits 2, and dies at L2.
- **Box events** (first turn with 0 legal moves, r12 or later):
  - Ours: 91, 0.59 a game. Her length was L5-8 in 71 of them.
  - Ours, sides blocked: kelp 149, her own body 137, allies 71, enemies 7.
  - FTM: 66, 0.33 a game. 47 of them are at L8+ (crowned, fed coil, r250+). Only 16 are at L7 or below in 198
    games.
- **Why size matters.** An L3 queen can't block herself: her tail is never next to her head. An L4-6 queen walking a
  corridor fills it, and from L5 QBOX_K2 sheds 2 a turn while she stays boxed. FTM keeps the queen at L2-3
  (rule Q2), so her body can't close her exits.
- **Code paths:**
  - `qgCap()` (main.cpp ~3167) has QG_MIN=5 from QG_FROM=20 (or 4 units). At L4-6 she can't split. At L7 she
    splits 2 and keeps 5.
  - The early floor (~6195) makes her keep 3 before r20.
  - QSPLIT_ROOM (`qsrBlock`) blocks a split when an ally head is within 2.
  - The dead-end veto (`eo.dead = qGuard() && area < need`, need = L+3, Voronoi area) acts only from r20. Before
    r20 POCKET_PUMP may even send her into a pocket.
  - QS_EARLY_RAM=1 lets the r<100 queen ram strictly shorter heads, a trade both lose (9 cases).
- **Previously traced single cases still stand** (TOP4_FTM_OCT8). 1278124 (a portal-blind QALLY_KEEP gate) is one
  of the 14 ally-caused deaths here. 1373837 (a forced ally move) falls in the 7 Oct window, so it is outside this
  count. The other 13 were not traced one by one, but `selfd.py` shows a boxed turn before 11 of them (all 11 ally-body deaths).

### The 2-3 differences that cause the self-deaths
1. **Split floor.**
   - Ours: QG_MIN=5 from r20, and 3 before. FTM: 2.
   - Result: we are L4-6 on 57% of turns and box at L5-8 (71 of 91 box events). FTM: 16 pre-crown box events in
     198 games.
   - This is the main one: 29 of our 40 self-deaths were L5+ within 30 rounds.
2. **Pocket and dead-end entries.**
   - With an open alternative we take a pocket 40% of the time and a dead end 22%. FTM: 10% and 3.6%.
   - Our veto is late (from r20) and L-relative (area < L+3).
3. **QS_EARLY_RAM.**
   - 9 queen-started head-ons, against 0 for FTM.
   - Smaller (6% of games) and mixed (4 W / 5 L).
   - (Threat-tile entries, 44% v 19%, are QE_KR's job in qf1 and are not counted here.)

## 4. Small maps r0-100 (Autarky, Trophy, Default, weakhold, plus Devil, TD, QoS, PD)
Medians per game (`econ.py`):
| map | units r50 / r100 (FTM v us) | mass r100 | eats by r100 | splits by r100 | unit self-type deaths by r100 |
|---|---|---|---|---|---|
| Autarky | 15 v 15.5 / **23.5 v 16.5** | 56.5 v 39.5 | 117 v 78 | 59 v 40 | FTM 24 NoValidAction / ours 14 HitSelf+body |
| Trophy | 6 v 6 / **5 v 1** | 12 v 2 | 92 v 52 | 37 v 19 | 0.5 / 0 |
| Default | 11 v 10 / 14 v 18 | 37 v 44.5 | 50 v 62 | 23 v 27 | 2 / 2 |
| weakhold | 8 v 5 / 13 v 13 | 32 v 38 | 80 v 44 | 39 v 17 | 29 / 5 |
| Devil | 10 v 7.5 / **16 v 4.5** | 38 v 10.5 | 140 v 78 | 58 v 33 | 21 / 7.5 |
| Tower Defense | 3 v 2.5 / 13 v 6.5 | 34 v 18.5 | 62 v 35 | 25 v 12.5 | 7 / 4.5 |
| Queen Of Spades | 7 v 6 / 9 v 11 | 21 v 27 | 50 v 44 | 21 v 18 | 8 / 5 |

- **The split rule is identical.** Both teams split 2 off at L4 (median parent L4, child 2). The difference is
  volume:
  - FTM's units eat 1.5-2x as many pearls by r100 on Autarky, Trophy, weakhold, Devil and TD.
  - Per unit-turn the rates are close (FTM 0.08-0.15 eats, ours 0.06-0.16).
  - So the gap compounds from more units alive sooner.
  - On Trophy our units die to head-ons (we hold 1 unit at r100, FTM holds 5).
- **FTM's L2s are disposable.**
  - On Autarky, weakhold, Devil and Trophy, 679 FTM units died NoValidAction by r100 (30 games). 586 of them were
    boxed, and all were L2-3.
  - Ours: 197 boxed HitSelf or ally-body deaths.
  - FTM's foragers dive into dead ends for pearls and die there. On weakhold they do it from r8:
    1294562 ids 4 and 6 eat 3 each in r8-13, split 3 off at L5 (the child takes the bulk out), and the stub dies
    next turn.
  - We have the same pump (POCKET_FACTORY/PUMP_TIP_SPLIT), but WH_NOPUMP switches it off on weakhold
    (weakhold eats by r50: 8 v 30).
- **Unit traces:**
  - 1294559 Autarky: FTM id4 walks (22,2) to (0,6) by r100, eats 8 and splits 4 times. Our id5 eats 3, splits
    twice and dies HitSelf at r29.
  - 1383474 Trophy: the FTM queen herself is the factory (splits at r4, 13, 23, 35, 42, 57, 79, 99, each 4 to 2).
    FTM child id6 eats 13 and splits 6 times by r100. Our queen is L5-8 over r32-54 and splits 2 off at L7-8, keeping 5-6, six times (QG_MIN).
    Our best unit (id12) matches FTM's id6 (12 eats, 6 splits) but is born at r36.
- **TD:** their first split is at r43 v r48.5. The centre race is FTM_OCT5's PM_TD_PULL story.

## 5. The 12+ traced games
`python3 work/top4b/ftm/games12.py 1298471,1282773,1303411,1282385,1294559,1383474,1274172,1294562,1416135,1274170,1269890,1164507,1261405,1265977`
prints, for each game:
- the queen's length path at r0/10/25/50/100/200/250/300/499;
- max spawn distance;
- splits (round:L>keep);
- pockets and danger tiles taken / refused, with two refusal examples;
- the death.

Patterns:
- **Slithery 1298471 / 1282773.** Both queens shed 26 to 5 in r0-9. FTM's goes on to L3, then walks at L3 in
  open ground (refusing area-1 tiles), and crowns at r250. Ours stops at L5 and dies at r28 (HitSelf L2) /
  r51 (ally body L5).
- **Portals 1303411.** FTM refuses 30 of 36 pockets (r10 E area 227 over N area 2). Ours dies r29 at L3 after a
  split at r26 (4 to 2).
- **Trophy 1383474.** FTM's queen: 8 splits 4 to 2, alive. Ours: L5-8 at r32-54, splits 2 off at L7-8 six times,
  rammed r57 at L5.
- **weakhold 1294562.** FTM refuses 28 of 30 pockets and crowns at r250. Ours takes 15 of 22 and dies r172 (ally
  body, L2) after 171 rounds at L4.
- **AUNSW 1416135, Islands 1261405, QoS 1269890, Australia 1164507.** All end in our box chain (section 3).

## 6. Prototype FTMQ (never-identified maps only)
`work/top4b/ftm/bot` = bot/ (with the qf1 `World::neverKnown()` gate) plus FTMQ, with `#define FTMQ 3` at the top of
params.hpp. Defaults are 0 in the params block. About 50 lines in main.cpp:
- `ftmqOn()` = FTMQ && queen && round < FTMQ_TO (300) && w.neverKnown().
- **Bit 1:** split floor FTMQ_MIN (2) in `qgCap` and in the early floor, so she splits 2 off at L4 like FTM. From r300
  the old floor returns, so she can regrow for the r500 queen tiebreak.
- **Bit 2:** pocket veto.
  - `eo.dead` is set when a time-aware flood from the step is smaller than max(L+3, FTMQ_AREA=10).
  - No POCKET_PUMP for her.
  - The QGUARD dead-end veto runs from r0, and never swaps into a more threatened step.
- Variants (same code, other top defines):
  - `bot_f2`: bit 2 only.
  - `bot_m3`: both bits with FTMQ_MIN 3, so she splits 2 off at L5 and stays L3-4.
  - `bot_f1`: bit 1 only (not run).
- Checks:
  - Known map: Trophy seed 1000, cand vs b4 and b4 vs b4 give the identical result line ("A wins after 93 rounds").
    The gate is the qf1 sticky bit, which already passed its 40/40 identity check.
  - Unknown map: rt2028_05 changes. Our queen is L2 on 70% of turns r10-299 (b4: L4 100%).

unseen_eval vs variants/b4, sets real / realhold / blind17, `--seeds 1`:
| build | seed-base | real | realhold | blind17 | pooled |
|---|---|---|---|---|---|
| FTMQ=3 (floor 2 + pocket veto) | 972000 | 41/80 .512 | 38/80 .475 | 30/68 .441 | **109/228 .478** |
| FTMQ=3 | 977000 | 41/80 .512 | 33/80 .412 | 33/68 .485 | **107/228 .469** |
| bot_f2 (pocket veto only) | 972000 | 40/80 .500 | 39/80 .487 | 31/68 .456 | 110/228 .482 |
| bot_m3 (floor 3 + veto) | 972000 | 40/80 .500 | 39/80 .487 | 35/68 .515 | 114/228 .500 |
| bot_m3 | 977000 | 43/80 .537 | 38/80 .475 | 33/68 .485 | 114/228 .500 |

**Mechanism check** (`mech2.py`, 20 real_gen/tune maps, seed 972000, both sides; cand vs b4 against b4 vs b4,
replays in `work/top4b/ftm/mech/m972/`; bot_m3 in `mech/m972m3/`):
| | FTMQ=3 | b4 |
|---|---|---|
| score | 22/40 | 20/40 |
| queen turns at L<=3 / L>=5 (r10-299) | 75% / 10% | 21% / 55% |
| box events (0 legal moves, r12+) | **35** | 55 |
| boxed (QBOX) queen splits r0-100 / r100-300 | **6 / 16** | 42 / 43 |
| pocket taken / available, r0-100 | 61/222 (27%) | 96/298 (32%) |
| dead end taken / available, r0-100 | 8/80 (10%) | 35/147 (24%) |
| queen self-caused deaths (HitSelf, ally body, NoValidAction) | **17** | 14 |
| queen alive r100 / r300 / r499 | 18 / 8 / 7 | 25 / 10 / 7 |
| allies within 4 of the queen (median of game means) | 1.67 | 1.39 |
| bot_m3 (floor 3) on the same 40 games | score 22/40, L<=3 40% / L>=5 18%, box events 50, self-deaths 12, enemy kills 20 (b4 18), alive r100 21 (b4 25) | |
| queen turns with 2+ sides blocked by her own body | 11.8% | 20.4% (FTM server 2.7%) |

**Reading.**
- The prototype does what FTM's queen does: she is small, boxes far less and hardly sheds. But her self-deaths don't
  fall (17 v 14). The deaths move from the L5+ box chain to an L2-4 queen sealed by allies, often her own fresh L2
  children.
  - Examples: rt2028_02 A r64 `L4/0 [self,self,ally,ally]`; rt2028_17 B r49 she splits 4 to 2, and at r52 she is
    boxed by ally, self and kelp.
  - Allies around her rise (1.67 v 1.39 within 4).
- FTM's children don't disperse faster than ours. Child distance from the queen is a median 4/5/6/7 at +1/3/5/10
  rounds, ours 5/5/6/6 (`kids.py`). FTM's allies block a side of their L2-3 queen
  more often than ours do (7.7% of her turns, against our 4.9%).
  - So the seals in our local games come from denser boards plus b4's own units: free sides of 1 or fewer on 34-37%
    of queen turns locally, against 19-21% on the server.
  - Not resolved.
- Local queens mostly die to enemy head-ons before r100 on these maps (cand 15, b4 18 of 40), so a self-death rule
  moves few results. That fits every build landing at .47-.50.

**Verdict: no ship.**
- FTMQ=3 is below the .48 bar on both seed bases (pooled 216/456 = .474).
- The single bits are neutral at best: pocket veto alone .482 (972000), floor 3 plus veto .500 on both seed bases
  (228/456). Locally floor 3 trades 2 fewer self-deaths for 2 more enemy kills.
- The opponent is our own b4, which doesn't lunge or hunt the queen like FTM. That was always the limit of this test:
  it can catch a regression, not show a gain against FTM.
- With this evidence nothing here beats the qf1 build (QE_KR + UNK_PORTAL_SIDES).

## 7. What this means for the Qualifier and after
1. **Don't copy the floor.** FTM's L2-3 queen survives because the whole team plays around her:
   - feeders die next to her, never in her corridor;
   - foragers leave;
   - she crowns at about r220.

   Copying only her size moves our deaths from self-boxes to ally seals (section 6).
2. **QS_EARLY_RAM is a clean candidate for later.** 9/153 queen head-ons that we started against 0/198, every
   victim an L2-3 non-queen. Gating it off on unknown maps is a one-line change (`(FTMQ & 4)`-style, not built).
   It is too rare (6% of games) to measure locally before the freeze.
3. **The box chain is real.** 38/40 of our self-deaths pass through a 0-legal-move turn, and QBOX_K2 sheds 2 a turn
   while still boxed (the 1407454 / 1151983 Portals chains are this). QBOX_ONESPLIT (FTM_OCT5) covers the crowned
   case only (r200+). A pre-crown version is the post-Qualifier lead, together with an ally-avoidance ring that
   scales with the queen's free exits.
4. **Crowning.** FTM crowns a living queen at r208-260 on 12 map types, through feeder suicides 1-2 tiles from her
   (eaten within 2 rounds). It is the same lesson as TOP4_SYNTHESIS action 5: a redesign, not a pre-freeze flag.
5. **Small maps.** The r50-100 economy gap is volume (more units alive sooner, disposable L2 foragers diving into
   pockets), not a different split rule. On weakhold, WH_NOPUMP turns off exactly the dive FTM uses from r8
   (our eats by r50: 8 v 30). That is a known-map flag; worth an unranked block after the freeze if the server is free.
