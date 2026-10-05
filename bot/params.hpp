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
#define KING_V2_MERGE_ROUND 380
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
#define INFER_SYM 1 // on since 2026-10-04: unknown maps only; .548 blind in two separate runs (REAL_SWEEP + qual)
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
#define UNK_KING 1
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
#define UNK_SMALL_RAMGUARD 1
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
#define UNK_EXPLORE_BFS_CAP 2000
#endif
// UNK_EXPLORE=2: explore (scouted or hungry) only when our portal-free region < this share of the board
#ifndef UNK_EXPLORE_SEALED_FRAC
#define UNK_EXPLORE_SEALED_FRAC 0.85
#endif
// ---- Q3: pearl/area ties go to us (sequential turn order)
#ifndef TURN_ORDER_TIES
#define TURN_ORDER_TIES 0
#endif
// ---- penalty for moving from one portal mouth tile to another without crossing (Abyss idea)
#ifndef PORTAL_LOITER_PEN
#define PORTAL_LOITER_PEN 0.0
#endif
// ---- Codex (notes: codex-battlecode/notes/portal-safety-v28.diff): record unknown portal edges
// on both sides; in the all-lethal fallback never take the unknown portal behind our head
#ifndef UNK_PORTAL_SIDES
#define UNK_PORTAL_SIDES 0
#endif
#ifndef UNK_NECK_ESCAPE_GUARD
#define UNK_NECK_ESCAPE_GUARD 1
#endif
// ---- notes/22: when sizing a pump split, a neighbour that is itself a 1-2 tile dead end is not an exit
#ifndef PUMP_TIP_DEADEND
#define PUMP_TIP_DEADEND 0
#endif
// ---- notes/22 F2: small dragons are drawn to entrances of fast-refilling dead-end pockets
#ifndef HOT_PULL
#define HOT_PULL 0.0
#endif
#ifndef HOT_PULL_RANGE
#define HOT_PULL_RANGE 14
#endif
// ---- notes/21: king fragmentation and stale-king feed suicides
#ifndef KING_FOCUS
#define KING_FOCUS 0
#endif
#ifndef KING_FOCUS_GAP
#define KING_FOCUS_GAP 6
#endif
#ifndef FEED_STALE_GUARD
#define FEED_STALE_GUARD 0
#endif
// ---- notes/forensics (Slithery RC1/RC2, Schooltime A1): one king per team.
// kingId = the LONGEST king heard in KC_MEM rounds (relay it); a crowned dragon steps down when ONE king
// >= myLen+max(3,myLen/4) was heard in KC_STEP_MEM rounds; no self-crown while a king >= myLen+2 is known;
// feed only a king >= KC_FEED_FRAC of the longest heard in KC_FEED_MEM rounds.
#ifndef KING_CONSENSUS
#define KING_CONSENSUS 1
#endif
#ifndef KC_MEM
#define KC_MEM 12
#endif
#ifndef KC_STEP_MEM
#define KC_STEP_MEM 30
#endif
#ifndef KC_FEED_MEM
#define KC_FEED_MEM 40
#endif
#ifndef KC_FEED_FRAC
#define KC_FEED_FRAC 0.75
#endif
// ---- notes/levers/blocked-food.md: on unknown maps, open the UNK_EXPLORE gate (knock, cross on a
// clean echo) when seen pearl spawners are provably unreachable without a portal.
// 1 = strict (outside our portal-free component), 2 = also long nearby detours
#ifndef UNK_SEALED_FOOD
#define UNK_SEALED_FOOD 0
#endif
#ifndef UNK_SEALED_HUNGER
#define UNK_SEALED_HUNGER 20
#endif
#ifndef UNK_SEALED_MIN
#define UNK_SEALED_MIN 4
#endif
#ifndef UNK_SEALED_FRAC
#define UNK_SEALED_FRAC 0.2
#endif
#ifndef UNK_SEALED_DETOUR_NEAR
#define UNK_SEALED_DETOUR_NEAR 6
#endif
#ifndef UNK_SEALED_DETOUR
#define UNK_SEALED_DETOUR 8
#endif
#ifndef UNK_SEALED_LOG
#define UNK_SEALED_LOG 0
#endif
// sealed food per tile must be at least this multiple of the walkable food's rate
#ifndef UNK_SEALED_RICH
#define UNK_SEALED_RICH 1.0
#endif
// rounds after an explore crossing during which no explore desire (either gate) fires
#ifndef UNK_SEALED_SETTLE
#define UNK_SEALED_SETTLE 15
#endif
// no split while our portal-free room is smaller than this; a small room this crowded
// (other segments >= 1/4 of its tiles) opens the explore gate at once
#ifndef UNK_SEALED_ROOM_MIN
#define UNK_SEALED_ROOM_MIN 32
#endif
// ---- notes/levers/frontier-explore.md: learned value of never-seen tiles (unknown maps only).
// Every tile entering our view for the first time is a free sample of "what an unseen tile
// holds". EXPLORE_LEARN replaces the time-growing UNK_PRIOR guess 0.5*min(1, r*UNK_PRIOR)
// for never-seen tiles with a smoothed first-sight hit rate (pearl there, or a countdown
// <= EXPLORE_CD). 0 off, 1 on.
#ifndef EXPLORE_LEARN
#define EXPLORE_LEARN 0
#endif
#ifndef EXPLORE_M0 // prior mean hit rate (Beta pseudo-count mean) before any samples
#define EXPLORE_M0 0.03
#endif
#ifndef EXPLORE_N0 // prior weight in samples (~7 new tiles per straight step)
#define EXPLORE_N0 30.0
#endif
#ifndef EXPLORE_DECAY // per-turn forgetting of old samples (window ~ 7/(1-d) samples)
#define EXPLORE_DECAY 0.98
#endif
#ifndef EXPLORE_CD // a first-seen countdown <= this counts as food (we arrive ~3 steps after sight)
#define EXPLORE_CD 3
#endif
#ifndef EXPLORE_MULT // scale on the estimate
#define EXPLORE_MULT 1.0
#endif
#ifndef EXPLORE_MAX
#define EXPLORE_MAX 0.5
#endif
// ---- notes/levers/budget-lookahead.md: spend spare CPU on a 1-ply enemy-reply check for big dragons
// REPLY_SEARCH: for L >= REPLY_MIN_LEN, each candidate step is re-checked against every joint 1-step
// reply of the (up to REPLY_MAX_ENEMIES) nearest enemy heads within REPLY_RADIUS: the reply tiles are
// blocked, our next step may not enter a tile the replied heads can reach, and surviveDepth is re-run.
// A reply that leaves no safe next step ("forced": every next step threatened or lethal) costs
// REPLY_FORCED_PEN + REPLY_FORCED_PER_LEN*L; a shortfall in survival depth costs REPLY_SHORT_PEN per step.
#ifndef REPLY_SEARCH
#define REPLY_SEARCH 0
#endif
#ifndef REPLY_MIN_LEN
#define REPLY_MIN_LEN 8
#endif
#ifndef REPLY_RADIUS
#define REPLY_RADIUS 3
#endif
#ifndef REPLY_MAX_ENEMIES
#define REPLY_MAX_ENEMIES 3
#endif
#ifndef REPLY_NODE_CAP
#define REPLY_NODE_CAP 6000
#endif
#ifndef REPLY_FORCED_PEN
#define REPLY_FORCED_PEN 40.0
#endif
#ifndef REPLY_FORCED_PER_LEN
#define REPLY_FORCED_PER_LEN 3.0
#endif
#ifndef REPLY_SHORT_PEN
#define REPLY_SHORT_PEN 12.0
#endif
// The reply penalty is capped at this fraction of the direct-threat penalty (25+4L) so a forced-next-turn
// tile is never ranked below a tile an enemy head can ram right now.
#ifndef REPLY_CAP_FRAC
#define REPLY_CAP_FRAC 0.8
#endif
// Stop starting new reply checks once this many points (sandbox clock, 1e6 points = 1 ms) have been
// spent this turn; the rest of the candidates keep their plain score. Keeps worst case far below 100M.
#ifndef REPLY_BUDGET_M
#define REPLY_BUDGET_M 45
#endif
// PROFILE_POINTS: append a LOG line with per-section points (sandbox clock) each turn. Local only.
#ifndef PROFILE_POINTS
#define PROFILE_POINTS 0
#endif
// ---- notes/23 M1: required flood area (tiles) for each half after a growth split; 0 = off
#ifndef SPLIT_VIABLE
#define SPLIT_VIABLE 0
#endif
// extra area required when units >= 3/4 of the unit limit
#ifndef SPLIT_VIABLE_DENSE
#define SPLIT_VIABLE_DENSE 0
#endif

// ---- notes/autarky_calc/PLAN.md (Autarky vs calc): pocket treadmill fixes, all general (local geometry)
// PUMP_TIP2: inside a static 1-wide dead end (kelp flood ahead of the head, not via the neck, <= REGION
// tiles), L4..MAXLEN keeps eating toward a pearl/every-round tile instead of the normal SPLIT 2 one tile
// early, and with nothing left ahead splits k=L-2 so the child (tail end, at/outside the mouth) takes the bulk.
#ifndef PUMP_TIP2
#define PUMP_TIP2 0
#endif
#ifndef PUMP_TIP2_REGION
#define PUMP_TIP2_REGION 6
#endif
#ifndef PUMP_TIP2_MAXLEN
#define PUMP_TIP2_MAXLEN 7
#endif
// POCKET_ENEMY_LOCAL: 0 = old veto (any enemy head within 3 of the entry tile); 1 = veto only an enemy head
// within 1 of the entry tile; 2 = also when enemy heads within 3 outnumber ours (me included)
#ifndef POCKET_ENEMY_LOCAL
#define POCKET_ENEMY_LOCAL 0
#endif
// POCKET_CERTAIN: extra score per pocket pearl (pocketWorthPumping count) for a YES pump candidate
#ifndef POCKET_CERTAIN
#define POCKET_CERTAIN 0.0
#endif
// PUMP_TIP2: only split at the tip if we ate within the last PUMP_TIP2_REGION rounds (we harvested
// this dead end); dragons that merely start/walk into a dead end must not throw away a stub
#ifndef PUMP_TIP2_ATE
#define PUMP_TIP2_ATE 1
#endif
// ---- POCKET_FACTORY (notes/pocket_factory/LOG.md): general dead-end pocket cycle (entry test from timed
// expected pearls, one diver per pocket, eat to the end, split k=L-2 so the outward child carries the bulk).
#ifndef POCKET_FACTORY
#define POCKET_FACTORY 1
#endif
#ifndef PF_MAXLEN            // in-pocket control for dragons up to this length (longer: old play)
#define PF_MAXLEN 10
#endif
#ifndef PF_ENTER_MAXLEN      // only dragons this short dive
#define PF_ENTER_MAXLEN 3
#endif
#ifndef PF_MIN_P             // expected pearls along the dive path needed to enter (net = P - 2)
#define PF_MIN_P 2.5
#endif
#ifndef PF_SAFETY            // margin on reaching length 4 (the split) with expected pearls
#define PF_SAFETY 0.5
#endif
#ifndef PF_BONUS             // entry score per expected net pearl (P - 2)
#define PF_BONUS 4.0
#endif
#ifndef PF_ENEMY             // 0: veto any enemy head within 3 of the entry; 1: veto when enemies>=allies within 3;
#define PF_ENEMY 1           // 2: veto when enemies>allies; always veto an enemy head adjacent to the entry
#endif
#ifndef PF_AHEAD_MIN         // inside: keep going while at least this many expected pearls lie ahead
#define PF_AHEAD_MIN 0.5
#endif
#ifndef PF_CHILD_AREA        // inside: the k=L-2 child needs this much room (time-aware) or we step deeper first
#define PF_CHILD_AREA 4
#endif
#ifndef PF_UNIT_RESERVE      // no dives when fewer than this many free unit slots (a diver must split to get out)
#define PF_UNIT_RESERVE 6
#endif
#ifndef PF_PULL              // score per BFS step toward a free stocked pocket mouth (nearest ally only), 0 = off
#define PF_PULL 0.0
#endif
#ifndef PF_PULL_RANGE
#define PF_PULL_RANGE 6
#endif
#ifndef PF_EARLY             // inside with certain food ahead: split k=L+Pc-4 now (parent refills to 4 by the end)
#define PF_EARLY 1
#endif
#ifndef PF_CHILD_MAX         // >0: children of at most this size (tip: repeat one split per turn); 0 = one k=L-2 child
#define PF_CHILD_MAX 2
#endif

// ---- Schooltime layout B keepers (bot/maps/schooltime.hpp, notes/sch_b/LOG.txt). Default OFF.
#ifndef PM_SCHB              // R3 map-keyed switch: 0 off; else Schooltime layout-B keepers on with cluster mask = PM_SCHB (3 = our half, 15 = all)
#define PM_SCHB 0
#endif
#if PM_SCHB
#ifndef SCH_B_KEEP
#define SCH_B_KEEP 1
#endif
#ifndef SCH_B_KEEP_CL
#define SCH_B_KEEP_CL PM_SCHB
#endif
#endif
#ifndef SCH_B_KEEP           // on layout B, small dragons born near a top-strip cluster keep farming it
#define SCH_B_KEEP 0
#endif
#ifndef SCH_B_KEEP_CL        // cluster mask: 1 our west (8,2)(9,5)(10,7), 2 our east (14,3)(14,5)(20,4),
#define SCH_B_KEEP_CL 3      // 4 their east (mirror of 2), 8 their west (mirror of 1); team B mirrors x
#endif
#ifndef SCH_B_KEEP_R         // keepers are released at this round
#define SCH_B_KEEP_R 400
#endif
#ifndef SCH_B_KEEP_LEN       // keeper duty only while myLen <= this (and not a self-declared king)
#define SCH_B_KEEP_LEN 6
#endif
#ifndef SCH_B_KEEP_RANGE     // at birth: become the keeper of the nearest cluster within this many steps
#define SCH_B_KEEP_RANGE 6
#endif
#ifndef SCH_B_KEEP_ZONE      // the zone: tiles within this many steps of a cluster tile
#define SCH_B_KEEP_ZONE 4
#endif
#ifndef SCH_B_KEEP_PULL      // per step back towards the zone when outside it
#define SCH_B_KEEP_PULL 3.0
#endif
#ifndef SCH_B_KEEP_LEAVE     // penalty for stepping out of the zone
#define SCH_B_KEEP_LEAVE 12.0
#endif
#ifndef SCH_B_KEEP_TW        // per step towards the cluster tile that is due first
#define SCH_B_KEEP_TW 1.5
#endif
#ifndef SCH_B_KEEP_YIELD     // turns a lower-id ally head must share the zone before we give it up
#define SCH_B_KEEP_YIELD 3
#endif
// ---- notes/forensics: KING_ESCAPE ignored an unthreatened step even when it led into a dead end
#ifndef ESCAPE_DEADEND_FIX
#define ESCAPE_DEADEND_FIX 1
#endif
// ---- notes/portals_v31: Portals consolidation (M2). Portals is a solo race; our swarm keeps L<=5 splitting
// and pocket-diving to r450 (small mass 46 v 12 at r450, king share 0.29 v 0.64 in v30/v31 server losses).
#ifndef PM_POR_LATESPLIT     // Portals: LATE_SPLIT_ROUND override (-1 = keep 450; 0 = small splits stop at the split stop)
#define PM_POR_LATESPLIT 0
#endif
#ifndef PM_POR_DIVESTOP      // Portals: no pocket-factory / pump dives from this round (0 = off)
#define PM_POR_DIVESTOP 360
#endif
// ---- notes/forensics/portals + notes/portals_v31 (M4): a big dragon whose only move is a blind portal crossing
// into a body its own probe echoed last turn splits 2 off and stays (re-probe) instead of crossing. Value = min length.
#ifndef ECHO_EXIT_HOLD
#define ECHO_EXIT_HOLD 15
#endif
#ifndef ECHO_HOLD_MAX        // holds in a row before falling back to the normal decision
#define ECHO_HOLD_MAX 2
#endif
// ---- notes/forensics/portals + notes/portals_v31: a reverse-split child of at least this length keeps the crown
// (0 = off). Stops the newborn body feeding itself into its L2 parent (local: two L16 kings lost this way at age 0).
#ifndef CROWN_INHERIT
#define CROWN_INHERIT 5
#endif
// ---- notes/top3/PLAN.txt A: top-3 teams stop splitting after ~r330 on king maps and consolidate;
// no LATE_SPLIT small splits from this round on maps where we declare a king (0 = off)
#ifndef LATE_SPLIT_KING_MAPS
#define LATE_SPLIT_KING_MAPS 0
#endif
// ---- notes/slithery_pockets/LOG.txt: DIVE_VALUE - one dive-value rule for every dead-end pocket entry (old pump,
// pocket factory, plain scoring). A head that enters a dead end can never turn: its front 2 are lost (it must split
// k=L+P-2 out at the tip) or, if it cannot split (fewer than 4 by the tip / no unit slot), the whole dragon.
// V = P - 2 - DV_TURN_COST*turns (split possible) else -L, with P = expected pearls along the best single path
// (timed: visible / countdown-due = 1, remembered / fast guesses discounted; stops at tiles still occupied).
// Enter by choice only when V >= DV_MARGIN; any other entry is scored down by DV_PEN per length of shortfall.
#ifndef DIVE_VALUE
#define DIVE_VALUE 0
#endif
#ifndef DV_MARGIN            // required expected net length of a dive
#define DV_MARGIN 0.5
#endif
#ifndef DV_TURN_COST         // opportunity cost per turn spent inside (open-field eats/turn of a small dragon)
#define DV_TURN_COST 0.0
#endif
#ifndef DV_PEN               // score per length of shortfall for a non-approved entry (ranks forced/bad options)
#define DV_PEN 20.0
#endif
#ifndef DV_UNIT_RESERVE      // free unit slots needed to count on the tip split (else the whole dragon is lost)
#define DV_UNIT_RESERVE 1
#endif
#ifndef DV_CONTEST           // pearls expected per enemy head within 3 of the mouth are cut by this fraction
#define DV_CONTEST 0.0
#endif
#ifndef DV_FUNNEL            // weight (x DV_PEN) for stepping onto a core tile whose single core exit another head
#define DV_FUNNEL 0.5        // can take first while its other exits are losing pocket entries (0 = off)
#endif
#ifndef DV_PARTS             // DIVE_VALUE parts: 1 factory entry gate, 2 old pump gate, 4 inward-born child, 8 scoring
#define DV_PARTS 15
#endif
// ---- king beacon carries the POST-move head/facing (sonar is cast after the move; IMP_FINDINGS.md #3)
#ifndef KING_POS_POSTMOVE
#define KING_POS_POSTMOVE 0
#endif
// ---- scramble every sonar word we send with a keyed bijection (enemies intercept our rays) (IMP_FINDINGS.md)
#ifndef SONAR_ENCRYPT
#define SONAR_ENCRYPT 1
#endif
// ---- IMP_FINDINGS (durr cheji micro study): don't park our body on tiles about to spawn; don't coil over our own path
#ifndef SPAWN_BLOCK_PEN
#define SPAWN_BLOCK_PEN 0.0
#endif
#ifndef REVISIT_PEN
#define REVISIT_PEN 0.0
#endif
#ifndef REVISIT_WIN
#define REVISIT_WIN 20
#endif
// ---- CONSOLIDATION (notes/consolidation/LOG.txt; notes/top3/PLAN.txt B, IMP_FINDINGS.md 2).
// From CONS_R, a small dragon (L <= CONS_MAXLEN) that is not needed as reserve picks the nearest heard/seen
// longer ally (king beacons, CONS status beacons, visible ally heads) as its host, walks toward it while it
// keeps foraging, stops its own growth splits, and dies 1-2 tiles in front of / beside the host when it is
// first in line, no enemy head is near and the previous meal has been eaten. Default 0 = off (v32 identical).
#ifndef CONS_R
#define CONS_R 0              // start round (0 = off); test 330
#endif
#ifndef CONS_MAPS
#define CONS_MAPS 0           // 0 = king-race maps (Slithery, Schooltime, Portals, QoS), 1 = any king-declare map, 2 = all
#endif
#ifndef CONS_MAXLEN
#define CONS_MAXLEN 5         // feeders are this long or shorter
#endif
#ifndef CONS_HOST_MIN
#define CONS_HOST_MIN 5       // a host is at least this long ...
#endif
#ifndef CONS_GAP
#define CONS_GAP 3            // ... and at least this much longer than the feeder
#endif
#ifndef CONS_KEEP
#define CONS_KEEP 8           // no consolidation while our unit count is at or below this (reserve)
#endif
#ifndef CONS_RANGE
#define CONS_RANGE 24         // ignore hosts farther than this (wrap Manhattan)
#endif
#ifndef CONS_MEM
#define CONS_MEM 6            // host info older than this many rounds is ignored
#endif
#ifndef CONS_LEN_W
#define CONS_LEN_W 0.5        // host choice: minimise distance - CONS_LEN_W * length
#endif
#ifndef CONS_PULL
#define CONS_PULL 2.0         // score per BFS step toward the host's feed spot (one pearl = 10)
#endif
#ifndef CONS_PULL_CAP
#define CONS_PULL_CAP 30
#endif
#ifndef CONS_ENEMY_R
#define CONS_ENEMY_R 4        // never feed while an enemy head is this close to the host
#endif
#ifndef CONS_WAIT_R
#define CONS_WAIT_R 5         // throttle: a consolidator that is not first in line stops pulling inside this radius
#endif
#ifndef CONS_CLEAR
#define CONS_CLEAR 6.0        // throttle: ... and pays this to step within 2 of the host's head
#endif
#ifndef CONS_NOSPLIT
#define CONS_NOSPLIT 1        // consolidating feeders (and would-be hosts L>=CONS_HOST_MIN) skip growth splits
#endif
#ifndef CONS_BEACON
#define CONS_BEACON 1         // L >= CONS_BEACON_MIN dragons with idle rays send a status beacon (pos, len, id, dir)
#endif
#ifndef CONS_BEACON_MIN
#define CONS_BEACON_MIN 5
#endif
#ifndef CONS_BEACON_LEAD
#define CONS_BEACON_LEAD 10   // beacons start this many rounds before CONS_R
#endif
#ifndef CONS_TRACE
#define CONS_TRACE 0          // local diagnostics only: per-turn consolidation state to $CONS_TRACE_DIR/<id>.txt
#endif
#ifndef CONS_OVER_KING
#define CONS_OVER_KING 1      // 1: a (king-class) host replaces the KING_V2 feed pipeline (0: king feeding keeps priority)
#endif
#ifndef CONS_LOOSE
#define CONS_LOOSE 1          // also die within 2 of the host's 2-ahead tile (not only on the 4 exact spots)
#endif
#ifndef CONS_RELAY_HOPS
#define CONS_RELAY_HOPS 2     // dragons with idle rays re-send the longest status beacon they heard (0 = no relay)
#endif
#ifndef CONS_STEAL
#define CONS_STEAL 1          // wait while another small ally head is as close to our head as the host is
#endif
#ifndef CONS_HOST_FRAC
#define CONS_HOST_FRAC 0.75   // a host must be at least this fraction of the longest ally heard (0 = any longer ally)
#endif

// Early king (IMP_FINDINGS s5): round from which L<=6 dragons feed the king (v32: 380)
#ifndef KING_V2_FEED6_ROUND
#define KING_V2_FEED6_ROUND 300
#endif

// ---- v36 queen rules (unswbc 1.2.3, notes/queen/PLAN.md). Queens are dragons 0 and 1 (one per team);
// amQueen() = myId <= 1. All flags 0 = v35 behaviour.
// S1: the queen never rams/feeds/crowns, sees enemy reach F(L)+1 (uncapped), avoids threatened tiles.
#ifndef QUEEN_SAFE
#define QUEEN_SAFE 1
#endif
#ifndef QS_FROM
#define QS_FROM 100           // QUEEN_SAFE rules start this round (sticky); before it the queen plays v35 with limits
#endif
#ifndef QS_UNITS
#define QS_UNITS 0            // ...or once we have this many units (0 = from round QS_FROM only)
#endif
#ifndef QS_EARLY_RAM
#define QS_EARLY_RAM 1        // the early queen may ram strictly shorter heads (head-on kills both!)
#endif
#ifndef QUEEN_KING
#define QUEEN_KING 0          // king maps: from the seed round our queen is the only king (others don't crown, all feed her)
#endif
#ifndef QUEEN_ALIVE_MEM
#define QUEEN_ALIVE_MEM 30    // non-queens treat the queen as alive while heard/seen within this many rounds
#endif
#ifndef QUEEN_THREAT_PEN
#define QUEEN_THREAT_PEN 300.0
#endif
#ifndef QUEEN_PAID_PEN
#define QUEEN_PAID_PEN 120.0  // a tile an enemy head reaches only with one paid step
#endif
#ifndef QUEEN_EXIT_W
#define QUEEN_EXIT_W 8.0      // per free exit of the candidate tile
#endif
#ifndef QUEEN_HEAD_W
#define QUEEN_HEAD_W 60.0     // -W/dist to the nearest enemy head when dist <= 4
#endif
#ifndef QUEEN_MINLEN
#define QUEEN_MINLEN 2        // the queen's own (head) piece after a split
#endif
#ifndef QUEEN_ALLY_THREAT
#define QUEEN_ALLY_THREAT 0   // tiles next to ally heads count as threats for the queen
#endif
#ifndef QUEEN_BLIND_PEN
#define QUEEN_BLIND_PEN 200.0 // the queen crossing a portal onto a tile she can't see (v36_s1 default s1 died so)
#endif
#ifndef QUEEN_PEXIT_PEN
#define QUEEN_PEXIT_PEN 80.0  // the queen standing on a portal exit (others cross blind onto her)
#endif
#ifndef QUEEN_ESCAPE
#define QUEEN_ESCAPE 0        // a queen of L>=3 whose every step is threatened sprints 2-3 steps (KING_ESCAPE path)
#endif
// S4: queen lookahead. Penalise a step whose worst enemy reply (F free steps, then a ram) leaves < 2 safe exits.
#ifndef QUEEN_LOOK
#define QUEEN_LOOK 0
#endif
#ifndef QL_EXIT_PEN
#define QL_EXIT_PEN 80.0
#endif
#ifndef QUEEN_ENCLOSE_PEN
#define QUEEN_ENCLOSE_PEN 0.0  // v36q 400: open area (her body as a wall) below 3L+20, scaled by the missing fraction
#endif
#ifndef QUEEN_DIST_VETO
#define QUEEN_DIST_VETO 0      // veto ending within F(L)+1 of any visible enemy head when another safe step exists
#endif
#ifndef QUEEN_VETO_DEPTH
#define QUEEN_VETO_DEPTH 4    // an unthreatened alternative must survive this deep to veto a threatened step
#endif
// S2: 1.2.3 move costs (first ceil(L/4) steps free; F fixed at the turn's starting length, checked in replays).
#ifndef FREE_FIX
#define FREE_FIX 1
#endif
#ifndef FREE_SURVIVE
#define FREE_SURVIVE FREE_FIX // surviveDepth counts turns as ceil(step/F)
#endif
#ifndef THREAT_FREE
#define THREAT_FREE 0         // enemy reach = F(L) (full penalty) + up to 2 paid steps (x THREAT_PAID_MULT)
#endif
#ifndef THREAT_FREE_SMALL_CAP
#define THREAT_FREE_SMALL_CAP 2
#endif
#ifndef THREAT_PAID_MULT
#define THREAT_PAID_MULT 0.33
#endif
// S3: non-queens ram the enemy queen (id <= 1, other team) whenever they can.
#ifndef QUEEN_HUNT
#define QUEEN_HUNT 1
#endif
#ifndef QH_BONUS
#define QH_BONUS 500.0
#endif
#ifndef QH_MIN_UNITS
#define QH_MIN_UNITS 3
#endif

// ---- v37a (notes/newrules/PLAN.md, unswbc 1.2.3). F(L)=ceil(L/4), K(L)=F+(L-2) = kamikaze reach. All 0 = v36 with the v37a defaults above.
// Step 1 QKILL: any non-queen with a body-simulated path of <= K(myLen) steps onto the enemy queen's head takes it (certain kill).
#ifndef QKILL
#define QKILL 1
#endif
// Step 3 KREACH: enemy threat reach min(K(Lv), KR_CAP) (unseen tail: Lv>=3) for our L>=5 (paid tier x THREAT_PAID_MULT) and the queen (full).
#ifndef KREACH
#define KREACH 0
#endif
#ifndef KR_CAP
#define KR_CAP 4
#endif
// Step 4 QSTATE: queen-state modes from a queen beacon (QSECRET sonar word) and an enemy-queen tracker.
#ifndef QSTATE
#define QSTATE 0
#endif
#ifndef QS_LATE
#define QS_LATE 400           // our queen plays QUEEN_SAFE from this round when the enemy queen's fate is unknown
#endif
#ifndef QS_HUNT_W
#define QS_HUNT_W 20.0        // ours dead, theirs alive: -W*dist to the enemy queen's last tile (within QS_HUNT_R)
#endif
#ifndef QS_HUNT_R
#define QS_HUNT_R 12
#endif
#ifndef QS_SEEN_MEM
#define QS_SEEN_MEM 40        // an enemy-queen sighting older than this is not hunted
#endif
#ifndef QS_RELAY_HOPS
#define QS_RELAY_HOPS 3
#endif
// Step 7 KREACH_KING: kings see L>=17 enemies at F(Lv) (past KING_THREAT_REACH); king keep-away >= F(enemy)+1.
#ifndef KREACH_KING
#define KREACH_KING 1
#endif

// ---- v37e = v37d + QGUARD (ported from v37b, PLAN.md step 2; notes/newrules/V37E.md). QGUARD 0 = v37d.
// QGUARD: queen keeps >= QG_MIN after any split, splits on a trap only when every step is lethal,
// avoids dead ends she can't turn in (never against the QUEEN_SAFE threat veto); allies keep their head away from hers.
#ifndef QGUARD
#define QGUARD 1           // v38q: on (NEWMAPS re-test: dilemma/autarky/slithery 74/120 vs v38q QGUARD=0, queen alive 41 v 19)
#endif
#ifndef QG_FROM
#define QG_FROM 20            // QGUARD applies from this round...
#endif
#ifndef QG_UNITS
#define QG_UNITS 4            // ...or once we have this many units (v37b: 5; AB_DIAG asks >= 4)
#endif
#ifndef QG_MIN
#define QG_MIN 5              // queen length kept after a split (F=2)
#endif
#ifndef QG_ALLY_PEN
#define QG_ALLY_PEN 300.0     // ally ending a step with our queen's head inside its kamikaze reach K
#endif
#ifndef QG_ALLY_KCAP
#define QG_ALLY_KCAP 3        // cap on that K (a long ally's K covers the whole view)
#endif

// ---- v38 = v37e + UNK_SCARCE_FIX + UNK_PORTAL_EXPLORE (ported from bot/, notes/qualifier/SCARCE_PORTAL.md, scp2 settings)
// + QALLY_KEEP (notes/newrules/V38.md). All three = 0 gives v37e.
// UNK_SCARCE_FIX=1: once seen spawners reachable only via portal pairs whose BOTH ends we've seen are
// >= USF_FRAC of the known food rate (and >= USF_MIN tiles), path through known pairs (sticky).
#ifndef UNK_SCARCE_FIX
#define UNK_SCARCE_FIX 1
#endif
#ifndef USF_MIN
#define USF_MIN 4
#endif
#ifndef USF_FRAC
#define USF_FRAC 0.5
#endif
// per-spawner-tile richness: portal-only rate/tile >= USF_RICH x walkable rate/tile (0 = no test)
#ifndef USF_RICH
#define USF_RICH 4
#endif
#ifndef USF_LOG
#define USF_LOG 0
#endif
// UNK_PORTAL_EXPLORE=1 (calc's rule): small (L<=UPE_MAXLEN) non-queen (id>1) dragons with no walkable food
// (no remembered pearl / spawn due on arrival within UPE_RANGE steps) for UPE_HUNGER rounds scout an unexplored portal
// via the UNK_EXPLORE knock/cross machinery. Rationed: (id + round/UPE_SLOT) % UPE_MOD == 0, no ally head within 3.
#ifndef UNK_PORTAL_EXPLORE
#define UNK_PORTAL_EXPLORE 1
#endif
#ifndef UPE_MAXLEN
#define UPE_MAXLEN 4
#endif
#ifndef UPE_HUNGER
#define UPE_HUNGER 25
#endif
#ifndef UPE_RANGE
#define UPE_RANGE 16
#endif
#ifndef UPE_SOON
#define UPE_SOON 4
#endif
#ifndef UPE_MIN_ROUND
#define UPE_MIN_ROUND 5
#endif
#ifndef UPE_SLOT
#define UPE_SLOT 30
#endif
#ifndef UPE_MOD
#define UPE_MOD 4
#endif
// QALLY_KEEP=1: non-queen allies pay QAK_PEN for ending a step within QAK_DIST (Manhattan) of our queen's head
// or on her best escape tiles (largest-flood open first step + QAK_ESC_DEPTH more), when the queen is seen
// (or beaconed this/last round), from round QAK_FROM. Feeding the queen in feedPhase is exempt.
#ifndef QALLY_KEEP
#define QALLY_KEEP 1            // v43: on (Maze/weakhold queen walled in by allies, V43.md); was 0           // off: lesson .427 alone vs v37d (V38.md)
#endif
#ifndef QAK_PEN
#define QAK_PEN 150.0
#endif
#ifndef QAK_DIST
#define QAK_DIST 2
#endif
#ifndef QAK_ESC_DEPTH
#define QAK_ESC_DEPTH 2
#endif
#ifndef QAK_CAP
#define QAK_CAP 24
#endif
#ifndef QAK_FROM
#define QAK_FROM 10
#endif
// ---- v38q = v38m + QBOX + QSPLIT_ROOM port (v39a) + QGUARD small-region rule (notes/newrules/V38Q.md)
// QBOX: queen with no legal move splits (myLen-2) even without a tail exit; QBOX_EAT_PEN on a pearl step that leaves
// her no free neighbour next turn; from QBOX_LATE no voluntary queen split leaves her below L3.
#ifndef QBOX
#define QBOX 1
#endif
#ifndef QBOX_RESERVE
#define QBOX_RESERVE 1        // unit slots non-queens leave free (a split at 64 units is illegal and kills the parent)
#endif
#ifndef QBOX_LATE
#define QBOX_LATE 480
#endif
#ifndef QBOX_EAT_PEN
#define QBOX_EAT_PEN 500.0
#endif
#ifndef QBOX_REGION_CAP
#define QBOX_REGION_CAP 64
#endif
// QGUARD: the QG_MIN split floor is off while the queen's kelp-sealed region is < QG_REGION_MIN tiles
#ifndef QG_REGION_MIN
#define QG_REGION_MIN 6
#endif
// v39 QSPLIT_ROOM (ported from v39a): the queen splits only with >= QSR_A tiles on her side and no ally head within QSR_ALLY
#ifndef QSPLIT_ROOM
#define QSPLIT_ROOM 1
#endif
#ifndef QSR_A
#define QSR_A 16
#endif
#ifndef QSR_ALLY
#define QSR_ALLY 2
#endif

// ---- v38s: Sprint maps known (notes/newrules/V38S.md)
// SPRINT_KNOWN=1: adopt the 7 Sprint maps from maps_data and give them UNK_KING seed/feed + small-map ram guard.
// 0 = behave as v38m (Sprint candidates skipped, maps stay unknown).
#ifndef SPRINT_KNOWN
#define SPRINT_KNOWN 1
#endif
// SPRINT_KING_FULL=1: on a known Sprint map also use UNK_KING's shrinking feed reserve + crown-early rule
#ifndef SPRINT_KING_FULL
#define SPRINT_KING_FULL 1
#endif
#ifndef SPRINT_DEBUG
#define SPRINT_DEBUG 0
#endif
// SPRINT_ROUTE=1: keep PEARL_ROUTE=2's route valuation on known Sprint maps (v38m had it there as unknown maps)
#ifndef SPRINT_ROUTE
#define SPRINT_ROUTE 1
#endif

// SPRINT_ROUTE off on weakhold (112-game test: weakhold route off 14/16, on 0/16; other Sprint maps better with it)
#ifndef SPRINT_ROUTE_NOWEAK
#define SPRINT_ROUTE_NOWEAK 1
#endif

// ---- v41: FREE_STEPS (notes/newrules/V41.md)
// FREE_STEPS=1: dragons with F=ceil(L/4)>=2 also score free multi-step paths of 2..F steps (beam search over the
// normal per-move evaluation run on a virtual body), and take the best one when it beats the chosen 1-step by FS_MARGIN.
#ifndef FREE_STEPS
#define FREE_STEPS 1
#endif
#ifndef FS_MAXF
#define FS_MAXF 4 // longest path tried (F capped here)
#endif
#ifndef FS_BEAM
#define FS_BEAM 3 // prefixes kept per depth
#endif
#ifndef FS_MARGIN
#define FS_MARGIN 0.5
#endif
#ifndef FS_BUDGET_M
#define FS_BUDGET_M 20 // stop expanding once this turn has used this many M points
#endif
#ifndef FS_EAT_W
#define FS_EAT_W 8.2 // value of a pearl eaten on an intermediate step (= 10 * PEARL_GAMMA, like an endpoint pearl)
#endif
#ifndef FS_PAID_VETO
#define FS_PAID_VETO 1 // a path endpoint in paid-step ram reach only if the chosen 1-step is too
#endif
#ifndef FS_VIS
#define FS_VIS 1 // endpoint's neighbours must be in view; unseen tiles 2 away cost FS_BLIND_PEN each (queen: veto)
#endif
#ifndef FS_BLIND_PEN
#define FS_BLIND_PEN 3.0
#endif
#ifndef FS_DEBUG
#define FS_DEBUG 0 // LOG fsused lines for usage counting
#endif

// ---- v43 (notes/newrules/V43.md): Maze/weakhold queen survival. All 0 = v41.
// QEXIT_KEEP: non-queen allies pay QEK_PEN for ending a move (incl. FREE_STEPS paths) that leaves our visible queen's
// head with <= QEK_MIN free neighbours when it had more.
#ifndef QEXIT_KEEP
#define QEXIT_KEEP 0
#endif
#ifndef QEK_PEN
#define QEK_PEN 400.0
#endif
#ifndef QEK_MIN
#define QEK_MIN 1
#endif
#ifndef QEK_FROM
#define QEK_FROM 0
#endif
// QBOX_K2: a queen with no legal move (L >= 5) splits off only 2 (keeps L-2) instead of k = L-2.
#ifndef QBOX_K2
#define QBOX_K2 1
#endif
// WH_NOPUMP: on weakhold (known map) no pocket-factory dives or pocket pumps.
#ifndef WH_NOPUMP
#define WH_NOPUMP 0
#endif
// QNOPOCKET: the queen's step deeper into a leaf-pruned dead-end pocket (pfDepth) counts as a QGUARD dead end
// (vetoed when an open surviving step exists), from round 1, whether or not QGUARD is active yet.
#ifndef QNOPOCKET
#define QNOPOCKET 0
#endif
// QOPEN_PEN: queen (QUEEN_SAFE phase) pays this per missing kelp-exit below 3 on her step's tile (0 = off).
#ifndef QOPEN_PEN
#define QOPEN_PEN 0.0
#endif

// ---- v44 (notes/newrules/V44.md): weakhold growth + Maze queen. All 0 = v43.
// ESC_NET: surviveDepth's escape-by-split (L0<=3 growing to 4) only counts when the path ate at least ESC_NET pearls,
// so the doomed 2-long stub is paid for (weakhold treadmill: L3 eats one corpse in the (10,1) corner, grows to 4 in a
// 2x2 loop, splits, stub dies: net -1 per cycle). 0 = off.
#ifndef ESC_NET
#define ESC_NET 0
#endif
// WH_CENTRE: weakhold opening. The non-queen starter (ids 2/3; WHC_IDS&2: every id < 8) pays WHC_PULL per BFS step
// to the nearest tile with gmax >= WHC_GAP (the open fields) until within WHC_STOP of it or round WHC_UNTIL.
#ifndef WH_CENTRE
#define WH_CENTRE 1          // v44: on (weakhold only, V44.md)
#endif
#ifndef WHC_PULL
#define WHC_PULL 4.0
#endif
#ifndef WHC_GAP
#define WHC_GAP 100
#endif
#ifndef WHC_STOP
#define WHC_STOP 0
#endif
#ifndef WHC_UNTIL
#define WHC_UNTIL 60
#endif
#ifndef WHC_IDS
#define WHC_IDS 3            // v44: 3 = every non-queen id < 8
#endif
// QEXIT1: queen pays QX_PEN for a step into a 1-wide corridor (<= QX_LEN tiles checked) whose onward tile is blocked
// by another body for longer than she reaches it, or has another head within QX_R (enemy heads x QX_ENEMY_MULT).
#ifndef QEXIT1
#define QEXIT1 0
#endif
#ifndef QX_PEN
#define QX_PEN 60.0
#endif
#ifndef QX_LEN
#define QX_LEN 4
#endif
#ifndef QX_R
#define QX_R 2
#endif
#ifndef QX_ENEMY_MULT
#define QX_ENEMY_MULT 1.0
#endif
#ifndef QX_FROM
#define QX_FROM 0
#endif
// ---- v51 MATCH_STRICT (lite): unseen-map guard. Official maps (start fits) play exactly as v44. A starting dragon whose
// start fits no same-size known map marks the map unseen and passes that on at its splits; children that hear it drop
// any known-map guess. (v45/v49's strict child rules, handoff gossip and pearl distrust are NOT used: v49 regressed on
// the server, notes/newrules/UNSEEN_GENERALISATION.md section 10.)
#ifndef MATCH_STRICT
#define MATCH_STRICT 1
#endif
#ifndef MS_DEBUG
#define MS_DEBUG 0 // 1: one line per turn to the file named by env MS_TRACE
#endif
#ifndef MS_GOSSIP_R
#define MS_GOSSIP_R 500 // unseen-map word also on idle turns before this round (0 = split turns only); only fires on look-alike unseen maps
#endif

// ---- v47 (notes/newrules/V47.md): EQ_HUNT, hunt the enemy queen (NEW_RULES_TOP5 idea 1). All 0 = v43.
// EQ_HUNT=1: run the QSTATE enemy-queen tracker (sightings relayed on the idle sonar rays; our own queen's
// QSTATE play-safe modes are NOT turned on), and small non-queen, non-king units within EQH_R of her last
// sighting (<= EQH_MEM rounds old) pay EQH_W per Manhattan step to it. Active from round EQH_FROM, or once
// we have >= EQH_UNITS units. From EQH_LATE the radius is EQH_R_LATE and the length cap EQH_MAXLEN_LATE.
// EQ_HUNT=2 (= "EQ_HUNT_LATE"): same but only from EQH_LATE.
#ifndef EQ_HUNT
#define EQ_HUNT 0 // v68: off (= v61); LATE_HUNT reuses its tracker and pull code
#endif
#ifndef EQH_W
#define EQH_W 6.0
#endif
#ifndef EQH_R
#define EQH_R 12
#endif
#ifndef EQH_R_LATE
#define EQH_R_LATE 20
#endif
#ifndef EQH_MAXLEN
#define EQH_MAXLEN 4
#endif
#ifndef EQH_MAXLEN_LATE
#define EQH_MAXLEN_LATE 8
#endif
#ifndef EQH_FROM
#define EQH_FROM 200
#endif
#ifndef EQH_UNITS
#define EQH_UNITS 24
#endif
#ifndef EQH_LATE
#define EQH_LATE 300
#endif
#ifndef EQH_MEM
#define EQH_MEM 20
#endif
// EQH_NOTHREAT=1: a hunter ignores the enemy queen's own threat zone (her head-on with ours kills both: a win
// for us at r500 while our queen lives); her body still blocks.
#ifndef EQH_NOTHREAT
#define EQH_NOTHREAT 1
#endif
// EQH_MIN_UNITS: no pull while we have fewer units than this (don't strip a thin army)
#ifndef EQH_MIN_UNITS
#define EQH_MIN_UNITS 6
#endif
// EQH_BFS=1: pull by this move's time-aware BFS distance to a tile beside her head (kelp/portals respected),
// capped at EQH_CAP (unreachable = cap: no pull); 0 = Manhattan distance (first version)
#ifndef EQH_BFS
#define EQH_BFS 1
#endif
#ifndef EQH_CAP
#define EQH_CAP 30
#endif
#ifndef EQH_DEBUG
#define EQH_DEBUG 0
#endif
// ---- v47 round 2: who to hunt and how to approach
// EQH_TARGET=1: hunt only queens that don't run: max seen length >= EQH_BIGLEN, or sightings that stayed within
// EQH_STILL_R of one tile for >= EQH_STILL_ROUNDS rounds. A big target lets units up to EQH_MAXLEN_BIG hunt (K reach).
#ifndef EQH_TARGET
#define EQH_TARGET 1 // v59: on
#endif
#ifndef EQH_BIGLEN
#define EQH_BIGLEN 8
#endif
#ifndef EQH_STILL_R
#define EQH_STILL_R 3
#endif
#ifndef EQH_STILL_ROUNDS
#define EQH_STILL_ROUNDS 8
#endif
#ifndef EQH_MAXLEN_BIG
#define EQH_MAXLEN_BIG 8 // v59: 8 (v47 default EQH_MAXLEN)
#endif
// intercept: aim EQH_LEAD steps ahead of her facing and EQH_FLANK to the side (odd ids one side, even the other),
// while farther than EQH_LEAD_NEAR from her; 0/0 = aim at her head
#ifndef EQH_LEAD
#define EQH_LEAD 0
#endif
#ifndef EQH_FLANK
#define EQH_FLANK 0
#endif
#ifndef EQH_LEAD_NEAR
#define EQH_LEAD_NEAR 3
#endif
// a big target (EQH_TARGET, max length >= EQH_BIGLEN) is hunted from farther and on older sightings
#ifndef EQH_MEM_BIG
#define EQH_MEM_BIG EQH_MEM
#endif
#ifndef EQH_R_BIG
#define EQH_R_BIG 0
#endif

// ---- v68 (notes/newrules/V68.md): LATE_HUNT. Once our queen is known dead (an ally saw her die, or heard the
// relayed notice) and the enemy queen is not known dead, r500 is lost unless she dies: pull non-king units map-wide
// toward her last sighting (or sweep her spawn side), ignoring her threat zone. Nothing changes while our queen lives.
#ifndef LATE_HUNT
#define LATE_HUNT 0 // bot/: off = v61; v68 runs 1
#endif
#ifndef LH_MAXLEN
#define LH_MAXLEN 8           // hunters: non-king units up to this length...
#endif
#ifndef LH_SMALLQ
#define LH_SMALLQ 4           // ...or any length when her max seen length is <= this
#endif
#ifndef LH_W
#define LH_W 6.0              // pull per BFS step
#endif
#ifndef LH_CAP
#define LH_CAP 60
#endif
#ifndef LH_MEM
#define LH_MEM 60             // a sighting younger than this is chased (unless I checked her tile and she's gone)
#endif
#ifndef LH_MIN_UNITS
#define LH_MIN_UNITS 1
#endif
#ifndef LH_SWEEP
#define LH_SWEEP 1            // no usable sighting: walk to the enemy spawns (known maps), queen spawn first
#endif
#ifndef LH_KING_KILL
#define LH_KING_KILL 1        // the king may also take a visible queen-kill (tryQueenKill) while hunting
#endif
#ifndef LH_NOTICE_FULL
#define LH_NOTICE_FULL 20     // "our queen is dead" notice on idle rays every turn for this many rounds after learning...
#endif
#ifndef LH_NOTICE_EVERY
#define LH_NOTICE_EVERY 5     // ...then every this many rounds
#endif
#ifndef LH_DEBUG
#define LH_DEBUG 0
#endif
// LH_BEACON=1: also infer "dead" from silence: our queen beacons on fully idle turns, allies relay it sparsely and
// king words carry an "alive recently" key salt. Off by default: the queen's rays mostly hit kelp, so silence gave
// many false alarms (r65+ on Trauma/AUNSW/Slithery), which break the "no change while she lives" rule.
#ifndef LH_BEACON
#define LH_BEACON 0
#endif
#ifndef LH_SILENT
#define LH_SILENT 40          // LH_BEACON: no sign of our queen for this many rounds (after hearing her once) = dead
#endif
#ifndef LH_BEACON_EVERY
#define LH_BEACON_EVERY 1     // our queen's alive beacon on fully idle turns, every this many rounds
#endif
#ifndef LH_RELAY_FRESH
#define LH_RELAY_FRESH 12     // relay an alive round at most this old...
#endif
#ifndef LH_RELAY_GAP
#define LH_RELAY_GAP 3        // ...and at most once per this many rounds per dragon
#endif
#ifndef LH_EVID
#define LH_EVID 1             // hunt only after a sighting of her at/after our queen's death
#endif
#ifndef LH_SWEEP_MEM
#define LH_SWEEP_MEM 120      // sweep the enemy spawns only while her last sighting is younger than this
#endif

// ================= ROUND 2 (notes/newrules/ROUND2.md "Built flags"). All default 0 = v61. =================
// ---- P1: kill the lone enemy queen (use together with LATE_HUNT=1)
// QKILL_KING=1: a king in the feed phase also takes a certain visible queen-kill (tryQueenKill). v61 returned from
// tryRam() on `feedPhase() && iAmKing()` before the QKILL call, so L>=8 self-crowned campers and the real king refused
// free kills (985968 r419: L8 unit, lone queen 5 steps away, K=8; 1007417: L26 king). A king of L >= QKK_KEEP_LEN
// skips it only when our queen was seen alive within QKK_ALIVE_MEM rounds and is longer than the target looks.
#ifndef QKILL_KING
#define QKILL_KING 0
#endif
#ifndef QKK_KEEP_LEN
#define QKK_KEEP_LEN 20
#endif
#ifndef QKK_ALIVE_MEM
#define QKK_ALIVE_MEM 30
#endif
// LH_FINISH=1 (needs LATE_HUNT=1 for the tracker): local finisher, independent of our queen's state. A non-queen,
// non-king unit that itself saw her within LHF_MEM rounds at max length <= LHF_QLEN, with no other enemy head in
// view, from round LHF_FROM, gets the LATE_HUNT pull to her (her threat zone ignored). Not lhOn(): no relay changes.
#ifndef LH_FINISH
#define LH_FINISH 0
#endif
#ifndef LHF_FROM
#define LHF_FROM 300
#endif
#ifndef LHF_QLEN
#define LHF_QLEN 4
#endif
#ifndef LHF_MEM
#define LHF_MEM 8
#endif
// LH_LONG=1: while this unit's hunt pull is on, no growth split leaves the parent below LHL_KEEP (an L2 hunter has
// kamikaze reach 1: Devil 985964 had 582 sighting turns and 0 killable), and hunters shorter than LHL_SMALL pull at
// LHL_SMALL_MULT x LH_W so they still eat on the way.
#ifndef LH_LONG
#define LH_LONG 0
#endif
#ifndef LHL_KEEP
#define LHL_KEEP 6
#endif
#ifndef LHL_SMALL
#define LHL_SMALL 5
#endif
#ifndef LHL_SMALL_MULT
#define LHL_SMALL_MULT 0.5
#endif
// R2_DEBUG=1: "LOG r2 <event> r.. id.. L.. v.." lines for local mechanism counts (never on the server)
#ifndef R2_DEBUG
#define R2_DEBUG 0
#endif
// ---- P3: allies must not seal our queen
// QAK_HARD=1: an ally of length >= QAKH_LEN that sees our queen's head marks a step as "queen-blocking" when it ends
// within QAKH_DIST of her head without moving away from her, or cuts her free neighbours to <= QAKH_MIN (QEXIT_KEEP's
// count: bodies included). A marked best step is replaced by the best unmarked step that is unthreatened, not a dead
// end and survives QUEEN_VETO_DEPTH (same shape as the QGUARD veto); free-step paths through marked tiles are dropped.
// A long body follows its head, so keeping the head out keeps the body off her exits (Maze 985232, PD 984268).
#ifndef QAK_HARD
#define QAK_HARD 0
#endif
#ifndef QAKH_LEN
#define QAKH_LEN 8
#endif
#ifndef QAKH_DIST
#define QAKH_DIST 3
#endif
#ifndef QAKH_MIN
#define QAKH_MIN 1
#endif
// QPLUG_LOOK=1: the queen follows a 1-wide corridor behind her step for up to QPL_DEPTH tiles (10: a long queen dies deep in a corridor, Maze 985232); if it is plugged by
// another dragon's body that will still be there when she arrives, the step counts as a dead end (vetoed when an open
// surviving step exists). Body plugs only: QEXIT_LOOK (all low-exit tiles) lost on the server.
#ifndef QPLUG_LOOK
#define QPLUG_LOOK 0
#endif
#ifndef QPL_DEPTH
#define QPL_DEPTH 10
#endif
#ifndef QPL_FROM
#define QPL_FROM 20
#endif
// ---- P5: stillborn children. No new flag for the split half: use SPLIT_NEEDS_EXIT=1 (line ~141). Local split-site
// counts (R2_DEBUG, 24 games): the growth split makes 88% of all children that die within a round of birth, and 91% of
// growth splits made with no tail exit are stillborn (7% with one).
// ---- P6: defensive reach and endgame
// KREACH_MINLEN / KREACH_QUEEN: who gets the KREACH kamikaze reach when KREACH=1 (defaults = the old behaviour:
// L>=5 paid tier, queen full). Staged test: KREACH=1 KREACH_MINLEN=8 KREACH_QUEEN=0 KR_CAP=6.
#ifndef KREACH_MINLEN
#define KREACH_MINLEN 5
#endif
#ifndef KREACH_QUEEN
#define KREACH_QUEEN 1
#endif
// ENDGAME_GUARD=<round> (0 = off; test 470): from that round our queen and our king (iAmKing, L >= KING_MIN_LEN)
// protect the lead: no voluntary splits; every visible enemy head is given kamikaze reach K(Lv) (unseen tail: Lv >=
// EG_UNSEEN_LEN); tiles within K+1 cost EG_W per step of overlap, and a best step inside K is replaced by the best
// step outside it that is unthreatened, not a dead end and survives QUEEN_VETO_DEPTH. Free-step paths obey the same.
// EG_NOSWAP=<round> (0 = off): from that round a king does not take the king-escape reverse split (loses 2 length).
#ifndef ENDGAME_GUARD
#define ENDGAME_GUARD 0
#endif
#ifndef EG_UNSEEN_LEN
#define EG_UNSEEN_LEN 6
#endif
#ifndef EG_W
#define EG_W 40.0
#endif
#ifndef EG_NOSWAP
#define EG_NOSWAP 0
#endif
// ROUND6 QK_EG (OWN_RANKED_OCT4 fix 1): the crowned queen (queenKingRound, L >= QK_EG_MINLEN) applies the endgame-guard
// kamikaze reach K(Lv) / EG_W penalty / veto at any round; an unseen tail counts as QK_EG_UNSEEN_LEN. No split ban.
#ifndef QK_EG
#define QK_EG 0
#endif
#ifndef QK_EG_MINLEN
#define QK_EG_MINLEN 12
#endif
#ifndef QK_EG_UNSEEN_LEN
#define QK_EG_UNSEEN_LEN 4
#endif
// QK_EG=2: also give her the kamikaze reach min(K(Lv), QK_EG_KRCAP) as full threat in computeThreats (threat penalty and
// the queen threat veto), +1 for a head that closed in two rounds in a row (QK_EG_TREND). QK_EG_KING=1: the same threat
// reach for our king (iAmKing, L >= QK_EG_KINGLEN), no guard veto, no split ban.
#ifndef QK_EG_KRCAP
#define QK_EG_KRCAP 5
#endif
#ifndef QK_EG_TREND
#define QK_EG_TREND 1
#endif
#ifndef QK_EG_KING
#define QK_EG_KING 0
#endif
#ifndef QK_EG_KINGLEN
#define QK_EG_KINGLEN 10
#endif
// ROUND6 QK_SURV (fix 2): the crowned queen's survival look-ahead is min(L, QK_SURV_CAP) deep (never below the old
// depth), park-banned steps (qparkBan, e.g. portals on Portals) are blocked inside it, node cap QK_SURV_NODES per call.
#ifndef QK_SURV
#define QK_SURV 0
#endif
#ifndef QK_SURV_CAP
#define QK_SURV_CAP 30
#endif
#ifndef QK_SURV_NODES
#define QK_SURV_NODES 8000    // per 1-step candidate
#endif
#ifndef QK_SURV_FSNODES
#define QK_SURV_FSNODES 2000  // per free-path node
#endif
#ifndef QK_SURV_BUDGET_M
#define QK_SURV_BUDGET_M 22   // past this many M points this turn the old depth is used
#endif

// ---- R3 SPRINT_KING_PM (folded from variants/v70): per-map king seed/feed/merge on Around UNSW / Islands / Australia
// (LOSS_AUDIT2 fix 2). Other Sprint maps keep UNK_KING_SEED/FEED. A map set to 250/300 = v61. Default OFF.
#ifndef SPRINT_KING_PM
#define SPRINT_KING_PM 0
#endif
#ifndef PM_AUNSW_SEED
#define PM_AUNSW_SEED 190
#endif
#ifndef PM_AUNSW_FEED
#define PM_AUNSW_FEED 230
#endif
#ifndef PM_ISL_SEED
#define PM_ISL_SEED 250
#endif
#ifndef PM_ISL_FEED
#define PM_ISL_FEED 300
#endif
#ifndef PM_AUS_SEED
#define PM_AUS_SEED 250
#endif
#ifndef PM_AUS_FEED
#define PM_AUS_FEED 300
#endif
#ifndef PM_AUNSW_MERGE
#define PM_AUNSW_MERGE KING_V2_MERGE_ROUND
#endif
#ifndef PM_ISL_MERGE
#define PM_ISL_MERGE KING_V2_MERGE_ROUND
#endif
#ifndef PM_AUS_MERGE
#define PM_AUS_MERGE KING_V2_MERGE_ROUND
#endif

// ---- R3 STRIPES_LOOP (bot/maps/stripes.hpp): Stripes centre-loop opening. 0 off; 1 = queen laps the loop, second
// starter dives the far W vault; 2 = queen laps, second starter unchanged, the queen's first loop child dives W.
#ifndef STRIPES_LOOP
#define STRIPES_LOOP 0
#endif
#ifndef STRIPES_LOOP_W       // score per step along the route / the loop
#define STRIPES_LOOP_W 40.0
#endif
#ifndef STRIPES_LOOP_R       // the queen stops lapping at this round
#define STRIPES_LOOP_R 500
#endif
#ifndef STRIPES_DIVE_T       // the W diver gives up this many rounds after birth
#define STRIPES_DIVE_T 40
#endif
#ifndef STRIPES_KID_R        // mode 2: a queen child born on the loop up to this round is the W diver
#define STRIPES_KID_R 20
#endif
#ifndef STRIPES_SPLIT_L      // the lapping queen splits 2 off at this length (two eats per lap on an 8-ring: she must enter the box at <= 5)
#define STRIPES_SPLIT_L 6
#endif

// ---- R3 TROPHY_QSPLIT (ROUND2 backlog "Trophy queen split floor"): on Trophy only, while we have at most
// TROPHY_QSPLIT_UNITS units (and before TROPHY_QSPLIT_R) the queen's split floors (early keep >= 3, QG_MIN) are off,
// so she splits at L4 like a normal unit. Server: our first queen split r27 v r10, 3 units at r30 v 6.5.
#ifndef TROPHY_QSPLIT
#define TROPHY_QSPLIT 0
#endif
#ifndef TROPHY_QSPLIT_UNITS
#define TROPHY_QSPLIT_UNITS 8
#endif
#ifndef TROPHY_QSPLIT_R
#define TROPHY_QSPLIT_R 100
#endif

// ---- ROUND3 P7 PM_QPARK (map-specific, default off; keyed through applyMapParams)
#ifndef PM_QPARK_PORTALS
#define PM_QPARK_PORTALS 1    // Portals: queen never crosses a portal, parks far from every portal exit, crowned at the seed round
#endif
#ifndef PM_QPARK_MAZE
#define PM_QPARK_MAZE 1       // Maze: queen stays in the home field (frame x < PM_MAZE_QX), crowned at the seed round
#endif
#ifndef PM_MAZE_CR
#define PM_MAZE_CR -1.0       // Maze: crowd penalty for every unit while round < king seed round (applied at the use site).
#endif                        // -1 = PM_MAZE_CR_AUTO when PM_QPARK_MAZE is on, else off; 0 = off; > 0 = that value (crowd-only test)
#ifndef PM_MAZE_CR_AUTO
#define PM_MAZE_CR_AUTO 5.0
#endif
#ifndef PM_MAZE_QX
#define PM_MAZE_QX 9          // Maze: first forbidden frame column for the queen (home field is x <= 10, doorways at 10/11)
#endif
#ifndef PM_MAZE_QSTAY
#define PM_MAZE_QSTAY 1       // Maze: 1 = the crowned queen stays in the home field for the whole game, 0 = only until the seed round
#endif
#ifndef PM_QP_PEN
#define PM_QP_PEN 600.0       // parked queen: penalty for a forbidden step (portal crossing / leaving the field)
#endif
#ifndef PM_QP_PULL
#define PM_QP_PULL 25.0       // Portals, before she is fed: per tile beyond L/4 from her 2x2 anchor block (an exit is worth 8: 8 let her drift off)
#endif
#ifndef PM_QP_PULL_FED
#define PM_QP_PULL_FED 8.0    // Portals, while she is fed: per tile beyond 3 + L/4 from her anchor
#endif
#ifndef PM_QP_FLEE
#define PM_QP_FLEE 5          // a visible enemy head this close lifts the Portals park rules for the turn
#endif
#ifndef PM_QK_DMIN
#define PM_QK_DMIN 1          // per-map queen-king: feeders die this many walking steps from her head at the nearest...
#endif
#ifndef PM_QK_DMAX
#define PM_QK_DMAX 5          // ...and this many at the furthest (a live ally body never waits beside her)
#endif
#ifndef PM_QK_KEEP
#define PM_QK_KEEP 3          // per-map queen-king: QALLY_KEEP radius round the crowned queen (QAK_DIST before the seed round)
#endif
#ifndef PM_QP_FLEEPEN
#define PM_QP_FLEEPEN 250.0   // Portals: portal crossing cost for the parked queen while an enemy head is within PM_QP_FLEE
#endif
#ifndef PM_QP_ALLY
#define PM_QP_ALLY 40.0       // Portals: parked/crowned queen, per ally head next to the tile she would step on
#endif
#ifndef PM_POR_QKFROM
#define PM_POR_QKFROM 0       // Portals: the parked queen is crowned at max(king seed round, this); before it non-queens play their normal king game
#endif
#ifndef PM_MAZE_QKFROM
#define PM_MAZE_QKFROM 0      // Maze: same
#endif
#ifndef PM_POR_QKCAP
#define PM_POR_QKCAP 0        // Portals: feeders stop feeding the crowned queen at this length (0 = no cap)
#endif
#ifndef PM_MAZE_QKCAP
#define PM_MAZE_QKCAP 50      // Maze: same (she still passes it on pearls already down and the r400 field respawn)
#endif

// ---- ROUND4 QPARK_GEN: generic queen park (RP.qPark 3). The queen picks a home block near her spawn from what she
// knows (open 2x2 with >= 2 roomy exits, far from portal mouths/exits, pockets, 1-wide corridors and the enemy half),
// stays within QPG_RAD of it (eats what spawns there, early splits unchanged), never crosses a portal or enters a
// pocket, and is crowned at the king seed round (RP.queenKing). One flag per known map + QPARK_UNK for unseen maps.
// Flag value 1 = parked from r0; 2 = late park (b1 play until QPG_UNITS units or round QPG_FROM, then park).
#ifndef PM_QPARK_AUSTRALIA
#define PM_QPARK_AUSTRALIA 0    // Australia
#endif
#ifndef PM_QPARK_AUNSW
#define PM_QPARK_AUNSW 0    // Around UNSW
#endif
#ifndef PM_QPARK_ISLANDS
#define PM_QPARK_ISLANDS 0    // Islands
#endif
#ifndef PM_QPARK_SLITHERY
#define PM_QPARK_SLITHERY 0    // Slithery Fight
#endif
#ifndef PM_QPARK_TOWER
#define PM_QPARK_TOWER 0    // Tower Defense
#endif
#ifndef PM_QPARK_DEVIL
#define PM_QPARK_DEVIL 0    // Devil
#endif
#ifndef PM_QPARK_TROPHY
#define PM_QPARK_TROPHY 0    // Trophy
#endif
#ifndef PM_QPARK_AUTARKY
#define PM_QPARK_AUTARKY 0    // Autarky
#endif
#ifndef PM_QPARK_DILEMMA
#define PM_QPARK_DILEMMA 0    // Prisoners Dilemma
#endif
#ifndef PM_QPARK_QOS
#define PM_QPARK_QOS 0    // Queen Of Spades
#endif
#ifndef PM_QPARK_DEFAULT
#define PM_QPARK_DEFAULT 0    // Default
#endif
#ifndef PM_QPARK_STRIPES
#define PM_QPARK_STRIPES 0    // Stripes
#endif
#ifndef PM_QPARK_WEAKHOLD
#define PM_QPARK_WEAKHOLD 0    // weakhold
#endif
#ifndef PM_QPARK_TRAUMA
#define PM_QPARK_TRAUMA 0    // Trauma
#endif
#ifndef PM_QPARK_SCHOOLTIME
#define PM_QPARK_SCHOOLTIME 0    // Schooltime
#endif
#ifndef QPARK_UNK
#define QPARK_UNK 0           // unseen maps: generic park from the first turn the map is known to be unseen
#endif
#ifndef QPG_UNITS
#define QPG_UNITS 8           // flag value 2 (late park): she plays b1 until we have this many units...
#endif
#ifndef QPG_FROM
#define QPG_FROM 60           // ...or this round, then parks
#endif
#ifndef QPG_HOME
#define QPG_HOME 9            // the home block is searched within this many tiles (torus manhattan) of her spawn
#endif
#ifndef QPG_RAD
#define QPG_RAD 4             // she may roam this many walking steps (+ L/4) from the block before the pull starts
#endif
#ifndef QPG_PULL
#define QPG_PULL 25.0         // per step beyond the radius (before she is fed); PM_QP_PULL_FED once fed
#endif
#ifndef QPG_NARROW
#define QPG_NARROW 40.0       // step onto a 1-wide corridor tile or an enemy-half tile
#endif
#ifndef QPG_GCAP
#define QPG_GCAP 4            // distance to danger counts up to this
#endif
#ifndef QPG_WG
#define QPG_WG 3.0            // block score: per step of distance to danger
#endif
#ifndef QPG_WO
#define QPG_WO 1.5            // per block tile on fully open ground
#endif
#ifndef QPG_WH
#define QPG_WH 0.6            // per tile from her spawn
#endif
#ifndef QPG_WF
#define QPG_WF 8.0            // per pearl/round spawning within the roam radius (capped at 1.0)
#endif
#ifndef QPG_SAFE0
#define QPG_SAFE0 0           // 1 = QUEEN_SAFE rules from r0 (as on Portals); 0 = she keeps the early economy until QS_FROM (as on Maze)
#endif
#ifndef QPG_REPLAN_TO
#define QPG_REPLAN_TO 60      // unseen maps: the block is re-picked every QPG_REPLAN_EVERY rounds until this round
#endif
#ifndef QPG_REPLAN_EVERY
#define QPG_REPLAN_EVERY 6
#endif
#ifndef QPG_QKCAP
#define QPG_QKCAP 0           // feeders stop feeding the crowned queen at this length (0 = no cap)
#endif
#ifndef QPG_RESCUE_UNITS
#define QPG_RESCUE_UNITS 2    // with this few units (and fewer than when the park started) before the feed round she forages again (bans stay)
#endif
#ifndef QPG_CROWN
#define QPG_CROWN 1           // 1 = the parked queen is crowned at the seed round (RP.queenKing); 0 = park only, normal kings
#endif
#ifndef QPG_STAY
#define QPG_STAY 1            // 1 = bans and pull also after she is crowned
#endif

// QKILL_FUEL (Codex, 2026-10-04): the certain visible-queen kill search (tryQueenKill) also counts steps paid by
// visible pearls on the path (eating keeps length). Top teams fund ~25% of their queen kills this way.
// Ordinary rams, queen safety and the king gate are unchanged. Unit test: codex-battlecode/tests/queen_fuel_test.cpp
#ifndef QKILL_FUEL
#define QKILL_FUEL 0
#endif
#ifndef QK_FUEL_MAXLEN
#define QK_FUEL_MAXLEN 7      // only units up to this length extend the search
#endif
#ifndef QK_FUEL_EXTRA
#define QK_FUEL_EXTRA 4       // at most this many pearl-paid extra steps
#endif
