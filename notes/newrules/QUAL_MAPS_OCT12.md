# The 14 Qualifier maps on the ladder (12 Oct 2026)

Times are US Eastern unless marked UTC. Commands run from `/Users/devsingh/Developer/UNSW_Battlecode`.
Scripts: `tools/analysis/oct12/`. Data, replays and staged builds: `work/oct12/` (gitignored).

## 1. What the ladder showed

Live build on 12 Oct 1:55 PM: qf1 (id 21001), 2177, #25. The 14 Qualifier maps joined the ranked pool on 10 Oct
(31 maps now), and qf1 still played all 14 as unseen maps.

Our last 200 series (1,015 games, 10 Oct 9:31 AM to 12 Oct 1:47 PM), win rate against the Elo expectation:

| group | games | W-L | win % | expected % | diff |
|---|---|---|---|---|---|
| 14 new maps | 423 | 192-231 | 45 | 54 | -8 |
| 17 old maps | 592 | 335-257 | 57 | 52 | +4 |

Worst maps: Atlantis 6-24 (-37), Whale Song 11-22 (-22), Around UNSW 11-21 (-21), Maelstrom 12-19 (-20),
Troll Australia 11-20 (-19), Slithery Fight 12-19 (-18), Trolley Problem 10-17 (-15), Devil 11-18 (-12),
Trophy 19-29 (-11), Trolley Problem (Buffed) 12-18 (-10). Best: Trauma 26-1, Tower Defense, Portals, Stripes, Default.
Full table: `python3 tools/analysis/oct12/series_report.py` (after `fetch_series.py`).

## 2. Why the new maps were weak

1. **Atlantis: we starved.** 96% of the food (6.4 of 6.6 pearls per round) is behind portals. An unseen-map dragon
   treats unknown portals as kelp, so we ate about 140 pearls against about 1,800 in a sample loss to a 1,965-rated team,
   and had a median of 7 units at r100 in our losses.
2. **Maelstrom and Troll Australia: slow start.** In our losses we had 25 units at r100 against 61 (length ratio
   0.24 and 0.37). Opponents who know the pearl tiles reach the unit cap by r100.
3. **Wrong map adopted.** Four new maps share every start tile with an older map, and the first difference is 4 to
   23 steps from the starts: Ezam = Maze (and Trauma), Detention = Schooltime, Troll Australia = Australia,
   Trolley Problem (Buffed) = Trolley Problem. In a traced Ezam game qf1's queen played the Maze module on all 455 of her turns.
   On the three new 64x64 maps split children also adopted Around UNSW, Australia or Big Empty in open views.
4. **The queen, as before.** On the seven worst maps our queen was alive at the end in 9 of 214 games; the opponent's
   in 78 of 214. "Our queen dead, theirs alive" decided 71 of 141 losses. Opponents split the queen at round 0
   (median first split r0; ours r41 to r137). Not addressed by this change except on Atlantis.

## 3. The change: QUAL_KNOWN and friends (all in `bot/`, default 0)

`bot/maps_data.hpp` now holds 47 maps: the old 33 unchanged and in the same order, then the 14 Qualifier maps
(`tools/analysis/oct12/append_maps.py` regenerates it byte for byte from `variants/qf1/maps_data.hpp`).

| flag | what it does |
|---|---|
| `QUAL_KNOWN` (bit mask) | Bit i adopts Qualifier map i as a known map and treats it like a Sprint map (UNK_KING seed and feed, small-map ram guard, SPRINT_KING_FULL). Bit order = `QUAL_MAPS` in main.cpp: Athena 0, Atlantis 1, Caution 2, Detention 3, Ezam 4, Hive 5, Maelstrom 6, Metro 7, Ouroboros 8, Thermopylae 9, Troll Australia 10, Trolley Problem 11, Trolley Problem (Buffed) 12, Whale Song 13. A map with its bit off is not even a candidate, so it plays as in qf1. |
| `QUAL_ROUTE` (mask) | PEARL_ROUTE valuation stays on for that known map (what SPRINT_ROUTE does). |
| `QUAL_QEKR` (mask) | QE_KR stays on for that known map (qf1 played these maps with it on). |
| `QUAL_GOSSIP`, `QUAL_GOSSIP_R` | Map word on the idle sonar: a dragon that has adopted a Qualifier map and has no other candidate left names it on split turns and on idle turns before round 200; a listener that still holds that map as a candidate adopts it. Only Qualifier-map adopters send it. |
| `QUAL_CROWD`, `QUAL_CROWD_V` (mask) | Crowd penalty on that known map. |
| `QUAL_QPARK` (mask) | Portals-style queen park (RP.qPark 1, crowned at the seed round) on that known map. |

Checks:
- **Old maps keep their map.** Adoption audit (`adopt_audit.py`, SPRINT_DEBUG build, both seats): on all 17 old maps
  plus Schooltime B x3 no process ever adopted a Qualifier map (map word off). With the map word on, the same holds
  on the seven layouts that share a size with a Qualifier map (Maze, Trauma, Schooltime, Schooltime B and B3,
  Australia, Around UNSW).
- **Flags off = qf1.** Full-transcript identity against qf1 on 8 maps x 2 seats: 15 of 16 match; the one difference
  is a same-destination move order (MOVE NW vs WN) at r355 on Maze. The search budgets run on the CPU-points clock,
  so any compiled difference can flip a tie on a heavy turn; this is why builds with the flags on cannot be
  transcript-identical on old maps and the adoption audit is the check that matters.
- **CPU and memory.** Max 39.0M points per turn (limit 100M), 1.6 MB (limit 48 MB).
- **Map word.** Processes that began with the wrong look-alike: Ezam 268 -> 136 of about 1,000 (never corrected
  212 -> 54; the queen now corrects at r14 to r44), Troll Australia 441 -> 181, Detention 130 -> 55.

## 4. Known is not better everywhere

Local games against qf1 (both seats per seed, `games.py` + `score.py`; `mech.py` for the mechanism columns).
"Known" = all 14 bits on, route on, map word on.

| map | known vs qf1 | known + crowd vs qf1 | pearls eaten known / qf1 | units r100 | note |
|---|---|---|---|---|---|
| Whale Song | 4-0 | | 1,452 / 999 | 52 / 35 | |
| Troll Australia | 4-0 | | 2,178 / 966 | 53 / 19 | |
| Atlantis | 4-0 | | 2,495 / 79 | 57 / 10 | see section 5 |
| Caution | 4-0 | | 332 / 220 | 7 / 5 | qf1 is already +12 on the server; left alone |
| Maelstrom | 3-1 | | 3,506 / 943 | 62 / 28 | |
| Ezam | 3-1 | | 2,693 / 1,004 | 50 / 32 | server is at par; next round |
| Athena | 2-2 | 3-1 | 4,175 / 2,701 | 62 / 63 | |
| Hive | 2-2 | 2-2 | 4,410 / 2,351 | 63 / 57 | |
| Ouroboros | 2-2 | 2-2 | 3,594 / 2,202 | 60 / 63 | |
| Detention | 1-3 | 2-2 | 4,168 / 2,784 | 63 / 36 | queens sit in sealed 2x2 rooms: longest dragon decides |
| Thermopylae | 1-3 | 1-3 | 546 / 494 | 17 / 23 | known total length r300 41 vs 150 |
| Metro | 0-4 | 3-1 | 2,643 / 1,842 | 62 / 35 | close games |
| Trolley Problem | 0-4 | 0-4 | 648 / 3,048 | 13 / 21 | known units never leave the first pocket |
| Trolley Problem (Buffed) | 0-4 | 0-4 | 1,250 / 2,870 | 20 / 13 | same |

- The known build eats far more and hits the unit cap by r100 on most maps, then loses much more length to
  self and ally collisions (Athena 3,844 lost vs 2,313), so by r300 totals are level against qf1. Real opponents
  are strong early, which qf1 is not, so these even maps may still be better known. That is a server question.
- **Trolley Problem** is broken when known: every unit goes to the nearest hot pocket (38-39, 3-8) and stays; the
  unseen-map build spreads over five clusters and eats 4.5x more. The crowd penalty does not fix it.
- **Route valuation** (known route on vs known route off, same seeds): on is better overall (36-20), but off wins
  4-0 on Atlantis and 4-0 on Caution, the two portal-gated maps (as on weakhold).

## 5. Atlantis

| pairing | W-L | what decided |
|---|---|---|
| known, route on vs qf1 | 4-0 | economy |
| known, route off vs qf1 | 1-3 | our queen dies near r100 in the pearl field; qf1's starving queen is alive at L9 |
| known, route on vs known, route off | 0-4 | route on has 7 units at r100 against 40 and is eliminated in 3 of 4 |
| route off + parked queen vs route off | 6-0 | "longer queen 4 to 0" (4) or elimination (2); our queen alive 6 of 6, theirs 0 of 6 |
| route off + parked queen vs qf1 | 5-5 | qf1's units roam our home region and ram the parked queen around r240 to r340 |

Against an opponent that also fights for the pearl field, route off is the only version with an economy, and the
parked queen wins the tiebreak. The parked queen stays at L4 (she eats nothing and no feeder reaches her), so she
still loses to a live queen that is longer. Next step there: let her grow.

## 6. km1 (uploaded Mon 12 Oct 3:20 PM, id 22249)

km1 = qf1 + `QUAL_KNOWN=0x2442` (Atlantis, Maelstrom, Troll Australia, Whale Song) + `QUAL_ROUTE=0x3FFD` (route off
on Atlantis) + `QUAL_GOSSIP=1` + `QUAL_QPARK=0x2` (Atlantis). The other 27 maps play as qf1. Copy: `variants/km1`.
Chosen because these four are both the weakest new maps on the server and clear local wins.

- Fresh seeds against qf1 on the four maps: 11-5 (Whale Song 4-0, Maelstrom 3-1, Troll Australia 3-1, Atlantis 1-3).
- Fallback: re-activate qf1 (id 21001).
- Server check: `python3 tools/analysis/oct12/build_watch.py 2026-10-12T19:20:06 --maps "Atlantis,Maelstrom,Troll Australia,Whale Song"`.
  qf1's record on these four maps over the two days before: 40-85 (32%, expected 56%).
- An unranked loop restricted to these four maps runs against ranks 14 to 44 (`replays/auto_km1/`; stop with
  `touch replays/auto_km1/STOP`).

## 7. Next candidates

1. Atlantis queen growth (eat the home pearls while parked, or keep the park all game).
2. Ezam known (local 7-3 over three runs; fixes the Maze mix-up).
3. Athena, Hive, Metro, Ouroboros, Detention known with the crowd penalty (local 12-8 with it, 7-13 without).
4. Trolley Problem x2: find why known units stay in one pocket; until then they stay unseen maps.
5. Detention: both queens are sealed in at L4, so only the longest dragon counts.
6. The queen on the old weak maps (Around UNSW: our queen dead and theirs alive in 15 of 21 losses).
