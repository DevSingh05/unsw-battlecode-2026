# aAah (id 454, #1 at 2555): who they are, how they play, why b4 loses to them (8 Oct)

Written 2026-10-08 ~05:30 UTC (01:30 EDT). Read-only study: nothing in bot/ or variants/ changed, nothing submitted,
no challenges. Data: 88 replays in `replays/top4_aaah/` (68 vs us from 6 Oct 16:49 to 7 Oct 19:31 UTC, 20 ranked vs
FTM/horse/Cutlery/larp/SSS from 7 Oct 20:26 to 8 Oct 03:11), game list for 30 h (`games_454.json`, 6315 games),
`which_submission.json` (which of OUR zips actually played each game). Scripts are in the scratchpad
`top4/aaah/` (prof_aaah.py and agg_aaah.py are copies of the dev5 profilers; whichsub.py, fatal.py, hob.py, qtrack.py).

## 0. The short version
- **aAah beats b4 17-40 (30%) in b4-code games.** They win by mass on open maps: in our losses the r100 totals are
  36 (us) vs 82 (them), and r200 is 32 vs 173. 23 of the 40 losses are eliminations. In our wins it is the other
  way round (r100 55 vs 22). The game is decided by r50-100, before any queen or king logic matters.
- **The engine of that mass is mid-size units plus the 64-unit cap.** Their units live at L4-12 and move 2-3 tiles a
  turn for free (ceil(L/4)). Ours split at L4 into 2+2 and move 1 tile a turn. Moves made by an L4+ unit: aAah
  4638 per game, us 472. Fresh pearls eaten by L4-7 units: aAah 273 per game, us 23. They reach 60-64 units by
  r300 on every open map.
- **Their queen is an L2 that stays away from enemy heads.** She splits at r0, is L2-3 all game, and keeps 8-9 tiles
  from enemy heads. She is alive at the end in 25/39 games vs us and 10/20 vs top teams. Ours dies before r150
  in 26/40 b4 losses.
- **New data-integrity finding (harness-verified): 11 of the 68 "kf1/b4" games vs aAah were played by OUR OLD
  ZIPS, v35 (14238) and v61 (16388).** Different games in the same 5-game series used different zips. None of the 12
  same-window games vs other teams did. So every upload-window A/B number that includes aAah games is polluted
  (section 4).
- **No cheap known-map fix survived.** The cause is a whole-economy design, not one decision. The single
  decision-level candidate tested (queen kamikaze reach, KREACH queen-only) changes 5/24 fatal-move windows in
  losses but also 4/8 in wins, so it is not selective. For the Qualifier, the transferable lessons are in section 5;
  none of them is a 24-hour change.

## 1. Who they are
- University of Melbourne, 4 members (honey, aleks, andrewwang, Ray9232), C++. Description: "Working on.... The
  element of surprise".
- **Sprint (old rules):** seed 77 (1659). They won R1 7-0 and R2 4-3, then lost 3-4 in R3 to Quant Merch Trader. So
  they did not win or place in the Sprint (Cutlery won it). Their whole climb came under the new rules.
- **Rating history** (leaderboard history, about 5 h steps): 1500 on 1 Oct, 1700 on 2 Oct, a +209 step to 1928 at
  08:20 UTC on 3 Oct, a steady climb on 4 Oct (1951 → 2240), 2400 at 04:43 on 6 Oct, a **+126 step to 2518 at 15:14
  on 6 Oct**, a dip to 2425 at 12:16 on 7 Oct, then 2496 → 2518 → **2555 at 04:03 on 8 Oct**. Steps like +126 and
  +209 are typical of a fresh upload (extra sigma). A new build around 6 Oct 10:00-15:00 UTC is likely, and maybe
  another around 7 Oct 12:00. The rating alone can't prove it.
- **Behaviour change in the last 36 h: not detectable from this sample.** Every metric moves with the map mix (for
  example, the mid-size share is 0.20 in the 6 Oct block of Islands/Australia/Maze and 0.04-0.08 later). One hint:
  the Islands r20 queen kill on us is identical move for move in three 6 Oct games and different on 7 Oct
  (1369517, r22). That could also be the pearl seed.
- **Volume:** about 200 games per hour involve them. aAah is the listed "a" side (the challenger) in 17% of them,
  about 28 challenges per hour. The rest are other teams challenging #1. Over the last 16 h they went 129/184 vs
  SSS, 126/219 vs FTM, 92/158 vs Cutlery, 84/134 vs Sponge, 56/120 vs chad gdp, 25/50 vs horse, 35/67 vs DEV.
  They have played no game vs us since 7 Oct 19:31.

## 2. Current play (profile; 57 b4-code games vs us plus 20 ranked vs top teams; numbers are per game, us | them)
| | aAah vs us | aAah vs top-5 |
|---|---|---|
| total length r50 / r100 / r200 / r300 | 44 / 90 / 142 / 171 vs our 41 / 53 / 60 / 80 | 32 / 81 / 142 / 245 vs 29 / 69 / 78 / 98 |
| units r100 / r300 | 35 / 52 vs our 22 / 30 | 33 / 58 vs 23 / 32 |
| unit-rounds at L4-7 / L8+ (r100-199) | 27% / 8% (ours 6% / 0%) | 21% / 7% (theirs 9% / 1%) |
| moves by L4-7 / L8+ units | 2798 / 1840 (ours 344 / 128) | |
| fresh eats by L4-7 / L8+ units | 273 / 136 (ours 23 / 11) | 313 / 176 (theirs 72 / 22) |
| paid (beyond free) moves that ate, no kill | 56 (ours 0) | 58 (theirs 3) |
| splits: (L,k) top | (4,2) 156, (5,3) 65, (12,10) 32, (6,4) 28 | (4,2) 172, (5,3) 68, (12,10) 48 |
| head-on kills by 3+ steps | 9.9 (ours 0) | 13.8 (theirs 3.4) |
| kills of L10+ units | 0.9, mostly by 3-6 steps from distance 4 | 2.5, steps 3-5 |
| portal crossings (portal maps) | 113 (ours 61) | 218 (theirs 70) |

- **Opening:** they are equal with us to r45 (16 units, total 39 for both sides). On open maps they lead already at
  r50 (Around UNSW 109 vs 76, Slithery 158 vs 117, Islands 78 vs 59, Australia 65 vs 42), and the gap explodes
  r50-150 (Australia r100 168 vs 36).
- **Unit sizes and splitting:** children are mostly L-2 with the parent keeping 2: (5,3), (6,4), (7,5), (8,6),
  (12,10). The L2 head keeps going and the big body walks off backwards. Units cycle L2 → L5-12 → split. With the
  64-unit cap reached by r200-300, the extra growth goes into length (longest 20-50 at the end).
- **Feeding:** distributed, with no single king. Own corpses eaten: by L8+ units 100 per game, by the king 28, by
  the queen 4. HitSelf deaths (mostly L2 suicides) number about 280 per game after r100. Total mass falls from r300 to r400
  (171 → 130) as they consolidate. No crowned queen in 59 games.
- **Kings and kills:** every head-on kill is mutual (a kamikaze). They spend paid steps to reach queens and kings:
  L4 units hit 3 steps away, L5 units 5. Our queen's killers were L2-6 with 1-6 steps.
- **Queen:** first split at r0 (median). She is L2-3 at r25-r400. Distance from her spawn is 14-18 (she roams), and
  the nearest enemy head is 8.6-9.4 away. She eats 14 pearls per game. When she dies, it is mostly head-on at
  r100-300.
- **Per map (all 88 games):** strong on the open maps (Around UNSW 6/7, Australia 5/5, Islands 5/5, Maze 5/5,
  Schooltime 6/6, Slithery 5/7, QoS 6/6, weakhold 5/6). **Weak on lane/small maps: Tower Defense 0/4, Trophy 0/3,
  Devil 1/3, Trauma 1/3.** There they don't reach mass (TD r100 total 8.5 vs 59.5).
- **Endgame:** 9/15 of their wins vs top teams and 18/31 vs us are eliminations. r500 wins come from queen-alive vs
  queen-dead, or from longest when both queens are L2-3 (Schooltime: both queens sit as L3 in their kelp boxes all
  game, so longest decides: 3 vs 20-47).

## 3. Our losses vs them with b4 code (40 losses, 57 games)
Per map, b4 code only: AUNSW 0/4, Australia 0/3, Autarky 2/5, Default 1/4, Devil 2/2, Islands 0/4, Maze 0/2, PD 2/4,
QoS 0/5, Schooltime 0/4, Slithery 1/5, Stripes 0/2, TD 4/4, Trauma 2/2, Trophy 2/2, weakhold 1/5.
(The old zips, 6 v35 and 5 v61 games, went 2-9: Portals 2/5, Australia 0/2, and so on.)

How the 40 losses end: 23 eliminations (18 with our queen dead before r150), 9 on longest, 8 on queen length.

**Decisive moment = the r50-100 mass race on open maps, not a single decision.** In losses the r100 total is 36 vs 82.
The fatal queen moves were checked in the harness: all 24 b4 losses where our queen died head-on, rounds R-3..R,
`fatal.py`, and **every base move MATCHes the server**:
- 13/24: the chosen move was rated threat 0. The killer lunged from beyond our modelled reach, or arrived from out of
  view (Australia ×3, Autarky ×2, Default ×3, Maze ×2, QoS, Slithery, AUNSW).
- 6/24: forced. Every candidate had threat ≥ 1. On weakhold (4/4) our L4 queen ate **0 pearls all game**, hovering
  at (8-10,0-1) with 1-2 candidates for many rounds until an L2-3 rams her at r152-284. The other two are Islands
  r22 (1369517, a corner reached by a 2-step sprint at r21; the L2 then closes the only exit) and QoS r54.
- 5/24: trapped. No candidates, then a reverse split (Islands r20 ×3, same position, the 6 Oct games; Autarky r245;
  PD r10).
- **Counterfactual tested:** `-D KREACH=1 -D KREACH_MINLEN=99 -D KR_CAP=4` (the queen alone sees kamikaze reach).
  It changes a move in the fatal window in 5/24 losses (1294526 r77, 1352321 r245, 1364970 r73, 1364972 r51,
  1378311 r61) and in 4/8 wins where the queen also died (1278152, 1278153, 1312610, 1373867). It is not selective,
  and it sits next to the KREACH/QKREACH/v69 rejections. **Rejected; not prototyped further.**

**Second waste source, measured:** before r100 we lose 8.5 units per game by moving into our OWN bodies; aAah loses
0.2. Most are on Slithery (50 per game), then Around UNSW 18, Australia 13, Islands 9. Harness on 8 such deaths in
1369514 (Slithery):
- 6/8 had **0 candidates**: L2-3 units boxed in by allies at r14-37, with 32-34 units on the map by r14.
- 2/8 chose a portal exit tile (57,13) E → (5,14) rated freeT=1 that was an ally's tail. This is the known portal-exit
  freeT issue (P2 in ROUND2, "real but doesn't change outcomes").

This is the crowding that s1/c1 showed is cheaper to keep than to block, so no fix is proposed.

**Cheap known-map fixes:** none found that keep everything else identical.
- weakhold is the only map with one repeated mechanism (4/4 losses: a starved home queen rammed at r150-280).
  The obvious levers (queen park or crown on weakhold) already lost in q1, and `WH_QCROWN` was never decision-verified.
- Schooltime 0/4 is pure economy: both queens are boxed at L3 and longest decides.

## 4. Data integrity: which of our zips actually played (verified)
`whichsub.py` rebuilt each game, replayed our queen r0-12 with each candidate zip, and required an exact match.
Every b4 match was then confirmed by the full fatal-window replays.

| zip | games vs aAah (6 Oct 16:49 - 7 Oct 19:31) | record |
|---|---|---|
| b4/kf1 code (19891 = 18751; kf1 identical at these turns) | 57 | 17-40 |
| **v35 (14238)** | 6 (Stripes 1303363 and Maze 1303362 at 03:02-03:07; Portals 1369513 17:27 and 1378312 19:29; one Around UNSW, one Default) | 0-6 |
| **v61 (16388)** | 5 (Portals 05:09, 13:45, 18:28; Australia 17:27, 18:26) | 2-3 |

- The old zips show up **within the same 5-game series** as b4 games. In the 17:25-17:31 series: weakhold b4,
  Portals v35, Australia v61, Islands b4, Slithery b4. An activation switch can't explain that, because activation
  is team-wide. It is specific to the aAah series: 12/12 same-window games vs FTM, SSS, horse, Sponge, DEV and
  Sabotage-d were b4. 1311053 (Bot, 04:43 Oct 7) was v61, which matches the v61 activation Codex logged.
- We are the listed "a" side in all 70 games vs aAah, so these were our loop's challenges. The mechanism is unknown.
- **Consequences:**
  - (1) kf1's -6.0 pp verdict and the kf1 vs aAah 20-56 include v35/v61 games. Portals vs aAah was never b4 in this
    sample.
  - (2) Any per-map or A/B scoring by upload window should drop aAah games, or classify them with the harness first.
  - (3) The harness default `--sub b4` silently gives 0-70% matches on these games. That is how it was found.

## 5. What generalises to unseen maps (Qualifier, Bo7, all unseen)
1. **Open maps are a harvest-speed race decided by r100.** aAah's L5-12 units move 2-3 tiles per turn for free and
   sprint through pearls (a paid step onto a pearl is net 0). They reach the 64 cap by r200-300. On any unseen open
   map they will out-mass b4 by r100. Our MIDSIZE test (ms1: half the units, split at L6 from r150) is not their
   design. Theirs starts at r50, applies to every unit, and splits L-2 off with the parent kept at L2. This is the
   largest structural gap, but it is a post-Qualifier project, not a 24-hour flag.
2. **A small, distant queen.** They split her at r0 to L2 and keep her about 9 tiles from enemy heads. She survives in
   about half of all games, and a living L2 queen beats a dead one in the tiebreak. b4's queen grows from r0
   (QS_FROM=100) and dies before r150 in 26/40 losses. Similar ideas lost before (l1 lane small queen, QPARK_UNK
   unseen park), so this is evidence for a future redesign, not a flag to ship.
3. **Kamikaze lunges.** Every kill is mutual. They pay length to reach queens and kings 3-5 tiles away, so threat
   models that assume free-step reach are wrong against them. Our KREACH counterfactual shows the reach model
   alone isn't selective.
4. **Their weakness: lanes and small maps** (TD 0/4, Trophy 0/3, Devil 1/3, Trauma 1/3). On narrow unseen maps, b4's
   fast-split elimination style beats them. In a Bo7 vs aAah, the open unseen maps will be lost and the narrow ones
   won.

## 6. Not done / caveats
- No prototype in `scratchpad/top4/aaah/bot/`: the only decision-level candidate (KREACH queen-only) failed
  selectivity, and nothing else was cheap.
- The vs-top sample is small (20 games, 4 per opponent, ranked only). A build-change claim needs per-map
  before/after pairs, which this sample lacks.
- The game list was crawled to 6 Oct 22:42 only (the crawl was stopped at 30 h).
