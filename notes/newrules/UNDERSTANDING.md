# Why b3 wins and loses (decision-level study, 2026-10-05)

Corpus: every server game played by f1 / cm1 / b3 (plus b1, l1, k2, q1, v61, h1 as contrast) on all 17 maps,
about 800 games. Six map-group studies watched the losses turn by turn, then a second pass replayed the claimed
decision points in the sandbox harness (exact b3 zip, every base decision MATCHes the server) and tested a
counterfactual flag on each. Per-group notes, tools and scratch bot copies:
`/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/dgu/<group>/notes.md`
and `.../dgu/root-<group>/bot` (flags default 0, plays identically to b3 with flags off).

Read this file as: what the games say, then what the harness confirmed, then what to test.
Win ratios are not used as evidence anywhere below.

---

## 1. The one-paragraph version

The r500 tiebreak is **queen length first**, and most of our results are decided by the two queens, not by fights
or mass. We win when **their** queen dies (we kill her head-on with a small unit, or she dies on her own) and
we have more mass for the longest-dragon tiebreak. We lose when **our** queen dies while theirs lives, and this
happens in a small number of repeatable ways: she walks through a portal into a tiny room before r100 (Australia,
Slithery), she forages into kamikaze reach of L2-4 heads before r100 (Devil, Trophy, Autarky, TD), she is crowned
on Maze and fed in an emptied home field that enemy hunters walk into, or she coils into her own body on Portals.
On top of that, our L8+ "kings" skip **certain** enemy-queen kills after r300 because of one early return in
`tryRam`, and on three maps our map knowledge is wrong or too weak (TD centre is discounted to zero, Schooltime
layout B doors are modelled as kelp, Trophy allows a 1-for-1 ram at r7-9). Economy waste (stillborn children,
ally jams) is real but sits at the same rate in wins and losses; s1 and c1 already showed blocking it costs more
than it saves.

Several plausible-looking causes from the first pass were **wrong at the decision level** (section 3). Those are
the ideas we would otherwise have churned versions on.

---

## 2. How we win and how we lose, per map group

### Portals / Maze (113 games: Portals 44-14, Maze 18-37)
- **Portals wins:** the park works (queen alive at r300 in 58/58). Fed to L38-56, she wins when their queen died
  on its own (15 wins) or our roaming L2s killed it (7), or both alive and ours longer. But 21/58 crowned games
  have a long shed chain, wins included: the margin is thinner than 44-14.
- **Portals losses (14):** 7 are our crowned queen dying HitSelf at L2-3 after coiling into a self-made seal
  (in 4 of them their queen was already dead), 3 more lost the queen race after big sheds, 4 lost the race to
  DEV/FTM who funnel 60-85 non-queen mass into their queen after r400.
  *Decision level:* the trap is not a static map dead end (static pockets are already banned by qparkScore). In
  1155622 r422 the 4-step sprint EEEN enters a region bounded by her own coil whose time-aware area (41) just
  passes `need = L+3 = 40`; one turn later the area is 7. `bfsFromImpl` assumes her tail retracts, but a fed
  queen eats every 1-2 turns so it doesn't. 4 of 6 collapses are still unexplained.
- **Maze wins (18):** in 15 of them no enemy head entered our 264-tile home field after the crown (0.0-0.2 enemy
  heads per queen turn); their queen often died on its own.
- **Maze losses (37):** 25 are the crowned L25-80 queen rammed at r320-497 by an L3-8. At r300 `shouldFeed()`
  sends every small unit on a direct feed walk/suicide into her (these bypass `evalDir`), the field goes from ~30
  of our units at r250 to ~5 at r325, and enemy heads in the field jump from 0.1 to 1.1-1.5 per turn. Same
  opponent, win vs loss: the only difference is whether hunters got into the field. In 10/25 rams their queen was
  already dead or L<=7, so any living queen of ours would have won.
  *Decision level:* her threat model is not the binding constraint (full kamikaze reach flips 0/27 final moves;
  that is why k2 failed). What binds is her move set: FS_VIS limits queen sprint endpoints to her visible zone,
  and the Maze park band (`PM_MAZE_QX=9`, -600 and `qparkBan`) forbids the escape squares. 1164516 r337: both
  candidates carry -600, FS reports 0 paths, she steps E at margin 1 and dies to ESS. Our nearby small units
  don't engage because `tryRam` only sees heads at distance 1-2 and the Maze `ramGuard` refuses even trades
  (1162273 d711 r341/r343: killer at distance 2, refused, then "feed suicide").

### Big open: Australia, Around UNSW, Islands (156 games, 71-85)
- **The defining fact:** our queen dies in 155/156 games here. Enemy queen alive at r500 -> we lost 42/42;
  enemy queen dead -> we won 71/114. Every win had their queen dead, 66/71 killed head-on by us.
- **Wins:** mass (Australia vault factory, Islands tips) plus an early kill of their roaming L4-6 queen.
- **Losses, queen tiebreak (42):** in 23 of them our longest was >= theirs, so killing their queen alone wins.
  Their queen was in our view in 25 of 42. *Decision level, verified 11/11:* every certain in-view kill we
  skipped was at r>=320 by an L9-29 unit that counts as king (`kingDeclare`: any L8+ that hasn't heard a longer
  king). `tryRam` returns at `(feedPhase() && iAmKing())` before `tryQueenKill()`. 1137705 r320: L10 head,
  her L3 head 3 free steps away on an open path, she has already moved; we walk EE. Lost 0 v 3 queens with
  longest 55 v 20.
- **Australia queen death:** 47/65 games she takes the portal E of (28,39) into the 12-tile vault at r27-73
  and dies inside in 37 (17 of those are wins too). *Decision level:* before `QS_FROM=100` she is scored as a
  worker; the vault is out of view so ally bodies inside are invisible, area 12 >= need 7, and map-known beds give
  +38.8 against ~3.6 for open moves (1164507 r36: E 39.09 vs S 3.63).
- **Losses, longest (39):** we eat more than they do but waste it (Islands r100-300 HitSelf 305 v 41 length;
  45 stillborn per game at (14,21)). Treadmill and jam waste appear equally in wins, so they are not what decides.
- **cm1 on AUNSW** measured an opening bug, not the crowd penalty: the crowd term makes ally id8 seal the queen's
  only exit at r4 (fork at r2) and she dies at r6 in 23/27 games.

### Schooltime, Slithery Fight, Trauma (145 games)
- **Trauma 44-5:** the scripted pen does the work. All 5 losses are queen races lost by 1-8. Two came from the
  queen coiling, and the seal in both was **our own TRA_PENFEED feeder** entering the pen lane through the portal
  (1137690 r317, 1101311 r418), not a queen decision. Three lost by 1-2 with 59-108 length idle in L3 units that
  are not `facBorn` and so never feed.
- **Schooltime** is two server layouts. Layout A 9-10 (close king races). Layout B 5-18 and **0-15 vs strong
  teams**: the server opens 4 door edges into the side-room chambers (115 tiles, 34 of 172 spawn tiles); our map
  data has them as kelp, and any unit that sees an open door drops the known map entirely (1164276 id82 r180
  `map=?`). Chamber eats in B losses: 0/57, 0/119, 0/114 ... us/them. Even with the doors fixed the units stay
  myopic: `PEARL_GAMMA=0.82` discounts a chamber 10-20 steps away to near nothing.
- **Slithery 12-41:** our queen took a portal into the 4-tile U-shaped vault in 31/53 games (theirs 0/53) and
  died there in 20; 11 losses are decided by that. *Decision level:* entry scores like open ground (bfsFrom
  floods through portals, area 500-1000), then the ordinary economy split's child steps onto the only exit tile.
  ~14 more losses are mid-game queen lunge deaths, mostly by heads **out of view** (1164100: only the killer's
  body was visible; computeThreats ignores headless bodies).

### Lanes A: Devil, Trophy, Stripes (125 games)
- **Devil:** we win when our L4 queen reaches the centre farm by r15-20 and survives (28.6 centre eats r20-60 in
  wins vs 9 in losses). We lose when an enemy L2-4 contests the centre and rams her at r15-45 (15/21 losses).
  *Decision level:* 7/10 fatal moves end at distance 2-3 from a visible L3-4 head with threat=0, because before
  r100 `MAX_THREAT_REACH=1` and an L<6 queen pays only `SMALL_THREAT_PEN=12`.
  The "contested Cfarm stillborn pump" is actually a dead-end 2x2 pocket and an `ESCAPE_SPLIT` bug in
  `surviveDepth` (counts a growth split as an escape without checking the child has a free tile); low priority.
- **Trophy:** wins come from splitting early and owning the Cup. In 6/11 losses our second starter rams the
  mirrored L3 at r7-9 (we are the mover 54/54 times) because `PM_TROPHY_RG=0` disables the ram guard there.
  Then our queen/last unit hovers at the bottom portal mouth for 13-40 rounds, pinned by `pearlValue`'s
  never-decaying estimate for unseen Cup tiles.
- **Stripes:** the vault pump outproduces most teams. Losses to VIB/DEV/horse: spare L2s circle the vault
  mouth because bfsFrom still counts a pocket they can't legally enter; the lane kills are forced positions.

### Lanes B: Tower Defense, Prisoners Dilemma, Autarky, Queen of Spades (191 games)
- **TD:** decided by the centre race at r40-80. Winners send the non-queen out at r36 and keep the queen home.
  We do the opposite: the non-queen circles the empty home ring because the centre (28-40 steps) is worth
  0.82^35 = 0.001, and the queen random-walks out and is rammed in the centre. Then we're eliminated, or win mass
  and lose the r500 tiebreak to their queen in her spawn box.
- **PD:** wins are eliminations. 5/13 losses are r500 with 47-109 v 2-3 mass and their L2 queen looping by her
  spawn; no unit of ours ever goes there (EQ_HUNT/LATE_HUNT off, so the enemy-queen tracker doesn't run).
  Note: the bot never identifies PD's second pearl layout (15/15 `map=?`).
- **Autarky / QoS:** our home factory is taken over by DEV. There is no veto loop as first thought; our units
  stop coming because DEV parks a head at the mouth and pocket value drops x0.25. One real bug: `pfDiveOK` uses
  wall-blind `wrapDist` for "enemy-adj". Our early queen is rammed at the centre gates in 25/29 Autarky losses
  after sitting at distance 2 from L2-3 heads for 4-5 rounds.

### Default / weakhold (72 games)
- **Default 25-13:** an opening economy snowball on a pearl-poor map; losses are mostly opening luck plus numbers.
  The "swarm never catches the queen" case was wrong: every cited kill was blocked by kelp.
- **weakhold 17-17:** 8/17 losses are both-queens-alive with ours L4 all game (she ate 0 pearls in 7/8) while all
  feed goes to a non-queen king and their queen is fed L2->9-21. 2 more are king-gate cases (1102507: our L6 king
  saw their lone L2 queen, the last enemy unit, 2 tiles away with E,E free on r336/348/360, walked SS; lost Q0 v 2
  with 74 v 2 total).

---

## 3. Causes the decision-level check rejected (do not build these)
| claim | what the harness showed |
|---|---|
| Maze queen dies because threat reach is underestimated | full K reach flips 0/27 final moves; constraint is the park band + FS_VIS (matches k2 loss) |
| Portals queen coils into static dead ends past the 12-step lookahead | static pockets already banned; KING_SURVIVE_DEPTH 24/40 flips 1-3/6; traps are self-made coils |
| PM_MAZE_QKFROM=400 delays the Maze crown | feeding is driven by `feedStart` (UNK_KING_FEED), not qkFrom |
| Default swarm misses visible queen kills | 0/7 were kills: kelp between |
| P6_kreach saves big units and the mid-game queen | 0/38 flips; killers are out of view |
| Stripes pumpers die from bad lane choices | forced positions, 1 candidate |
| Devil stillborn pump is caused by enemy contesting the farm | dead-end pocket geometry + ESCAPE_SPLIT bug |
| Autarky/QoS factory "occupied" veto loop | 'occupied' fired 0 times; presence problem, not a veto |
| EXITRACE (ally corridor jam) | 2/8 flips, changes 1.7% of turns in wins incl. r1 openings |
| BOX_TAILFIX | real scoring bug, but changes 72/72 games; needs its own A/B, not now |

---

## 4. Ranked fixes (test one at a time)

### 1. QKILL_KING alone, gated to free steps — all maps
- **Cause:** `tryRam` early return `(feedPhase() && iAmKing())` before `tryQueenKill()` (main.cpp ~4646).
- **Implementation:** `-D QKILL_KING=1` (exists, params.hpp:1679, qkkAllowed/QKK_KEEP_LEN=20) plus a new gate
  `QKK_FREE=1`: only take it when path length <= freeSteps(myLen) (no long paid paths; 1161893 had a 23-step one).
- **Harness:** 11/11 big-open failure points flip to a certain kill; fires in 15/42 "their queen alive" losses, 4
  of them plausibly flip (1137705, 1162103, 1161366, 1165648). weakhold variant (QKK_WH): 0/42 wins change, 4/30
  losses change, each first change a certain kill (1102507 = elimination). 6/8 big-open wins byte-identical; 2
  fire earlier on a queen we killed later anyway.
- **New angle vs h1:** h1 bundled LATE_HUNT's map-wide movement; QKILL_KING alone was never server-tested.
  The QKK_FREE gate is not yet re-run in the harness: rerun the 11 points before staging.
- **Risk:** the killer (sometimes our longest) dies; with our queen dead, longest decides.
- **Server metric:** share of games with their queen alive at r500; king queen-kills per game; on
  Australia/AUNSW/Islands/weakhold specifically.

### 2. QVAULT — queen never enters a small portal-only room (Slithery, Australia)
- **Cause:** bfsFrom floods through portals, so a 4-tile (Slithery) or 12-tile (Australia) portal room scores like
  open ground; pre-r100 queen has no blind/portal penalty.
- **Implementation:** two scratch versions share the name and must be merged into one flag:
  (a) root-school-slither-trauma: `isVault` = plain-graph component <= 6 tiles with only portal exits; -500 for
  entering or stepping onto a mouth with all non-vault exits occupied; `qsrBlock` while inside; gated `!RP.qPark`.
  (b) root-big-open: Australia only, before qsOn, -60 for a portal step whose area < 30.
- **Harness:** Slithery 9/9 entry points flip; Portals queen 100% unchanged; Schooltime A wins unchanged.
  Australia 9/9 flip; 8/13 wins unchanged, 5/13 change at the same vault-entry move (queen died there in those
  wins too).
- **New angle vs v69/q1:** v69 penalised every portal/blind step and q1 parked her; this touches only one tile
  class that the opponent's queen never enters (0/53 on Slithery).
- **Risk:** loses 1-4 early vault pearls per entry; Australia queen gives up some early growth.
- **Server metric:** queen vault entries per game (Slithery 31/53 -> 0), queen alive at r100 on Slithery and
  Australia, r500 "our queen dead / theirs alive" share on those maps.

### 3. PM_TROPHY_RG=2 — Trophy only
- **Cause:** ramGuard 0 on Trophy, so the r7-9 equal L3 head-on trade always fires.
- **Implementation:** existing flag, `-D PM_TROPHY_RG=2` (local-numbers guard, same as Devil).
- **Harness:** 5/5 loss rams flip to safe moves; 12 Trophy wins 99.3-99.98% unchanged (also removes the
  1102831 win-contrast ram).
- **Risk:** blocks every equal ram on Trophy when we are not locally ahead.
- **Server metric:** Trophy result vs 2000+ non-top teams (where the trade was 4-11 vs 32-7), r20 unit count,
  queen first split round.

### 4. PM_TD_PULL=2 — Tower Defense only, non-queens, r<100
- **Cause:** PEARL_GAMMA discounts the centre field to 0.001, so the starting non-queen circles the empty ring.
- **Implementation:** root-lanes-b `tdPullScore`: +2 per BFS step closer to the centre field (x13-18) until
  within 2 of it.
- **Harness:** away-from-centre moves r0-60 fall 141 -> 38 of 427 across 7 losses; 3 cited points + the key
  r16/r0-3 turns flip; 5 wins change 1-9 moves, all toward the centre; queens unchanged; flags-off 100% verify.
- **New angle vs l1/q1:** they parked the queen and left the non-queen late; this only sends the non-queen.
- **Risk:** queen still random-walks out (pair later with an early-queen threat fix).
- **Server metric:** our first centre arrival round (target < r44), centre heads at r60/r70, r100 total vs
  DEV/FTM/horse, TD eliminations.

### 5. QG_RAM — Maze crowned-queen guard by trade
- **Cause:** home-field allies refuse even trades with the queen's hunter (`ramGuard`), and nothing targets
  intruders.
- **Implementation:** root-portals-maze: in `tryRam`, an enemy head within 8 of the queen's last tile or (Maze,
  qPark==2) inside our home field (frame x <= 11) is always worth it for our L<=6 units and skips ramGuard.
- **Harness:** flips 3/15 ally points (1162273 d711 r341/r343 now ram the eventual killer 3-5 rounds early); 1
  action changed in ~49k turns of Maze wins.
- **Risk:** small. Only covers intruders within 2 of an ally (minority). Follow-up, once this is read:
  `PM_MAZE_FEED~400` (Maze-only `RP.feedStart`; footprint 55-87 decisions at r300-325) to stop emptying the
  field, then `PM_MAZE_FLEE` (3/27 rams flip). Each separately.
- **Server metric:** Maze crowned queen alive at r500, enemy heads in our field per crowned turn.

### 6. SCH_DOORS (+ SCH_CHAMBER) — Schooltime layout B
- **Cause:** layout B door edges modelled as kelp; seeing an open door drops the known map.
- **Implementation:** root-school-slither-trauma: SCH_DOORS opens the 4 door edges and makes an open door
  consistent with Schooltime; SCH_CHAMBER pulls L<=4 units at r30-299 toward the chambers (max 2 allies inside).
- **Harness:** layout A wins unchanged (only rare CPU-budget FS turns differ); doors alone flip 1/8 B points,
  doors+pull 4/8; B wins change 14-16% of turns (intended).
- **New angle vs PM_SCHB (m1, lost):** PM_SCHB was B-layout keepers; this fixes the wall model. Do SCH_DOORS
  first (pure correctness), and run a local B game on `sch_1164105.map` before the chamber pull goes to the server.
- **Server metric:** chamber eats per B game (target > 30), our spawn eats, B-layout results vs strong set.

### Next tier (evidence real, not yet decision-verified or too narrow)
- `WH_QCROWN` (weakhold, crown queen from r300, no park): 8/17 weakhold losses; nothing changes before r300 in
  any game; q1's weakhold sub-result 9W-4L both-alive. Harness can't score feeding.
- `QE_THREAT_PEN` / `QE_KR` (early queen threat on lane maps): 21/21 changed moves go away from enemies,
  7/10 Devil points flip; but sits next to v69/l1/QKREACH losses, so gate to Devil/Trophy/TD/Autarky and test
  after fixes 3-4.
- `QK_EQDEAD` (stop crowning once their queen is seen dead): flips 1/3 tested; detection is the weak link.
- `LA_PEST` (Trophy hover), `KGHOST`, `QFORCE`, `PM_POR_RES`, `TRA_MERGE` + feeder door-lane fix: narrow or
  footprint-only.
- Prerequisite bug for any spawn sweep: `guessFrame()` gives split children the wrong frame (TD 1138634 d15
  swept OUR queen's spawn). Applies to h1/LATE_HUNT too.

## 5. Built (builder run, 2026-10-05)

All six fixes are in `bot/` behind their own flags, all defaulting to 0 (main.cpp, params.hpp, maps/schooltime.hpp,
uncommitted; the pre-edit copy is in `archive/build_partial_20261005/`). With every flag off, bot/ plays the same
games as variants/b3: sandbox seed 1000 on australia, devil, portals and queen_of_spades, bot on both sides, gives
8/8 identical result-line hashes (run after the last main.cpp edit).
The harness (`tools/decision_replay.py verify`) on flags-off bot matches 100% of turns on Trophy, TD, Maze, Slithery
and Australia (queen). Schooltime has 166 noise turns in 5 games and big-open has a few 1-turn CPU-budget swaps
(ES/SE). The counts below have that noise subtracted.
Staged candidates (= bot/ minus .unswbc-build/*.orig, with the #defines prepended to params.hpp; checked identical to
bot/) are in `scratchpad/dgu/stage/<flag>/`. Scripts and logs: `scratchpad/dgu/builder/` (vp.py, summ.py, smoke.sh, ident.sh).
Smoke: 4+ sandbox games for each stage against variants/b3, Australia included. No errors, and our max CPU is 33.8M or less.

| stage | defines | failure points | wins changed | smoke notes |
|---|---|---|---|---|
| QKK_FREE | QKILL_KING=1 QKK_FREE=1 | 10/12 big-open points flip to a multi-step kill path (1137705 r320, 1162103 r492, 1161366 r458+r477, 1165648 r481, 1104003 r372+r387, 1164290 r451, 1137738 r423, 1105653 r408). 1152153 r393 (L5, 2 free steps) and 1162103 r489 do not flip: the free gate removes them. Big-open losses: 10/82 change. weakhold/Default losses: 4/30 (1102507, 1102529, 1134002, 1164610) | big-open 10/74, of which about 6 are real kill moves (1138101, 1136357, 1152426, 1166062, 1134249, 1138635); the rest are 1-turn noise at 30M+ points. weakhold/Default 2/42 (1139368, 1137700; this ungated version fires where QKK_WH did not) | AUNSW, Australia, Islands, weakhold: same results as ref |
| QVAULT | QVAULT=3 | Slithery: queen-only verify changes 21/37 losses at r17-44 (entry rounds). Australia: 19/31 losses, 1-4 turns at r32-62. Bit 1 alone does nothing on Australia (0/65 games: no portal room of 6 tiles or fewer); all Australia changes come from bit 2 | Slithery 10/12 wins change (the queen enters vaults in wins too, and survives). Australia 17/34, 1-7 turns at r30-95 | slithery A/B won; australia as B the same as ref. **australia as A lost 21-41 (ref won 57-44)** |
| PM_TROPHY_RG | PM_TROPHY_RG=2 | 5/5 r7-8 equal rams flip to non-rams (1152532, 1165828, 1164098, 1164988, 1137702). Trophy losses 11/11 change, 1.8% of turns | 26/26 wins change but only 0.12% of turns (it refuses every equal ram; 1102831 r8 contrast ram flips) | trophy A won in 69 rounds (ref 93), trophy B won in 136 |
| PM_TD_PULL | PM_TD_PULL=2 | 1162275, 1164525 and 1165647 r40 W->S, 1166190 r16, 1152346 r0-3: all flip. 21/21 losses change (1.2%) | 21/21 change (0.41%, from r0, toward the centre) | TD A won (elimination r288), TD B lost (r86); ref b3-b3 = B wins r133 |
| QG_RAM | QG_RAM=8 | 1162273 d711 r341 W->NN, r343 S->EE, 1100870 d879 r392: all flip. Maze losses 14/30 (53 turns) | 6/13 (15 turns in 230k) | maze: same result as ref (B 23-0) |
| SCH_DOORS | SCH_DOORS=1 | 1/4 sampled B points (1164948 r52); 1165061 r59/r68 and 1161529 r74 do not flip. Layout-B losses 17/17 change (3.1%) | layout A: 0.00-0.01% (CPU-budget turns only, also in losses); layout-B wins 5/5 (8.2%) | sch_1164105, schooltime, schooltime_b3 and B-door maps: mixed, as expected for one seed |
| SCH_CHAMBER | SCH_DOORS=1 SCH_CHAMBER=1 | 4/4 sampled B points flip (1164948 r52, 1165061 id17 r59 + id3 r68, 1161529 id5 r74). B losses 17/17 change (11.4%) | layout A unchanged; B wins 5/5 change (13.7%) | sch_1164105: A lost 10-11 on total length (ref won 11-7), B won 7-6. Movement-heavy on B: ship after SCH_DOORS |

Read-outs:
- QKK_FREE is the cleanest: every changed decision in a loss is a kill path within the free steps, and the free gate
  costs only the one L5 point.
- QVAULT=3 on Australia is effectively bit 2 alone. Slithery wins change 10/12, so the claim "wins unchanged" does
  not hold there: the vault penalty also re-routes queens that survived their vault trip. The Australia-A smoke loss
  is one seed, but it should be read before QVAULT is chosen. `stage/QVAULT1` (bit 1 only = Slithery-only behaviour) is staged
  as the narrower fallback.
- PM_TROPHY_RG and PM_TD_PULL change every game on their map, as designed (a general rule, not a point fix).
- Not done: server tests (not this agent's job). Nothing was submitted.
