# Vibing++ (306) vs us, 4 Oct 23:00 to 5 Oct 22:00 UTC: profile, loss causes, harness-checked fixes

Written 5-6 Oct (EDT). This was a read and replay study only:
- Nothing in `bot/` or `variants/` changed. Nothing was submitted, no challenges were run, and no local games were played.
- All prototypes live in the scratch copy `scratchpad/vib5/bot/` (= `bot/` plus one new flag, `QSTALK`, default 0).

## 0. Data and tools
- **Our games vs VIB:** 145, attributed to builds with `ab_server.collect` (300 s grace). Saved in scratch `vib5/ours_vs_vib.json`.
  - W-L by build: f1 5-5, k2 11-14, cm1 3-7, b3 4-6, h1 12-18, s1 10-15, l1 7-8, ms1 10-10.
- **The b3-equivalent set:** f1, cm1 and b3, plus k2 everywhere except Portals and Maze. k2 = b2 + QK_EG, and QK_EG only acts on the crowned queen on those two maps.
  - 51 games: **22 W / 29 L**. Lists are in scratch `vib5/all_eq.txt`, `wins.txt` and `losses.txt`.
- **Replays:** `replays/vib_oct5/`, 78 games. That is 55 of ours (every f1/cm1/b3/k2 game) plus 23 VIB vs FTM/SSS/DEV (8 per opponent, spread over the day; one download failed). The list is in `sample.json`.
  - VIB listing: `games_306.json`, 1527 games.
  - VIB win rate by opponent: FTM 52%, SSS 57%, us 56%, Settlers 74%, DEV 28%.
- **Scripts** (`notes/top5/new_rules_tools/`):
  - `fetch_vib5.py`: listing crawl.
  - `an_vib5.py`: per-game rows; output in scratch `vib5/rows_vib5.pkl`. Wraps `an_vib4.analyse`.
  - `agg_vib5.py`: the profile table in section 1.
  - `trace_vib5.py`: round-by-round trace of one game.
  - `qctx_vib5.py`: the 8 rounds before our queen dies, with the nearest enemy heads.
- **Scratch scripts** (`vib5/`):
  - `vp.py`: batch harness verify. It runs f1 games with `CROWD_MAPS=0`, k2 with `CROWD_MAPS=0 QK_EG=2`, and cm1 with `CROWD_MAPS=3`; `VPQ=1` checks the queen only.
  - `schfirst.py`: Schooltime direction test.
  - Harness JSON results are in `v/<label>/`.
- **Harness fidelity:** the flags-off scratch bot matched every queen turn in the 22 wins and in the losses (the only exception is 1125003, a Queen Of Spades game on the unfitted 2nd layout, rebuilt DIFF). It also matched all-dragon turns 100% in 4 of 5 Schooltime games; the fifth has 16 of 9612 CPU-budget turns that differ.

**VIB switched submission at about 22:06 UTC 5 Oct.** Their rating went 2458 → 1536 by 23:31, with 0-5 / 0-17 results against 1500-2100 teams. This is their usual test-build flip. Everything below is from games before 22:00 UTC (their strong build). The leaderboard now shows them at #152, so expect them back.

## 1. What VIB does now (VIB-side medians; "oct4" = rows from TOP1_VIBING_OCT4.md, which were against our older builds)
| metric | oct5 vs us (55) | oct5 vs FTM/SSS/DEV (23) | oct4 vs us (102) |
|---|---|---|---|
| VIB win % | 58 | 39 | 60 |
| queen never splits / first split | 9% / r8 | 30% / r8 | 24% / r10 |
| queen alive at end / median death | 38% / r89 | 26% / r94 | 38% / r112 |
| queen self (NoValid) deaths | 14 | 5 | 19 |
| queen length alive r100/200/300 | 3/5/6 | 3/5.5/11 | 3/6/10 |
| queen is king at end | 20% | 26% | 20% |
| units r50/100/200/300 | 12/22/43/57 | 10.5/22/41.5/51.5 | 10/20/34.5/46 |
| total r50/100/200/300 | 27/54/**105/170** | 25/53/110/149 | 25.5/54/89.5/110 |
| our total r100/200/300 | 65/101/112 | (opp) 54/111.5/96 | 64/89.5/89.5 |
| longest r100/200/300/400 | 4/6/14/32 | 4/9/9.5/14 | 4/8/12.5/28.5 |
| first L10 / L20 | r156 / r326 | r171 / r407 | r160 / r322 |
| kills per game | 30 | 21 | 21.5 |
| kill steps 1/2/3/4+ (mean per game) | 11.8/16.0/**8.0**/0.1 | 15.7/12.7/5.7/0.1 | 10.6/14.1/6.0/0.3 |
| paid kills / kills where a pearl paid | 23.6 / 10.1 | 18.4 / 6.3 | 20.0 / 7.7 |
| enemy queen killed by VIB | 47% | 57% | 57% |
| feeding by NoValidAction per game | 213 | 222 | 170 |
| splits per game / stillborn by r100 | 280 / 2 | 282 / 1 | 231 / 1 |

**What changed vs the Oct 4 notes:**
- Same family and the same style: NoValidAction feeding, 0 HitSelf, bulk splits, pearl-refunded lunges.
- The queen splits a bit earlier and almost always (only 9% never split vs 24%).
- More units and mass from r200 on: 43 units / 105 total at r200 vs 34.5 / 89.5. At r300 they have 170 vs our 112.
- More 3-step kills: 8 per game vs 6.
- These numbers compare different builds of ours on each side, so they are only indicative.

**There is no targeted queen hunt in aggregate.** VIB heads within 4 tiles of our queen average 0.1 per sampled round, against 0.2 near our other heads. Our queen dies to small VIB heads because she walks among their many units (section 2.4), not because they hunt her.

**Per map, VIB wins vs us (b3-eq):**
- Maps they win: Schooltime 5/5, Maze 4/4, Stripes 3/3, QoS 3/3, Slithery 5/7, AUNSW 3/4, Devil 3/5.
- Maps we win: Trauma 0/5, PD 0/3, Trophy 0/3, weakhold 0/2 (VIB wins 0 of these).

## 2. Our losses (29) and their causes
Queen fate in losses:
- Their queen alive at the end in 13 of 29; killed by us in 9; died on her own in 7.
- Ours: killed in 13, self-inflicted in 11, alive in 5 (the Schooltime games).

| bucket | losses | decided by | decision-level status |
|---|---|---|---|
| Schooltime layout B | 4 (1102499, 1133224, 1138232, 1151986) + 1 layout A (1124560) | Both queens are locked L3 in their 2x2 spawn box (area=4, she loops all game), so the longest dragon decides. On B our units eat **0 pearls at y>=24**; VIB gets 25-45% of its r0-200 eats there. At r300 our total is 3-19 vs 236-299 in 3 games. | 2.1 |
| Queen dies to small VIB heads | 9: Devil 1106626, 1133223, 1164512; Default 1129479; Australia 1129482; Islands 1129480, 1164513; QoS 1125003; AUNSW 1102496 | VIB L2-3 heads (an L10 in AUNSW) within 2-4 tiles for 3-10 rounds, then a head-on ram | 2.4 |
| Slithery | 5: early vault deaths 1137688 (r28), 1164514 (r66); late coils 1124563 (r258), 1129048 (r388); 1138231 (h2h r339) | | 2.2 |
| Stripes | 3 eliminations (1137684, 1138230, 1151989) | Our queen's r13 vault death is by design (76 of 79 Stripes games since 02:50 UTC, wins included). VIB runs the same vault pump (NoValidAction) but keeps 2-3x our units (r40: 9 vs 5; r100: 18 vs 5). A mass race with no single decision. | not fixable by one gate |
| Other | QoS 1102498 / 1137687 (queen self-death r35-37), AUNSW 1124559 / 1125002, Autarky 1106629, Maze 1137685 / 1164516 | | not examined |

### 2.1 Schooltime B
- **The bed mismatch is not the cause.** Both `maps_data.hpp` entries (MAP13, MAP14) carry layout A's 326 beds; layout B has 178, and only 60 are shared. But `maps/schooltime.hpp` already patches in B's 178-bed table once `schDetect()` sees B (`SCH_LAYOUT=1`, `SCH_LAYOUT_PATCH=1`).
  - Checked at r90 in two B games: 7 of 7 live units still have `map=Schooltime`, with and without SCH_DOORS.
- **The cause is myopia**, as in UNDERSTANDING.md: the lower field and chambers are never visited.
- **Harness:** first changed decision per dragon in the 4 B losses. Does the new move end closer (plain BFS on the replay's walls) to B beds at y>=24 than the server move did?
  - `SCH_DOORS=1 SCH_CHAMBER=1`: closer 116, farther 44, same 65.
  - `SCH_DOORS=1` alone: closer 64, farther 35, same 31.
  - Layout A loss 1124560: 21965/21965 turns unchanged under both.
  - The all-turn count (polluted by drift) had no signal, so trust only the first-change numbers.

### 2.2 Slithery (QVAULT)
- `QVAULT=1`, queen moves only, Slithery + Australia games:
  - **2 of 2 early vault-death losses flip at the vault-entry move:** 1137688 r22 (server E into the vault, new WS) and 1164514 r30 (server W, new EE).
  - **Both Slithery wins also change**, at their own vault entry: 1124999 r20 (that queen died at r26 anyway) and 1151988 r19 (that queen survived; 29 of 500 turns change).
  - The late losses 1124563 / 1129048 and 1138231 are unchanged.
- `QVAULT=3` (adds the Australia bit): the same on Slithery. It also changes the Australia win 1151985 at r34-36 (that queen died at r44 HitSelf in the vault, and we won on mass). The Australia loss 1129482 is unchanged (that death is an ally seal, section 2.4).
- **The late Slithery deaths are not vault deaths.** 1129048 r381: our own L32 king (id 1224) coils around the L14 queen and leaves her 1 candidate. At r382 she is boxed, then sheds 2 per turn to L2 and dies at r388 (the same pattern in 1124563 r255-258).
  - `QAK_HARD=1` does not change the king's moves: every king candidate already carries the ~-450 QALLY_KEEP penalty, so it picks the least bad.
  - No small fix found.

### 2.3 QKK_FREE on VIB games
- `QKILL_KING=1 QKK_FREE=1`, all dragons, 15 losses / 14 wins on the non-lane maps.
- **0 of 15 losses change.** Their queen is either big (L34-95 crowned) or out of reach.
- 2 of 14 wins change: 1129049 Islands r390 (a king takes a queen-kill path) and 1124999 (1 turn).
- So QKK_FREE does nothing against VIB; its ranking stays as UNDERSTANDING.md has it.

### 2.4 Queen killed by small VIB heads (9 losses)
Context (`qctx_vib5.py`) and the harness (sandbox, every base move MATCHes the server):

| game | death | the decision | type |
|---|---|---|---|
| 1133223 Devil | r18 | r16 free-path sprint NW into (15,0), the closed top of the 2-wide x=15-16 corridor; r17 0 candidates; the L3 that walked up x=15 rams her at r18 | dead end with a stalker 4 away |
| 1106626 Devil | r22 | r19 free-path sprint SE into the centre 1-1 farm (L5 → L7 → L8); r21 0 candidates, split; rammed r22 | farm pocket, L2-3 heads at 1-3 |
| 1164512 Devil | r35 | r30-34 centre farm, heads at 2-3; r35 0 candidates, an ally head adjacent | farm pocket |
| 1129479 Default | r74 | r74 her own move ends inside an L3's 2-step reach | open-ground lunge |
| 1129482 Australia | r62 | r61 N to (34,21); at r62 **our ally A4's head (34,20) blocks N**, leaving only E, next to an enemy L2 | ally seal + stalker |
| 1129480 Islands | r148 | r140-148 1-2 candidates every turn in the 1-wide tip loops, L3 at 2-4 for 8 rounds | forced loop |
| 1164513 Islands | r134 | r133 free path; r134 0 candidates | forced, in the tips |
| 1102496 AUNSW | r121 | 2 open candidates, killed by an L10 lunge from 3 tiles, after r100 | big-head lunge |
| 1125003 QoS | r100 | three L2s at distance 1-3 for 8 rounds | 2nd layout: the rebuild diverges from r16, so not checkable |

**Prototype QSTALK** (scratch `vib5/bot/main.cpp`, in evalDir; params at the end of `params.hpp`; default 0). It applies only to the queen, never on queen-park maps, and only at L <= 10.
- **Bit 4:** before `queenSafe()`, the queen pays `QSE_THREAT_PEN` (300) for `threat>0`, and `QSE_PAID_PEN` (120) when any visible enemy head's kamikaze reach K(Lv) = ceil(Lv/4) + (Lv-2), capped at `QSE_KCAP=3`, covers the tile (wrapDist). This is RLB's QE_THREAT_PEN with an explicit K-reach, because `threatPaidAt` is empty while THREAT_FREE and KREACH are 0. The 300 penalty for threat>0 is the same as RLB's.
- **Bit 1:** the tile has <= 1 free exit and an enemy L<=6 head is within K+1.
- **Bit 2:** a corridor walk from the tile (one way on, bodies that haven't vacated block, a dead end counts as 99) is >= 2 tiles long, and the head is within K+1+min(cd,4).

Harness, queen moves only (counterfactual on a fixed history):

| variant | losses changed | at the decisive move | wins changed (of 22) |
|---|---|---|---|
| QSTALK=4 | 1106626 r19 (the trap sprint SE → EN), 1129479 r74 (the fatal step E → EN), 1164512 r23/r26 (12 rounds before death); also Autarky 1106629 r43 (queen died r477), Slithery 1138231 r20, 1164514 r19 | **3 of 8 checkable** (1106626, 1129479, 1164512) | 3, one turn each: 1125000 r24, 1129483 r39, 1151988 r18 |
| QSTALK=7 (bits 1+2+4) | adds **1133223 r16** (NW into the dead end → W); keeps 1106626 r20 and 1164512 r17/r26; loses 1129479 | 3 of 8 | 5, 1-2 turns each (1124561, 1125000, 1129483, 1151988, 1151985) |
| QSTALK=7 side effect | also changes the Stripes queen at r5/r9 in 3 of 3 Stripes losses: it steers her off the designed vault dive | | |

**Not reachable by any variant:**
- Islands ×2: forced 1-wide loops.
- Australia: our own ally's head seals her.
- AUNSW: an L10 lunge after r100. queenSafe's paid-threat penalty already applies there; she had 2 candidates, and both were in reach.
- QoS: not checkable.

Read the counts as "the trap move changes", not "she survives". The history is fixed, so survival after the change can't be scored.

## 3. Our wins (22): what went right
- **Their queen died in 17 of 22.** 11 we killed: Devil/Trophy early rams, AUNSW 1164515 r291 (an L20 queen killed by our L4), Slithery 1151988 r291. 6 she died on her own (NoValidAction: Trophy r24, PD r21/r61, Portals r118, weakhold r139, Islands r447).
- **The other 5 wins are all Trauma,** both queens alive: our pen queen gets to 37-57 vs their 21-33.
- **Eliminations (7):** Trophy ×3, PD ×3, Devil. Our early units won the opening fights and swept.
- **Mass wins:** Australia 1151985 (r300 369 vs 3), Default 1102497 (144 vs 8), Islands 1129049 (149 vs 125, longest 51 vs 29), Slithery 1124999 (longest 95 vs 36). Our L4+ economy beat theirs on those maps when our early losses were small.
- **Our queen lived in only 9 of 22 wins.** We win when theirs dies too, so killing their queen remains the main win path; QKK_FREE does not add kills against VIB (2.3).

## 4. Ranked fixes (harness-checked on VIB games)
1. **SCH_DOORS + SCH_CHAMBER**: Schooltime layout B only. Already in `bot/` as flags; the stage is `dgu/stage/SCH_CHAMBER`.
   - Causes covered: 4 of 29 losses (0/4 vs VIB on B; DGU: 0-15 vs strong teams on B).
   - Flips: first changes per dragon are 116 closer / 44 farther / 65 same toward B's lower-field and chamber beds. Doors alone: 64 / 35 / 31.
   - Unchanged: the layout A game, 21965/21965. There are no Schooltime wins vs VIB to check.
   - Scope: about half of Schooltime games. Risk: movement-heavy on B (DGU smoke: one seed lost on sch_1164105). Ship SCH_DOORS first, as DGU advised.
2. **QVAULT=1**: Slithery only (the Australia bit 2 adds nothing against VIB). Already in `bot/`; the stage is `dgu/stage/QVAULT1`.
   - Flips: 2 of 2 early vault-death losses, at the entry move.
   - Wins: 2 of 2 Slithery wins change at their own vault entry. In one of those the queen died in the vault anyway; in the other she survived.
   - Late coil losses: 0 of 2 change.
   - Risk: loses the 1-4 vault pearls per entry.
3. **QSTALK=4**: early queen (before queenSafe) avoids enemy K-reach tiles, all maps. New, scratch only.
   - Flips: 3 of 8 checkable small-head queen deaths change at or before the trap move (Devil ×2, Default).
   - Wins: 19 of 22 have identical queen moves; 3 change 1 turn.
   - Risk: **high on history.** It is in the v69 / l1 / QKREACH lineage, all server losses. Only test it as a Devil/Default-gated unranked loop; judge it on queen alive at r50 and centre-farm eats. Do not use bits 1/2, which steer the Stripes queen off her designed dive.
4. **QKK_FREE**: no VIB effect (0 of 15 losses, 2 of 14 wins). Keep its place in the UNDERSTANDING.md queue for the non-VIB field.

**Not fixable by a small change (evidence only):**
- Stripes vs VIB: a mass race in which they out-split us with the same pump.
- Slithery and Portals late queen boxed by our own L30+ king: QALLY_KEEP saturates and QAK_HARD doesn't change it. A real fix needs the king to stay away from the queen in the endgame on the planning side.
- Australia 1129482: an ally head seals the queen while an enemy L2 waits.

## 5. Files
- Scratch `vib5/bot/` = `bot/` + QSTALK (main.cpp evalDir: an exit/corridor block before QBOX, and the bit-4 block before the QSTATE hunt; params at the end of params.hpp).
- Harness JSON: `vib5/v/{off,schd,schdc,qs4l,qs4w,qs7l,qs7w,qv1,qv3,qkfl,qkfw}/`.
- Traces: `vib5/qd/`, `vib5/qs/`, `vib5/qs2/`.
