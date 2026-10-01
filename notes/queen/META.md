# Queen-rule meta at the top (2026-10-01, games 13:58-15:37 UTC)

Sample: 21 public replays (42 queens) since the rule change. Server is on 1.2.3 free-step rules: a len 4-7 dragon makes 2-step moves at 0 cost, len 12+ makes 3-4.
Games: Sponge v Stockfish x5, C-- v 3.14 x3, Sponge v calc x2, calc v 龙虎豹, y v Stockfish x2, :3 v C-- x2,
C-- v Sabotage-d x2, Sponge v WeHaveQuizzes, Sponge v SKKU, 中国必须人能飞 v Cutlery x2. Script: notes/queen/meta_analyze.py.
Replays: scratchpad/qn/*.replay. The team list is in scratchpad/qn/allgames.json (from /games/__data.json?teams=ID&page=N).

## Headline: nobody has adapted. Top teams treat the queen as an ordinary dragon.
- Queens alive at r500: 0/42. One queen (Stockfish, Trophy) was still alive (len 4) when it won by elimination at r152.
- Queen death round: 18/42 by r10, 20 in r11-150, 3 in r150-250 (latest r244).
- Cause: 19 head-to-head with an enemy, 23 HitWall/HitSelf/own H2H. Self-inflicted deaths are the majority.
- Splitting: every team splits its queen at r0-3, down to len 2-3 (Default 5->2/3, Autarky 15->3, Slithery 8->3/4).
  Stockfish/C-- peel 2-segment tips off the queen every turn. After that the queen keeps growth-splitting at 4 -> 2+2 (5-9 splits per game).
- Queen length at r100/200/300 while alive: always 2-3. Max after r10 is about 4-5. No team grows a queen.
- Feeding: none. The queen eats 0-15 pearls, under 1% of team eats. It eats 0-3 own-team corpses, and own dragons die within 2 tiles of it only 0-1 times per game.
- Hide or roam: it roams like any swarm unit. Mean distance from spawn is 7-37 (max 13-48), and the mean distance to the nearest enemy head is 5-15.
- Hunting the enemy queen: no sign. The mean queen-to-queen distance is 8-34. Its H2H deaths look like ordinary swarm collisions with tiny 2-3 segment bodies.
- Slithery Fight: all 12 queens (6 games, every team) die at r3-5 in the spawn pocket. The map is unplayable for the queen until maps are updated.
- Stockfish (#1) team description says "Bot is not updated." Behaviour fits pre-queen code for every top team sampled.

## Who wins at r500 now
- 13/21 games reached r500, and every one went to the longer LONGEST dragon. In 3 of them the team with the larger total lost.
  Both queens were dead in every game, so the queen tiebreak never fired. 8/21 ended by elimination at r74-338.

## Implication for us
- Any queen of length >=1 alive at r500 beats these bots on tiebreak (queen 1+ vs 0), whatever the longest/total.
  The queen does not need to be big, only alive. A tiny hidden queen (len 2-4, never fights, avoids all heads and corridors) is enough.
- So: v35 economy for everyone else, plus a queen that only survives. v36q's no-split, big-queen design is the wrong target.
  Let her shed early (that matches the meta and keeps economy). Then park her len >= 2 in the safest open pocket and give her v36q's threat avoidance.
- Elimination still decides about 40% of games, so a hidden queen must not cost army strength. On Slithery accept a dead queen until maps change.
- Re-check after map updates and after Stockfish/calc change their descriptions or resubmit. One fix by them flips this edge.
