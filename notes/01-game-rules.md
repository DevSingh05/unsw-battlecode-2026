# UNSW Battlecode 2026: Game Rules Reference

Source: https://game.battlecode.au/docs/{overview, structure, map-info, pearls, kelp-and-portals, vision, movement, splitting, sonar, death}, fetched 2026-09-26.
Cross-checked against /docs/execution-order, /docs/protocol, /docs/protocol-upgrade, /docs/map-files and /docs/timeouts (read from the site's embedded search index, which holds the full text of every docs page), and against the C/C++/Raw code tabs and the animated demo maps in the page JS chunks (`/_app/immutable/nodes/*.js`).
Raw HTML, stripped text and JS chunks are in the session scratchpad at `.../scratchpad/raw/` (`search_index.txt` has every docs section).

Where a rules page and the Execution Order page disagree, both versions are recorded below. The Execution Order page is the more precise, engine-level description.

---

## 1. Setting and win condition

- Each team controls "leviathan" dragons (snake-like). Pearls make a dragon longer. At the end, your **longest** dragon is what counts.
- **Game length: at most 500 rounds.**
- **Outcomes:** A wins, B wins, or draw.
  - A team is **eliminated** when all of its dragons are dead. The game ends immediately (checked at the **end of the round**, per Execution Order) once any team is eliminated.
  - Exactly one team eliminated: the other team wins.
  - Both teams eliminated **in the same round**: draw.
  - Otherwise, after round 500, tiebreaks in order:
    1. Team with the **longest living dragon** (the single maximum length).
    2. Team with the **greatest total length across all its dragons** (presumably living ones only).
    3. Draw.
- A ranked battle is 5 games on random maps. You keep the same colour for every game in the battle (from Game Format; outside this area).

## 2. Team and program model

- **Up to 64 living dragons per team** (`UNIT_LIMIT`, default 64, sent in the init block).
- Each team writes **one program**. **Every dragon runs its own separate process/instance** of it. There is no shared memory. The only way dragons talk to each other is **sonar**.
- A dragon's process persists across its turns, so per-dragon memory lasts until the dragon dies or its process is restarted (timeout or crash). A restarted process gets a fresh init block.
- Split children get a **brand-new process with no memory of the parent**. They inherit only the protocol version.
- Compute: the Overview says "~25 ms per turn". The judge actually meters **CPU points: 100 million points per dragon per turn**, with 48 MB memory and 1 thread. Python parsing one round costs about 10M points. A 32×32 flood fill costs about 19M points in Python and about 0.3M in C++. Each stdout write costs 2.5M points plus 4,000 per byte. Local `unswbc run` only has a 10 s wall clock, so use `--sandbox` to test budgets. (Full details are in /docs/timeouts.)
- Games are deterministic given the seed. RNG is seeded per dragon per game.

## 3. Rounds, turns, execution order

Each round runs in this order:
1. **Pearls tick.** Every tile's countdown decrements by 1 (top row to bottom, left to right). At 0 the tile tries to spawn a pearl, succeeding only if the tile is free, and then redraws its countdown either way.
2. **Each living dragon takes one turn, in ascending dragon ID.** A dragon that died earlier in the round is skipped. A split child is **appended** to the list and **takes its turn later in the same round**.
3. Round ends. The game ends if a team has no dragons, or if this was round 500.

The consequence: on your turn, every lower-ID dragon (either team) has already moved this round and every higher-ID dragon has not. The board you see is the exact current state.

Initial dragon IDs come from the map file's `DRAGON` line order, starting at 0. That order is also the turn order. Later splits take the next unused ID.

**One turn:**
1. The sonar inbox and echo counts are written to the bot's input and then emptied.
2. Defaults are set: **action = suicide**, sonars = none, indicator = none.
3. Bot output is read line by line until `ENDTURN`.
4. The action is applied.
5. If the dragon is still alive, sonars are cast in the order N, E, S, W.

**Reply commands (raw protocol v3):**

| Command | Args | Effect |
|---|---|---|
| `MOVE` | letters N/E/S/W, e.g. `MOVE NNE` = 3 steps | action: move/sprint |
| `SPLIT` | segment count k | action: split off the rear k segments |
| `SONAR` | `N|E|S|W` + uint64 | ping in that direction after the action |
| `PROTOCOL 3` | | protocol 3 input starts next turn |
| `INDICATOR` | text | label (cut to 512 chars) |
| `LOG` | text | log message |
| `DOT x y r g b`, `LINE x1 y1 x2 y2 r g b` | | replay drawings |
| `ENDTURN` | | stop reading |

- `MOVE` and `SPLIT` **overwrite each other**, so only the last one counts ("`MOVE N` then `MOVE E` moves east"). A `SONAR` overwrites an earlier one in the same direction. `INDICATOR` overwrites. Nothing is applied until reading ends.
- A line that can't be parsed is skipped with a log entry and doesn't change the action already set.
- A turn ends at the first of: `ENDTURN`; the bot blocking to read its next input; the bot exiting; the bot hitting its budget limit. In the first two cases the output is delivered. In the last two **nothing is delivered, so the action stays suicide**, and the bot restarts as a new process.

**Input each turn (protocol 3):** `ROUND r`, `DIR` (own facing), `LENGTH`, `UNIT_COUNT` (living dragons on own team), `NUM_MSGS n` + n uint64 values, `ECHOES kelp ally ally_head enemy enemy_head`. Then 49 tile lines `x y hasPearl pearlIn` (row 0 is 3 tiles north of the head, column 0 is 3 tiles west; coordinates already wrapped; `pearlIn = -1` means the tile never spawns). Then `DRAGON_BODIES n` + one line `team id x y facing isHead` per visible segment, own body included. Then 8 lines of 7 horizontal edges and 7 lines of 8 vertical edges (`.` open, `w` kelp, integer = portal id).
Init block, once per process: `ID`, `TEAM A|B`, `MAP w h`, `UNIT_LIMIT 64`.

## 4. The map

- A rectangular grid, **width and height each 10 to 64 inclusive**. (0,0) is the top-left, x increases to the right (east), y increases **down** (south). North is up.
- `game.get_map_size()` → (width, height). Available from the init block.
- **Symmetry is guaranteed**: vertical mirror, horizontal mirror, or 180° rotation. It is **not directly queryable**, so you have to infer it. (The map-file `SYMMETRY` directive is `x`, `y` or `xy`, and it is optional in custom map files.)
- **Topology is a torus.** Edges wrap. Moving off the east edge puts you on the west side, and so on. Vision and sonar also wrap. The east and south borders are drawn dashed and are the same edges as the west and north borders.
- The map is **tiles** (which can hold pearls or dragon segments) plus **edges** between tiles (open, kelp, or portal). Border edges count as edges too, so kelp or a portal can sit on the wrap boundary.
- Map file edge indexing: rows alternate between horizontal edges (north side of tile row r) and vertical edges (west side of tile row r). Each row is width+1 long, so the index runs to (2·H+1)·(W+1). I verified this against the demo maps. Edge kinds: 0 open, 1 kelp (portal id -1), 2 portal (id shared by exactly 2 edges).
- Starting dragons are defined per map (`DRAGON team len x y ...`, head first, minimum length 2). The doc example maps use **one length-3 dragon per team**. The number and length of starting dragons on the real ladder maps is not stated on these pages.

## 5. Pearls

- Pearls are the **only resource**. Eating one is the **only way to gain length** (+1 segment).
- Every tile has a **countdown** (`pearl_time`) that any dragon can see if the tile is in its vision.
  - It decrements by 1 at the **start of each round**, before any dragon moves.
  - At 0 the tile **tries to spawn** a pearl. It succeeds only if the tile is **empty (no dragon segment and no pearl)**. The countdown **resets whether or not the spawn succeeded**.
  - Reset value: uniform random integer in **[min_gap, max_gap] inclusive**. These are per-tile values set by the map, and dragons **cannot see them**.
  - `max_gap = 0`: the tile never spawns and always reports **-1**.
- **Symmetric pearls:** each tile **shares its countdown with its mirror tile**, so both fire together. If one is blocked, only the other spawns.
- **Death drops pearls**: ⌈L/2⌉ (see §11). Death drops **don't change countdowns**.
- A tile holding an uneaten pearl blocks its own next spawn, which wastes that spawn.

## 6. Kelp and portals (special edges)

**Kelp** is a wall on an edge. Moving across a kelp edge means **death ("Hit Wall")**, and the dragon drops pearls like any other death. Kelp has no other properties. It stops sonar.

**Portals:**
- Each portal has a non-negative ID. **Exactly one other portal edge shares the ID**, and the two are linked.
- Linked portals have the **same orientation** (both vertical edges or both horizontal). Either both lie on the map's line of symmetry or both lie off it.
- They are **double-sided**. Direction is preserved: entering from the left (moving east) puts your head out on the right side (east) of the partner edge. Engine wording: "the destination is the tile across the edge now faced… a portal leads out of its partner edge."
  - Verified in the demo map: a dragon moving east across the west edge of (4,3), a portal, arrives at (8,3), the tile east of the partner edge, which is the west edge of (8,3).
- Crossing a portal is a normal single step with no extra cost. The body then trails behind through the portal.
- **Vision does not pass through portals.** The far side is visible only if it's within Chebyshev 3 of the head by ordinary distance. So stepping through a portal is stepping into unknown terrain. The demo is literally "travels through a portal, straight into kelp".
- **Sonar does pass through portals.**
- API: `edge.get_edge_type()` returns EMPTY, KELP or PORTAL. `edge.get_portal_id()` returns -1 if the edge isn't a portal. In C/C++ there are also `is_passable()` (false only for kelp) and `is_portal()`.

## 7. Vision

- **7×7 square centred on the head** (Chebyshev distance ≤ 3, 49 tiles). It wraps around map edges. It does **not** see through portals.
- For each visible tile you get absolute (wrapped) coordinates, **pearl present?**, **pearl countdown**, **dragon segment** (team, dragon id, is_head, dir), and **its 4 edges** (type and portal id).
- Segment `dir`: for a head it's the heading; for a body segment it's **the direction toward the next segment nearer the head**. You can trace any visible dragon's body and so read its visible length and where its head is.
- `ct.get_tile(pos)` returns None outside the window. Your own `LENGTH` and `DIR` are given directly. Enemy lengths are only known from visible segments.
- There's nothing beyond vision except sonar echoes and messages, and whatever you remember. The map (kelp, portals) is static, so a dragon can accumulate map knowledge over time and exploit symmetry.

## 8. Movement

- **Every dragon must output exactly one action per turn**: a move (possibly multi-step) or a split. Only the last one output takes effect. No valid action means death.
- Actions are applied **after the turn's output is complete**.
- **Standard move:** 1 tile in a cardinal direction (N/E/S/W). The head moves and the body follows. The tail advances unless a pearl was eaten.
- **Facing** = direction from the first body segment to the head. The engine sets facing to each step's direction.
- **Moving backwards** (opposite to facing) pushes the head into its own neck, which is "often fatal". It's always fatal unless the head–neck link crosses a portal or the neck isn't actually in that tile. See the ambiguities.
- **Eating:** moving the head onto a pearl eats it automatically. The tail doesn't advance that step, so length +1.

### Collisions (per step, checked BEFORE anything moves)
Moving into an edge or tile, in this order:
1. Kelp edge: this dragon dies (Hit Wall).
2. Portal: the destination is across the partner edge. Otherwise the destination is the adjacent wrapped tile.
3. The destination is checked against the **dragon's own body first** (**including its current tail**, since the tail hasn't moved yet). Hit means Hit Self.
4. Then against other dragons:
   - **Another dragon's head** (either team): **both die**. The other dragon's death sequence runs first, then the mover's.
   - **Any other segment of another dragon** (either team): **only the mover dies** (Hit Other Body). The dragon that was hit is unharmed.
- The tail tile is **always blocked** for the move, including your own tail ("will die moving into own tail even if the tail would have moved"). In practice, **any tile currently occupied by any segment is lethal**, and a head-occupied tile is a mutual kill.
- There's no simultaneous-move resolution because everything is sequential by ID. Lower-ID dragons have already moved when you act, higher-ID ones haven't.

### Sprinting (multi-step move)
- `MOVE` with several letters, e.g. `MOVE NNE`, or `ct.make_moves([...])`. Steps can be any mix of directions.
- **Cost: x steps removes x−1 segments** (the first step is free).
- Each step is a full move with its own collision check and pearl eating, done in order. `NNE` might kill you where `ENN` wouldn't, even though both end on the same tile.
- **Per-step engine algorithm:**
  1. If this is not the first step, check the dragon can pay. **A length-2 dragon can't pay**, so it dies with No Valid Action.
  2. Facing = step direction.
  3. Resolve the destination (kelp, portal, wrap).
  4. Check own body, then other dragons.
  5. Head moves. Eat a pearl if one is there. Tail advances unless a pearl was eaten.
  6. If not the first step, remove one more tail segment.
- A death on any step **discards the remaining steps AND the turn's sonar**. Steps already taken still stand.
- Step k (k ≥ 2) is checked against the body **as the previous step left it**. A tile that would be fatal as a first step can be safe as a second step, because your tail has moved out of it.
- **Maximum sprint length for a length-L dragon = L−1 steps**, ending at length 2, if no pearls are eaten. Each step after the first needs length ≥ 3 before it.
- **Pearls during a sprint:** the first step eats and gains +1. Later steps that eat are **net 0** (the tail stays, then one extra segment is removed). So sprinting along a line of pearls costs nothing beyond the first step's normal gain.
- **Over-sprinting:** a sprint is *not truncated*. The dragon does the steps it can pay for, then pays for the next one with its life (No Valid Action, and pearls drop).

## 9. Splitting

- Splitting is the other action type. You get one action per turn, so you **can't move and split in the same turn**. The parent stays still that turn.
- `SPLIT k` / `ct.do_split(k)` / `ct.can_split(k)`. **k is the child's length.**
- The child is **the parent's rear k segments in reverse order**. The parent's old tail becomes the child's head, and the child faces **away** from the parent. The parent keeps its front L−k segments and its head and facing.
- **Legal only if:** child length k ≥ 2 (`SPLIT 1` is never legal); parent length after the split, L−k, ≥ 2; the team has **fewer than 64** living dragons.
  - So you need L ≥ 4 to split at all. Example: L=6 can split 2, 3 or 4.
- **An illegal split kills the parent** (No Valid Action).
- The child gets the **next unused dragon ID**, is appended to the turn list, and **takes its first turn later in the same round**. It runs a brand-new program instance with no memory, and it inherits the protocol version.
- The total length of the two dragons is conserved (no cost).
- The demo animation for a length-6 dragon doing `SPLIT 2` shows parent body (8,3)…(5,3), length 4, and child head (3,3) with tail (4,3), facing west.

## 10. Sonar (protocol 3)

### Sending
- Up to **4 sonars per turn, one per direction** (N, E, S, W). Each carries an **unsigned 64-bit integer**. Sending twice in the same direction keeps only the last one.
- Sonar is cast **after the action**, only **if the dragon is still alive**, in the order **N, E, S, W**. It **starts at the head** (the new, post-move head).
- The ray travels in a straight line. It **wraps**, **passes through portals**, and **stops at the first kelp edge or dragon segment** it hits (any team, including the sender's own body).
- If it hits a dragon, the message goes into **that dragon's** inbox. If it reaches no dragon within **WIDTH + HEIGHT tiles**, it's lost. Hitting kelp also means no delivery.
- **Edge case ("total internal refraction"):** a sonar sent **opposite to the facing direction** (into your own neck) **leaves from the tail instead**, travelling in the direction the tail points away from the body. For example, an east-facing dragon sending W has its ray start at the tail and go in the tail's outward direction, which isn't necessarily west if the body bends.
- Sonar costs nothing in length. It's independent of the move/split action, so you can split and send sonar in the same turn.

### Receiving
- Messages are read **at the start of the recipient's next turn**. A recipient with a higher ID than the sender gets it **later in the same round**. One with a lower ID gets it **next round**.
- Several messages can arrive in one turn, in send order.
- A signal is lost if the sender died during its move (nothing is cast) or if it hit nothing. The replay shows the ray either way.
- **Either team can receive a message.** It carries no sender or team information. Enemies can intercept (their body blocks the ray and they receive your message) and can spoof.

### Echoes
- At the start of its next turn, the sender gets **counts** of what its sonars stopped on, in the order **kelp, ally (body, including its own), ally_head, enemy (body), enemy_head**. A ray that hits nothing adds nothing.
- The counts are aggregated over all four rays, so there's no per-direction breakdown unless you send only one ray per turn.
- Example: 4 rays hitting 2 kelp, 1 ally body and 1 nothing gives `ECHOES 2 1 0 0 0`.
- **Protocol 3 only.** You have to print `PROTOCOL 3`; the current helpers do this in `end_turn`. On protocol 2 you get no echoes, and values above 2^32−1 are dropped.
- API: `ct.send_sonar(Direction, value)`, `ct.get_sonar_messages()`, `ct.get_sonar_echoes().enemy_head` (and so on). The legacy `send_sonar(value)` sends a 32-bit value in the facing direction.

## 11. Death

| Reason | Cause |
|---|---|
| Hit Wall | moved across kelp |
| Hit Self | moved into own body, including the tail |
| Hit Other Body | moved into any non-head segment of another dragon (either team) |
| Head to Head | moved into another dragon's head, so **both** die |
| No Valid Action | unpayable sprint step, illegal split, malformed command, no action, crash, or (per Execution Order/Timeouts) running out of points or time |

- **Mandatory action:** no valid action means suicide.
- **Pearl drop:** starting at the head, **every second segment of the body as it stands** becomes a pearl (head, skip one, next, …), so **⌈L/2⌉ pearls**. Countdowns are unchanged. Then the dragon is removed. Its remaining sprint steps and its sonars are discarded.
- On a collision death, the head **never entered** the destination, because the check happens before movement. The pearls land along the dragon's pre-step body.
- Head-to-head: the victim, whose head was on the destination, drops its pearls first. Then the mover drops its own pearls.
- Demo check: a length-3 dragon dies and drops pearls at its head tile and 3rd segment tile (2 = ⌈3/2⌉). A length-6 dragon drops 3.

## 12. Ambiguities and unclear points

1. **Timeout fate conflict.** The Death page says dragons that exceed the time limit *after* outputting a valid action "experience a different fate (see Timeouts)". But Timeouts and Execution Order both say a turn that hits the limit **delivers nothing, so the action defaults to suicide** and the process restarts. Assume a timeout kills the dragon.
2. **Split child's first turn.** The text says the child acts **later in the same round**, but the split demo animation shows the child moving only from the next round. Trust the text (Execution Order agrees), but test it locally.
3. **"Total length across all of its dragons"** (tiebreak 2): it's presumably living dragons only, but this isn't stated.
4. **Elimination timing.** "Both eliminated in the same round → draw." Elimination is evaluated at round end, so a team wiped out mid-round can still be saved (for a draw) if the other team also dies later in that round.
5. **Backwards move** is "often" fatal. The exceptions are presumably when the neck isn't in the backward tile: the head–neck link crosses a portal (backwards then goes through the portal), or on odd wrap geometries. This isn't spelled out.
6. **Body facing across portals and wrap**: the facing of a segment whose next segment is on the far side of a portal isn't defined. Probably it's the move direction. This matters when tracing enemy bodies from `dir` values.
7. **Sonar range `WIDTH + HEIGHT` tiles.** It's unclear whether a portal jump counts as one tile. The ray start tile is also unclear: presumably the first tile checked is the one adjacent to the head.
8. **Sonar that hits the sender's own body**: delivered to itself, next turn. The "opposite direction exits via tail" rule only covers the neck case. What happens if the tail's outward ray immediately hits the body (e.g. a coiled dragon) isn't described.
9. **Portal ID uniqueness**: "almost-unique", meaning exactly 2 edges per ID. It isn't stated whether an ID can repeat across different symmetric pairs.
10. **min_gap/max_gap** distributions and typical values are hidden. Countdown values seen give only partial information.
11. **Starting configuration** (number and length of dragons, positions) on ladder maps isn't stated on the rules pages. `GET /api/v1/maps` returns map texts (needs an API key; not fetched).
12. **The Overview's "25 ms" figure** is superseded by the CPU-points model (100M points per turn).
13. **Pearl spawn onto a tile with a head arriving later that round**: the spawn happens at the round start, so a pearl can appear right where you planned to move. This is harmless, since eating is automatic.

---

## Strategic implications

**What wins**
- If both teams survive to round 500, **max single-dragon length decides**, and total length only breaks ties. A wide swarm doesn't win by itself. You need one giant at the end, **or you eliminate the enemy entirely**, which wins regardless of length.
- **Elimination is total loss.** Always keep more than one dragon alive, far apart, as insurance. A lone huge dragon is one head-on collision away from losing the game.

**Collisions are the combat system**
- **Body-blocking**: an enemy head moving into any of your body segments dies and you're unharmed. Long bodies are weapons and walls. Cutting in front of an enemy head (Tron-style) in tight spaces, next to kelp, or in corridors kills it.
- **Head-on trades are 1-for-1 regardless of size.** A **small kamikaze dragon (length 2–5) ramming the enemy's longest dragon's head** is an enormous trade. The big one drops ⌈L/2⌉ pearls that your nearby dragons can eat.
- **Sprint makes ramming range = length−1 steps.** A length-L dragon can reach any tile within L−1 steps along a clear path in one turn and hit a head. Vision is Chebyshev 3, so up to Manhattan 6 inside the window. Defensively, **keep your big dragon's head out of reach of enemy heads** (reach ≈ enemy length − 1 along free paths). Also note that lower-ID dragons act before you: an enemy with a higher ID gets to react to your move in the same round.
- **Turn order matters.** When you act, everything with a lower ID has already moved. You know their final positions this round; higher-ID dragons still get to respond. Kills are easiest against dragons that move after you and have few escape squares. Split children always get high IDs, so they act late in the round and see more.
- **Tails are not safe tiles.** Every occupied tile is lethal. Simple rule: a tile is safe iff it's empty and its edge isn't kelp, but think about enemy heads adjacent to it (they could ram you after you move if their ID is higher).

**Economy**
- Pearl countdowns are visible, and mirrored tiles share a countdown. Once the symmetry is known (infer it from kelp and portal layout or countdown matches), **every countdown you see tells you the mirror tile's countdown too**. Build a map-wide spawn timer table in memory and route to tiles just before they spawn.
- Don't park on a spawn tile when its countdown hits 0: the spawn fails and the timer resets. The same applies to leaving pearls uneaten, which blocks future spawns there. Clear pearls promptly.
- **Sprint economics**: sprinting costs 1 length per extra step, but steps after the first that eat pearls are net-free. It pays to grab a pearl the enemy would otherwise take, to escape, or to reach a kill. Sprinting is also the only way to "think ahead" several steps inside one turn's compute budget.
- **Corpses**: killing a dragon of length L makes ⌈L/2⌉ pearls on alternating body tiles. Be ready to harvest them, and deny the enemy your own corpses.
- **Splitting** conserves length and multiplies foraging heads (up to 64). But you can't merge at the end, so the final winner must be a single dragon. A plausible plan: split into foragers and fighters early, and funnel pearls to one "king" or just let several grow, then protect the longest one late. A forager can feed the king by dying next to it (loses half), which is inefficient but possibly useful at round ~480+ when a dying dragon's length otherwise only counts for tiebreak 2.
- A split child starts facing away from the parent at the old tail position with a fresh process. Its first move must not be backwards. Split while the tail region has free space. The parent stays still that turn, so don't split when a higher-ID enemy head could ram you.

**Information**
- Vision is tiny (7×7). The map is static and symmetric, so **persistent per-dragon map memory** (kelp, portals, portal pairings, countdowns) is high value. Portal destinations are unseen, so remember them after you cross once, or infer them from symmetry and pairing constraints.
- **Sonar echoes are free long-range radar**: 4 rays per turn, each up to W+H tiles, report enemy heads and bodies along the cardinal lines. Rays are aggregated, so rotate directions across turns or use single rays to localise.
- **Sonar messages are interceptable and spoofable.** Use a checksum or key (derived from something enemies can't guess, e.g. a hardcoded secret) and ignore unauthenticated messages. Encode compact data in 64 bits (positions 6+6 bits, round, type, target, etc.).
- Messages to lower-ID dragons arrive a round late. Parent-to-child in the same round works, since children have higher IDs.

**Engineering**
- The compute budget is 100M points per dragon-turn. Python parsing alone is about 10M, so serious search (flood fill for space safety, multi-step move search, opponent head-reach) strongly favours **C/C++**. Output one flush per turn, and keep logs minimal (2.5M points per write).
- Always emit a safe default action early (the helpers overwrite actions, so set a fallback move first). Guard every sprint and split with `can_split` and length checks; an illegal action is death.
- Flood-fill/space-counting to avoid self-trapping is standard Snake AI and applies directly here. Because of torus wrap and portals, the neighbour function must handle both.
