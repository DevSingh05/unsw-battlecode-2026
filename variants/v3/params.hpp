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
