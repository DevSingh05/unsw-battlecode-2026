# horse (id 842) deep study: what changed, how they hunt, does QE_KR=2 answer it (8 Oct, PAUSED 16:21 UTC)

Status: **paused on the user's request, partial.** Sections 1-4 are done. Section 5 (escape check on every flip) is
started, and the prototype plus unseen_eval are not done. Nothing in bot/ or variants/ was edited. Nothing was
submitted or challenged. Scratch, data and scripts are in `work/top4b/horse/` (see `PROGRESS.md` there).

Data:
- 392 cached horse replays (our caches since 2 Oct, plus `replays/top4_horse/`).
- 71 horse games vs four control teams, downloaded from the public endpoint at 1.6 s pacing: WeHaveQuizzes, we love gru,
  Preyas and Kaizen. They come from 6 Oct 14:00-17:50 and 6 Oct 19:00 to 7 Oct 12:00.
- Per-turn traces: `work/top4b/horse/data/tr/<gid>.pkl`. For every horse turn the trace records:
  - Chebyshev (vision) and BFS distance to our queen;
  - whether her head is inside that unit's exact kamikaze reach this turn: free steps ceil(L/4), paid steps need L>=3,
    each pearl adds a segment, bodies block.

Eras:
- E0: before 6 Oct 17:50.
- E1: 6 Oct 18:00 to 7 Oct 11:00.
- E2: from 7 Oct 11:00 (see section 1).

## 1. When horse changed, and the 6 Oct 18:00 claim
- **The listing "elo" field is not per submission.** It is the team's rating when the page was fetched. Our own value is
  2253 on every game in the crawl, including b3, b4 and kf1. So the "2214 -> 2407 jump at 18:00" in TOP4_HORSE is not
  evidence of an upload.
- **Fingerprint 1, sonar.** Each starting dragon's first-turn sonar uses 4 fixed constants (top 32 bits 0xde71d8f5,
  0xaed5686e, 0x490895bd, 0x50976d94).
  - They appear in every horse game up to **7 Oct 10:51 UTC** and in none from **7 Oct 13:41**: 0 in 75 games, all maps.
  - The new first turn sends one value on its first three rays.
  - So a new build (new message protocol) went live between 7 Oct 10:51 and 13:41 UTC. This is E2.
- **Fingerprint 2, openings** (deterministic per map and side):
  - PD: unit 3 changes from `SS,P11` to a split chain `P2,P2,P2,P3`, first seen 7 Oct 06:40. That game still has the
    old sonar, so there is another change between 6 Oct 21:51 and 7 Oct 06:40.
  - Autarky: `SS,P14` changes to `P2,P2,P2,P2,P2,P2`.
  - TD and Default openings: new by 7 Oct 17:24.
  - Devil and Trophy: unchanged.
- **horse's overall win rate** (listing, all opponents):
  - 61% on 6 Oct 14:00-18:00 and 62% on 18:55-23:30;
  - 68% on 7 Oct 00:00-12:00;
  - 74% after 7 Oct 12:00.
  - Against gru: 56%, 76%, 79%, 86%.
  - So their gain came in two steps, about 7 Oct 00:00-06:00 and 11:00-13:00. Nothing changes at 18:00.
- **Our record vs horse** (ab_server, since 5 Oct):
  - E0: 134-138 (49%). That splits into b3 42-58 (**42%**) and h1 57-48. **The "48% before" baseline is inflated by h1.**
  - E1: 19-38 (33%, all kf1).
  - E2: 18-42 (30%): b4 11-20, kf1 7-22.
- **Attribution.** I checked 86 horse-vs-us games since 6 Oct 15:38 by replaying our queen r1-40 with each cached zip.
  - 78 match b4's queen exactly.
  - 5 were played by our old zips: 1303423 Trophy (v35), and 1352310 Maze, 1352308 Australia, 1354489 Portals,
    1365013 Portals (v61).
  - 3 QoS games are ambiguous: every zip mismatches 3-18 turns.
  - Old-zip pinning does not explain the drop.

## 2. Hunting policy (explicit rules; counts are vs us, r<100 unless noted)
1. **Strike as soon as our queen is inside kamikaze reach. They never wait.**
   - Conversion: E0 35/45 (78%), E1 5/7, E2 17/22 (77%).
   - By hunter: L3 20/24 (E0), 13/14 (E2); L2 11/14, 4/7.
   - Paid lunges: 27/32 (E0), 15/16 (E2). Free 1-step chances are taken less often: 8/13, 2/6.
   - In 0 of 51 kills did the killer already have her in reach 1-3 rounds earlier. Every strike is the first chance.
2. **The queen is chosen by id.**
   - The same units, with one of our non-queen heads in reach, strike only 18% of the time (E0 293/1671), 16% (E1) and
     15% (E2 88/583).
   - L3 vs our L3 non-queens: 17-23%. L3 vs our queen: 83-93%. That is 4-5x the rate.
   - Units of L5+ almost never lunge at her (whole game: L5-7 3/18, L8+ 7/34 in E0).
3. **No remote detection or homing.**
   - Units at Chebyshev 4-12 (outside their own view) move closer to her on 24-25% of moves and away on 26%. Toward a
     null point (her position mirrored through the centre) the split is the same: 24-25% closer.
   - This holds whether or not a teammate saw her this round or last. Sample: E0 16,463 moves, E2 7,207.
   - The same holds vs control teams. There is no sign of sonar-relayed tracking or of a march on her spawn.
4. **No stalking inside view either.** Units at Chebyshev 1-3 move closer 18% and away 30%, vs a null of 29/27.
   - Escort density: 0.18-0.21 horse non-queen heads within Chebyshev 3 per queen turn before r100, in every era.
   - Exposure (her move ends inside at least one horse reach): 0.4% of queen turns in E0, 0.5% after.
5. **Every kill starts inside the killer's 7x7 view.** That is 0 of 57 out of view (E0-E2 vs us); vs control teams, 1.
6. **The geometry of a kill is that our queen walks in.**
   - On the fatal move she can see the killer (Chebyshev <= 3 from her head before her move): E0 28/35, E2 15/16.
   - She moved toward it on the fatal move in E0 21/35, E2 6/16. One round earlier: 20/35, 11/16. Two rounds
     earlier: 17/35, 11/16.
   - The gap closes about 2 tiles a round because both move. The "approach 13 -> 9 -> 7 -> 5 -> 3" in TOP4_HORSE is
     this, plus selection of the eventual killer.
7. **E2 killers come from further out.**
   - Two rounds before the strike, the killer is in her view in 5/16 (E2) vs 17/35 (E0), but at Chebyshev <= 4 in 12/16.
   - One round before, it is within 3 in 14/16.
   - She usually first sees the killer one round before the strike, or on the fatal move itself.
8. **The strike itself:**
   - E2 killers are L3 13/17 and L2 4/17.
   - Steps: 2 steps 9, 3 steps 5, 4 steps 1.
   - Paid 15/17. A pearl is eaten during the lunge in 7/17.
   - E0: L2 11, L3 20, L4 4; up to 5 steps; pearl eaten 17/35.
9. **The rest of the army is not escorting.** Non-killers near her behave like any other unit (rules 3-4). Their army
   farms and lunges at our non-queens only 15-18% of the time when it can.

## 3. What actually changed (E0 -> E2, vs us; the map mix differs, so per group)
The hunting rules above are unchanged. Head-on kills of our queen before r100 rose only from 26% to 30% of games. The
gains are elsewhere:
- **Lane maps** (Devil, Trophy, TD, Default, Autarky, QoS, PD, Stripes, weakhold; E0 n=65, E2 n=31):
  - horse's queen alive at r100: 49% -> 68%.
  - Our queen alive at r100: 35% -> 26%; at r500: 14% -> **0%**.
  - Our total at r300: 47 -> 31. horse's total at r300: 52 -> 62.
  - horse win 58% -> 71%; 27 of 31 games end in elimination.
  - horse's split chain opening (PD/Autarky) is part of this.
- **Park maps** (Portals, Maze, Schooltime, Trauma, Slithery; E0 n=51, E2 n=18):
  - horse's queen length: r200 4.4 -> 6.5, r300 6.0 -> 8.4, **r500 15 -> 32**. Alive at r500: 61% -> 78%.
  - Ours alive at r500: 69% -> 50%. Our queen length at r500: 23 -> 14.5.
  - Games where their queen died and ours lived (always our wins): 11/51 -> **0/18**.
- **Open maps** (n 25 vs 8): no clear change.
- **Economy:** splits before r100 per game 56 -> 41 (stillborn 7 -> 4.3). On lane maps the split count is about the same
  (30 -> 27).
- **Control teams** (36 E0 vs 36 E1 games; no E2 control yet): no change in hunting (r<100 strike 8/16 vs 8/14) or
  win rate (58% vs 53%).

**Conclusion so far:** horse did not change *how* it kills our queen. It strikes the first time she is in reach, as
before. What changed is that **their queen survives and is fed larger** (park maps), and **their lane-map opening and
economy snowball harder**. As a result, our early queen death (same mechanism, slightly more often) now ends in
elimination, and on park maps their queen out-races ours. The pre-r100 queen-death fix is still the right defensive
lever, but it addresses only part of the gap.

## 4. QE_KR flips on our queen deaths to horse (decision-replay harness)
- **Setup:** 25 r<100 head-on queen deaths in b4-era games. 24 have a verified base (every server move MATCH); 1383483
  QoS mismatches; 1303423 (v35 zip) was dropped. Harness runs our queen r-4..r with `work/top4b/horse/bot` (= bot/, QF1
  flags) and `-D QE_KR=2 -D QE_KR_ANYMAP=1` (ungated).
- **QE_KR=2:** the fatal move changes in **12/24**; any change in r-4..r in 13/24.
  - The 12 are 1261516 PD r12 E->N, 1261517 Autarky r30 N->E, 1270304 Default r64 E->NE, 1298850 Trophy r37 (r35-36
    change too), 1354488 Autarky r39 E->S, 1365009 Devil r19 SW->WN (r16 too), 1369505 Default r23 N->W, 1378302 TD
    r58 S->N, 1378748 Australia r80 S->SS, 1383484 Trophy r43 WS->WW, 1383488 Devil r51 E->WN, 1383799 Trophy r18 W->S.
  - 1378746 TD changes only at r72.
- **QE_KR=1** (no pearls): 8/24 fatal, 10/24 any.
- **Not flipped:** the 3 PD r9 kills (deterministic opening, 3-step NEE lunge), Australia r38/r44/r46, Autarky r46,
  Default r86, Devil r23, TD r67, Trophy r48.
- **Escape check** (`scripts/safety.py`: applies the move to her body and floods every horse head's exact reach on that
  board). Only one is done so far: 1383488 r51, where server E is reached by id15 L3 in 4 steps, while QE_KR=2's WN is
  **safe** (S, W, WW and SS are safe too). The other 11 flips are not checked yet.

## 5. Not done (resume from work/top4b/horse/PROGRESS.md)
- Safety check on the other 11 flips, plus "was any 1-3 step move safe?" on the 12 unflipped deaths. This separates
  "threat model blind" from "already squeezed".
- Prototype (unknown-map only, in `work/top4b/horse/bot/`). Rule 7 suggests the 2-turn reaction should target
  heads at Chebyshev 4 that she cannot see, e.g. via ally sightings. Rule 6 suggests the cheaper lever is not walking
  toward a visible L2-3 head when her move would leave Chebyshev <= 3 of it. Then run
  `python3 tools/unseen_eval.py work/top4b/horse/bot --base variants/b4 --seeds 1 --jobs 2 --seed-base 973000 --sets real,realhold,blind17`.
- E2 control games (horse vs gru/WHQ after 7 Oct 13:40) to confirm section 3 independently of us.
