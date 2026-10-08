# STATUS (single source of truth)

Last updated: 2026-10-08 17:05 EDT. All updates to the user come from this page. Times are US Eastern.

## Live and mainline
- **Mainline = `bot/`** = b4 (b3 + Tower Defense centre pull + Australia queen vault ban); b3 = b2 + Australia crowd penalty: v61 (QS_FROM=100, QSPLIT_ROOM=1) + Portals/Maze queen park and crown + QKILL_FUEL + INFER_SYM (unknown maps only). Every new idea goes into `bot/` as a flag, default 0. No vNN copies; test builds are staged in the scratchpad.
- **Last accepted live build:** f1 (= b2 on known maps; identical copy in `variants/f1` for rating-restoring re-uploads). b1 copy kept in `variants/b1`.
- **Fallbacks:** `variants/v61`, `variants/v44`. Re-uploading an identical build restores its old rating.
- **Kept in `variants/`:** b1 (live), v61, v44 (fallbacks), v35, v38m (local test opponents).
- **Challenge budget:** the server allows 60 challenge games/h (12 series). Unranked series let us choose maps, so map-specific fixes are tested with the loop restricted to their maps.

## Key dates
- **Official (8 Oct update):** freeze 9 Oct 06:00 UTC = **Fri 9 Oct 2:00 AM EDT**; last active submission = Qualifier submission; then 3-4 h autoscrims on the current 17-map pool set seeds; Qualifier 10 Oct, Bo7, ALL UNSEEN maps; top 10 eligible go to the Grand Final. Strategy: known-map play (seeding) stays b4; Qualifier gains must come from unknown-map-gated changes that keep the 17 maps byte-identical.
- **Submission freeze for the Qualifier:** Fri 9 Oct, 2:00 AM EDT. Seeding comes from the final ladder.
- **Qualifier stream:** Sat 10 Oct, 2:30 AM EDT. Best of 7, knockout, unseen maps.
- **Grand Final:** 17 Oct.

## Rating strategy (8 Oct)
- Ranked challenges go only to teams where our win rate beats the Elo expectation (gain even when we lose 2-3): SSS (W .44 vs E .19), larp (.40 vs .15), horse (.38 vs .24), Cutlery, FTM (.31 vs .23). Dropped Sponge (.32 vs .46), bread first search, Team SKKU (below expectation). Recompute with the snippet in notes/journal.md 8 Oct.

## How we test (lessons, in order of trust)
0. **Ranked challenges only while an accepted build is live.** Test builds get unranked challenges only (u1 lost 69 Elo in its first ranked series because new uploads start with high uncertainty).
1. **Server A/B is the judge.** One build is live at a time, for about 2-3 h (challenge loop at 45/h plus autoscrims).
   - Score it with `python3 tools/ab_server.py <base> <cand>`. It reports PAE: our score minus the Elo expectation per game, so opponent strength is controlled for. See notes/newrules/AB_SERVER.md.
   - Lose → re-upload the identical base, and its rating comes back.
2. **Local self-play on known maps is nearly useless for strategy.** Most maps come out 2/4, because the side decides. Use it only to check a build compiles, doesn't crash, stays under CPU, and has the intended mechanism (stats).
3. **Unseen-map checks for the Qualifier:**
   - `tools/unseen_eval.py --sets real,realhold,blind17`. These are realistic generated maps, plus the official maps with map knowledge off.
   - The old gen/lesson/gated sets don't look like real maps.
4. **Map-identification changes must play identically to the live build on all 17 official maps.** v49 broke this and lost.

## Server A/B scoreboard
| build | change | verdict | numbers |
|---|---|---|---|
| v43 | QALLY_KEEP + QBOX_K2 (allies stay off queen, boxed queen sheds 2) | kept | 2095-2123 |
| v44 | WH_CENTRE (weakhold opening) | kept | ~2094 |
| v49 | MATCH_STRICT full (map gossip on idle sonar) | **LOSS** | -4.8 pp (CI -8.8..-0.7); Stripes/QoS/Devil/Portals collapsed |
| v55 | QS_FROM=100 (queen joins early economy before r100) | **WIN** | +5.7 pp (CI +0.6..+11.4); 2051 → 2133; vs top-10 +13 |
| v60 | QEXIT_LOOK (queen avoids ≤1-exit tiles) | loss | -1.4 pp; 2094 vs 2126 |
| v61 | QSPLIT_ROOM=1 (early queen avoids pocket splits) | **WIN** (leaning) | +3.2 pp; 2126 → 2174; 11/17 maps |
| v64 | LUNGE34 (3-4 step lunges) + INFER_SYM | **LOSS** | -6.8 pp; 2136 vs 2174; lunges cost length |
| v65 | QK_BIG (queen becomes the king on big maps) | **LOSS** | -6.4 pp; 2143; 5/17 maps |
| v69 | QEARLY_PEN (queen portal/blind penalties before r100) | loss (leaning) | -4.8 pp (CI -12.9..+3.3); 2121 vs 2187; 6/17 maps; vs top-10 -1.8 vs +12.2 |
| c1 | SPLIT_NEEDS_EXIT + LATE_HUNT + QKILL_KING | **LOSS** | 81 games: adjusted -9.9 pp, P(better) 0.03. Stillborn splits did fall (11.3 → 4.3 per game) and queen alive at r100 rose (40% → 55%), but total length vs opponent at r300 fell (x0.66). Bundle, so the culprit isn't isolated; SPLIT_NEEDS_EXIT is the suspect. |
| m1 | Map pack: Portals/Maze queen park+crown, Stripes loop, Trophy early split, Schooltime B | partial (95 games): overall adjusted +9.6 pp, P(better) 0.99 | Portals: queen alive at r500 0% → 90%, wins 42% → 70% (n=10). Stripes 92% (n=13). Maze and Trophy flat (n=10-15). **Schooltime worse**: wins 77% → 45% (n=11), r300 length x0.54 → PM_SCHB dropped. |
| m2 | m1 without the Schooltime change | **WIN** | 219 games: adjusted +7.5 pp (CI +1.0..+13.4), P(better) 0.99. Pooled m1+m2 per map vs v61: Portals 54% vs 41% (queen alive r500 85% vs 0%); Maze 40% vs 35% (queen alive 34% vs 10%); Stripes 85% vs 84% (flat → off); Trophy 64% vs 70% (→ off). |
| b1 | v61 + PM_QPARK_PORTALS + PM_QPARK_MAZE (new mainline) | live since Sun 6:55 PM, ranked loop on all maps | baseline block for the next tests |
| q1 | b1 + queen park on Australia/Around UNSW/Slithery/Tower Defense/weakhold | **LOSS** | per map vs v61 (unranked panel vs v61's mixed baseline, so biased against q1, but mechanisms agree): Australia 41% vs 56%, Around UNSW 40% vs 59%, Slithery 16% vs 31%, Tower Defense 43% vs 69% with eliminations 8% → 44% and r100 length ratio x0.29. All five off. Park helps only on Portals/Maze. |
| f1 | b1 + QKILL_FUEL (Codex: pearl-paid steps in the certain queen-kill search) | **accepted** (neutral) | 240 games: adjusted -0.1 pp (CI -12..+11), P 0.50; mechanism: enemy queen killed 39% → 43%, eliminated 27% → 12% (raw, opponent mix differs). Narrow, sound change → kept. Rating-restore copy: variants/f1. |
| h1 | b2 + LATE_HUNT + QKILL_KING (lone enemy queen kill, alone) | **LOSS** | 586 games: adjusted -2.1 pp (CI -9.6..+5.3), P 0.29 → drop at 500. King queen kills 0% → 4% but no gain. f1 restored (2221). |
| k2 | b2 + QK_EG=2 (crowned-queen kamikaze guard) | **LOSS** (mechanism) | 313 games: adjusted -0.9 pp, P 0.41; target stat wrong way: queen alive at r500 Portals 92% → 81%, Maze 56% → 39% (mostly vs dev team). Dropped; f1 restored (2221). |
| cm1 | b2 + CROWD_MAPS=3 (crowd penalty on Around UNSW + Australia) | **accepted for Australia only** | per map (n 12-28, cm1 mostly vs dev team): Australia length ratio r100 1.65 → 2.51, r300 1.21 → 2.07, wins 50% → 57%; Around UNSW stillborn down but ratio flat, wins 67% → 46% → bit off. Mainline b3 = CROWD_MAPS=2. |
| s1 | b3 + SPLIT_DEFER=3 | **LOSS** | 318 games: adjusted -4.8 pp (CI -13.2..+3.8), P 0.14. Stillborn by r100 12.6 → 4.5 per game, but length ratio r100 1.82 → 1.20, eliminated 11% → 24%. Second time that blocking/deferring splits backfired (c1 too): stillborn children are cheap and the extra splits pay off. Don't retry. |
| b3 | mainline: b2 + Australia crowd penalty | live since Mon 10:35 AM (inherited 2232 from cm1) | |
| l1 | b3 + lane-map small queen (TD, Devil late, Autarky, QoS) | **LOSS** | vs dev team on those maps, l1 vs earlier builds (h1+s1): Autarky 0/20 vs 0/19, TD 3/20 vs 4/19, QoS 6/20 vs 5/20, Devil 6/20 vs 11/20. Adjusted -5.0 pp, P 0.13. b3 restored. |
| ms1 | b3 + MIDSIZE (half of units split at L6 from r150) | **LOSS** | 356 games: adjusted -5.8 pp (CI -12.4..+1.3), P 0.05. r300 length ratio x1.18 but wins down. b3 restored. |
| u1 | b3 + 5 map-specific fixes (QVAULT, PM_TROPHY_RG, PM_TD_PULL, QG_RAM, SCH_DOORS/CHAMBER) | **pulled** after 0-5 ranked vs Sponge (2212 → 2131) and weak dev-team games; user call. b3 restored. |
| v1 | b3 + PM_TD_PULL + QVAULT=3 + SCH_DOORS (unranked) | **partly accepted** | per map vs b3: TD wins 41% → 60%, eliminated 48% → 24%, r100 length x2.6 (keep); Australia queen alive r100 18% → 45%, wins 53% → 58% (keep QVAULT bit 2); Slithery queen alive r100 57% → 87% but wins 25% → 21%, r300 length x0.86 (bit 1 off); Schooltime wins 36% → 25% (SCH_DOORS off). New mainline b4. |
| b4 | mainline: b3 + PM_TD_PULL=2 + QVAULT=2 (Australia) | **live (ranked)**, re-uploaded Wed 3:30 PM (2220); copy variants/b4 | |
| qf1 | **Qualifier build, live since Thu 1:00 PM**: b4 + QE_KR=2 (pearl-aware early-queen kamikaze reach) + UNK_PORTAL_SIDES=2, both gated to never-identified maps | known maps: 40/40 full-trace identical to b4 (17 maps + Schooltime B x3, both sides); unseen vs b4: .570 and .518 on two seed bases (pooled .544, 456 games); unknown_neck fixture: queen suicide fixed; CPU same as b4 (rare 40-54M spikes on a 64x64 map, b4 too; judge limit 100M). Copy: variants/qf1. Fallback: variants/b4. |
| kf1 | b4 + QKILL_KING + QKK_FREE | **LOSS** | 392 games (unranked): adjusted -6.0 pp (CI -16..+4), P 0.13. King queen kills barely changed. b4 restored. |
| ag1 | qf1 base + UNK_GOV=50 (aAah split cap, unseen only) | **not shipped** | unseen vs b4: .491 / .531 (pooled .511, 456 games). Mid-size mass spreads away from the king and loses longest-dragon tiebreaks. |
| cx1 | UNK_XP=1 (Cutlery-style portal crossing, unseen only) | **not shipped** | unseen vs b4: .487 / .539 (pooled .513); realhold under .5 on both seeds. Early blind queen crossers die early (ours 8/8, Cutlery 32/43). |
| qn1 | qf1 + QNO_UNKPORTAL (queen never crosses unknown portals, unseen only) | **not shipped** | 17 maps + Schooltime B: 40/40 identical to qf1. Mechanism (10 blind games vs qf1): queen crossings before r100 8 → 0-3, queen alive r150 4 → 8. Unseen vs qf1: value 1 .518 / .500, value 2 .522 / .504 (blind17 .456 at 982000); ship rule needs ≥ .52 on both. Flag in bot/, default 0. |
| pb2 | b4 + QBOX_ONESPLIT | **LOSS** | Portals wins 75% → 60%, queen alive r500 83% → 80%; Maze flat; Trauma 96% → 80%. Off. |
| (next) | QKILL_KING + QKK_FREE (king takes certain free-step queen kills) | queued | all maps; 10/12 failure decisions flip, 64/74 big-open wins unchanged |
| k1 | b1 + QK_EG=2 (crowned-queen kamikaze guard, lunge reach 5 + approach trend) | staged (scratch r6/stage/k1), queued | Portals/Maze only in effect; judge on crowned-queen rams after r300 |

## What the week taught us (summary, 7 Oct)
- **Server wins came from queen handling and map-specific fixes:** QS_FROM=100 (early-economy queen), QSPLIT_ROOM, the Portals/Maze queen park, the Tower Defense centre pull and the Australia vault ban. Every one of them was either a narrow, decision-verified fix or a per-map change judged on its own map.
- **What kept losing:** broad behaviour changes copied from other teams (lunges, queen-as-king on big maps, mid-size units), anything that blocked or delayed splits (c1, s1), and queen-safety penalties that moved her deaths without preventing them.
- **Method:** decision-replay first (does the fix flip the losing decision and leave winning ones alone?), then unranked server tests judged per map. Ranked games only on accepted builds.
- **Per-map portfolio:** across about 6,000 games and 24 builds, b4 was already the best on every map once noise and confounds were removed.

## What we know about why we lose (notes/newrules/LOSS_AUDIT2.md, v55/v61, 250 losses)
- **We lose r500 tiebreaks, not fights.**
  - In 45% of losses to non-top-10 teams, our queen is dead at r500 and theirs is alive.
  - In ~21% of all losses we had the bigger army and their queen came near our heads for 10+ rounds. Example: 141 vs 2 on Devil.
- **59% of our queen deaths follow one pattern:** she eats into a kelp pocket or a 2x2 portal vault, sheds 2 at a time, and dies at L2-3. Since QS_FROM=100 this mostly happens before r100 (Portals, Australia, Around UNSW).
- **Weak maps:** Maze, Devil (early eliminations), Portals, Slithery, Around UNSW. On Around UNSW we lose the longest-dragon race despite 1.5x total length.
- **Top teams** (notes/top5/TOP2_VIBING_FTM.md, TOP1_FORGOT_TO_MENTION.md):
  - Vibing++ = Cutlery renamed, with a strong new build. It grows mid-game on big maps, uses long lunges, and keeps its queen whole until she becomes the king.
  - Copying those features directly (v64, v65) lost on the server.

## Round 2 study (2026-10-04, notes/newrules/ROUND2.md): six lenses, two skeptics
- **We lose on the queen, not on fights.** Against the top 5, combat is even; in r500 games our queen was alive in 4 of 54 and theirs in 26.
- **Most queen deaths are self-inflicted** (shed chains in 103 of 250 losses): an ally body boxes her (47), she splits with one open step (45), the pocket is too small after eating (35), and a false "exit blocked" on portal exits (25, a real bug).
- **We don't finish a lone enemy queen:** 14 of 53 losses to non-top-10 teams, with us holding 45-255 length. The king gate in tryRam returns before the queen-kill call.
- **Stillborn splits:** 14% of our split children die within a round (top 5: 4.8%).
- **A/B method:** every test so far was underpowered. Use v61's stored rating as our standing; score with the adjusted model (opponent + map effects); test in two stages (mechanism gate at ~150 games, then win rate at 250/500/850 games); fixed opponent panel; unranked challenges while a candidate is live.

**Fixes that survived both skeptics (now in bot/ as flags, default 0; staged test copies live in the scratchpad, not in variants/):**
1. P1: kill the lone enemy queen (LATE_HUNT on, king may take the kill, finisher).
2. P3: allies must not seal the queen (hard keep-out including bodies, corridor-plug look-ahead).
3. P5: stop stillborn split children (SPLIT_SAFE).
4. P6: wider threat reach for long dragons, protect the lead from r470.
5. P7: park and crown the queen on Portals and Maze (ladder only).
Refuted: P2 portal-exit bug fix (bug is real, fix doesn't change outcomes), P4 pocket test, P8 Devil queen split.

## Rejected (don't retry as-is)
- **On the server:** QEXIT_LOOK, LUNGE34, QK_BIG, full MATCH_STRICT gossip.
- **Locally, never server-tested** (low priority):
  - EQ_HUNT variants (always-on queen hunt).
  - Queen safety: QKREACH, QWARN, QESCORT, QDEAD2, QSPLIT_MIN4.
  - Economy: COVERAGE, SUICIDE_FEED, HOME_DEFEND, EARLY_PUSH.
  - Harvesters (HARVEST 1/2), EARLY_QSPLIT.
- **REAL_SWEEP** (notes/newrules/REAL_SWEEP.md): old unknown-map flags gave nothing except INFER_SYM.

## Plan (one fix at a time, focused on the r500 queen problem)
1. **LATE_HUNT** (in bot/ as flag `LATE_HUNT`, default 0; variants/v68 = on): once our queen is dead, hunt theirs map-wide. Plays identically to v61 until an ally sees our queen die (detects ~60% of deaths, 0 false alarms). Local neutral, as expected. Next server test after v69. Judge it on r500 'our queen dead' losses vs non-top-10.
2. **QEARLY_PEN** (v69): queen portal/blind penalties also before r100. Server test lost (leaning); flag not folded into bot/.
3. **King timing** (v70, SPRINT_KING_PM): Around UNSW seed 190/feed 230. Mixed locally: helps when we out-mass the opponent, hurts against equal mass. Low priority; affects 1/17 of games.
4. **Qualifier build** (before Fri 2 AM): mainline, which now has INFER_SYM on (unseen-only, ~.55 blind in two runs) + MATCH_STRICT-lite. Unseen queen park (QPARK_UNK) rejected: .579, .526, .465 on three seed sets, official-blind always below .50.

## Where things are
- Journal (timestamped log, UTC): notes/journal.md
- Rules: notes/RULES_2026-10-01.md; older references in notes/01-04.
- Active analysis: notes/newrules/{AB_SERVER, LOSS_AUDIT2, UNSEEN_GENERALISATION, REAL_SWEEP}.md, notes/top5/.
- Archived on 2026-10-04: archive/variants_20261004, archive/bot_oldrules_20261004, archive/notes_oldrules_20261004, archive/notes_newrules_20261004, archive/root_misc_20261004.
