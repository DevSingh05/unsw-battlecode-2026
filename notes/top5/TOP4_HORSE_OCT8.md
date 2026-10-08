# horse (#3, id 842): current build, how it beats b4, and one verified fix (8 Oct, ~05:00 UTC)

Read-only study. Nothing in bot/ or variants/ was changed, and nothing was submitted or challenged.
- **Data:** horse's listing crawled back to 6 Oct 14:00 UTC (2,444 games): `replays/top4_horse/games_842.json`.
- **Replays:** 98 replays in `replays/top4_horse/` (`sample.json`; 10 are symlinks to existing caches):
  - 30 vs b4 (re-uploaded 7 Oct 19:26)
  - 29 vs kf1 (= b4 + king queen-kill; the queen code is the same as b4)
  - 5 vs kf1/b4 just before horse's build change
  - 34 vs FTM and larp from the last 24 h
- **Scripts:** `notes/top5/new_rules_tools/*_horse8.py`. Scratch prototype: `scratchpad/top4/horse/bot/` (b4 plus the `QE_KR` flag, default 0). Diff: `new_rules_tools/QE_KR_horse8.diff`.

## 1. Who they are and what changed
- **Team:** Chalmers (Sweden), C++, about 64 games/h (60% are challenges they send).
- **Rating history:** 2211 (6 Oct 20:38) -> 2320 (7 Oct 01:54) -> 2385 (17:42) -> 2419 (22:58) -> **2462 now** (#3, behind aAah 2555 and FTM 2487).
- **New build between 6 Oct 17:50 and 18:53 UTC:**
  - The Elo field our cache stores for horse jumped from 2214 to 2407 in that hour.
  - horse's win rate went from 61% (6 Oct 14:00-18:00) to 66% (to 7 Oct 12:00) to 74% since then.
  - vs "we love gru": 56% -> 77% -> 86%. vs Sponge: 7-8 -> 37-17.
  - A second, smaller upload around 6 Oct 23:45 is possible: their listing Elo field changes 2462 -> 2458 there. This is weak evidence.
- **Our record vs horse:**
  - Before the change: 279-301 (48%).
  - Since: kf1 26-59, b4 11-19.
  - Since the change, per map (b4+kf1): AUNSW 0-8, Maze 0-7, weakhold 0-4, Portals 1-9, Autarky 1-7, Australia 1-4, TD 3-9, Stripes 3-6, Islands 1-2, QoS 2-3, Devil 2-3, Default 4-5, Schooltime 3-3, Slithery 2-2, Trophy 2-2, PD 6-3, Trauma 6-1.
- **What changed in their play** (10 pre-change vs 64 post-change games vs us):
  - Queen alive at r100: 50% -> 83%.
  - Kills per game: 17 -> 23.
  - Their Portals queen is now parked and fed: first split r88-205, L49-81 at r500. Before: first split r31, died r449 (only n=1 pre-change Portals game).

## 2. Current play (64 games vs b4/kf1, 24 vs FTM/larp)
- **Queen: small early, grown late.**
  - Their queen splits at L4-5 (often at r0) and keeps L2-3 to r100. Ours splits at L7 and keeps L5-7.
  - She roams (about 10 tiles from spawn, like ours) and is alive at r100 in 83% of games (ours 53%) and at the end in 33/64 (ours 11/64).
  - On Portals and Maze she is fed from about r100-200 and reaches L50-88 at r500.
  - Feeding is horse's own units dissolving next to her (HitSelf). Their Portals queen makes 72-102 corpse eats; ours makes 17.
  - Schooltime: both queens sit at L3 all game, so the longest dragon decides.
- **Kills are kamikaze lunges.**
  - All head-on kills are trades. 61% of horse's kills use paid steps (a paid step costs a dying head nothing).
  - Kills by steps: 1 step 558, 2 steps 685, 3 steps 198, 4+ steps 49. So 17% take 3+ steps; ours 0.9% (14 of 1612).
  - 18% of their killers are L4-7 (ours 2.5%).
  - **13% of their kills reach beyond plain K(L) = ceil(L/4) + (L-2) by eating pearls on the way.** A pearl on any step adds a segment, so it buys one more paid step. Ours: 6 of 1612.
  - Hunters close in on our queen over 4-6 rounds, about 2 tiles per round (approach 13 -> 9 -> 7 -> 5 -> 3), then strike from distance 2-4.
  - Only 9-15% of kills start from outside our 7x7 vision.
- **Economy:**
  - Before r100 they split less than we do (58 vs 87) and have fewer stillborn children (3.7 vs 17).
  - On r500 maps we eat more by r100 (200 vs 142) but have less total length (72 vs 94).
  - The gap opens at r50-100. Self-inflicted deaths (HitSelf, own body, wall) cost us about 80 length per game and we re-eat 46; for horse it is 25 and 20. Most of ours are our designed pocket/vault pumps (e.g. the Australia vault tiles (53,37), (56,38-40), (10,26)), so this is the known economy waste, not a new lever. s1 and c1 already showed that blocking splits loses.
- **Other numbers:** portal crossings 204 per game (ours 161). Kills per game are equal (23 vs 25). horse lets L10+ dragons die head-on 2.5 times per game (we kill more of their big dragons than they kill of ours: 112 vs 46).

## 3. Why b4 loses to them
In 64 games vs b4/kf1 we won 20 and lost 44:
- 21 losses were eliminations, 23 were r500 losses.
- We won 9 by elimination and 11 at r500.

1. **Lane and small maps: early queen killed, then eliminated** (TD, Default, Devil, Trophy, QoS, weakhold, Autarky, Stripes, PD).
   - Eliminations are a symmetric snowball. Whoever leads at r50 (22 vs 16 in their wins, 13 vs 23 in ours) is 3x ahead at r100.
   - **horse killed our queen before r100 in 19 games (13 of them our losses).**
     - The pattern: an L2-4 hunter approaches, and our queen's own move ends inside its kamikaze reach (often its pearl-extended reach).
     - Before r100 our queen counts every enemy head as reach 1 (MAX_THREAT_REACH=1, QS_FROM=100) and an L<6 queen pays only SMALL_THREAT_PEN=12, so every candidate shows threat=0.
   - Example, 1383488 Devil r51: queen L6 at (14,11) picks E (15,11) at 14.98, all candidates threat=0. The killer B15 is an L3 at (16,8), visible, with tail seen (so plain K=2). It goes W,S,S,S over 2 pearls and lands on (15,11).
   - On PD, horse's opening kills our queen at r7-9 in 4/4 games (L3, 3 steps, one pearl eaten on the free step).
2. **Portals (1-9) and Maze (0-7): their fed queen is bigger, or ours collapses.**
   - Portals in b4 games:
     - 2/4: our crowned queen coils and dies in a 2-per-turn split chain (1378744 r347-356 from L20; 1383130 r374-383). The area collapses at r340-344 after a 3-step free path. This is the known "self-made seal" (UNDERSTANDING §2), with no cheap fix.
     - 2/4: our queen is alive but shorter (32 v 77, 48 v 81). Ours is L3 at r300 (crown from r300); theirs is L20 at r300.
   - Maze: our crowned queen (L28, L52) is rammed by L3-L7 lunges of 4 steps (known; k2/QG_RAM territory).
3. **Big open (Australia, AUNSW, Islands): longest dragon.**
   - Both queens die, and horse's mass at r300-500 is 1.5-20x ours.
   - Example, Australia 1378748: our total is 159 at r300 and 46 at r400. Our kings die head-on: L33 at r380 to an L8 that waited 4 rounds just outside our vision (Chebyshev 4, then a 6-step lunge); L25 at r398 to an L5 4-step lunge; L10 at r411.

## 4. Verified fix: QE_KR=2, pearl-aware kamikaze reach for the early queen
- **What it does:** before QS_FROM, for each visible enemy head, the queen floods K-reach with pearl refunds:
  - steps up to QE_KR_CAP=4;
  - the paid budget is Lv-2 (an unseen tail counts as Lv>=3);
  - every visible pearl on the path refunds one step;
  - bodies block the flood.
  - Tiles it reaches get `threatAt`, plus a QE_KR_PEN=60 penalty on top of the small-unit threat penalty.
  - Queen only, before r100. With the flag at 0 the code is unchanged: the flags-off scratch copy verifies 16414/16414 actions on 1383129.
- **Loss points** (all 19 early queen kills by horse vs b4/kf1, rounds r-3..r of the queen):
  - **8/19 fatal final moves flip:** 1298850 Trophy r37, 1354488 Autarky r39, 1378302 TD r58, 1378748 Australia r80, 1383484 Trophy r43, 1383488 Devil r51 (E -> WN), 1383799 Trophy r18, plus 1365009 Devil (r16 W -> S, earlier in the approach).
  - In 1383483 QoS the move 1-2 rounds before the kill also flips.
  - **Not flipped:**
    - PD r9 ×3: by r9 two L3 heads threaten all three candidates; the fatal move is r8.
    - Australia r38/r46 and TD r67/r76: every candidate is already threatened, i.e. she was squeezed earlier.
  - Plain QE_KR=1 (K reach without pearls) flips only 4/19, so the pearl refund matters.
- **Wins** (51 win runs, ~45 distinct games, our queen only, compared with a flags-off run):
  - 34 are unchanged, including every Portals, Maze, Schooltime, Trauma, weakhold, AUNSW and Slithery win.
  - 9 change 1-2 queen turns. Mostly lane maps where the queen died by r19-81 anyway.
  - PD 1379200 changes 7 turns; Islands 1257441 changes 10 (6 of them before r100).
- **Server metric:**
  - Our queen alive at r100 on Devil, Trophy, TD, Autarky, QoS and Australia (vs horse, DEV and FTM).
  - Queen deaths before r100 by HitHeadToHead per game.
  - Win rate on those maps.
- **Risk / precedent:**
  - v69 (portal/blind penalties) and l1 (home queen) lost.
  - KREACH, the queen's plain kamikaze reach, was rejected locally and never server-tested.
  - The new angle: exact pearl-aware reach, queen-only and pre-r100, which leaves parked or crowned queens alone.
  - It changes known-map play on lane maps, so it is not byte-identical on the 17. Test it only as a full server A/B. The default for the freeze is to leave it out unless it can be tested by about Thu 8 Oct 22:00 EDT (9 Oct 02:00 UTC).
- **Smoke:**
  - Not run locally (CPU budget). The added cost is one BFS of at most 4 steps per visible enemy head, queen only, before r100.
  - Before staging: one `unswbc run --sandbox` game on Devil and one on PD to check CPU.

## 5. What carries to unseen maps
1. **The threat model is the general lesson.** For a head-on, cost = steps - ceil(L/4), and every pearl on the path adds a segment. So a small hunter's reach is F + (L-2) + pearls, which is 3-5 tiles for an L3 in a pearl field. Every top team now kills with 3-5-step paid lunges (horse 17%, FTM 9%), and they hunt queens by id (0/1). On unseen maps (Qualifier) our early queen meets this in every game, so QE_KR=2 is a Qualifier-relevant change, not a map patch. If it can't be server-tested, `INFER_SYM`-style gating ("unknown maps only") keeps the 17 identical: `QE_KR=2` only under the same unknown-map gate INFER_SYM uses. That is a weaker claim, since the unseen-eval sets were not run.
2. **A small early queen (L2-3, split at L4) plus late feeding by dissolving units next to her.** This generalises, but our versions (l1 lane small-queen, QK_BIG) lost. Do not copy it.
3. **horse's open-map strength is length retention.** They have fewer, safer splits and fewer stillborn children. We out-eat them and still trail by r100. This is not a freeze-week change.
4. **Kings get stalked from just outside 7x7 vision** (Chebyshev 4) by L5-8 heads that then lunge 4-6 steps. On unseen maps a king could treat "an enemy head seen within 4 in the last 2 rounds and now gone" as threat. Not verified; low priority.

## 6. Bottom line
horse's new build (live since 6 Oct ~18:00 UTC) beats b4 30-70.
- **Lane maps:** their L2-4 hunters kill our early queen with paid, pearl-extended lunges that our reach-1 early threat model can't see.
- **Portals/Maze:** their queen is fed from r100 instead of r300.
- **Open maps:** they keep more length.

The one cheap, decision-verified lever is **QE_KR=2**: 8/19 fatal moves flip, and 34/45 wins are unchanged, with no change on any park or crown map.
