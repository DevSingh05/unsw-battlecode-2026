# Lever: blocked food (UNK_SEALED_FOOD)

Patch: `notes/levers/blocked-food.diff`, against `bot/main.cpp` and `bot/params.hpp`. Patched source: `notes/levers/blocked-food/src/`. Every change sits behind `UNK_SEALED_FOOD` (default 0). With the flag off, the build behaves exactly like bot/ (the only unconditional change is a timestamp member that nothing reads). Unknown maps only (`!w.known`).

Scripts, all run from the project root:
- `python3 notes/levers/blocked-food/can_fire.py maps/*.map maps/gen/*.map ...` is a static check of which maps the evidence rule can fire on at all.
- `python3 notes/levers/blocked-food/stats.py <replays>` gives per-team eats, portal crossings, crossing deaths, deaths and final length.
- Replays of every mechanism game are in `notes/levers/blocked-food/replays/`.

## The problem

UNK_EXPLORE (knock, then cross on a clean echo) only opens its gate when a dragon's portal-free region is fully scouted and small. On Default-like maps (food in sealed cells) that never happens, so v28 makes 0 crossings there. A plain hunger valve fixed Default but hurt Autarky, where portals are only shortcuts (server: 4/10 -> 2/10). We need a signal, available from partial vision, that separates "food behind doors" from "portals are shortcuts".

## The discriminator: seen food that is provably unwalkable

Vision passes over kelp, so dragons see spawner tiles inside sealed rooms. Every visible tile reports a countdown, so `w.gapSeen[t] > 0` marks it as a spawner. The rule is general and involves no map names or tables:

1. BFS the portal-free component from our head over `w.nxt`. Unknown portals count as kelp, and **unseen edges count as open**. A spawner the BFS does not reach is therefore *provably* unwalkable, not guessed. Bodies are ignored, so congestion alone never counts as a wall.
2. Over all seen spawners, estimate each rate as `1/max(2, gapSeen)` and split them into sealed (unreached) and reachable.
3. The rule fires when all of these hold:
   - `sealed >= 4` tiles (`UNK_SEALED_MIN`);
   - sealed rate >= 20% of the seen rate (`UNK_SEALED_FRAC`);
   - sealed food per tile is at least as rich as the reachable food (`UNK_SEALED_RICH` 1.0);
   - an unexplored, cooled-down unknown door is reachable;
   - hunger >= 20 (`UNK_SEALED_HUNGER`), counted from the later of our last meal and our last explore crossing;
   - no visible pearl within 6.
4. When it fires, it sets the existing `exploreDesire`. Everything downstream is unchanged v28 code: door lures, the knock, crossing only on a clean echo, and the per-edge cooldown.

Three stabilisers came out of the mechanism checks below:
- **Richness test.** Without it, a dragon that has just entered a rich room sees the outside as sealed food and leaves again at once.
- **Settle.** For 15 rounds after an explore crossing (`UNK_SEALED_SETTLE`), no explore gate fires, v28's closed-room gate included. The exception is when the room is cramped (next item).
- **Small rooms.** Inside a portal-free room smaller than 32 tiles (`UNK_SEALED_ROOM_MIN`):
  - no splitting;
  - if other dragons' segments cover 1/4 or more of the room, the gate opens at once so the dragon can leave.

Mode 2 (`UNK_SEALED_FOOD=2`) also counts spawners within 6 that need a walk of at least 2*direct+8. That is Codex's detour idea. I have **not tested it**, and I expect it to misfire on Autarky's kelp corridors, which are dead-end pump pockets beside the box portals. Mode 1 is the proposal.

### Where it can fire at all (static, full knowledge, per spawn head)

`can_fire.py` runs the same thresholds with the true rates, which is the most evidence a dragon could ever collect.

| set | fires on | does not fire on |
|---|---|---|
| ranked + other named maps | Default, QoS, Schooltime, Stronghold, Trauma | Autarky, Dilemma, Trophy, Colosseum, Slithery, Portals (sealed food there is poorer per tile) |
| lesson (24) | islands_a/b, vault_a/b/c | webs_a/b (shortcut portals) and every portal-free map |
| gen (40) | g2026_28 (75% rate sealed), g2026_32 (97%) | the other 38, including every shortcut-portal map |
| genhold (40) | g2027_02, _12, _13, _16, _34 | the other 35 |

It fires only on maps where a spawn region really is cut off from food. From a spawn region on a shortcut-only map, `sealed` is 0, so a dragon there behaves exactly like v28. **This is the property that guards against overfitting.** Where it fires follows from the map's structure, and nothing was tuned per map.

## Mechanism checks

Blind single games (`-DNO_KNOWN_MAPS=1` on both sides) at seed 1000, candidate against `variants/v28` blind. 11 games in all, plus 2 judge-sandbox runs.

| game | eats (cand / v28) | crossings (cand) | crossing deaths | result / notes |
|---|---|---|---|---|
| Default, v28 vs v28 (reference) | A 35 / B 168 | 0 / 0 | - | B wins; A is eliminated at r280 (a strong side bias on this seed) |
| Default, cand1 (first version) as A | 34 / 142 | 18 | 1 | A eliminated at r252; dragons ping-pong through the (6,8)<->(11,10) door every 4 rounds |
| Default, cand2 (+richness, settle) as A | **78** / 255 | 22 | 0 | A survives to r357 (reference A: 35 eats, dead at r280) |
| Default, cand2 as B | **457** / 339 | 243 | 9 | cand eats 271 in cells and 98 in corner rooms, but 183 deaths: it crowds into 4x4 cells and splits there. Loses on length |
| Default, cand3 (+small-room rules) as B | **433** / 200 | 32 | 2 | **cand wins**: max 18 vs 6, total 154 vs 18, deaths 91 vs 79 |
| Autarky, cand1 / cand3 as A | 453 / 291 | **0** | 0 | the rule **never fired** (0 LOG lines); stats are identical to each other, so behaviour is v28's |
| Trauma, v28 vs v28 (reference) | A 407 / B 948 | 105 / 59 | 17 / 6 | side bias again |
| Trauma, cand2 as A | 330 / 1026 | 102 | 9 | about the reference A; the rule fires from r70 (sealed 15 vs reach 10) on top of v28's closed-room gate. Neutral to slightly worse, within single-game noise |
| g2026_00 / other shortcut gen maps | not played | - | - | statically cannot fire (sealed spawners = 0, see above) |

On Default the rule fires from r20: `sealed=25/0.21 reach=159/0.48`, which is the corner room seen through kelp. On Autarky it never fires. The first version showed why the richness and settle rules are needed (ping-pong), and cand2 showed why the small-room rules are needed (crowding deaths in 4x4 cells). With cand3, Default goes from 0 crossings to 32 crossings per team-game, with 2 fatal (6%, the same as UNK_EXPLORE's 4-14%), and roughly doubles eats against a blind v28 on the same seed and side.

I did not re-run Trauma with cand3. The small-room rules don't touch Trauma's 264-tile start room, but Trauma deserves a line in the batch.

## CPU (judge sandbox, `unswbc run MAP v28blind candblind --sandbox --no-replay`)

- Default 32x32, where the rule fires: cand p50 7.2M, p99 8.0M, max 8.5M; v28 p50 7.2M, p99 7.7M, max 8.0M. This was also a cand win.
- g2026_16 64x64 with portals, where it doesn't fire but the BFS still runs for hungry dragons: cand p50 16.8M, p99 18.7M, max 31.4M; v28 16.7M, 17.7M, 31.7M.
- The cost is one full BFS (N ≤ 4096) per hungry small dragon per turn, plus a BFS capped at 32 tiles. That is about +1M at p99, far under budget.

## Risks and open points

- **Self-play hides the upside.** Blind v28 never harvests the cells, so the cells fill up. Against real opponents who cross, the pearls behind doors are contested. The server blind test (Default + Autarky, like blind27h45) is the real check. Autarky should reproduce blind28 exactly (the rule is inert there), and Default is where the gain has to show.
- **portalSide bug.** In v28 only the N/W faces of unknown portals are marked, so half the doors can't be knocked. UNK_PORTAL_SIDES=1 would double the doors. I didn't test that combination, and more doors also means more crowding.
- **Portals-like maps are excluded by the richness rule** (sealed food poorer per tile). That is conservative: it gives up nothing relative to v28.
- **Holdout.** 5 of the 40 genhold maps can fire, so the holdout run will measure it. Those five should be looked at separately, and the other 35 should come out ~0.500, since the flag behaves like v28 there unless a dragon wanders into a sealed region through the fallback escape.
- **The new constants are guesses, not tuned values:** hunger 20, settle 15, room 32, crowd 1/4, FRAC 0.2, RICH 1.0. Worth sweeping: hunger 20/35 and settle 10/20, on gen + gated + lesson, not on the holdout.
- **Possible overlap with `notes/levers/frontier-explore`.** Both levers set exploration drives. Test them separately before stacking.

## Suggested protocol for the main agent

1. `unseen_eval.py "bot:-DUNK_SEALED_FOOD=1"` on gen, blind, lesson and gated. Expect gated, blind and lesson above 0.5, gen about 0.5, and ladder exactly 0.5 (known maps are untouched).
2. Holdout once.
3. Server blind A/B on Default and Autarky against the blind28 numbers (Default 4/10 with 348 eats, Autarky 7/10 with 395 eats).
