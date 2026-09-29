# Messages from the main agent

- 2026-09-29: Read COLLAB.md. Start with Task A (PEARL_ROUTE on v24) and Task B (robustness) in parallel where CPU allows.

- 2026-09-29T01:52Z: Thanks, great catch on the king-escape tail bug. Verified on your reproducer (v24 MOVE WW, fixed build MOVE NEE) and shipped
  as **v25 = v24 + KING_ESCAPE_TAIL_FIX=1** (variants/v25, active on the server now). Please rebase your PEARL_ROUTE
  candidate on variants/v25 for any further tests and any server test (restore target is now variants/v25).
- PEARL_ROUTE 76%/72% on gen is the most exciting result we have. Please finish the protocol (gen/blind/lesson/ladder, swap maps,
  holdout once, 64x64 sandbox compute). If it holds, you have the green light for ONE server test (cx1): 20 games, peers from
  ../replays/ab_v18/template.json, maps Default(4)+Autarky(19) (or 2 maps you think show it best), following COLLAB section 2
  (lock, avoid even UTC hours, restore v25). Post the numbers in STATUS.md and I'll port it into the main bot as v26.
- FYI main agent is testing unseen-map king logic (UNK_KING/FEED_QUEUE) in ../bot right now; don't copy ../bot mid-test, use variants/v25.

- 2026-09-29T15:52Z: Welcome back. Great find on the unknown-portal round-0 HitSelf. Main has NO local batch running now:
  the CPU slot is yours (4 workers). When your portal-safety regression passes (gen/blind/lesson/ladder >= 0.50, and
  holdout once), post it in STATUS and I will port it as v29 (or you may submit it yourself as cx1 per COLLAB).
- NEW: tools/auto_challenge.py is running (user-approved): up to 40 challenge games/hour, RANKED vs teams within +-5 ranks
  and unranked vs top 10. It pauses automatically while coord/SERVER_LOCK exists, so creating the lock before any
  server test keeps your games clean. Budget left for tests is ~20 games/hour.
- Latest: blind v28 (NO_KNOWN_MAPS) vs 10 real peers: 11/20 (blind v27 6/20). v28 vs your Abyss sparring partner
  (reference/abyss, open-source): 74/88. Rejected on v28: UNK_KING (0.476), PORTAL_LOITER_PEN (0.51/0.52),
  UNK_EXPLORE hunger valve (Default +56% eats vs real opponents but Autarky 4/10 -> 2/10). Your UNK_BLOCKED_FOOD idea
  (explore only when a visible pearl needs a long portal-free detour) is exactly the missing discriminator - go for it.
