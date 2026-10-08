# forgot to mention (FTM, id 264): current play vs b4, 2026-10-08

Written 8 Oct, about 05:30 UTC (01:30 EDT). Read-only study. Nothing submitted, no challenges, no Discord or browser.
bot/ and variants/ were not touched. Earlier study: FTM_OCT5.md (vs b3). This file only updates what changed.

## TL;DR
- **Same build as 5 Oct, as far as the data shows.** FTM is #2 at 2487. The per-game listing rating stayed at 2487-2499
  for the whole 38 h. Opening fingerprints recur from 5 Oct to 7 Oct (TD, weakhold, Stripes, Australia, QoS, Devil).
  The queen profile, kill-step mix and feeding counts match FTM_OCT5. They play about 250 games an hour, 90% of
  them challenges.
- **Against b4-equivalent code we are 32-74 (30%)** over 106 harness-attributed games.
  - Losses by type: 31 eliminations, 16 queen tiebreaks (our queen dead, theirs alive) and 27 longest-dragon races
    (Schooltime 9, Around UNSW 6, Islands 5, Portals 3, others 4).
  - We win only Stripes (4/4) and Trauma (3/3). Slithery is 0/8, Autarky 0/6, Islands 1/6 and Around UNSW 1/7.
- **Attribution warning.** 18 of the games that upload times label "kf1" were played by **v61** (16388), not kf1;
  the harness matched every turn to v61. Our active submission switched to v61 for part of 7 Oct (between about
  04:00 and 19:24 UTC, interleaved with kf1). Codex flagged the same thing in
  codex-battlecode/notes/server-state-20261007.md. The kf1 verdict in STATUS is contaminated. Every number here
  uses per-game harness attribution (kf1 18798 or b4 18751/19891 = "b4-equivalent").
- **Verified fix for a known-map loss: Schooltime layout B, `SCH_DOORS=1 SCH_CHAMBER=1`.** Both flags already
  exist in b4 and default to 0.
  - FTM farms the side-room chambers from r59-162, eating 119-147 chamber pearls a game. We eat 0-13.
  - In our only layout-B win, we farmed the chambers (101 eats) and FTM didn't.
  - The flags change our moves from r29-42 in 6/6 B losses. Changed moves go toward the chambers 2.3-2.8 to 1.
  - Layout-A games and other maps are byte-identical. A staged copy is ready at
    `scratchpad/top4/ftm/bot/` (= variants/b4 + the two defines).
- **What carries to unseen maps:** FTM's queen dies by her own hand in 1 of 106 games; ours does in 19. FTM's
  queen is alive at the end in 50% of games, ours in 27%. FTM also crowns a living queen at r215-260 on every map
  type. Details in "Generalises to unseen maps" below.

## 1. Who they are and whether the build changed
- Team "forgot to mention", 4 members, record 30112-11-13926. Rank 2 at 2487; aAah is #1 at 2555.
  Leaderboard order: aAah, FTM, horse, Cutlery, larp, dev test 1, SSS, chad gdp, WHQ, glyph, test4, Sponge, ...;
  we are #14 at 2253.
- Crawl: 8,612 completed FTM games from 13:57 UTC 6 Oct to 04:05 UTC 8 Oct.
  - 220-320 games an hour, about 25-60 of them ranked; the rest are challenges.
  - The listing's FTM rating stays at 2487-2499 the whole time. A new upload would show its extra sigma here,
    as it did on 4 Oct.
  - The team page's rank history moves between 1 and 7 many times a day. That comes from others' uploads, because
    FTM's own rating barely moves.
- Behaviour check. Opening fingerprint = FTM's moves in rounds 0-7, hashed per map and side, across the 5 Oct and
  8 Oct samples:
  - These recur unchanged: TD 2ba7c7 (5 Oct and 7 Oct), weakhold 2a1664 (5 Oct and 7 Oct), Stripes 623075
    (5 Oct to 7 Oct 05:03), Australia 008dc2 (5 Oct and 6 Oct), Devil 53a6e4/6c4115, QoS 45e780/37c667.
  - Other maps vary, because our moves and the per-match pearl seed enter their view early.
  - The profile is the same as FTM_OCT5:
    - queen split at r0-1 in 50-57% of games;
    - kill steps 52% 1-step and 35% 2-step;
    - about 180 NoValidAction feed deaths a game;
    - queen crowned at r225-250 on Portals and Maze.
  - **No evidence of a new build.**
- Per-map win rate over these 36 h vs the top 9 (aAah, horse, Cutlery, larp, DEV, SSS, chad, WHQ, glyph; 3,771 games): 50%.
  - Strong: TD 79%, Trauma 78%, Portals 76%, Slithery 59%, Trophy 59%, Devil 58%.
  - Weak: Around UNSW 23%, Australia 34%, Default 34%, QoS 35%, Islands 37%.
  - vs aAah: 0-14% on Default, Islands, QoS, Australia, weakhold and AUNSW.

## 2. Data
- Scratch folder: `/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/top4/ftm/`.
  - `games_264.json` / `g36.json`: the crawl.
  - `team264.json`: team record and rank history.
  - `subs.json`: our submissions.
  - `rows.pkl`: an_top1 rows for all 157 replays.
  - `cls.json`: per-game build from the harness.
  - `attr2*.json`: verify match counts per candidate submission.
  - `v_sch/`, `v_qv/`: counterfactual runs.
  - Scripts: crawl.py, build.py, attr2.py, agg.py, permap.py, prof.py, qt.py MAP, sch.py, qself.py, seal.py,
    who.py, feedeff.py, vsch_an.py, fp.py.
- **Replays: `replays/top4_ftm/`, 157 files.**
  - 137 vs us, every game from 16:00 UTC 6 Oct to 04:00 UTC 8 Oct (cache plus crawl).
  - 20 vs the top 9 (aAah ×4, two each of the others, 7 Oct 04:00 onwards).
- Attribution with `decision_replay verify`, all our dragons, exact submission zips.
  - 106 games are b4-equivalent: kf1 18798 matches 67 (100% of turns); b4 18751/19891 matches 39.
  - 18 are v61 (16388), from 7 Oct 04:02-19:24 UTC.
  - 13 don't rebuild exactly: QoS second layout (7) and the 7 Oct 03:02 series (pearl gaps).
  - kf1 differs from b4 only by QKILL_KING+QKK_FREE. Against FTM that changed 1 turn in 61 games on 5 Oct, so kf1
    games count as b4.

## 3. FTM's current play (vs us; 137 games, 106 of them b4-equivalent)
| | FTM | b4 |
|---|---|---|
| queen alive at the end | **50%** | 27% |
| queen dead before r100 | 30/106 | 47/106 |
| queen self-deaths (HitSelf / own body / own head) | **1/106** | **19/106** |
| queen splits after r5, per game | 5.0 | 3.3 |
| paid lunges per game | 35 | 16 |
| kills with 3+ steps | 11% | 0% |
| portal steps per game | 91 | 138 |
| h2h kills per game | 72 | 72 |

- **Queen policy, the same on every map type.**
  - She stays L2-4 near spawn (9.5 tiles on average).
  - On Slithery she sheds 2 per round at r0-3 (L26 → 19), is L3 by r25, and is never in the vault.
  - She is crowned when alive. First round at L10:
    - Portals r225-306 (7/7), Maze 215-226 (3/3);
    - Trauma 221-260, Autarky 217-264, AUNSW 231-251;
    - Default 228-240, QoS 250-279, TD 250-298, weakhold 247;
    - Slithery queen L3 until r200-250, then L30-91 at r500 (7/8 alive).
  - Feeding is mostly corpse pearls, eaten by her: own-corpse eats / all her eats were Portals 501/501,
    Slithery 444/486, Maze 268/397, Trauma 152/165, Autarky 98/108.
  - Schooltime: her spawn box keeps both queens at L3 all game.
- **Units.** Almost all are L2-4 (r100: 2s and 3-4s only; r300: a few 5-16, about 1 at 17+), the same shape as
  ours. The unit count tops out near 62 on big maps for both teams.
- **Feeding.** About 160-200 NoValidAction deaths a game (L2s that can't pay). They peak at r300-400 on big maps
  (Slithery 1824 in r300-399 over 8 games).
- **Kills.** 52% one-step and 35% two-step, plus 35 paid lunges a game (11% of kills take 3+ steps). Ours never
  take more than 2.
- **Economy.**
  - Equal to ours at r100 on big maps (AUNSW 133 v 142, Australia 82 v 86).
  - Ahead on lane and small maps: Autarky 55 v 32, Devil 53 v 13, TD 35 v 24, weakhold 31 v 23.
  - After r300 FTM keeps its total mass while feeding: in both-queens-dead races, total at r350 is 189 for FTM
    and 121 for us.
- **Portal use** is lower than ours (91 vs 138 steps a game).

## 4. Our 74 b4-equivalent losses: decisive moments
| map | n | W | elim. | queen TB | longest race | our queen alive at end | FTM queen alive at end |
|---|---|---|---|---|---|---|---|
| Around UNSW | 7 | 1 | 0 | 0 | 6 | 0 | 0 |
| Australia | 4 | 1 | 0 | 2 | 1 | 0 | 2 |
| Autarky | 6 | 0 | 5 | 1 | 0 | 0 | 5 |
| Default | 12 | 5 | 7 | 0 | 0 | 3 | 4 |
| Devil | 4 | 1 | 3 | 0 | 0 | 0 | 0 |
| Islands | 6 | 1 | 0 | 0 | 5 | 0 | 0 |
| Maze | 3 | 0 | 0 | 2 | 1 | 1 | 3 |
| Portals | 6 | 2 | 0 | 1 | 3 | 5 | 6 |
| Prisoners Dilemma | 3 | 1 | 1 | 1 | 0 | 0 | 1 |
| Queen Of Spades | 6 | 3 | 3 | 0 | 0 | 0 | 2 |
| Schooltime | 11 | 2 | 0 | 0 | 9 | 11 | 11 |
| Slithery Fight | 8 | 0 | 0 | 7 | 1 | 0 | 7 |
| Stripes | 4 | 4 | 0 | 0 | 0 | 0 | 0 |
| Tower Defense | 4 | 2 | 1 | 1 | 0 | 1 | 2 |
| Trauma | 3 | 3 | 0 | 0 | 0 | 3 | 3 |
| Trophy | 9 | 3 | 6 | 0 | 0 | 1 | 4 |
| weakhold | 10 | 3 | 5 | 1 | 1 | 4 | 3 |

1. **Eliminations (31).**
   - By r100 FTM has twice our mass (median 48 v 23) and units (19.5 v 9.5). The leads were smaller at r50
     (26 v 19).
   - FTM heads kill our queen at a median r72 (30/31).
   - The game ends at a median r221.
   - Maps: Default 7, Trophy 6, Autarky 5, weakhold 5, Devil 3, QoS 3.
   - This is the r50-100 small-map fight and economy. It is the same family as UNDERSTANDING's lane-map early-queen
     cause.
   - Not decision-verified here. Earlier attempts in this family (l1, QEARLY_PEN) lost.
2. **Queen tiebreak (16): our queen dead, theirs alive.**
   - Slithery 7/8. FTM's queen survives 7/8 and is fed to L31-91. Ours dies at r17-484: 5 by our own hand, 3 by
     FTM.
   - Even our two survivors to r400+ were L5-8 at r450 against FTM's L31-56. So queen survival alone does not flip
     Slithery against FTM; it needs survival plus feeding her.
   - *Harness (QVAULT=3, Slithery bit, queen only, 8 games):*
     - The vault-entry move flips in 4/8: 1298471 r20, 1282773 r46, 1294561 r19/r32, 1364997 r70.
     - In 1298471 and 1282773 those entries start the box chain that kills her (SPLIT 2 at r22-24 / r48, dead at
       r28 / r51).
     - Unchanged in 4/8: 1352340, 1282386, 1278124, 1383472.
     - So the cause is confirmed. It is not a result flip against FTM, because her survivors would still lose the
       queen race.
3. **Longest-dragon race (27).**
   - **Schooltime (9).** Both queens are L3 in their boxes, so the longest dragon decides. In 6 of the 9 (layout B)
     the decisive gap is the chamber economy (section 5).
   - **Around UNSW, Islands and Australia (12).** Both queens die before r300.
     - FTM's longest leads from r250 (median 9 v 6; r300 14 v 8.5; r400 34.5 v 26; r450 51 v 32.5).
     - FTM keeps its total during feeding (r300 185 → r400 204); ours falls (162 → 126).
     - Over these 18 both-dead games FTM wins 13.
   - **Portals (3).** Both queens alive and crowned. FTM's queen is L8-24 at r300; ours is L3 because our crown
     starts at r300. FTM wins 54 v 38, 38 v 21. This is FTM_OCT5's Portals cause, unchanged.
   - **weakhold 1282387.** Both queens alive: theirs L11, ours L4, while our non-queen king is L41. This is the
     WH_QCROWN case from UNDERSTANDING.
4. **Our queen's self-deaths: 19/106 games (FTM 1/106).**
   - 12 of the 16 checked follow her own SPLIT within 6 rounds (box, reverse split, dead).
   - Traced with the harness (exact kf1 zip, every shown turn MATCHes the server):
     - **1373837 AUNSW r82.** Two candidates: S (score 2.11, area 3448) and E (-1.26, area 3447). She takes S onto
       (47,12), whose only other exit is (48,12). Ally 186 (L3) at (48,13) had exactly one legal move, N onto
       (48,12) (its trace: `top 1/1 cand N score -505`). It sees her new head and still has to take it. At r83 she
       has 0 moves and dies HitSelf.
       - Cause: she ignores an adjacent ally's forced move.
       - One case only. Not prototyped.
     - **1278124 Slithery r17.** A newborn L2 child (id 87, born the same round) steps E through the portal at
       (57,13) onto her new head tile (5,14) and kills her head-on.
       - QALLY_KEEP (main.cpp ~6289) gates on `wrapDist(myHead, qakHead) <= QAK_DIST+3`, which doesn't see
         through portals.
       - One case only.
     - **1298471 / 1282773 Slithery.** Vault entry, then K2 shed (QVAULT above).
     - **1261405 Islands r45.** The free path WS ends in a cell whose area falls from 1484 to 0 one turn later.
       Allies were stationary; it is a self-made pocket.

## 5. Verified known-map fix: Schooltime layout B chambers (SCH_DOORS=1 + SCH_CHAMBER=1)
- **Cause, from the replays.** On layout B, FTM's units enter the side-room chambers (x5-15 / x44-54, y28-33) from
  r59-162. They keep 20-77 heads in there per 100 rounds (10-round samples) and eat 119-147 chamber pearls a game.
  - Ours enter 0-11 times and eat 0-13.
  - Our total at r300 collapses (3-61 against FTM's 131-218), and our longest ends at 3-10.
  - In the one layout-B win (1265612) we farmed the chambers (101 eats, from r259) and FTM didn't (2).
  - Layout A (yard pool, about 2,000 eats) is a separate close king race: 2 losses, 1 win here.
- **Harness.** `verify --sub 18798 -D SCH_DOORS=1 -D SCH_CHAMBER=1`, every one of our dragons:
  | game | layout | result | turns changed | first change | moves toward / away from the chambers |
  |---|---|---|---|---|---|
  | 1269891 | B | L | 837/6966 | r34 | 381 / 132 |
  | 1274174 | B | L | 359/3099 | r42 | 173 / 74 |
  | 1307866 | B | L | 935/7990 | r30 | 477 / 168 |
  | 1373840 | B | L | 1002/9495 | r29 | 519 / 201 |
  | 1374274 | B | L | 721/6003 | r31 | 360 / 107 |
  | 1383112 | B | L | 955/7810 | r37 | 416 / 184 |
  | 1265612 | B | W | 2551/16393 | r19 | 990 / 494 |
  | 1265975 | A | L | **0**/22311 | - | - |
  | 1383473 | A | L | **0**/24015 | - | - |
  | 1265615 | Trauma | W | **0**/15563 | - | - |
- Every layout-B loss changes 6/6, starting 20-130 rounds before FTM's first chamber eat, mostly toward the
  chambers. Layout A and other maps are identical, as the code gates require.
- The harness can't score the result. The changed decisions are the ones the replays say decide B.
- **Why this isn't a re-run of a loser.**
  - v1 shipped SCH_DOORS alone, and Schooltime fell from 36% to 25%.
  - UNDERSTANDING found doors alone flip 1/8 B decision points, and doors plus the pull flip 4/8.
  - SCH_CHAMBER (the pull) has never been on the server.
  - The new evidence is that FTM, the #2 team, wins B through exactly this economy, 6/6 against us.
- **Stage:** `scratchpad/top4/ftm/bot/` = variants/b4 plus `#define SCH_DOORS 1`, `#define SCH_CHAMBER 1` at the
  top of params.hpp.
  - verify `--src` gives 6129/6966 on 1269891, identical to the -D run, and 24015/24015 on layout-A 1383473.
  - Earlier sandbox smoke of the same code (dgu stage SCH_CHAMBER) showed no errors and normal CPU.
- **Scope and risk.** Schooltime only, 1/17 of seeding games. The earlier risk note still applies: B wins change
  14-16% of their turns.
- **Server metric:** chamber eats per B game (target > 30) and the B-layout result vs FTM, DEV and SSS.
- **Freeze-time call: a coin flip.** It only touches seeding, and the freeze is about 20 h away. Ship it only as a
  Schooltime-only unranked test with time to judge about 20 B games.

## 6. Generalises to unseen maps
1. **Queen self-preservation is the biggest gap.**
   - FTM's queen dies by her own hand in 1/106 games; ours in 19/106. Before r100: theirs 30/106, ours 47/106.
   - Of the 74 b4 losses, 16 are decided by the queen tiebreak with their queen alive.
   - Their recipe needs no map knowledge:
     - L2-4 near spawn, about 9.5 tiles away;
     - no vault or pocket entries;
     - big sheds only at r0-3 (Slithery);
     - 5 splits a game after r5, mostly late feeding.
   - Our self-deaths are box-then-split chains (12/16) plus ally seals (1373837, forced ally move; 1278124, a
     newborn through a portal).
   - The ally-seal sub-causes are new, decision-level angles:
     - the queen ignores forced ally moves next to her;
     - QALLY_KEEP's gate is portal-blind.
   - Both are single traced cases so far. Count them over a larger corpus before building anything.
2. **Crown a living queen at about r220.**
   - FTM's living queen reaches L10 at r215-260 on 10 map types, mostly from own-corpse pearls dropped next to her.
     On unknown maps we seed the king at 250 and feed at 300, and the king is a non-queen.
   - When both queens live (Portals, Maze, weakhold), FTM wins by queen length.
   - **Caution:** QK_BIG (queen as king on big maps), q1 (queen park) and QPARK_UNK all lost or were rejected. The
     FTM data says crowning works when the queen is already safe. It doesn't say crowning a roaming queen works.
     Treat it as a decision to gate on her safety, not a copy.
3. **Feeding keeps mass in FTM's both-queens-dead races.** Their total holds (185 → 204 over r300-400) while ours
   drops (162 → 126). Their longest leads from r250. This is generic king feeding, and it decides the open-map
   longest races (AUNSW and Islands 2/13).
4. **Kill shape.** 35 paid lunges a game (11% of kills take 3+ steps) against our 16 and 0%. LUNGE34 lost on the
   server, so this is information, not a lever.
5. **Small maps.** FTM's r50-100 economy doubles ours (48 v 23 at r100) and eliminates us 31 times. Against the
   top 9 the same FTM is eliminated by aAah, DEV, SSS, chad and Cutlery on Devil, Default, Trophy, Autarky, QoS and
   Stripes (11/14 of its losses in the sample).
   - So small-map aggression beats FTM. aAah beats them 86-100% on Default, Islands, QoS and Australia.

## 7. Ranked findings
1. Schooltime B chamber pull (SCH_DOORS+SCH_CHAMBER): verified, staged, Schooltime-only (section 5).
2. Our queen self-deaths (19/106 vs 1/106) are the most general difference. Two new single-case decision causes
   (forced ally move, portal-blind QALLY_KEEP gate) are worth counting on the full b4 corpus. Not prototyped.
3. Slithery 0/8 needs queen survival plus feeding. QVAULT=3 flips the vault entries (4/8) but would not flip the
   results against FTM's L30-90 queen.
4. Attribution: 18 "kf1" games were v61. Re-check the kf1 verdict and any A/B that used upload windows on 7 Oct.
