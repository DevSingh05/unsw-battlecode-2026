# Stripes food bug + portal exploration (UNK_SCARCE_FIX, UNK_PORTAL_EXPLORE), 2026-10-01

## Root cause (Task 1)
Our dragons on Stripes don't eat because nearly all the food sits behind portals, and on unknown maps v35 treats every portal as kelp (LEARN_PORTALS=0).
- maps/sprint/stripes.map, with gaps rebuilt from replays: the fast spawners (gap 1-1, 1-4, 1-10, ...) are all inside 2x2 pockets walled by kelp, and portals are the only way in. Examples are (2-3,0-1) and the hotspots (11-12,0-1)/(11-12,10-11). Static BFS from every start (scratchpad frac.py): walkable spawners are 30 tiles worth 0.15 pearls/rd; spawners reachable only through portals are 24 tiles worth 11.2/rd. That is 99% of the food, about 90x richer per tile.
- Local v35 vs v35, seeds 1-3: 0 portal crossings, 4-22 eats per team, and the pocket pearls stay uneaten for the whole game (round-by-round maps in scratchpad an2.py).
- Why the existing valves don't fire. UNK_EXPLORE's sealed-in gate needs the portal-free region to be under 0.7 of the board, and on Stripes it is 248/288 = 0.86. The hunger valve is off (100000). UNK_SEALED_FOOD is off. The dragons can see both ends of every pocket portal, so the exact link is known from vision, but it is never used.
- The other suspects are consequences of starving, not causes. Explore wandering, never reaching L4 and so never splitting: once the food is reachable, the same bot splits 14-63 times per game.

## Changes (bot/main.cpp, bot/params.hpp; all default 0; q36 behaviour unchanged with flags off)
- **UNK_SCARCE_FIX** (+USF_MIN 4, USF_FRAC 0.5, USF_RICH, USF_LOG). Portal pairs are always recorded (World::portalSeen). New `scarceFixCheck()` runs each turn on unknown maps until it fires. It does two BFS runs from the head: walk-only, and walk plus the pairs whose two ends we've seen. It fires when the seen spawners reachable only through the links number at least 4, carry at least 50% of the known food rate, and (USF_RICH) are at least USF_RICH times richer per spawner tile than the walkable ones. When it fires, `World::enablePortalUse()` links the known pairs into nxt, and from then on the dragon behaves as LEARN_PORTALS (sticky, per dragon). On shortcut-only maps there is never any portal-only food, so v35 behaviour is unchanged.
  - Without USF_RICH, the gate also fired on room-grid maps (lesson islands_a/b, g2026_23/28, where every room has food, richness 0.5-2x) and lost there: islands_a 1/8, islands_b 2/8, g2026_23 2/8. This is the old LEARN_PORTALS over-crossing. USF_RICH=4 keeps Stripes (91x), Australia (11x) and the vaults (27-51x) and drops those maps.
- **UNK_PORTAL_EXPLORE** (+UPE_MAXLEN 4, UPE_HUNGER 12, UPE_RANGE 16, UPE_SOON 4, UPE_MIN_ROUND 5, UPE_SLOT 30, UPE_MOD 3). This is calc's rule. A dragon with L<=4 and id>1 (never a queen), with nothing eaten or explored for UPE_HUNGER rounds and no walkable food within 16 steps (a remembered pearl, or a spawn due when we'd arrive), sets exploreDesire. The existing UNK_EXPLORE machinery does the rest: a door lure, a sonar knock, crossing only on a clean echo, a per-edge cooldown, and learnDest records the exit. Scouts are rationed without new sonar traffic: (id + round/UPE_SLOT) % UPE_MOD == 0, and no ally head within 3. Learned or seen pairs go into pathing only through the UNK_SCARCE_FIX gate. Pairs become known from vision after the crossing, so no separate "use learned portal" path was added; this keeps the LEARN_PORTALS over-crossing risk out. On Stripes it barely fires, because some walkable food always exists. UPE_TRACE_DIR=dir writes the fire events to dir/upe.txt.
- logPending: LOG lines made in analyse() survive decide()'s out.clear().

## Mechanism (Stripes, cand vs q36, both sides)
| variant | W | eats cand / q36 | crossings cand |
|---|---|---|---|
| q36 vs q36 (s1-2) | 2/4 (side) | 4-22 | 0 |
| LEARN_PORTALS=1 | 4/4 (r57-88 elim) | 36-93 / 1-8 | 20-50 |
| UNK_SEALED_FOOD=1 | 4/4 | 24-76 / 13-26 | 0-4 |
| sc1 UNK_SCARCE_FIX | 8/8 (s1-4) | 21-141 / 1-18 | 10-64 |
| sc2 (+USF_RICH 4) | 4/4 | 30-134 / 1-17 | 11-52 |
Real Sprint winners ate 43-275 per game, so sc1/sc2 are now in that range.

## Eval vs variants/q36 (unseen_eval --seeds 2 --jobs 3 --seed-base 181000, gen,lesson,gated,sprint +holdout)
| variant | gen | lesson | gated | sprint | holdout | pooled |
|---|---|---|---|---|---|---|
| sc1 SCARCE_FIX (no rich test) | .494 | .479 | .475 | .589 | .512 | .504 |
| sc2 SCARCE_FIX + USF_RICH=4 | .500 | .490 | .500 | **.607** | .487 | .505 |
| sp1 PORTAL_EXPLORE (hunger 12, mod 3) | .475 | .500 | .487 | .518 | .438 | .475 |
| sp2 PORTAL_EXPLORE (hunger 25, mod 4) | .469 | .500 | .512 | .554 | .531 | .507 |
| scp (sc1+sp1) | .475 | .479 | .438 | .607 | .463 | .480 |
| scp2 (sc2+sp2) | .469 | .490 | .525 | **.661** | .525 | **.516** |
sc1 per map (4 seeds, sprint + gated): stripes 8/8, australia 5/8, g2027_13 8/8, islands_a 1/8, islands_b 2/8, g2026_23 2/8, g2026_28 3/8. Every other map was 4/8 (gate never fired, so the games were mirror-identical).
Sandbox CPU for scp2: vault_c max 9.4M/turn, Stripes 5.3M.

## Recommendation
- UNK_SCARCE_FIX=1 (USF_RICH=4, now the default in bot/params.hpp) is the core fix. On Stripes it turns a coin flip into 8/8 locally, and every other set stays within noise, because it only fires where portal-only food is much richer than walkable food.
- The best combination is scp2: UNK_SCARCE_FIX=1 + UNK_PORTAL_EXPLORE=1 with UPE_HUNGER=25, UPE_MOD=4. It scored pooled .516 and sprint .661, with no set clearly below .5 (gen .469 is inside the CI). UNK_PORTAL_EXPLORE alone is noise-level (sp1 .475, sp2 .507), and with the eager settings (hunger 12, mod 3) it hurts. If both flags ship, use the hunger 25 / mod 4 settings. A fresh-seed confirmation of scp2 vs sc2 is the next step.
- Flags off: sc0 (bot/ with q36 values) vs q36 replays are byte-identical apart from the 3-byte bot path (Stripes, vault_a, seed 5).
