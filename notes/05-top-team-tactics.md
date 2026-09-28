# 05 - Top-team tactics from public replays (quantitative)

Data: 40 replays of games played 2026-09-26/27 (challenge and ranked games, both teams Elo ≥ 1980), 4 per ranked map.
Teams in the sample: Sabotage-d (32 games), 龙虎豹 (21), Vibing++ (9), SHINK AI 6500 (6), STAR (4), 中国人能飞 (4), Sponge (3), Peanut Butter (1).
Files:
- Replays: `notes/replays/<matchId>.replay`, plus `index.json` (teams and map per match). `*.sim.pkl` files are caches.
- Tools in `notes/tools/`:
  - `list_games.py`: devalue-decodes `/games/__data.json`.
  - `fetch_replays.py`: downloads the replays.
  - `replay_sim.py`: full state reconstruction (bodies, portals, eats, kills). It reproduces the final result exactly on all 40 replays.
  - `analyze_top.py`: the main report, and it builds the cache.
  - `king_analysis.py`, `timeline.py`, `per_map.py`, `load_cache.py`.

Re-run: `cd notes/tools && python3 analyze_top.py > /tmp/a.txt && python3 king_analysis.py && python3 timeline.py && python3 per_map.py`

---

## 0. The meta in one paragraph
Every top team plays the same two-phase game.
- **Phase 1 (rounds 0 to about 300): swarm.** Every dragon is capped at length 4. At length 4 it immediately does `SPLIT 2` (parent 2 + child 2). A team peaks at 30-64 units of length 2-3. Heads fight by head-on ramming, and dead-end-trapped dragons suicide.
- **Phase 2 (about 300 to 500): consolidation.** One dragon (the king) grows from about 4 to 35-70. Length-2/3 "feeders" walk next to it and kill themselves (mostly `HitSelf` by reversing), so the king eats their pearls. Units drop from about 40 to 3-20.

On the small, closed maps (Trophy, Devil, Prisoners Dilemma, often Queen of Spades and Default) phase 2 never happens. The bigger swarm eliminates the other team by round 95-400.

---

## 1. Splitting policy
**Split distribution.** Share of all splits that are (L=4, k=2):

| team | share | total splits |
|---|---|---|
| Sabotage-d | 85% | 7065 |
| 龙虎豹 | 77% | 4676 |
| Vibing++ | 78% | 2483 |
| STAR | 82% | |
| 中国人能飞 | 84% | |

- Parent length at split: p10-p75 = 4, p90 = 5-6.
- Parent age at split: median 18-24 rounds. The p25 is 3-8 rounds, i.e. a child that eats 2 pearls quickly splits again.

**Rule to copy: at length 4, `SPLIT 2`.** At length 5, top teams do (5,2) or (5,3); at 6, mostly (6,4).

**Reverse split (k = L-2).** This is 5-60% of splits depending on the team. The parent keeps 2 segments and the child keeps the body with its head at the old tail, so it is a **U-turn that costs 2 length**.
- For L ≥ 8 it is almost always done when the head has **0 free exits**:
  - 龙虎豹: 117/129
  - STAR: 79/101
  - Sponge: 157/181
  - SHINK: 766/766
- Sabotage-d also does it with 1-2 exits.
- The leftover length-2 parent usually suicides the next turn (HitWall/HitSelf/HitOtherBody), dropping 1 pearl.
- Implement this as the escape from dead ends instead of dying.

**"Peeling" a long starting dragon.** Slithery Fight (starter of length 25), Autarky (14) and Prisoners Dilemma (11) start with long dragons.
- 龙虎豹, SHINK and Vibing++ do `SPLIT 2` off the big dragon every turn: 23→21→19→…, one new length-2 unit per round.
- Sabotage-d instead halves it on round 0 (15→8+7, 12→7+5).

**Unit count.** Medians over all games:

| round | 50 | 100 | 150 | 200 | 250 | 300 | 350 | 400 | 450 | 499 |
|---|---|---|---|---|---|---|---|---|---|---|
| 龙虎豹 units | 16 | 25 | 33 | 38 | 44 | 46 | 39 | 22 | 11 | 6 |
| Sabotage-d units | 8 | 12 | 17 | 31 | 33 | 27 | 23 | 20 | 12 | 5 |
| Vibing++ units | 14 | 24 | 32 | 41 | 42 | 38 | 23 | 8 | 6 | 4 |

- **64 is reached only on the big maps**:
  - Slithery Fight: rounds 66-142, and even round 328.
  - Schooltime: rounds 91-269.
  - 龙虎豹 once on Autarky (round 284) and Prisoners Dilemma (round 344).
- On other maps the peak is 30-55. The number of pearls available is the limit, not the cap.

**4→2+2 splits per game in 50-round buckets.**
- 龙虎豹: 22, 33, 22, 18, 17, 17, 22, 16, **3, 3**
- Sabotage-d: 18, 29, 26, 26, 25, 19, 18, 14, 10, **1**
- Vibing++: 16, 36, 33, 40, 35, 25, 23, **7, 1, 0**

**They stop splitting at rounds 350-400** (the last 4→2+2 is around round 400; Sabotage-d tapers from 300).

## 2. Movement and sprints
**Sprint share of moves:** 0.09% (中国人能飞) to 0.46% (Vibing++). 龙虎豹 is 0.22%, Sabotage-d 0.14%.

**Almost all sprints are rams.**

| team | sprints ending in a head-on kill | enemy head Manhattan distance (median) | length before sprint |
|---|---|---|---|
| Sabotage-d | 274/326 | 2 | 3-4 |
| 中国人能飞 | 27/27 | 2 | 3-4 |
| Sponge | 97/97 | 2 | 3-4 |
| Peanut Butter | 69/69 | 2 | 3-4 |
| STAR | 42/69 | 2 | 3-4 |
| Vibing++ | 161/365 (136 of the 365 also ate) | 2 | 3-4 |

- Vibing++ also sprints to grab pearls.
- 龙虎豹: 200 of its 529 sprints are rams. The other 326 are **deliberate suicides**: "NS"/"EW" reversal sprints by length-2/3 dragons (NoValidAction/HitSelf), mostly in rounds 300-450 while feeding.
- **Nobody sprints to flee.** Sprints that neither eat nor kill are under about 5%.
- Across all enemy rams: 959 were 1-step (adjacent head) and 885 were 2-6 step sprints (662 of them 2-step).

## 3. Combat
Kills come almost entirely from head-to-head (H2H) rams. Body-block kills per team across all its games:

| team | body-block kills | H2H rams initiated |
|---|---|---|
| 龙虎豹 | 17 | 456 |
| Sabotage-d | 15 | 537 |
| Vibing++ | 10 | 296 |
| 中国人能飞 | 11 | 123 |

- The attacker (mover) is length 2-3 at the median, and so is the victim. Every trade is 1-for-1.
- Rammers do not wait for a size edge. 龙虎豹 as mover was smaller, larger or equal to its victim 129, 65 and 262 times; Sabotage-d 216, 164 and 157.
- **Big dragons die to small rammers.** Of 63 H2H deaths of dragons with L ≥ 12, **55 were rammed by an enemy of length ≤ 5**. Examples:
  - 龙虎豹 kings of 66 (round 485), 47 (round 463), 46 (round 473) and 37 (round 418) were killed by Sabotage-d/Sponge dragons of length 2-4.
  - Vibing++ 48 (round 410) and 38 (round 488) were killed by Sabotage-d length-3 dragons.
- **King head safety decides roundLimit games.**
- Of all deaths of L ≥ 12 (157 total): H2H 70, HitSelf 59 (mostly deliberate, see §4), HitWall 14, HitOtherBody 8.

**Death reasons across all games.**

| team | deaths | HitWall | HitSelf | H2H | other |
|---|---|---|---|---|---|
| Sabotage-d | 6968 | 2993 | 1232 | 1890 | HitOtherBody 853, 827 of them into its own allies |
| 龙虎豹 | 4363 | 1657 | 1477 | 1012 | |
| Vibing++ | 2361 | | | | NoValidAction 1755 (its suicide method) |

- **Most deaths are self-inflicted by length-2/3 dragons.**
- The pearls they drop are eaten by allies 98% of the time (Sabotage-d: 7656 own, 125 enemy), with a median lag of 2-4 rounds.
- These are not accidents: dead-end suicides, factory recycling (§7) and feeding (§4).

## 4. Late-game consolidation: feeding the king
**Timing (first round the team's longest dragon is ≥ 10 / ≥ 20).**
- Sabotage-d:
  - ≥ 10 around rounds 280-310 on most maps (Schooltime 108-200, Portals 178-296, Autarky 302-421).
  - ≥ 20 at rounds 301-470, median about 350.
- 龙虎豹: ≥ 20 at rounds 272-482.
- Vibing++: ≥ 20 at rounds 353-448 (Schooltime 122).

**Longest dragon, median, for 龙虎豹 / Sabotage-d / Vibing++:**

| round | 龙虎豹 | Sabotage-d | Vibing++ |
|---|---|---|---|
| 300 | 6.5 | 8.5 | 6 |
| 350 | 17.5 | 13.5 | 17 |
| 400 | 23.5 | 22.5 | 28 |
| 450 | 37 | 31 | 21 |
| 480 | 44 | 35 | 28 |

**The king grows until the very end.** The round of the king's last growth has a median of 494-498. Nobody stops early.

**Sources of growth.** After round 300, growth of dragons with L ≥ 10 comes from:
- own corpses: 67% (龙虎豹), 71% (Sabotage-d), 46% (Vibing++), 57% (中国人能飞)
- natural spawns: 24-48%
- enemy corpses: 3-5%

**Feeder profile** (death within 4 of the king, round ≥ 250):
- Length: 2 or 3. 龙虎豹 feeder lengths were 2 (183), 3 (152), 4 (32); Sabotage-d's were 2 (252), 3 (249), 4 (62).
  - Length 3 is the best value: 2 pearls from 3 segments.
- Kill method: **HitSelf** (move backwards into own neck).
  - Sabotage-d: 206/214.
  - 龙虎豹: 26/31, plus NoValidAction from a length-2 two-step move.
  - 中国人能飞 and Vibing++ use NoValidAction (an empty or invalid action).
- **Placement relative to the king's head:**
  - 龙虎豹: 25/31 feeders die at Manhattan 1, **directly in front** (12 of 31) or beside it (13). The king eats on its next step. Median lag is 1 round (p75 7).
  - Sabotage-d: dies at distance 2-4, **ahead of the king**. The top relative head positions (right, forward) are (0,3), (0,2), (1,2), (2,2) and (±3,0). The king's path runs over the pearls, with a median lag of 4 rounds.
  - Across all teams, dropped-pearl positions cluster at forward 1-3.
- About 50-100% of a feeder's drop is eaten by the king (median 100%).

**Feeding volume.**
- Sabotage-d: about 50 own-corpse pearls to the king per game, with feeders dying in rounds 326-467 (median 421).
- 龙虎豹: 403-476 (median 450).

**King choice.** It is the team's current longest dragon: whichever dragon is longest once the swarm stops splitting.
- The final king's ID is often "born" late (for example round 470-499) because **reverse splits re-ID the big body**. The king chosen is effectively "the longest", never "the lowest ID".
- Sabotage-d's sonar beacon (§5) broadcasts the length and position of big dragons (median beacon-origin length 12). That is how feeders find it.

**Insurance.** Winners end with 3-24 living dragons, never 1. Median final units: Sabotage-d 5, 龙虎豹 6.

## 5. Sonar
**Pings per turn.**

| team | pings per turn |
|---|---|
| Sabotage-d | 0 in 92% of turns, 4 in 8% (only from round 250 on) |
| 龙虎豹 | 4 in 25% (spike in rounds 350-450) |
| Vibing++ | 1-3 every turn |
| STAR | 1 (70%) or 4 (28%) |
| SHINK | none |

- Directions are evenly spread.
- Rays stop at: kelp 51-62%, ally body 25-32%, ally head 11-17%, enemy body 2%, enemy head 1%.

**Values.** 龙虎豹, Vibing++, STAR, Sponge and 中国人能飞 look encrypted or hashed: every bit is about 50% ones. STAR and 中国人能飞 send the same value in all directions per turn, and have few distinct values (STAR 6.5k distinct out of 87k pings).

**Sabotage-d beacon (decoded, 97.5% match).** The same value is sent in all 4 directions:

```
bits 58-63 = 0 | 42-57 = 16-bit hash/checksum | 36-41 = 0
bits 26-35 = originator dragon id (10 bits) | 24-25 flags | 21-23 = hop count (0-3) | 20 = flag
bits 12-17 = originator length | 6-11 = originator y | 0-5 = originator x
```

- Hop 0: sent by the dragon itself. The x,y match its head in 9878/10127 cases.
- Hops 1-3: relayed by allies that heard it (hop counts 3566, 2438, 2322).
- Originators have a median length of 12 (p10 5, p90 34). It is effectively a "big dragon here" flood, used to route feeders.

**For us:** use a keyed checksum as they do. Rays mostly hit kelp or allies, so a relay flood with a hop count is needed to reach across the map.

## 6. Per map (4 games each)

| map | elim / 4 | end round median | winner longest (roundLimit) | loser longest | winner peak units | winner units at end |
|---|---|---|---|---|---|---|
| Trophy | 4 | 180 (120-235) | n/a (swarm of L ≤ 4) | n/a | 40-48 | 40-48 |
| Devil | 3 | 122 (96-500) | 34 | 16 | 32-49 | 27-45 |
| Prisoners Dilemma | 3 | 252 (95-500) | 40 | 15 | 3-64 | 2-61 |
| Queen Of Spades | 2 | 454 | 14, 32 | 7, 12 | 19-29 | 1-27 |
| Default | 2 | 433 | 37, 40 | 12, 13 | 30-44 | 11-41 |
| Portals | 0 | 500 | 29, 39, 46, 48 | 21-47 | 37-46 | 3-5 |
| Trauma | 0 | 500 | 42, 43, 43, 50 | 23-46 | 33-54 | 6-20 |
| Autarky | 0 | 500 | 29, 35, 36, 74 | 19-67 | 37-64 | 3-13 |
| Schooltime | 0 | 500 | 38, 49, 60, 65 | 32-48 | 51-64 | 3-64 |
| Slithery Fight | 0 | 500 | 38, 48, 52, 70 | 18-45 | 64 | 9-24 |

- Elimination games are won by out-producing units: the winner's peak is 27-61 units against the loser's 7-19. Trades are 1:1, so unit count wins.
- On Trophy, both teams stay at L ≤ 4 all game.
- **Target for a roundLimit win: king of about 40-50 by round 500 (65-70 on Schooltime/Slithery).**

## 7. Hot tiles (pearl gap [1,1])
**Maps with hot tiles:** Autarky 8, Portals 8, Trauma 12, Prisoners Dilemma 12 (these are 100% of its spawns: all other tiles are 150-250 or 480-490), Devil 18, Slithery 31.

**Hot-tile share of spawn eats.**
- Trauma: winner 45-81%.
- Autarky: 30-73%.
- Portals: 23-47%.
- Prisoners Dilemma: 73-100%.
- Slithery: only 2-18%. There are so many other spawns there that it doesn't matter.

**The "factory" (hot corridor ping-pong).** Traced on Trauma, 龙虎豹 at the kelp-walled 1-wide corridor x=36, y=9..13 plus the dead end (35,9):
1. A length-2 dragon enters the corridor and eats hot pearls every step. At length 4 it does `SPLIT 2`.
2. The child is born at the tail end, facing the other way, and keeps eating back down the corridor.
3. The parent, stuck at the dead end, either leaves or suicides into kelp (HitWall), dropping its pearl on a hot tile that is re-eaten on the next pass.

- Output: exactly **3 hot eats per 4 rounds** (75 per 100 rounds, flat from round 100 to 499), plus a new length-2 unit roughly every 4 rounds. 238 different dragons did the eating.
- SHINK on Autarky/Prisoners Dilemma: exactly 50 per 100 rounds (1 per 2 rounds), with 249 different eaters.
- Sabotage-d on Trauma: the same loop, with the parent dying HitWall every 4 rounds (rounds 80, 84, 88, …).
- **Do this on Trauma, Autarky, Portals and Prisoners Dilemma.** Each factory is a steady unit/pearl source; winners out-harvest losers there by about 1.5-3x.

## 8. Actionable checklist
1. At length 4, `SPLIT 2` until about round 300-350 (earlier on elimination-prone maps: never stop). Allow growth past 4 only for the king.
2. Swarm heads: ram enemy heads at Manhattan 1 (step), or 2 (2-step sprint), when the target is within reach. Prefer targets with length ≥ own length, and **always ram enemy dragons of L ≥ 10** (55/63 big-dragon deaths came this way).
3. Dead end with 0 exits: reverse split `SPLIT L-2`, then the length-2 stub suicides next turn.
4. Hot-tile corridor factories: ping-pong split loop.
5. From about round 300: pick the longest dragon as king and broadcast its (id, len, x, y, hop) with a checksum; allies relay up to 3 hops. Feeders of length 2-3 path to 1-3 tiles ahead of the king's head and `HitSelf` (move opposite to facing). Continue to round 499.
6. Keep 3-10 other dragons alive, and keep the king's head away from enemy heads (their reach is Manhattan 1 + sprint 1-2, with length 3-4 rammers).
