# How the teams that beat us play under the new rules (2026-10-01, replays after 15:30 UTC)
Data: 27 battles / 140 games vs C-- 55, calc 25, Stockfish 20, 中国必须人能飞 20, 3.14159265 15, EternalWisdom 5 (Sponge: none in window). 63 losses.
Replays: scratchpad nr/*.replay + index.json; per-game records in nr/rows.pkl (scripts an2.py, rep.py, replay_sim.simulate).
Caveat: "US" = whatever submission was active per battle (most are 16:4x-18:5x unranked challenges); dist = Manhattan head-to-head at turn start (5+ usually means a portal/wrap).

## Outcomes
- 37 losses at r500, 26 by elimination (Trophy 10, Dilemma 6, Devil 5, QoS 2, other 3).
- Queens nearly never decide it: at r500, queen alive in 0/37 losses for us and 1/37 for them. The one queen-decided loss was 829875 (C-- Schooltime): their queen L14 alive, our longest 36 vs their 22, we lost. Everything else was decided by longest living dragon.

## 1. They grow one big dragon; we spread length over many (r500 losses)
- Final medians in r500 losses: our longest 39 vs their 56. Our total 126 vs 124, and our total is higher in 24/37 of these losses. Units 15 vs 7.
- Their king pulls ahead early. Mean longest, us vs them: r200 5 vs 11, r300 13 vs 15, r400 27 vs 31.
- In our r500 wins the picture flips: longest 44 vs 27.
- Our extra mass sits in small units, and the tiebreak gives it zero value.

## 2. Free sprint: C-- and 中国 use it, we don't
| Team | % of turns with 2+ steps, L5-8 | L9+ |
|---|---|---|
| C-- | 53.5% (n=12.3k, 99% free, 99% at exactly ceil(L/4)) | 60.5% (n=10.2k, 99% free) |
| 中国 | 2.6% | 5.3% (all free) |
| Us | 0.1% | 0.4% |
| Stockfish / calc / 3.14 / EW | 0.0-0.8% | 0.0-0.8% |
- Nobody pays for multi-steps with big dragons. Paid multi-steps happen only at L2-4, and those are lunges.

## 3. Lunge reach is 2-3 tiles, and they hit us from outside the 1-step model
- Our L>=5 head-on deaths (179 total, 126 in losses): killer distance at turn start was 1: 40, 2: 60, 3: 37, 4: 20, 5+: 22.
- So 97/179 (54%) started at distance 2-3, and 80% were 2+ away. In 126/179 the killer moved 2+ steps that turn.
- Killers are tiny: median length 3 (Stockfish 4), against victims of median length 6-7.
- Stockfish lunges 3 deep (kdist 3: 21 of its 61 kills on our L>=5). An L4 that pays 2 steps can travel 3.
- Our own lunges top out at distance 2 (kdist 3+ only 1-2 times in 400+ kills), so they outreach us by 1.
- All sizes: 1240/2795 (44%) of our head-on victim deaths had the killer at distance 2-3.

## 4. Elimination games are a unit and pearl snowball decided by r50
- Elimination losses, us vs them: units r25 5.6 vs 6.3, r50 8.1 vs 13.0, r100 9.5 vs 27.8. Total length r50 20 vs 33, r100 22 vs 69.
- Elimination wins are the mirror: r100 27 vs 8.5.
- Head-on trades are about even (we kill 15.5 per game, they kill 16.3), so the difference is in growth.
- Their dragons die into walls 19 times per game (feeding by suicide). Ours die 5.6 times per game by HitSelf.
- 77% of their 2+-step head-on kills are made by L2-3 units.

## 5. Queens: everyone treats the queen as a splittable unit; ours just dies first
- Our queen median death round is 15 (EW games 14, calc 10, 中国 10). Theirs is 28.5 (EW 99, n=5).
- Ours: 92/140 die HitSelf at L2-3, the split-down remnant fed or trapped. Theirs: 65/140 die HitWall, mostly the same kind of remnant suicide.
- Queen head-on kills: they killed ours 16 times, we killed theirs 34. Every one was a distance 1-2 lunge by an L2-3 unit.
- Splitting: we split more than every opponent. Units at r100, us vs them: C-- 33.5 vs 19.9, Stockfish 37 vs 31, EW 26 vs 24. Splits per game: 391-500 for us vs 167-308 for them, mostly 4 -> 2+2 churn.

## Implications
1. Use r500 rules: stop splitting mass off the king once r>=200 and grow the single longest. Score is longest, not total.
2. Give big dragons free ceil(L/4)-step pathing for food and escape, as C-- does.
3. Danger model: an enemy L3-4 can reach 2-3 tiles. Check this for any dragon of L>=5.
4. Elimination maps: avoid falling behind in units/food by r50.
5. Keep the queen out of the split/feed pool (cheap; it decides about 1 in 37 games now, and more once the safer-spawn maps arrive).
