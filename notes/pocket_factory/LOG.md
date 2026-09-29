# Pocket factory (POCKET_FACTORY) experiment log

Tools (run from project root):
- `python3 notes/pocket_factory/mech.py "bot:-DPOCKET_FACTORY=1" --maps autarky,dilemma --seeds 2 --jobs 3 [--keep DIR]`
  plays cand vs v29 both sides, prints per map: win, dives, net/dive, pocket eats, stub deaths (L2/L3/L4+ dying in pockets), totals.
- `python3 notes/pocket_factory/pockets_show.py maps/X.map` lists leaf-pruned pockets (depth, gaps) and starters' head/tail pocket status.

Design (bot/main.cpp, flags in params.hpp, all default 0 = v29 behaviour):
- pfCompute: leaf-prune the known edge graph; pfDepth (1 = mouth tile), pfComp. Once on known maps, every turn on unseen maps.
- pfPearl/pfBranch: timed expected pearls along the best inward branch (visible pearl or countdown <= arrival = 1.0;
  remembered 0.7; unseen fast tile 0.7/0.4). Path stops at tiles still occupied on arrival.
- Entry (pfDiveOK, replaces pocketWorthPumping for inward pocket moves): L2..PF_ENTER_MAXLEN, no other head inside the
  pocket (one diver), no enemy head adjacent to the entry, PF_ENEMY local-count rule, L+P >= 4+PF_SAFETY, P >= PF_MIN_P.
  Accepted entry gets +PF_BONUS*(P-2).
- Inside (pfInward: head in pocket, neck shallower, tail not in a *different* pocket -> corridor starters keep v29 play),
  L <= PF_MAXLEN: move along the best branch while >= PF_AHEAD_MIN pearls ahead (suppresses the one-tile-early SPLIT 2);
  else SPLIT L-2 (child = tail end facing out) if the child has PF_CHILD_AREA room, else step deeper first.
- pfChildInwardBad: a normal split whose child would be born inside a pocket facing inward is skipped unless that child's
  own dive passes the entry numbers (this was the big leak: L2 grandchildren dying in emptied pockets).

## Log
- 21:20 UTC baseline (bot flags 0 == v29, identical results). v29 self-play: Autarky 80 dives/g at +0.24, stub3 66/g;
  Dilemma 34 dives +0.03; Slithery 192 dives -0.28 (stub3 151/g, 12 L4+ pocket deaths/g). Dilemma is side-determined
  (side A wins, ends r167-184 by elimination; rams in the middle).
- 21:30 PF=1 v1 (no child guard): Autarky net/dive +1.01 (shapes (3->4), (2->3)), but 0.25 win (1/4), totals behind at r200;
  133 L2 pocket deaths/g vs 85 dives: exiting L4 children split 2 inside the mouth -> inward L2 grandchildren die.
- 21:38 PF=1 v2 (+pfChildInwardBad): Autarky 4/4 (total r200 105 v 38, end 132 v 16, base eliminated twice), net/dive +0.93,
  pocket eats 369 v 128. Dilemma 2/4 (side-determined, same as base).
- 21:50 Local caveat: Dilemma and Devil are fully deterministic here (bot RNG seeded by dragon id, all-(1,1) or seed-free
  pearls): every seed replays the same 2 games (side A wins Dilemma for base and cand alike). swap/autarky == autarky.
  Use maps/var/*_pv1/pv2 (same walls, other gaps) and gen/lesson for real sample size.
- 21:55 Slithery (8 games) 5/8 -> after fix below 3/8: 64-unit cap! Divers reached the tip at units 64/64 and could not
  split (dragon 311 r54, L5 died whole). Added PF_UNIT_RESERVE=6 (no dives / no inward-born children when fewer free
  slots). Slithery ledger: v29 pocket mill = 600-690 pocket eats but 700-770 length dying in pockets (net negative);
  PF 200-400 eats vs 180-370 deaths (about even). Slithery is a king race on a rich map (2600-3600 eats/team), so
  wins there follow the king, not the pockets. Autarky with reserve: 8/8, net/dive +1.03, total r200 118 v 42.
- 22:00 Added PF_PULL (off): nearest free ally L2-3 within PF_PULL_RANGE of a free stocked mouth (P>=PF_MIN_P on
  arrival, enemies<=allies there) gets -PF_PULL per BFS step to it.
- 22:25 PF=1 (reserve 6) unseen gen .487 (39/80), lesson .458 (22/48), pooled .477. Mechanism on pocket-bearing maps:
  lesson/pockets_a 0/4 (eliminated), pockets_b 0/4; gen pocket maps even. pockets_a/b = 32x16 melee near the unit cap
  with 5-deep (1,20)+(1,1)-tip pockets; v29 wins there because its L4 split-2 fires twice per dive (two L2 units per
  dive); PF made one bigger child -> fewer units -> fewer heads -> fewer dives late. Note most entries there are not
  gated at all (a 5-deep pocket is not "area < L+3" for L2) - same as v29.
- 22:30 PF_EARLY=1 (inside with certain food ahead, split k=min(L-2, L+Pc-4) now): pockets_a 0/4, pockets_b 2/4.
  PF_MIN_P=2.0/PF_SAFETY=0: no help (pockets_a 0/4).
- 22:50 PF_CHILD_MAX (children of at most N, repeated one split per turn at the tip; parent stays >=4 between):
  =2: pockets_a 1/4 (end total 105 v 106), pockets_b 2/4, autarky 4/4 (end 116 v 17). =3: same as off (0/4, 1/4).
  -> candidate config POCKET_FACTORY=1 PF_EARLY=1 PF_CHILD_MAX=2.
- 23:10 Candidate POCKET_FACTORY=1 PF_EARLY=1 PF_CHILD_MAX=2 vs v29 (seeds 8000-8002, 6 games/map): autarky 6/6
  (net/dive +1.02 v +0.27, stub3 0.5 v 45/g, pocket eats 248 v 179, total r200 98 v 53, end 113 v 27, base elim 3/6);
  dilemma 3/6 (deterministic, = base); devil 3/6 (PF never fires); slithery 3/6 (L4+ pocket deaths 6.7 v 16.5/g,
  net/dive -0.03 v -0.40, end total 208 v 142); var pearl variants 18/36 (autarky_pv1 4/6, pv2 3/6, dilemma_pv1 2/6,
  pv2 4/6, slithery_pv1 4/6, pv2 1/6).
- unseen: gen .487, lesson .479, pooled .484 (vs v29). PF is exactly inert on pocket-free maps (mirror-identical games
  checked on g2026_00-03), so the gen number is 0.5 on ~28 maps + the pocket maps. Gen pocket maps, 6 games each:
  31/66 = .47 (g12 5/6, g27/35/37/39 2/6 each: elimination/king-race maps where pockets are a minor food source;
  chaotic divergence). lesson pockets_a/b 3/8 with CHILD_MAX=2 (0/8 without it).
- 23:20 PF_PULL=0.5 on top: autarky 5/6 (dives 89 v 79/g, pocket eats 277), slithery 2/6, others equal -> keep 0.
- 23:25 flags-off bot == v29 re-verified (autarky, slithery, pockets_a identical mirrored games).
