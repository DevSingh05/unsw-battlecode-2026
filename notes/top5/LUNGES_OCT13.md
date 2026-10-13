# Long dragons and lunges: aAah (#1) and larp stock zi balls (#2), 13 Oct 2026

Read-only replay study: nothing in bot/, variants/, tools/ changed, nothing uploaded or challenged, no local games; scripts,
data and the 110 downloaded replays (limit 120) are in `work/top_oct13/lunges/`. The teams' "rules" are inferred from frequencies.

**Answer.** Neither team hunts long dragons and neither holds units at length 5-7 on purpose; both kill long dragons with an
on-the-spot lunge when an enemy head of 8+ is inside a small unit's 7x7 view and inside its step budget. aAah lunges to
its full reach (41-51% of chances at 3 steps, 36% at 4, 26-32% at 5, with any unit not longer than the target); larp
stops at exactly 3 steps (25-34% at 3, 0-1% at 4+) and uses only units of 2-4. On defence the two differ completely.
aAah does not keep its long dragons alive: they are rammed 4.0-4.2 times per 1000 long-dragon turns (ours 5.3-6.6),
340-410 length a game on the dense maps; it carries 14-18 dragons of 8+ where we carried 5-6. larp's are rammed 0.8-1.2
times per 1000 turns, 44-52 length a game from about as many long-dragon turns as ours.
The clearest behaviour we lack: a larp dragon of 8+ whose turn starts with a visible enemy head within about 3
steps makes a reverse split (keeps 2, the long part's head is now the old tail) in 77-81% of cases when a unit slot is
free; we do it in 10%. It does not explain the whole gap: larp's long heads also start a turn inside a reach five times
less often than ours, and why was not determined (section 6). 42-44% of our rammed long dragons started their last turn
inside an enemy's reach, in three cases of four with the killer's head in their own view; larp's rate in that class is
about a tenth of ours. From r250 larp also has few dragons of 5-16 left to lose (5-6, from 16 at r200; fed to 3-4 kings).

## 0. Samples and definitions
- **Dense maps** (where dragons of 8+ exist in number): Metro, Athena, Hive, Maelstrom, Ouroboros, Detention, Troll
  Australia, Around UNSW, Whale Song, Ezam, Slithery Fight, Islands. All tables use these 12 maps.
- aAah: 61 games of 10-12 Oct (the `work/top3_oct12/aaah` sample; 3-7 per map) and 69 games of 13 Oct 17:19-20:11 UTC
  (1:19-4:11 PM EDT; 24 v larp, 23 unranked v FTM / SSS, 22 ranked v others). larp: 47 games of 10-12 Oct and 65 of
  13 Oct (24 v aAah, 29 v SSS / FTM, 12 v others; 17 ranked). Us: 244 games of 13 Oct 07:02-18:56 UTC (km12-13) and 109
  of 18:56-20:09 UTC (km14-15); 190 of the 353 are against dev test 1, which lunges more than the rest (31 / 19 / 18%
  of chances at 3 / 4 / 5 steps against 19 / 7 / 7%).
- "8+ turn" = one turn of one non-queen dragon of 8 or more segments. reach(L) = ceil(L/4) + L - 2. "Inside a reach" =
  an enemy head can walk to our head over free tiles in d steps with d <= its reach and d <= 6 (pearls not counted).
  "In view" = Chebyshev distance 3 or less. "Reverse split" = parent keeps 2-3, the reversed child is the long part.
- Rates are per 1000 8+ turns (the teams hold very different numbers of long dragons); per-game figures are means over
  maps, each map weighted equally. "Field" = the studied team's opponents in the same games. km12-13 and km14-15 differ
  in maps and opponents (ladder draw, then the DEV loop), so the two rows are not a before/after test of km14.

## 1. Unit-length profile and split rule
Mean units per game by length, dense maps, the team / its opponents in the same games (10-12 Oct samples; aAah n=61,
larp n=47, us km12-13 n=244). 13 Oct samples, 8+ dragons at r200 / r300 / r400: aAah 14.3 / 15.1 / 16.4, larp 8.8 / 5.7 / 4.4.

| round | team | units | L2 | L3 | L4 | L5-8 | L9-16 | L17+ |
|---|---|---|---|---|---|---|---|---|
| r100 | aAah | 55 / 42 | 17.9 / 21.9 | 16.2 / 12.5 | 6.0 / 3.4 | 9.5 / 2.8 | 4.3 / 1.0 | 0.7 / 0.1 |
| r100 | larp | 54 / 48 | 24.7 / 24.1 | 15.1 / 15.2 | 5.7 / 3.5 | 6.3 / 3.1 | 1.6 / 1.4 | 0.1 / 0.2 |
| r100 | us | 54 / 46 | 25.7 / 22.9 | 15.7 / 14.6 | 5.8 / 3.6 | 5.5 / 3.5 | 1.1 / 0.8 | 0 / 0.1 |
| r150 | aAah | 58 / 44 | 15.0 / 21.7 | 13.3 / 13.2 | 7.2 / 3.4 | 12.6 / 4.1 | 7.5 / 1.4 | 2.7 / 0.3 |
| r150 | larp | 59 / 50 | 22.6 / 23.6 | 15.7 / 15.3 | 6.1 / 3.7 | 8.3 / 4.6 | 5.0 / 2.2 | 0.9 / 0.4 |
| r150 | us | 57 / 52 | 25.6 / 24.3 | 15.8 / 15.8 | 5.9 / 4.6 | 6.4 / 5.2 | 2.8 / 2.0 | 0.2 / 0.4 |
| r200 | aAah | 59 / 45 | 13.4 / 21.2 | 11.5 / 13.7 | 7.3 / 3.2 | 13.5 / 4.3 | 9.2 / 1.9 | 4.1 / 0.5 |
| r200 | larp | 60 / 50 | 20.7 / 23.2 | 14.6 / 15.2 | 6.4 / 4.4 | 10.5 / 4.3 | 6.0 / 2.3 | 2.0 / 0.7 |
| r200 | us | 58 / 56 | 25.1 / 24.9 | 16.0 / 16.5 | 6.1 / 4.8 | 5.9 / 5.9 | 3.8 / 2.7 | 0.6 / 0.8 |
| r300 | aAah | 59 / 43 | 14.4 / 21.5 | 9.9 / 13.2 | 6.8 / 3.5 | 12.3 / 2.9 | 9.6 / 1.5 | 5.7 / 0.9 |
| r300 | larp | 57 / 48 | 28.0 / 23.4 | 15.6 / 14.9 | 4.5 / 3.8 | 3.3 / 2.9 | 2.3 / 1.9 | 3.4 / 0.9 |
| r300 | us | 55 / 57 | 24.4 / 25.2 | 14.9 / 16.0 | 5.4 / 4.9 | 5.1 / 6.1 | 3.8 / 3.3 | 1.4 / 1.5 |
| r400 | aAah | 59 / 37 | 14.5 / 17.9 | 10.4 / 10.9 | 7.1 / 2.8 | 11.6 / 2.5 | 9.6 / 1.5 | 5.9 / 1.3 |
| r400 | larp | 49 / 39 | 24.6 / 16.9 | 14.0 / 11.3 | 3.3 / 3.8 | 2.1 / 3.8 | 1.5 / 2.0 | 3.4 / 1.2 |
| r400 | us | 42 / 43 | 20.6 / 16.5 | 12.9 / 11.1 | 2.6 / 4.2 | 1.5 / 5.1 | 1.7 / 3.1 | 2.8 / 3.1 |

- **r50** (units; L2 / L3 / L4 / L5-8): aAah 35 (18.6 / 12.6 / 2.8 / 1.0), larp 32 (19.7 / 10.3 / 1.5 / 0.2), us 39 (24.2 /
  12.1 / 2.2 / 0.4); opponents 26, 31, 30. Nobody has more than 0.1 dragons of 9+.
- **Dragons of 8+ at r200 / r300 / r400:** aAah 16.0 / 17.8 / 17.7, larp 9.5 / 6.3 / 5.1, us 5.2 / 6.1 / 4.8 (field 3-7).
  Units of exactly 5-7: aAah 10.8 at r200, larp 9.0, us 5.0. The histogram is smooth, with no pile-up at 5-7.
- **Split rule below 40 units** (non-queen splits): 75-87% happen at length 4 (field 67-81%), parent keeps 2 in 91-99%.
- **aAah appears to stop growth splits at about 56 units.** At 56-61 units only 16-19% of its splits are at L4 and 49-54% are
  at L8+ (us 54-65% at L4, larp 56-64%); 51-52% are reverse splits. So its units grow from about r100 and the count stays
  at 55-59. aAah's 8+ dragons make 313-316 splits a game, 96% with no enemy near: these are turn-arounds.
- **larp keeps splitting at 4 up to the cap** (56-64% at L4 with 56-61 units, 34-38% at 62-63) and then, from r250,
  removes its mid-size units by suicide: L5-16 falls from 16.5 units at r200 to 5.6 at r300, L17+ rises from 2.0 to 3.4.
  So units of 5-7 look like dragons on their way up (aAah) or about to be fed (larp), not a class held on purpose.

## 2. How their long dragons die
### 2.1 Deaths of 8+ dragons (non-queen), dense maps
| side | games | 8+ turns per game | rammed by an enemy head, per 1000 turns (mean over maps) | own body | ally body | suicide | length lost to rams per game | step of the killing move 1 / 2 / 3 / 4+ |
|---|---|---|---|---|---|---|---|---|
| aAah 10-12 Oct | 61 | 6112 | 4.2 (4.0) | 3.7 | 0.4 | 0 | 409 | 34 / 37 / 21 / 8% (n=1547) |
| aAah 13 Oct | 69 | 5549 | 4.0 (3.8) | 2.7 | 0.4 | 0 | 343 | 41 / 31 / 22 / 6% (n=1472) |
| larp 10-12 Oct | 47 | 2603 | 0.8 (0.7) | 2.1 | 1.3 | 7.6 | 44 | 6 / 45 / 32 / 17% (n=94) |
| larp 13 Oct | 65 | 2314 | 1.2 (1.2) | 1.2 | 1.0 | 6.3 | 52 | 22 / 26 / 20 / 32% (n=174) |
| us km12-13 | 244 | 2584 | 5.3 (5.9) | 4.5 | 1.8 | 0 | 266 | 13 / 20 / 35 / 32% (n=2648) |
| us km14-15 | 109 | 3354 | 6.6 (5.9) | 4.5 | 2.1 | 0 | 318 | 15 / 21 / 33 / 31% (n=2722) |
| field v aAah | 61 / 69 | 1018 / 1207 | 9.1 / 7.0 | 2.0 / 0.9 | 1.7 / 0.5 | 3.1 / 4.8 | 138 / 140 | 16 / 22 / 27 / 36% |
| field v larp | 47 / 65 | 1428 / 1957 | 7.7 / 6.3 | 2.3 / 2.1 | 1.1 / 0.3 | 1.5 / 1.1 | 169 / 186 | 28 / 40 / 32 / 0% |
| field v us | 244 / 109 | 2583 / 2270 | 3.5 / 5.8 | 1.8 / 0.8 | 0.6 / 0.5 | 3.8 / 3.5 | 208 / 206 | 35 / 65 / 0 / 0%, then 26 / 56 / 8 / 10% |

- Metro alone (games; rammed per 1000 turns; length lost per game): aAah 5 and 6; 8.6 and 4.4; 629 and 447. larp 5 and
  4; 0.8 and 1.2; 41 and 25. Us 25 and 19; 10.5 and 9.2; 472 and 474. larp is lowest on all 12 maps; we exceed aAah on 9.
- In the 40 games between the two: aAah's long dragons die to larp's 1-3 step rams 5.4 times per 1000 turns, larp's to
  aAah's lunges (42% from 4+ steps) 2.6 times. Against our qf1 build (9 and 6 games) the figures were 2.6 and 0.2.

### 2.2 The same ram deaths by the victim's own last turn (per 1000 of the side's 8+ turns; share of its ram deaths)
| class | aAah 10-12 | aAah 13 | larp 10-12 | larp 13 | us km12-13 | us km14-15 |
|---|---|---|---|---|---|---|
| A: its turn started inside an enemy's reach | 0.80 (19%) | 0.85 (21%) | 0.18 (23%) | 0.42 (36%) | 2.22 (42%) | 2.92 (44%) |
| B: it moved into the reach of a head it could see | 0.45 (11%) | 0.84 (21%) | 0.01 | 0.03 | 0.62 (12%) | 0.68 (10%) |
| C: killer in view, end tile outside its no-pearl reach | 0.23 (6%) | 0.24 (6%) | 0.00 | 0.03 | 0.77 (14%) | 0.90 (14%) |
| D: it moved into the reach of a head it could not see | 1.71 (41%) | 1.13 (29%) | 0.35 (45%) | 0.47 (39%) | 0.73 (14%) | 0.92 (14%) |
| E: unseen killer, end tile outside its no-pearl reach | 0.54 | 0.41 | 0.13 | 0.18 | 0.41 | 0.45 |
| N: killer split off after the victim moved, or no record | 0.41 | 0.49 | 0.11 | 0.06 | 0.57 | 0.70 |

- The killer never moves between the victim's last turn and the hit, so at the start of that turn it stood where it
  lunged from. It was in our victim's own 7x7 view in 62-64% of our ram deaths (aAah 26-47%, larp 10-19%), mostly 2
  (18%), 3 (35%) or 4 (32%) tiles away; the hit then came from 3 (40%), 4 (24%) or 5+ (13%) steps.
- **Class A is our gap** (2.2-2.9 against aAah's 0.8 and larp's 0.2-0.4). Our class-A victims took one step (39-42%) or
  sprinted (55-59%), made a reverse split in 2%, and ended at d=3 (28-29%) or d=4-6 (35-38%) from a head that could
  still reach them. A, B and C are no lower in the km14-15 games than before (different maps and opponents).
- **Class C is pearl fuel**: 25-26% of all kills on our long dragons (29% of those with the killer in view) hit beyond
  ceil(L/4) + L - 2, because every pearl on the path is one more step. aAah's dragons face it in 18%, larp's in 11-15%.
- **Class D is aAah's main loss**: a sprint (96-98% of its D victims) that ends next to an unseen unit. larp sprints as
  much (section 4) at 0.35-0.47; we could not determine why beyond the density figures below.

### 2.3 Exposure, and what an 8+ dragon does when its turn starts inside a reach of d <= 3
| side | turn starts inside a reach d<=3 (share of 8+ turns) | turn ends inside a reach | no enemy head within 6 | n (starts d<=3) | one step / sprint / reverse split | ends outside every reach | rammed before its next turn, per 1000, after one step / sprint / reverse split |
|---|---|---|---|---|---|---|---|
| aAah 10-12 | 1.0% | 1.3% | 75% | 4,277 | 20 / 66 / 13% | 82% | 38 / 57 / 32 |
| aAah 13 | 1.3% | 1.5% | 72% | 5,157 | 26 / 61 / 12% | 83% | 44 / 50 / 27 |
| larp 10-12 | 0.5% | 0.8% | 81% | 596 | 17 / 33 / 50% | 84% | 61 / 20 / 10 |
| larp 13 | 0.5% | 1.1% | 82% | 765 | 16 / 32 / 51% | 80% | 119 / 49 / 8 |
| us km12-13 | 2.4% | 3.7% | 61% | 11,452 | 29 / 60 / 11% | 69% | 75 / 56 / 29 |
| us km14-15 | 2.9% | 5.0% | 59% | 12,568 | 29 / 61 / 9% | 66% | 80 / 58 / 26 |
| field (six sides) | 1.6-2.1% | 2.0-5.4% | 60-71% | 1,214-8,015 | 21-32 / 48-61 / 10-26% | 59-81% | 67-145 / 56-131 / 19-44 |

- One step also kills the mover itself (wall, body) 17-101 times per 1000; a reverse split never does. In all twelve
  team-sides the reverse split is followed by the lowest ram rate (8-44 per 1000). This is an association: which
  dragons split is not random, and the split child's window to its next turn is slightly longer.
- **What larp's dragons do** (13 Oct and 10-12 Oct samples, n = 499 and 357): threatening head in view and a
  unit slot free: reverse split in 77% and 81%. Head not in view: 4% and 3%. No slot (64 units): 0%, and then 196 and
  83 rammed per 1000 when no first step leads out (n = 46, 48) against 31 and 17 with a slot (n = 286, 174). The share
  does not depend on the enemy's length (L2 54-63%, L3 56-59%, L4 60-71%, L5-7 59-76%, L8+ 66-72%) nor on its own
  (58-69% for 8-11, 12-19, 20+), and stays at 56-64% when a safe first step exists. At d = 4-6 it is 18-40%.
- Same situation, slot free, head in view: us (km14-15) 10% of 11,152, aAah (13 Oct only) 13% of 4,532. No safe first step:
  us reverse split 16%, ends outside every reach 43%, rammed 91 per 1000 (n = 5,810); aAah 26%, 63%, 71; larp 63-73%,
  70-72%, 17-31.
- **Do they retreat?** Everyone does, we most of all: with the threatening head in view at d = 2 / 3 our dragon ends
  further from it in 95-96% / 82% of turns (aAah 76-80% / 60-62%, larp 77-79% / 84-85%). One tile further is still
  inside reach: we are rammed 44-50 per 1000 after moving "further", larp 8-43.
- **Small allies in between?** A small ally (2-4) head nearer to the nearest enemy than the long head: larp 23-24% of
  turns with an enemy within 6, us 15-16%, aAah 10%; the ram rate is then a third (us 3.7-4.6 against 13.5-15.9 per 1000). Placed or by chance: not determined.
- **Regions with few enemies?** Yes for larp (81-82% of 8+ turns have no enemy head within 6; us 59-61%), on every
  map, but not by staying home: 51-54% of 8+ turns are on the own queen's half for all three teams and the ram rate is
  the same on both halves (us 4.9 home, 5.3 away). **No mid-size dragons?** Only larp, and only after r250.

## 3. Their kills on enemy long dragons
### 3.1 Head-on kills on enemy dragons of 8+ (the killer moved), dense maps
| killer side | per game | per 1000 enemy 8+ turns | killer length 2 / 3 / 4 / 5-7 / 8+ | step of the hit 1 / 2 / 3 / 4 / 5 / 6+ | needed paid steps (median paid) | killer to victim 1 / 3 / 5 rounds before (median tiles) | length killed per own length |
|---|---|---|---|---|---|---|---|
| aAah 10-12 (n=577) | 9.5 | 9.1 | 14 / 22 / 18 / 26 / 21% | 16 / 22 / 27 / 20 / 11 / 5% | 74% (2) | 6 / 10 / 12 | 2.7 |
| aAah 13 (n=594) | 8.6 | 7.0 | 14 / 22 / 17 / 26 / 21% | 16 / 21 / 25 / 23 / 10 / 5% | 77% (2) | 6 / 9 / 12 | 3.1 |
| larp 10-12 (n=478) | 10.2 | 7.7 | 26 / 49 / 20 / 4 / 1% | 28 / 40 / 32 / 0 / 0 / 0% | 70% (1) | 6 / 8 / 10 | 4.9 |
| larp 13 (n=801) | 12.3 | 6.3 | 27 / 51 / 16 / 5 / 1% | 35 / 38 / 27 / 0 / 0 / 0% | 64% (1) | 5 / 8 / 10 | 4.6 |
| us km12-13 (n=1759) | 7.2 | 3.5 | 19 / 56 / 16 / 8 / 1% | 35 / 65 / 0 / 0 / 0 / 0% | 57% (1) | 5 / 8 / 10 | 4.9 |
| us km14-15 (n=1474) | 13.5 | 5.8 | 14 / 48 / 18 / 18 / 2% | 26 / 56 / 8 / 5 / 3 / 2% | 67% (1) | 5 / 8 / 10 | 4.4 |
| field v us (n=5370) | 10.9, then 25.0 | 5.3, then 6.6 | 13 / 31 / 22 / 26 / 7% | 13 / 20 / 35 / 18 / 10 / 3% | 84% (2) | 5 / 7 / 9 | 3.6 |

- In every sample 95-99% of these kills start with the victim's head inside the killer's 7x7 view and 100% hit on the
  last planned step: no blind lunges and no accidents. 7-16% of killers were split off 3 rounds or less before.
- Share of chances taken, units of length 3-7 with a visible 8+ head inside reach, by walking distance d = 1 / 2 / 3 /
  4 / 5 / 6: **aAah 78 / 68 / 41 / 36 / 32 / 18%** (n = 34-195) and 77 / 66 / 51 / 37 / 26 / 15% on 13 Oct; **larp
  78 / 65 / 34 / 0 / 1 / 0%** and 82 / 64 / 25 / 1 / 1 / 2% (n = 17-400); us km12-13 69 / 64 / 0 / 0 / 1 / 0%
  (n = 223-1756), km14-15 63 / 59 / 7 / 5 / 6 / 5%; field v us 60 / 46 / 29 / 14 / 12 / 5%.
- **aAah by lengths** (share of chances taken at d = 2-3, 10-12 Oct / 13 Oct; n >= 15 per cell):

| own length | target L2 | L3 | L4 | L5 | L6-7 | L8-11 | L12-19 |
|---|---|---|---|---|---|---|---|
| 3 | 18 / 20% | 36 / 40% | 61 / 69% | 66 / 78% | 76 / 67% | 73 / 80% | 85 / 78% |
| 4 | 12 / 12% | 25 / 29% | 42 / 38% | 36 / 42% | 60 / 44% | 63 / 63% | 55 / 59% |
| 5 | 3 / 3% | 9 / 8% | 19 / 22% | 33 / 58% | 32 / 32% | 42 / 44% | 38 / 38% |
| 6 | 1 / 1% | 4 / 3% | 9 / 23% | 24 / 26% | 44 / 32% | 38 / 30% | 39% / - |
| 7 | 0 / 0% | 0 / 2% | 9 / 10% | 12 / 9% | 32 / 15% | 19% / - | 28 / 25% |
| 10+ | 0 / 0% | 0 / 0% | 1 / 0% | 0 / 0% | 3 / 1% | 4 / 4% | 13 / 7% |

  The rate jumps where the target is about as long as the unit or longer; at d = 4-6 a length-5 unit still takes
  22-28% (target L5), 26-34% (L8-11) and 34-48% (L12-19). larp on 13 Oct: length 3 takes 72-83% of targets of 4+,
  length 4 takes 23-37%, length 5 takes 9-24% at d = 2-3 and 0-1% (n = 491) at d = 4-6.
- **No sign of a hunt** (one test: drift over 5 rounds from 4-10 tiles; a hunt on shared sonar would not show). A unit
  of 2-3 that starts 4-6 tiles from where an enemy head stood ends, 5 rounds later, +1.98 tiles further if that head was L2-3, +1.94 if L8-15, +2.00 if L16+ (aAah, n = 280-13,612; 13 Oct +2.48 / +2.51 / +2.81);
  larp +1.53 / +1.51 / +1.68 and +1.64 / +1.54 / +1.48. The share closing 3+ tiles is flat across target classes (7-13%).
- **What the killer did before:** its own distance to the tile of the hit 1 / 3 / 5 rounds earlier is 4 / 5-6 / 6-7 for
  aAah and 3 / 4 / 5 for larp and for us; 61-62% of larp's killers were within 4 tiles of that tile three rounds
  earlier (aAah 32-34%). In 42-47% of both teams' kills the victim's head entered the killer's view on its own last move.

## 4. Other differences in the head-on domain
| side (dense) | head-ons made on enemies per game | own length spent | enemy length killed | ratio | steps 1 / 2 / 3 / 4+ | head-ons on allies per game |
|---|---|---|---|---|---|---|
| aAah 10-12 / 13 | 92 / 103 | 323 / 355 | 390 / 413 | 1.21 / 1.16 | 39 / 26 / 19 / 15% | 1.7 / 1.6 |
| larp 10-12 / 13 | 124 / 139 | 341 / 375 | 480 / 538 | 1.41 / 1.44 | 43 / 37 / 20 / 0% | 0.2 / 0.3 |
| us km12-13 / km14-15 | 74 / 99 | 209 / 304 | 302 / 475 | 1.45 / 1.56 | 53 / 46 / 0 / 0% | 0.8 / 1.0 |
| field v aAah / v larp / v us | 110 / 97-106 / 88-123 | 315-326 / 297-326 / 286-416 | 598-653 / 288-323 / 421-718 | 1.9-2.0 / 0.97-0.99 / 1.47-1.73 | | 1.2-3.2 |

- **larp rams whatever comes within 2 steps.** Share of chances taken on an adjacent / 2-step enemy head of L2-3: larp
  41-42% / 23-24%, us 24-30% / 12-16%, aAah 28-29% / 9-10%; on a head of L4-7 (the lungers): larp 78-80% / 46-49%, us
  47-56% / 26-30%, aAah 56-60% / 26-27%. It is the only side whose opponents trade below 1.0 against it.
- **aAah's lunges at everything are not efficient**: 1.16-1.21 overall, and 21% of its kills on long dragons cost a unit of 8+.
- **Their long dragons move faster.** Mean steps per turn at L8-11 / L12-19 / L20+: aAah 1.9-2.1 / 2.3-2.6 / 2.4-2.9,
  larp 1.9-2.0 / 2.4-2.5 / 2.7, field 1.7-1.9 / 2.0-2.4 / 2.0-2.6, us 1.5 / 1.7 / 1.7. A single step is 22-34% of
  their turns and 49-50% of ours. Paid steps by 8+ dragons are under 1% of turns for everyone: nobody pays to flee.
- **Our long dragons also die more on their own and allied bodies** (4.5 and 1.8-2.1 per 1000 turns; aAah 2.7-3.7 and
  0.4; larp 1.2-2.1 and 1.0-1.3). We make 83-145 splits of 8+ dragons a game, aAah 313-316, larp 143-169.

## 5. Rules to implement (ranked by expected value)
1. **Threat split (larp).** *Condition:* non-queen dragon of 8+; an enemy head in its 7x7; that head can walk to ours
   in d <= 3 steps (d <= 6 if no end tile within our free steps is outside every visible reach); team has a free unit
   slot. *Action:* split, parent keeps 2; the reversed long part moves later the same round with its head at the old
   tail. *Evidence:* larp 77-81% (n = 856) against our 10% (n = 11,152); followed by 8-44 rams per 1000 in all twelve
   team-sides against 20-131 after a sprint and 38-145 after one step (association, see 2.3); class A is 42-44% of our rammed long dragons
   and larp's class-A rate is 0.18-0.42 against our 2.2-2.9. *Size (estimate, unverified):* at larp's rates in the same
   situations, 5-8 fewer rammed long dragons of about 16 a game in the km14-15 games, a fifth to a third of that loss.
   *In our code (params.hpp comments only; main.cpp not read):* the `BIG_RESERVE` turn-around split. *Check:* `cats.py` class A.
2. **Reach is a full threat for the END tile, with pearls, and one step is not an escape.** *Condition:* dragon of 8+,
   candidate end tile T of the whole move, visible enemy head E with walking distance d to T and
   d <= ceil(L_E/4) + L_E - 2 + (pearls on that path). *Action:* penalty of the adjacent-head penalty times 1.0 / 0.5 /
   0.4 / 0.1 for d = 1 / 2 / 3 / 4-6; if no candidate is outside every reach, rule 1. *Evidence:* our 8+ heads are
   rammed before their next turn 421-462 / 210-222 / 146-181 / 37-41 per 1000 after ending at d = 1 / 2 / 3 / 4-6 and
   1.7-2.0 outside (n = 904,000 turns); classes B + C are 24-26% of our ram deaths, larp's B + C is 0.01-0.06 per 1000
   against our 1.4-1.6. The weights are our own hazard ratios; no team was shown to use them.
3. **Lunge to the full reach when the target is at least as long as the unit (aAah), or to 3 steps with units of 3-4
   (larp).** *Condition:* non-queen unit of length <= 7; enemy head in view; a certain path of d steps with
   d <= own reach + pearls on it; visible target length >= own length + 2 (aAah takes equal lengths; the margin is
   ours, unverified). *Action:* take the head-on. *Evidence:* chances taken at d = 3 / 4 / 5: aAah 41-51 / 36-37 /
   26-32%, field 18-29 / 4-19 / 6-15%, us km14-15 7 / 5 / 6% (n = 1220 / 790 / 602), about a sixth of aAah's; which
   `KING_KILL` condition (`KK_MIN_VIS=9`, the certainty test, own length) blocks the rest was not checked; kills per 1000 enemy 8+ turns: aAah 7.0-9.1, larp 6.3-7.7,
   us 3.5 then 5.8. Keep `KK_OWN_MAX` at 5-7: aAah's units of 8+ make 21% of its long kills (return 2.7-3.1, larp 4.6-4.9).
4. **Small units take every 1-2 step head-on on an enemy unit of 4-7.** *Condition:* own length 2-3, enemy head of
   L4-7 at walking distance 1-2 (inside reach). *Action:* ram. *Evidence:* larp 78-80% / 46-49% against our 47-56% /
   26-30%; units of 4-7 make 48% of the kills on our long dragons. That this is why larp's long heads meet fewer
   enemies is unverified. *In our code:* `RAM_GUARD` restricts even trades; this is a 2-3 for 4-7 trade.
5. **Keep two unit slots free once rule 1 is live.** *Condition:* team at 62+ units. *Action:* no growth split.
   *Evidence:* larp with no slot makes no threat split and is rammed 83-196 per 1000 (n = 48, 46) where it is rammed
   17-31 with one. We had a slot in nearly every threatened turn of km14-15, so this matters only after rule 1.
6. **Long dragons use their free steps (unverified as a cause).** *Action:* take ceil(L/4) steps, end tile by rule 2.
   *Evidence:* section 4 speeds. Counter-evidence: sprints into unseen units are aAah's largest loss (class D).

## 6. Not verified, and how this was run
- Why larp's long heads meet fewer enemies (81-82% of turns with none within 6): home side is ruled out, rule 4 and the
  feeding at r250 are candidates. Why larp's class D is a third of aAah's with the same sprint lengths.
- The reach measure ignores pearl fuel and our own tail moving, so "outside every reach" is too generous (classes C, E).
- Rule 1's size uses larp's rates against larp's opponents (dev test 1 lunges more). Rule 3's margin (+2) and rule 6 come
  from distributions, not from an A/B. Nothing here was tested in a game. Sonar: in 24% of our class D/E deaths the
  killer stood on the victim's row or column 4+ tiles away; not followed up.
- 71 of the 110 games of 13 Oct are unranked games among aAah, larp, FTM and SSS; only 22 + 17 rows are ranked.
- The simulator ran three times as counters were added: tables use `cache3/` (13 Oct samples, larp 10-12 Oct, us km14-15)
  and `cache2/` (aAah 10-12 Oct, us km12-13); the slot / safe-step breakdown of 2.3 does not exist for those two.
- The 13 Oct listing (about 55 GETs, paced 1.4 s) was read from the public games page with urllib, as the
  `work/top3_oct12/*/crawl.py` scripts do, not through `tools/api.py`; only the replay downloads used `tools/api.py`.

## 7. Rerun (from `/Users/devsingh/Developer/UNSW_Battlecode`; 2 worker processes; an hour or more, not timed as one run; tables in `work/top_oct13/lunges/out/`)
```
python3 work/top_oct13/lunges/fetch_new.py            # 13 Oct listing + replays (GET only, paced 1.4 s, cap 112)
LCACHE=cache3 python3 work/top_oct13/lunges/run.py    # lsim.py over all samples -> cache3/ (--only top|uskm14|new)
python3 work/top_oct13/lunges/q1.py dense             # 1;  q2.py dense: 2.1, 2.3;  cats.py me|op: 2.2;  q3.py dense: 3, 4
python3 work/top_oct13/lunges/explore3.py thr dense   # 2.3 actions; also opp2 ret mv home h2h;  permap.py me|op: per map
```
