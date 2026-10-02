# v37d (= v38 on known maps): the 37 server losses vs the top-10, 2026-10-01
Data: replays/ab_v37dsrv (21 losses) and ab_v37d_other (16). We are side A in all of them (replay result matches launch.log).
Queen = the id in {0,1} whose map DRAGON team is A. Scripts: scratchpad ab/{loss,qall,late,kingd,lens,k2,eco,qtrace,win5}.py (sim2).

## Classes
(a) eliminated: 16. (b) r500, lost on the queen step: 5. (c) r500, both queens dead, lost on longest: 16. (d) other: 0.
| map | n | class | games |
| Slithery | 7 | c | all 7: both queens die r4-5 (forced by the spawn pocket, see below) |
| Trophy | 5 | a | dead by r71-215. Units us/them r50 2/17, 7/16, 12/7, 5/11, 9/13; r100 0/30, 7/39, 21/15, 11/34, 7/38 |
| Devil | 5 | 4a + 1b | a: r100 3/19, 1/26, 0/29, 5/26. b 842159: we had 46 units, longest 13 vs 2, but our queen died r120 (HitSelf L2) and theirs (L2) lived |
| Portals | 5 | 4c + 1b | b 837856: longest 61 vs 43, our queen HitSelf r122, theirs alive at L3 |
| Autarky | 4 | 3a + 1c | queens die r5-10 for both teams (forced). a: r100 11/24, 20/25, 18/30; r200 2/54, 17/41, 15/44 |
| Default | 3 | 1a + 2c | c: longest 6/48 (Stockfish), 13/28 (中国) |
| Queen of Spades | 3 | 2a + 1c | |
| Schooltime | 3 | 1c + 2b | b: 837557 (27 vs 24, our queen HitSelf r222, theirs L18), 837855 (34 vs 18, ours killed r43, theirs L11) |
| Dilemma | 1 | a | |
| Trauma | 1 | b | 842326: both queens alive, ours 7 vs theirs 18 (our longest was 30 vs 18) |
By opponent: 中国 6, Stockfish 5, Sponge 5, C-- 5, WHQ 4, 3.14 3, Delusion 3, calc 2, SKKU 2, Computers 2.

## (c) longest, us/them at r300 / r400 / r500
Slithery: 19/28 42/45 54/64 | 22/5 41/34 43/55 | 17/25 41/52 53/66 | 19/23 44/45 37/44 | 28/8 41/33 44/60 | 21/37 36/74 65/101 | 17/13 28/28 31/55.
Portals: 3/6 17/27 37/58 | 4/12 15/21 38/40 | 4/7 21/18 34/39 | 4/5 17/10 44/46. Others: Default 3/11 9/27 6/48, 3/4 3/15 13/28; Autarky 3/3 3/6 10/50; QoS 3/11 4/29 24/37; School 3/19 6/38 13/66.
We lead or tie at r300-400 in 8 of 11 Slithery+Portals games. Our king adds only +6.9 in r400-500 on Slithery; theirs adds +18.
Our length is spread over 2-3 big dragons: 837541 54+44, 837546 43+41+26, 837551 53+22+22+20, 837859 37+30+29 (r450), 837566 37+23,
837548 37+26+18, 837558 38+24, 837573 34+15+10, 837861 44+11. Our top two are 8-30 tiles apart at r420-480.
Our king died late in only 2 losses: 837566 (L46, killed r451 by an L2) and 837859 (L40, killed r483 by an L6).

## Queen
Our queen alive at r500: 25/100 games, and we won 24 of those (the loss is Trauma 7 vs 18). Their queen alive: 7/100.
Forced deaths: Slithery spawn head (54,16) sits in a dead-end pocket 16-18 (only S is open), so the queen dies r5. Autarky r10 and Dilemma r7 are the same for every team.
In 10 r500 losses, our queen surviving at her current length would have won (their queen was dead or L<=3):
842159, 837856 (b) and 837548, 837558, 837573, 837861, 842193, 837577, 842155, 842160 (c).
6 of the 10 deaths are HitSelf at L2-3 in kelp corridors, boxed by kelp plus ally heads or bodies, 1-13 rounds after a queen growth split L4 -> 2+2
(837558 split r227 died r228; 837573 57/59; 837861 88/101; 837856 116/122; 842159 117/120; 837557 221/222 among the b losses). The other 4 were H2H by an enemy head at dist 1.
Over all 100 games: 25 of our queen's HitSelf/HitOtherBody deaths after r12 had an ally adjacent; 12 came within 3 rounds of a queen split.
The queen does 3.35 splits per game, so she never grows past L4-5. In the 3 b losses, their queens reached 11-18.

## Eliminations
Total length is about equal at r25. By r100 theirs is 2-3x ours. Eats per unit-round are equal (Trophy losses .095/.092, Devil .098/.131),
so the gap compounds from unit count (splits r26-100 in Trophy losses: 19 vs 42). Head-on trades stay 1:1. This is the r25-60 fight snowball already covered in AB_DIAG.
