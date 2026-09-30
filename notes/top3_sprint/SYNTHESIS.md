# Top-3 synthesis (30 Sep, ~21:20 UTC / 17:20 EDT). Sources: Cutlery.md, cheji_bt.md, 3_14159265.md

## (A) Patterns all top-3 share that we lack, ranked by evidence
1. The early unit count keeps growing on small, dense maps (strong: all 3 reports, many replays).
   - Devil at r100: 27-48 of their units vs our 1-5. Trophy at r100: 41-45 vs 5. Splits by r100: 59-85 vs our 15-35.
   - We are eliminated at r106-141 on Devil and Trophy even when we win the head-on count (Trophy 13-6).
   - Our splitting stalls after r50. The split rule matches theirs, so the cause is the gates plus length-2 self-trap deaths
     (14 HitSelf at length 2-3 on Devil). Our worst head-to-head maps: Default, Devil, Trophy, QoS.
2. Short multi-step moves to eat pearls (medium: Cutlery about 26 per game and cheji 55-763 per game; 3.14159265 does NOT do this).
   - Our EAT_SPRINT already lost (0.463, journal 15:28) and is on the do-not-re-run list in notes/unseen/PLAN.md.
   - The narrow form is untested: length 2-4, pearl on every step, each step checked safe.
3. More aggressive sprint rams, including 3-step rams and rams by length-2 dragons (Cutlery only; about -33 length per game for us). One team, so medium-low.
4. Consolidation late (all 3), but LATE_SPLIT_KING_MAPS=340 was already rejected on the server (journal 04:33). Not a gap to chase again.
5. Sonar on every unit (3.14159265 only; we sent 0-1 pings in the Devil and Trophy losses). Unclear whether it is a cause or a symptom of having almost no units.
Not gaps: overall splitting rate on large maps, suicide-feeding volume, portal handling (mixed; Cutlery's portal king is one map, 3 games).

## (B) Change before the 23:00 UTC freeze: NO CHANGE BEFORE FREEZE.
- The two candidates that are flags or single numbers have both already lost:
  - EAT_SPRINT: 0.463 locally.
  - LATE_SPLIT_KING_MAPS 340: rejected on the server.
- The real gap (#1) sits in the split, escape and self-trap gates. There is no single numeric flag for it that we have evidence for.
- A 40-minute unseen_eval at --jobs 2 cannot resolve a +-3% effect, and several forensic fixes lost on the server today. Keep v35.

## (C) Qualifier (10 Oct) priorities
1. Small-map swarm growth. Instrument replays 742884 (Devil) and 742899/742900 (3.14159265) over r30-100.
   - For each blocked split or pearl, log which gate blocked it: ESCAPE_SPLIT, PORTAL_NO_SPLIT, safety.
   - Fix length-2 HitSelf deaths (notes/19).
   - Target: at least 25 units at r100 on Devil and Trophy.
2. Allow equal-length head-on trades when we are ahead on units (cheji wins on numbers, not on individual fights).
3. A narrow eat-sprint: length 2-4, pearl on each step, each step safe, 2-3 steps, under a new flag (EAT_SPRINT2). Keep the old EAT_SPRINT.
4. 3-step rams, and 2-step rams at length 2 when the path eats a pearl, in tryRam behind a flag with ramGuard kept.
5. Reactive king on unknown maps: seed early (about r150) when we trail on units by 1.5x or more. Evidence so far is Cutlery on Portals, 3/3.
6. Sonar audit: why did emitSonar send 0 pings in 742899 and 742900? Cheap to check. Then test sharing pearl and wall info on unknown maps.
Test every change with a server A/B on Devil, Trophy, Default and QoS against the top 8, not only with local evals.
