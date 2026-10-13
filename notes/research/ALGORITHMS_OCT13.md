# Outside algorithms for four open problems (13 Oct 2026)

Web survey (search and page fetch only). No project data left the machine and no code from other teams in this
contest was looked at. Source status: **[read]** = page fetched and read; **[abs]** = abstract or search summary only
(PDFs could not be parsed in this session, so details from those are less certain). Lines marked *derived* are my own
reasoning from `notes/RULES_2026-10-01.md` and a read of `bot/main.cpp` / `bot/params.hpp`; no source backs them and
none of them has been run. Check them before building on them.

## Game facts the proposals lean on
- Lunge reach R(L) = ceil(L/4) + (L-2): L2 1, L3 2, L4 3, **L5 5**, L6 6, L7 7, L8 8, L9 10. Reach jumps at L=5 (second
  free step). Cheapest unit for a strike at d path steps, Lmin(d): d1 L2, d2 L3, d3 L4, d4-5 L5, d6 L6, d7 L7.
  A 7x7 view holds tiles up to Manhattan 6 away, so in open ground an L6 can strike any tile it sees and an L5 all but
  the four corners (*derived*).
- Each dragon is told its id, the team's living unit count (`units`) and the countdown of every tile in view.
- A head may not enter its own tail tile, and a pearl keeps the tail in place on the eating step. So own segment i
  (0 = head) of a body of length L0 can be entered on step s only if at least L0 - i of the steps 1..s-1 ate nothing
  (*derived*; counted in steps, because collisions are checked on every step of a sprint).
- Queens are ids 0 and 1, so they move first in a round; enemies see ids, so decoys cannot work.

---

## 1. Dispersion / coverage

### Techniques
1. **Ideal free distribution (IFD) with a marginal-value leaving rule.** Foragers settle so that the number in each
   patch matches the patch's input rate; nobody gains by moving. The rule that produces it is individual: stay in a
   patch, leave when your own intake drops below the habitat average (Charnov's marginal value theorem), and count
   travel time as pure loss. A simulation study reports that competitors who each use that leaving rule converge toward
   the IFD from a random start provided patches do not deplete faster than the foragers learn. Known failures:
   undermatching (rich patches under-used) and travel costs.
   Sources: "Ideal free distribution" https://en.wikipedia.org/wiki/Ideal_free_distribution [read];
   "Marginal value theorem" https://en.wikipedia.org/wiki/Marginal_value_theorem [abs]; Fauvergue et al. 2006
   https://w4.paca.inrae.fr/perso/wajnberg/pdf/fauvergue%20et%20al.%20(2006).pdf [abs].
2. **Search by agents that cannot talk (the ANTS problem).** k identical agents leave one nest. If each knows k to
   within a constant factor, purely independent randomised plans reach the optimal O(D + D^2/k) time; with no knowledge
   of k there is a logarithmic penalty. The simple "harmonic" plan draws a heavy-tailed distance, searches there and
   comes back. The point: silence costs little when agents know how many they are and deliberately decorrelate.
   Source: Feinerman, Korman, Lotker, Sereni, "Collaborative search on the plane without communication"
   https://arxiv.org/abs/1205.2170 [abs].
3. **Deterministic assignment from the agent's id.** A 2023 MIT Battlecode team (each robot is its own program, tiny
   shared memory) had carriers fan out in five directions chosen by id mod 5. Rendezvous hashing is the general
   form: every agent scores every site with a shared hash and takes the best; the weighted variant
   score = w / (-ln h) picks site j with probability proportional to w_j, with no messages.
   Sources: "Battlecode 2023 postmortem, no thoughts" https://battlecode.org/assets/files/postmortem-2023-no-thoughts.pdf
   [abs]; "Rendezvous hashing" https://en.wikipedia.org/wiki/Rendezvous_hashing [read].
4. **Several homes instead of one.** In ant-style robot foraging, spreading several nests over the area gave higher
   foraging rates, fewer robot collisions and less travel than one central nest.
   Source: Lu, Moses, Hecker, "A Scalable and Adaptable Multiple-Place Foraging Algorithm for Ant-Inspired Robot
   Swarms" https://arxiv.org/abs/1612.00480 [read, abstract].

### Fit to this game
- The "ideal" half of IFD holds: spawn rates are in the static map. The "free" half does not: 30 steps of travel is
  30 turns without food, so moves must be rare and triggered by intake, not by a clock.
- `units` gives every dragon k, so the fair share per unit (side's total spawn rate / units) is computable locally.
- The only shared medium is the pearl field itself. Pearls standing on spawn tiles in view, and their countdowns, are
  a readable depletion signal (foraging theory's "giving-up density"). That is the stigmergy available here.
- **Does not transfer:** Lloyd / Voronoi coverage control (Cortes et al., https://arxiv.org/abs/math/0212212 [abs])
  needs each agent to know its neighbours' positions every step; only a static, precomputed partition survives.
  Pheromone trails need a writable medium. Auctions need messages. Frontier exploration solves an unknown-map problem
  we do not have on known maps. Collaborative diffusion (Repenning,
  https://home.cs.colorado.edu/~ralex/papers/PDF/OOPSLA06antiobjects.pdf [abs]) needs a global scent field; its 7x7
  version is the crowd penalty the bot already has.
- **Why SCATTER raised coverage but not income** (*derived* from the code, a hypothesis): it is nomadic. A unit
  picks a tile, walks, rests 6 rounds and picks again; the weights ignore distance and ignore how many others drew the
  same area; nothing ties leaving to intake. Theory says the gain comes from residence plus leave-when-below-average.
- **Check before building:** is the gap dispersion or growth? If far patches hold many standing pearls at r100 it is
  dispersion. If they do not, the 34-against-60 unit count is the cause and the split policy is the place to look.

### Proposal 1A: home patch with a giving-up rule (replaces nomadic SCATTER)
```
once per known map (table, or first turn):
  patches P_1..P_K: farthest-point seeds over spawn tiles (static BFS distance); each spawn tile joins its nearest seed
  R_j = sum of 1/mean_gap, c_j = medoid, rad_j = radius;  SR = sum of R_j on our side of the spawn bisector (+ a band)
at birth, and whenever GIVE_UP fires (epoch += 1):
  for j != current:  w_j = R_j * exp(-dist(me, c_j) / TAU);   u = hash01(id, epoch, j)
  home = argmax_j  w_j / (-ln u)            # P(j) proportional to w_j; different ids land on different patches
travel:    pull HP_PULL per static step toward c_home; eat only food at most 1 step off the path
resident:  (dist(me, c_home) <= rad_home + HP_LEASH)  normal scoring, food outside the leash multiplied by HP_OUT
each turn: I = pearls eaten in the last HP_W rounds / HP_W;   F = SR / units          # fair share per unit
GIVE_UP if resident for >= HP_W rounds and I < HP_THETA * F
GIVE_UP at once if >= HP_CROWD allied heads in view, pearls standing on spawn tiles in view < HP_GUD,
                   and my id is the highest of those heads                            # one leaves, not all
```
Tune: K 16-32, TAU 10-30, HP_W 20, HP_THETA 0.5, HP_LEASH 3, HP_OUT 0.2, HP_CROWD 2, HP_GUD 1.
Risk: a wrong SR (enemy eats part of our side) makes F too high and everybody restless; clamp F or raise HP_W.

### Proposal 1B: bud outward at birth (small, independent of 1A)
```
on my first turn (birthRound == round, round > 0):
  q    = BUD_Q0 << (ctz(id) % 4)         # half the ids go Q0, a quarter 2*Q0, an eighth 4*Q0, an eighth 8*Q0
  lane = id % BUD_LANES                   # which outward exit to take when several rise equally
while age < BUD_TTL and Dhome(head) < Dhome(birth) + q:
  score(move) += BUD_PULL * (Dhome(next) - Dhome(head));  ties by lane;  food within 1 step of the path is still eaten
```
Dhome = static BFS distance from our queen's spawn; stay on our half before round BUD_HALF. Tune: BUD_Q0 4,
BUD_LANES 3-5, BUD_TTL 40. The heavy tail is the ANTS harmonic idea; the lanes are the Battlecode fan-out. The split
child already faces away from its parent, so this costs the parent nothing.

---

## 2. Self-trapping

### Techniques
1. **Eat only if a virtual copy can still reach its own tail.** Classic single-player solver: find the path to the
   food, move a copy of the snake along it, then require a path from the copy's head to its tail; otherwise follow the
   tail instead. Source: chuyangliu/snake, `docs/algorithms.md` https://github.com/chuyangliu/snake [abs].
2. **Bodies clear on a schedule.** A Battlesnake bot plans n moves ahead assuming every snake steps forward, "thus
   freeing its tail at each step", which generalises tail-following; flood fill is its last resort only. Official docs
   recommend flood fill to avoid enclosed spaces. Sources: okjuan/snake2017-2018 README
   https://github.com/okjuan/snake2017-2018 [read]; https://docs.battlesnake.com/guides/useful-algorithms [read].
3. **Tron space counting: articulation points, chambers, checkerboard.** The 2010 Google AI Challenge winner avoided
   cut vertices, evaluated a tree of chambers joined at articulation points (you can fill only the chambers along one
   branch), and bounded fillable space by colouring the board like a checkerboard: a path alternates colours, so
   surplus squares of one colour are wasted. Sources: a1k0n, "Google AI Challenge post-mortem"
   https://www.a1k0n.net/2010/03/04/google-ai-postmortem.html [read]; Janzert https://janzert.com/tron/ [read].
4. **Hamiltonian cycle with ordered shortcuts.** Follow a fixed cycle; a shortcut is legal only if it keeps the
   order tail < head along the cycle and leaves room for growth. Source: John Tapsell, "Nokia 6110 Part 3 - Algorithms"
   https://johnflux.com/2015/05/02/nokia-6110-part-3-algorithms/ [read].

### Fit to this game (*derived* unless a source is given)
- **Area is the wrong currency here.** A dragon must move and cannot reverse, so it survives only on a
  cycle. A one-wide dead end of any size is fatal to the head; "flood area >= length" from Battlesnake is not a test.
- **Battlesnake thresholds are one short.** Its engine removes the tail before checking collisions
  (https://docs.battlesnake.com/rules [read]), so a snake may enter its tail square. Here it may not: a body of L
  needs a cycle of L+1 tiles, and L+1+E if it eats E pearls on the lap.
- The Hamiltonian idea does not scale to a shared 64x64 board, but its invariant is exact at room scale: on a cycle
  of C tiles a body is safe iff L + E <= C - 1.
- `uboxPen` (in the bot since today) is a counting test: free tiles minus pearls against the wait for the exit
  segment. It assumes the head can visit every tile of the region in one path and end next to the exit, and it
  ignores loops inside the region. The Tron parity bound and an exact search fix both; regions are under 12 tiles.

### Proposal 2A: static turn capacity (zero run-time cost on known maps)
```
offline per map:
  core = 2-core of the tile graph: repeat { delete every tile with <= 1 open edge }     # portals and wrap are edges
  tiles outside core are dead-end trees: a head entering one away from the core never returns  -> price as a dive
  rooms = small leaf blocks of the block-cut tree of core (a block behind one door tile, <= 16 tiles)
  Cmax  = longest cycle through the door tile (w x h room, w,h >= 2: w*h if even, else w*h - 1; odd shapes: brute force)
  turnCap[room] = Cmax - 1
run time, before a step into room r:
  E = pearls I would eat inside (visible now, plus spawns due within Cmax rounds)
  if myLen + E > turnCap[r]:  enclosed;  value = E - 2 if (myLen + E >= 4 and units < cap) else -myLen
```
For the 2x2 room (Cmax 4): L + E <= 3. An L2 may eat one pearl and leave, an L3 may walk the lap but eat nothing, an
L4 cannot turn at all. Checked by hand against the rules for L2 eating one, L2 eating two and L3 eating one.

### Proposal 2B: exact test for small regions (bodies in the way, unseen maps)
```
enclosed(t):                                  # t = the tile I step onto now
  body = my body after the step, L0 = its length, rel(i) = L0 - i
  region = flood from t over free tiles, at most UB_EXACT (12) tiles; larger -> use the filter below
  dfs(head, ne, visited):                     # ne = steps so far that ate nothing
    for v in neighbours(head), v not in visited:
      if wall: continue
      if v is my segment i:      ok = (ne >= rel(i))
      elif v is another body:    ok = (steps so far + 1 > freeT[v])
      else:                      ok = true
      if ok and (v is OPEN or v is my segment): return ESCAPE     # OPEN = static core tile outside the region
      if ok and dfs(v, ne + (pearl[v] ? 0 : 1), visited + v) == ESCAPE: return ESCAPE
  return ENCLOSED if no branch escaped
filter for larger regions (replaces A in uboxPen):
  strip dead-end tiles of the region that do not touch an exit segment
  usable = 2*min(B, W) + (B > W ? 1 : 0)      # B = remaining tiles of the colour opposite to t, W = same colour as t
  enclosed if usable - p < L0 - iMax
```
Stepping onto my own released segment is an escape because from there I can follow my old trail tailward (the way I
came in), each tile of which was released earlier. Tune: UB_EXACT 12, and the existing UBOX_MIN_GAIN / UBOX_PEN.
`badsplit.py` already separates pockets (leaf-pruned tiles) from the core; 2A's new part is the turn capacity of small
rooms inside the core, which is where its "core" bad splits happen.

---

## 3. Protecting the queen, hunting theirs

### Techniques
1. **Search games and random search.** For a hider who cannot move on a tree, hiding at leaves is optimal and the
   choice among leaves must be randomised (Gal 1979). Koopman's random-search law gives the chance a target in area A
   is found by a searcher with sweep width W after path length vt: 1 - exp(-W v t / A).
   Sources: Alpern and Lidbetter, "Search for an Immobile Hider on a Binary Tree with Unreliable Locational
   Information" https://arxiv.org/abs/2303.13378 [read, abstract]; Alpern, "Find-and-fetch search on a tree"
   https://researchonline.lse.ac.uk/id/eprint/40090 [abs]; search-and-rescue summary of the law
   https://www.archive.asrc.net/ASRC-Operations/2012-08-30-Sweep-Width-POD-Effect-Ferguson.pdf [abs].
2. **Cops and robbers.** Three cops catch a visible robber on any planar graph, and one cop can guard a shortest
   path. Against an arbitrarily fast evader the number needed is the treewidth if he is visible and the pathwidth if
   he is not; an infinitely fast visible robber on an n x n grid needs n-1 or n cops.
   Sources: "Cop number" https://en.wikipedia.org/wiki/Cop_number [read]; "Pursuit-evasion"
   https://en.wikipedia.org/wiki/Pursuit%E2%80%93evasion [read]; Kinnersley and Townsend, "Catching an infinitely
   fast robber on a grid" https://arxiv.org/abs/2107.14193 [read].
3. **Cover sets and fixed roles.** Cover = the tiles a pursuer reaches before the target; pursuers move to enlarge
   the team's cover (Isaza et al., AIIDE 2008 https://ojs.aaai.org/index.php/AIIDE/article/view/18672 [abs]).
   Pac-Man's ghosts corner the player with no communication through fixed roles: one targets the player's tile, one
   targets four tiles ahead of him, one breaks off to its own corner when within eight tiles; none may reverse
   (The Pac-Man Dossier https://pacman.holenet.info/ [read]). For the evader, TrailMax plans against the pursuers'
   known positions (Moldenhauer and Sturtevant, IJCAI 2009 https://www.ijcai.org/Abstract/09/103 [abs]).
4. **King safety and perimeter defence.** Chess engines score a pawn shield next to the king, count "attack units"
   of pieces bearing on the king zone, and use "virtual mobility" (how many lines lead to the king)
   (https://www.chessprogramming.org/King_Safety [read]). Perimeter-defence work has defenders intercept intruders
   before a target region, including a two-defender pincer (Shishika and Kumar, "A Review of Multi Agent Perimeter
   Defense Games" https://link.springer.com/chapter/10.1007/978-3-030-64793-3_26 [abs]).

### Fit to this game (all *derived*)
- **Hiding buys time, not safety.** Put W = 7, v = 1, A = 4096 into Koopman: one random roamer finds a still target
  at 0.0017 per round. Three roamers give a mean of about 195 rounds, which is the r150-250 we observe. Surviving 500
  rounds at 80% by hiding alone needs a spot about eleven times quieter than average. P(death) = P(found) x
  P(killed once found), and the second factor is the one we can move a lot.
- **Do not wander.** In the same law a moving target raises relative speed and so the encounter rate. Loop in place.
- **Cornering is not the bottleneck when we hunt.** Cops-and-robbers bounds assume equal speed and a robber who may
  stand still. Our hunters are faster (lunge) and a length-2 queen can neither stop nor reverse, so one L5-6 unit that
  sees an unshielded queen kills her. What is hard is finding her and getting past bodies. The pathwidth bound is
  for a fast evader and a slow queen is easier, but 3-5 hunters with 7-wide views on a 64-wide map still cannot
  guarantee a find by sweeping, so use priors.
- **A ring of friendly bodies does not work in open ground.** Every dragon must move, so any ring has a moving gap,
  and a lunge enters a one-tile gap and strikes in the same turn. Worse, the tile in front of the queen must be free
  on her turn, and she moves first, so that tile lies open to every enemy acting after its last occupant left. A
  shield holds only where walls force the approach to that tile through a friendly body or make it longer than the
  attacker's reach. This is the chess "virtual mobility" count: free approach tiles of her head.
- Present settings worth a look: `QHUNT_MAXLEN 4` gives hunters a reach of at most 3, and escorts have no minimum
  length, so an L2-3 escort can only ram at 1-2 steps.

### Proposal 3A: lancer band for escorts and hunters
```
escorts and hunters hold length 5..6 (reach 5..6, nearly the whole 7x7):  below 5 eat first;  at 7+ split off the surplus
escort post: on the enemy side of the hideout, Chebyshev 3-4 from the queen's loop
             (sees an intruder 6-7 from her, one turn before it can see her)
  among such tiles prefer x with dist(x, door) <= dist(visible enemy head, door) - 1     # be first to the door
escort fire: any enemy head inside QESC_ZONE with a simulated path of <= R(myLen) steps -> strike, whatever its length
hunter list: mirror (map symmetry) of [our queen's spawn tile, then our own top hideouts];  start index = id % len
  walk to the candidate; when its loop tiles are in view and empty, go to the next                # probability / cost
her head seen but shielded: role = id % 3 -> 0 aim at her head; 1 aim 2 tiles ahead of her facing; 2 sit on her door
```
Tune: band 5-6 (try 5-7), post distance 3-4, list length 3-5.

### Proposal 3B: hideout score with a moat, and two queen rules
```
offline per map, for every 2x2 loop h in the static core on our side:
  moat(h)  = min over tiles u outside h's room with Chebyshev(u, h) <= 3 of pathdist(u, h)     # seen but not reached
  doors(h) = door tiles of h's room;  dfar(h) = static distance from the enemy spawn;  food7(h) = spawn rate within 7
  score = A*min(moat, 8) - B*(doors - 1) + C*dfar - D*food7 - E*traffic(h)        # traffic = the replay table
  keep the best 3; the queen picks one from her own round-0 entropy and names it in her beacon word
hidden queen, each turn:
  never eat if myLen + 1 > turnCap of my loop                                      # proposal 2A
  choose the move minimising (free neighbours of the new head, bar my neck, that a visible enemy head can reach in
  R(Lv) - 1 steps), then (free neighbours of the new head);  leave the loop only if every loop move fails the first test
```
A moat of 7 means a scout that sees her needs length 7 to strike on sight; anything shorter has to walk round, which
is the turn the escorts need. Randomising among three matters because all battles are public.

---

## 4. Lunges: avoiding and exploiting

### Techniques
1. **Influence and threat maps.** Stamp a threat template round each enemy and a proximity template round each
   friend, combine them, and read off safe cells, retreat cells, or where to put a tough unit between enemies and a
   weak ally. Sources: Champandard, "The Core Mechanics of Influence Mapping"
   https://gamedev.net/tutorials/programming/artificial-intelligence/the-core-mechanics-of-influence-mapping-r2799
   [abs]; Dave Mark, "Modular Tactical Influence Maps", Game AI Pro 2 ch. 30
   https://www.gameaipro.com/GameAIPro2/GameAIPro2_Chapter30_Modular_Tactical_Influence_Maps.pdf [abs].
2. **Occupancy maps for enemies that left view.** Probability starts at the last seen position, spreads to
   neighbours each tick, and is zeroed wherever the agent now sees nothing. A StarCraft bot did the same with
   particles and gained about 10%. Sources: Isla, "Third Eye Crime: Building a Stealth Game Around Occupancy Maps"
   https://ojs.aaai.org/index.php/AIIDE/article/view/12663 [abs]; Weber, Mateas, Jhala, "A Particle Model for State
   Estimation in Real-Time Strategy Games" https://ojs.aaai.org/index.php/AIIDE/article/view/12424 [abs].
3. **Graded head-danger buckets.** A Battlesnake bot prefers paths avoiding tiles within 2 of another head, relaxes
   to adjacent tiles, then drops the rule; others sort moves into safe and risky. Source: okjuan README (above) [read].
4. **Static exchange evaluation.** To judge a trade on one square, capture with the least valuable attacker first,
   and let either side stand pat when continuing loses material.
   Source: https://www.chessprogramming.org/Static_Exchange_Evaluation [read].

### Fit to this game (all *derived*)
- **A targeted lunge needs our head tile.** The attacker must have our head (or our neck with its direction) inside
  its own 7x7 when its turn starts. Views are symmetric, so either it was already in our view on our last turn, and we
  had one warning turn, or our own move carried the head into its window. The second case is the "outside our view
  when we moved" death, and we cause it.
- **Fog table.** After advancing k steps the nearest tile that was outside the turn-start view lies 4-k steps ahead.
  k=1: only an unseen L4+ dead ahead (L5+ off-centre) can strike. k=2: L3+. k=3: any unit. Dragons of 8+ have two or
  more free steps, and using them toward unseen ground is what exposes them.
- A global influence map cannot be built by one process. What fits: the 7x7 view, static priors (which side of the
  spawn bisector), and a three-round memory. A particle filter is overkill; one growing ball per remembered head.
- Check `KR_CAP` (4 in params): inside the view an L5 reaches 5 and an L6 reaches 6.
- A strike made at long range arrives short (paid steps), so it leaves few of our pearls; the victim leaves
  ceil(Lv/2). Who is nearer to the wreck decides the real exchange, which is SEE's recapture step.

### Proposal 4A: fog discipline for long dragons (length >= FOG_MINLEN)
```
mem: every enemy head seen in the last FOG_MEM rounds and not visible now: (tile p, visible length Lv, age a)
front(t) = dEnemySpawn(t) - dOwnSpawn(t)  (static, large = deep in our side)
prior(t) = FOG_PHOME if front(t) > FOG_BAND else FOG_PFRONT   (+ FOG_PE if my sonar echo on that side hit an enemy part)
for a candidate move ending with the head on h:
  fringe = tiles within Chebyshev 3 of h that were not in my turn-start view
  risk = sum over free n in fringe:  prior(n) * Plen( Lmin(pathdist(n, h)) )      # Plen(L) = share of enemy units >= L
       + sum over mem:  GAMMA^a  if pathdist(p, h) <= R(Lv) + a*ceil(Lv/4)
  open = free neighbours of h, bar my neck
  score -= FOG_W * risk * (1 + FOG_OPEN*open) * myLen
hard rule: where front(h) <= FOG_BAND take one step per turn, unless retreating or an allied body covers the fringe
warning turn (visible enemy head with pathdist <= R(Lv) + 1): prefer an end tile with pathdist > R(Lv);
  else one with head and neck both outside its 7x7;  else one with open == 0
```
Tune: FOG_MINLEN 8, FOG_MEM 3, GAMMA 0.6, FOG_PHOME/PFRONT/PE, FOG_BAND, FOG_W, FOG_OPEN; Plen from replays. Start with
the hard rule alone: it is one line and its cost (slower long units) is easy to see in the economy numbers. The whole
proposal assumes attackers need sight of the head and that a view is not refreshed between the steps of one move.

### Proposal 4B: least valuable lancer (the reverse)
```
target e = enemy head in view, visible length Lv;  value = Lv (+ bonus for their queen or their longest seen)
  can = simulated path to its head <= R(myLen)
  fire iff can and value >= RHO*myLen + C0
       and no visible ally a with id > mine (still to move this round), len(a) < myLen, pathdist(a, e) <= R(len(a))
       and (allied heads in view >= enemy heads in view  or  value >= 2*myLen)        # who eats the wreck
pickets: units with id % PK_MOD == PK_R hold length 5..6 and keep 3-5 steps on the enemy side (front gradient) of the
         nearest allied body of length >= 8 in view
```
Tune: RHO 1.5, C0 0, PK_MOD 6. This extends `KING_KILL` (length <= 7 against 9+ visible) with a shooter choice and a
recapture test; pickets double as the screen that makes 4A's "allied body covers the fringe" true.

---

## Ranked shortlist and cheap tests

The order is a judgement: nothing in this file was run. The A/B scorer failed an A/A check on 9 Oct, so each test
below names a mechanism counter, not a win rate. All tools run from the project root.

1. **3A lancer band for escorts and hunters.** Mostly constants (`QHUNT_MAXLEN`, an escort minimum), aimed at the
   event that decides games. Test: local series on Thermopylae, Metro, Athena against km14. Read
   `tools/analysis/oct13/qsurv.py RUN NAME` (queens alive at the end, median death round, both sides) and
   `qkiller.py REPLAY` (the killer's length and the steps of its last move); add one counter: intruders killed inside
   the escort zone before they strike.
2. **4A fog discipline, hard rule first.** Test: `tools/analysis/oct13/bigdeaths.py` for length lost to lunges per
   game, ours against theirs, plus one new column: was the killer outside our turn-start view? Measure that share on
   today's replays first. If it is already small, 4A is the wrong fix and the warning-turn response (`KREACH`,
   `KR_CAP`) is the place to look; if it is large, it should fall toward zero. Watch length at r200 in `econ.py`.
3. **2A + 2B turn capacity and the exact test.** Test without any game: feed the pre-split positions that
   `badsplit.py` already finds to `uboxPen` and to the exact search and tabulate agreement. Then count bad splits per
   game on Slithery Fight, Maelstrom, Australia.
4. **1A home patch with a giving-up rule.** Test on Around UNSW: `spread.py` (tiles stood on by r100) and `econ.py`
   (units at r100, length at r200), plus two new counters: share of unit-rounds spent travelling, and pearls standing
   in the far patches at r100. Expect travel share to fall against SCATTER while coverage holds.
5. **1B bud outward.** Same counters, same map, flag on alone. If the standing-pearl check in section 1 says the far
   field is already eaten, drop 1A and 1B and look at the split policy instead.

Not on the list: 3B (needs offline work per map and the gain depends on escorts existing first) and 4B (the gain
depends on how often a cheaper ally is actually in view; measure that in replays before coding it).
