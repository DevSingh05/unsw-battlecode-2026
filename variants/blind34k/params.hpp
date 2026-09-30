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
#define NO_KNOWN_MAPS 1
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
