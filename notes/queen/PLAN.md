# v36 plan (queen rules, engine 1.2.3), 2026-10-01. Sources: DEATHS.md, META.md, FREEMOVES.md
Goal: our queen alive at r500 at any length >= 1 (META: 0/42 top-team queens survive), with no army weakening (elimination decides ~40% of games).
Base: variants/v36 = copy of v35. All flags live in params.hpp, default 0. Every flag changes only the queen (amQueen() = myId == myTeam, since queens are id 0/1)
or one formula. Non-queens run v35 unchanged, and so does everyone after our queen dies (fallback, item 5).
Test (from /Users/devsingh/Developer/UNSW_Battlecode, one game at a time): `unswbc run maps/<m>.map variants/v36 variants/v35 --seed S -o <scratchpad>/qn/v36_v35_<m>_sS.replay`, plus swapped sides.
Set M6 = default, schooltime, devil, trauma, gen/g2026_01, gen/g2026_02. Seeds 1-3, both sides: 36 games. Skip slithery (pocket spawn, lost whatever we do).
Metrics: our queen alive at r500 (qdeaths.py), win rate vs v35, our queen's median death round. Ship gate: win rate >= 55% and survival >= 35% (v35 baseline 6/48 = 12%).

## S1 QUEEN_SAFE: ships first, ~2-3 h (biggest value: kills 18 "queen moved in" deaths and most of the 24 small-enemy rams)
- tryRam l.2960: `if (QUEEN_SAFE && amQueen()) return false;`. In decide l.3606, feeding=false and tryConsFeed is skipped for the queen.
  updateKingship l.1912 / iAmKing l.1954: the queen never self-crowns (a big king is a ram magnet; length is not needed to win).
- Keep v35 splits: she sheds to length 2-4 the way v35/meta do (v36q's no-split rule cost economy). Only add guards: no split when threatAt[myHead]>0,
  and her own piece must stay >= QUEEN_MINLEN=2. Parent keeps the id, so check that SPLIT k leaves the head part (the queen) >= 2.
- computeThreats l.2287: when amQueen(), reach per enemy head = F(Lvis) + 1 with F = ceil(L/4), and the cap is ignored. Unseen tail -> Lvis = max(Lvis, 4).
  Ally heads within 1 tile also count as threats (no ally head-on).
- Move loop l.3938 / scoring l.4018: for the queen, give a threatened tile -QUEEN_THREAT_PEN (300). Hard veto of threatened tiles when any unthreatened legal tile exists.
  Add +QUEEN_EXIT_W * (free exits of t) and -QUEEN_HEAD_W/dist(t, nearest enemy head) when dist <= 4.
- Risk: low. A passive queen forages less, but at length 2-4 her eating is <1% of team food anyway (META).

## S2 FREE_FIX: correct costs under free moves (self-kill fix, all dragons)
- tryEatSprint l.2879: `net = eaten - max(0, steps-F)`, `tailFreed = (steps-eaten) + max(0, steps-F)` (copy from v36q). tryKingEscape l.3337: same, and n-F in ESC_SPRINT_COST.
- surviveDepth l.1224: count turns as ceil(t/F). Flag THREAT_FREE: computeThreats/replyEnemyReach l.3191 reach = F(Lvis) for everyone with MAX_THREAT_REACH=2
  (enemies of length 5+ ram from 2 tiles for free). Penalty at full strength inside free reach, x0.33 for 1-2 paid steps beyond it.
- First run 1 game with -v to confirm F is fixed at the turn's starting L and whether a free step onto a pearl gives +1.
- Test: M6 x3 both sides. Metrics: win rate and own self/ally-collision deaths per game (qdeaths.py cause column). Risk: low (FREE_FIX) / medium (THREAT_FREE makes small units timid).

## S3 QUEEN_HUNT: kill theirs (a 1-for-1 trade wins whenever ours survives)
- tryRam l.2960: if s.id == 1-myTeam (enemy queen), skip the `worth`/ramGuard checks, value += QH_BONUS (500), and allow a 2-step free ram when myLen >= 5.
  Only when units >= 3 and we are not the queen. Optional: the nearest non-queen with dist <= 8 to the last-seen enemy queen steers toward her (score bonus in the move loop).
- Test: M6 x3. Metric: the enemy (v35) queen's median death round falls; win rate. Risk: low (top teams' queens already die early, so the gain shows mostly vs updated bots).

## S4 QUEEN_LOOK: 2-3 turn lookahead and anti-coil for the queen (long trauma games, deaths at r350-450)
- For each queen first step: run surviveDepth plus replyPenalty l.3218 against enemy replies of up to F steps, and require >= 2 safe exits after the worst reply.
- queenOpen() from v36q: flood with her body as walls, penalise area < 3L+20. Prefer tiles where we reach pearls before any enemy head (Voronoi), away from the centre.
- Test: trauma/devil seeds 1-5. Metric: deaths after r150 and r500 survival. Risk: medium (CPU: keep under 40M/turn, check --sandbox).

## S5 FREE_PATH: exploit free multi-step moves (FREEMOVES A/B/D)
- New tryFreePath() before the l.3938 loop for myLen >= 5: enumerate paths of 1..F steps with the body simulated, prefilter (pearls, endpoint threat,
  exits), run the v35 eval on the top 6 endpoints, and stop at 60M points (fall back to the single step). Queen escape reuses it.
- Test: M6 x3. Metrics: win rate and pearls/turn of len>=5 dragons. Risk: high (big new code, timeouts). Ship only if >= 55% vs the best of S1-S4.

## S6 QUEEN_LATE (optional): after round 430, if both queens might be alive, allies with len <= 3 feed the queen via the existing shouldFeed/feedTarget
  path with kingTile = queen. Wins "longer queen" against bots that also protect theirs. Test only once a self-play queen survives in S1+S4.

## Item 5, fallback: queenDeadSeen (no beacon or sighting for 30 rounds after a death event) turns off every Q* flag, and v35 king/longest-dragon logic runs untouched.
Re-check META after the top teams resubmit and after the "safer spawn" maps arrive (maps/ currently matches the 1.2.3 bundle).
