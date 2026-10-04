# Loss audit 2: v55 + v61 server games (2026-10-03/04)

Written ~01:45 UTC 4 Oct (21:45 EDT 3 Oct). Read-only audit. No code changes, nothing submitted, no challenges.

## Data
- Game list from `python3 tools/ab_server.py v55 v61 --ends --json replays/loss_audit2/ab_rows.json` (run from the project root).
  Windows: v55 #15842 11:47-15:27 UTC 3 Oct (485 games, 298-187). v61 #16063 17:54-19:50 UTC (171 games, 108-63).
  The v61 re-upload #16233 from 01:02 UTC had only 7-10 finished games at fetch time and is not in the replay set.
- Replays in replays/loss_audit2/: all 250 losses (no draws) plus 99 wins (the 3 wins against the highest-rated
  opponents per map x tier). summary.json = all 656 games; rows.json = 349 classified games.
- Scripts: notes/newrules/loss_audit2_tools/ (copies of scratchpad la2/). fetch2.py -> build2.py (replay_sim -> pkl,
  2 workers) -> classify2.py -> an1/an2/an3.py, tqseen.py (how long their queen stayed in our view after ours died).
- top-10 = current leaderboard top 10 excluding us (ab_server definition).
- Decisive cause, per loss:
  - eliminated: we had 0 dragons before r500.
  - r500 queen dead: ours dead, theirs alive.
  - r500 both dead, longest lost.
  - r500 queen shorter/equal: both queens alive (Schooltime q3 v q3 then goes to longest).
- "trapsplit" = the queen split within 4 rounds before dying at L<=3. In this build that always means QBOX_K2 shedding 2 at a time.

## Headline: we lose r500 tiebreaks, not fights
ab_server end-type split (PAE per game, pooled R_us 2140):
| | elim W-L | elim PAE | r500 W-L | r500 PAE |
|---|---|---|---|---|
| v55 vs top-10 | 33-32 | +3.8 | 62-62 | +4.0 |
| v55 vs rest | 94-21 | +4.9 | 109-72 | **-12.4** |
| v61 vs top-10 | 15-10 | +15.1 | 17-23 | -1.0 |
| v61 vs rest | 40-10 | +7.9 | 36-20 | **-8.5** |
Our whole deficit against weaker teams is in games that reach r500.

## Cause x tier (250 losses; v61-only in brackets)
| cause | vs top-10 (127) | vs rest (123) | v61 top-10 / rest (33 / 30) |
|---|---|---|---|
| r500, our queen dead, theirs alive | 49 (39%) | **55 (45%)** | 13 / 11 |
| eliminated | 42 (33%) | 31 (25%) | 10 / 10 |
| r500, both queens dead, longest lost | 26 (20%) | 20 (16%) | 6 / 6 |
| r500, both alive, queen shorter/equal | 10 (8%) | 17 (14%) | 4 / 3 |
Against the rest, 92 of 123 losses (75%) are r500 tiebreaks.

## Cause x map (all 250 losses)
| map | L | elim | r500 Q dead (died <=r100) | both dead | Q shorter | top-10 share |
|---|---|---|---|---|---|---|
| Devil | 27 | 19 | 8 (8) | 0 | 0 | 14 |
| Portals | 26 | 0 | 19 (18) | 7 | 0 | 13 |
| Maze | 25 | 0 | 16 (0) | 8 | 1 | 8 |
| Slithery Fight | 21 | 0 | 13 (4) | 5 | 3 | 10 |
| Autarky | 18 | 6 | 7 (2) | 3 | 2 | 10 |
| Around UNSW | 17 | 0 | 7 (4) | 10 | 0 | 11 |
| Australia | 16 | 0 | 12 (12) | 4 | 0 | 7 |
| Schooltime | 14 | 0 | 0 | 0 | 14 | 7 |
| Trophy | 14 | 14 | 0 | 0 | 0 | 7 |
| Prisoners Dilemma | 13 | 8 | 3 (2) | 0 | 2 | 6 |
| Tower Defense | 12 | 5 | 6 (2) | 0 | 1 | 5 |
| Queen Of Spades | 11 | 9 | 1 | 1 | 0 | 7 |
| Islands | 10 | 0 | 5 (4) | 5 | 0 | 7 |
| Stripes | 10 | 9 | 0 | 1 | 0 | 6 |
| weakhold | 9 | 1 | 5 (0) | 0 | 3 | 6 |
| Default | 6 | 2 | 2 (1) | 2 | 0 | 3 |
| Trauma | 1 | 0 | 0 | 0 | 1 | 0 |

Weakest v61 maps on the server, and what kills them:
- **Maze**: queen killed late (r130-440) by L2-3 enemies (13) or a shed chain in a corridor (9). Their queen is usually a big king (L15-125). We are also behind on mass in 10 of 16.
- **Devil**: eliminations with the gap opening at r29-70 (19). In the other 8 our queen died at r25-96, head-on with an enemy L2-3, while their L2-3 queen survived. We led on mass in all 8, four times 141-174 v 2.
- **Portals**: 21 queen deaths before r100 are the same shed chain: the queen eats into a 2x2 portal vault, L5 -> 8, sheds 2 three times, dies HitSelf at L3 (e.g. 964249 r30-36). Their queen then sat in our view for 200-300 rounds.
- **Slithery**: shed chains in kelp corridors, early and late (15), plus H2H (3).
- **Around UNSW**: 10 of 17 are both queens dead with longest lost. We had more total mass in **all 10** (median 1.5x; 380 v 199, 368 v 114) but a shorter longest dragon (median gap 5: 31v35, 50v52, 52v53, 56v59).

## Queen-death mechanics (150 r500 losses where our queen died)
- Shed chains (QBOX_K2): 89 (59%). HitSelf 59, ally body 30. Typical sequences: [L8 k2 ex1] [L7 k2 ex0] [L5 k2 ex1] -> L3
  dies, or 6 -> 4 -> 2. Neighbours at death are kelp + own neck + ally body. In Portals, Australia and Around UNSW the
  pocket is reached through a portal before r100, when the early queen has no QUEEN_BLIND_PEN/QUEEN_PEXIT_PEN.
  Australia 967616: she crosses a portal onto a blind tile at r56 into a 1-wide kelp pocket full of allies and is dead by r60.
- Head-on by an enemy: 55. Killer L2-3 in 45, the queen L4-6, mostly enemy_near 1.
- Timing changed with QS_FROM=100. Queen deaths before r100 (losses + win sample, v41/43 audit -> v55/61):
  Portals 5/34 -> 27/32, Australia 3/15 -> 21/22, Tower Defense 0/18 -> 9/18, Slithery 1/31 -> 10/27, Devil 12/27 -> 32/33.
  Per-map PAE on the server, v44 -> v55: Portals +9, Australia +5, Slithery 0, Around UNSW 0, **Tower Defense -19**.
  So earlier queen deaths did not lower PAE on most big or portal maps. Tower Defense is the exception.
- In the win sample, our queen survived in 38/99 and theirs died in 85/99. We win when their queen dies.

## The biggest lever: their queen survives while we are ahead
- Of the 104 r500 queen-dead losses: our total mass ended higher in 61 and our longest was longer in 65.
  Their queen was L<=4 in 26 (19 of them vs rest).
- tqseen.py, after our queen died:
  - Their queen came within Chebyshev 3 of one of our heads for >=10 rounds in 74 of 104.
  - In **52 of 104** she was seen >=10 rounds AND we ended ahead on mass: 21 vs top-10, **31 of 55 vs rest**.
  - By map: Portals 16, Devil 8, Maze 6, Tower Defense 5, Around UNSW 3, Autarky 3, Slithery 3, Australia 3.
- 20 losses ended with the opponent at <=25 total mass, often a single L2 queen, against our 50-174.
  Devil 968373 (test4): they had 1 dragon, an L2 queen wandering their x 27-31 home box, for 400 rounds, and we had 141.
  We lost on the queen tiebreak. Our units never go there (no pearls left), and QKILL/QUEEN_HUNT in tryRam
  (main.cpp:3640-3650) only fire when she is within K reach of a unit that happens to be adjacent (an L2 has K=1).
- About 21% of all losses (25% vs rest) were winnable by killing a queen we could already see. That is a head-on
  trade, which kills both whatever the lengths.

## Ranked fix list (current build v61)

### 1. Late enemy-queen hunt, gated on "our queen is dead" (targets ~52 losses, 21%; 25% vs rest)
- Port v59's EQ_HUNT (enemy-queen tracker + relay + BFS pull for small units; v59 = v51 + v47 code) onto v61,
  with a new gate in place of the v47 "T" non-runner rule (max len >= 8 or static).
- Gate: pull only when our queen is known dead (non-queens: `!qstOurAlive()`, main.cpp:2115) and theirs is alive.
  From then on every r500 game is lost unless she dies or we eliminate them, so the hunt costs almost nothing.
  Also pull when the visible enemy count is tiny (finisher).
- Settings: hunters L<=8 (any length when she is L<=4), radius = whole map via EQH_BFS with a larger EQH_CAP (e.g. 60),
  EQH_MEM 40+, EQH_MIN_UNITS 3, EQH_NOTHREAT=1 (her head-on with a hunter is the goal).
- Plumbing: in v61, qsOurRound is only updated by QSTATE (main.cpp:1890, 2124-2137). The our-queen beacon/relay must
  run under the new flag without QSTATE's own-queen play-safe modes. In v59 the beacon stayed QSTATE-only, so this
  part is new code.
- Not tried on the server. v47/v59 were neutral locally (.525/.491), but self-play can't show this: both queens die
  symmetrically. The gate is the new angle.
- Local check: games where our queen is dead by r150 vs a v61 copy. Count enemy-queen kills after that and r500 W/L.

### 2. Around UNSW (and big Sprint maps) king consolidation (10 AUNSW losses; 46 both-dead losses overall)
- All Sprint maps share UNK_KING_SEED 250 / UNK_KING_FEED 300 (applyMapParams, main.cpp:90-101; params.hpp:605/608).
  On AUNSW we out-mass them 1.5x and still lose the longest race by ~5.
- Change: per-map override for Around UNSW, seed ~180-200 and feed ~220-240, possibly a larger feedReserve. Same
  candidate for Islands and Australia, where the both-dead losses are close (51v78, 45v51, 47v54).
- Cheap: params only. Different from the rejected QK_BIG, which made the queen the king. This keeps the non-queen king.
- Local check: longest at r500 on AUNSW/Islands/Australia vs v61. That measures fine in self-play.

### 3. Queen shed-chain deaths: stop the early queen eating into portal pockets (89 of 150 queen deaths)
- Already rejected or no-op: QEXIT_LOOK (server v60, -1.4pp), QDEAD2 (local), QNOPOCKET (never fires),
  QKREACH/QWARN/QESCORT, QSPLIT_MIN4 (no-op). Do not re-propose these as-is.
- New angles:
  - (a) Apply the queenSafe portal penalties (QUEEN_BLIND_PEN 200, QUEEN_PEXIT_PEN 80) in the pre-QS_FROM phase as
    well. Today they are gated by queenSafe() (main.cpp:2105), which is off before r100 under QS_FROM=100. 18 of 19
    Portals queen-dead losses and 12 of 12 Australia ones died before r100 through a portal pocket.
  - (b) Or the built-but-never-server-tested v58 QS_SMALL. It keeps QS_FROM=100 only on area <= 1024 maps without
    dense portals (Devil, Stripes, Dilemma, Trophy, QoS, Default, TD; Portals and the big maps go queen-safe from r0).
    Its local screen was the best of that batch (.548), but the server per-map deltas for v44 -> v55 on Portals and
    Australia were positive. So (a) is the cheaper and more targeted test.
- Expected gain is smaller than fix 1. On Portals their queen is a roaming king we could hunt anyway.

### 4. Devil/Trophy early eliminations (33 losses, 13%; the gap opens r29-55)
- Locally rejected: HOME_DEFEND, EARLY_PUSH (v48), COVERAGE+STP4 (v56, .478). None were server-tested.
  LUNGE34 was rejected on the server (v64).
- No new cheap idea from this audit. The 8 Devil r500 losses (their L2 queen alive, us ahead on mass) are covered by fix 1.

### 5. Schooltime box (14 losses, all both queens L3, longest lost)
- In half of them our army was wiped out (our total 3-90 vs 197-250) and only the boxed queen lived. The rest are
  close king races (61v80, 66v69, 39v47). This is an economy problem with a long tail. Lower priority.

## Already rejected on the server (don't repeat without a new angle)
- v60 QEXIT_LOOK (-1.4pp)
- v64 LUNGE34 + INFER_SYM (-6.8pp)
- v65 QK_BIG, the queen as king on big maps (-6.4pp)
- Accepted: v55 QS_FROM=100 (+5.7/+7.0pp vs v44), v61 QSPLIT_ROOM (+3.2/+3.5pp, CI crosses 0).

## Notes / caveats
- The win sample is biased toward strong opponents (3 per map x tier). Win-side rates are only for contrast.
- Cause counts mix v55 (187 losses) and v61 (63). The v61-only split has the same shape: r500 queen dead is the top cause in both tiers.
- "Seen" uses Chebyshev distance <= 3 between heads, ignoring walls. On Portals she can be across a kelp/portal edge.
  So read the 52 as an upper bound on easy kills. The 20 games where the opponent was down to <=25 mass are the clearest cases.
