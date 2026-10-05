# Own ranked games, b1 + q1 (4-5 Oct): loss study

Written 5 Oct ~02:00 UTC (4 Oct 22:00 EDT). Read-only: nothing in bot/ or variants/ changed, nothing submitted, no challenges.

## Data
- Game list: `python3 tools/ab_server.py b1 q1 --ends --json replays/own_ranked/ab_rows.json` (run from the project root).
  - b1 #17160: 22:52-23:34 UTC 4 Oct. 69 ranked games (59 ranked challenges + 10 autoscrims), 31-38. All 69 were against the top 10 (mean opponent 2228).
  - q1 #17191: 23:39 UTC 4 Oct - 01:29 UTC 5 Oct. 45 ranked games (15 challenges + 30 autoscrims), 34-11. 40 of the 45 were against the rest (mean ~2000).
  - The 183 unranked q1 panel games are left out; another check covers them.
- All 114 ranked replays (49 losses, 65 wins) are in `replays/own_ranked/`. `summary.json` lists the games.
- Scripts are in the scratchpad `own/`: fetch.py, build.py (replay_sim -> pk/), classify.py (-> rows.json), late.py, board.py, opts.py. They are adapted from `notes/newrules/loss_audit2_tools/`.
- Caveat: the sample is small. Only 8 ranked q1 games are on its five new park maps (AUNSW 2, TD 3, Slithery 1, weakhold 2, Australia 0). The tier mix also differs completely between the builds (b1 played only the top 10, q1 mostly the rest), so this page compares mechanisms, not win rates.

## Headline
1. **Parking works. The crowned queen is now the weak point.** Portals went 9-1 ranked: the queen was alive at r500 in 9 of 10 games, at L34-59.
   - Every queen that was crowned on Maze (3/3) and Around UNSW (2/2) died after r300 at L21-44, killed head-on by an L3-L6 enemy. On Tower Defense 1 of 3 died the same way.
   - Because all our mass sits in her, one ram loses the queen tiebreak and the longest-dragon tiebreak together. Example: Maze 1087063, our longest went from 41 to 8 against their 86.
2. **New mechanical failure: the coiled crowned queen.** A long crowned queen (L38-58) walks into a dead-end lane or notch formed by kelp and her own body. QBOX_K2 then sheds 2 per turn for 12-21 turns.
   - This happened in 5 of ~20 crowned games: Portals 1086127, 1094635 and 1087098 (minor); Tower Defense 1094618 and 1091874.
   - It decided Portals 1086127 (their queen had been dead since r27) and set up the TD 1094618 death.
3. **The other losses are the old shapes.**
   - Lane-map eliminations against the top 10: Trophy 7, QoS 5, Stripes 4, TD 3, Devil 2, Autarky 2, Default 1.
   - Unparked Slithery queens dying while our king out-measured their queen (4).
   - Lone-queen survivors we never finish (Devil 146 v 3, TD 62 v 15).
   - The Schooltime box (3).
   - Nothing new appears on maps b1/q1 did not touch.

## Cause x tier (49 ranked losses)
| cause | top 10 | rest | maps |
|---|---|---|---|
| eliminated | 22 | 3 | Trophy 7, QoS 5, Stripes 4, TD 3, Devil 2, Autarky 2, Maze 1 (after the crowned queen died), Default 1 |
| r500, our queen dead, theirs alive | 10 | 2 | Slithery 4 (b1, unparked), AUNSW 2 (1 crowned), TD 2 (1 crowned), Default 1, Devil 1, Islands 1, Maze 1 |
| r500, both dead, longest lost | 6 | 1 | Islands 2 (34 v 35, 67 v 85), Australia 1 (51 v 52), Default 1, Maze 1 (crowned queen died r369), Portals 1 (crowned queen shed chain), weakhold 1 |
| r500, both alive, queen shorter | 3 | 2 | Schooltime 3 (q3 v q3, longest lost), weakhold 1 (Q4 v 21 with 85 v 27 total), Autarky 1 (Q14 v 26 with our king L30) |

Compared with v61 in LOSS_AUDIT2 (top-10 losses: 30% eliminated, 39% queen dead):
- Eliminations are now 22 of 41 top-10 losses (54%).
- b1's games were ranked challenges against aAah (0-5), Vibing++, SSS, forgot to mention and "dev test 1" on random maps. Trophy, QoS and Stripes play identically to v61 in b1, so the rise is opponent and map mix, not the build.
- Every elimination opened its economy gap at r26-75 (Trophy/Stripes/Devil/QoS) or r115-190 (QoS/Autarky/Default/Maze).

Ranked W-L by map: Portals 9-1, Prisoners Dilemma 7-0, Trauma 5-0, Islands 8-3, Default 7-3, Stripes 7-4, Autarky 3-3, AUNSW 2-2, weakhold 2-2, Australia 2-1, Schooltime 2-3, TD 3-5, Devil 1-3, Maze 1-3, Slithery 1-4, QoS 2-5, Trophy 3-7.

## (a) Guard stat: do parked/crowned queens die late with all the mass in them?
r500 losses with our queen dying after r300: **6 of 24** r500 losses.
- 4 on park maps: Maze 1087063 (L41, r369), AUNSW 1090198 (L44, r385), TD 1094618 (L32, r473), Portals 1086127 (shed to L2, r409).
- 2 on Slithery under b1, where the queen was not parked: L7 at r352, L14 at r431.
- One more crowned death ended in an elimination: Maze 1087084 (L42 at r363, then eliminated at r488).

Per park map (ranked only; "crowned" = queen reached L15 or more):
| map / build | games | W | crowned | queen alive r500 | crowned queen died after r300 | K2 shed chain on the crowned queen |
|---|---|---|---|---|---|---|
| Portals b1 | 6 | 5 | 6 | 5 | 0 (one shed to death at r409) | 2 (1086127 38->2 dead; 1087098 45->39) |
| Portals q1 | 4 | 4 | 4 | 4 | 0 | 1 (1094635 58->34 at r488-499) |
| Maze b1 | 3 | 0 | 2 | 0 | 2 (L42 r363, L41 r369) | 0 |
| Maze q1 | 1 | 1 | 1 | 0 | 1 (L21 r316; won on longest) | 0 |
| AUNSW q1 | 2 | 1 | 2 | 0 | 2 (L28 r327 won; L44 r385 lost) | 0 |
| TD q1 | 3 | 2 | 3 | 2 | 1 (L32 r473) | 2 (46->10, 50->8) |
| Slithery q1 | 1 | 1 | 1 | 1 (L85) | 0 | 0 |
| weakhold q1 | 2 | 2 | 0 (L7-12) | 1 (other game ended by elimination, queen alive) | 0 | 0 |

**Answer: yes on Maze and Around UNSW; on Portals and TD the leak is self-inflicted.**
- Maze and Around UNSW: every crowned queen was rammed between r316 and r385.
- Portals and TD: the coiled-queen shed chain.

How the crowned queens die, all head-on by small units:
| game | queen | killer | lunge | visible to her at her move? | distance after her move | old queen threat reach (F / F+1) | kamikaze K(L) |
|---|---|---|---|---|---|---|---|
| 1090198 AUNSW | L44 | L4 | 3 steps, 1 pearl | yes (Cheb 3) | 3 | 1 / 2 | 3 |
| 1087084 Maze | L42 | L4 | 4 steps, 2 pearls | no (Cheb 4) | 4 | 1 / 2 | 3 |
| 1087063 Maze | L41 | L6 | 4 steps | yes (Cheb 3) | 4 | 2 / 3 | 6 |
| 1094618 TD | L32 | L3 | 1 step | yes (she was boxed after the shed chain) | 1 | 1 / 2 | 2 |
| 1087909 AUNSW (win) | L28 | L4 | 3 steps, 1 pearl | no (Cheb 4) | 3 | 1 / 2 | 3 |
| 1087815 Maze (win) | L21 | L3 | 3 steps, 1 pearl | yes | 3 | 1 / 2 | 2 |
| 1086400 Slithery (b1, not crowned) | L14 | L4 | 6 steps, 3 pearls | yes | 4 | 1 / 2 | 3 |

- Under QUEEN_SAFE the queen treats an enemy's free reach F(L) as the threat, plus one paid step at QUEEN_PAID_PEN 120 (main.cpp:3643-3656).
- A head-on kills both dragons whatever their lengths, so an L4 happily pays its tail to kill an L44. Its real reach is K(L) = F + L - 2, plus one step per pearl it eats on the way.
- In 3 of 6 the killer was visible and the queen stepped to within K(L) (or K+1) of it.
- In 2 the killer was waiting at Chebyshev 4, outside her 7x7 view; only ally relays or sonar would show it.
- In the 2 Maze losses our queen was feeding while the killer closed from Chebyshev 7 to 3-4 over 5-10 rounds.

## (b) New failure modes in b1/q1 compared with v61 (LOSS_AUDIT2)
1. **New: crowned-queen ram.** v61 lost Maze by queen death at L2-6 (13 of 16). Now the queen survives to be crowned (L41-44) and is then rammed by the same L3-6 enemies.
   - The loss is now total: our non-queen units stop growing kings while she lives, so the longest-dragon tiebreak is lost as well (Maze 1087063: 8 v 86).
   - Maze economy is unchanged and still behind: r200 total 99-108 against 176-201.
2. **New: crowned-queen coil, then a K2 shed chain.** The repeated `SPLIT 2` comes from the QBOX branch (main.cpp:6528-6540) with `bestD < 0`, fired 12-21 turns in a row at L38-58.
   - v61 never had a queen this long, so the branch was tuned for L4-8 queens in Schooltime boxes.
   - The trap is set 4-10 turns earlier. In every case she spent the last 3-6 turns with a single legal move inside a lane closed by her own body, kelp or a banned portal (opts.py).
3. **Gone or reduced:** the early Portals portal-vault shed chain (v61: 19 queen-dead losses on Portals; now 0 before r390). The Maze field-doorway death before r300 dropped to 1 in 4 games (1086125, r228, before the crown).
4. **Unchanged:** the Stripes r13 queen dive dies in all 11 Stripes games, wins included (it is the farm seed); lane-map eliminations; Schooltime q3 v q3; Islands and Australia longest races lost by 1 (34 v 35, 51 v 52).
5. **q1-specific, ranked only (n=8 on its maps):**
   - Slithery: 1-0, the queen reached L85.
   - weakhold: 2-0 (queen alive L12, and a win by elimination).
   - TD: 2-1. AUNSW: 1-1.
   - For contrast, in b1 all 4 Slithery losses were "our queen dead, our longest beat their queen" (95 v 33, 86 v 51, 91 v 60, 73 v 54). That is exactly the shape the Slithery park targets.
   - The unranked q1 panel (another check) was much worse on these maps (ab_server: Slithery 4-16, TD 8-18, Australia 8-13, AUNSW 10-13). Decide q1 on that check; this page only says the ranked replays show no new q1-specific bug apart from (1) and (2).

## (c) The 3 most common fixable causes now (ranked)

### 1. Crowned queen rammed late by a small kamikaze (Maze, AUNSW, TD; 4 losses + 1 elimination, 2 wins at risk)
- **Code path:**
  - The queen's threat reach is set in `computeThreats()` under `queenSafe()`: `reach = F; paidReach = F+1` (main.cpp:3643-3656). An L4 enemy gives reach 1 and paid reach 2, but K(4) = 3.
  - `KREACH` (main.cpp:3658-3668) would add K(L) but is 0.
  - `ENDGAME_GUARD` (egOn main.cpp:2971; eval main.cpp:6188-6201; veto main.cpp:6451-6462) has the right rule (stay out of K(L) of every visible enemy head, veto when an unthreatened alternative exists). It is off, it starts at r470, and with `EG_UNSEEN_LEN 6` any unseen-tail head gets K=6, which covers the whole view so the veto never finds an alternative (ROUND2 builder: "no effect").
- **Minimal fix (new flag, default 0, `QK_EG=1`):**
  - In `egOn()` also return true for `amQueen() && queenKingRound() && myLen >= 12`.
  - For that case, floor the unseen-tail length at 4 instead of `EG_UNSEEN_LEN`: K=3, and the penalty ring K+1 covers a 1-pearl lunge.
  - A crowned queen has 3-11 free steps per turn, so she can always outrun an L3-6. The veto already requires `candDepth >= QUEEN_VETO_DEPTH` and `!candDead`, so it cannot push her into a dead end.
  - About 6 lines in egOn / evalDir. Do not use the `ENDGAME_GUARD=300` parameter alone: it also bans voluntary splits for the king and for small uncrowned queens from r300.
- **Server stat:** crowned queen (L >= 15) killed head-on after r300, per crowned game on Portals/Maze/AUNSW/TD/Slithery. Now 6 of 19 (Maze 3/3, AUNSW 2/2, TD 1/3); target 2 or fewer. Guard stats: crowned queen length at r500 must not fall; Portals stays at 9/10 alive.
- **Limits:** 2 of the 6 killers were outside her view at Chebyshev 4. That needs an ally "enemy head near our queen" relay, which is not minimal.

### 2. Crowned queen coils into a dead end, then QBOX_K2 sheds 2 per turn (Portals, TD; 1 loss decided, 1 contributing, 3 wins lost 24-42 queen length)
- **Code path:**
  - `evalDir` asks `surviveDepth(t, wantDepth)` with `wantDepth = max(SURVIVE_DEPTH, min(myLen, KING_SURVIVE_DEPTH))` = 12 for every L >= 10 (main.cpp:6076; `KING_SURVIVE_DEPTH 12`, params.hpp:301).
  - For an L40-58 queen a lane closed by her own body 13-20 steps ahead scores as fully safe, so she enters it. She then has one legal move per turn until `bestD < 0`, and `QBOX_K2` (main.cpp:6537-6538) emits `SPLIT 2` every turn until the blocking segment becomes her tail (38->2, 46->10, 50->8, 58->34).
  - On Portals the DFS uses `step()` (main.cpp:1520), which crosses portals, while `qparkBan()` (main.cpp:2849-2864) forbids her those crossings. A notch whose only exit is a portal (1086127 at (12,15)) therefore looks escapable to the search, but the park will not let her use it.
- **Minimal fix (new flag `QK_SURV=1`):**
  - At main.cpp:6076, for `amQueen() && queenKingRound()` use `wantDepth = min(myLen, QK_SURV_DEPTH)` with `QK_SURV_DEPTH 30`.
  - In `surviveDepthImpl` skip `qparkBan(f.tile, d)` steps (one `continue` after line 1520; first-tile check too).
  - CPU: the DFS stops at the first path that reaches maxDepth and `nodeCap` is 60000, but check the CPU max locally (2 sandbox games on Portals and TD with a long queen; it must stay under ~40M of 100M).
  - Optional backstop: for a queen of L >= 20 with `bestD < 0`, shed `k = myLen - (index of the body segment adjacent to the head) + 1` in one split instead of repeated 2s. The queen length lost is the same, but one long child keeps the mass for the longest-dragon tiebreak instead of 10-20 L2 children.
- **Server stat:** runs of 3 or more consecutive queen `SPLIT 2` at L >= 12 after r300. Now 5 in ~20 crowned games (Portals 3/10, TD 2/3); target 0-1. Also queen length at r500 on Portals/TD.

### 3. We never finish a lone or visible enemy queen after ours dies (Devil, TD, Default; 3 clear losses, plus 4 Slithery on the queen-tiebreak shape)
- **The games:**
  - Devil 1088849 vs ouroboros (1801): 146 v 3. Their L3 queen was in view of one of our heads on 353 rounds after r43, 20 of them next to an L5+ unit.
  - TD 1087100 vs horse: 62 v 15. Their L15 queen was seen on 115 rounds.
  - Default 1087083: their L2 queen was seen on 99 rounds.
- **Code path:** the king gate in `tryRam()` returns before the queen-kill call: `if (!ENABLE_RAM || units < 2 || (feedPhase() && iAmKing())) return false;` (main.cpp:4473). The built flags `QKILL_KING` (main.cpp:4468, params.hpp:1679) and `LATE_HUNT` (lhOn main.cpp:2296, params.hpp:1612) are 0.
- **Minimal fix:** server-test `LATE_HUNT=1 QKILL_KING=1` alone (scratch stage `r2/stage/P1_qkill`), not bundled with SPLIT_NEEDS_EXIT as c1 was. The f1 `QKILL_FUEL` test (queued) touches the same `tryQueenKill`, so test them one at a time.
- **Server stat:** r500 losses with our queen dead and theirs alive while we lead on total or longest, per 100 games (here 8 of 114, 7.0%); `any_qkill` and `king_qkill` from `tools/ab_mech.py`.

### Not ranked (no cheap verified fix, or already in a build)
- **Lane-map eliminations against the top 10 (25 losses):** the economy gap opens at r26-75 with 2-6 units against 4-9 at r30. Same as v61; no new idea.
- **Slithery:** b1's 4 queen-dead losses all had our longest above their queen. q1's `PM_QPARK_SLITHERY` targets this (ranked 1-0, L85), but it also inherits causes 1 and 2. Keep or drop it on the unranked-panel check.
- **weakhold 1087097 (Q4 v 21 with 85 v 27 total) and Autarky 1093875 (Q14 v 26 next to our L30 king):** tiebreak-aware feeding (feed the queen when theirs is longer). q1's weakhold crown covers the first.
- **Schooltime q3 v q3 (3):** economy, unchanged.

## Per-loss table (49)
"gap" is the first round their total reached 1.5x ours + 10.
| game | build | map | opponent (tier, Elo) | cause | queen death / end | r500 margin or gap | note / counterfactual |
|---|---|---|---|---|---|---|---|
| 1087080 | b1 | Autarky | SSS (top10, 2266) | eliminated | r32 L5 H2H by enemy by L3 | gap r170; r30 units 14 v 15; ended r314 | economy gap (lane map), queen lost early; no cheap fix |
| 1087072 | b1 | Autarky | dev test 1 :P (top10, 2297) | eliminated | r144 L6 H2H by enemy by L4 | gap r189; r30 units 13 v 15; ended r446 | economy gap (lane map), queen lost early; no cheap fix |
| 1090202 | q1 | Default | Sponge(Albert and Bob) (top10, 2254) | eliminated | r210 L5 H2H by enemy by L2 | gap r120; r30 units 9 v 11; ended r352 | economy gap (lane map), queen lost early; no cheap fix |
| 1087069 | b1 | Devil | dev test 1 :P (top10, 2297) | eliminated | r21 L5 H2H by enemy by L2 | gap r54; r30 units 7 v 7; ended r73 | economy gap (lane map), queen lost early; no cheap fix |
| 1090199 | q1 | Devil | Sponge(Albert and Bob) (top10, 2254) | eliminated | r78 L5 H2H by enemy by L3 | gap r74; r30 units 6 v 7; ended r126 | economy gap (lane map), queen lost early; no cheap fix |
| 1087084 | b1 | Maze | aAah (top10, 2250) | eliminated | r363 L42 H2H by enemy by L4 | gap r172; r30 units 8 v 9; ended r488 | crowned queen L42 rammed head-on r363 by an L4 lunging 4 steps (2 pearls) from Chebyshev 4, outside her view; army then collapsed (r300 72 v 219) -> eliminated r488 ; fix: QK guard (partly: killer unseen) + Maze economy |
| 1087088 | b1 | Queen Of Spades | bread first search (top10, 2191) | eliminated | r218 L6 H2H by enemy by L4 | gap r115; r30 units 5 v 5; ended r236 | economy gap (lane map), queen lost early; no cheap fix |
| 1087071 | b1 | Queen Of Spades | dev test 1 :P (top10, 2297) | eliminated | r82 L6 H2H by enemy by L3 | gap r84; r30 units 3 v 6; ended r275 | economy gap (lane map), queen lost early; no cheap fix |
| 1086398 | b1 | Queen Of Spades | Sponge(Albert and Bob) (top10, 2254) | eliminated | r45 L4 H2H by enemy by L3 | gap r62; r30 units 5 v 7; ended r189 | economy gap (lane map), queen lost early; no cheap fix |
| 1086122 | b1 | Queen Of Spades | SSS (top10, 2266) | eliminated | r43 L5 H2H by enemy by L3 | gap r83; r30 units 5 v 7; ended r225 | economy gap (lane map), queen lost early; no cheap fix |
| 1086124 | b1 | Queen Of Spades | Vibing++ (top10, 2317) | eliminated | r64 L6 H2H by enemy by L3 | gap r131; r30 units 3 v 6; ended r232 | economy gap (lane map), queen lost early; no cheap fix |
| 1087086 | b1 | Stripes | aAah (top10, 2250) | eliminated | r13 L3 HitSelf+trapsplit | gap r41; r30 units 5 v 7; ended r77 | economy gap (lane map), queen lost early; no cheap fix |
| 1087065 | b1 | Stripes | Vibing++ (top10, 2317) | eliminated | r13 L3 HitSelf+trapsplit | gap r84; r30 units 4 v 6; ended r165 | economy gap (lane map), queen lost early; no cheap fix |
| 1086128 | b1 | Stripes | Vibing++ (top10, 2317) | eliminated | r13 L3 HitSelf+trapsplit | gap r43; r30 units 4 v 6; ended r111 | economy gap (lane map), queen lost early; no cheap fix |
| 1094631 | q1 | Stripes | Computers (rest, 2066) | eliminated | r13 L3 HitSelf+trapsplit | gap r114; r30 units 4 v 3; ended r214 | economy gap (lane map), queen lost early; no cheap fix |
| 1087105 | b1 | Tower Defense | forgot to mention (top10, 2277) | eliminated | r54 L2 HitSelf+trapsplit | gap r69; r30 units 2 v 2; ended r182 | economy gap (lane map), queen lost early; no cheap fix |
| 1087093 | b1 | Tower Defense | 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿 (top10, 2247) | eliminated | r77 L4 H2H by enemy by L3 | gap r75; r30 units 2 v 2; ended r136 | economy gap (lane map), queen lost early; no cheap fix |
| 1084968 | b1 | Tower Defense | 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿 (top10, 2247) | eliminated | r85 L7 H2H by enemy by L3 | gap r128; r30 units 2 v 3; ended r297 | economy gap (lane map), queen lost early; no cheap fix |
| 1087089 | b1 | Trophy | bread first search (top10, 2191) | eliminated | r75 L5 H2H by enemy by L3 | gap r64; r30 units 2 v 4; ended r97 | economy gap (lane map), queen lost early; no cheap fix |
| 1087106 | b1 | Trophy | forgot to mention (top10, 2277) | eliminated | r26 L4 H2H by enemy by L3 | gap r26; r30 units 2 v 8; ended r42 | economy gap (lane map), queen lost early; no cheap fix |
| 1087101 | b1 | Trophy | horse (top10, 2194) | eliminated | r30 L4 H2H by enemy by L5 | gap r28; r30 units 0 v 6; ended r30 | economy gap (lane map), queen lost early; no cheap fix |
| 1086402 | b1 | Trophy | Sponge(Albert and Bob) (top10, 2254) | eliminated | r81 L5 H2H by enemy by L3 | gap r51; r30 units 5 v 5; ended r137 | economy gap (lane map), queen lost early; no cheap fix |
| 1086123 | b1 | Trophy | SSS (top10, 2266) | eliminated | r35 L6 H2H by enemy by L3 | gap r35; r30 units 2 v 4; ended r40 | economy gap (lane map), queen lost early; no cheap fix |
| 1094620 | q1 | Trophy | ComTamSuonNuong (rest, 1998) | eliminated | r54 L6 H2H moved into enemy | gap r54; r30 units 3 v 5; ended r153 | economy gap (lane map), queen lost early; no cheap fix |
| 1092845 | q1 | Trophy | Proof by Intimidation (rest, 1894) | eliminated | r78 L5 H2H by enemy by L3 | gap r51; r30 units 9 v 8; ended r98 | economy gap (lane map), queen lost early; no cheap fix |
| 1087087 | b1 | Around UNSW | aAah (top10, 2250) | r500 queen dead | r46 L6 H2H by enemy by L3 | Q 0 v 3, longest 17 v 33, total 89 v 420 | queen L6 rammed r46 by a small enemy; their army 420 v 89 (gap r42) ; fix: economy (aAah) |
| 1090198 | q1 | Around UNSW | Sponge(Albert and Bob) (top10, 2254) | r500 queen dead | r385 L44 H2H by enemy by L4 | Q 0 v 24, longest 31 v 65, total 178 v 226 | crowned queen L44 rammed r385 by a visible L4 3-step lunge (she stepped to distance 3 = K(4)); theirs L24 alive ; fix: QK guard flips it (L44 > 24) |
| 1087083 | b1 | Default | aAah (top10, 2250) | r500 queen dead | r80 L5 H2H by enemy by L3 | Q 0 v 2, longest 14 v 5, total 28 v 119 | queen L5 rammed r80 by L4 from 5 (unseen); their L2 queen seen 99 rounds; we behind on total 28 v 119 ; fix: P1 hunt |
| 1088849 | q1 | Devil | ouroboros (rest, 1801) | r500 queen dead | r43 L5 H2H by enemy by L3 | Q 0 v 3, longest 11 v 3, total 146 v 3 | queen dead r43 (H2H by L3); then 146 v 3 for 450 rounds, their L3 queen in our view 353 rounds ; fix: LATE_HUNT + QKILL_KING (P1) |
| 1087070 | b1 | Islands | dev test 1 :P (top10, 2297) | r500 queen dead | r283 L3 HitSelf+trapsplit | Q 0 v 66, longest 20 v 66, total 83 v 229 | queen L7 shed chain HitSelf r283; their queen L66 ; fix: none cheap (we were behind 83 v 229) |
| 1086125 | b1 | Maze | Vibing++ (top10, 2317) | r500 queen dead | r228 L6 H2H by enemy by L11 | Q 0 v 95, longest 28 v 95, total 36 v 176 | queen L6 rammed r228 by an L12 (pre-crown, at the field doorway); their queen L95 ; fix: Maze economy (r200 99 v 176) |
| 1087081 | b1 | Slithery Fight | SSS (top10, 2266) | r500 queen dead | r298 L3 Body ally | Q 0 v 33, longest 95 v 69, total 255 v 202 | queen L3 boxed by ally body r298 (Slithery, not parked in b1); our longest 95 > their queen 33 ; fix: q1 Slithery park (crown) |
| 1087104 | b1 | Slithery Fight | forgot to mention (top10, 2277) | r500 queen dead | r352 L7 H2H by enemy by L3 | Q 0 v 51, longest 86 v 62, total 171 v 229 | queen L7 rammed r352 by L3 2 steps; our longest 86 > their queen 51 ; fix: q1 Slithery park |
| 1086400 | b1 | Slithery Fight | Sponge(Albert and Bob) (top10, 2254) | r500 queen dead | r431 L14 H2H by enemy by L3 | Q 0 v 60, longest 91 v 60, total 139 v 239 | queen L14 rammed r431 by L4 6-step pearl lunge; our longest 91 > their queen 60 ; fix: q1 Slithery park |
| 1084967 | b1 | Slithery Fight | 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿 (top10, 2247) | r500 queen dead | r133 L2 HitSelf+trapsplit | Q 0 v 54, longest 73 v 54, total 251 v 165 | queen L8 shed chain HitSelf r133 (kelp corridor); our longest 73 > their queen 54 ; fix: q1 Slithery park |
| 1087100 | b1 | Tower Defense | horse (top10, 2194) | r500 queen dead | r84 L2 Body ally+trapsplit | Q 0 v 15, longest 62 v 15, total 83 v 23 | queen L4 boxed by allies, shed to L2, dead r84; we had 62 longest v their L15 queen, seen 115 rounds ; fix: P1 hunt; P3 ally keep-out |
| 1094618 | q1 | Tower Defense | ComTamSuonNuong (rest, 1998) | r500 queen dead | r473 L32 H2H by enemy by L3 | Q 0 v 8, longest 20 v 8, total 42 v 50 | crowned queen L46 coiled into a dead-end lane next to an L3 (r428), shed 2 x18 to L10 (r429-446), regrew to L32, rammed r473 by an L3 1 step away while boxed ; fix: QK survive depth + QK guard |
| 1086121 | b1 | Australia | SSS (top10, 2266) | r500 both dead longest | r60 L3 Body ally+trapsplit | Q 0 v 0, longest 51 v 52, total 140 v 268 | longest lost by 1 (51 v 52); queen boxed by an ally r60 ; fix: q1 Australia park |
| 1087074 | b1 | Default | Sponge(Albert and Bob) (top10, 2254) | r500 both dead longest | r49 L6 H2H by enemy by L3 | Q 0 v 0, longest 13 v 36, total 17 v 107 | longest lost |
| 1084966 | b1 | Islands | 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿 (top10, 2247) | r500 both dead longest | r91 L6 H2H by enemy by L3 | Q 0 v 0, longest 67 v 85, total 104 v 210 | longest lost |
| 1094633 | q1 | Islands | Computers (rest, 2066) | r500 both dead longest | r95 L5 H2H by enemy by L2 | Q 0 v 0, longest 34 v 35, total 73 v 185 | longest lost by 1 (34 v 35); behind on total from r400 |
| 1087063 | b1 | Maze | Vibing++ (top10, 2317) | r500 both dead longest | r369 L41 H2H by enemy by L5 | Q 0 v 0, longest 8 v 86, total 12 v 226 | crowned queen L41 rammed r369 by an L6 (4-step lunge, ended 4 from killer; K(6)=6); all mass was in her, our longest after = 8 v 86 ; fix: QK guard |
| 1086127 | b1 | Portals | Vibing++ (top10, 2317) | r500 both dead longest | r409 L2 HitSelf+trapsplit | Q 0 v 0, longest 40 v 49, total 46 v 65 | crowned queen L38 walked into a notch whose only exit is a portal (banned for her), shed 2 x15 (r391-408), died HitSelf L2 r409; their queen dead since r27 -> L38 queen alive wins ; fix: QK survive depth (skip banned portal steps) |
| 1087103 | b1 | weakhold | forgot to mention (top10, 2277) | r500 both dead longest | r284 L2 H2H by enemy+trapsplit by L2 | Q 0 v 0, longest 5 v 38, total 10 v 80 | longest lost |
| 1093875 | q1 | Autarky | Computers (rest, 2066) | r500 queen shorter | alive L14 | Q 14 v 26, longest 30 v 26, total 57 v 95 | king L30 grew beside a L14 queen; theirs L26 ; fix: tiebreak-aware feed (feed the queen when theirs is longer) |
| 1087085 | b1 | Schooltime | aAah (top10, 2250) | r500 queen shorter | alive L3 | Q 3 v 3, longest 3 v 20, total 3 v 363 | Schooltime box q3 v q3, longest lost (economy) |
| 1087078 | b1 | Schooltime | SSS (top10, 2266) | r500 queen shorter | alive L3 | Q 3 v 3, longest 47 v 93, total 164 v 368 | Schooltime box q3 v q3, longest lost (economy) |
| 1092847 | q1 | Schooltime | Proof by Intimidation (rest, 1894) | r500 queen shorter | alive L3 | Q 3 v 3, longest 25 v 41, total 95 v 173 | Schooltime box q3 v q3, longest lost (economy) |
| 1087097 | b1 | weakhold | 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿 (top10, 2247) | r500 queen shorter | alive L4 | Q 4 v 21, longest 24 v 21, total 85 v 27 | both queens alive: ours L4 parked/starved, theirs L21; we had 85 v 27 total ; fix: weakhold queen crown (q1 flag) or tiebreak-aware feed |

## Round 6 build: QK_EG / QK_SURV (5 Oct, local sandbox only; nothing submitted)
Built in `bot/`, all default 0. Flags off = b1 play: 8/8 identical fingerprints vs `variants/b1` (Australia, Devil, Portals, Maze, both sides, seed 1000).
- **QK_EG=1:** `egOn()` is also true for the crowned queen (`amQueen() && queenKingRound() && myLen >= QK_EG_MINLEN` 12). That turns on the endgame-guard K(Lv) penalty and veto at any round; an unseen tail counts as `QK_EG_UNSEEN_LEN` 4. The split ban moved to `egOrigOn()` (ENDGAME_GUARD only), so kings and small queens are untouched.
- **QK_EG=2:** QK_EG=1 plus, in `computeThreats()`, full threat reach `min(K(Lv), QK_EG_KRCAP 5)` for her (threat penalty and the queen threat veto). An enemy head that closed in two rounds in a row gets +1 (`QK_EG_TREND` 1). `QK_EG_KING=1` gives the same reach to our king (L >= 10); it is built but untested.
- **QK_SURV=1:** the crowned queen's look-ahead depth is `max(old, min(L, QK_SURV_CAP 30))`, and `qparkBan` steps are blocked inside `surviveDepth`. CPU bounds: `QK_SURV_NODES` 8000 per candidate, `QK_SURV_FSNODES` 2000 per free-path node, and the old depth past `QK_SURV_BUDGET_M` 22M points. The first version at 60000 nodes hit 94M on TD.

Paired sandbox games, candidate vs bot/ (both with PM_QPARK_AUNSW=1 PM_QPARK_TOWER=1), seeds 2000-2009, both sides. Columns show cand / base. "rams" = queen at L15+ killed head-on after r300. "shed" = runs of 3+ consecutive queen SPLIT 2 at L12+ (segments shed in brackets).
| flag | map (n) | rams | shed runs (segs) | queen alive r500 | queen len r500 | longest r500 |
|---|---|---|---|---|---|---|
| QK_EG=1 | Portals (10) | 0 / 0 | 8 (196) / 7 (180) | 8 / 7 | 27 / 31 | 34 / 35 |
| | Maze (20) | 4 / 3 | 6 (84) / 10 (192) | 15 / 15 | 51 / 47 | 61 / 56 |
| | AUNSW (20) | 7 / 7 | 3 (66) / 4 (102) | 7 / 7 | 22 / 20 | 52 / 49 |
| | TD (10) | 1 / 1 | 3 (72) / 2 (76) | 7 / 7 | 20 / 20 | 24 / 24 |
| QK_EG=2 | Portals (10) | 0 / 0 | 8 (196) / 7 (180) | 8 / 7 | 27 / 31 | 34 / 35 |
| | Maze (20) | 3 / 3 | 9 (192) / 10 (192) | 16 / 15 | 51 / 47 | 59 / 55 |
| | AUNSW (20) | 6 / 7 | 8 (230) / 4 (74) | 8 / 7 | 21 / 23 | 49 / 49 |
| | TD (10) | 1 / 1 | 3 (72) / 2 (76) | 7 / 7 | 20 / 20 | 24 / 24 |
| QK_SURV | Portals (10) | 0 / 0 | 4 (80) / 3 (66) | 8 / 10 | 35 / 40 | 38 / 40 |
| | Maze (10) | 3 / 2 | 3 (78) / 4 (112) | 6 / 7 | 34 / 47 | 57 / 59 |
| | AUNSW (10) | 3 / 3 | 3 (34) / 2 (44) | 3 / 4 | 18 / 29 | 47 / 55 |
| | TD (10) | 1 / 1 | 2 (70) / 2 (76) | 7 / 7 | 21 / 20 | 24 / 23 |
Total length at r300 is the same in every pair (play diverges only after the crown).

- **QK_EG: the sandbox cannot test the server failure.**
  - Self-play rams are swarms. The crowned queen is coiled against kelp with 6-10 enemy L2-4 heads around her, so every step is inside someone's reach.
  - With R2_DEBUG on, in 24 games the veto never fired. Each queen logged "egfree" on 30-260 turns and "eg0" (no safe alternative) on 0-9.
  - Over 60 games QK_EG=2 moved slightly the right way: rams 10 v 11, queen alive at r500 39 v 36. This is within noise. QK_EG=1 was flat (rams 12 v 11, alive 37 v 36).
  - The isolated 3-5 step lunge from a lone L3-6 (server, Vibing++) needs a server test.
- **QK_SURV moved the shed mechanism a little but the guard stats the wrong way.**
  - Over four settings (60000 nodes, 8000, the final 8000/2000+budget, and cap 64), segments shed fell 12-42% against the same-run base.
  - But queen alive at r500 fell by 1-4 in every run, and queen length at r500 fell on Portals, Maze and AUNSW.
  - The sandbox shed chains are not the server shape (a lane closed 13-20 steps ahead). They are an L40-62 queen coiled inside a park region smaller than her body (Portals 2000_A, AUNSW 2003_B), where no 30-step path exists. QK_SURV also produced a new L48 HitSelf on AUNSW 2003_B in all four settings.
  - A real fix probably needs the single big shed backstop (fix 2's option) or a park radius that grows with L, not a deeper DFS.
- **CPU (sandbox max):**
  - k1sv (QK_EG=2 + QK_SURV): Australia 33.1M, Portals 16.3M, TD 14.8M (TD unparked). With the TD park, sv2 reached 28.1M on TD and 25.8M on Portals.
  - QK_EG alone matches base: Portals 9.9M, Maze 27.4M, AUNSW 34.1M, TD 16.8M.
- **Staged:**
  - `r6/stage/k1` = bot/ + QK_EG=2 (the only flag that did not move the wrong way; QK_SURV left out).
  - `r6/stage/k1sv` = bot/ + QK_EG=2 + QK_SURV=1, for reference.
  - Neither stage has park flags beyond the bot/ defaults (Portals, Maze).
- Scripts are in the scratchpad `r6/`: mkstage.sh, qp6.py (qp.py plus rams and shed runs, QP_LOGS for R2_DEBUG counts), sumj.py, rams.py, board6.py, ident.sh.
