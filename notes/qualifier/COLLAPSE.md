# Unit collapse on small crowded unknown maps (Devil, blind v35) - 1 Oct 2026
Data: 10 blind-v35 Devil games, replays/ab_blind34kr (1W/9L, all games vs the top 10). For comparison, 17 known-map v35 Devil games vs the same teams, 30 Sep 19:56 to 1 Oct 02:22 (7W/10L; ids in scratchpad q/known_devil2.json), plus 15 v34 ranked games (9W/6L). Tools: sim2 plus scratch scripts in scratchpad q/ (col.py, cmp.py, board.py). Devil is 32x16 with **no portals**. Every lane outside the centre is a 1- or 2-wide kelp corridor.
## Numbers (blind losses, per game; window r20-120 unless noted)
- Units r30/50/75/100: us 7.3/8.3/7.3/6.8, them 11.5/19.6/23.5/29.3. We don't so much collapse as never grow.
- Splits: us 29, them 104. Turns where a dragon of L>=4 moved instead of splitting: **us 0.7, them 61**. So the split gates (main.cpp:3817-3820, ESCAPE_SPLIT, keepLen=0, PORTAL_NO_SPLIT=0, unitLimit) never block anything: every dragon that reaches L4 splits. Splits are **starved of length** (mean length about 2.2).
- Eats: spawn pearls us 41 vs them 157; corpse pearls 33 vs 110. Length lost in deaths 78 (us) vs 180 (them). Our net length is about 0, theirs about +87.
- Our deaths (281 in 9 games, all of length 2-4: 158 L2, 105 L3, 18 L4):
  - self-trap (HitSelf): 111
  - rammed head-on by an enemy: 102. Mostly even L2/L3 trades, or the enemy is 1 longer (2v3 25, 3v3 22, 2v2 17, 3v2 12).
  - we moved into an enemy head and died: 50
  - into a body: 18, of which 14 ally
  - portal: 0 (none on the map). Starvation: not an engine death cause.
- Self-traps: **102 of 111 have neighbours (ally, kelp, kelp, own neck)**. That is a 1-wide kelp lane whose only way forward is blocked by an ally's body or head (an ally crossing the lane mouth, or a second ally coming in from the other end through the wrap). The nearest enemy is more than 3 away in 92 of them. Rate per 1000 unit-rounds: blind 16.8, known-map losses 6.8.
## Known vs blind Devil (same opponents; v35 is identical on known maps apart from map data)
- Our heads in the centre (x 12-19) at r15/25/35/45: blind **0.4/1.3/1.1/0.8**, known losses 3.8/4.3/4.3/3.8, known wins 3.6/6.6/9.6/11.9.
- Spawn pearls eaten r0-50, centre/outside: blind 5.4/16.1 (them 39.4 in the centre), known losses 15.6/3.1, known wins 37.1/3.7.
- Known Devil is bimodal (whoever holds the centre by about r30 snowballs: wins reach 29 units at r100). Blind, we never contest the centre: the starters split at home on the east edge and forage the lanes there.
- These do **not** explain the gap: the ram guard is the same in both modes (known: RAM_GUARD_LOCAL main.cpp:135 gives ramGuard=2; unknown: UNK_SMALL_RAMGUARD main.cpp:850 gives 2 when N<=750). maps/devil.hpp is an empty stub, and Devil has no portals. The whole known-map advantage is **map data**.
## Mechanisms and code
1. **No pull toward unseen food.** On unknown maps, `World::rate()` (main.cpp:631-643) returns UNK_PRIOR=0.001 (params.hpp:421) for never-seen tiles, and `pearlValue()` (main.cpp:1095-1131) values them at about 0.5*arrive*0.001, close to 0. On the known map, gmin/gmax (maps_data.hpp:110) pull us to the centre hot tubes and dead ends. Result: we eat 1/3 to 1/4 as many spawn pearls from r0 onward, so no length and no splits.
   - EXPLORE_LEARN, LEARN_GAPS and HOT_LEARN (all off) were only judged blind-vs-blind locally, where neither side contests the centre. The real opponents rush the centre by r10, so those local tests were biased and need a server test.
2. **Unseen edges are assumed open, and children start with no map.** `nxt` is initialised to plainStep (main.cpp:333-336), and only `observeEdges` (514-583) adds kelp. Children start fresh, so beyond their 7x7 view a 1-wide lane looks like open ground. The survival search therefore enters lanes and thinks there are side exits. It also doesn't model an ally body closing the lane. That gives about 11 lane-ally self-traps per game (~2.5x the known-map rate), plus the 14 deaths into ally bodies.
3. **Even head-on trades while thin.** We are rammed 11 times a game, at L2-3 against L2-4. The enemy eats 143 of our corpse pearls; we eat 56 of theirs. With 1/3 of their units, an even 1-for-1 trade is a net loss. This is the secondary drain once mechanism 1 has made us thin.
## Caveat and next steps
- Caveat: in the blind tests the opponents knew Devil. On truly unseen maps they lose that data too, but pi and cheji rush the map centre in a way that looks generic.
- Fix 1 (general, unknown maps only): an early frontier/centre prior. For example, from r0 to r60, value never-seen tiles by how close they are to the map centre / symmetry axis, or give EXPLORE_LEARN a higher floor. Test it on the server against the top 8 on Devil, Trophy and Prisoners Dilemma.
- Fix 2: a lane-entry guard. Don't step into a 1-wide tile (both side edges kelp) whose far end is unseen when an ally head is within 3 tiles of the lane or of its mouth.
- Measure both against these 10 blind games (target: ≥3 centre heads at r25, and lane-ally self-traps below 7 per 1000 unit-rounds).
