# STATUS (single source of truth)

Last updated: 2026-10-04 00:30 EDT. All updates to the user come from this page. Times are US Eastern.

## Live and mainline
- **Mainline = `bot/`** = v61: v51 + `QS_FROM=100` + `QSPLIT_ROOM=1`. Every new idea goes into `bot/` as a flag, default 0. No more vNN copies.
- **Live on server:** v61 (identical copy kept in `variants/v61` for rating-restoring re-uploads). Rating ~2176.
- **Fallback:** `variants/v44`. Re-uploading an identical build restores its old rating.
- **Kept in `variants/`:**
  - v35, v38m: local test opponents (older styles).
  - v44: fallback.
  - v55: proven step.
  - v61: live, identical copy.
  - v68, v69, v70: in progress; they get folded into `bot/` as flags.
  - Everything else is in `archive/variants_20261004/`.

## Key dates
- **Submission freeze for the Qualifier:** Fri 9 Oct, 2:00 AM EDT. Seeding comes from the final ladder.
- **Qualifier stream:** Sat 10 Oct, 2:30 AM EDT. Best of 7, knockout, unseen maps.
- **Grand Final:** 17 Oct.

## How we test (lessons, in order of trust)
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

**Fixes that survived both skeptics (being built into bot/ as flags, default 0):**
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
4. **Qualifier build** (before Fri 2 AM): mainline + INFER_SYM=1 (unseen-only, +.548 blind) + MATCH_STRICT-lite (already in). Check that blind17/real don't regress.

## Where things are
- Journal (timestamped log, UTC): notes/journal.md
- Rules: notes/RULES_2026-10-01.md; older references in notes/01-04.
- Active analysis: notes/newrules/{AB_SERVER, LOSS_AUDIT2, UNSEEN_GENERALISATION, REAL_SWEEP}.md, notes/top5/.
- Archived on 2026-10-04: archive/variants_20261004, archive/bot_oldrules_20261004, archive/notes_oldrules_20261004, archive/notes_newrules_20261004, archive/root_misc_20261004.
