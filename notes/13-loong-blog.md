# 13. "The Loong Game" blog: what to steal (28 Sep 2026)

Source: https://over-yonder.tech/games/loong/ (Kieran Hannigan, over|yonder, also competing). Posts 0-18.
Repo (read-only shallow clone): `reference/loong/` = github.com/overyonder/the-loong-game.
Markdown sources of every post: `reference/loong/blog/NN-*.md` (easier to read than the site).
**Not in the public repo:** the example bots (`examples/` is referenced but not published) and their private
competition bot. What IS there: `harness/` (mapgen, verdict, ladder, rating, round robin, Zig judge), `replays/`
(decoder + Odin viewer), `just/*.just` recipes. No LICENSE file, so treat it as reference; for our private
testing we can run it in place or re-implement.

Their bots are Nim -> C, but their architecture/eval lessons are language-independent.

---

## 1. Post-by-post: key ideas and measured results

**0 The Loong Game / 1 Wishlist.** Organisers said on Discord: *Sprint, Qualifier and Grand Final maps are all
unseen; don't tune to ladder maps.* Each new submission resets K factor (bigger rating swings). Ladder once served
a 16x8 map "Small" although docs say >=10 per side; his bot refused maps <10 and died in round 0 on every dragon.
Stats: 17/26 wins between two identical random bots happens ~8% of the time; telling 60% from 50% takes ~150 games.

**3 Evaluation harness.** Round robin: every pair, every map, both sides (turn order = id order makes sides
unequal even on symmetric maps), N seeds. Seed = crc32(map_name:index) so every pairing/side meets the same
pearl schedule. Cache seeded sandbox games keyed by hash(bots, map, seed, toolkit). **Crashes/timeouts/
NoValidAction/missing replay go in an "errors" column, never counted as losses** (a crash on 1 map in 10 looks
like "slightly worse" otherwise).

**4 Better, worse or undecided (paired verdict)** - `harness/verdict.py`, `just verdict`.
- Every game played twice: candidate vs opponent on (map, side, seed), then baseline in the same seat with the same
  (map, side, seed). Seeded games are deterministic, so if the change never fires both games are identical and
  cancel. Only changed pairs count.
- Weighting: each bot writes the name of the behaviour that chose its move as its INDICATOR every turn; the
  verdict weights each changed pair by the fraction of candidate turns where the changed behaviour was active.
  Test = sign-flip permutation (200k trials): p(random signs on the weighted changes sum >= observed). better if
  p<0.05, worse if the mirror p<0.05, else undecided.
- Opponent set = the baseline itself + the two starter bots (C and Py random walkers). **A candidate that loses
  more games to starters than the baseline did is never called better**, and every such game is listed as a bug.
- Reports median rounds-to-win per version and flags unusually short wins (flukes).
- Keeps numbered snapshots; candidates must also beat the last few (rock-paper-scissors cycle guard).
- Sanity checks: flood-fill vs random: 56 gained / 2 dropped / 46 unchanged of 104 -> better. C vs Py port of the
  same bot: 104/104 identical -> undecided (exact null).
- **Pearl chasing** (flood fill + "prefer the move nearest a visible pearl when room is plentiful"): 18 gained /
  36 dropped (p=0.023, worse); vs starters lost 51 games the plain bot won, won back 3. Wins faster (163 vs 203
  rounds median) but dies more.

**5 Maps nobody has seen** - `harness/mapgen.py`, `just mapgen --count 20 --seed 2026`. Details in section 2.
Result: flood-fill vs starter on generated maps starts **losing to a random bot**, mostly by running into its own
body. Cause: flood fill treats a portal like an ordinary open edge; the head actually exits at the partner edge
anywhere on the map, sometimes onto its own body. 9 bundled maps have portals and the bug almost never showed there.

**6 A ladder of our own** - `harness/ladder.py`, `harness/rating.py`. Offline Bradley-Terry fit by Newton's
method over ALL games (order-independent), with one imaginary draw vs an average bot as a prior (so 100% records
get finite ratings). Rating = 1500 + 400*log10(strength), pool mean 1500. Game-by-game Elo compresses lopsided
records: a bot scoring 98/100 sat at 1916 under fixed-K Elo vs 2270 fitted. Schedule in rounds (each bot <=1 game
per round), sides alternate, map changes after each 2-sided cycle, resumable via hashes. Always print the
head-to-head table to spot cycles (lower-rated bot with a winning record vs a higher one).

**7/8 Everyone else's games / Reading a replay.** Public replays fetched through the site's own pages
(`/battles?sort=rating`, `/api/matches/<id>/replay`, gzipped Cap'n Proto). Decoder rebuilds board per round
and each dragon's 7x7 view. (We already have notes/tools/replay_decode.py etc.)

**9 Through one dragon's eyes (why chasing pearls kills).** Debug by asking "what could this dragon see?".
Pearl chaser: median longest dragon 33.5 vs 13.5; median length of self-hitters 32 vs 13.5. **A third of its
self-hits were dragons longer than 49 segments (can't fit in their own window)**; two failure types: (a) moved
south through a portal beside its head and landed on its own body; (b) head wound in a knot of own body on
big_empty (no portals) and the in-window flood fill had nothing to choose with. Lesson: a long dragon must track
its body outside the window. (Our bot already tracks its full body and does a 12-move self-sim look-ahead;
DFS_EATS fixed the eat-aware part. Good.)

**10 Where the points go / 15 Counting room faster.** Room count is the only part of a turn that grows with
look-ahead. Bitboard flood fill of the 7x7 window (49 bits in a u64; N = >>7, E = <<1, masks per direction) +
SIMD mask building: 116k -> 1.75k points (66x). Median turn only 3.2M -> 3.0M because parsing/output dominate.
Meter: 1 pt arithmetic, 2 loads/stores/branches/SIMD, 3 div; no cache/pipeline effects - only instruction count
matters. (We use 5-9M of 100M: compute is not our bottleneck.)

**11 The shape of the problem.** Don't grind: an evolutionary weight optimiser's top 5 bots won only 1-3 of 11
games vs a random bot (overfit to training opponents/maps). >20 teams hardcoded pearl schedules and broke when
seeding went random on 25 Sep. Architecture: a *repertoire* of behaviour modules (each owns eligibility, value,
execution, plus one factory per architecture), assembled into state machine / utility / HTN / BDI bots. Hard
constraints (fatal moves) filtered BEFORE scoring. First strategy bot = HSM with Evade (enemy head within 2:
room + 4*gap) and Roam (max room). **Movement drops steps into kelp, bodies, next-to-enemy-head, and portals it
can't see through; portals only as a last resort.** Verdict vs flood fill: 77 gained / 50 dropped of 264 (better,
p~3%). Bundled maps 21-25 (level), generated maps **56-25**; self-hits on generated maps **74 -> 23**. I.e. the
whole gain is unseen-map robustness from "don't step through unseen portals".

**12 Roles** (details in section 3). Champion/kamikaze/worker by sonar-heard lengths. Split-at-10-off-3 creating
kamikazes was the big win (39-4 of 132). Self-echo fix 26-14. Friendly head-ons 382 vs 78 enemy; friendly berth
undecided/leaning worse (19-29).

**13 Tactics** (details in section 4). Coil + forage 80-45 of 264 (p=0.0036) but undecided overall due to 3 starter
losses; every sacrifice/feeding variant worse.

**14 Sonar.** Up to 4 u64/turn, one per direction; ray wraps, passes portals, stops at kelp or first living
segment incl. sender's own body; lost after W+H steps; the ray opposite the facing starts from the TAIL. PROTOCOL 3
echo counts are totals over all rays (kelp, ally body, ally head, enemy body, enemy head) - direction ambiguous.
Ideas listed: fingerprinting opponents by message shape, echolocation, misinformation (validate what you hear
against what you see), multi-turn messages reassembled by one listener.

**16 The machine inside the judge.** Their Zig judge = same engine wasm + same metering, 4x faster. **Race in the
official toolkit sandbox (1.1.0 and 1.2.2) occasionally kills a freshly split child with "no valid action"**
(2 of 384 games on busy machines): `_write()` notes park count and feeds stdin without holding the pipe lock.
Fix: wrap both lines in `with self._stdin.cv:`. Relevance to us: we split at 4 constantly and run 6-14 jobs in
parallel, so some local child NoValidAction deaths are harness noise, not bot bugs. Don't chase them.

**17/18** AWS Spot batch runner ($17.51 for tens of thousands of games), columnar game data. Not needed.

---

## 2. Their unseen-map generator (reimplementable; code at `reference/loong/harness/mapgen.py`, 564 lines, stdlib only)

**Run it as-is** (verified 28 Sep: 20 maps generated in scratchpad and one played through `unswbc run` with our bot):
```sh
PYTHONPATH=reference/loong python3 -c "
import random; from harness.mapgen import generate_map, serialise_map
g = random.Random(2026)
for n in range(1, 41):
    m = generate_map(g, f'gen_2026_{n:02d}')
    open(f'maps/gen/gen_2026_{n:02d}.map', 'w').write(serialise_map(m))"
```
(`tools/arena.py` builds `ROOT/maps/<name>.map`, so `--maps gen/gen_2026_01,...` works if files sit in `maps/gen/`.)
Output uses the official format (edge index = (2y or 2y+1)*(W+1)+x, same as notes/02 section 10).

Recipe (`generate_map`, one retry loop - any failed check discards the whole map):
1. **Size**: width from bands (10-20 | 21-40 | 41-64) weights 35/40/25; aspect from
   {1,1,1,0.5,0.6,0.75,1.4,0.33,0.16}; height = clamp(round(w*aspect), 8, 64). So 8-high strips happen.
2. **Symmetry**: x (mirror y), y (mirror x), xy (180 rotation, double weight). 20% of maps omit the SYMMETRY line
   (geometry symmetric but pearl countdowns NOT shared).
3. **Kelp**: 1-3 styles from {segments, rooms, pillars, border, open, maze, divide}; every edge added together
   with `mirror_edge` (wrap-aware: N edge mirrored in y maps y -> (H-y)%H, W edge mirrored in x maps x -> (W-x)%W).
   - segments: 2..W*H/40 straight runs of length 2..min(W,H)/3.
   - rooms: grid of rooms size 6..min/2 with doors 1-3 wide.
   - pillars: 2..W*H/120 hollow rectangles 1-4 x 1-4.
   - border: wall around x=0/y=0 lines, sometimes with a gap every 5 or 8.
   - maze: DFS maze on cells of 2-4 tiles, then 1/4-1/10 of walls removed for loops.
   - divide: wall across the middle (and the wrap seam) with 1-3 gaps (like The Great Divide).
   Reject if kelp > 35% of edges (60% for maze).
4. **Portals**: pair count from {0,0,1,2,3,4,6} capped at W*H/80. Pair = 2 random same-orientation edges; their
   mirror images form a second pair (unless the pair is its own mirror); no portal on the symmetry line, none on
   kelp/existing portal. Crossing keeps heading and exits from the partner edge.
5. **Playable**: largest connected component (BFS following portals) must be >= 60% of tiles (35% with maze).
6. **Dragons**: per team 1-2 (area<400), 1-4 (<1600), 1-6. Lengths: 50% equal {3,3,4,4,5,6}; 35% "flagship"
   (one of {9,11,14,14,16,20,30,80} capped at playable_half/3, rest length 3); 15% mixed {3,5,7,8,12,16}.
   Team A in its half (1 <= coord < size/2-1), bodies straight with p=0.7, no body across kelp/portal edge;
   team B = mirror; every A segment >= 4 (Chebyshev, wrapped) from every B segment; own dragons >= 2 apart; head
   needs >= 2 free exits.
7. **Pearls** (TILE min max): layout from {spread x3, starving, centre, fields}.
   - spread: one base range from {(1,100),(1,200),(1,250),(1,385),(1,600),(1,750),(1,1000),(1,3849),(8,20),(10,20),
     (20,200)}; 0/30/50/75% barren clusters grown from seeds; 60% chance of 1-4 hotspot blocks (1-3 square) with
     {(1,1),(1,50),(5,30),(20,50),(1,100)}; 25% chance of late blocks {(240,320),(320,400),(150,250),(480,490)}.
   - starving: all barren except 0-6 slow tiles (late ranges or (1,2559)).
   - centre: a strip of half-width size/10..size/6 around the middle, 60% of tiles with {(1,1),(1,5),(1,10),(150,250)}.
   - fields: centre + one private block per side ({(1,1),(1,5),(1,10),(480,490)}), like Autarky.
   All pearl choices mirrored.

Gaps vs our notes/02 knowledge worth adding if we write our own: UNIT_LIMIT line (they never set it), dragons
starting in portal-adjacent spots (they forbid body across portals), asymmetric SYMMETRY-less countdowns
(they do 20%). Their own finding: generated maps expose portal and small-map bugs the bundled maps hide.

---

## 3. Role architecture and sonar role election

- Roles are parent states in a hierarchical state machine re-entered from the root every turn; children are the
  behaviours the role may use (first child whose guard holds takes the turn). Reflexes (split, strike) run before
  children. Movement layer filters fatal moves first; only Hunt may step next to an enemy head.
  - **Champion**: my length >= longest teammate length heard in the last 12 turns. Children: Split reflex
    (at length 10 split off 3), Evade (within 2), Coil (tactics bot), Roam.
  - **Kamikaze**: length <= 3 and some longer teammate heard. Hunt: objective min(room,6) - 10*gap to nearest
    enemy head; strike reflex drives into an adjacent enemy head.
  - **Worker / Feeder**: everyone else: Evade + Roam (roles bot) or Evade + Forage (tactics bot).
- **Election = no election**: every dragon broadcasts every turn; each picks its own role from what it heard. A
  split child hears the parent's length announcement on its first turn and becomes kamikaze by itself.
- Message v1 (roles bot): `[32-bit tag 0x4C4F4F4E "LOON"][16-bit sender id][4-bit role][12-bit length]`.
  Message v2 (tactics bot): `[16 tag][16 id][4 role][12 length][8 x][8 y]`. Decoder: reject wrong tag AND
  reject sender id == my id.
- **Self-echo bug**: rays wrap the torus; on Arena (11 wide) a dragon's own ray came back and hit its own body; it
  heard its pre-split length 13 while now 10 and demoted itself to Worker for 12 turns. Fix (ignore own id) won
  26-14. (We already drop own id for king messages; warn messages have no id but are harmless.)
- Measured (vs first bot, 132 paired games): first try (champion berth 3) 12-26 worse; no kamikazes 10-25 worse;
  no kamikaze + berth 2: 0 changed (sonar itself costs nothing); berth 2: 3-4 undecided (kamikaze turns only 1.7%
  of dragon-turns, role rarely active); **champion splits at 10 (child 3 = kamikaze): 39-4 better**; split but
  children are workers: 35-8 better (more dragons helps by itself); kamikaze-vs-worker children head to head
  weighted by kamikaze turns: 30-12. Ladder: roles bot 1739 vs first bot 1547.
- Friendly fire after splitting: 382 own-vs-own head-ons vs 78 with enemies. Giving friendly heads the same berth:
  19-29, lost 5 extra to starters -> undecided/worse. (Same shape as our portal-penalty experience: blanket
  caution costs more than it saves; our PORTAL_WARN sonar is the targeted version.)

---

## 4. Coiling and feeding: what worked vs didn't (vs roles bot, weighted by active turns)

| Variant | Gained-Dropped (of 132 unless noted) | Verdict |
|---|---|---|
| Coil only (champion hugs own body when no enemy head within 3) | 31-25 | undecided |
| Coil + forage + sacrifice (Deliver) | 24-42 | worse |
| Forage + sacrifice, no coil | 16-40 | worse |
| Sacrifice without foraging | 25-39 | worse |
| Sacrifice only when champion head within 2 | 24-41 | worse |
| Forage only, no coil | 32-21 | undecided |
| **Coil + forage, 4 seeds (264)** | **80-45, p=0.0036** | better head-to-head, but undecided overall: 3 extra losses to starters |

- Coil objective: +100 eat pearl, +20 per own segment adjacent to the step **only if the step leaves >= 10 tiles of
  room**, + room. Produces tight 3x3 spirals.
- Forage: 4*min(room,10) - 6*dist to nearest visible pearl. Deliver: after length 6, +8 per step toward champion's
  last heard position; reflex drives into the champion's BODY when its head is within 2 (only mover dies; half the
  feeder's segments become pearls next to the champion).
- Why sacrifice failed (their guess): pearls dropped along the champion's body/tail, champion never comes back
  for them. **Our feeding is different and did work** (feed vs no feed 35-25, Portals 6/6; KING_V2 +): our feeders
  die 1-2 tiles AHEAD of the king's head so it walks over the pearls. Keep ours; their result is evidence that
  "die into the body" is the wrong geometry.
- Coil failure modes on starters: two games on a generated 40x40 map (coiled champion starved waiting for food on
  a big sparse board, lost on length at r500) and one on a 16x10 map (both dragons died head-on at r22).
  Conclusion: coil only when the board is crowded; gate by map size / pearl density.
- Ladder of their versions (990 games, 33 maps): tactics 1791, roles 1739, first 1547, room-c 1485,
  room-pearls 1377, starter-c 1060. No cycles.

---

## 5. Evaluation methodology to copy

1. **Held-out unseen maps**: a fixed generated set (e.g. 40 maps, seed 2026) + a second fresh seed for final
   confirmation, never tuned on. Report bundled vs generated separately (their first bot: level on bundled,
   +31 net on generated).
2. **Paired candidate/baseline games** on identical (map, side, seed, opponent); count only changed pairs.
   Our pool.py compares candidate and baseline win rates from separate games; pairing removes most variance and
   makes flag-gated changes (that fire rarely) measurable with far fewer games.
3. **Activation weighting**: log which behaviour/flag chose the move (INDICATOR or BOTDBG) and weight pairs by
   the fraction of turns it fired. Sign-flip permutation test (their `sign_flip_p_values`, 20 lines).
4. **Weak-bot guard**: always include the starter (random) bot; any new loss to it is a bug, listed by
   map+seed, and blocks acceptance.
5. **Errors never counted as losses**; separate column. Ignore fresh-child NoValidAction from the sandbox race.
6. **Snapshots + offline Bradley-Terry ladder** of v8..v13+ to catch cycles; head-to-head table.
7. Median rounds-to-win and short-win flags.

---

## 6. Ranked additive changes for our bot (unseen-map robustness first)

All behind new flags in `bot/params.hpp`, default 0 until they pass a paired test on generated maps
AND a regression check on the 10 ranked maps. Nothing existing is removed.

1. **Unseen-map test bed (tools only, do first).** New `tools/mapgen.py` = thin wrapper that imports
   `reference/loong/harness/mapgen.py` (or a copy) and writes `maps/gen/*.map` (40 maps seed 2026, 40 seed 2027
   held out). New `tools/verdict.py` wrapping `arena.py`: candidate and baseline each vs {baseline, v8, starter}
   on the same (map, side, seed), pair them, sign-flip p-value, list starter losses. First measurement:
   v13 vs v13 `-DNO_KNOWN_MAPS=1` on ranked maps, and v13 vs starter on gen maps (any loss = bug list).

2. **`UNK_PORTAL_ESCAPE` - unseen portal as last resort** (`decide()`, the `if (bestD < 0)` all-lethal fallback,
   ~line 1838). Today an unknown portal edge has `step()==-1` (treated as kelp) so it ranks 1, *below* rank 2
   (certain death into a body). Record portal edges seen in `observeEdges()` (new `std::vector<char> unkPortal`
   filled from `portalObs`) and rank them above certain death (and above the reverse-split check when
   `tailHasExit` fails). Loong's movement does exactly this ("unseen portal only when nothing else is left") and it
   was their entire generated-map gain (self-hits 74->23). Cheap, can only fire when we'd otherwise die.

3. **`INFER_SYM` - symmetry inference on unknown maps** (new `inferSymmetry()` in the map-knowledge struct,
   called from `observeEdges()` when `!known`; sym is currently -1 on unknown maps). Keep 3 hypotheses {x, y, xy};
   refute one when an observed edge's kind differs from its already-observed mirror edge (use Loong's
   `mirror_edge` formulas), or when visible `pearlIn` countdowns at t and mirror(t) disagree after round
   adjustment (shared countdowns only if SYMMETRY declared - so only use countdowns as positive evidence, never
   to refute). Prior from start: original dragons at round 0 see their own team's start; enemy start = mirror.
   When one hypothesis survives: set `sym`, write mirrored kelp/open edges into `nxt` (doubles map knowledge),
   and mirror pearl-gap memory (`LEARN_GAPS` path). Mirror learned portal pairs too.

4. **`SPLIT_HANDOFF` - tell the child what the parent knows** (`emitSonar()` + `readMessages()`). Engine order
   (notes/02 section 6): parent splits, then (if alive) casts sonars; the ray opposite its facing leaves from its
   new tail pointing away from the body, i.e. into the child's body; the child has a higher id and acts later the
   SAME round, reading its inbox on its very first turn. Send on that ray a tagged message: known-map index
   (skips re-identification and the look-alike problem), inferred symmetry, and on later turns learned portal
   pairs (2 x 13-bit canonical edges + portal id fits in 64 bits with a 16-bit tag). Verify the geometry with a
   BOTDBG run first. On unknown maps this directly fixes "newly split dragons know nothing".

5. **`MAP_GOSSIP` - swarm-wide map facts** (same functions). Non-king, non-warning dragons spend one ray per turn
   (prefer the tail ray) on a rotating fact: portal pair, symmetry, map index. Receivers apply only facts
   consistent with their own vision (Loong post 14: messages are unauthenticated; enemies hear them too; use tag
   + our existing checksum + drop own id). Makes `LEARN_PORTALS` useful to dragons that never saw both ends.

6. **`UNK_PORTAL_BLIND` - learned portals for planning, cautious for stepping** (`observeEdges()` and move
   scoring). LEARN_PORTALS alone scored 0.45; likely the Loong failure mode: stepping blind onto an unseen exit
   (own body/ally). Use learned links in BFS/area/pearl scoring, but add a penalty for the immediate step through
   a portal whose exit tile's neighbourhood was not seen in the last k rounds and no PORTAL_WARN was received.
   Gate on `!known` only - on known maps the portal penalties already tested negative.

7. **`maps/unknown.hpp` module** (`unknownOverride()/unknownScore()` hooked in `mapOverride()/mapScore()` for
   `mapKey()==-1`, plus an `applyMapParams("unknown")` param set). Tune generic params ONLY on gen maps:
   KING_SEED_ROUND/KS scaled by area, SPLIT_STOP_ROUND, CROWD_PENALTY (our per-map crowd=3 helped 4 big maps),
   RAM_GUARD. Keeps per-map modules untouched and gives unseen maps their own tuned defaults.

8. **`SMALL_MAP_SAFE` - odd-size robustness** (checks, not strategy): run the starter guard on gen maps with
   H=8..10 and 0.16-aspect strips (ladder already served 16x8). 7x7 window on an 8-tall map nearly wraps onto
   itself; confirm no index/wrap assumptions break, unit-limit handling, splitting on 1-2 dragon maps.

9. **`KING_COIL` (lower priority)** - in king scoring, +w per own segment adjacent to the step when the step
   leaves >= 10 tiles of room and no enemy head within 3; **only on crowded/small boards** (area < ~1000 or
   many enemies seen) since coil starved on 40x40. Their coil+forage was their best tactic (80-45).

10. **Eval hygiene** - in `tools/deaths.py`, flag NoValidAction deaths of dragons on their first turn as
    probable sandbox race (Loong post 16), not bot bugs.

Do NOT copy: pearl-chasing without body tracking (we have it), sacrifice-into-body feeding (always worse for them),
blanket friendly-head berth (undecided/worse for them, and our PORTAL_* blanket penalties also lost).
