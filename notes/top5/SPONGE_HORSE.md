# Sponge (#1, id 213) and horse (#2, id 842): replay study, games after 2026-10-02 04:15 UTC
Data: 16 replays, 13 maps. 10 are Sponge v horse ranked games (854873-7, 860437-41). 6 are ours: 854884/5/7 v Sponge and 854388/9/90 v horse, all played by v38m (v40 went live 06:57). Listing: games/__data.json?teams=ID&page=N (notes/tools/list_games.py); battle detail: /api/v1/battles/{id}. Scripts and replays: scratchpad top5/{an,an2,an3}.py (sim2).
Caveat: queens are map-file dragons 0/1, and the map team of dragon 0 can be B (Stripes). Look up the queen's team, don't assume 0 = A.

## Results
- Sponge v horse 6-4 overall. Sponge won 6 of 7 r500 games (lost Maze). horse won all 4 elimination games (TD r148, Stripes r128, Default r199, weakhold r362).
- Queen tiebreak decided 1 of 7 r500 games (Trauma: Sponge queen L59 alive, horse queen dead at r61). Schooltime: both queens parked at L3 (moved 1 tile all game), so the longest dragon decided (91 v 50). The other 5: both queens dead, longest dragon decided.

## Queen behaviour (both teams)
- An L4 queen is split 2+2 on round 0 by both teams in every game (we do the same). After that she roams as an ordinary L2-3 unit, 10-29 tiles from spawn by r50.
- Queen death round. Sponge: 11/13 died, median r93 (by head-on 8, wall 2, self 1). horse: 10/13 died, median r66. Ours: 5/6 died, r101-193. Queen kills: Sponge 3, horse 6, us 3 (in 6 games).
- **Late queen feeding when she survives.** Sponge Trauma: queen L2 at r100, 10 at r200, 34 at r400, 59 at the end. 57 eats, 49 of them corpse pearls from her own team, and 37 ally deaths within 3 tiles of her. horse Islands: queen L3 at r200, 40 at r400 (40 own-corpse eats), killed r452 by a Sponge L15. horse Australia v us: queen L4 at r300, 17 at r400. Sponge Maze: queen L22 at r200, then used as a 2-split pump (22 splits); died r388 at L3.
- v40 has QUEEN_KING=0, so we never feed the queen. Both top teams do once she lives past about r200, and a lone surviving queen wins the tiebreak.

## Distinctive, map-independent behaviours
**horse**
1. **Uses free sprint steps.** Takes 2+ steps on 45% of L5-8 turns, 49% of L9-16 and 50% of L17+. Paid-step share for L>=5 is 0.3% or less. Pearls per turn: .160 at L5-8, .217 at L9-16, .341 at L17+. Sponge: 23/25/20% with paid 0, .131/.183/.294. Us (v38m): 0.1% at L5-8 and 0% at L9+, .085 at L5-8. v40 still has EAT_SPRINT=0.
2. **Faster early economy.** Before r100, median 38 splits (almost all k=2) and 98 pearls, vs Sponge 28/70 and us 28.5/65.5. horse ate more than Sponge by r100 in 8 of 10 head-to-head games. In its elimination wins, units at r100 were 12-20 vs 1-9 for the opponent.
3. **Mid-game cascade of medium dragons dissolved into the king.** 121 deaths at L>=10 over 7 r500 games, median r322, median L13. 72 were HitSelf suicides, and 458 of their 531 pearls went to horse (an L>=10 dragon steers into its own body next to a bigger ally). Cost: 42 of these L>=10 dragons died head-on, and the enemy ate 273 of their pearls. That leak is why horse loses r500 games to Sponge.

**Sponge**
1. **Late king consolidation by explicit suicide.** 17 of 25 L>=10 deaths are NoValidAction (the default-suicide action) at median r440. 114 of their 129 pearls went to Sponge, 93 of them to one dragon. Longest dragon r400 -> end: 28->57, 34->91, 14->62, 37->57, 57->83. Units fall from about 60 at r300 to 4-31 at the end. The king stays at 8-17 until r300.
2. **Keeps big dragons out of fights.** Only 6 L>=10 head-on deaths in 6 r500 games (horse 42 in 7). The king takes 2+ steps on only 16% of turns after r300 (horse's 56%). Sponge feeds its own pieces to itself instead of trading them.
3. **Deep lunges by small units.** 435 kills: 87% by L2-3 units; by steps taken, 1: 178, 2: 183, 3: 55, 4: 19 (17% with 3+ steps). horse: 13% with 3+ steps (64 of 493). Us: 111 kills, all with 1-2 steps. Both teams also kill dragons we model as out of reach.
- Also: Sponge dissolves feeders mostly by HitWall (683) and NoValidAction (453), horse by HitSelf (1385). Same purpose, different method. Portal steps per step taken: Sponge 0.86%, horse 0.77%, us 0.21%. On Australia we took 1 portal step in 19.8k steps, horse 95 in 26.4k and Sponge 118 in 25.7k. That was v38m, which didn't know the Sprint maps; recheck v40, especially portal use on unseen maps.

## Suggested transfers to v40 (all behind flags, test on unseen maps)
1. EAT_SPRINT-style free-step pathing for L>=5 (target 2+ steps on 30-50% of turns, never paid).
2. Endgame merge: from about r380, any L>=10 non-king with an ally king within a few tiles suicides (default action) next to the king. The king avoids fights from r300.
3. QUEEN_KING-lite: if our queen is alive at r250 and the enemy queen is dead or shorter, route corpse feeding to her (Trauma: L59, won).
4. Extend our lunge model to 3-4 steps for L3-4 rammers, in both attack and threat checks.
