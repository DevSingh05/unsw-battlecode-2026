# Sprint maps synthesis (7 maps; v35 = our Sprint bot; ~10 losses: Aus 2, Maze 2, Stripes 3, Isl 1, AUNSW 1, weakhold 1)
Caveat: every maps/sprint/*.map has TILE gaps `0 0` (no natural pearls locally); spawn tiles in the per-map notes were inferred from replays. Rebuild the map files before local tests.

## A. Recurring design themes (expect these in the Qualifier's unseen maps)
1. Portals as blind shortcuts / portal-only regions: Australia (2 sealed vaults, ~25% of pearls), Islands (12 pairs to the centre fountains), Maze (16 pairs; walk 48->25 steps; 88 portal-only tiles), Stripes (band links), Around UNSW (NE<->SW).
2. Rich pearls in dead-end pockets/tips (fast respawn, every 4-15 rounds): Maze tips, TD 2-tile pockets, weakhold fast pockets, Islands alcove fountains, Australia vaults.
3. Poor home, rich contested middle: weakhold bay (0 spawns), TD rooms (0.06/rd) vs mid (0.66/rd), Maze rooms (slow) vs maze (60%), Australia (6 spawn tiles within 10 of start), AUNSW empty quadrants.
4. 1-wide corridors and 1-tile doors: Maze, TD, Stripes, weakhold (top teams log 100-250 wall deaths there).
5. Bait/denial: sealed unreachable pearls (Stripes boxes), planted units in the enemy half (Aus lone L4, Islands L2 on enemy fountain, AUNSW L3 raiders).
6. Geometry: 180-degree rotation on 6/7 (Islands is a mirror); wrap edges on Islands, Stripes, AUNSW. Size sets the game type: small and scarce (Stripes, TD) = swarm/elimination; large (Aus, AUNSW, Maze, Isl, weakhold) = r500 king race, kings only form after r250-300.

## B. Where v35 is weakest (ranked by Sprint losses)
1. Late or split king (UNK_KING_SEED/FEED 250/300, feedReserveNow reserve 14->3): 7 losses (Aus 2, Maze 2, Isl, AUNSW, weakhold). PPP led on king at every checkpoint, e.g. 27 vs 13 at r300 on AUNSW. Feed was split over 2 kings (35+31 vs 62), and on weakhold the king parked in the zero-spawn bay.
2. No portal use on unknown maps (LEARN_PORTALS=0 means portal = kelp; explore only at hunger 100000; UNK_SEALED_FOOD=0): 5 losses (Aus 2 with 0 vault pearls, Isl 1 with 0 crossings, Maze 2 with 8-37 portal moves vs 150-550).
3. Unknown-map explore wandering away from food on scarce maps; never reached L4, so it never split: 3 losses (Stripes; ate 1-11 pearls vs 34-279). Suspected cause of the slow AUNSW start (36 vs 49-55 units at r50).
4. Self-collisions of L2-3 in dead ends and ally jams: Isl 165 HitSelf in the loss (85 on dead-end tiles), TD 389 (302 at L2, 194 ally+kelp boxed), 47 TD pocket-pump deaths. These cost unit count rather than whole games, except the swarm game in Isl.
5. tryKingEscape SPLIT L-2 loop in corridors: Maze vs dslafkj (king 27 split 9 times, lost ~18 length).
6. Can't break a turtle: TD vs Serendipity (won only on longest 30-6; under the queen rules a turtled live queen beats us).

## C. General behaviours to add or fix (runtime-detectable)
- Portal learning: when any head steps on a portal, record src->dst. Infer the partner by map symmetry. Plan through known portals, and send 1-2 expendable L2-3 scouts into unknown portals by about r20-40, not only when sealed. Turn on the sealed-food trigger: visible pearls with no walk path => go via portal. (B2; Aus vault, Isl, Maze)
- Spawn-rate map: count respawns per tile seen and rank hot tiles (respawn every 4-15 rounds). Foragers patrol the hot tiles. The king/queen grazes hot tiles near home, never a zero-spawn region. (B1 weakhold, A2)
- King timing by map class: on big boards seed about r150-200 and feed one king only (merge, not 2); shrink the feed reserve. On small, scarce boards don't seed; split at L3-4 and maximise heads. Classify by water tiles and observed food rate in the first ~30 rounds. (B1, B3)
- Leash on scarce maps: if visible food rate is low, don't explore unseen tiles beyond N steps from known spawns; ignore pearls with no walk path unless a portal route is known. (Stripes)
- Dead-end safety: precompute dead-end and pocket depth from known kelp. An L2-3 enters a depth-1 tip only if the reverse is legal or it has a planned split. Avoid entering a tile whose only exits hold allies. (B4; Isl, TD)
- Escape: cap king splits (e.g. 1 per 20 rounds) and use the true enemy reach (free moves ceil(L/4)) rather than "every corridor step is threatened". (B5)
- Siege: the enemy queen start = sym(our queen start). After about r150, if the enemy queen is alive and static, send L4+ hunters to its home. (B6, TD)

## D. Under the new queen rules (queens = ids 0/1, longer queen wins r500, free moves ceil(L/4))
- Spawn: 6/7 starts are safe at r0 (22-73 steps from any enemy). Stripes is the exception (enemy heads in the queen's band by r25-40). Organisers say spawns are moving to safer spots and new maps are coming, so we should rely on the general behaviours above, not per-map tables.
- The real killer is our own play. In Sprint, Isl ids 0/1 died 19 of 20 times at r39-120 and AUNSW 22 of 22 by r275, from head-ons, kelp and self-hits at L2-3 plus feed-suicides. TD was the safest (queen alive in 4 of 6).
- Queen rules: never SPLIT (SPLIT L-2 leaves the id on the 2-long head), never feed-suicide, never enter dead ends, portal tiles or 1-wide corridors. Keep at least 2 tiles beyond any enemy head's reach. She moves first, so every head reacts to her move.
- Where to park her: a low-traffic area near home next to a hot tile. Candidates: Stripes own middle band, AUNSW empty quadrant, weakhold bay rows 3-11, TD inner room, Maze room plus home tips, Aus/Isl home water away from the vault and portal ends. Guard the 1-2 nearest entrances (Maze gaps, weakhold lanes).
- The old king race becomes a queen race: feed the queen as the single king (earlier, about r150-300). The army does the portal and pocket income. On swarm maps the swarm must still win, but any elimination includes her.
