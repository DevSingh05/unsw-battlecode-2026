# Failure mining: v24 on unseen maps (track: failure-mining)

28 Sep 2026. Read-only on bot/ and variants/. I ran 18 single games (9 arena calls with `--seeds 1 --jobs 1`, each a
side-swapped pair) and analysed the replays together with the existing server batches `replays/ab_v21..v24`.

## TL;DR (ranked by value)

1. **Unit-cap deaths of big dragons (cheapest fix, strongest evidence).** Of our trapped deaths at L>=5 before r400
   (head fully boxed in), **88% happen while the team is at the 64-dragon cap** (329/374 deaths, 3159 of 3446 length).
   In 95% of them the tail still had a free exit, so `SPLIT L-2` would have saved the rear. The trapped reverse split,
   KING_ESCAPE's split and ESCAPE_SPLIT are all gated on `units < unitLimit`, and normal growth splits spend every last
   slot. **The same thing happens on the ladder:** in Schooltime server games (ab_v22/v23), 305 of 338 trapped L>=5
   deaths happened at the cap (2268 length, up to 49 per game). This is the "we win the yard and then die en masse inside
   it" pattern from the journal. Fix: keep 3-4 slots free for emergency splits. `-DSPLIT_MAX_UNITS=60` already does
   this with no code change.
2. **Portal blindness on unknown maps is the biggest loss, and our eval can't see it.** On unknown maps v24 treats
   every portal as kelp. On the devs' own ranked maps, walking alone reaches only **1% (Trauma), 27% (QoS), 41%
   (Portals), 50% (Default) and 67% (Schooltime)** of the pearl rate. Only 3 of 40 `maps/gen` maps (and 3/40 genhold)
   are gated like that, so the gen set under-represents it. Blind v24 against map-aware v24 on Default lost 0/2 and
   was **eliminated at r206/r215**: 6-13 eats in r0-99 against 81-91, 70-83% of dragon-turns idle, and 0 portal
   crossings against their 271-292 (only 2-4 of theirs fatal). `unseen_eval.py` always runs blind against blind, so
   neither side uses portals and this gap never shows up.
3. **Portal knowledge doesn't reach the dragons that need it.** Taken together, the team sees both ends of 10/12
   pairs by r100 on blind Default and 10/10 by r50 on g2026_22. But a living dragon knows on average only 0.2-3 pairs,
   because children start with empty memory and most living dragons are young children. LEARN_PORTALS as written can
   only use pairs that one dragon saw both ends of by itself. On islands maps the team knows 1/12 pairs at r100:
   there, pairs can only be learned by crossing.
4. **Eval hygiene: many "unseen" games are coin flips on side.** v24 and v16 play *identical* games on unknown
   maps until about r300: every game that ended before r300 (pockets_a r100, g2026_22 r356, blind Default r324) had
   the same result by side, not by bot. Mirror games break symmetry within 1-4 rounds (tie-breaks, turn order), and
   the break is amplified into 63-0 unit collapses (pockets_a). Early-elimination maps add noise to v16-descendant
   A/Bs, not signal.
5. Smaller: starvation maps (g2026_06/19: 12 pearl tiles, gaps 240-490) are decided by 1-4 late pearls; escape-gamble
   portal crossings die 35% of the time (they would have died anyway); head-on trades are symmetric (x:x).

## 1. Games played

`notes/unseen/replays/fm/**` (v24 vs v16, seed 1000, both sides) and `notes/unseen/replays/fm_known/` (v24 blind vs
v24 map-aware on Default).

| map (type) | v24 result (A, B) | notes |
|---|---|---|
| lesson/islands_a (portal-only islands) | L500r, W500r | stuck on the spawn island to about r150; whichever side escapes first wins (king 56 vs 19) |
| gen/g2026_06 (30x30 portal maze, starvation) | L, L (500r) | no pearls before r300; 1 death per game; decided by 1-3 pearls |
| gen/g2026_19 (49x49 maze, starvation) | W, L (500r) | as B we never ate in 500 rounds (longest 2 vs 6) |
| lesson/open_a (60x60 king race) | W, W | 62 of 64 units at cap for 350+ rounds; about 60 trapped L>=5 deaths per side |
| lesson/maze_a (wrapping maze) | L, W | at cap for 250-290 rounds; 132 trapped L>=5 deaths for v24-as-B |
| gen/g2026_22 (20x20, 10 portal pairs, rich) | L356e, W356e | same game by side (identical bots until elimination) |
| lesson/pockets_a (factory) | W101e, L101e | same game by side; side B collapses 63-0 by r100 |
| blind default (NO_KNOWN both) | W324e, L324e | same game by side; 47% of dragon-turns idle |
| default: v24 blind vs v24 known | L216e, L207e | blind side eliminated; 0 vs 271-292 portal crossings |

## 2. Failure A: big dragons die boxed in while the team is at the unit cap

**What happens.** On rich or big maps the team reaches 64 dragons (mostly L2-4) and stays there: 350/499 rounds on
open_a, 248-286 on maze_a, 184 on islands_a (as B), and 118-209 rounds in 12/20 Schooltime server games. At the cap:
- L4+ dragons stop splitting and grow (this part is fine);
- **a big dragon whose head gets boxed in has no way out**, because every rescue split (trapped reverse split at
  main.cpp:2481, KING_ESCAPE's reverse split at :2139, ESCAPE_SPLIT at :1156) needs `units < w.unitLimit`. It dies whole.

**Numbers** (`notes/unseen/tools/fm_trapped.py`, plus a cap check):

| set | trapped L>=5 deaths r<400 | at >=63 units | length lost at cap | tail still had an exit |
|---|---|---|---|---|
| 16 local unseen games | 374 | 329 (88%) | 3159 | 354/374 (95%) |
| Schooltime server games ab_v22+v23 (20) | 338 | 305 (90%) | 2268 | not measured |
| Default/Autarky/Devil/Dilemma server games (60) | 0-0.7 per game | cap rounds 0-4% | n/a | n/a |

What boxed the head in: ally+self 125, ally+kelp+self 123, pure self-coil 66, enemy+self 38, ally+enemy 22. At the cap
the board is crowded with our own small dragons, and that crowding is what closes the box.

**Examples**
- open_a seed 1000, v24 as A: r148 id137 L9 boxed by ally bodies N/E/S; r219 id48 L19 boxed by enemy bodies N/W
  and its own body; r187 id101 L18. Team at 64 each time.
- maze_a seed 1000, v24 as B: r126 id96 L10 self-coil at (22,12) (west kelp, N/E own body, S ally); r202 id286 L15;
  r174 id283 L12. A run of 45 L8+ trapped deaths from r126 to r349.
- Schooltime server 530808 (loss vs Kamikaze): 177 rounds at cap, 41 trapped L>=5 deaths; 530810 (loss vs hm): 168, 49.

**Fix (P1).** Keep a few slots free for emergencies. Normal growth splits stop at 64-R; rescue splits may use the
last R slots. `SPLIT_MAX_UNITS` already exists and is used only by the growth split, so `-DSPLIT_MAX_UNITS=60`
is the zero-code test. A cleaner flag `CAP_RESERVE` would give pocket-pump/ESCAPE_SPLIT a middle tier (see the
proposal). Expected: most of the ~330 at-cap trapped deaths per 16 games become reverse splits (the L-2 rear
survives as one dragon). The team gets 4 fewer foragers at the cap (6%), which is negligible. Many of the saved
dragons are L10-36 on open_a, i.e. future kings.

## 3. Failure B: portal blindness on unknown maps

**What v24 does.** In `observeEdges()`, when `!known` a portal edge gets `nxt = -1` (kelp) unless LEARN_PORTALS
links it (off). The only crossings are UNK_PORTAL_ESCAPE gambles, taken when every other move is lethal.

**How much of the map that hides** (`notes/unseen/tools/fm_regions.py`: tiles and pearl rate reachable from team
A's starts by walking, as a fraction of what is reachable with portals):

| map | walk-reachable tiles | walk-reachable pearl rate |
|---|---|---|
| ranked/trauma | 0.23 | **0.01** |
| lesson/islands_a | 0.06 | 0.03 |
| gen/g2026_32 | 0.11 | 0.03 |
| lesson/vault_a/b/c | 0.89-0.93 | 0.09-0.17 |
| genhold/g2027_13 | 0.23 | 0.21 |
| gen/g2026_28 | 0.39 | 0.25 |
| lesson/islands_b | 0.25 | 0.25 |
| ranked/queen_of_spades | 0.95 | **0.27** |
| ranked/portals | 0.87 | **0.41** |
| gen/g2026_23, genhold/g2027_16 | 0.50 | 0.50 |
| ranked/default | 0.81 | **0.50** |
| ranked/schooltime | 0.90 | **0.67** |

The devs' hand-made maps put the fast pearls behind portals (5/10 ranked maps below 80%). Their generator (notes/13)
only requires the portal-connected component to be at least 60% of the map, so gated maps also come out of it,
just more rarely (3/40 in our gen set). Tournament maps are new and hand-made ("each map teaches a lesson"), so the
ranked-map rate is the better prior.

**What it costs against someone who uses portals** (Default, seed 1000, v24 blind vs v24 map-aware; the map-aware
bot stands in for any opponent with a working generic portal model):
- blind as A: eliminated r215. Eats r0-99 6 vs 91, r100-299 2 vs 160. Units r100 6 vs 37. 83% of dragon-turns idle.
- blind as B: eliminated r206. Eats 13 vs 81 and 1 vs 150. 58% idle.
- the map-aware side crossed 271-292 times, and only 2-4 of those crossings were fatal.

Blind against blind, the same map is a 1-1 side coin flip (W324e/L324e) at 47% idle. The waste is there in both
cases; blind-vs-blind simply can't punish it.

**Why LEARN_PORTALS kept failing, and why a new variant could work.** Every LEARN_PORTALS test (0.45, 0.438,
0.482, 0.485, and 3/8 with the blind penalty) was run blind against blind on gen+blind+lesson. There:
(a) 37/40 gen maps are walk-connected, so learning portals can only cost (crossing deaths);
(b) the opponent never reaches the gated pearls either, so nothing is lost by leaving them;
(c) per-dragon knowledge is thin (see below), so the few crossings that happen come from whichever dragon happened
to see both ends, not from a plan.

`fm_portalknow.py` (pairs known once a dragon has seen both ends in its own window; children start empty):

| game | team union knows | mean pairs known per living dragon |
|---|---|---|
| blind Default r100 / r200 | 10/12 / 10/12 | 2.7 / 1.4 (22-37% of dragons know none) |
| g2026_22 r50 / r200 | 10/10 / 10/10 | 0.24 / 0.61 (78% know none at r50) |
| g2026_19 r100 / r300 | 10/12 / 12/12 | 0.7 / 4-5 |
| islands_a r100 / r300 | 1/12 / 4-9/12 | 0.6 / 0.9 (both ends can only be seen by crossing) |

Sharing that knowledge (sonar handoff to split children plus gossip) would multiply what each dragon knows by
4-10x on these maps. Since v20, all the portal-safety machinery (PORTAL_WARN, WARN_MEMO, ECHO_GUARD, ECHO_BODY_PEN,
NEWBORN_NECK_GUARD, KING_PORTAL_PENALTY) keys off `portalExit[]`, which is computed from `nxt`. Learned links
therefore get the same guards that cut Default portal deaths from 61 to about 8 per game on known maps.

**Recommended order:** first measure on the right test (P4). Then an atlas (P2) and scouting of confined regions
(P3), all behind flags gated on `!w.known`.

## 4. Failure C: evaluation blind spots

- **Identical games.** v16 and v24 differ only in late/king/portal-on-known-map logic, so on unknown maps their
  play is identical until about r300. Every pair that ended by elimination before then was decided by side
  (pockets_a W101e/L101e, g2026_22 W356e/L356e, blind Default W324e/L324e). Such (map, seed) pairs score exactly
  0.5 and dilute the unseen score toward 0.5. Scores like "gen 0.588" come from the long games only.
- **Chaotic side effects.** `fm_mirror.py` shows that mirror games lose symmetry at r1 (blind Default, 180-degree
  map), r4 (pockets_a, g2026_22) or r75 (maze_a). By r100 that is a 63-0 unit swing on pockets_a. Some of our
  choices aren't mirror-equivariant (direction tie-breaks in N,E,S,W order); A moves first within each id pair.
  The swings are big, so single seeds on elimination maps are very noisy; use more seeds there, or mark those maps.
- **Blind vs blind can't measure portal use** (section 3). Add an asymmetric set: candidate with `-DNO_KNOWN_MAPS=1`
  against map-aware v24 on {default, trauma, queen_of_spades, portals, schooltime}, plus lesson islands_a/b and
  vault_a/b/c and gen g2026_23/28/32 blind vs blind. v24's baseline there is roughly 0 wins, so any real portal
  model shows up quickly.

## 5. Smaller findings (not proposed now)

- **Starvation maps** (g2026_06, g2026_19: 12-14 spawning tiles with gaps [240,490] plus 2 of [1,2559]): nothing
  happens until r240+, then 1-6 pearls decide the tiebreak. Visible countdowns give exact spawn rounds (spawnAt), so
  a "be there when it fires" rule for L2 dragons could matter. Only 2 games of evidence.
- **Escape-gamble crossings** (UNK_PORTAL_ESCAPE): 31 crossings / 10 deaths on islands_a, 53 / 19 on g2026_22 (about
  35% fatal, all by dragons that would otherwise certainly die). These gambles also teach the pair under LEARN_PORTALS.
- **Pocket-mouth jams** on pockets_a: several L2-3 deaths with the neck on one side and an ally diver on the other in
  a 1-wide pocket, where an exiting child meets an entering diver. Both sides do it.
- **Head-on trades** are symmetric in every game (our rammed = their chose_headon), so there's no one-sided ram
  weakness on these maps.

## 6. Tools (all in notes/unseen/tools/, read-only on replays)

- `fm_analyze.py DIR [--us TAG]`: per-game result, units/longest/total timeline, our and their death classes
  (feed / merge / portal_* / trapped_* / chose_* / rammed), L>=8 deaths, portal crossings, head and vision coverage,
  eats per phase, idle dragon-turns.
- `fm_trapped.py DIR`: trapped L>=5 deaths before r400, tail-exit check, what boxed the head in (slow: it
  re-simulates to each death, about 9 min for 16 games).
- `fm_regions.py [gen genhold lesson ranked]`: walk-reachable vs portal-reachable tiles and pearl rate per map.
- `fm_portalknow.py REPLAY...`: portal pairs known per dragon vs team union over time.
- `fm_mirror.py REPLAY`: first round a mirror match breaks symmetry.

## 7. Proposals (details in the structured summary)

| # | flag | what | test first on |
|---|---|---|---|
| P1 | `SPLIT_MAX_UNITS=60` / `CAP_RESERVE` | keep emergency split slots at the unit cap | lesson open_a, maze_a, islands_a; ladder Schooltime; then the full unseen_eval |
| P2 | `PORTAL_ATLAS` (+ LEARN_PORTALS=1) | share learned portal pairs: split handoff + gossip rays | blind-vs-known set (P4) + lesson islands/vault |
| P3 | `UNK_SCOUT` | when confined, an L2-3 dragon crosses an unlearned portal on purpose (learn by crossing) | islands_a/b, vault_*, blind trauma/qos |
| P4 | eval: blind-vs-known set | harness change, no bot flag | n/a |
| P5 | `CAP_RESERVE_PRIO` | tiered slot reserve, cap-aware pump | after P1 wins |
