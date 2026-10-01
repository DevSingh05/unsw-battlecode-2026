# Why queens die early (unswbc 1.2.3 local, 2026-10-01)
36 games: {v35-v35, v36q-v35, v35-v36q} x {default, schooltime, devil, trauma, gen/g2026_01, gen/g2026_02} x seeds 1-2.
Replays and logs are in scratchpad/qn/ (named v35_v36q_<map>_s<seed>.*). Scripts: notes/queen/qdeaths.py (one row per queen), qkill.py (killer distance and reach), qescape.py (did a safe 1-step move exist on her last turn). Per-row output: scratchpad/qn/q*.txt.

## Facts
- Head-to-head kills BOTH dragons whatever their lengths (engine Step(): Kill other, Kill self). An L2 enemy trades 1:1 with an L54 queen.
- Queen id: id 0 is the 1st DRAGON line and id 1 is the 2nd (ids follow map line order; checked in all 36 replays). In every map here line 1 is team 0 and line 2 is team 1.
- The 1.2.3 toolkit maps are byte-identical to maps/ (no "safer spawn" update yet). No queen spawns in a pocket on these 6 maps (head deg 4, 32-44 open tiles within 4 steps).
  But default spawns the two queens 2 apart through the torus wrap: (0,0) and (31,31). Other spawn gaps: g01 4, g02 5, devil 7, schooltime 7, trauma 15. QUEEN.md says slithery spawns both queens in a dead-end pocket.

## Counts (72 queen-games)
| bot | died | <=r150 | median round | median L at death | head-on, she moved in | head-on, enemy moved in | into ally body | self-trap | wall/portal | survived |
|---|---|---|---|---|---|---|---|---|---|---|
| v35 | 42/48 | 32 | 67 | 3 | 18 | 10 | 6 | 8 | 0 | 6 |
| v36q | 21/24 | 13 | 91 | 7 (max 54) | 2 | 14 | 0 | 5 | 0 | 3 |
No queen died to kelp or a portal, and no queen died head-on with an ally. 16 of 63 deaths were in a corridor tile (2 or fewer non-kelp exits). The rest were in open ground.

## Dominant causes
1. **Rammed head-on by a small enemy (24, 14 of them v36q).** Every killer was L2 or L3, 1-2 tiles away at the start of its turn, so within its reach. v35 tryRam values a target at 40+3*theirLen, which makes a long queen the best ram target.
   On her last turn, 11 of 14 v36q victims had no safe 1-step move (qescape.py): she was already boxed in with 1-2 legal exits. A 1-ply threat penalty sees the danger too late.
2. **v35's queen is just another small unit (18 times it moved head-on itself).** v35 splits her down to L2-4 (up to 9 splits) and then she rams or forages like any other unit. Median death r67.
3. **Self-trap or body hit late in a long life (13 v35, 5 v36q).** On trauma the queens grow to 26-54 and then coil into themselves or a teammate around r350-450. v35 splits her to L2 first; v36q, which never splits, coils at L38-54.

## Proposed queen-survival behaviours (all behind QUEEN_* flags)
- **Head-distance invariant.** End every queen turn with each enemy head farther than reach(L) = ceil(L/4)+(L-2), capped at 3 for L<=4 units. Look ahead 2-3 plies, counting her escape squares and not just the threatened tile. Treat ally heads within 1 tile as blockers.
- **Safe-region home.** Each round, pick the region on our half with the most open tiles and the fewest enemy-head arrivals (a BFS from all enemy heads beats a BFS from her). She grazes only pearls she reaches strictly before every enemy head (+2 margin), and never enters the centre or the yards.
- **Bodyguard screen.** 1-2 allies of L>=3 park between her and the nearest enemy head and ram any small enemy within 2 tiles of her; this is v35 tryRam with the target set to "threatens queen". The queen never rams.
- **Keep the queen as a reserve, not a grower.** Split her early (before r150) for economy while L>=4 (QUEEN.md idea). After about r430, all-feed her through allies. She doesn't need to be big, only alive and longer than theirs at r500.
- **Anti-coil.** Use the v36q QUEEN_ENCLOSE_PEN reachable-area check with her own tail treated as moving. Once she is long (L>=20), keep her in a loop region or peel her tail to an ally.
- **Offence.** Our cheap L2-3 units should hunt the enemy queen (id 1-myTeam) with the same 1:1 trade. It costs almost nothing and decides the game.
