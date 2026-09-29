# 23: Why we lose the big boards to top teams (29 Sep 2026)

**Question.** Against top-15 teams since v28 we win Trauma, Default and Prisoners Dilemma but lose Schooltime (60x40), Slithery Fight (63x27) and Autarky (54x18). What single, board-agnostic mechanism explains the three losses, and how do we fix it?

**Short answer.**
- **Board size is the wrong axis.** Trauma (48x24, 1152 tiles) is bigger than Autarky (972) and we win it 25/26. Portals (512 tiles) is weak too (21/42).
- **What orders the maps is mass retention:** the share of fresh income (spawn pearls + enemy corpses) that we keep as length, set against the top team's share.
  - On every map we win, our retention is at least theirs, or we out-harvest them about 2:1.
  - On all four weak maps our retention is far below theirs (Slithery 0.10 v 0.27, Schooltime 0.22 v 0.42, Autarky 0.01 v 0.33, Portals 0.15 v 0.21), and our harvest edge is only 1.3x or less.
- **The loss is the "burn", not income or territory.** In big-board losses we eat as many spawn pearls as they do. But we lose 1.6x as many dragons to our own moves (134 v 86 per 100 rounds), and each loss costs about 1.1 length net.
  - Over r0-300 this excess burn is about −150 length per game, against a final mass gap of about −75 at r300.
- **General mechanism M1: splitting is blind to density.** We split 2+2 at L4 wherever we stand.
  - As our swarm grows, more and more of those splits drop the child into a sealed spot, and the child dies within 3 rounds.
  - The share of splits whose child has a flood area of less than 4 tiles rises from 8% below 20 units to 37% at 50-60 units. The top teams stay flat at 12-19%.
  - Stillborn children cost 102 v 40 per game on the big boards (r0-349). That is about −65 length per game, and about −18 by r100, which is when the unit race is decided.
- **General mechanism M2: the pump cycle emits an L2 child.** We split at L4 in dead ends; the top teams eat to the tip and split k=L−2 (child L3+).
  - Pump-cycle child size: Slithery 2.08 v 3.10, Autarky 2.00 v 3.41, Trauma 2.01 v 2.47.
  - The existing `PUMP_TIP_SPLIT` copies their cycle exactly on the server (ab_tip29: child 3.39, parent dies at L2.01). But without an area check it raised stillborn children from 4.6 to 35.7 per game, so retention didn't move (0.26 → 0.25).
  - **So M2 only pays together with M1.**
- **Hypotheses (a)-(c):**
  - **(a) Territory/expansion:** only Autarky is really a territory loss (income share 0.31 at r100 in losses). On Slithery and Schooltime our Voronoi income share in losses is 0.51-0.57, yet we still lose.
  - **(b) King too late:** no. Our king reaches L16 *earlier* (r165 v r246), but ends smaller (33.5 v 54.4), because our mass is lower (134 v 165) and less of it ends in the king (0.27 v 0.33 at r450).
  - **(c) Transit deaths:** no. Deaths away from our spawn, portal deaths and L≥8 losses are equal or lower for us.

---

## 1. Data and tools

**Games.**
- The `replays/auto/games` and `replays/v28` ledgers, deduplicated: 704 games, 29 Sep 05:18-19:34 UTC, v28/v29 live.
- **Top-15 set:** 285 games against 13 teams that were ranked ≤15 when `auto_challenge` launched a series against them (`replays/auto/launched.jsonl`). The set is slightly wider than the journal's 245, because 'bread first search' counts.
- **Big-3** = Schooltime + Slithery + Autarky: 94 top games, W 22 / L 72. **Strong-3** = Trauma + Default + Dilemma: 77 top games, W 67 / L 10.

**Scripts** (all in `notes/tools/bigboard/`; read-only over replays; run from the project root):

| script | output |
|---|---|
| `collect.py [--jobs 6]` | `games.pkl`: per-round units/total/max, eats by phase × zone × source × near/far, head-Voronoi territory every 25 rounds, deaths (classified like porsli), splits. `BB_DIRS=dir1,dir2` reads other ledgers. |
| `report.py [list tl terr eats deaths splits gap end king]` | the tables in §2-§6 |
| `ledger.py` | mass ledger per 100 rounds (§3) |
| `retention.py` | per-map fresh income, burn, retention (§7.1) |
| `predict.py [maps]` | AUC of early features for W vs L (§4) |
| `deathctx.py` / `dreport.py` / `trapped.py` / `newborn.py` / `burn.py` | per-death context (age, unit count, dead-end, blockers, re-eaten pearls) and the burn decomposition (§7.2) |
| `sim3.py` | copy of `midgame/sim2.py` plus child/parent flood area (cap 30) at every split |
| `splitviab.py [--report]` | split-child viability vs early death (§7.3) |
| `abcheck.py replays/ab_x ...` | the M1/M2 mechanism metrics for any server A/B batch (reads `summary.json`) |
| `window.py` | per-window splits and deaths, W vs L |

**Definitions.**
- **Zones:** `rel = (dOpp − dOwn)/(dOpp + dOwn)`, with BFS distance (portals included) to each team's starting heads. home rel>0.2, far rel<−0.2, mid otherwise.
- **near25:** a tile within 25% of the maximum BFS distance from our own starts.
- **Territory:** multi-source BFS from all living heads over the portal graph (bodies ignored, ties split). *Income share* weights tiles by the spawns actually seen on them in that game. *cover* = fraction of the board within Chebyshev 3 of a head.
- **Self-inflicted death:** any death on our own move except a head-on with an enemy.
- **Burn:** own death length − own-corpse pearls re-eaten. **Fresh** = spawn eats + enemy-corpse eats. **Retention** = 1 − burn/fresh.
- **Sealed split:** the child head's flood area is < 4 tiles, with every current body treated as a wall. **Stillborn:** the split child dies within 3 rounds.

---

## 2. Timelines (mean per game, us/them)

| group | | r25 | r50 | r100 | r150 | r200 | r300 | r400 | r500 |
|---|---|---|---|---|---|---|---|---|---|
| **Big-3 L (72)** | units | 19.5/16.7 | 26.5/24.9 | 35.9/37.3 | 38.1/44.3 | 38.3/49.1 | 26.1/52.9 | 19.6/37.6 | 8.7/24.3 |
| | total | 44.9/42.6 | 63.8/61.7 | 87.7/96.4 | 97.2/123.3 | 101.3/142.6 | 91.9/166.3 | 96.2/166.5 | 98.8/163.3 |
| | longest | 3.3/5.6 | 3.7/5.4 | 3.7/5.7 | 4.3/6.6 | 4.7/7.7 | 10.9/11.0 | 17.5/25.5 | 24.7/42.6 |
| Big-3 W (22) | units | 19.6/15.0 | 29.5/22.7 | 43.4/32.5 | 47.2/38.8 | 50.0/40.8 | 39.3/42.6 | 33.3/23.7 | 14.9/10.6 |
| | total | 45.8/41.3 | 70.5/60.4 | 108.1/89.0 | 124.9/108.5 | 135.0/119.5 | 132.8/125.4 | 146.8/116.5 | 153.4/110.8 |
| | longest | 3.3/7.8 | 3.6/7.8 | 4.1/8.2 | 5.1/8.0 | 5.9/9.4 | 14.4/7.5 | 25.8/17.0 | 42.5/25.0 |
| Strong-3 W (67) | units | 6.3/5.1 | 10.9/6.0 | 20.0/8.9 | 26.8/11.0 | 31.7/11.5 | 35.3/10.2 | 34.9/6.3 | 30.6/3.6 |
| | total | 16.8/12.9 | 26.5/14.8 | 47.6/21.9 | 66.9/27.3 | 80.6/29.4 | 94.2/28.1 | 100.8/22.9 | 105.1/20.4 |
| | longest | 4.3/3.6 | 4.1/3.3 | 5.0/3.4 | 6.3/3.3 | 8.6/3.6 | 12.8/4.4 | 18.7/6.8 | 23.1/10.0 |

(Eliminated teams are carried at 0. "Them" longest before r100 on the Big-3 is the long starters of Slithery and Autarky; sim2 counts starters one segment too long.)

**What the timelines show.**
- On the Big-3 the game is even at r50 (63.8 v 61.7).
- In losses our total then **flatlines at about 90-100 from r100 to r500**, while theirs climbs to 166.
- In wins, our total keeps pace and we lead on units by +10 at r100.
- On the Strong-3 the opponent stalls instead: their total holds at 20-30.

**When the gap opens** (`report.py gap`; the first round where their total leads by at least max(8, 20%) and our total never catches up again):
- It happens in 49 of 72 Big-3 losses. Median **r66**, quartiles r51 / r66 / r193.
- **Autarky:** 18/23 before r75 (earliest r13).
- **Slithery:** 9/12 at r54-131.
- **Schooltime:** 5/14 at r46-80; the rest after r188.
- The unit gap follows at a median of r102.

**How the games end** (Big-3, top opponents):

| | n | eliminated (mean end) | round limit | longest at r500 us/them | total us/them | units us/them |
|---|---|---|---|---|---|---|
| W | 22 | 2 (r332) | 20 | 45.7/27.5 | 158/122 | 12.7/11.7 |
| **L** | 72 | **19 (r297)** | 53 | **33.5/54.4** | 134/165 | 11.8/14.0 |
| Strong-3 W | 67 | 40 (r197) | 27 | 47.6/24.7 | 145/51 | 31.4/8.9 |

Big-board losses are mostly (74%) round-limit king races, lost by about 21 on the longest dragon. A quarter are eliminations.

---

## 3. Where the length goes: mass ledger per 100 rounds (Big-3 losses, us || them)

Columns: spawn / own-corpse / enemy-corpse eats | deaths, length lost in deaths (self-inflicted, head-on) | Δtotal.

| window | us | them |
|---|---|---|
| r0-99 | 173 / 128 / 7 \| 103, 251 (216, 30) \| **+54** | 146 / 67 / 9 \| 63, 149 (113, 30) \| **+63** |
| r100-199 | 177 / 181 / 21 \| 134, 365 (281, 79) \| **+14** | 173 / 108 / 22 \| 86, 239 (144, 84) \| **+46** |
| r200-299 | 158 / 180 / 20 \| 136, 367 (289, 72) \| **−9** | 156 / 121 / 23 \| 87, 255 (164, 77) \| **+24** |
| r300-399 | 129 / 140 / 13 \| 112, 277 (227, 46) \| +4 | 124 / 125 / 16 \| 89, 253 (198, 44) \| +0 |

**Decomposition of the gap, r0-299, per game:**

| term | effect on us − them |
|---|---|
| spawn eats | +22 |
| enemy corpses | −6 |
| their sprint costs (the ledger residual; ours is ≈0) | +54 |
| **excess own burn** (death length − own corpse re-eaten) | **−146** |
| observed Δtotal | −74 |

**What the ledger shows.**
- Head-on losses are symmetric (79 v 84 length per 100 rounds).
- **The whole difference is self-inflicted deaths.** We lose 281 v 144 length per 100 rounds and re-eat only 181 v 108 of it.
- Big-3 wins look the same on the death side (330 v 156 self-inflicted), but there our spawn intake is +56 per 100 rounds higher (208 v 152). The burn is a constant tax, and on these boards it is larger than our harvest edge.

---

## 4. Hypothesis (a): the territory/expansion race

**Territory, all Big-3 top games** (r25 / 50 / 75 / 100 / 150 / 200 / 300 / 400):
- **Tile share (us):** .51 .45 .45 .45 .43 .43 .39 .45. Strong-3: .54 .58 .56 .59 .62 .64 .63 .64.
- **Income share (us):** .54 .49 .47 .47 .45 .46 .46 .54. Strong-3: .66 → .69.
- **Board within vision:** us .29 → .41 (r150); them .30 → .57 (r150) and .61 (r300).
- **Head positions:** our heads are in the far zone 4-7% of the time, theirs 11-15%. Home zone: us 50-53%, them 48-50%.

**Territory, W vs L** (tile share / income share, r50 / 100 / 150 / 200 / 300):
- Big-3 W: tile .47 .52 .51 .53 .48, income .54 .56 .55 .56 .57.
- Big-3 L: tile .44 .43 .41 .40 .36, income .48 .44 .42 .43 .43.

**Per map, losses, income share at r50 / 100 / 200:**
- **Autarky .38 / .31 / .21**: a real territory loss, the pocket-mouth story in notes/22.
- **Slithery .52 / .51 / .57**: we hold *more* of the income and still lose.
- **Schooltime .55 / .53 / .53**: same.

**Eats per 100 rounds, spawn only, near our starts / away from them** (Big-3 losses, us/them):

| | r0 | r100 | r200 | r300 | r400 |
|---|---|---|---|---|---|
| near25 | 131/111 | 122/95 | 108/79 | 87/60 | 63/35 |
| not near | 42/35 | **55/78** | **50/77** | 42/65 | 42/41 |

- They out-eat us 23-27 per 100 rounds away from our spawn in r100-299; we out-eat them by as much near home. Net spawn intake is equal.
- In Big-3 wins we also win the far side: 82/60 and 75/58.

**Best early predictors of a Big-3 win** (`predict.py`, AUC):

| feature | AUC | W | L |
|---|---|---|---|
| units diff r100 | .78 | +10.8 | −1.4 |
| cover diff r100 | .75 | | |
| net (eats − death length) diff r0-99 | .74 | +18 | −15 |
| tile share r100 | .72 | | |
| income share r100 | .72 | | |
| far spawn eats diff r0-199 | .67 | +54 | −15 |

Head spacing (nearest-own-head distance) has AUC .42-.47 and doesn't predict.

**Verdict.**
- Territory **tracks** the outcome, but it follows the unit count: vision tiles per head are about the same for us and them at equal units.
- The only map where territory is the root cause is Autarky (fresh income ratio 0.46).
- On Slithery and Schooltime the unit race is lost by burn (§3, §7), not by coverage. So (a) is a symptom, except on Autarky.

---

## 5. Hypothesis (b): king too late or too small

**Round-limit games, median first round the team's longest reaches L** (us/them):

| | n | L12 | L16 | L20 | L30 | king/total at r450 |
|---|---|---|---|---|---|---|
| Big-3 W | 20 | r176/325 | r288/349 | r325/367 | r410/486 | .25/.27 |
| **Big-3 L** | 53 | r154/144 | **r165/246** | **r264/329** | r416/384 | **.27/.33** |
| Strong-3 W | 27 | r159/362 | r195/393 | r221/414 | r333/— | .31/.44 |

- Our king forms **earlier**. It loses the r380-500 growth: their king goes L20 → L30 in about 55 rounds, ours in about 150.
- Final longest in losses: 33.5 v 54.4.
  - Our mass with their king share: 0.33 × 134 ≈ 44.
  - Their mass with our king share: 0.27 × 165 ≈ 45.
  - So about half the king gap is mass (§3) and half is conversion. The conversion half is covered by KING_FOCUS, FEED_EAGER and LATE_SPLIT in notes/16 and notes/21.

**Verdict:** not "too late". "Too small" is mostly the mass gap, plus notes/21 M1.

---

## 6. Hypothesis (c): dragons lost in transit

**Big-3 losses, per phase r0-99 / 100-199 / 200-349 / 350-500** (us/them):
- **Deaths away from our spawn (not near25):** 13.8/11.6, 32.6/36.9, 57.6/63.5, 35.8/37.1.
- **Portal deaths:** 1.7/1.3, 1.8/3.0, 2.2/4.9, 1.0/1.9.
- **Head-on with an enemy:** 11.4/11.4, 28.4/28.4, 33.5/33.2, 9.7/9.6 (1 for 1, as always).

**L≥8 losses before r450, per game:** us 3.28 (41.9 length), them 5.47 (62.9).

**Verdict:** rejected. We don't lose more dragons on the road, at portals, or among the big ones.

---

## 7. Hypothesis (d): the burn

### 7.1 Retention orders the maps; area does not (`retention.py`, top games, r0-299)

| map | win | area | fresh us/them (ratio) | burn us/them | **retention us/them** | deaths/g us/them | total@300 us/them |
|---|---|---|---|---|---|---|---|
| Trauma | .96 | 1152 | 375/215 (1.75) | 258/148 | .31/.31 | 234/124 | 125/68 |
| Default | .91 | 1024 | 215/99 (2.17) | 113/94 | .48/.05 | 84/53 | 118/18 |
| Dilemma | .76 | 512 | 58/33 (1.76) | 55/45 | .05/−.37 | 40/27 | 21/6 |
| Devil | .67 | 512 | 185/107 (1.73) | 137/82 | .26/.23 | 114/58 | 60/31 |
| Trophy | .63 | 625 | 167/114 (1.47) | 93/72 | .44/.37 | 52/43 | 80/44 |
| QoS | .58 | 875 | 115/101 (1.14) | 68/75 | .41/.25 | 47/51 | 53/29 |
| **Portals** | .50 | 512 | 491/401 (1.23) | 416/318 | **.15/.21** | 402/290 | 82/81 |
| **Schooltime** | .24 | 2400 | 544/420 (1.30) | 427/244 | **.22/.42** | 273/142 | 127/157 |
| **Autarky** | .24 | 972 | 137/300 (0.46) | 136/201 | **.01/.33** | 83/156 | 30/120 |
| **Slithery** | .23 | 1701 | 1093/850 (1.29) | 985/623 | **.10/.27** | 810/425 | 155/197 |

- Our retention is below theirs on exactly the four weakest maps, and at or above theirs on the six others.
- The high-income boards (fresh income above 450 per 300 rounds: Slithery, Schooltime, Portals) are where we burn the most: we run 1.4-1.9x their death count.
- Autarky is the exception, and its problem is income (§4, notes/22).

### 7.2 What the burn is made of (`burn.py`, self-inflicted deaths r0-349, per game, net cost in brackets)

| | stillborn child | pump parent (dies ≤5 rounds after its own split) | young (age 4-15) | old | feed |
|---|---|---|---|---|---|
| **Big-3 L** us | **102 (108)** | **158 (182)** | 37 (48) | 52 (70) | 11 |
| Big-3 L them | 35 (40) | 104 (117) | 20 (33) | 44 (68) | 4 |
| Slithery us/them | 264/100 | 406/196 | 79/47 | 103/84 | 26/6 |
| Schooltime us/them | 47/12 | 57/19 | 42/12 | 64/29 | 9/2 |
| Autarky us/them | 1/8 | 32/86 | 0/4 | 2/16 | 0/4 |
| Trauma us/them (we win) | 98/43 | 45/36 | 29/16 | 78/31 | 19/2 |

**What this shows.**
- The excess net cost on the Big-3 is about 156 per game: stillborn **+68**, pump parent **+65**, young +15, feed +6.
- In r0-100 alone it is about 38 (stillborn +18, pump +20). Our spawn edge offsets part of that (§3), and the rest is the total gap in the r50-100 unit race that decides W/L (units diff r100: W +10.8, L −1.4; AUC .78).

**Other death facts.**
- **Where they die:** 70% of these deaths (Slithery) are in corridor or dead-end tiles (degree ≤2).
- **What blocks them:** beyond the neck, the neighbours are kelp 41%, ally body 23% (them 17%) and free 9%.
- **Age:** our median age at death is 7 on Slithery (them 11) and 14 on Schooltime (them 38).
- **Unit count:** 70% of our Big-3 stillborns happen when we have ≥50 units.

### 7.3 M1: our sealed-split rate rises with our own density (`splitviab.py`)

**Big-3, splits before r350, per game.** "Sealed" means the child's flood area is < 4 tiles at birth.

| units before the split | our splits | our sealed share | our stillborn share | their splits | their sealed share | their stillborn share |
|---|---|---|---|---|---|---|
| 0-19 | 37 | 0.08 | 0.08 | 32 | 0.14 | 0.10 |
| 20-39 | 73 | 0.20 | 0.19 | 70 | 0.12 | 0.11 |
| 40-49 | 63 | **0.31** | 0.28 | 36 | 0.19 | 0.16 |
| 50-59 | 112 | **0.37** | 0.32 | 67 | 0.19 | 0.17 |
| 60-63 | 180 | 0.28 | 0.23 | 124 | 0.18 | 0.16 |

**Totals.**
- Big-3 sealed splits: 129 per game (28% of our splits) against 55 (17%).
- Children die within 3 rounds in 63% of sealed splits, 14% of cramped ones (area 4-11) and 7% of open ones.
- Stillborn children: 111 v 48 per game.
- Per map: Slithery sealed 338 v 135, Schooltime 51 v 10, Trauma 180 v 78 (we survive that tax on Trauma with a 1.75x harvest edge).

**Is the waste avoidable?**
- In 35% of our stillborn splits the parent side was open (area ≥4): the split just threw the child into the wall.
- In the rest both halves were in a closed region, but the parent then survived more than 5 rounds in 61% of cases. The region opened as bodies moved, so an unsplit L4 would most likely have lived too.
- A stillborn L2 costs about 1.06 length net (its one pearl is usually re-eaten).

**Why it's general.**
- The rule "split at L4 whenever not threatened" doesn't look at where the child's head (our tail) will be.
- On a big, high-income board our swarm reaches 40-64 units and packs the pockets and corridors. Blind splits then land in sealed spots about a third of the time.
- The top teams' rate doesn't rise with density.

### 7.4 M2: the pump cycle shape (dragons that die ≤5 rounds after their own split)

| map | split L us/them | child k us/them | parent dies at L us/them | parent dies at L2 us/them |
|---|---|---|---|---|
| Slithery | 4.15/5.16 | **2.08/3.10** | 2.65/2.34 | 46%/78% |
| Autarky | 4.00/5.41 | **2.00/3.41** | 2.75/2.09 | 25%/91% |
| Trauma | 4.01/4.47 | 2.01/2.47 | 2.05/2.04 | 95%/96% |
| Schooltime | 4.88/4.94 | 2.69/2.84 | 2.45/2.27 | 72%/80% |

- The notes/22 finding (eat to the tip, split k=L−2, the L2 parent dies) is not Autarky-specific: Slithery shows the same shape gap.

**Server evidence already on disk** (`abcheck.py replays/ab_v28base replays/ab_tip29`, 10 Autarky games each vs the same peers):

| batch | W | splits/g | sealed | stillborn/g | pump child k | parent dies L | retention |
|---|---|---|---|---|---|---|---|
| v28 | 6 | 153 | 0.04 | 4.6 | 2.00 | 2.63 | 0.26 |
| tip29 (PUMP_TIP_SPLIT + DEADEND) | 7 | 185 | **0.19** | **35.7** | **3.39** | **2.01** | 0.25 |

`PUMP_TIP_SPLIT` reproduces the top teams' cycle exactly (3.41 / 2.09). But its only exit test is `tailHasExit()`: one free neighbour of the tail. So it creates stillborn children, and they cancel the gain. **M2 needs M1's area test.**

---

## 8. Proposals (new flags, default 0; board-agnostic)

### 8.1 `SPLIT_VIABLE` (M1): don't split a child into a sealed spot; tighter when our swarm is dense

**Where:** `decide()`, normal split block (`bot/main.cpp` about line 2951, just before `out += "SPLIT " + std::to_string(k)` at about line 2979). Also replace the `tailHasExit(myLen - 2)` tests at about lines 2937 and 2976 (the PUMP_TIP_SPLIT gates) when the flag is on.

**params.hpp:**
```cpp
// notes/23 M1: required flood area (tiles) for each half after a split; 0 = off (try 4)
#ifndef SPLIT_VIABLE
#define SPLIT_VIABLE 0
#endif
// extra area required when units >= 3/4 of the unit limit (sealed share climbs with density; try 4)
#ifndef SPLIT_VIABLE_DENSE
#define SPLIT_VIABLE_DENSE 0
#endif
```

**New helper (next to `tailHasExit`).** It is a time-aware flood for one half after `SPLIT k`. Other dragons use `freeOther`; our own segments free up as each half moves.
```cpp
int splitSideArea(bool childSide, int k, int cap)
{
    int L = myLen, P = L - k;
    if (static_cast<int>(trail.size()) < L) return cap;           // tail unseen: don't block
    std::vector<int>& rel = scratchRel;                           // member, sized w.N, all 0
    for (int i = 0; i < P; i++) rel[trail[i]] = P - i;            // parent: its tail frees first
    for (int m = 0; m < k; m++) rel[trail[L - 1 - m]] = k - m;    // child: head = old tail
    int start = childSide ? trail[L - 1] : trail[0];
    int neck  = childSide ? trail[L - 2] : trail[1];
    std::vector<int> q{start}, dist{0}; std::vector<char>& seen = scratchSeen; seen[start] = 1;
    int area = 0;
    for (size_t qi = 0; qi < q.size() && area < cap; qi++)
        for (int d = 0; d < 4; d++) {
            int v = step(q[qi], d), du = dist[qi] + 1;
            if (v < 0 || seen[v] || (qi == 0 && v == neck)) continue;
            if (freeOther[v] > du || rel[v] > du) continue;       // occupied when we'd get there
            seen[v] = 1; q.push_back(v); dist.push_back(du); area++;
        }
    for (int t : q) seen[t] = 0;
    for (int i = 0; i < L; i++) rel[trail[i]] = 0;
    return area;
}
```

**Gate, in the split block after `k` is chosen:**
```cpp
#if SPLIT_VIABLE > 0
    int A = SPLIT_VIABLE + (units * 4 >= w.unitLimit * 3 ? SPLIT_VIABLE_DENSE : 0);
    int ca = splitSideArea(true, k, A), pa = splitSideArea(false, k, A);
    if (ca < A) goto noSplit;                        // child would be stillborn: keep moving/eating
    if (pa < A && myLen >= 5) k = myLen - 2;          // parent sealed at a tip: bulk leaves as the child
#endif
```
- `noSplit` falls through to the move scoring. The trapped reverse split (about line 3174) and ESCAPE_SPLIT are unchanged, so a truly trapped dragon still saves its bulk.
- **Cost:** at most 4 capped floods of ≤8 tiles per split decision, which is negligible.
- **Expected effect (Big-3):**
  - Sealed share at ≥50 units falls from 0.28-0.37 to the top teams' level (≤0.20).
  - Stillborn children fall from about 102 to 50 per game, for about +50-65 length by r350 (about +15-18 by r100, roughly +5-7 units at r100).
  - Retention: Slithery 0.10 → ~0.18, Schooltime 0.22 → ~0.30.
  - Trauma has the same tax (98 v 43 stillborn), so it should gain too.
  - Default and Dilemma have few sealed splits, so they should be neutral.

### 8.2 `PUMP_TIP_SPLIT` + `PUMP_TIP_DEADEND` on top of `SPLIT_VIABLE` (M2)

- **What changes:** no new mechanism. With `SPLIT_VIABLE` on:
  - the `holdTile` gate uses `splitSideArea(true, myLen - 2, A) >= A` instead of `tailHasExit(myLen - 2)`;
  - the tip `k = myLen - 2` needs the same test.
- **Evidence:** tip29 already produced the top teams' cycle on the server (child 3.39, parent dies at L2.01). Its failure was only the +31 stillborn children per game that M1 removes.
- **Expected effect:** notes/22 measured about +0.8 length per cycle (−0.2 → +0.58). Cycles per game run from 70 (Autarky) to 400 (Slithery), but a realistic net gain is +20-40 length per game once some cycles convert to non-splits.

### 8.3 How to measure (no local batches were run for this study)

1. **Offline decision check (no games):**
   - Re-run the flagged binary on 200 sampled real splits from Slithery, Schooltime and Trauma replays, with `notes/tools/porsli/botrun.py` (reconstructed views).
   - **Pass:** it refuses at least 80% of splits with child area <4 (and ≥60% of the stillborn ones), and at most 5% of open splits (area ≥12).
2. **Local self-play:** only a regression guard. Self-play has both sides burning, and it under-rewarded tip29 (0.449).
3. **Server A/B:** 10 peers × Slithery + Schooltime (+ Autarky for 8.2), about 20 games per arm, then `python3 notes/tools/bigboard/abcheck.py replays/ab_<base> replays/ab_<cand>`. Targets for the candidate:
   - sealed share (≥50 units) ≤0.20;
   - stillborn per game at least halved;
   - pump child k ≥3.0 with 8.2;
   - retention up by ≥0.08 on Slithery/Schooltime;
   - total length at r150 not below base;
   - wins not below base (the W/L predictor is the unit difference at r100).
4. **Win-side confirmation:** on the auto-challenge games after release, `retention.py` and `report.py tl` on the Big-3 vs top-15.
   - **Pass:** our retention ≥ theirs, and the r100 total gap ≥0.

---

## 9. Caveats

- **Big-3 W vs L:** the burn is just as high in our Big-3 *wins*. It is a tax that turns harvest parity into a mass deficit, not a switch.
  - W vs L is decided by the r50-100 unit race (AUC .78). The burn is its largest controllable input (−18 by r100 from stillborns alone), but opponent strength and map layout also matter.
  - Schooltime's two spawn layouts (notes/maps/schooltime-pass2.md) are pooled here.
- **"Sealed" is pessimistic:** it treats every body as a wall at split time. The in-bot test is time-aware, so it will refuse fewer splits than §7.3 counts.
- **Zones:** Slithery (start distance 4) and Schooltime (7) interleave both teams' starts, so most tiles are "mid". The near25/not-near split is the more useful home/away measure there.
- **Top set:** 13 teams, ranks taken at launch time. Samples: Schooltime 29, Slithery 31, Autarky 34 games; 7-8 wins each.
- **Counts:** the first `collect` run (before `launched.jsonl` grew) gave the same qualitative picture with 245 games.
