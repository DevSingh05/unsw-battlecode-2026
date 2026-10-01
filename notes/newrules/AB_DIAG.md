# Server A/B diagnosis: v35 vs v36 vs v37c (same top-10, 5 maps x 10), 2026-10-01
Scripts: scratchpad ab/{an,agg,win,eat,tf,qk}.py (sim2-based). We are side A in all 150 games. Queen id = the id in {0,1} whose map DRAGON team is ours
(on Dilemma/Trophy/Slithery id 0 is team B, so a fixed "id 0 = ours" is wrong there).

Wins: v35 25/50, v36 21/50 (all 50 replays present), v37c 21/50.
| map | v35 | v36 | v37c | note |
| Dilemma | 9 | 8 | 7 | elim map, queens die r5-7 for everyone |
| Trophy | 7 | 4 | 3 | the regression |
| Slithery | 4 | 4 | 3 | flat; r500 longest 51/54 vs 51/63 vs 48/65; queens die r5 |
| Schooltime | 1 | 2 | 4 | gain |
| Portals | 4 | 3 | 4 | flat |

## Trophy (all games elim)
- units us/them r50: 13.8/10 | 11.4/10.6 | 10.3/13.0; r100: 28/15 | 19/23 | 17/27; r200: 44/18 | 21/35 | 18/35.
- Our eats r26-50: 29.5 | 19.7 | 20.3 (r1-25 equal: 9.3/8.7/7.5). Eats r1-75: 76 | 61 | 50, mostly lost far from enemies (en5+: 59 | 47 | 39).
- Small non-queen units (L<=4, enemy head within 5, r<=100): ending at dist 2 from the enemy 8.0% | 4.9% | 4.7%; dist 3 unchanged (19.5/19.2/20.8%);
  moved closer 35.5% | 32.0% | 31.8%; ate per move .090 | .077 | .078. Same fingerprint on Schooltime (10.5->7.5%) and Dilemma.
- Head-on deaths are not the cause: per game our d1/d2+ victims 3.2/8.5 | 6.4/10.4 | 3.5/5.4 vs theirs 13.4/16.8 | 21.9/34.7 | 10.7/20.0. Rams always kill both.
- Our queen died r50 (5/10 while ramming) | r129 | r146. Queen splits r<=60: 2.1 | 1.7 | 1.7.

## Flags
- THREAT_FREE: v35 small units have MAX_THREAT_REACH=1. TF adds a paid tier to F+2 (L3: dist 2, L4+: dist 3) at 0.33*12 = -4 for small units.
  That is exactly the dist-2 drop (-40%), with dist 3 unchanged. Local KREACH (similar extra caution) scored trophy .29 (V37A.md). Main suspect.
- QUEEN_SAFE: removes one fighter (v35 queen got ~0.5 kills/game on Trophy) and ~0.4 early queen splits. Small effect on Trophy. But it is the only thing
  that kept our queen alive: alive at end 0/50 | 3/50 | 3/50, all 6 were wins. Locally S1 was the biggest cost (.39-.42 vs v35).
- FREE_FIX: almost inert (F=1 at L<=4; EAT_SPRINT=0). QUEEN_HUNT: enemy queens killed by us in 10 | 12 | 12 games, no change.
- QKILL fired 3 times: dist-3, 3-step kills by an L4 (835970 r20, 835980 r23, 836057 r166). v35/v36 never did that; all 3 were wins.

## r500 queen-tiebreak losses
Lost at r500 with our longest larger but their queen alive: v35 3, v36 3, v37c 3 (Schooltime 36v19, 38v11, 32v19, Portals).
Our queen deaths (Trophy+School+Portals): HitSelf 15 | 13 | 13 of 30, at L2-3, all after r20 in v36/v37c. Several opponents' queens now survive (Computers, Sponge, 中国).
