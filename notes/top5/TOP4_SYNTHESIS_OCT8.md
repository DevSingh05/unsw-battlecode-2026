# TOP4 synthesis (8 Oct): what to do before the freeze

Written 8 Oct ~05:00 UTC (01:00 EDT). The freeze is **Fri 9 Oct 06:00 UTC (02:00 EDT)**. After it, 3-4 h of autoscrims on the
current 17 maps set the seeds. The Qualifier is a Bo7 on all-unseen maps.

Sources: TOP4_AAAH_OCT8.md, TOP4_FTM_OCT8.md, TOP4_HORSE_OCT8.md, TOP4_CUTLERY_OCT8.md, plus STATUS.md (the server scoreboard),
UNDERSTANDING.md and the running qualifier-final-push scratch (qfp/: robustness, MAPID_RESET, QUEEN_NO_EXPLORE, NO_KNOWN_MAPS remix
.471). Nothing was built, submitted or challenged for this note.

## Bottom line
- **Known-map play stays b4.** None of the four studies found a known-map change that is both decision-verified and
  server-safe. The only map-gated candidate is Schooltime B (action 3), and its nearest relative lost on the server (v1
  SCH_DOORS: 36% to 25%). Seeding risk is not worth it unless an unranked Schooltime block clears it.
- **The one cross-team, decision-verified, map-free lesson is the early queen's threat model.** Before r100 our queen does
  not see paid-step kamikaze reach, and pearls on the path extend it. horse, Cutlery and aAah all kill her this way, and FTM
  hunts the queen by id too. Ship it **gated to unknown maps only** (action 1), so the 17 maps stay byte-identical to b4.
- Everything else the top 4 do better (aAah's mid-size economy, FTM's and horse's queen crowning, king feeding efficiency) is a
  redesign. Our copies already lost on the server (MIDSIZE ms1, QK_BIG, q1, l1, QPARK_UNK, LUNGE34). Do not retry before the freeze.

## Ranked actions (max 5)

### 1. QE_KR=2 (pearl-aware early-queen kamikaze reach), unknown maps only: ship in the Qualifier build if the checks pass
- **What:** horse's scratch flag (`scratchpad/top4/horse/bot`, diff `notes/top5/new_rules_tools/QE_KR_horse8.diff`).
  - Scope: our queen, before QS_FROM, so roughly r0-99.
  - For each visible enemy head it floods the reach `F(Lv) + (Lv-2)`, plus one extra tile per pearl on the path, capped at 4. An
    unseen tail counts as Lv>=3, and bodies block.
  - Tiles it reaches get `threatAt` plus a penalty of 60.
  - New for the Qualifier: AND the trigger with the unknown-map gate.
- **Why (cross-team):**
  - horse: killed our early queen in 19 games, 13 of them our losses. 13% of their kills use pearl-extended reach (ours: 6 of 1612).
  - Cutlery: small-head early queen kills are the biggest b4 loss bucket (26 of 70 panel losses) and decided 2 of 5 losses to them.
    Our queen alive at r500 decided the result in 9 of 10 games.
  - aAah: 13 of 24 fatal queen moves were rated threat 0, because the killer lunged with paid steps from beyond our modelled reach.
  - FTM: 35 paid lunges a game; their heads kill our queen at a median r72 in 30 of 31 eliminations.
  - The same blind spot shows up in four independent corpora. It carries straight to unseen maps, because it needs no map knowledge.
- **Seeding risk:** zero if the gate is right (see "Gate caveat" below). It changes Qualifier play only.
- **Harness evidence (horse study, exact b4/kf1 zips, every base move MATCH):**
  - Losses: QE_KR=2 flips the fatal final move in **8 of 19** queen kills: Trophy ×3, Autarky, TD, Australia, Devil ×2. A ninth
    (QoS) flips 1-2 rounds earlier. Plain reach without pearls (QE_KR=1) flips only 4 of 19.
  - Wins: 34 of ~45 unchanged. 9 change 1-2 queen turns, mostly where she died by r19-81 anyway. Two change 7-10 turns.
  - Flag off: 16414/16414 actions match.
  - Corroboration: Cutlery's sibling rule (QSTALK bit 4, a 1000 penalty on threat tiles) moves the queen off the collision tile at
    the fatal move in 7 of 28 checkable small-head deaths, and changes 5 of 40 wins.
  - Caution: aAah's queen-only KREACH counterfactual changed 5 of 24 losses but also 4 of 8 wins (games where the queen died
    anyway). This is the same family as v69 (lost, leaning) and QKREACH (never server-tested). The harness shows the fatal move
    changes, **not that she survives**. That is why this ships unknown-only, not on the ladder.
- **Gate caveat (must fix before building):** the existing unknown-map gate, `!w.known && w.candidates.empty()`
  (main.cpp ~1062, UNK_KING), turns true mid-game on **server Schooltime layout B**, where the door edges drop the map by design
  (see qfp MAPID_RESET's Schooltime exemption). Gate QE_KR on a sticky "never identified" bit set at r0/birth from
  `!w.known && w.candidates.empty()`, the same rule INFER_SYM and NO_KNOWN_MAPS use. Do not gate on the live `w.known`.
  If qfp's MAPID_RESET ships, decide explicitly whether a reset look-alike counts as unknown; it should.
- **Test plan (light CPU: max 2 local games, `--jobs 2`; all commands from the project root `/Users/devsingh/Developer/UNSW_Battlecode`):**
  1. Build `qek1` = b4 + gated QE_KR=2 in the scratchpad (copy from `scratchpad/top4/horse/bot`, add the gate). Do not touch
     bot/ or variants/.
  2. Identity on known maps: sandbox seed 1000, qek1 vs b4 with the bot on both sides. Run all 17 maps plus
     `maps/schooltime_b3.map`; result-line hashes must be identical on all 18. Any difference means no ship.
  3. Unseen regression: `python3 tools/unseen_eval.py "<qek1>:" --base variants/b4 --sets real,realhold,blind17 --jobs 2`.
     The opponent is b4, which does not lunge like horse, so this catches regressions only and cannot show a gain.
     - Ship bar: pooled at least .48.
     - Also check queen alive at r100 is not lower than b4's (mechq.py-style trace on blind17).
  4. Optional, only if the server is free (check `codex-battlecode/coord/SERVER_LOCK`) and it fits before ~20:00 UTC on 8 Oct:
     - Upload the **ungated** QE_KR=2 build, unranked only, for one ~3 h block on the lane maps where the deaths are:
       Devil, Trophy, TD, Autarky, PD, QoS, Default.
     - Judge on early-queen head-on deaths per game and queen alive at r100, plus adjusted PAE per map against b4's history.
     - Attribute every game with the harness first (action 2).
     - Abort if it looks like v69 (PAE about -5 pp). Restore b4 afterwards; the identical re-upload brings its rating back.
  5. Merge into the Qualifier build that qfp is staging, as one more unknown-only flag. Finish by **9 Oct 02:00 UTC
     (8 Oct 22:00 EDT)** to leave a 4 h buffer.

### 2. Attribute every server game per game before judging any A/B this week (analysis only, no bot change)
- **What:** run `tools/decision_replay.py verify` (or aAah's `whichsub.py`) on each game before `ab_server.py`. Drop or re-label
  games that match an old zip. Mappings are already saved in `replays/top4_aaah/which_submission.json` and
  `scratchpad/top4/ftm/attr2*.json`.
- **Why:** two independent studies found games labelled with the upload window that were played by old zips. FTM: 18 games
  labelled "kf1" were v61. aAah: 11 games labelled kf1/b4 were v35 or v61, and the aAah Portals sample was never b4.
  Same-window games against other teams were clean (12 of 12 b4). The kf1 verdict (-6.0 pp) is contaminated.
- **Seeding risk:** none.
- **Harness evidence:** 100% turn matches in every reclassified game (FTM: 18; aAah: 68 classified).
- **Test plan:**
  - Required before scoring action 1's server block.
  - Re-scoring kf1 on clean games is a nice-to-have. Even if kf1 turned neutral, it is an all-maps change, so do not ship it before the freeze.

### 3. (Optional, known map) Schooltime B: SCH_DOORS=1 + SCH_CHAMBER=1. Ship only after an unranked Schooltime block
- **What:** b4 plus the two existing flags, staged at `scratchpad/top4/ftm/bot/`. They act only on Schooltime.
- **Why:** against FTM, layout B is lost through the side-room chambers:
  - FTM ate 119-147 chamber pearls; we ate 0-13. We lost 6 of 6.
  - In our only B win we ate 101 in the chambers and FTM ate 2.
  - VIB_OCT5 found the same lever on the earlier build.
- **Harness evidence:**
  - All 6 B losses change from r29-42, and the changed moves go toward the chambers.
  - The B win changes 15%.
  - Layout A and other maps: 0 of 46k and 0 of 15.6k turns changed.
  - The harness cannot score the outcome.
- **Against it:** SCH_DOORS alone lost on the server (v1: Schooltime 36% to 25%, small n). The chamber pull has never been on
  the server. The prize is at most 1/17 of seeding games, and the Qualifier never plays Schooltime.
- **Test plan:**
  - Only if a server slot is left after action 1: a 2-3 h unranked block on Schooltime only (both layouts).
  - Accept if chamber eats per B game exceed 30, B wins are at least b4's, and layout A is unchanged.
  - Otherwise keep b4. If action 1's server block hasn't run by ~18:00 UTC on 8 Oct, skip this.

### 4. Count the two new ally-caused queen self-deaths on the full b4 corpus; build nothing unless the count is large
- **What:** FTM traced two new single-case causes:
  - a candidate tile whose only exit is an adjacent ally's forced move (1373837 AUNSW r82);
  - a QALLY_KEEP gate that uses `wrapDist` and so doesn't see through portals (1278124 Slithery r17).
- **Why:**
  - Self-deaths: our queen 19 of 106 games vs FTM's 1 of 106. 12 of 16 checked are box-then-split chains.
  - aAah: 6 of 8 early self-collisions are boxed units.
  - Cutlery AUNSW 1333032: allies sealed the queen at r52.
  - A queen alive at the end is worth the tiebreak in 16 of 74 FTM losses.
  - Self-deaths do not depend on map knowledge.
- **Seeding risk:** none (counting only).
- **Harness evidence:** two decision points only. No prototype, and no flip test.
- **Test plan:**
  - Count both patterns over all b4-attributed games with qself.py / seal.py (scratchpad/top4/ftm).
  - Only if they explain at least 10% of queen self-deaths: prototype as an unknown-gated flag and run harness flips plus
    action 1 steps 2-3.
  - Realistically this is post-Qualifier work. Do not let it delay action 1.

### 5. Freeze known-map play at b4 and do nothing else to it
This is the stated default, not filler. The studies point at large, real gaps:
- aAah: r100 mass 82 vs 36 in our open-map losses;
- FTM and horse: crowned queens from r100-250;
- horse: kings stalked from just outside 7x7 vision.

Every cheap form of these already lost on the server, or is single-case and unverified:
- MIDSIZE ms1;
- QK_BIG / q1 / l1 / QPARK_UNK;
- LUNGE34;
- k2/pb2 for the Portals coil;
- Slithery QVAULT alone (v1);
- the weakhold queen corridor (no counterfactual found);
- PM_POR_EARLY (failed locally);
- king "recently seen head" memory (1 case).

Keep b4 live, use the ranked loop only on b4, and re-upload identical b4 after any test block, so that the
final active submission before 06:00 UTC on 9 Oct is b4 plus unknown-only flags (the qfp build + QE_KR).

## Not actions, but expect these in the Qualifier
- **Against aAah:** we lose open maps by r100 on mass, and win lane and small maps (TD 4/4, Trophy 2/2, Devil 2/2, Trauma 2/2).
  Most of the Bo7 depends on the map mix.
- **Against Cutlery:** their queen is dead in 70% of games and their longest at r400 is 15-23. Every game in which our queen
  lives to r500 should be ours, which is action 1's target.
- **Against FTM:** small-map early eliminations are their win path. Teams that beat FTM do it with early small-map aggression;
  we don't have a verified version of that.
- **Against horse:** lane-map early queen kills, then elimination. That is also action 1's target.

## Timeline (UTC / EDT)
| when | step |
|---|---|
| 8 Oct 05:00-09:00 UTC (01:00-05:00 EDT) | Build qek1 with the sticky gate. Run the 18-map identity check, then unseen_eval at `--jobs 2`. Attribute games (action 2). |
| 8 Oct 09:00-17:00 UTC (05:00-13:00 EDT) | Optional: ungated server block on the lane maps (one build live at a time; check SERVER_LOCK). Then restore b4. |
| 8 Oct 17:00-20:00 UTC (13:00-16:00 EDT) | Decide QE_KR. Schooltime block only if a slot is left. |
| by 9 Oct 02:00 UTC (8 Oct 22:00 EDT) | Final Qualifier build = b4 + qfp unknown-only flags + QE_KR (if passed). Run the identity check on 17 maps plus Schooltime B again, then upload. |
| 9 Oct 06:00 UTC (02:00 EDT) | Freeze. |
