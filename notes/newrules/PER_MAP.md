# PER_MAP: how every server build did on each of the 17 ranked maps

Written 2026-10-07 ~20:30 UTC (16:30 EDT) by the `measure` step of the per-map portfolio workflow. Read-only analysis: nothing was submitted and no loops were touched.
Data: 10,969 of our server games from 3 Oct 07:18 UTC to 7 Oct 20:54 UTC (`replays/ab_server/games.json`, refreshed today), the submissions list (`byMap` per-map ratings, fetched about 19:55 UTC) and mechanism rows from `replays/ab_mech/*/rows.json` (extended today: b4, v1, u1 complete; kf1/pb2 to 200; v55/v65/v69 100; v60/v64 80).
Scripts and raw outputs: scratchpad `pmp/measure/` (`p2.py` model, `report.py` tables, `permap_l*_d*.json`).

## 0. Read this first: attribution error, kf1 vs v61 on 7 Oct

**From about 03:20 UTC on 7 Oct until the b4 upload at 19:26 UTC, the active submission was v61#16388, not kf1.**
- The server credits v61#16388 with 2,363 games. Its own upload windows hold only 890.
- The 1,473 extra games match, per map and per W/L, the last 1,459 games of the "kf1" upload window (03:25-19:25 UTC on 7 Oct). The error summed over all 34 W/L cells is 30 games.
- Team rating history shows the switch: 2210 at 03:13, then 2174 at 03:23. It ended at 2184 (v61's rating), not kf1's 2174.
- kf1 actually ran 6 Oct 16:54 to 7 Oct 03:12 UTC: 1,318 games, 13% ranked. The server credits it 1,227.

What this means:
- Every upload-window tool (`ab_server.py`, `ab_mech.py`) counts 16 hours of v61 play as kf1. The kf1 verdict in STATUS (392 games, -6.0 pp) came from a cache that stopped at 6 Oct 19:22, so it only saw true kf1 games. That verdict stands.
- Nothing in the journal explains who re-activated v61, or why. Someone should check before the freeze.
- All numbers below use the corrected attribution. Games in the ambiguous 03:13-03:25 interval are dropped.

Other uploads match the server's per-submission counts to within queueing slop: plus or minus 40 games at window edges, mostly c1, b3 and b4#18751.

## 1. Builds and flag sets relative to b4

Sources:
- Staged `params.hpp` in the scratchpad (`r2/c1`, `r3/m1,m2`, `r4/q1`, `r5/f1`, `r7/h1`, `r8/k2,cm_pack,sdf`, `r10/l1`, `r11/ms1`, `dgu/u1`, `r12/v1,pb2`, `r13/kf1`).
- `variants/{v61,b1,b2,b3,b4,f1}`, STATUS.md and the journal.

INFER_SYM and MATCH_STRICT-lite only act on unseen maps, so they are ignored here.

Token legend:

| token | flag | maps it acts on |
|---|---|---|
| QS | QS_FROM=100 | all |
| QSR | QSPLIT_ROOM=1 | all |
| FUEL | QKILL_FUEL=1 | all |
| PARK_P | PM_QPARK_PORTALS | Portals |
| PARK_M | PM_QPARK_MAZE | Maze |
| CRAUS | CROWD_MAPS bit 2 | Australia |
| CRAUN | CROWD_MAPS bit 1 | Around UNSW |
| TDP | PM_TD_PULL=2 | Tower Defense |
| QVA | QVAULT bit 2 | Australia |
| QVS | QVAULT bit 1 | Slithery |
| QEXIT | QEXIT_LOOK | all |
| L34 | LUNGE34 | all |
| QKBIG | QK_BIG | treated as all maps; the "big map" gate wasn't recoverable from the archive |
| QEP | QEARLY_PEN | all; its blind-tile penalty applies everywhere |
| C1 | SPLIT_NEEDS_EXIT + LATE_HUNT + QKILL_KING | all |
| H1 | LATE_HUNT + QKILL_KING | all |
| QKEG | QK_EG=2 | Portals and Maze (the crowned queen exists only there) |
| QGR | QG_RAM=8 | Portals and Maze (crowned queen) |
| STR | STRIPES_LOOP | Stripes |
| TRQ | TROPHY_QSPLIT | Trophy |
| SCHB | PM_SCHB=3 | Schooltime |
| TRG | PM_TROPHY_RG=2 | Trophy |
| SCHD | SCH_DOORS | Schooltime |
| SCHC | SCH_CHAMBER | Schooltime |
| Q1PARK | PM_QPARK_{AUSTRALIA,AUNSW,SLITHERY,TOWER,WEAKHOLD} | those 5 maps |
| LANE | LANE_QSMALL=54 (+LANE_QSM_LATE=4) | TD, Devil, Autarky, QoS |
| SDEF | SPLIT_DEFER=3 | all |
| MID | MIDSIZE=1 (MS_FROM 150, MS_BULK 0, MS_SAFE 15) | all |
| PB | QBOX_ONESPLIT=1 | all; fires from r200 |
| KF | QKILL_KING + QKK_FREE | all |

b4 = QS QSR FUEL PARK_P PARK_M CRAUS TDP QVA.

| build | flags vs b4 | live windows (UTC, from games; corrected) | games | ranked | win |
|---|---|---|---|---|---|
| v44 | -QS -QSR -FUEL -PARK_P -PARK_M -CRAUS -TDP -QVA | 10-03 07:18-11:39 | 374 | 65% | 60% |
| v55 | -QSR -FUEL -PARK -CRAUS -TDP -QVA | 10-03 11:54-15:24 | 485 | 43% | 61% |
| v60 | v55 +QEXIT | 10-03 15:34-17:49 | 196 | 52% | 54% |
| v61 | -FUEL -PARK_P -PARK_M -CRAUS -TDP -QVA | 10-03 18:10-19:50; 10-04 01:04-02:23; 10-04 04:32-17:13; **10-07 03:31-19:25** (not in its upload window) | 2616 | 33% | 54% |
| v64 | v61 +L34 | 10-03 19:56-21:41 | 163 | 40% | 57% |
| v65 | v61 +QKBIG | 10-03 21:57-10-04 00:48 | 265 | 66% | 56% |
| v69 | v61 +QEP | 10-04 02:34-04:26 | 195 | 83% | 57% |
| c1 | v61 +C1 | 10-04 17:18-18:25 | 81 | 32% | 43% |
| m1 | v61 +PARK_P +PARK_M +STR +TRQ +SCHB | 10-04 18:42-20:06 | 95 | 31% | 58% |
| m2 | m1 -SCHB | 10-04 20:23-22:40 | 219 | 18% | 60% |
| b1 | v61 +PARK_P +PARK_M | 10-04 22:53-23:33 | 74 | 93% | 49% |
| q1 | b1 +Q1PARK | 10-04 23:41-10-05 02:39 | 416 | 24% | 53% |
| f1 (=b2) | b1 +FUEL | 10-05 02:52-04:22 | 240 | 22% | 64% |
| h1 | f1 +H1 | 10-05 04:32-08:11 | 586 | 49% | 50% |
| k2 | f1 +QKEG | 10-05 08:19-10:24 | 315 | 60% | 52% |
| cm1 | f1 +CRAUS +CRAUN | 10-05 10:30-12:13 | 217 | 53% | 53% |
| s1 | b3 +SDEF (assumed b3-based per STATUS; the staged `sdf` dir predates CROWD_MAPS=2, so the Australia class membership is uncertain) | 10-05 12:19-14:24 | 330 | 56% | 43% |
| b3 | f1 +CRAUS | 10-05 14:30-14:39; 16:38-18:09; 20:45-22:51; 23:35-10-06 03:04 | 865 | 59% | 49% |
| l1 | b3 +LANE | 10-05 14:46-16:30 | 254 | 53% | 44% |
| ms1 | b3 +MID | 10-05 18:24-20:39 | 357 | 52% | 38% |
| u1 | b3 +TDP +QVA +QVS +SCHD +SCHC +TRG +QGR | 10-05 22:57-23:10 | 30 | 16% | 43% |
| v1 | b3 +TDP +QVA +QVS +SCHD | 10-06 03:09-05:09 | 245 | 19% | 44% |
| pb2 | b4 +PB | 10-06 05:16-15:38 | 814 | 30% | 60% |
| b4 | (b3 +TDP +QVA) | 10-06 15:55-16:49; 10-07 19:31-now (live) | 115 at 19:50 | 61% | 57% |
| kf1 | b4 +KF | 10-06 16:54-10-07 03:12 (**corrected**) | 1318 | 13% | 42% |

## 2. Method

- **Equivalence classes.** For each map, builds whose flag sets agree on the tokens that act on that map form one class, and their games are pooled.
  - Example: on Islands, f1, k2, cm1, b3, l1 and b4 are one class.
  - The class that contains b4 is the baseline. Each class's members, and the games each member played, are listed in its table row.
- **Adjusted model.** One joint ridge-logistic fit over all 10,969 games (`p2.py`):
  - logit(win) = map + (map x class), with ridge 0.25 and b4-class = 0
  - \+ opponent (ridge 0.3, for opponents with at least 12 games)
  - \+ opponent x 24 h block (ridge 1.0, for at least 6 games in the block). This is the time-local opponent context: it absorbs opponents uploading stronger bots, and dev-team changes.
  - \+ Elo slope for rare opponents, + ranked + autoscrim.
  - Fitted ranked +0.15 and autoscrim -0.04 (logit). Draws count 0.5.
- **Effect in pp.** Average marginal effect: every game of the class and of the b4 class is predicted once as each class. The CI comes from the coefficient's standard error, and P(better) = Phi(est/se).
- **Sensitivity.** Ridge 0.05 (shown as [λ.05]) and 12 h opponent blocks both move effects by about 1-3 pp, so I don't tabulate the 12 h version.
- **Time-local check.**
  - The model is refitted on all games within ±36 h of the class's games on that map, with opponent terms from that window only.
  - The contrast is against b4-class games on that map inside the window. It reads "n/a" when fewer than 8 such games exist (v44, v55, and most Oct 3 builds on maps where the b4 class starts on 5-6 Oct).
- **E[win] as b4.** The mean predicted win probability of the class's games if b4's class had played them. When it is far from the b4 class's own value, that row faced a different opponent mix, and the raw W-L can't be compared directly.
- **Server per-map rating.** `byMap` rating (W-L) for each member upload with at least 5 games on the map (the upload with the most games when a name has several). Rating per map = R + O_m. The team rating is their mean over the 17 maps.
- **Mechanism columns.** From `ab_mech` replays, sampled and not complete for every build:
  - n (replays on this map)
  - q500 = our queen alive at r500 / games that reached r500
  - elim = games we lost by elimination
  - lr300 = geometric mean of our total length / theirs at r300

## 3. How much to trust a per-map number: two calibrations

1. **Same code, different days.** v61's games split into its 3-4 Oct blocks and its 7 Oct block (identical code):

   | map | 7 Oct block | 3-4 Oct blocks |
   |---|---|---|
   | Devil | +8.5 | -8.1 |
   | Islands | -5.3 | +9.2 |
   | Tower Defense | -30.5 | -14.1 |
   | Australia | -27.8 | -14.9 |
   | Autarky | +4.0 | +13.5 |
   | Around UNSW | -9.3 | -1.2 |
   | Trauma | -7.3 | +0.1 |

   - Both sides are measured against the same b4 class, so the gap between them is noise plus drift the model does not absorb.
   - A placebo split of the b4 class itself, before vs after 6 Oct 00:00, gives "early minus late" of +23 on Portals (P 1.00), +14 on Stripes (P .97) and +8 on Trauma (P .97). Australia, +42, has only 5 early games. On the other 13 maps it is within ±12.
   - **So on a single map, an effect under about 15 pp, or with P(better) under about .97, is not reliable on its own.** With ~250 contrasts, about 12 will reach P .95 by chance.
   - Trust effects that are large and repeat across members and eras, or that a mechanism and the server's own rating also support.
2. **Server per-map ratings are noisy too.**
   - Identical b3 code on four uploads got Around UNSW 2037/2124/2206/2220, Trophy 2141-2307, Default 2196-2363 and Portals 2240-2375.
   - Ratings move only on ranked games, and test builds were mostly unranked, so their per-map ratings are largely inherited.
   - Each new upload also **inherits** the previous active submission's per-map offsets (with extra uncertainty). The per-map ratings along the upload chain are therefore one running estimate that drifts with time, not independent votes per build.
   - A single upload's per-map rating is weak evidence. Patterns across many uploads are better.

**Shared-baseline caveat:** every contrast on a map is measured against the same b4-class games. If the b4 class was unlucky on a map, every row looks better; see weakhold and Schooltime.

## 4. Summary per map

Columns:
- **b4 srv:** server rating of b4#18751 / b4#19891 (team mean = 2234 for b4#19891).
- **best alternative:** the strongest well-sampled alternative class. Numbers are adjusted pp, P(better), then time-local pp ("loc").
- **evidence:** includes mechanism stats where they help. q500 = queen alive at r500; elim = eliminated; lr300 = length ratio at r300.
- **confidence:** how far the best alternative can be trusted against b4.

| map | b4 class (n, win%) | b4 srv | best alternative | evidence for/against | confidence | best class |
|---|---|---|---|---|---|---|
| Around UNSW | f1 k2 b3 l1 v1 b4 (87, 48%) | 2034 / 2045 | h1 +8.6, P .84, loc +10 | pb2 +7.9 (.79); cm1 (CRAUN) +5.8 (.72); v61 class -5.5. Server: cm1 2229 and h1 2179 vs b4 2034, but identical b3 spans 2037-2220. | low | b4 (no class at P≥.9) |
| Australia | u1 v1 b4 (68, 54%) | 2212 / 2211 | none credible (s1 +14.3, n=20, P .89) | v61 class -21.8 (both eras -15/-28); f1+k2 -22.2; cm1/b3/l1 (CRAUS, no QVA) -5.0. CROWD_MAPS Australia bit ≈ +17, QVAULT bit 2 ≈ +5 (n.s.). Mechanism: queen alive r100 49% (b4 class) vs 8% (v61) and 20% (cm1/b3/l1). | high (b4 > pre-b3) | **b4** |
| Autarky | f1 k2 cm1 b3 v1 b4 (100, 34%) | 2303 / 2314 | v61 class (b4 minus FUEL) +9.6, P .96, loc +8 | Every no-FUEL build is above b4 here (v55 +17, v64 +32, v65 +16, v69 +33; n 13-34); FUEL builds ≤0. But the 7 Oct v61 block is only +4.0, and elimination rates are equal (31% vs 30%). Server: v61 2240 vs b4 2303. | low | b4 (FUEL-off-on-Autarky is a lead, not proven) |
| Default | f1 k2 cm1 b3 l1 v1 b4 (121, 66%) | 2145 / 2220 | v61 class +1.4 (.62) | s1 +16.4 (n=17, .93): noise-sized. | medium (no difference) | b4 |
| Devil | f1 k2 cm1 b3 v1 b4 (115, 47%) | 2273 / 2292 | h1 +19.2, P .97, loc +17 (n=27) | pb2 +15.7 (.95, n=33); kf1 +6.0. v61 eras disagree (-8 / +8.5). Server: h1 2199, pb2 2287 vs b4 2273-2292 (disagrees). | low | b4 |
| Islands | f1 k2 cm1 b3 l1 b4 (105, 48%) | 2216 / 2197 | v61 class +2.9 (.70) | Eras +9.2 / -5.3. ms1 -31.9, s1 -23.6. | medium (no difference) | b4 |
| Maze | f1 cm1 b3 l1 v1 b4 (93, 38%) | 1990 / 1994 | **m1+m2+b1+q1 (park, no FUEL) +12.6, P .96, loc +14**, n=72, same opponent strength (E[win] .35 vs .37) | h1 +9.0 (.86); v61 (no park) -17.9 (both eras). Mechanism does not back it: queen alive r500 34% (19/56) vs b4 class 45% (30/66), lr300 0.80 vs 0.81. Server weakly agrees: the Maze offset jumped from -255 (m1) to -81 during m2's own games, then drifted down once FUEL arrived (f1 -174, k2 -225, cm1 -283, pb2 -197, b4 -230). Offsets are inherited along the upload chain, so this is one drifting estimate, not independent votes. | medium-low | b4 for now; **lead: QKILL_FUEL off on Maze** (the b1 class) |
| Portals | f1 cm1 b3 l1 v1 b4 (102, 73%) | 2273 / 2274 | s1 +8.8 (.84, n=25) | v61 -35.6 (both eras -33/-39), v55 -28.4: the park is confirmed. Queen alive r500 86% (63/73) vs v61 0% (0/72). pb2 0.0, kf1 +2.8, park-without-FUEL -3.9, k2 -7.1. | high | **b4** |
| Prisoners Dilemma | f1 k2 cm1 b3 l1 v1 b4 (114, 63%) | 2181 / 2257 | h1 +12.7 (.94) | ms1 +18.1 (.97, n=22) but ms1 is -11 pp map-mean; pb2 -18.5 (.01). Server: h1 2228 vs b4 2181-2257. | low | b4 |
| Queen Of Spades | f1 k2 cm1 b3 v1 b4 (122, 53%) | 2201 / 2200 | pb2 +6.1 (.78) | v61 class +0.3; ms1 -37. | medium (no difference) | b4 |
| Schooltime | f1 k2 cm1 b3 l1 b4 (121, 36%) | 2222 / 2208 | pb2 +17.0, P .98, loc +16 (n=41); v61 class (b4 minus FUEL) +10.6, P .97, loc +10, both eras positive (+13.6 / +7.2) | Queen alive r500 is 100% for every class, so games go to the length tiebreak. lr300: v61 class 1.07 and pb2 1.08 vs b4 class 0.60 (other FUEL builds 0.38-0.69). v55 +16.9, v64 +24 (n=13); v1 (SCH_DOORS) -6.3. Almost everything beats the b4 class, which points to the shared baseline. Server: v61 2228, v55 2179, pb2 2266 vs b4 2208-2222. | low-medium | b4 for now; leads: FUEL off, or QBOX_ONESPLIT on Schooltime |
| Slithery Fight | f1 k2 cm1 b3 l1 b4 (116, 27%) | 1886 / 1897 | v55 (no QSR, no FUEL) +15.2, P .96 (n=29, 3 Oct only) | v44 +10.7, v60 +9.1 (no QSR), but v64 (with QSR) +8.9 too. v61 class (QSR, no FUEL) -5.9 (both eras negative); pb2 -12.2; u1+v1 (QVAULT Slithery bit) +1.8. Mechanism flat: lr300 0.65-0.80 and q500 under 15% for all classes. Server: our worst map, b4 1886 (offset -334, about -20 on team rating). The inherited offset chain was -15..+87 up to 3 Oct (v61#16063 with QSR: -15; v64: +58), then fell from 4 Oct (v69 -115, v61#16388 -217) and stayed at -200..-360. That looks like a time effect (opponents got better here) more than a QSR effect. | low, **largest upside** | b4 for now; lead: QSPLIT_ROOM off on Slithery (weak) |
| Stripes | f1 k2 cm1 b3 l1 u1 v1 b4 (141, 67%) | 2285 / 2295 | **m1+m2 (STRIPES_LOOP, no FUEL) +17.0, P .99, loc +18**, n=52, same opponent strength (E[win] .68 vs .67) | v61+b1+q1 (no loop, no FUEL) -0.8, so the loop is worth about +18. Mechanism agrees: eliminated 15% vs 34%, queen alive r100 50% vs 6%. Server: m2 2214, m1 2173 vs b4 2285 (disagrees, but m1/m2 were 18-31% ranked). Placebo on Stripes was +14, which weakens it. | medium | b4 for now; **lead: STRIPES_LOOP on Stripes** (the best-supported lead) |
| Tower Defense | u1 v1 b4 (68, 63%) | 2311 / 2304 | pb2 +7.6 (.79), kf1 +6.6 (.81) | No-TDP classes: f1/k2/cm1/b3 -17.7 (.01; eliminated 39% vs 17%), v61 -22.4, q1 -26.5, l1 -33.9. TD_PULL confirmed. | high | **b4** |
| Trauma | f1 k2 cm1 b3 l1 u1 v1 b4 (135, 95%) | 2739 / 2775 | v55 +5.4 (n=23) | pb2 -10.0 (.01), kf1 -19.2, 7 Oct v61 block -7. | high | **b4** |
| Trophy | f1 k2 cm1 b3 l1 b4 (106, 51%) | 2151 / 2145 | m1+m2 (TROPHY_QSPLIT, no FUEL) +12.0, P .93, loc +14, n=47 | v61+b1+q1 -5.4, so qsplit ≈ +17 over its own base. Mechanism weak: eliminated 36% vs 42%. Server: m2 2160, m1 2168 vs b4 2151 (weakly agrees). | low-medium | b4 for now; lead: TROPHY_QSPLIT on Trophy |
| weakhold | f1 k2 cm1 b3 l1 u1 v1 b4 (106, 58%) | 2309 / 2343 | h1 +16.0 (.95), ms1 +15.1 (.94), pb2 +13.9 (.91) | Everything beats the b4 class, a shared-baseline artefact. Server: b4 2309-2343 (offset +90..+110), one of b4's best maps. | high that b4 is fine | **b4** |

**Map-mean effect vs b4** (mean of the 17 per-map pp; this is what moves the team rating):

| build | map-mean pp vs b4 | ±95% (approx.) |
|---|---|---|
| pb2 | +0.7 | 3.8 |
| m2 | +0.5 | 2.7 |
| m1 | +0.3 | 3.0 |
| v55 | +0.0 | 4.3 |
| v1 | -0.3 | 1.1 |
| cm1 | -1.0 | 1.6 |
| h1 | -1.2 | 3.9 |
| b3 | -1.3 | 1.1 |
| b1 | -1.6 | 2.6 |
| q1 | -1.7 | 2.9 |
| f1 | -2.3 | 1.2 |
| s1 | -2.8 | 4.7 |
| k2 | -3.0 | 1.8 |
| l1 | -3.2 | 2.1 |
| kf1 | -3.8 | 3.1 |
| v64 | -5.0 | 6.2 |
| v61 | -5.2 | 2.4 |
| v60 | -5.2 | 6.1 |
| v69 | -5.4 | 5.8 |
| v65 | -5.8 | 5.1 |
| v44 | -7.1 | 4.9 |
| c1 | -8.4 | 7.4 |
| ms1 | -11.0 | 4.4 |

Server overall (= mean map rating): pb2 2290 (the highest of any upload), v1 2254, b4#19891 2234, cm1 2232, f1 2221, b4#18751 2220, b3 2189-2221, m2 2210, v61 2184, kf1 2174.

What this says for a portfolio:
- **No all-map build clearly beats b4.** pb2 is +0.7 ± 3.8 on our model, with about 245 ranked games behind its 2290. Our adjusted Trauma -10 (P .01) and PD -18.5 (P .01) back STATUS's rejection of it, while Schooltime +17, Devil +16 and weakhold +14 favour it.
- **High-confidence keeps:** b4 on Portals, Tower Defense, Australia and Trauma. On weakhold, b4's server rating says it's fine.
- **Leads, in order of support** (rating gain ≈ per-map Elo gain / 17):
  1. STRIPES_LOOP on Stripes: +17 pp, P .99, time-local +18, mechanism agrees.
  2. QKILL_FUEL off on Maze: +12.6, P .96, server weakly agrees, mechanism doesn't.
  3. TROPHY_QSPLIT on Trophy: +12, P .93.
  4. QKILL_FUEL off on Schooltime: +10.6, P .97; both eras and lr300 agree, but there's a shared-baseline risk.
  5. QKILL_FUEL off on Autarky: +9.6, P .96, but only +4 in the 7 Oct era.
  6. QSPLIT_ROOM off on Slithery: weak evidence, but the worst map, so the largest upside.
- None of these leads clears the bar of 15 pp with both eras and the server agreeing. Each needs a server check (unranked, restricted to its map) before going into a ranked build. The five map-gated switches 1-5 can be combined in one portfolio build, because each changes play only on its own map.
- **Everything else: stay with b4.**

## 5. Per-map tables (all classes, including n < 15)

### Around UNSW

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| f1 12, k2 10, b3 46, l1 7, v1 5, b4 7 | = b4 | 87 | 42-45 | 48 | **baseline** |  |  | 0.47 | f1 2144 (8-4); k2 2142 (5-6); b3 2124 (6-12); l1 2141 (4-5); v1 2125 (4-1) | 47: 2/47 / 0 / 0.88 |
| v61 139, m1 1, m2 5, b1 2 | -FUEL | 147 | 67-80 | 46 | -5.5 (-16..+6) [λ.05: -7.5] | 0.17 | -6.6 (0.12) | 0.51 | v61 2116 (53-71); m2 2164 (5-0) | 48: 3/47 / 1 / 1.0 |
| kf1 78 | +KF | 78 | 20-58 | 26 | -11.3 (-22..+2) [λ.05: -13.2] | 0.05 | -14.7 (0.02) | 0.36 | kf1 2071 (19-53) | 12: 0/12 / 0 / 0.53 |
| q1 42 | +Q1PARK -FUEL | 42 | 16-26 | 38 | -6.3 (-21..+10) [λ.05: -8.4] | 0.23 | -1.8 (0.42) | 0.45 | q1 2072 (16-26) | 40: 6/40 / 0 / 0.95 |
| h1 40 | +H1 | 40 | 20-20 | 50 | +8.6 (-8..+25) [λ.05: +7.3] | 0.84 | +10.0 (0.88) | 0.41 | h1 2179 (21-20) | 10: 0/10 / 0 / 0.98 |
| pb2 30 | +PB | 30 | 19-11 | 63 | +7.9 (-11..+26) [λ.05: +6.5] | 0.79 | +3.7 (0.65) | 0.56 | pb2 2102 (20-11) | 9: 0/9 / 0 / 0.99 |
| cm1 27 | +CRAUN | 27 | 12-15 | 44 | +5.8 (-12..+25) [λ.05: +4.9] | 0.72 | +8.6 (0.81) | 0.39 | cm1 2229 (13-17) | 26: 0/26 / 0 / 0.87 |
| v55 26 | -FUEL -QSR | 26 | 13-13 | 50 | -2.4 (-20..+17) [λ.05: -5.1] | 0.41 | n/a (b4-class n=4) | 0.52 | v55 2038 (13-13) | 6: 0/6 / 0 / 1.09 |
| ms1 24 | +MID | 24 | 4-20 | 17 | -18.8 (-33..+3) [λ.05: -21.0] | 0.04 | -17.3 (0.06) | 0.35 | ms1 2025 (4-21) | 24: 1/24 / 0 / 0.86 |
| v44 23 | -FUEL -QS -QSR | 23 | 14-9 | 61 | -1.5 (-21..+19) [λ.05: -4.2] | 0.44 | n/a (b4-class n=0) | 0.62 | v44 2034 (14-9) | - |
| s1 18 | +SDEF | 18 | 3-15 | 17 | -20.0 (-35..+4) [λ.05: -22.4] | 0.05 | -17.9 (0.07) | 0.38 | s1 2062 (4-18) | 8: 0/8 / 0 / 0.86 |
| v60 10 | +QEXIT -FUEL -QSR | 10 | 5-5 | 50 | -5.3 (-29..+23) [λ.05: -8.5] | 0.36 | -9.9 (0.28) | 0.56 | v60 2018 (5-5) | 5: 1/5 / 0 / 1.06 |
| v64 7 | +L34 -FUEL | 7 | 3-4 | 43 | -17.0 (-38..+16) [λ.05: -21.9] | 0.15 | -21.4 (0.12) | 0.62 | v64 2048 (3-4) | 5: 0/5 / 0 / 1.21 |
| v65 7 | +QKBIG -FUEL | 7 | 1-6 | 14 | -37.4 (-46..-13) [λ.05: -42.8] | 0.00 | -43.7 (0.00) | 0.70 | v65 2015 (1-6) | 2: 0/2 / 0 / 1.11 |
| v69 7 | +QEP -FUEL | 7 | 4-3 | 57 | -7.0 (-32..+26) [λ.05: -10.6] | 0.34 | -11.5 (0.26) | 0.65 | v69 1984 (4-4) | 4: 0/4 / 0 / 1.25 |
| c1 4 | +C1 -FUEL | 4 | 2-2 | 50 | +2.0 (-30..+37) [λ.05: +0.5] | 0.54 | +4.4 (0.58) | 0.47 | - | 4: 0/4 / 0 / 0.84 |

### Australia

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| u1 5, v1 50, b4 13 | = b4 | 68 | 37-31 | 54 | **baseline** |  |  | 0.50 | u1 2150 (5-0); v1 2295 (27-25); b4 2212 (3-5) | 61: 2/60 / 0 / 1.28 |
| v61 151, m1 2, m2 7, b1 3 | -CRAUS -FUEL -QVA | 163 | 70-93 | 43 | -21.8 (-32..-10) [λ.05: -25.1] | 0.00 | -22.4 (0.00) | 0.65 | v61 2128 (60-82); m2 2095 (3-4) | 63: 1/63 / 0 / 1.95 |
| cm1 29, b3 55, l1 7 | -QVA | 91 | 47-44 | 52 | -5.0 (-18..+9) [λ.05: -7.7] | 0.24 | -5.6 (0.22) | 0.57 | cm1 2182 (17-16); b3 2203 (17-14); l1 2160 (4-5) | 83: 1/82 / 0 / 1.95 |
| kf1 77 | +KF | 77 | 18-59 | 23 | -24.5 (-34..-11) [λ.05: -28.2] | 0.00 | -29.9 (0.00) | 0.48 | kf1 2150 (17-54) | 7: 0/7 / 0 / 0.52 |
| q1 42 | +Q1PARK -CRAUS -FUEL -QVA | 42 | 19-23 | 45 | -15.1 (-30..+2) [λ.05: -18.8] | 0.04 | -15.7 (0.04) | 0.61 | q1 2246 (19-23) | 34: 1/34 / 0 / 1.27 |
| h1 34 | +H1 -CRAUS -QVA | 34 | 18-16 | 53 | -0.1 (-18..+18) [λ.05: -3.1] | 0.50 | -1.5 (0.44) | 0.53 | h1 2191 (19-16) | 10: 0/10 / 0 / 1.39 |
| v55 32 | -CRAUS -FUEL -QSR -QVA | 32 | 20-12 | 62 | -5.9 (-23..+13) [λ.05: -10.2] | 0.27 | n/a (b4-class n=0) | 0.68 | v55 2186 (20-12) | 4: 0/4 / 0 / 1.26 |
| pb2 28 | +PB | 28 | 17-11 | 61 | -7.2 (-25..+13) [λ.05: -10.5] | 0.24 | -10.4 (0.15) | 0.67 | pb2 2359 (18-11) | 9: 1/8 / 0 / 1.83 |
| f1 14, k2 13 | -CRAUS -QVA | 27 | 10-17 | 37 | -22.2 (-36..-3) [λ.05: -25.9] | 0.01 | -22.9 (0.01) | 0.61 | f1 2138 (7-7); k2 1956 (3-10) | 14: 0/13 / 1 / 1.21 |
| v44 23 | -CRAUS -FUEL -QS -QSR -QVA | 23 | 14-9 | 61 | -16.8 (-33..+4) [λ.05: -21.3] | 0.06 | n/a (b4-class n=0) | 0.76 | v44 2058 (14-9) | - |
| s1 20 | +SDEF -QVA | 20 | 13-7 | 65 | +14.3 (-8..+32) [λ.05: +12.2] | 0.89 | +14.1 (0.89) | 0.49 | s1 2291 (15-8) | 9: 0/9 / 0 / 2.62 |
| ms1 17 | +MID -QVA | 17 | 8-9 | 47 | -11.7 (-31..+12) [λ.05: -15.0] | 0.17 | -10.8 (0.19) | 0.59 | ms1 2199 (8-9) | 17: 1/16 / 0 / 2.45 |
| v65 16 | +QKBIG -CRAUS -FUEL -QVA | 16 | 8-8 | 50 | -16.6 (-35..+7) [λ.05: -21.5] | 0.08 | n/a (b4-class n=0) | 0.68 | v65 2155 (8-8) | 6: 0/6 / 0 / 1.52 |
| v69 14 | +QEP -CRAUS -FUEL -QVA | 14 | 5-9 | 36 | -28.0 (-42..-4) [λ.05: -33.3] | 0.01 | n/a (b4-class n=0) | 0.68 | v69 1988 (5-9) | 10: 1/10 / 0 / 1.17 |
| v60 13 | +QEXIT -CRAUS -FUEL -QSR -QVA | 13 | 6-7 | 46 | -19.8 (-37..+6) [λ.05: -25.1] | 0.06 | n/a (b4-class n=0) | 0.68 | v60 2143 (6-8) | 2: 0/2 / 0 / 1.52 |
| v64 9 | +L34 -CRAUS -FUEL -QVA | 9 | 5-4 | 56 | -11.4 (-35..+19) [λ.05: -16.8] | 0.23 | n/a (b4-class n=0) | 0.68 | v64 2143 (5-4) | 5: 0/5 / 0 / 0.89 |
| c1 4 | +C1 -CRAUS -FUEL -QVA | 4 | 1-3 | 25 | -21.2 (-43..+19) [λ.05: -28.4] | 0.15 | -22.4 (0.14) | 0.56 | - | 3: 1/3 / 0 / 1.59 |

### Autarky

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| f1 16, k2 16, cm1 10, b3 50, v1 2, b4 6 | = b4 | 100 | 34-66 | 34 | **baseline** |  |  | 0.36 | f1 2332 (10-6); k2 2101 (3-13); cm1 2285 (7-5); b3 2213 (2-16); b4 2303 (4-1) | 54: 2/26 / 16 / 0.68 |
| v61 135, m1 6, m2 2, b1 3, q1 15 | -FUEL | 161 | 77-84 | 48 | +9.6 (-1..+21) [λ.05: +9.6] | 0.96 | +8.4 (0.94) | 0.38 | v61 2240 (55-67); m1 2259 (2-4); q1 2187 (10-5) | 16: 4/5 / 5 / 0.64 |
| kf1 73 | +KF | 73 | 16-57 | 22 | -4.3 (-15..+9) [λ.05: -4.2] | 0.25 | -3.1 (0.31) | 0.26 | kf1 2259 (15-54) | 8: 0/2 / 5 / 0.18 |
| h1 36 | +H1 | 36 | 9-27 | 25 | -8.6 (-21..+9) [λ.05: -8.5] | 0.16 | -8.8 (0.15) | 0.33 | h1 2181 (9-28) | 13: 0/2 / 8 / 0.18 |
| v55 34 | -FUEL -QSR | 34 | 20-14 | 59 | +17.5 (-0..+35) [λ.05: +17.2] | 0.97 | -7.1 (0.28) | 0.40 | v55 2329 (20-14) | 9: 1/1 / 3 / 2.42 |
| l1 30 | +LANE | 30 | 5-25 | 17 | -10.4 (-23..+9) [λ.05: -10.0] | 0.13 | -8.2 (0.19) | 0.26 | l1 2231 (5-27) | 24: 0/5 / 16 / 0.32 |
| pb2 30 | +PB | 30 | 13-17 | 43 | -2.2 (-17..+16) [λ.05: -2.0] | 0.40 | -3.5 (0.34) | 0.46 | pb2 2331 (13-17) | 10: 3/7 / 2 / 0.97 |
| v44 23 | -FUEL -QS -QSR | 23 | 16-7 | 70 | +26.8 (+6..+44) [λ.05: +27.2] | 0.99 | n/a (b4-class n=0) | 0.41 | v44 2240 (16-12) | - |
| v65 22 | +QKBIG -FUEL | 22 | 13-9 | 59 | +16.5 (-4..+36) [λ.05: +16.3] | 0.94 | +13.2 (0.87) | 0.40 | v65 2264 (13-9) | 10: 1/3 / 0 / 3.73 |
| ms1 20 | +MID | 20 | 3-17 | 15 | -17.5 (-29..+4) [λ.05: -18.0] | 0.05 | -14.7 (0.08) | 0.33 | ms1 2070 (3-17) | 20: 0/3 / 14 / 0.51 |
| s1 18 | +SDEF | 18 | 4-14 | 22 | -0.6 (-18..+23) [λ.05: +0.3] | 0.48 | +0.6 (0.52) | 0.23 | s1 2315 (4-15) | 5: 0/1 / 4 / 0.47 |
| v60 17 | +QEXIT -FUEL -QSR | 17 | 7-10 | 41 | +5.5 (-14..+28) [λ.05: +5.2] | 0.69 | -10.8 (0.22) | 0.35 | v60 2223 (7-10) | 7: 2/4 / 1 / 1.27 |
| v69 15 | +QEP -FUEL | 15 | 11-4 | 73 | +33.1 (+8..+51) [λ.05: +34.5] | 1.00 | +31.4 (0.99) | 0.34 | v69 2349 (11-4) | 11: 2/4 / 1 / 3.42 |
| v64 13 | +L34 -FUEL | 13 | 10-3 | 77 | +32.5 (+6..+52) [λ.05: +34.4] | 0.99 | +26.6 (0.97) | 0.40 | v64 2252 (10-3) | 7: 1/2 / 0 / 9.09 |
| c1 6 | +C1 -FUEL | 6 | 2-4 | 33 | -5.4 (-27..+29) [λ.05: -6.3] | 0.37 | -6.8 (0.34) | 0.41 | c1 2228 (2-4) | 6: 5/5 / 1 / 1.06 |

### Default

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| f1 11, k2 14, cm1 8, b3 56, l1 13, v1 4, b4 15 | = b4 | 121 | 80-41 | 66 | **baseline** |  |  | 0.66 | f1 2332 (8-3); k2 2395 (10-4); cm1 2351 (5-3); b3 2196 (13-6); l1 2405 (11-3); b4 2145 (5-4) | 59: 0/20 / 14 / 1.75 |
| v61 178, m1 3, m2 8, b1 5, q1 20 | -FUEL | 214 | 156-58 | 73 | +1.4 (-8..+10) [λ.05: +0.8] | 0.62 | +1.9 (0.66) | 0.72 | v61 2315 (118-44); m2 2295 (5-3); b1 2313 (3-2); q1 2334 (13-7) | 20: 0/5 / 1 / 6.44 |
| kf1 82 | +KF | 82 | 51-31 | 62 | +4.2 (-9..+15) [λ.05: +3.8] | 0.74 | +1.0 (0.56) | 0.58 | kf1 2155 (46-30) | 13: 0/3 / 6 / 0.63 |
| pb2 43 | +PB | 43 | 29-14 | 67 | -7.5 (-24..+8) [λ.05: -8.0] | 0.18 | -8.9 (0.13) | 0.74 | pb2 2280 (31-14) | 10: 0/3 / 4 / 1.35 |
| h1 40 | +H1 | 40 | 22-18 | 55 | -6.7 (-23..+8) [λ.05: -7.0] | 0.20 | -6.3 (0.22) | 0.62 | h1 2287 (22-18) | 9: 0/5 / 4 / 0.81 |
| v55 33 | -FUEL -QSR | 33 | 27-6 | 82 | +7.5 (-12..+21) [λ.05: +6.6] | 0.79 | n/a (b4-class n=5) | 0.75 | v55 2275 (27-6) | 6: 0/2 / 0 / 26.87 |
| v44 23 | -FUEL -QS -QSR | 23 | 18-5 | 78 | -2.3 (-25..+16) [λ.05: -3.6] | 0.42 | n/a (b4-class n=0) | 0.80 | v44 2159 (19-5) | - |
| ms1 18 | +MID | 18 | 8-10 | 44 | -14.2 (-35..+7) [λ.05: -14.7] | 0.10 | -10.2 (0.18) | 0.60 | ms1 2203 (8-10) | 18: 0/5 / 7 / 0.79 |
| s1 17 | +SDEF | 17 | 14-3 | 82 | +16.4 (-6..+28) [λ.05: +17.7] | 0.93 | +18.5 (0.96) | 0.64 | s1 2397 (14-3) | 6: 0/2 / 0 / 4.67 |
| v64 15 | +L34 -FUEL | 15 | 9-6 | 60 | -13.6 (-36..+9) [λ.05: -15.8] | 0.13 | -14.5 (0.14) | 0.74 | v64 2185 (9-7) | 7: 0/2 / 2 / 2.66 |
| v65 15 | +QKBIG -FUEL | 15 | 11-4 | 73 | -3.0 (-28..+17) [λ.05: -4.6] | 0.40 | -0.8 (0.47) | 0.76 | v65 2234 (14-4) | 9: 2/4 / 1 / 4.37 |
| v60 11 | +QEXIT -FUEL -QSR | 11 | 6-5 | 55 | -14.2 (-39..+11) [λ.05: -16.8] | 0.15 | -14.1 (0.18) | 0.70 | v60 2194 (6-5) | 5: 1/3 / 2 / 19.46 |
| v69 9 | +QEP -FUEL | 9 | 8-1 | 89 | +14.7 (-20..+30) [λ.05: +16.3] | 0.82 | +13.1 (0.82) | 0.74 | v69 2283 (8-1) | 4: 0/3 / 0 / 3.17 |
| c1 6 | +C1 -FUEL | 6 | 6-0 | 100 | +25.1 (-14..+33) [λ.05: +31.0] | 0.92 | +24.0 (0.93) | 0.69 | c1 2300 (6-0) | 6: 0/1 / 0 / 11.39 |

### Devil

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| f1 14, k2 17, cm1 11, b3 55, v1 3, b4 15 | = b4 | 115 | 54-61 | 47 | **baseline** |  |  | 0.47 | f1 2245 (8-6); k2 2295 (11-6); cm1 2109 (6-8); b3 2035 (6-17); b4 2273 (8-1) | 69: 0/6 / 35 / 19.18 |
| v61 160, m1 3, m2 8, b1 2, q1 15 | -FUEL | 188 | 101-87 | 54 | -0.2 (-10..+10) [λ.05: -1.1] | 0.49 | +0.6 (0.54) | 0.54 | v61 2182 (77-60); m2 2186 (5-3); q1 2159 (6-9) | 13: 0/2 / 5 / 43.58 |
| kf1 80 | +KF | 80 | 36-44 | 45 | +6.0 (-7..+19) [λ.05: +5.4] | 0.81 | +3.4 (0.69) | 0.39 | kf1 2239 (36-39) | 15: 0/1 / 8 / 46.63 |
| l1 36 | +LANE | 36 | 13-23 | 36 | -1.7 (-17..+15) [λ.05: -1.7] | 0.42 | -1.0 (0.45) | 0.38 | l1 2120 (14-24) | 27: 0/1 / 18 / 19.31 |
| v55 35 | -FUEL -QSR | 35 | 16-19 | 46 | -8.3 (-23..+9) [λ.05: -10.0] | 0.17 | -9.3 (0.23) | 0.55 | v55 1989 (16-19) | 7: 0/3 / 1 / 23.72 |
| pb2 33 | +PB | 33 | 23-10 | 70 | +15.7 (-3..+31) [λ.05: +15.7] | 0.95 | +12.6 (0.91) | 0.54 | pb2 2287 (24-10) | 6: 0/2 / 2 / 74.2 |
| h1 27 | +H1 | 27 | 17-10 | 63 | +19.2 (-0..+35) [λ.05: +19.5] | 0.97 | +17.2 (0.96) | 0.44 | h1 2199 (18-10) | 7: 0/1 / 1 / 0.85 |
| v65 23 | +QKBIG -FUEL | 23 | 11-12 | 48 | -7.2 (-24..+13) [λ.05: -8.9] | 0.24 | -8.6 (0.22) | 0.56 | v65 2030 (11-15) | 10: 0/4 / 2 / 39.2 |
| v44 21 | -FUEL -QS -QSR | 21 | 12-9 | 57 | -6.1 (-24..+15) [λ.05: -7.9] | 0.29 | n/a (b4-class n=0) | 0.63 | v44 1990 (18-12) | - |
| s1 20 | +SDEF | 20 | 8-12 | 40 | +2.7 (-16..+23) [λ.05: +2.8] | 0.60 | +3.4 (0.63) | 0.37 | s1 2098 (8-14) | 10: 0/2 / 5 / 67.93 |
| ms1 18 | +MID | 18 | 4-14 | 22 | -13.6 (-30..+10) [λ.05: -14.3] | 0.12 | -13.4 (0.13) | 0.36 | ms1 1981 (4-14) | 18: 0/3 / 11 / 9.35 |
| v69 16 | +QEP -FUEL | 16 | 10-6 | 62 | +0.1 (-21..+23) [λ.05: -1.3] | 0.50 | -1.5 (0.45) | 0.62 | v69 2067 (10-6) | 9: 0/2 / 3 / 3.85 |
| v60 11 | +QEXIT -FUEL -QSR | 11 | 7-4 | 64 | +0.7 (-24..+27) [λ.05: -0.9] | 0.52 | -0.1 (0.50) | 0.63 | v60 1969 (7-4) | 4: 0/1 / 1 / 4.67 |
| v64 6 | +L34 -FUEL | 6 | 2-4 | 33 | -22.8 (-41..+12) [λ.05: -27.3] | 0.09 | -27.8 (0.07) | 0.61 | v64 1939 (2-5) | 1: 0/0 / 0 / 61.5 |
| c1 6 | +C1 -FUEL | 6 | 3-3 | 50 | +0.6 (-28..+32) [λ.05: -0.1] | 0.51 | +0.6 (0.51) | 0.49 | c1 2100 (3-3) | 6: 1/2 / 2 / 66.11 |

### Islands

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| f1 13, k2 14, cm1 8, b3 49, l1 12, b4 9 | = b4 | 105 | 50-55 | 48 | **baseline** |  |  | 0.47 | f1 2353 (6-7); k2 2179 (5-9); cm1 2408 (5-5); b3 2317 (11-6); l1 2355 (6-7); b4 2216 (1-6) | 42: 1/40 / 0 / 0.85 |
| v61 143, m1 2, m2 5, b1 5, q1 22 | -FUEL | 177 | 102-75 | 58 | +2.9 (-8..+13) [λ.05: +1.6] | 0.70 | +2.7 (0.70) | 0.55 | v61 2243 (67-57); m2 2309 (2-3); b1 2379 (3-2); q1 2348 (14-8) | 11: 0/10 / 0 / 2.58 |
| kf1 79 | +KF | 79 | 26-53 | 33 | -5.9 (-18..+8) [λ.05: -7.1] | 0.19 | -10.0 (0.07) | 0.39 | kf1 2174 (25-47) | 10: 0/10 / 0 / 0.81 |
| h1 38 | +H1 | 38 | 13-25 | 34 | -13.1 (-27..+4) [λ.05: -14.3] | 0.06 | -12.5 (0.07) | 0.47 | h1 2263 (14-25) | 16: 0/16 / 0 / 0.81 |
| pb2 31 | +PB | 31 | 18-13 | 58 | +3.0 (-15..+21) [λ.05: +2.2] | 0.63 | +0.5 (0.52) | 0.55 | pb2 2349 (18-14) | 4: 0/3 / 0 / 2.5 |
| ms1 24 | +MID | 24 | 3-21 | 12 | -31.9 (-41..-13) [λ.05: -34.1] | 0.00 | -29.2 (0.00) | 0.45 | ms1 2118 (3-21) | 24: 0/23 / 0 / 0.97 |
| v44 23 | -FUEL -QS -QSR | 23 | 13-10 | 57 | -5.1 (-23..+16) [λ.05: -7.3] | 0.31 | n/a (b4-class n=0) | 0.62 | v44 2115 (14-10) | - |
| v55 21 | -FUEL -QSR | 21 | 13-8 | 62 | +3.6 (-17..+24) [λ.05: +1.8] | 0.63 | n/a (b4-class n=2) | 0.58 | v55 2172 (13-8) | 3: 0/3 / 0 / 2.4 |
| s1 17 | +SDEF | 17 | 2-15 | 12 | -23.6 (-38..+2) [λ.05: -25.8] | 0.03 | -22.8 (0.04) | 0.35 | s1 2234 (3-18) | 10: 0/10 / 0 / 0.74 |
| v64 10 | +L34 -FUEL | 10 | 4-6 | 40 | -13.1 (-34..+16) [λ.05: -16.0] | 0.18 | -7.8 (0.31) | 0.55 | v64 2195 (4-6) | 3: 0/3 / 0 / 2.93 |
| v65 9 | +QKBIG -FUEL | 9 | 7-2 | 78 | +17.9 (-14..+41) [λ.05: +18.3] | 0.86 | +24.9 (0.93) | 0.59 | v65 2292 (7-2) | 2: 0/2 / 0 / 2.73 |
| v69 9 | +QEP -FUEL | 9 | 7-2 | 78 | +20.6 (-11..+42) [λ.05: +21.3] | 0.90 | +24.8 (0.94) | 0.56 | v69 2307 (7-2) | 2: 0/2 / 0 / 1.76 |
| v60 8 | +QEXIT -FUEL -QSR | 8 | 5-3 | 62 | +6.2 (-23..+34) [λ.05: +5.1] | 0.65 | +5.6 (0.62) | 0.56 | v60 2135 (5-3) | 2: 0/2 / 0 / 0.54 |
| c1 4 | +C1 -FUEL | 4 | 1-3 | 25 | -10.8 (-38..+29) [λ.05: -14.4] | 0.30 | -12.5 (0.27) | 0.39 | - | 4: 0/4 / 0 / 1.16 |

### Maze

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| f1 18, cm1 9, b3 42, l1 8, v1 1, b4 15 | = b4 | 93 | 35-58 | 38 | **baseline** |  |  | 0.37 | f1 2047 (11-7); cm1 1949 (0-11); b3 1805 (2-14); l1 1966 (4-5); b4 1990 (3-5) | 68: 30/66 / 0 / 0.81 |
| v61 151 | -FUEL -PARK_M | 151 | 39-112 | 26 | -17.9 (-25..-8) [λ.05: -19.5] | 0.00 | -18.3 (0.00) | 0.44 | v61 1889 (33-102) | 60: 5/59 / 0 / 0.72 |
| pb2 95 | +PB | 95 | 28-67 | 29 | +0.2 (-10..+13) [λ.05: -0.8] | 0.51 | -1.7 (0.39) | 0.29 | pb2 2093 (28-68) | 61: 16/59 / 1 / 0.79 |
| kf1 74 | +KF | 74 | 23-51 | 31 | +3.5 (-9..+18) [λ.05: +2.2] | 0.70 | +2.6 (0.65) | 0.28 | kf1 1975 (23-44) | 14: 5/14 / 0 / 0.64 |
| m1 15, m2 41, b1 4, q1 12 | -FUEL | 72 | 35-37 | 49 | +12.6 (-1..+27) [λ.05: +11.3] | 0.96 | +13.5 (0.97) | 0.35 | m1 1943 (5-13); m2 2129 (19-22); q1 2103 (11-1) | 59: 19/56 / 1 / 0.8 |
| k2 45 | +QKEG | 45 | 10-35 | 22 | -4.5 (-17..+12) [λ.05: -5.2] | 0.28 | -4.1 (0.30) | 0.26 | k2 1936 (10-36) | 37: 14/36 / 0 / 0.75 |
| h1 39 | +H1 | 39 | 17-22 | 44 | +9.0 (-7..+26) [λ.05: +8.2] | 0.86 | +8.1 (0.83) | 0.35 | h1 2061 (18-22) | 18: 7/18 / 0 / 0.83 |
| v55 27 | -FUEL -PARK_M -QSR | 27 | 10-17 | 37 | -7.8 (-22..+11) [λ.05: -10.2] | 0.20 | -9.6 (0.22) | 0.46 | v55 1916 (10-17) | 2: 0/2 / 0 / 0.76 |
| v44 22 | -FUEL -PARK_M -QS -QSR | 22 | 7-15 | 32 | -18.1 (-30..+1) [λ.05: -20.9] | 0.03 | n/a (b4-class n=0) | 0.52 | v44 1827 (8-15) | - |
| ms1 22 | +MID | 22 | 6-16 | 27 | -4.0 (-20..+18) [λ.05: -5.0] | 0.35 | -3.0 (0.39) | 0.31 | ms1 1942 (6-16) | 22: 4/22 / 0 / 0.81 |
| s1 15 | +SDEF | 15 | 6-9 | 40 | +11.9 (-9..+35) [λ.05: +11.9] | 0.85 | +12.1 (0.85) | 0.27 | s1 1978 (6-11) | 9: 3/9 / 0 / 0.65 |
| v65 13 | +QKBIG -FUEL -PARK_M | 13 | 5-8 | 38 | -3.9 (-23..+21) [λ.05: -6.3] | 0.37 | -1.0 (0.47) | 0.43 | v65 1958 (5-8) | 4: 0/4 / 0 / 0.58 |
| v69 10 | +QEP -FUEL -PARK_M | 10 | 4-6 | 40 | -3.8 (-24..+25) [λ.05: -6.3] | 0.39 | -1.5 (0.46) | 0.44 | v69 1945 (6-6) | 4: 0/4 / 0 / 0.47 |
| v60 7 | +QEXIT -FUEL -PARK_M -QSR | 7 | 1-6 | 14 | -22.2 (-35..+11) [λ.05: -27.5] | 0.08 | -33.1 (0.04) | 0.41 | v60 1838 (1-6) | 2: 0/2 / 0 / 0.52 |
| v64 5 | +L34 -FUEL -PARK_M | 5 | 2-3 | 40 | -11.1 (-31..+26) [λ.05: -15.3] | 0.26 | -19.7 (0.17) | 0.54 | v64 1884 (3-3) | 1: 0/1 / 0 / 0.31 |
| c1 5 | +C1 -FUEL -PARK_M | 5 | 2-3 | 40 | -0.2 (-26..+35) [λ.05: -1.8] | 0.49 | -2.9 (0.43) | 0.40 | c1 1950 (2-3) | 4: 0/4 / 0 / 0.96 |
| u1 4 | +QGR | 4 | 0-4 | 0 | -19.0 (-35..+32) [λ.05: -29.3] | 0.20 | -18.5 (0.22) | 0.21 | u1 1854 (1-5) | 4: 1/4 / 0 / 0.7 |

### Portals

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| f1 13, cm1 13, b3 47, l1 10, v1 4, b4 15 | = b4 | 102 | 74-28 | 73 | **baseline** |  |  | 0.68 | f1 2243 (13-0); cm1 2240 (11-5); b3 2375 (14-4); l1 2204 (7-4); v1 2424 (4-2); b4 2273 (5-2) | 73: 63/73 / 0 / 1.01 |
| v61 161 | -FUEL -PARK_P | 161 | 60-101 | 37 | -35.6 (-45..-25) [λ.05: -38.8] | 0.00 | -36.7 (0.00) | 0.72 | v61 1948 (53-92) | 72: 0/72 / 0 / 1.12 |
| pb2 104 | +PB | 104 | 66-38 | 63 | +0.0 (-12..+11) [λ.05: -2.8] | 0.50 | -3.4 (0.29) | 0.63 | pb2 2358 (68-39) | 62: 50/62 / 0 / 0.94 |
| kf1 76 | +KF | 76 | 46-30 | 61 | +2.8 (-11..+14) [λ.05: -0.3] | 0.66 | -1.1 (0.43) | 0.58 | kf1 2190 (45-26) | 6: 6/6 / 0 / 0.96 |
| m1 10, m2 36, b1 6, q1 22 | -FUEL | 74 | 49-25 | 66 | -3.9 (-18..+8) [λ.05: -7.0] | 0.28 | -5.5 (0.20) | 0.70 | m1 1998 (10-3); m2 1992 (18-18); b1 2197 (5-1); q1 2261 (19-3) | 52: 44/52 / 0 / 0.96 |
| h1 39 | +H1 | 39 | 26-13 | 67 | +1.2 (-16..+15) [λ.05: -1.5] | 0.56 | -2.5 (0.38) | 0.65 | h1 2293 (27-13) | 11: 8/11 / 0 / 0.92 |
| v55 38 | -FUEL -PARK_P -QSR | 38 | 17-21 | 45 | -28.4 (-43..-11) [λ.05: -32.8] | 0.00 | n/a (b4-class n=3) | 0.74 | v55 1886 (17-21) | 7: 0/7 / 0 / 1.0 |
| k2 37 | +QKEG | 37 | 19-18 | 51 | -7.1 (-24..+8) [λ.05: -9.6] | 0.19 | -7.8 (0.17) | 0.60 | k2 2181 (20-18) | 31: 25/31 / 0 / 0.9 |
| v44 28 | -FUEL -PARK_P -QS -QSR | 28 | 10-18 | 36 | -42.2 (-55..-24) [λ.05: -47.0] | 0.00 | n/a (b4-class n=0) | 0.79 | v44 2003 (18-13) | - |
| s1 25 | +SDEF | 25 | 18-7 | 72 | +8.8 (-10..+21) [λ.05: +6.7] | 0.84 | +5.6 (0.74) | 0.61 | s1 2328 (18-8) | 10: 10/10 / 0 / 0.85 |
| v60 18 | +QEXIT -FUEL -PARK_P -QSR | 18 | 8-10 | 44 | -23.7 (-43..-2) [λ.05: -28.6] | 0.02 | -19.5 (0.08) | 0.71 | v60 1844 (8-10) | 6: 0/6 / 0 / 0.88 |
| ms1 18 | +MID | 18 | 12-6 | 67 | +1.8 (-20..+18) [λ.05: -0.4] | 0.57 | -0.1 (0.50) | 0.65 | ms1 2365 (12-6) | 18: 15/18 / 0 / 0.92 |
| v65 17 | +QKBIG -FUEL -PARK_P | 17 | 6-11 | 35 | -35.5 (-52..-13) [λ.05: -40.8] | 0.00 | -31.6 (0.01) | 0.75 | v65 2043 (6-11) | 3: 0/3 / 0 / 1.06 |
| v64 13 | +L34 -FUEL -PARK_P | 13 | 5-8 | 38 | -33.6 (-52..-9) [λ.05: -39.2] | 0.00 | -30.8 (0.02) | 0.77 | v64 1956 (5-8) | 6: 0/6 / 0 / 1.09 |
| v69 11 | +QEP -FUEL -PARK_P | 11 | 4-7 | 36 | -39.0 (-57..-13) [λ.05: -45.2] | 0.00 | -34.3 (0.01) | 0.80 | v69 1917 (4-7) | 3: 0/3 / 0 / 1.1 |
| c1 4 | +C1 -FUEL -PARK_P | 4 | 0-4 | 0 | -49.7 (-65..-8) [λ.05: -64.2] | 0.01 | -51.3 (0.01) | 0.71 | - | 4: 0/4 / 0 / 0.99 |

### Prisoners Dilemma

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| f1 19, k2 17, cm1 6, b3 46, l1 8, v1 6, b4 12 | = b4 | 114 | 72-42 | 63 | **baseline** |  |  | 0.62 | f1 2221 (12-7); k2 2218 (14-3); cm1 2185 (7-2); b3 2165 (13-4); l1 2086 (4-5); v1 2202 (4-2); b4 2181 (2-4) | 48: 5/14 / 13 / 13.51 |
| v61 161, m1 1, m2 4, b1 7, q1 16 | -FUEL | 189 | 122-67 | 65 | +0.2 (-10..+10) [λ.05: -0.9] | 0.52 | -0.2 (0.49) | 0.64 | v61 2175 (95-50); b1 2312 (7-0); q1 2229 (8-8) | 19: 1/4 / 3 / 9.32 |
| kf1 79 | +KF | 79 | 47-32 | 59 | +6.5 (-7..+18) [λ.05: +5.6] | 0.83 | +1.0 (0.56) | 0.53 | kf1 2092 (45-31) | 11: 1/1 / 5 / 0.74 |
| pb2 43 | +PB | 43 | 22-21 | 51 | -18.5 (-33..-2) [λ.05: -19.7] | 0.01 | -21.0 (0.00) | 0.70 | pb2 2257 (22-21) | 13: 3/7 / 3 / 15.89 |
| h1 39 | +H1 | 39 | 28-11 | 72 | +12.7 (-4..+25) [λ.05: +12.5] | 0.94 | +10.6 (0.91) | 0.59 | h1 2228 (28-12) | 9: 1/1 / 3 / 23.0 |
| v55 25 | -FUEL -QSR | 25 | 14-11 | 56 | -12.4 (-31..+7) [λ.05: -14.6] | 0.11 | n/a (b4-class n=6) | 0.69 | v55 2034 (14-11) | 8: 2/2 / 1 / 3.56 |
| v44 23 | -FUEL -QS -QSR | 23 | 14-9 | 61 | -10.8 (-30..+9) [λ.05: -12.9] | 0.15 | n/a (b4-class n=0) | 0.72 | v44 2068 (22-13) | - |
| s1 22 | +SDEF | 22 | 10-12 | 45 | -7.1 (-26..+12) [λ.05: -7.5] | 0.24 | -6.1 (0.28) | 0.53 | s1 2142 (10-12) | 13: 0/2 / 5 / 18.31 |
| ms1 22 | +MID | 22 | 17-5 | 77 | +18.1 (-1..+30) [λ.05: +18.6] | 0.97 | +18.5 (0.97) | 0.56 | ms1 2163 (17-5) | 22: 2/3 / 4 / 15.02 |
| v65 17 | +QKBIG -FUEL | 17 | 12-5 | 71 | +1.5 (-22..+20) [λ.05: -0.1] | 0.55 | -0.7 (0.47) | 0.69 | v65 2195 (12-5) | 5: 1/1 / 1 / 16.0 |
| v60 11 | +QEXIT -FUEL -QSR | 11 | 9-2 | 82 | +12.8 (-17..+30) [λ.05: +12.8] | 0.81 | +18.7 (0.90) | 0.69 | v60 2038 (9-2) | 5: 0/2 / 0 / 24.87 |
| v69 11 | +QEP -FUEL | 11 | 7-4 | 64 | -6.1 (-33..+18) [λ.05: -8.3] | 0.33 | -5.6 (0.35) | 0.70 | v69 2073 (7-4) | 6: 2/3 / 2 / 2.9 |
| v64 5 | +L34 -FUEL | 5 | 3-2 | 60 | -12.2 (-45..+22) [λ.05: -16.5] | 0.27 | -12.8 (0.27) | 0.73 | v64 2126 (3-2) | 3: 0/0 / 1 / 1.78 |
| c1 5 | +C1 -FUEL | 5 | 1-4 | 20 | -32.3 (-54..+5) [λ.05: -38.6] | 0.04 | -34.6 (0.04) | 0.64 | c1 2114 (1-4) | 4: 3/3 / 1 / 1.1 |

### Queen Of Spades

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| f1 14, k2 16, cm1 10, b3 63, v1 9, b4 10 | = b4 | 122 | 65-57 | 53 | **baseline** |  |  | 0.53 | f1 2173 (7-7); k2 2157 (12-4); cm1 2248 (7-5); b3 2151 (13-10); v1 2257 (7-2); b4 2201 (3-5) | 71: 0/5 / 35 / 2.35 |
| v61 167, m1 6, m2 4, b1 5, q1 16 | -FUEL | 198 | 116-82 | 59 | +0.3 (-10..+10) [λ.05: -0.8] | 0.53 | -0.0 (0.50) | 0.58 | v61 2197 (89-66); m1 2217 (3-3); b1 2157 (0-5); q1 2121 (11-6) | 16: 0/0 / 7 / 0.99 |
| kf1 86 | +KF | 86 | 34-52 | 40 | -4.6 (-17..+9) [λ.05: -5.6] | 0.25 | -8.8 (0.09) | 0.44 | kf1 2177 (32-48) | 16: 0/2 / 11 / 1.21 |
| pb2 48 | +PB | 48 | 31-17 | 65 | +6.1 (-10..+20) [λ.05: +5.5] | 0.78 | +3.8 (0.69) | 0.59 | pb2 2307 (32-17) | 12: 0/1 / 3 / 4.87 |
| h1 40 | +H1 | 40 | 19-21 | 48 | -7.5 (-23..+9) [λ.05: -8.3] | 0.19 | -7.5 (0.19) | 0.54 | h1 2113 (19-21) | 17: 0/4 / 5 / 4.85 |
| l1 34 | +LANE | 34 | 14-20 | 41 | -2.7 (-19..+14) [λ.05: -2.9] | 0.38 | -0.4 (0.48) | 0.44 | l1 2250 (15-21) | 30: 0/2 / 18 / 0.47 |
| v55 30 | -FUEL -QSR | 30 | 22-8 | 73 | +8.3 (-12..+25) [λ.05: +6.8] | 0.79 | n/a (b4-class n=2) | 0.66 | v55 2105 (22-8) | 12: 1/1 / 2 / 4.22 |
| v44 29 | -FUEL -QS -QSR | 29 | 20-9 | 69 | -0.5 (-20..+18) [λ.05: -2.4] | 0.48 | n/a (b4-class n=0) | 0.69 | v44 2032 (22-9) | - |
| s1 24 | +SDEF | 24 | 8-16 | 33 | -10.4 (-28..+10) [λ.05: -10.9] | 0.15 | -9.1 (0.19) | 0.45 | s1 2207 (8-17) | 10: 0/3 / 5 / 0.24 |
| ms1 19 | +MID | 19 | 1-18 | 5 | -37.1 (-47..-12) [λ.05: -40.5] | 0.00 | -35.8 (0.01) | 0.42 | ms1 2007 (1-18) | 19: 0/3 / 15 / 0.16 |
| v60 13 | +QEXIT -FUEL -QSR | 13 | 8-5 | 62 | +2.9 (-22..+26) [λ.05: +1.3] | 0.58 | +8.5 (0.71) | 0.58 | v60 2046 (8-5) | 4: 1/1 / 2 / 0.89 |
| v65 13 | +QKBIG -FUEL | 13 | 9-4 | 69 | +9.1 (-17..+30) [λ.05: +8.1] | 0.75 | +8.1 (0.73) | 0.59 | v65 2114 (9-4) | 6: 0/0 / 3 / 7.78 |
| v64 12 | +L34 -FUEL | 12 | 6-6 | 50 | -9.8 (-32..+16) [λ.05: -12.3] | 0.24 | -12.4 (0.20) | 0.61 | v64 2134 (6-6) | 7: 0/2 / 3 / 0.54 |
| v69 9 | +QEP -FUEL | 9 | 8-1 | 89 | +19.6 (-17..+40) [λ.05: +21.6] | 0.86 | +18.9 (0.87) | 0.72 | v69 2198 (8-1) | 2: 0/0 / 0 / 12.78 |
| c1 5 | +C1 -FUEL | 5 | 2-3 | 40 | -4.9 (-35..+28) [λ.05: -6.6] | 0.40 | -3.6 (0.42) | 0.47 | c1 2164 (2-3) | 4: 0/1 / 2 / 2.57 |

### Schooltime

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| f1 12, k2 13, cm1 13, b3 58, l1 10, b4 15 | = b4 | 121 | 44-77 | 36 | **baseline** |  |  | 0.38 | f1 2156 (5-7); k2 1996 (4-9); cm1 2240 (7-8); b3 2177 (15-19); l1 2145 (4-7); b4 2222 (4-4) | 73: 73/73 / 0 / 0.6 |
| v61 140, m2 5, b1 2, q1 15 | -FUEL | 162 | 89-73 | 55 | +10.6 (-0..+21) [λ.05: +10.4] | 0.97 | +10.3 (0.97) | 0.44 | v61 2228 (75-55); m2 2170 (1-4); q1 2117 (7-8) | 54: 54/54 / 0 / 1.07 |
| kf1 79 | +KF | 79 | 26-53 | 33 | +1.0 (-11..+14) [λ.05: +1.0] | 0.56 | -1.7 (0.39) | 0.32 | kf1 2086 (24-49) | 12: 12/12 / 0 / 0.38 |
| v1 47 | +SCHD | 47 | 10-37 | 21 | -6.3 (-18..+10) [λ.05: -5.7] | 0.20 | -5.6 (0.24) | 0.27 | v1 2241 (11-38) | 47: 47/47 / 0 / 0.53 |
| pb2 41 | +PB | 41 | 27-14 | 66 | +17.0 (+0..+33) [λ.05: +17.5] | 0.98 | +16.2 (0.97) | 0.49 | pb2 2266 (27-14) | 10: 10/10 / 0 / 1.08 |
| h1 30 | +H1 | 30 | 10-20 | 33 | +0.7 (-15..+20) [λ.05: +1.0] | 0.53 | +0.4 (0.52) | 0.33 | h1 2222 (10-20) | 16: 16/16 / 0 / 0.69 |
| v55 27 | -FUEL -QSR | 27 | 17-10 | 63 | +16.9 (-2..+35) [λ.05: +16.6] | 0.96 | n/a (b4-class n=7) | 0.44 | v55 2179 (17-10) | 4: 4/4 / 0 / 1.22 |
| ms1 25 | +MID | 25 | 7-18 | 28 | -3.6 (-19..+17) [λ.05: -3.1] | 0.35 | -2.4 (0.40) | 0.32 | ms1 2146 (7-18) | 25: 25/25 / 0 / 0.68 |
| v44 17 | -FUEL -QS -QSR | 17 | 9-8 | 53 | +3.0 (-17..+26) [λ.05: +2.3] | 0.60 | n/a (b4-class n=0) | 0.50 | v44 2166 (11-7) | - |
| v65 16 | +QKBIG -FUEL | 16 | 6-10 | 38 | -5.1 (-22..+18) [λ.05: -6.1] | 0.32 | -3.5 (0.39) | 0.43 | v65 2083 (6-10) | 4: 4/4 / 0 / 1.03 |
| s1 16 | +SDEF | 16 | 6-10 | 38 | +5.5 (-14..+29) [λ.05: +6.6] | 0.68 | +7.4 (0.74) | 0.32 | s1 2259 (8-11) | 11: 11/11 / 0 / 0.61 |
| v60 15 | +QEXIT -FUEL -QSR | 15 | 6-9 | 40 | -1.2 (-20..+23) [λ.05: -2.0] | 0.46 | -3.2 (0.42) | 0.41 | v60 2092 (6-10) | 12: 12/12 / 0 / 0.47 |
| v64 13 | +L34 -FUEL | 13 | 9-4 | 69 | +24.3 (-1..+45) [λ.05: +25.1] | 0.97 | +26.2 (0.96) | 0.41 | v64 2166 (9-4) | 7: 7/7 / 0 / 1.41 |
| v69 12 | +QEP -FUEL | 12 | 7-5 | 58 | +12.1 (-12..+37) [λ.05: +12.2] | 0.82 | +14.9 (0.86) | 0.44 | v69 2130 (7-5) | 7: 7/7 / 0 / 0.73 |
| m1 11 | +SCHB -FUEL | 11 | 5-6 | 45 | +7.5 (-16..+34) [λ.05: +8.0] | 0.71 | +9.6 (0.76) | 0.37 | m1 2247 (5-6) | 11: 11/11 / 0 / 0.69 |
| c1 5 | +C1 -FUEL | 5 | 1-4 | 20 | -10.0 (-31..+29) [λ.05: -11.9] | 0.29 | -9.2 (0.31) | 0.33 | c1 2209 (1-4) | 5: 5/5 / 0 / 0.18 |
| u1 5 | +SCHC +SCHD | 5 | 2-3 | 40 | +9.8 (-20..+44) [λ.05: +12.3] | 0.70 | +11.6 (0.73) | 0.28 | u1 2208 (2-4) | 5: 5/5 / 0 / 1.65 |

### Slithery Fight

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| f1 11, k2 12, cm1 16, b3 56, l1 10, b4 11 | = b4 | 116 | 31-85 | 27 | **baseline** |  |  | 0.27 | f1 1982 (5-6); k2 1935 (3-9); cm1 1881 (4-14); b3 1976 (9-18); l1 2003 (4-7); b4 1886 (0-6) | 70: 9/70 / 0 / 0.73 |
| v61 153, m1 4, m2 3, b1 4 | -FUEL | 164 | 41-123 | 25 | -5.9 (-14..+4) [λ.05: -6.9] | 0.11 | -6.3 (0.09) | 0.31 | v61 1967 (32-105) | 61: 7/61 / 0 / 0.78 |
| kf1 80 | +KF | 80 | 11-69 | 14 | -8.0 (-16..+4) [λ.05: -8.8] | 0.08 | -9.0 (0.05) | 0.21 | kf1 1871 (12-65) | 6: 0/6 / 0 / 0.7 |
| u1 4, v1 51 | +QVS | 55 | 11-44 | 20 | +1.8 (-9..+17) [λ.05: +1.8] | 0.61 | +2.7 (0.65) | 0.18 | u1 1859 (1-4); v1 2039 (10-42) | 55: 5/55 / 0 / 0.65 |
| pb2 49 | +PB | 49 | 9-40 | 18 | -12.2 (-20..+1) [λ.05: -13.0] | 0.03 | -13.7 (0.02) | 0.32 | pb2 1951 (9-40) | 14: 0/14 / 0 / 0.78 |
| q1 39 | +Q1PARK -FUEL | 39 | 7-32 | 18 | -7.5 (-18..+8) [λ.05: -8.4] | 0.16 | -6.8 (0.18) | 0.26 | q1 1973 (7-32) | 37: 5/37 / 0 / 0.68 |
| h1 30 | +H1 | 30 | 7-23 | 23 | -2.8 (-15..+16) [λ.05: -3.5] | 0.37 | -1.9 (0.41) | 0.26 | h1 1972 (7-23) | 8: 1/8 / 0 / 0.68 |
| v55 29 | -FUEL -QSR | 29 | 13-16 | 45 | +15.2 (-2..+34) [λ.05: +14.0] | 0.96 | n/a (b4-class n=7) | 0.28 | v55 2113 (13-16) | 5: 2/5 / 0 / 0.83 |
| s1 20 | +SDEF | 20 | 4-16 | 20 | +4.8 (-12..+29) [λ.05: +5.0] | 0.68 | +6.1 (0.73) | 0.16 | s1 1841 (6-17) | 8: 0/8 / 0 / 0.8 |
| v44 19 | -FUEL -QS -QSR | 19 | 9-10 | 47 | +10.7 (-8..+33) [λ.05: +9.6] | 0.86 | n/a (b4-class n=0) | 0.35 | v44 2177 (22-12) | - |
| ms1 19 | +MID | 19 | 3-16 | 16 | -1.4 (-16..+23) [λ.05: -1.6] | 0.45 | +0.5 (0.52) | 0.17 | ms1 1903 (3-16) | 19: 0/19 / 0 / 0.8 |
| v60 18 | +QEXIT -FUEL -QSR | 18 | 7-11 | 39 | +9.1 (-9..+32) [λ.05: +8.1] | 0.82 | +1.1 (0.53) | 0.28 | v60 2047 (7-11) | 9: 2/9 / 0 / 0.75 |
| v65 17 | +QKBIG -FUEL | 17 | 5-12 | 29 | -1.7 (-17..+21) [λ.05: -3.3] | 0.43 | -0.5 (0.48) | 0.31 | v65 2079 (5-12) | 8: 2/8 / 0 / 0.65 |
| v64 15 | +L34 -FUEL | 15 | 6-9 | 40 | +8.9 (-10..+33) [λ.05: +7.9] | 0.80 | +1.6 (0.55) | 0.29 | v64 2194 (6-9) | 7: 2/7 / 0 / 0.76 |
| v69 10 | +QEP -FUEL | 10 | 2-8 | 20 | -8.5 (-22..+20) [λ.05: -10.5] | 0.24 | -9.1 (0.25) | 0.31 | v69 1998 (2-8) | 4: 0/4 / 0 / 0.72 |
| c1 4 | +C1 -FUEL | 4 | 0-4 | 0 | -18.4 (-27..+22) [λ.05: -24.6] | 0.13 | -20.4 (0.10) | 0.30 | - | 4: 0/4 / 0 / 0.87 |

### Stripes

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| f1 16, k2 16, cm1 18, b3 52, l1 12, u1 1, v1 7, b4 19 | = b4 | 141 | 95-46 | 67 | **baseline** |  |  | 0.66 | f1 2204 (11-5); k2 2280 (12-4); cm1 2237 (13-5); b3 2276 (13-10); l1 2252 (11-2); v1 2232 (2-6); b4 2285 (7-4) | 87: 0/1 / 30 / 0.44 |
| v61 158, b1 6, q1 18 | -FUEL | 182 | 125-57 | 69 | -0.8 (-11..+8) [λ.05: -1.9] | 0.44 | -0.6 (0.45) | 0.69 | v61 2232 (99-43); b1 2236 (3-3); q1 2259 (12-6) | 60: 0/0 / 14 / 6.2 |
| kf1 76 | +KF | 76 | 31-45 | 41 | -14.8 (-28..-1) [λ.05: -16.1] | 0.02 | -19.4 (0.00) | 0.56 | kf1 2235 (31-39) | 14: 0/0 / 7 / - |
| m1 13, m2 39 | +STR -FUEL | 52 | 44-8 | 85 | +17.0 (+3..+25) [λ.05: +16.5] | 0.99 | +17.9 (0.99) | 0.67 | m1 2173 (15-1); m2 2214 (32-7) | 52: 0/1 / 8 / 9.22 |
| pb2 38 | +PB | 38 | 29-9 | 76 | +6.0 (-11..+19) [λ.05: +5.5] | 0.77 | +3.6 (0.67) | 0.71 | pb2 2292 (30-9) | 16: 0/0 / 3 / 0.05 |
| h1 34 | +H1 | 34 | 17-17 | 50 | -11.5 (-29..+5) [λ.05: -12.4] | 0.10 | -13.4 (0.06) | 0.62 | h1 2266 (17-17) | 10: 0/0 / 4 / - |
| v55 29 | -FUEL -QSR | 29 | 23-6 | 79 | +5.1 (-15..+19) [λ.05: +3.6] | 0.70 | n/a (b4-class n=3) | 0.75 | v55 2086 (23-6) | 8: 0/0 / 0 / - |
| ms1 26 | +MID | 26 | 14-12 | 54 | -7.0 (-26..+10) [λ.05: -7.5] | 0.22 | -5.6 (0.27) | 0.62 | ms1 2231 (14-12) | 26: 0/0 / 12 / - |
| v44 20 | -FUEL -QS -QSR | 20 | 9-11 | 45 | -34.6 (-51..-12) [λ.05: -38.0] | 0.00 | n/a (b4-class n=0) | 0.77 | v44 1845 (10-12) | - |
| s1 20 | +SDEF | 20 | 6-14 | 30 | -29.7 (-47..-7) [λ.05: -31.4] | 0.00 | -29.4 (0.01) | 0.62 | s1 2114 (7-14) | 5: 0/0 / 3 / - |
| v65 16 | +QKBIG -FUEL | 16 | 14-2 | 88 | +13.5 (-14..+27) [λ.05: +13.3] | 0.86 | +14.4 (0.89) | 0.76 | v65 2169 (14-2) | 6: 0/0 / 1 / 0.13 |
| v69 12 | +QEP -FUEL | 12 | 6-6 | 50 | -32.7 (-52..-5) [λ.05: -36.7] | 0.01 | -32.6 (0.01) | 0.81 | v69 2005 (6-6) | 7: 0/2 / 3 / 0.66 |
| v60 10 | +QEXIT -FUEL -QSR | 10 | 4-6 | 40 | -34.7 (-55..-5) [λ.05: -39.5] | 0.01 | -28.1 (0.04) | 0.75 | v60 1977 (4-6) | 3: 0/1 / 2 / 0.26 |
| v64 6 | +L34 -FUEL | 6 | 6-0 | 100 | +22.7 (-22..+32) [λ.05: +28.7] | 0.88 | +22.4 (0.89) | 0.78 | v64 2168 (6-0) | 4: 0/0 / 0 / - |
| c1 3 | +C1 -FUEL | 3 | 3-0 | 100 | +20.1 (-31..+32) [λ.05: +27.8] | 0.82 | +20.1 (0.82) | 0.72 | - | 3: 0/0 / 0 / - |

### Tower Defense

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| u1 4, v1 50, b4 14 | = b4 | 68 | 43-25 | 63 | **baseline** |  |  | 0.58 | u1 2082 (3-2); v1 2214 (32-20); b4 2311 (9-1) | 63: 5/26 / 11 / 7.84 |
| v61 162, m1 1, m2 5, b1 5 | -FUEL -TDP | 173 | 87-86 | 50 | -22.4 (-33..-11) [λ.05: -25.8] | 0.00 | -23.1 (0.00) | 0.72 | v61 2163 (67-74); m2 2184 (2-3); b1 2136 (1-4) | 63: 5/32 / 12 / 7.61 |
| f1 16, k2 12, cm1 8, b3 56 | -TDP | 92 | 46-46 | 50 | -17.7 (-31..-4) [λ.05: -20.7] | 0.01 | -17.8 (0.01) | 0.67 | f1 2060 (12-4); k2 2055 (7-5); cm1 2145 (5-4); b3 2122 (11-16) | 75: 5/26 / 29 / 10.47 |
| kf1 83 | +KF | 83 | 53-30 | 64 | +6.6 (-8..+19) [λ.05: +3.0] | 0.81 | +0.6 (0.53) | 0.57 | kf1 2243 (49-28) | 14: 1/7 / 0 / 7.43 |
| q1 46 | +Q1PARK -FUEL -TDP | 46 | 20-26 | 43 | -26.5 (-41..-9) [λ.05: -30.4] | 0.00 | -22.0 (0.01) | 0.70 | q1 2123 (20-26) | 46: 8/15 / 20 / 1.69 |
| pb2 39 | +PB | 39 | 31-8 | 79 | +7.6 (-12..+22) [λ.05: +4.5] | 0.79 | +4.7 (0.69) | 0.73 | pb2 2365 (32-8) | 12: 0/2 / 1 / 9.79 |
| v55 30 | -FUEL -QSR -TDP | 30 | 20-10 | 67 | -12.0 (-31..+8) [λ.05: -16.7] | 0.12 | n/a (b4-class n=0) | 0.77 | v55 2159 (20-10) | 8: 1/3 / 1 / 4.47 |
| h1 30 | +H1 -TDP | 30 | 11-19 | 37 | -28.3 (-43..-8) [λ.05: -32.4] | 0.00 | -28.9 (0.00) | 0.63 | h1 2084 (12-19) | 4: 0/3 / 0 / 7.03 |
| l1 30 | +LANE -TDP | 30 | 7-23 | 23 | -33.9 (-47..-14) [λ.05: -37.9] | 0.00 | -32.3 (0.00) | 0.58 | l1 2050 (8-24) | 22: 3/5 / 15 / 0.28 |
| v44 24 | -FUEL -QS -QSR -TDP | 24 | 21-3 | 88 | +10.4 (-16..+27) [λ.05: +7.2] | 0.80 | n/a (b4-class n=0) | 0.80 | v44 2185 (22-3) | - |
| v65 22 | +QKBIG -FUEL -TDP | 22 | 14-8 | 64 | -12.9 (-34..+9) [λ.05: -17.8] | 0.13 | n/a (b4-class n=0) | 0.75 | v65 2202 (15-10) | 10: 0/4 / 3 / 7.35 |
| s1 18 | +SDEF -TDP | 18 | 5-13 | 28 | -26.2 (-44..-2) [λ.05: -30.4] | 0.02 | -25.3 (0.02) | 0.56 | s1 2098 (5-15) | 10: 0/3 / 4 / 3.08 |
| ms1 18 | +MID -TDP | 18 | 5-13 | 28 | -28.4 (-45..-4) [λ.05: -32.7] | 0.01 | -28.1 (0.01) | 0.58 | ms1 2022 (5-13) | 18: 0/3 / 11 / 2.18 |
| v69 12 | +QEP -FUEL -TDP | 12 | 6-6 | 50 | -25.2 (-46..+3) [λ.05: -31.3] | 0.04 | n/a (b4-class n=0) | 0.75 | v69 2134 (6-6) | 7: 0/3 / 2 / 3.69 |
| v60 10 | +QEXIT -FUEL -QSR -TDP | 10 | 7-3 | 70 | -14.2 (-41..+16) [λ.05: -20.1] | 0.20 | n/a (b4-class n=0) | 0.81 | v60 2026 (7-3) | 4: 3/4 / 0 / 2.61 |
| v64 7 | +L34 -FUEL -TDP | 7 | 4-3 | 57 | -21.1 (-47..+14) [λ.05: -28.2] | 0.13 | n/a (b4-class n=0) | 0.78 | v64 2176 (4-3) | 3: 0/2 / 1 / 5.83 |
| c1 2 | +C1 -FUEL -TDP | 2 | 1-1 | 50 | -11.4 (-49..+31) [λ.05: -18.9] | 0.34 | -8.4 (0.38) | 0.67 | - | 2: 0/0 / 1 / 0.09 |

### Trauma

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| f1 17, k2 41, cm1 8, b3 48, l1 8, u1 1, v1 2, b4 10 | = b4 | 135 | 128-7 | 95 | **baseline** |  |  | 0.92 | f1 2742 (16-1); k2 2790 (41-1); cm1 2616 (6-3); b3 2731 (17-0); l1 2682 (9-0); b4 2739 (9-0) | 113: 112/112 / 0 / 1.62 |
| v61 142, m1 3, m2 7, b1 5, q1 18 | -FUEL | 175 | 157-18 | 90 | -3.6 (-12..+2) [λ.05: -4.6] | 0.12 | -4.6 (0.06) | 0.93 | v61 2703 (122-15); m2 2675 (6-1); b1 2725 (5-0); q1 2759 (18-0) | 12: 12/12 / 0 / 1.32 |
| pb2 107 | +PB | 107 | 87-20 | 81 | -10.0 (-22..-2) [λ.05: -11.0] | 0.01 | -11.2 (0.00) | 0.92 | pb2 2731 (88-20) | 60: 58/58 / 0 / 1.81 |
| kf1 71 | +KF | 71 | 47-24 | 66 | -19.2 (-35..-7) [λ.05: -20.9] | 0.00 | -24.2 (0.00) | 0.89 | kf1 2697 (46-21) | 9: 8/8 / 0 / 2.23 |
| h1 32 | +H1 | 32 | 29-3 | 91 | +0.5 (-14..+6) [λ.05: -0.3] | 0.55 | -0.4 (0.47) | 0.90 | h1 2749 (31-3) | 9: 9/9 / 0 / 1.75 |
| v55 23 | -FUEL -QSR | 23 | 23-0 | 100 | +5.4 (-15..+7) [λ.05: +6.1] | 0.84 | n/a (b4-class n=7) | 0.95 | v55 2630 (23-0) | 3: 3/3 / 0 / 2.95 |
| ms1 23 | +MID | 23 | 20-3 | 87 | -4.0 (-24..+4) [λ.05: -5.0] | 0.24 | -3.6 (0.26) | 0.92 | ms1 2634 (20-3) | 23: 22/23 / 0 / 1.47 |
| v65 15 | +QKBIG -FUEL | 15 | 14-1 | 93 | -1.6 (-31..+6) [λ.05: -3.3] | 0.41 | +0.1 (0.50) | 0.95 | v65 2572 (14-1) | 3: 2/2 / 0 / 2.23 |
| s1 14 | +SDEF | 14 | 13-1 | 93 | +1.9 (-20..+7) [λ.05: +1.6] | 0.62 | +2.1 (0.64) | 0.90 | s1 2652 (14-1) | 5: 5/5 / 0 / 1.33 |
| v44 13 | -FUEL -QS -QSR | 13 | 11-2 | 85 | -17.3 (-51..+1) [λ.05: -22.9] | 0.04 | n/a (b4-class n=0) | 0.97 | v44 2568 (18-1) | - |
| v60 13 | +QEXIT -FUEL -QSR | 13 | 10-3 | 77 | -19.0 (-49..-1) [λ.05: -23.7] | 0.02 | -10.5 (0.16) | 0.95 | v60 2475 (10-3) | 6: 6/6 / 0 / 2.73 |
| v69 12 | +QEP -FUEL | 12 | 11-1 | 92 | -3.9 (-37..+6) [λ.05: -6.4] | 0.32 | -2.5 (0.39) | 0.95 | v69 2544 (11-1) | 9: 8/9 / 0 / 1.6 |
| v64 9 | +L34 -FUEL | 9 | 9-0 | 100 | +4.5 (-28..+8) [λ.05: +5.8] | 0.73 | +5.9 (0.75) | 0.94 | v64 2575 (10-0) | 6: 6/6 / 0 / 2.05 |
| c1 5 | +C1 -FUEL | 5 | 4-1 | 80 | -10.2 (-53..+5) [λ.05: -15.4] | 0.19 | -9.7 (0.20) | 0.94 | c1 2656 (4-1) | 5: 5/5 / 0 / 1.39 |

### Trophy

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| f1 9, k2 11, cm1 14, b3 47, l1 9, b4 16 | = b4 | 106 | 54-52 | 51 | **baseline** |  |  | 0.50 | f1 2112 (9-0); k2 1985 (2-9); cm1 2365 (13-3); b3 2141 (10-8); l1 2140 (4-5); b4 2151 (6-3) | 78: 0/1 / 33 / 30.96 |
| v61 164, b1 7, q1 17 | -FUEL | 188 | 99-89 | 53 | -5.4 (-16..+5) [λ.05: -7.0] | 0.16 | -4.8 (0.18) | 0.58 | v61 2171 (84-67); b1 2107 (2-5); q1 1896 (5-12) | 76: 1/5 / 27 / 24.69 |
| kf1 77 | +KF | 77 | 31-46 | 40 | -1.0 (-14..+13) [λ.05: -2.4] | 0.44 | -1.2 (0.43) | 0.41 | kf1 2057 (29-42) | 10: 0/0 / 3 / - |
| m1 10, m2 37 | +TRQ -FUEL | 47 | 30-17 | 64 | +12.0 (-4..+26) [λ.05: +10.9] | 0.93 | +13.9 (0.95) | 0.51 | m1 2168 (10-3); m2 2160 (23-14) | 47: 0/0 / 17 / 34.46 |
| h1 29 | +H1 | 29 | 10-19 | 34 | -9.1 (-25..+10) [λ.05: -10.4] | 0.18 | -10.6 (0.14) | 0.44 | h1 2095 (10-20) | 11: 0/0 / 8 / - |
| v44 28 | -FUEL -QS -QSR | 28 | 17-11 | 61 | -4.0 (-22..+15) [λ.05: -6.4] | 0.34 | n/a (b4-class n=0) | 0.65 | v44 1961 (19-12) | - |
| pb2 28 | +PB | 28 | 15-13 | 54 | -7.4 (-25..+11) [λ.05: -8.7] | 0.22 | -10.7 (0.13) | 0.61 | pb2 2208 (15-13) | 6: 0/0 / 3 / - |
| s1 22 | +SDEF | 22 | 8-14 | 36 | -7.0 (-25..+14) [λ.05: -7.8] | 0.26 | -6.9 (0.26) | 0.44 | s1 2226 (8-15) | 12: 0/0 / 8 / - |
| v55 21 | -FUEL -QSR | 21 | 11-10 | 52 | -12.7 (-30..+9) [λ.05: -15.4] | 0.12 | n/a (b4-class n=5) | 0.66 | v55 2024 (11-10) | 3: 0/0 / 2 / - |
| ms1 18 | +MID | 18 | 3-15 | 17 | -28.7 (-42..-5) [λ.05: -31.4] | 0.01 | -28.1 (0.01) | 0.46 | ms1 2132 (3-15) | 18: 0/0 / 15 / - |
| v65 14 | +QKBIG -FUEL | 14 | 6-8 | 43 | -12.3 (-32..+12) [λ.05: -15.2] | 0.16 | -20.6 (0.06) | 0.57 | v65 1950 (9-8) | 5: 0/0 / 3 / - |
| v64 10 | +L34 -FUEL | 10 | 7-3 | 70 | +11.1 (-18..+35) [λ.05: +10.1] | 0.77 | +7.9 (0.69) | 0.58 | v64 2080 (7-3) | 5: 0/0 / 2 / 42.25 |
| v69 10 | +QEP -FUEL | 10 | 3-7 | 30 | -24.1 (-41..+4) [λ.05: -27.9] | 0.04 | -28.5 (0.03) | 0.59 | v69 1938 (3-7) | 4: 0/0 / 2 / - |
| c1 7 | +C1 -FUEL | 7 | 4-3 | 57 | +2.7 (-27..+31) [λ.05: +1.6] | 0.56 | +2.6 (0.56) | 0.54 | c1 2144 (4-3) | 6: 0/0 / 2 / - |
| v60 5 | +QEXIT -FUEL -QSR | 5 | 4-1 | 80 | +18.1 (-21..+42) [λ.05: +20.0] | 0.81 | +6.2 (0.63) | 0.59 | v60 2006 (4-1) | 3: 0/0 / 1 / - |
| u1 5 | +TRG | 5 | 1-4 | 20 | -16.1 (-41..+23) [λ.05: -19.8] | 0.21 | -16.2 (0.22) | 0.40 | u1 2135 (1-5) | 5: 0/0 / 4 / - |

### weakhold

| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |
|---|---|---|---|---|---|---|---|---|---|---|
| f1 15, k2 11, cm1 9, b3 39, l1 10, u1 1, v1 4, b4 17 | = b4 | 106 | 61-45 | 58 | **baseline** |  |  | 0.57 | f1 2278 (6-9); k2 2142 (5-6); cm1 2275 (6-3); b3 2107 (7-8); l1 2273 (7-3); b4 2309 (5-4) | 49: 25/38 / 7 / 1.4 |
| v61 151, m1 4, m2 3, b1 3 | -FUEL | 161 | 109-52 | 68 | +5.4 (-6..+15) [λ.05: +4.6] | 0.84 | +5.8 (0.86) | 0.63 | v61 2234 (89-45) | 60: 34/45 / 6 / 2.43 |
| kf1 68 | +KF | 68 | 31-37 | 46 | -1.9 (-16..+12) [λ.05: -2.6] | 0.40 | -9.8 (0.09) | 0.48 | kf1 2292 (29-34) | 12: 5/6 / 1 / 1.58 |
| q1 41 | +Q1PARK -FUEL | 41 | 26-15 | 63 | +2.5 (-14..+18) [λ.05: +2.0] | 0.62 | +8.3 (0.83) | 0.61 | q1 2259 (26-15) | 41: 23/27 / 8 / 1.43 |
| h1 29 | +H1 | 29 | 20-9 | 69 | +16.0 (-3..+30) [λ.05: +16.3] | 0.95 | +16.8 (0.96) | 0.52 | h1 2326 (20-9) | 7: 2/5 / 1 / 3.96 |
| pb2 27 | +PB | 27 | 21-6 | 78 | +13.9 (-7..+28) [λ.05: +14.2] | 0.91 | +11.1 (0.86) | 0.65 | pb2 2402 (23-6) | 7: 6/7 / 0 / 1.5 |
| ms1 26 | +MID | 26 | 18-8 | 69 | +15.1 (-4..+29) [λ.05: +15.7] | 0.94 | +19.7 (0.98) | 0.52 | ms1 2259 (18-8) | 26: 15/23 / 0 / 1.79 |
| v55 25 | -FUEL -QSR | 25 | 19-6 | 76 | +10.8 (-11..+27) [λ.05: +9.9] | 0.84 | +25.0 (0.97) | 0.66 | v55 2022 (19-6) | 5: 1/4 / 0 / 1.01 |
| s1 24 | +SDEF | 24 | 15-9 | 62 | +10.7 (-9..+26) [λ.05: +11.2] | 0.86 | +14.8 (0.93) | 0.50 | s1 2227 (16-9) | 9: 4/7 / 2 / 1.21 |
| v69 16 | +QEP -FUEL | 16 | 9-7 | 56 | -13.4 (-34..+10) [λ.05: -15.6] | 0.14 | -4.7 (0.36) | 0.70 | v69 2058 (9-7) | 7: 2/3 / 1 / 1.18 |
| v44 15 | -FUEL -QS -QSR | 15 | 10-5 | 67 | -11.4 (-35..+14) [λ.05: -13.8] | 0.20 | n/a (b4-class n=0) | 0.76 | v44 1902 (11-5) | - |
| v65 13 | +QKBIG -FUEL | 13 | 6-7 | 46 | -19.2 (-39..+6) [λ.05: -21.7] | 0.07 | -6.2 (0.33) | 0.68 | v65 2074 (6-7) | 7: 3/5 / 1 / 1.33 |
| v64 8 | +L34 -FUEL | 8 | 3-5 | 38 | -23.8 (-45..+8) [λ.05: -27.8] | 0.07 | -8.6 (0.31) | 0.65 | v64 2097 (3-5) | 3: 2/2 / 0 / 2.77 |
| v60 6 | +QEXIT -FUEL -QSR | 6 | 5-1 | 83 | +10.5 (-29..+35) [λ.05: +11.5] | 0.70 | +22.0 (0.86) | 0.73 | v60 2007 (5-1) | 1: 1/1 / 0 / 3.05 |
| c1 6 | +C1 -FUEL | 6 | 2-4 | 33 | -19.2 (-44..+15) [λ.05: -22.4] | 0.14 | -14.3 (0.21) | 0.58 | c1 2209 (3-4) | 5: 3/4 / 1 / 2.53 |
