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
#define PM_TRA_KS 275
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
