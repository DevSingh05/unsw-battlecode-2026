# Elo policy before the freeze (written 2026-09-30 17:15 UTC / 13:15 EDT)
**Formula (fit on 70 ranked series, 10:52-17:08 UTC):** it is per game. Our change = round(5 * (W - n*E)), where E = 1/(1+10^((Opp-Us)/400)) is computed once per series from the pre-series ratings. K=4.75-5: 61/70 exact, the rest off by 1. A series-outcome model fits badly: 6/70 exact.
Opponents have their own K. Eric Allen Le got +27 from a 3-2 where we got -7, and calc got -26 where we got +8. So challengers with provisional or high K gain far more than we lose.
Why a 4-1 loses Elo: against a team 400 below us, E = .909 per game, so we need 4.55 wins out of 5 to break even. 4-1 = -3, 5-0 = +2, 3-2 = -8.

**Per series vs opponent tier (per-game p from v34 games since 11:30, ranked+unranked / ranked only; EV = 25*(p-E)):**
| opp - us | break-even p | our p (all) | EV/series | our p (ranked) | EV/series |
|---|---|---|---|---|---|
| -400 | .909 | .914 (105g) | +0.1 | .855 (55g) | -1.4 |
| -300 | .849 | .800 (60g)  | -1.2 | 1.00 (10g) | +3.8 |
| -200 | .760 | .816 (256g) | +1.4 | .773 (75g) | +0.3 |
| -100 | .640 | .681 (210g) | +1.0 | .600 (40g) | -1.0 |
|    0 | .500 | .516 (213g) | +0.4 | .531 (130g)| +0.8 |
| +100 | .360 | no data (we are #2) | | | |
Using all data since 10:52 (including test builds) gives the same picture: -400 +0.1, -300 -1.2, -200 +1.5, -100 +0.6, 0 +0.2. The battles API only returns the last 200 battles, so there are no older at-time ratings.

**Ranked series since 14:00 UTC (we launched none; initiator = teamA, and autoscrims are requested at hh:00:00 with us as A):** 33 series, net **-12** (2106 -> 2094).
- Autoscrims, 3 series, -9: Cutlery 2-3 -4, SSS 2-3 -4, bfs 3-2 -1. A 4th vs ftm (17:00, 2096) is live at 3-2 to us, about +2.
- Incoming challenges, 30 series, -3: SHINK AI 6500 (-220) challenged 8 times, 29/40 games, **-12**. okbro (-400) 5 times in 3 min, 20/25 games, **-15**. Eric Allen Le 3-2 -7, BambooCode 4-1 -3, ftsp 3-2 -3. Gains: Cutlery 5-0 +10, C-- 5-0 +6, a few +1..+3. Full list: scratchpad pf/since14.txt.
- Adverse selection: the challengers pick themselves. A team that overperforms against us (SHINK, okbro) keeps challenging, and one that gets crushed stops. So incoming EV runs below the model, about -0.1/series, while the rate is high: ~11 series/h, SD ~4.5 Elo per series.

**Recommendation: turn ranked OFF now, and turn it back ON about 30 min before the freeze only if we cannot confirm that ranked-off teams are still in the post-freeze autoscrims.**
- Keeping it ON for ~7 h until the freeze (00:00 UTC / 20:00 EDT per journal; user says ~6 h) means ~75 incoming series. Mean ≈ 0 to -8, SD ≈ ±40 Elo.
- The top 7 sit within 49 Elo (2096 / 2094 / 2076 / 2074 / 2069 / 2057 / 2047). At #2 the upside is one place, and a 1-SD downside drops us to about #7. The payoff is lopsided, so cutting variance is right.
- Pre-freeze Elo is the starting point for the 3 h of post-freeze autoscrims. Before the freeze we saw exactly 1 autoscrim/hour at K=5/game (max about ±12/series). If that pace holds, post-freeze play moves us only ±15-30 and pre-freeze Elo mostly decides seeding.
- UNKNOWN: whether ranked-off teams are paired in the pre-freeze or post-freeze autoscrims. The journal says SSS/Cutlery had ranked off at 06:02, yet they autoscrimmed us at 14:00/15:00. They may have switched it back on (Cutlery challenged us ranked at 16:27), so this proves nothing. Ask organizers.
- If ranked-off does remove us from autoscrims, the cost is small: about +0.3 to +0.8 per autoscrim at p≈.52 vs near-rank teams, about 7 series before the freeze.
