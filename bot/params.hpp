#pragma once
// Tunable strategy knobs. Variants for local testing override these.

// Split once a dragon reaches this length (child takes half).
#ifndef SPLIT_LEN
#define SPLIT_LEN 4
#endif
// Stop splitting after this round.
#ifndef SPLIT_STOP_ROUND
#define SPLIT_STOP_ROUND 350
#endif
// Stop splitting once the team has this many dragons.
#ifndef SPLIT_MAX_UNITS
#define SPLIT_MAX_UNITS 64
#endif
// Discount per step for pearl value when path planning.
#ifndef PEARL_GAMMA
#define PEARL_GAMMA 0.82
#endif
// Ram enemy heads when the trade looks favourable.
#ifndef ENABLE_RAM
#define ENABLE_RAM 1
#endif
// Emit INDICATOR text (debug only; costs a few points).
#ifndef DEBUG_INDICATOR
#define DEBUG_INDICATOR 0
#endif
// Count only tiles we reach before any other head when judging room.
#ifndef VORONOI_AREA
#define VORONOI_AREA 1
#endif
// Don't path through tiles another head reaches first.
#ifndef VORONOI_BLOCK
#define VORONOI_BLOCK 0
#endif
// Segments assumed behind a tail we cannot see.
#ifndef UNKNOWN_TAIL_EXTRA
#define UNKNOWN_TAIL_EXTRA 1000000
#endif
// Look-ahead depth for the survival search.
#ifndef SURVIVE_DEPTH
#define SURVIVE_DEPTH 12
#endif
#ifndef AREA_WEIGHT
#define AREA_WEIGHT 60.0
#endif
// Child size when splitting (0 = half).
#ifndef SPLIT_CHILD
#define SPLIT_CHILD 2
#endif
// Our dragons up to this length ram any enemy head in reach.
#ifndef RAM_MAX_OWN_LEN
#define RAM_MAX_OWN_LEN 3
#endif
// How far (steps) we assume an enemy head can sprint to ram us.
#ifndef MAX_THREAT_REACH
#define MAX_THREAT_REACH 1
#endif
// ---- endgame: grow one king, feed it with small dragons
#ifndef FEED_ENABLE
#define FEED_ENABLE 1
#endif
#ifndef KING_MIN_LEN
#define KING_MIN_LEN 8
#endif
#ifndef KING_THREAT_REACH
#define KING_THREAT_REACH 4
#endif
#ifndef KING_BROADCAST_START
#define KING_BROADCAST_START 250
#endif
#ifndef KING_RELAY_HOPS
#define KING_RELAY_HOPS 3
#endif
#ifndef FEED_START
#define FEED_START 330
#endif
#ifndef FEED_AHEAD
#define FEED_AHEAD 2
#endif
#ifndef FEED_DIST
#define FEED_DIST 4
#endif
#ifndef FEED_RESERVE
#define FEED_RESERVE 4
#endif
#ifndef FEED_PULL
#define FEED_PULL 3.0
#endif
// Testing only: pretend no maps are known (as on a brand new map).
#ifndef NO_KNOWN_MAPS
#define NO_KNOWN_MAPS 0
#endif
// Penalty for walking through a portal onto a tile outside our view.
#ifndef PORTAL_BLIND_PENALTY
#define PORTAL_BLIND_PENALTY 0.0
#endif
// Penalty for stepping onto a tile others can portal onto blind.
#ifndef PORTAL_EXIT_PENALTY
#define PORTAL_EXIT_PENALTY 0.0
#endif
// Don't split while standing on a portal exit.
#ifndef PORTAL_NO_SPLIT
#define PORTAL_NO_SPLIT 0
#endif
// ---- declared king: grow one dragon from mid-game instead of waiting for length 8
#ifndef KING_DECLARE
#define KING_DECLARE 0
#endif
#ifndef KING_SEED_ROUND
#define KING_SEED_ROUND 250
#endif
#ifndef KING_DECLARE_P
#define KING_DECLARE_P 0.02
#endif
// Warn allies through a portal when standing on its exit.
#ifndef PORTAL_WARN
#define PORTAL_WARN 1
#endif
// How long a warned portal exit counts as blocked (2 = only for our next step).
#ifndef WARN_FREE_T
#define WARN_FREE_T 2
#endif
// Survival search counts pearls it would eat (tail stays put when eating).
#ifndef DFS_EATS
#define DFS_EATS 1
#endif
// Small dragons may enter dead ends if they'll grow to 4 and can split out.
#ifndef ESCAPE_SPLIT
#define ESCAPE_SPLIT 1
#endif
// Only make even-trade rams when we have the numbers.
#ifndef RAM_GUARD
#define RAM_GUARD 1
#endif
#ifndef RAM_MIN_UNITS
#define RAM_MIN_UNITS 8
#endif
// Only split when the child (our tail end) has a free tile to move to.
#ifndef SPLIT_NEEDS_EXIT
#define SPLIT_NEEDS_EXIT 0
#endif

// ---- per-map overrides (-1 = use the global default above)
#ifndef PM_DEVIL_RG
#define PM_DEVIL_RG 0
#endif
#ifndef PM_DEVIL_KD
#define PM_DEVIL_KD -1
#endif
#ifndef PM_DEVIL_KS
#define PM_DEVIL_KS -1
#endif
#ifndef PM_DEVIL_SS
#define PM_DEVIL_SS -1
#endif
#ifndef PM_DEVIL_FS
#define PM_DEVIL_FS -1
#endif
#ifndef PM_TROPHY_RG
#define PM_TROPHY_RG 0
#endif
#ifndef PM_TROPHY_KD
#define PM_TROPHY_KD -1
#endif
#ifndef PM_TROPHY_KS
#define PM_TROPHY_KS -1
#endif
#ifndef PM_TROPHY_SS
#define PM_TROPHY_SS -1
#endif
#ifndef PM_TROPHY_FS
#define PM_TROPHY_FS -1
#endif
#ifndef PM_QOS_RG
#define PM_QOS_RG -1
#endif
#ifndef PM_QOS_KD
#define PM_QOS_KD -1
#endif
#ifndef PM_QOS_KS
#define PM_QOS_KS -1
#endif
#ifndef PM_QOS_SS
#define PM_QOS_SS -1
#endif
#ifndef PM_QOS_FS
#define PM_QOS_FS -1
#endif
#ifndef PM_DIL_RG
#define PM_DIL_RG -1
#endif
#ifndef PM_DIL_KD
#define PM_DIL_KD 1
#endif
#ifndef PM_DIL_KS
#define PM_DIL_KS 350
#endif
#ifndef PM_DIL_SS
#define PM_DIL_SS -1
#endif
#ifndef PM_DIL_FS
#define PM_DIL_FS -1
#endif
#ifndef PM_DEF_RG
#define PM_DEF_RG -1
#endif
#ifndef PM_DEF_KD
#define PM_DEF_KD 1
#endif
#ifndef PM_DEF_KS
#define PM_DEF_KS 350
#endif
#ifndef PM_DEF_SS
#define PM_DEF_SS -1
#endif
#ifndef PM_DEF_FS
#define PM_DEF_FS -1
#endif
#ifndef PM_AUT_RG
#define PM_AUT_RG -1
#endif
#ifndef PM_AUT_KD
#define PM_AUT_KD 1
#endif
#ifndef PM_AUT_KS
#define PM_AUT_KS 380
#endif
#ifndef PM_AUT_SS
#define PM_AUT_SS -1
#endif
#ifndef PM_AUT_FS
#define PM_AUT_FS -1
#endif
#ifndef PM_SCH_RG
#define PM_SCH_RG -1
#endif
#ifndef PM_SCH_KD
#define PM_SCH_KD 1
#endif
#ifndef PM_SCH_KS
#define PM_SCH_KS 150
#endif
#ifndef PM_SCH_SS
#define PM_SCH_SS -1
#endif
#ifndef PM_SCH_FS
#define PM_SCH_FS -1
#endif
#ifndef PM_SLI_RG
#define PM_SLI_RG -1
#endif
#ifndef PM_SLI_KD
#define PM_SLI_KD 1
#endif
#ifndef PM_SLI_KS
#define PM_SLI_KS 250
#endif
#ifndef PM_SLI_SS
#define PM_SLI_SS -1
#endif
#ifndef PM_SLI_FS
#define PM_SLI_FS -1
#endif
#ifndef PM_TRA_RG
#define PM_TRA_RG -1
#endif
#ifndef PM_TRA_KD
#define PM_TRA_KD 1
#endif
#ifndef PM_TRA_KS
#define PM_TRA_KS 450
#endif
#ifndef PM_TRA_SS
#define PM_TRA_SS -1
#endif
#ifndef PM_TRA_FS
#define PM_TRA_FS -1
#endif
#ifndef PM_POR_RG
#define PM_POR_RG -1
#endif
#ifndef PM_POR_KD
#define PM_POR_KD 1
#endif
#ifndef PM_POR_KS
#define PM_POR_KS 330
#endif
#ifndef PM_POR_SS
#define PM_POR_SS -1
#endif
#ifndef PM_POR_FS
#define PM_POR_FS -1
#endif
// Only dragons this short sacrifice themselves to feed the king.
#ifndef FEED_MAX_LEN
#define FEED_MAX_LEN 1000
#endif
// Long dragons look further ahead (up to this many moves).
#ifndef KING_SURVIVE_DEPTH
#define KING_SURVIVE_DEPTH 12
#endif
// Extra penalty for a long dragon (10+) stepping blind through a portal.
#ifndef KING_PORTAL_PENALTY
#define KING_PORTAL_PENALTY 100.0
#endif
// Penalty per teammate head within 2 tiles of where we'd move (spread the swarm).
#ifndef CROWD_PENALTY
#define CROWD_PENALTY 0.0
#endif
#ifndef PM_QOS_CR
#define PM_QOS_CR 3.0
#endif
#ifndef PM_POR_CR
#define PM_POR_CR 3.0
#endif
#ifndef PM_TRA_CR
#define PM_TRA_CR 3.0
#endif
#ifndef PM_SCH_CR
#define PM_SCH_CR 3.0
#endif
#ifndef PM_DEF_CR
#define PM_DEF_CR -1.0
#endif
#ifndef PM_SLI_CR
#define PM_SLI_CR -1.0
#endif
// ---- 27 Sep afternoon (notes/10)
#ifndef KEEP_LEN
#define KEEP_LEN 0
#endif
#ifndef PM_DIL_KEEP
#define PM_DIL_KEEP -1
#endif
#ifndef ESCAPE_HOT_ONLY
#define ESCAPE_HOT_ONLY 0
#endif
#ifndef KING_DECLARE_MINLEN
#define KING_DECLARE_MINLEN 3
#endif
#ifndef KING_STEPDOWN_MARGIN
#define KING_STEPDOWN_MARGIN 2
#endif
#ifndef LATE_FEED_ROUND
#define LATE_FEED_ROUND 0
#endif
#ifndef PM_TRA_LATEFEED
#define PM_TRA_LATEFEED -1
#endif
#ifndef KING_RAM_AVOID
#define KING_RAM_AVOID 0.0
#endif
// ---- king rework from notes/11 (two candidates, per-map timing, spaced feeding)
#ifndef KING_V2
#define KING_V2 1
#endif
#ifndef KING_V2_MERGE_ROUND
#define KING_V2_MERGE_ROUND 420
#endif
#ifndef KING_V2_FEED_LEN
#define KING_V2_FEED_LEN 3
#endif
#ifndef KING_V2_LOOSE
#define KING_V2_LOOSE 1
#endif
#ifndef KING_V2_RES_BIG
#define KING_V2_RES_BIG 4
#endif
#ifndef PM_SCH_KPORTAL
#define PM_SCH_KPORTAL 100.0
#endif
#ifndef PM_SCH_KKEEP
#define PM_SCH_KKEEP 1
#endif
// Tiles next to the tail of a splittable enemy (length 4+) count as ram threats.
#ifndef TAIL_THREAT
#define TAIL_THREAT 2
#endif
// With this few dragons left, a ram can eliminate us: weigh threats much more.
#ifndef LAST_FEW_UNITS
#define LAST_FEW_UNITS 3
#endif
#ifndef LAST_FEW_MULT
#define LAST_FEW_MULT 4.0
#endif
// Penalty for a big dragon (10+) stepping onto a corridor tile (<=2 open sides).
#ifndef KING_CORRIDOR_PENALTY
#define KING_CORRIDOR_PENALTY 0.0
#endif
// ---- unknown-map learning
#ifndef LEARN_PORTALS
#define LEARN_PORTALS 0
#endif
#ifndef LEARN_GAPS
#define LEARN_GAPS 0
#endif
// Unknown maps: step through an unknown portal rather than die for certain.
#ifndef UNK_PORTAL_ESCAPE
#define UNK_PORTAL_ESCAPE 1
#endif
// Unknown maps: extra penalty for crossing a (learned) portal onto a tile we can't see.
#ifndef UNK_BLIND_PEN
#define UNK_BLIND_PEN 0.0
#endif
// Stop trusting built-in pearl gaps when visible countdowns contradict them
// (the server runs pearl-layout variants of the same walls).
#ifndef PEARL_DISTRUST
#define PEARL_DISTRUST 0
#endif
#ifndef PEARL_DISTRUST_MIN
#define PEARL_DISTRUST_MIN 3
#endif
// Assumed spawn rate for unseen tiles once built-in pearl data is distrusted.
#ifndef DISTRUST_PRIOR
#define DISTRUST_PRIOR 0.01
#endif
// ---- unseen maps
// Assumed spawn rate for a tile we've never seen on an unknown map.
#ifndef UNK_PRIOR
#define UNK_PRIOR 0.001
#endif
// On unknown maps, choose king timing by board size.
#ifndef UNK_SIZE_PARAMS
#define UNK_SIZE_PARAMS 0
#endif
#ifndef UNK_BIG_TILES
#define UNK_BIG_TILES 1000
#endif
#ifndef UNK_KS
#define UNK_KS 250
#endif
#ifndef UNK_SS
#define UNK_SS 360
#endif
#ifndef UNK_FS
#define UNK_FS 300
#endif
// Unknown maps: infer the map's symmetry from seen walls and mirror what we learn.
#ifndef INFER_SYM
#define INFER_SYM 0
#endif
// Matching non-open edges needed before trusting a symmetry.
#ifndef INFER_SYM_MIN
#define INFER_SYM_MIN 4
#endif
// Sprint along pearls that an enemy head could reach first.
#ifndef EAT_SPRINT
#define EAT_SPRINT 0
#endif
#ifndef EAT_SPRINT_MAX
#define EAT_SPRINT_MAX 3
#endif
// A pearl counts as contested if an enemy head is within this many tiles.
#ifndef EAT_SPRINT_CONTEST
#define EAT_SPRINT_CONTEST 3
#endif
#ifndef EAT_SPRINT_STRICT
#define EAT_SPRINT_STRICT 0
#endif
// Penalty for a small dragon (<6) moving where an enemy head could reach it.
#ifndef SMALL_THREAT_PEN
#define SMALL_THREAT_PEN 12.0
#endif
// ---- pocket pumping (notes/14): dive into pearl dead ends, split out at the tip
#ifndef POCKET_PUMP
#define POCKET_PUMP 1
#endif
#ifndef POCKET_PUMP_HOT
#define POCKET_PUMP_HOT 0
#endif
#ifndef POCKET_PUMP_BONUS
#define POCKET_PUMP_BONUS 3.0
#endif
#ifndef POCKET_MAX_ALLIES
#define POCKET_MAX_ALLIES 1
#endif
// Tiles with max gap at most this count as fast-respawning pocket food.
#ifndef POCKET_FAST_GAP
#define POCKET_FAST_GAP 10
#endif
#ifndef POCKET_OBSERVED
#define POCKET_OBSERVED 1
#endif
// Expected length at the tip needed to dive (4 = can split out).
#ifndef POCKET_NEED
#define POCKET_NEED 4.0
#endif
// Unseen maps: require evidence of fast pearls in a pocket before diving.
#ifndef POCKET_UNK_NEEDS_HOT
#define POCKET_UNK_NEEDS_HOT 1
#endif
// ---- ally-scaled blind portal cost (notes/14)
#ifndef PORTAL_ALLY_COST
#define PORTAL_ALLY_COST 0
#endif
#ifndef PORTAL_COST_A
#define PORTAL_COST_A 2.0
#endif
#ifndef PORTAL_COST_B
#define PORTAL_COST_B 6.0
#endif
#ifndef PORTAL_COST_C
#define PORTAL_COST_C 10.0
#endif
// ---- start-layout swap (notes/15): the server swaps which team starts where in ~half
// of games. 1: identify our side by start POSITION (not team letter), share it with
// split children through the sonar checksum, and let map modules use it.
#ifndef FRAME_FIX
#define FRAME_FIX 1
#endif
// ---- newborn neck guard (notes/15): a child born with its neck across a portal can't
// see it and stepped back into it (9/game on Default, 60/game on Portals).
#ifndef NEWBORN_NECK_GUARD
#define NEWBORN_NECK_GUARD 1
#endif
// ---- portal warnings remembered for the sender's length (notes/16): 80% of our
// crossing deaths into an ally body hit an ally that had just left the exit.
#ifndef PORTAL_WARN_MEMO
#define PORTAL_WARN_MEMO 1
#endif
// ---- trapped split with the tail out of view (game 517220 r398: a L10 child traded
// itself for an enemy L2 head instead of splitting).
#ifndef TRAP_SPLIT_BLIND
#define TRAP_SPLIT_BLIND 1
#endif
// Portals: king portal penalty override (negative = keep the global KING_PORTAL_PENALTY)
#ifndef PM_POR_KPORTAL
#define PM_POR_KPORTAL 0.0
#endif
// ---- portal echo guard (notes/17): our warn ray from a mouth tile probes the exit for
// free; 1 = an echoed head blocks the exit next turn, 2 = also echoed bodies when the
// ray's path past the exit ends on kelp within PORTAL_ECHO_RANGE tiles.
#ifndef PORTAL_ECHO_GUARD
#define PORTAL_ECHO_GUARD 2
#endif
#ifndef PORTAL_ECHO_RANGE
#define PORTAL_ECHO_RANGE 3
#endif
// keep a remembered warning this many extra rounds (off-by-one for lower-id crossers)
#ifndef PORTAL_WARN_MEMO_SLACK
#define PORTAL_WARN_MEMO_SLACK 1
#endif
// ---- feed only a king heard from within this many rounds (0 = off)
#ifndef FEED_FRESH
#define FEED_FRESH 0
#endif
// ---- late splitting (notes/15 #2, notes/16 #3): top teams keep doing 4->2+2 splits
// until ~r450; small dragons (len <= LATE_SPLIT_MAXLEN) keep splitting until this round (0 = off)
#ifndef LATE_SPLIT_ROUND
#define LATE_SPLIT_ROUND 450
#endif
#ifndef LATE_SPLIT_MAXLEN
#define LATE_SPLIT_MAXLEN 5
#endif
// ---- big-dragon escape when every 1-step move is threatened (notes/18)
#ifndef KING_ESCAPE
#define KING_ESCAPE 1
#endif
#ifndef ESC_SPRINT_COST
#define ESC_SPRINT_COST 15.0
#endif
// ---- enemy with its tail out of view: assume at least this reach vs our big dragons (0 = off)
#ifndef THREAT_TAIL_UNKNOWN
#define THREAT_TAIL_UNKNOWN 2
#endif
// ---- Schooltime-style long exits (notes/20): a body echo past the exit makes a crossing
// risky (~18% fatal) but the guard only blocks short exits; penalise instead (0 = off)
#ifndef PORTAL_ECHO_BODY_PEN
#define PORTAL_ECHO_BODY_PEN 30.0
#endif
// skip king/relay broadcasts on turns we probe a portal, so the body echo count is usable
#ifndef PORTAL_PROBE_SOLO
#define PORTAL_PROBE_SOLO 1
#endif

// ---- notes/19 (Devil / Prisoners Dilemma diagnosis)
// Ram guard that only asks for LOCAL odds (allies in view >= enemies in view, target included),
// not RAM_MIN_UNITS. 1 = Devil + Prisoners Dilemma, 2 = every map that uses the guard or has it off.
#ifndef RAM_GUARD_LOCAL
#define RAM_GUARD_LOCAL 1
#endif
// Small dragons (<6) that are not locally ahead: stronger 1-step threat penalty and a penalty for
// tiles an enemy (len>=3) can reach with a 2-step sprint (half of the rams we suffer on PD).
#ifndef SMALL_SPRINT_THREAT
#define SMALL_SPRINT_THREAT 0
#endif
#ifndef SMALL_THREAT_PEN_OUT
#define SMALL_THREAT_PEN_OUT 30.0
#endif
#ifndef SMALL_SPRINT_PEN
#define SMALL_SPRINT_PEN 10.0
#endif
// Pocket pump: don't split 2 off while a pearl in the dead end is next to us; at the tip give the
// child L-2 (a 2-long head dies there instead of a 3-long one).
#ifndef PUMP_TIP_SPLIT
#define PUMP_TIP_SPLIT 0
#endif
// ---- unseen maps (notes/unseen/PLAN.md)
// Q2: declare kings + feed on unknown maps; seed/feed rounds; reserve schedule; crown early when full
#ifndef UNK_KING
#define UNK_KING 0
#endif
#ifndef UNK_KING_SEED
#define UNK_KING_SEED 250
#endif
#ifndef UNK_KING_FEED
#define UNK_KING_FEED 300
#endif
// one feeder at a time, within 3 of the king, never onto uneaten food
#ifndef FEED_QUEUE
#define FEED_QUEUE 0
#endif
// Q7: unknown boards with N <= 750 use the local-odds ram guard
#ifndef UNK_SMALL_RAMGUARD
#define UNK_SMALL_RAMGUARD 0
#endif
// ---- route-based food valuation (Codex): 1 = all maps, 2 = unknown maps only
#ifndef PEARL_ROUTE
#define PEARL_ROUTE 2
#endif
#ifndef PEARL_ROUTE_SCALE
#define PEARL_ROUTE_SCALE 2.0
#endif
#ifndef PEARL_ROUTE_REGION
#define PEARL_ROUTE_REGION 0.15
#endif
// ---- king-escape sprint: occupancy tested before each step moves the tail (found by Codex)
#ifndef KING_ESCAPE_TAIL_FIX
#define KING_ESCAPE_TAIL_FIX 1
#endif
// ---- Q5: learn hot (every-round) pearl tiles on unknown maps from observed countdowns
#ifndef HOT_LEARN
#define HOT_LEARN 0
#endif
// ---- Q4 unknown-portal exploration: knock (sonar) on unknown portals, cross only on a clean
// echo and when the region is scouted/hungry; learned links kept out of w.nxt
#ifndef UNK_EXPLORE
#define UNK_EXPLORE 1
#endif
#ifndef UNK_EXPLORE_HUNGER
#define UNK_EXPLORE_HUNGER 100000
#endif
#ifndef UNK_EXPLORE_HUNGER_CLOSED
#define UNK_EXPLORE_HUNGER_CLOSED 3
#endif
#ifndef UNK_EXPLORE_COOLDOWN
#define UNK_EXPLORE_COOLDOWN 8
#endif
#ifndef UNK_EXPLORE_LURE
#define UNK_EXPLORE_LURE 0.4
#endif
#ifndef UNK_EXPLORE_SCORE
#define UNK_EXPLORE_SCORE 15.0
#endif
// explore only when our portal-free region is below this fraction of the board (sealed in)
#ifndef UNK_EXPLORE_REGION_FRAC
#define UNK_EXPLORE_REGION_FRAC 0.7
#endif
#ifndef UNK_EXPLORE_BFS_CAP
#define UNK_EXPLORE_BFS_CAP 4096
#endif
// UNK_EXPLORE=2: explore (scouted or hungry) only when our portal-free region < this share of the board
#ifndef UNK_EXPLORE_SEALED_FRAC
#define UNK_EXPLORE_SEALED_FRAC 0.85
#endif
// ---- Q3: pearl/area ties go to us (sequential turn order)
#ifndef TURN_ORDER_TIES
#define TURN_ORDER_TIES 0
#endif
