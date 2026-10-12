// MAINLINE (bot/) = b4 (2026-10-06): b3 + Tower Defense centre pull + Australia queen vault ban. New ideas = flags, default 0. Status: notes/STATUS.md
// v51: v44 + MATCH_STRICT-lite (unseen-map guard only: a starting dragon whose start fits no known map marks the map
// v51: v44 + MATCH_STRICT-lite (unseen-map guard only: a starting dragon whose start fits no known map marks the map
//      unseen for its team; official maps play exactly as v44; notes/newrules/UNSEEN_GENERALISATION.md section 10)
// v44: v43 + weakhold growth / Maze queen flags (notes/newrules/V44.md), all default 0 = v43
// v43: v41 + Maze/weakhold queen-survival flags (notes/newrules/V43.md)
// v41: v40 + FREE_STEPS (free multi-step path search, on; -DFREE_STEPS=0 = v40 behaviour)
// v40: v38q (QBOX, QGUARD) + v38s (Sprint maps known, SPRINT_ROUTE except weakhold)
// v38q: v38m + QBOX (boxed-queen trapped split, eat veto, late floor, unit reserve) + QGUARD on (small-region rule) + QSPLIT_ROOM port (off)
// v38m: v38 + maps_data with unswbc 1.2.6 map versions (old kept as *_old)
// UNSW Battlecode 2026 bot. (v38: v37d + UNK_SCARCE_FIX + UNK_PORTAL_EXPLORE + QALLY_KEEP (off), QGUARD off)
// Every dragon runs its own copy of this program. Each turn we read our 7x7
// view, update what we remember about the map, then pick a move by scoring
// each safe direction: pearls we can reach (time-aware BFS that knows when
// body segments will have moved away), room to manoeuvre, and enemy heads
// that could ram us.

#include "maps_data.hpp"
#include "params.hpp"

#include <algorithm>
#include <array>
#include <map>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <functional>
#include <iostream>
#include <string>
#include <vector>
#include <deque>
#include <cstdlib>
#include <chrono>

namespace {
FILE* dbg = nullptr;

// Sandbox clock: the judge's clock is virtual and advances with CPU points (100M points = 0.1 s),
// so milliseconds here are millions of points (notes/levers/budget-lookahead.md).
inline double pointsM()
{
    static const auto start = std::chrono::steady_clock::now();
    return std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - start).count();
}
#if PROFILE_POINTS
double profAcc[8]; // 0 parse, 1 analyse, 2 threats, 3 bfsFrom, 4 surviveDepth, 5 reply, 6 decide total, 7 sonar
#define PROF_BEGIN(k) const double prof_t0_##k = pointsM()
#define PROF_END(k, slot) profAcc[slot] += pointsM() - prof_t0_##k
#else
#define PROF_BEGIN(k)
#define PROF_END(k, slot)
#endif

// Strategy settings that can differ per map (see applyMapParams).
struct RuntimeParams
{
    int ramGuard = RAM_GUARD;
    int kingDeclare = KING_DECLARE;
    int kingSeedRound = KING_SEED_ROUND;
    int splitStopRound = SPLIT_STOP_ROUND;
    int feedStart = FEED_START;
    double crowd = CROWD_PENALTY;
    int keepLen = KEEP_LEN;          // dragons this long don't split (except peeling when much longer)
    int escapeHotOnly = ESCAPE_HOT_ONLY;
    int kingDeclareMinLen = KING_DECLARE_MINLEN;
    int lateFeedRound = LATE_FEED_ROUND;
    int feedReserve = FEED_RESERVE;
    double kingPortal = KING_PORTAL_PENALTY; // extra cost for a big dragon crossing a portal blind
    int kingKeepExtra = 0;                   // extra tiles a big dragon keeps from enemy heads
    int kingRace = 0;                        // set for the KING_V2 king-race maps (v2() table)
    int lateSplitRound = LATE_SPLIT_ROUND;   // small dragons keep splitting until this round (0 = off)
    int diveStopRound = 0;                   // no pocket dives from this round (0 = off)
    int queenKeep = 0;                       // R3 TROPHY_QSPLIT: >0 = while units <= this the queen has no split floor (splits at L4 like any unit)
    int mergeRound = KING_V2_MERGE_ROUND;    // R3 SPRINT_KING_PM: any-length feeding from this round (per-map on Sprint)
    int feed6Round = KING_V2_FEED6_ROUND;    // R7 PM_POR_EARLY: feeders up to L6 feed the king from this round
    int queenKeepR = TROPHY_QSPLIT_R;        // R7 PM_QOS_QSPLIT: queenKeep applies before this round
    int queenKing = 0;                       // ROUND3 P7: per-map QUEEN_KING (our queen is the only king from the seed round)
    int qPark = 0;                           // ROUND3 P7 PM_QPARK: 1 = Portals park (no portal crossing, home anchor), 2 = Maze home field
    int qpLate = 0;                          // ROUND4 QPARK_GEN: 1 = the generic park starts once we have QPG_UNITS units or at round QPG_FROM (b1 play before it)
    int qkCap = 0;                           // ROUND3 P7: feeders stop feeding the queen-king at this length (0 = no cap)
    int qkFrom = 0;                          // ROUND3 P7: the per-map queen-king starts at max(kingSeedRound, qkFrom)
    double crowdEarly = 0;                   // ROUND3 P7: crowd penalty used only while round < kingSeedRound (0 = off)
    int qSmall = 0;                          // R10 LANE_QSMALL: small home queen, never fed
#if QUAL_KNOWN
    int qParkIn = 0;                         // QUAL_QPARK_IN: the queen's process sets qPark = 1 once she has left her spawn's portal-free region
    int qHomeR = 0;                          // QUAL_QHOME: home leash radius for the queen (0 = off)
#endif
};
RuntimeParams RP;
static inline bool qkOn() { return QUEEN_KING || RP.queenKing; }

// QUAL_KNOWN: the 14 Qualifier maps (ranked pool since 10 Oct). The index is the bit in QUAL_KNOWN / QUAL_ROUTE / QUAL_QEKR.
static const char* const QUAL_MAPS[14] = {"Athena", "Atlantis", "Caution", "Detention", "Ezam", "Hive", "Maelstrom",
                                          "Metro", "Ouroboros", "Thermopylae", "Troll Australia", "Trolley Problem",
                                          "Trolley Problem (Buffed)", "Whale Song"};
int qualMapIndex(const char* name)
{
    std::string n(name ? name : "");
    for (int i = 0; i < 14; i++)
        if (n == QUAL_MAPS[i])
            return i;
    return -1;
}
// a Qualifier map whose QUAL_KNOWN bit is set (adopted and treated like a Sprint map)
bool qualKnown(const char* name)
{
    if (!(QUAL_KNOWN))
        return false; // flag off: folds away, no string work
    int i = qualMapIndex(name);
    return i >= 0 && ((QUAL_KNOWN) >> i & 1);
}

// Per-map overrides, keyed by the recognised map's name. Each value is a macro
// so local tests can flip one map at a time (e.g. -DPM_DEVIL_RG=0).
// SPRINT_KNOWN: the 7 Sprint maps (ranked pool since unswbc 1.2.7)
bool isSprintMap(const char* name)
{
    static const char* const S[] = {"Australia", "Islands", "Maze", "Stripes", "Tower Defense", "Around UNSW", "weakhold"};
    std::string n(name ? name : "");
    for (const char* s : S)
        if (n == s)
            return true;
    return false;
}

void applyMapParams(const char* name, int tiles = 0)
{
    RP = RuntimeParams{};
    std::string n(name ? name : "");
    if (LANE_QSMALL)
    {
        static const char* const LQ[] = {"Trophy", "Tower Defense", "Devil", "Prisoners Dilemma", "Autarky", "Queen Of Spades"};
        for (int i = 0; i < 6; i++)
            if ((LANE_QSMALL >> i & 1) && n == LQ[i])
                RP.qSmall = (LANE_QSM_LATE >> i & 1) ? 2 : 1; // R10: lane-map queen small and home (DEVTEST1 idea 4); 2 = late style
    }
    // ROUND4 QPARK_GEN: generic queen park + crown on one known map each (maps without a king get the unseen-map king timing)
    auto qgen = [&]() {
        static const struct { const char* map; int on; } G[] = {
            {"Australia", PM_QPARK_AUSTRALIA},
            {"Around UNSW", PM_QPARK_AUNSW},
            {"Islands", PM_QPARK_ISLANDS},
            {"Slithery Fight", PM_QPARK_SLITHERY},
            {"Tower Defense", PM_QPARK_TOWER},
            {"Devil", PM_QPARK_DEVIL},
            {"Trophy", PM_QPARK_TROPHY},
            {"Autarky", PM_QPARK_AUTARKY},
            {"Prisoners Dilemma", PM_QPARK_DILEMMA},
            {"Queen Of Spades", PM_QPARK_QOS},
            {"Default", PM_QPARK_DEFAULT},
            {"Stripes", PM_QPARK_STRIPES},
            {"weakhold", PM_QPARK_WEAKHOLD},
            {"Trauma", PM_QPARK_TRAUMA},
            {"Schooltime", PM_QPARK_SCHOOLTIME},
        };
        for (auto& g : G)
            if (g.on && n == g.map)
            {
                RP.queenKing = QPG_CROWN, RP.qPark = 3, RP.qkCap = QPG_QKCAP, RP.qpLate = g.on >= 2;
                if (!RP.kingDeclare)
                    RP.kingDeclare = 1, RP.kingSeedRound = UNK_KING_SEED, RP.feedStart = UNK_KING_FEED;
            }
    };
    // R8 CROWD_MAPS (DEVTEST1 fix 1A): crowd penalty on the maps where allies box each other in
    auto crowdMaps = [&]() {
        if (!CROWD_MAPS)
            return;
        if (((CROWD_MAPS & 1) && n == "Around UNSW") || ((CROWD_MAPS & 2) && n == "Australia") ||
            ((CROWD_MAPS & 4) && n == "Devil") || ((CROWD_MAPS & 8) && n == "Tower Defense"))
            RP.crowd = CROWD_MAPS_V;
        if ((CROWD_MAPS & 16) && n == "Schooltime")
            RP.crowd = CROWD_MAPS_SCH;
    };
    if ((SPRINT_KNOWN && isSprintMap(name)) || qualKnown(name))
    {
        // same high-level params the unknown-map path (UNK_KING / UNK_SMALL_RAMGUARD) gave them in v38m
        if (UNK_KING)
        {
            RP.kingDeclare = 1;
            RP.kingSeedRound = UNK_KING_SEED;
            RP.feedStart = UNK_KING_FEED;
            // R3 SPRINT_KING_PM (from variants/v70): earlier king seed / feed on the big Sprint maps where we lose the longest race
            if (SPRINT_KING_PM)
            {
                if (n == "Around UNSW") RP.kingSeedRound = PM_AUNSW_SEED, RP.feedStart = PM_AUNSW_FEED, RP.mergeRound = PM_AUNSW_MERGE;
                if (n == "Islands") RP.kingSeedRound = PM_ISL_SEED, RP.feedStart = PM_ISL_FEED, RP.mergeRound = PM_ISL_MERGE;
                if (n == "Australia") RP.kingSeedRound = PM_AUS_SEED, RP.feedStart = PM_AUS_FEED, RP.mergeRound = PM_AUS_MERGE;
            }
        }
        if (UNK_SMALL_RAMGUARD && tiles > 0 && tiles <= 750)
            RP.ramGuard = 2;
        if (n == "Maze")
        {
            // ROUND3 P7: Maze queen stays in the home field and is crowned; crowd penalty until the seed round
            if (PM_QPARK_MAZE)
                RP.queenKing = 1, RP.qPark = 2, RP.qkFrom = PM_MAZE_QKFROM, RP.qkCap = PM_MAZE_QKCAP;
            if (PM_MAZE_CR > 0 || (PM_MAZE_CR < 0 && PM_QPARK_MAZE))
                RP.crowdEarly = PM_MAZE_CR > 0 ? PM_MAZE_CR : PM_MAZE_CR_AUTO;
        }
        qgen();
        crowdMaps();
#if QUAL_KNOWN
        if (int qi = qualMapIndex(name); qi >= 0 && ((QUAL_CROWD) >> qi & 1))
            RP.crowd = QUAL_CROWD_V; // QUAL_CROWD: spread the swarm on this known Qualifier map
        if (int qi = qualMapIndex(name); qi >= 0 && ((QUAL_QPARK) >> qi & 1))
        {
            RP.queenKing = 1, RP.qPark = 1, RP.qkFrom = QUAL_QPARK_QKFROM, RP.qkCap = QUAL_QPARK_QKCAP; // QUAL_QPARK: parked queen, crowned at the seed round
            if ((QUAL_QPARK_IN) >> qi & 1)
                RP.qPark = 0, RP.qParkIn = 1; // QUAL_QPARK_IN: she plays on until she is through a portal (qparkPrep)
            if (QUAL_QPARK_SEED > 0)
                RP.kingDeclare = 1, RP.kingSeedRound = QUAL_QPARK_SEED;
            if (QUAL_QPARK_FEED > 0)
                RP.feedStart = QUAL_QPARK_FEED;
        }
        if (int qi = qualMapIndex(name); qi >= 0 && ((QUAL_QHOME) >> qi & 1))
            RP.qHomeR = QUAL_QHOME_R; // QUAL_QHOME: the queen forages near her spawn
#endif
        return;
    }
    auto set = [&](const char* map, int rg, int kd, int ks, int ss, int fs) {
        if (n == map)
        {
            if (rg >= 0) RP.ramGuard = rg;
            if (kd >= 0) RP.kingDeclare = kd;
            if (ks >= 0) RP.kingSeedRound = ks;
            if (ss >= 0) RP.splitStopRound = ss;
            if (fs >= 0) RP.feedStart = fs;
        }
    };
    //   map                 ram guard      king declare   seed round     split stop     feed start
    set("Devil",             PM_DEVIL_RG,   PM_DEVIL_KD,   PM_DEVIL_KS,   PM_DEVIL_SS,   PM_DEVIL_FS);
    set("Trophy",            PM_TROPHY_RG,  PM_TROPHY_KD,  PM_TROPHY_KS,  PM_TROPHY_SS,  PM_TROPHY_FS);
    set("Queen Of Spades",   PM_QOS_RG,     PM_QOS_KD,     PM_QOS_KS,     PM_QOS_SS,     PM_QOS_FS);
    set("Prisoners Dilemma", PM_DIL_RG,     PM_DIL_KD,     PM_DIL_KS,     PM_DIL_SS,     PM_DIL_FS);
    set("Default",           PM_DEF_RG,     PM_DEF_KD,     PM_DEF_KS,     PM_DEF_SS,     PM_DEF_FS);
    set("Autarky",           PM_AUT_RG,     PM_AUT_KD,     PM_AUT_KS,     PM_AUT_SS,     PM_AUT_FS);
    set("Schooltime",        PM_SCH_RG,     PM_SCH_KD,     PM_SCH_KS,     PM_SCH_SS,     PM_SCH_FS);
    set("Slithery Fight",    PM_SLI_RG,     PM_SLI_KD,     PM_SLI_KS,     PM_SLI_SS,     PM_SLI_FS);
    set("Trauma",            PM_TRA_RG,     PM_TRA_KD,     PM_TRA_KS,     PM_TRA_SS,     PM_TRA_FS);
    set("Portals",           PM_POR_RG,     PM_POR_KD,     PM_POR_KS,     PM_POR_SS,     PM_POR_FS);
    // crowding penalty per map (negative = use the global default)
    auto crowd = [&](const char* map, double v) {
        if (n == map && v >= 0)
            RP.crowd = v;
    };
    crowd("Queen Of Spades", PM_QOS_CR);
    crowd("Portals", PM_POR_CR);
    crowd("Trauma", PM_TRA_CR);
    crowd("Schooltime", PM_SCH_CR);
    crowd("Default", PM_DEF_CR);
    crowd("Slithery Fight", PM_SLI_CR);
    crowdMaps();
    if (KING_V2)
    {
        // notes/11: top-10 king timing on the big maps
        //                 map               seed  splitStop feed  reserve
        auto v2 = [&](const char* map, int ks, int ss, int fs, int res) {
            if (n == map)
            {
                RP.kingRace = 1;
                RP.kingDeclare = 1;
                RP.kingSeedRound = ks;
                RP.splitStopRound = ss;
                RP.feedStart = fs;
                RP.feedReserve = res;
            }
        };
        v2("Schooltime", 200, 340, 260, KING_V2_RES_BIG);
        v2("Slithery Fight", 170, 370, 250, KING_V2_RES_BIG);
        v2("Portals", 250, 360, 300, 3);
        v2("Queen Of Spades", 330, 420, 400, 4);
        if (n == "Schooltime")
        {
            if (PM_SCH_KPORTAL >= 0)
                RP.kingPortal = PM_SCH_KPORTAL;
            if (PM_SCH_KKEEP >= 0)
                RP.kingKeepExtra = PM_SCH_KKEEP;
        }
    }
    if (TROPHY_QSPLIT && n == "Trophy")
        RP.queenKeep = TROPHY_QSPLIT_UNITS; // R3: Trophy queen split floor off while we are few (ROUND2 backlog)
    if (PM_QOS_QSPLIT && n == "Queen Of Spades")
        RP.queenKeep = PM_QOS_QSPLIT_UNITS, RP.queenKeepR = PM_QOS_QSPLIT_R; // R7: QoS queen splits at L4 early (Vibing++ splits ~r10)
    if (PM_POR_EARLY && n == "Portals")
    {
        // R7: crown and feed the parked Portals queen earlier (Vibing++ queen L32 at r300; ours L3)
        RP.kingSeedRound = PM_POR_EARLY_KS, RP.feedStart = PM_POR_EARLY_FS, RP.splitStopRound = PM_POR_EARLY_SS;
        if (PM_POR_EARLY_F6 > 0) RP.feed6Round = PM_POR_EARLY_F6;
        if (PM_POR_EARLY_MERGE > 0) RP.mergeRound = PM_POR_EARLY_MERGE;
    }
    if (n == "Portals" && PM_POR_KPORTAL >= 0)
        RP.kingPortal = PM_POR_KPORTAL; // the Portals module routes the king through portals on purpose
    if (n == "Portals" && PM_POR_LATESPLIT >= 0)
        RP.lateSplitRound = PM_POR_LATESPLIT; // notes/portals_v31: no contact on Portals, consolidate
    if (n == "Portals" && PM_POR_DIVESTOP > 0)
        RP.diveStopRound = PM_POR_DIVESTOP;
    if (n == "Portals" && PM_QPARK_PORTALS)
        RP.queenKing = 1, RP.qPark = 1, RP.qkFrom = PM_POR_QKFROM, RP.qkCap = PM_POR_QKCAP; // ROUND3 P7: parked queen, crowned at the seed round
    if ((RAM_GUARD_LOCAL == 1 && (n == "Devil" || n == "Prisoners Dilemma")) || RAM_GUARD_LOCAL == 2)
        RP.ramGuard = 2; // notes/19: local odds only
    if (n == "Prisoners Dilemma" && PM_DIL_KEEP >= 0)
        RP.keepLen = PM_DIL_KEEP;
    if (n == "Trauma" && PM_TRA_LATEFEED >= 0)
        RP.lateFeedRound = PM_TRA_LATEFEED;
    // notes/top3/PLAN.txt A: on king maps the top teams stop splitting ~r330 and consolidate
    if (LATE_SPLIT_KING_MAPS > 0 && RP.kingRace && RP.lateSplitRound > LATE_SPLIT_KING_MAPS)
        RP.lateSplitRound = LATE_SPLIT_KING_MAPS;
    qgen();
}

constexpr int INF = 1 << 29;
constexpr int R = 3;  // vision radius
constexpr int VS = 7; // vision size
constexpr char DIRC[4] = {'N', 'E', 'S', 'W'};
constexpr int DX[4] = {0, 1, 0, -1};
constexpr int DY[4] = {-1, 0, 1, 0};

int dirIndex(char c)
{
    switch (c)
    {
    case 'N': return 0;
    case 'E': return 1;
    case 'S': return 2;
    default: return 3;
    }
}

// ---------------------------------------------------------------- RNG
struct Rng
{
    uint64_t s;
    explicit Rng(uint64_t seed) : s(seed * 0x9E3779B97F4A7C15ULL + 12345) {}
    uint64_t next()
    {
        s ^= s << 13;
        s ^= s >> 7;
        s ^= s << 17;
        return s;
    }
    double uni() { return (next() >> 11) * (1.0 / 9007199254740992.0); }
};

// ---------------------------------------------------------------- input
struct Part
{
    char team;
    int id, x, y, facing;
    bool head;
};

struct TurnInput
{
    int round = 0, dir = 0, length = 0, units = 0;
    std::vector<uint64_t> msgs;
    int echoes[5] = {0, 0, 0, 0, 0};
    bool echoesLine = false; // MATCH_STRICT: a starting dragon's first turn has no ECHOES line (protocol 2)
    int tx[49], ty[49], tpearl[49], tin[49];
    std::vector<Part> parts;
    std::string hEdges[8][7];
    std::string vEdges[7][8];
};

bool readToken(std::string& out) { return static_cast<bool>(std::cin >> out); }
bool readInt(long long& v)
{
    std::string t;
    if (!readToken(t))
        return false;
    v = std::strtoll(t.c_str(), nullptr, 10);
    return true;
}

// Returns false at end of game.
bool readTurn(TurnInput& in)
{
    std::string tok;
    long long v;
    if (!readToken(tok) || tok != "ROUND")
        return false;
    readInt(v);
    in.round = static_cast<int>(v);
    readToken(tok); // DIR
    readToken(tok);
    in.dir = dirIndex(tok[0]);
    readToken(tok);
    readInt(v);
    in.length = static_cast<int>(v);
    readToken(tok);
    readInt(v);
    in.units = static_cast<int>(v);
    readToken(tok); // NUM_MSGS
    readInt(v);
    in.msgs.clear();
    for (long long i = 0; i < v; i++)
    {
        readToken(tok);
        in.msgs.push_back(std::strtoull(tok.c_str(), nullptr, 10));
    }
    readToken(tok);
    for (int& e : in.echoes)
        e = 0;
    in.echoesLine = tok == "ECHOES";
    if (tok == "ECHOES")
    {
        for (int& e : in.echoes)
        {
            readInt(v);
            e = static_cast<int>(v);
        }
        readToken(tok);
    }
    for (int i = 0; i < 49; i++)
    {
        if (i > 0)
            readToken(tok);
        in.tx[i] = std::atoi(tok.c_str());
        readInt(v);
        in.ty[i] = static_cast<int>(v);
        readInt(v);
        in.tpearl[i] = static_cast<int>(v);
        readInt(v);
        in.tin[i] = static_cast<int>(v);
    }
    readToken(tok); // DRAGON_BODIES
    long long nparts = 0;
    readInt(nparts);
    in.parts.clear();
    for (long long i = 0; i < nparts; i++)
    {
        Part p;
        readToken(tok);
        p.team = tok[0];
        readInt(v);
        p.id = static_cast<int>(v);
        long long x, y;
        readInt(x);
        readInt(y);
        p.x = static_cast<int>(x);
        p.y = static_cast<int>(y);
        readToken(tok);
        p.facing = dirIndex(tok[0]);
        readInt(v);
        p.head = v == 1;
        in.parts.push_back(p);
    }
    for (auto& row : in.hEdges)
        for (auto& e : row)
            readToken(e);
    for (auto& row : in.vEdges)
        for (auto& e : row)
            readToken(e);
    return static_cast<bool>(std::cin);
}

// ---------------------------------------------------------------- world model
struct World
{
    int W = 0, H = 0, N = 0;
    int unitLimit = 64;
    int myId = 0;
    char myTeam = 'A';
    int sym = -1; // 0 none, 1 x, 2 y, 3 xy, -1 unknown
    const KnownMap* known = nullptr;
    std::vector<int> candidates; // indices into KNOWN_MAPS still consistent
    // FRAME_FIX: did the server swap the teams' start positions vs the map file?
    int swapState = -1;     // -1 unknown, 0 as in the file, 1 swapped
    bool swapKnown = false; // learned from our own start or an ally's sonar (not a guess)

    std::vector<int> nxt;        // N*4, -1 blocked
    std::vector<int> gmin, gmax; // gap range, gmax 0 = never spawns, -1 unknown

    // memory
    std::vector<int> lastSeen;  // round, -1 never
    std::vector<char> pearlMem; // pearl present when last seen
    std::vector<int> spawnAt;   // absolute round a spawn will be attempted, -1 unknown

    int idx(int x, int y) const { return y * W + x; }
    int wrapX(int x) const { return ((x % W) + W) % W; }
    int wrapY(int y) const { return ((y % H) + H) % H; }
    int plainStep(int t, int d) const { return idx(wrapX(t % W + DX[d]), wrapY(t / W + DY[d])); }

    int mirror(int t) const
    {
        int x = t % W, y = t / W;
        switch (sym)
        {
        case 1: return idx(x, H - 1 - y);
        case 2: return idx(W - 1 - x, y);
        case 3: return idx(W - 1 - x, H - 1 - y);
        default: return -1;
        }
    }

    void init(int w, int h)
    {
        W = w;
        H = h;
        N = w * h;
        nxt.assign(N * 4, 0);
        for (int t = 0; t < N; t++)
            for (int d = 0; d < 4; d++)
                nxt[t * 4 + d] = plainStep(t, d);
        gmin.assign(N, -1);
        gmax.assign(N, -1);
        lastSeen.assign(N, -1);
        pearlMem.assign(N, 0);
        spawnAt.assign(N, -1);
        for (int i = 0; i < KNOWN_MAP_COUNT; i++)
            if (!NO_KNOWN_MAPS && KNOWN_MAPS[i].w == w && KNOWN_MAPS[i].h == h &&
                (SPRINT_KNOWN || !isSprintMap(KNOWN_MAPS[i].name)) &&
                (i < KNOWN_MAP_COUNT - 14 || ((QUAL_KNOWN) >> (i - (KNOWN_MAP_COUNT - 14)) & 1))) // QUAL_KNOWN: the 14 Qualifier maps are the last entries (QUAL_MAPS order); candidates only with their bit set
                candidates.push_back(i);
    }

    // QUAL_KNOWN: index of the adopted map in QUAL_MAPS when its QUAL_KNOWN bit is set, else -1. Set by adopt(); read
    // only while known != nullptr. Cached so the per-turn hooks cost an int test, not string compares (the search
    // budgets run on the CPU-points clock, so extra work per turn shifts decisions on every map).
    int qualIdx = -1;
    bool qualTold = false; // QUAL_GOSSIP: an ally that was sure named this map
    bool qualOn() const { return (QUAL_KNOWN) && known && qualIdx >= 0; }
    bool qualOn(int mask) const { return (QUAL_KNOWN) && known && qualIdx >= 0 && (mask >> qualIdx & 1); }
    void adopt(const KnownMap* m)
    {
        known = m;
#if QUAL_KNOWN
        qualIdx = qualKnown(m->name) ? qualMapIndex(m->name) : -1;
#endif
        everKnown = true; // QF1: sticky, never cleared (a later drop or MATCH_STRICT reset keeps it)
        applyMapParams(m->name, m->w * m->h);
        sym = m->sym;
#if SPRINT_DEBUG
        std::fprintf(stderr, "ADOPT %s id=%d team=%c\n", m->name, myId, myTeam);
#endif
        for (int i = 0; i < N * 4; i++)
            nxt[i] = m->nxt[i];
        for (int t = 0; t < N; t++)
        {
            gmin[t] = m->gmin[t];
            gmax[t] = m->gmax[t];
        }
    }

    // Edge letter seen in vision: '.', 'w', or a portal id.
    static int edgeKind(const std::string& s) { return s == "." ? 0 : s == "w" ? 1 : 2; }

    // ---- unknown-map learning: portal pairs share an id; once both ends are
    // seen we know exactly where crossing leads.
    std::vector<std::pair<int, std::vector<int>>> portalSeen; // id -> canonical edges (tile*2 + 0 horiz / 1 vert)
    std::vector<int> gapSeen;                                  // largest countdown+1 seen per tile
    std::vector<char> portalSide;                              // tile*4+dir is a portal edge (unknown maps)
    bool pearlDistrust = false;                                // built-in pearl gaps contradicted by what we see
    // MATCH_STRICT (v51): msDead = this process treats the map as unseen for good (no known-map adoption)
    bool msDead = false;
    // QF1 (8 Oct, Qualifier build): sticky per-process "never identified" bit. everKnown = a known map was adopted at
    // any time (adopt(); split children that adopt the map count too). nkBirth = decided once, at the end of the
    // process's first turn of identification: no known map and no candidate left (the INFER_SYM / NO_KNOWN_MAPS rule).
    // Live !known is NOT used: it flips mid-game on known maps (Schooltime layout B door edges drop the map).
    bool everKnown = false;
    int nkBirth = -1; // -1 = first turn not finished yet
    bool neverKnown() const { return !everKnown && (nkBirth < 0 ? (!known && candidates.empty()) : nkBirth == 1); }
    void msMarkUnseen()
    {
        if (known)
        {
            // same reset as a wall contradiction
            known = nullptr;
            sym = -1;
            for (int t = 0; t < N; t++)
                for (int d = 0; d < 4; d++)
                    nxt[t * 4 + d] = plainStep(t, d);
            std::fill(gmin.begin(), gmin.end(), -1);
            std::fill(gmax.begin(), gmax.end(), -1);
        }
        candidates.clear();
        msDead = true;
    }
    int pearlContradictions = 0;
    int canonEdge(int t, int d) const
    {
        switch (d)
        {
        case 0: return t * 2 + 0;
        case 2: return plainStep(t, 2) * 2 + 0;
        case 3: return t * 2 + 1;
        default: return plainStep(t, 1) * 2 + 1;
        }
    }
    void linkPortal(int e1, int e2)
    {
        auto link = [&](int a, int b, bool horiz) {
            if (horiz)
            {
                nxt[a * 4 + 0] = plainStep(b, 0);          // crossing north from a
                nxt[plainStep(a, 0) * 4 + 2] = b;          // crossing south into a's edge
            }
            else
            {
                nxt[a * 4 + 3] = plainStep(b, 3);          // crossing west from a
                nxt[plainStep(a, 3) * 4 + 1] = b;          // crossing east into a's edge
            }
        };
        if ((e1 & 1) != (e2 & 1))
            return;
        link(e1 / 2, e2 / 2, (e1 & 1) == 0);
        link(e2 / 2, e1 / 2, (e1 & 1) == 0);
    }
    // UNK_SCARCE_FIX (notes/qualifier/SCARCE_PORTAL.md): pairs are always recorded; they are linked into
    // nxt (walkable) only once portalUse is on (LEARN_PORTALS behaviour from then on)
    bool portalUse = false;
    bool portalLearnOn() const { return LEARN_PORTALS || portalUse; }
    void enablePortalUse()
    {
        portalUse = true;
        for (auto& [id, edges] : portalSeen)
            if (edges.size() == 2)
                linkPortal(edges[0], edges[1]);
    }
    void notePortal(int t, int d, int pid)
    {
        int e = canonEdge(t, d);
        for (auto& [id, edges] : portalSeen)
            if (id == pid)
            {
                if (std::find(edges.begin(), edges.end(), e) == edges.end())
                    edges.push_back(e);
                if (edges.size() == 2 && portalLearnOn())
                    linkPortal(edges[0], edges[1]);
                return;
            }
        portalSeen.push_back({pid, {e}});
    }
    // ---- unknown maps: work out the map's symmetry from walls we've seen, then
    // mirror every wall we learn (each observation also teaches us the far side).
    std::vector<signed char> edgeObs; // tile*4+dir -> -1 unknown, 0 open, 1 kelp, 2 portal
    int symBad[4] = {0, 0, 0, 0}, symGood[4] = {0, 0, 0, 0};
    int mirrorTileAs(int t, int sy) const
    {
        int x = t % W, y = t / W;
        if (sy == 1) return idx(x, H - 1 - y);
        if (sy == 2) return idx(W - 1 - x, y);
        return idx(W - 1 - x, H - 1 - y);
    }
    static int mirrorDirAs(int d, int sy)
    {
        bool flipNS = sy == 1 || sy == 3, flipEW = sy == 2 || sy == 3;
        if ((d == 0 || d == 2) && flipNS) return d ^ 2;
        if ((d == 1 || d == 3) && flipEW) return d ^ 2;
        return d;
    }
    void inferSymmetry(const std::vector<std::pair<int, int>>& obs)
    {
        if (edgeObs.size() != nxt.size())
            edgeObs.assign(nxt.size(), -1);
        for (auto& [td, k] : obs)
            edgeObs[td] = static_cast<signed char>(k);
        if (sym < 0)
        {
            // score each candidate on the walls we've seen from both mirrored sides
            for (auto& [td, k] : obs)
            {
                int t = td / 4, d = td % 4;
                for (int sy = 1; sy <= 3; sy++)
                {
                    int mt = mirrorTileAs(t, sy), md = mirrorDirAs(d, sy);
                    int other = edgeObs[mt * 4 + md];
                    if (other < 0 || (mt == t && md == d))
                        continue;
                    if (other != k)
                        symBad[sy]++;
                    else if (k != 0)
                        symGood[sy]++;
                }
            }
            int alive = 0, pick = -1;
            for (int sy = 1; sy <= 3; sy++)
                if (symBad[sy] == 0)
                {
                    alive++;
                    pick = sy;
                }
            if (alive == 1 && symGood[pick] >= INFER_SYM_MIN)
            {
                sym = pick;
                if (dbg)
                    std::fprintf(dbg, "SYMINFER %d good=%d bad=%d,%d,%d\n", sym, symGood[pick], symBad[1], symBad[2], symBad[3]);
            }
        }
        if (sym > 0)
        {
            // copy what we know onto the mirrored edges we haven't seen yet
            for (int td = 0; td < static_cast<int>(edgeObs.size()); td++)
            {
                int k = edgeObs[td];
                if (k < 0)
                    continue;
                int mt = mirrorTileAs(td / 4, sym), md = mirrorDirAs(td % 4, sym);
                int m = mt * 4 + md;
                if (edgeObs[m] >= 0)
                    continue;
                if (k == 0)
                    nxt[m] = plainStep(mt, md);
                else
                    nxt[m] = -1;
            }
        }
    }

    bool portalKnown(int t, int d) const
    {
        int e = canonEdge(t, d);
        for (auto& [id, edges] : portalSeen)
            if (edges.size() == 2 && (edges[0] == e || edges[1] == e))
                return true;
        return false;
    }

    // DGU F6 SCH_DOORS: Schooltime layout B opens 4 kelp edges of layout A (the side-room chamber doors at y30)
    static bool schDoor(const KnownMap& m, int W, int t, int d)
    {
        if (!SCH_DOORS || (d != 1 && d != 3) || W != 60 || t / W != 30 || m.h != 40)
            return false;
        int xe = d == 1 ? t % W : t % W - 1; // the tile west of the edge
        if (xe != 4 && xe != 15 && xe != 43 && xe != 54)
            return false;
        return std::strcmp(m.name, "Schooltime") == 0;
    }
    bool schDoorKelp = false; // DGU F6: a door edge was seen as kelp: never open the doors again
    void schOpenDoors()
    {
        if (schDoorKelp)
            return;
        for (int x : {4, 15, 43, 54})
        {
            int a = idx(x, 30), b = idx(x + 1, 30);
            nxt[a * 4 + 1] = b;
            nxt[b * 4 + 3] = a;
        }
    }

    // Tile t, side d has edge kind k. Check it against a known map.
    static bool consistent(const KnownMap& m, int W, int t, int d, int k)
    {
        if (k == 0 && schDoor(m, W, t, d))
            return true; // DGU F6 SCH_DOORS: an open door fits Schooltime (layout B)
        int v = m.nxt[t * 4 + d];
        int x = t % W, y = t / W;
        int H = m.h;
        int plain = ((y + DY[d] + H) % H) * W + ((x + DX[d] + W) % W);
        if (k == 1)
            return v == -1;
        if (k == 0)
            return v == plain;
        if (CONSIST_PORTAL)
            return v != -1 && v != plain; // a portal never fits a plain edge
        return v != -1; // portal: goes somewhere (maybe the plain tile by coincidence)
    }

    // Apply the visible edges: filter candidate maps, learn edges if unknown.
    void observeEdges(const TurnInput& in, int headX, int headY)
    {
        auto tileAt = [&](int col, int row) { return idx(wrapX(headX + col - R), wrapY(headY + row - R)); };
        std::vector<std::pair<int, int>> obs; // (tile*4+dir, kind)
        std::vector<std::pair<int, int>> portalObs; // (tile*4+dir, portal id)
        for (int row = 0; row <= VS; row++)
            for (int col = 0; col < VS; col++)
            {
                int k = edgeKind(in.hEdges[row][col]);
                if (row < VS)
                    obs.push_back({tileAt(col, row) * 4 + 0, k});
                if (row > 0)
                    obs.push_back({tileAt(col, row - 1) * 4 + 2, k});
                if (k == 2)
                    portalObs.push_back({(row < VS ? tileAt(col, row) * 4 + 0 : tileAt(col, row - 1) * 4 + 2),
                                         std::atoi(in.hEdges[row][col].c_str())});
            }
        for (int row = 0; row < VS; row++)
            for (int col = 0; col <= VS; col++)
            {
                int k = edgeKind(in.vEdges[row][col]);
                if (col < VS)
                    obs.push_back({tileAt(col, row) * 4 + 3, k});
                if (col > 0)
                    obs.push_back({tileAt(col - 1, row) * 4 + 1, k});
                if (k == 2)
                    portalObs.push_back({(col < VS ? tileAt(col, row) * 4 + 3 : tileAt(col - 1, row) * 4 + 1),
                                         std::atoi(in.vEdges[row][col].c_str())});
            }
        if (!candidates.empty())
        {
            std::vector<int> keep;
            for (int c : candidates)
            {
                bool ok = true;
                for (auto& [td, k] : obs)
                    if (!consistent(KNOWN_MAPS[c], W, td / 4, td % 4, k))
                    {
                        ok = false;
                        break;
                    }
                if (ok)
                    keep.push_back(c);
            }
            candidates.swap(keep);
            if (known && (candidates.empty() ||
                          std::find_if(candidates.begin(), candidates.end(),
                                       [&](int c) { return &KNOWN_MAPS[c] == known; }) == candidates.end()))
            {
                // Our map guess was wrong: fall back to learning.
#if SPRINT_DEBUG
                std::fprintf(stderr, "DROP %s id=%d team=%c\n", known->name, myId, myTeam);
#endif
                known = nullptr;
                sym = -1;
                for (int t = 0; t < N; t++)
                    for (int d = 0; d < 4; d++)
                        nxt[t * 4 + d] = plainStep(t, d);
                std::fill(gmin.begin(), gmin.end(), -1);
                std::fill(gmax.begin(), gmax.end(), -1);
            }
            if (!known && !candidates.empty())
                adopt(&KNOWN_MAPS[candidates.front()]);
            if (SCH_DOORS && known)
            {
                bool open = false;
                for (auto& [td, k] : obs)
                    if (schDoor(*known, W, td / 4, td % 4))
                    {
                        if (k == 0)
                            open = true;
                        else if (k == 1 && !schDoorKelp)
                        {
                            // a door seen closed (layout A, or a B map without the doors): close all 4 for good
                            for (int x : {4, 15, 43, 54})
                            {
                                int a = idx(x, 30), b = idx(x + 1, 30);
                                nxt[a * 4 + 1] = -1;
                                nxt[b * 4 + 3] = -1;
                            }
                            schDoorKelp = true;
                        }
                    }
                if (open)
                    schOpenDoors(); // DGU F6 SCH_DOORS: a door seen open = layout B
            }
        }
        if (!known)
        {
            for (auto& [td, k] : obs)
            {
                int t = td / 4, d = td % 4;
                if (k == 0)
                    nxt[td] = plainStep(t, d);
                else if (k == 1 || !portalLearnOn() || !portalKnown(t, d))
                    nxt[td] = -1; // kelp, or a portal whose far side we don't know yet
            }
            if (LEARN_PORTALS || UNK_SCARCE_FIX || UNK_PORTAL_EXPLORE)
                for (auto& [td, pid] : portalObs)
                    notePortal(td / 4, td % 4, pid);
            if (portalSide.size() != nxt.size())
                portalSide.assign(nxt.size(), 0);
            for (auto& [td, pid] : portalObs)
            {
                portalSide[td] = 1;
                if (UNK_PORTAL_SIDES == 1 || (UNK_PORTAL_SIDES >= 2 && neverKnown())) // the edge is a portal from its other side too (Codex); 2 = never-identified maps only (QF1)
                    portalSide[plainStep(td / 4, td % 4) * 4 + (td % 4 + 2) % 4] = 1;
            }
            if (INFER_SYM)
                inferSymmetry(obs);
        }
    }

    // Identify the map from our starting position (only works for original dragons).
    void identifyByStart(int headX, int headY)
    {
        for (int c : candidates)
        {
            const KnownMap& m = KNOWN_MAPS[c];
            if (myId >= m.dragonCount)
                continue;
            const int16_t* d = m.dragons + myId * 4;
            char team = d[0] == 0 ? 'A' : 'B';
            if ((team == myTeam || FRAME_FIX) && d[2] == headX && d[3] == headY)
            {
                if (FRAME_FIX)
                {
                    swapState = team != myTeam;
                    swapKnown = true;
                }
                // Prefer this candidate by moving it to the front.
                std::vector<int> keep{c};
                for (int o : candidates)
                    if (o != c)
                        keep.push_back(o);
                candidates.swap(keep);
                adopt(&m);
                return;
            }
        }
    }

    double rate(int t) const
    {
        if (gmax[t] == 0)
            return 0;
        if (gmax[t] < 0)
        {
            // unknown map: estimate from the largest countdown we've seen here
            if ((LEARN_GAPS || pearlDistrust) && !gapSeen.empty() && gapSeen[t] > 0)
                return 1.0 / std::max(1.0, 0.75 * gapSeen[t]);
            if (pearlDistrust)
                return DISTRUST_PRIOR; // unseen tile on a distrusted map: assume a typical rate so we still explore
            return UNK_PRIOR;
        }
        return 2.0 / (gmin[t] + gmax[t]);
    }
};

// ---------------------------------------------------------------- per-turn analysis
struct Seg
{
    int tile, id;
    char team;
    int facing;
    bool head;
};

struct Bot
{
    World w;
    Rng rng{1};
    TurnInput in;
    int round = 0, myLen = 0, units = 0, myDir = 0;
    int myHead = -1;
    std::vector<char> visible;  // tile in current vision
    std::vector<int> freeT;     // step index at which the tile can be entered (1 = now)
    std::vector<int> occId;     // dragon id on tile now, -1 none
    std::vector<char> occTeam;  // team on tile
    std::vector<char> occHead;  // head on tile
    std::vector<int> otherDist; // BFS distance from nearest other head
    std::vector<Seg> segs;
    std::vector<int> segAt;     // tile -> index into segs, -1
    std::string out;
    bool unkKingSet = false;
    int birthRound = -1; // first round this process played
    std::vector<int> headSeen; // REVISIT_PEN: last round our head was on each tile
    std::vector<int> hotRun, hotLast; // HOT_LEARN
    // EXPLORE_LEARN: decayed first-sight samples (hits, total) -> value of a never-seen tile
    double exploreHits = 0, exploreN = 0;
    double exploreEst() const
    {
        double e = (exploreHits + EXPLORE_N0 * EXPLORE_M0) / (exploreN + EXPLORE_N0);
        return std::min(EXPLORE_MAX, EXPLORE_MULT * e);
    }
    // UNK_EXPLORE (notes/unseen/unknown-portals.md): knock on unknown portals, cross on a clean echo
    std::vector<int> learnDest, edgeCrossRound; // N*4; learned by crossing, never copied into w.nxt
    std::vector<char> lureTile;
    int lastGrowRound = -1, prevLen = 0;
    int exploreFrom = -1, exploreDir = -1, exploreRound = -100;
    int unkEchoRound = -100, unkEchoTile = -1, unkEchoMask = 0;
    bool unkEchoClean = false, exploreDesire = false;
    bool unkParamsSet = false; // generic settings chosen for an unseen map
    std::vector<std::pair<int, int>> allyHeadMemory; // (tile, round) of ally heads seen lately
    int lastMoveDir = 0;
    int lastPortalRound = -100;                       // last round we stepped through a portal
    std::vector<int> trail;    // our body, head first (tracked across turns)
    std::vector<int> freeOther; // like freeT but ignoring our own body
    std::vector<int> bodyCnt;   // survival search: our simulated body
    std::vector<int> simBody;   // ring buffer
    std::vector<char> eatenMark; // survival search: pearls eaten on this path
    long long nodes = 0;
    std::map<int, std::array<int, 3>> qkTrend; // ROUND6 QK_EG_TREND: enemy id -> {round seen, distance, closing streak}
    bool survQBan = false;       // ROUND6 QK_SURV: surviveDepth skips qparkBan steps
    bool inFreePath = false;     // ROUND6 QK_SURV: evalDir is scoring a free-path node (smaller node cap)
    long long nodeCap = 60000;   // surviveDepth node limit (REPLY_SEARCH lowers it for its re-runs)
    std::vector<char> replyBan;  // REPLY_SEARCH: tiles our 2nd step may not enter (replied heads reach them)
    bool replyBanOn = false;
    double turnT0 = 0;           // sandbox clock (millions of points) when this turn's input was read
    std::vector<int> pending;  // tiles our last move stepped onto, in order
    bool pendingSplit = false;

    void setup()
    {
        std::string tok;
        long long v;
        std::string t;
        std::cin >> tok >> v; // ID
        w.myId = static_cast<int>(v);
        std::cin >> tok >> t; // TEAM
        w.myTeam = t[0];
        int wd, ht;
        std::cin >> tok >> wd >> ht; // MAP
        std::cin >> tok >> v;        // UNIT_LIMIT
        w.unitLimit = static_cast<int>(v);
        if (QBOX && w.myId > 1)
            w.unitLimit -= QBOX_RESERVE; // QBOX: non-queens leave a free unit slot for the queen's emergency split
        w.init(wd, ht);
        rng = Rng(static_cast<uint64_t>(w.myId) * 7919 + 17);
        visible.assign(w.N, 0);
        freeT.assign(w.N, 1);
        occId.assign(w.N, -1);
        occTeam.assign(w.N, 0);
        occHead.assign(w.N, 0);
        otherDist.assign(w.N, INF);
        segAt.assign(w.N, -1);
    }

    int step(int t, int d) const { return w.nxt[t * 4 + d]; }

    // Maps with identical walls can differ in pearl gaps. A visible countdown
    // above a map's max gap (or spawning where it never spawns) rules it out.
    void filterByCountdowns()
    {
        if (w.candidates.size() < 2 && w.known)
            return;
        std::vector<int> keep;
        for (int c : w.candidates)
        {
            const KnownMap& m = KNOWN_MAPS[c];
            bool ok = true;
            for (int i = 0; i < 49 && ok; i++)
            {
                int t = w.idx(in.tx[i], in.ty[i]);
                int tin = in.tin[i];
                if ((tin < 0) != (m.gmax[t] == 0) || tin > m.gmax[t])
                    ok = false;
            }
            if (ok)
                keep.push_back(c);
        }
        if (keep.empty())
            return; // nothing fits: keep what we had
        w.candidates.swap(keep);
        bool stillKnown = false;
        for (int c : w.candidates)
            if (&KNOWN_MAPS[c] == w.known)
                stillKnown = true;
        if (!stillKnown)
            w.adopt(&KNOWN_MAPS[w.candidates.front()]);
    }

    // Tiles you can arrive on by crossing a portal: whoever stands there is
    // invisible to a dragon about to cross.
    std::vector<char> portalExit;
    void computePortalExits()
    {
        portalExit.assign(w.N, 0);
        for (int t = 0; t < w.N; t++)
            for (int d = 0; d < 4; d++)
            {
                int v = step(t, d);
                if (v >= 0 && v != w.plainStep(t, d))
                    portalExit[v] = 1;
            }
        if (UNK_EXPLORE && !w.known && !w.portalSide.empty())
            for (int t = 0; t < w.N; t++)
                for (int d = 0; d < 4; d++)
                {
                    if (w.portalSide[t * 4 + d])
                        portalExit[t] = 1; // someone crossing the partner edge lands here
                    if (!learnDest.empty() && learnDest[t * 4 + d] >= 0)
                        portalExit[learnDest[t * 4 + d]] = 1;
                }
    }

    void analyse()
    {
        round = in.round;
        myLen = in.length;
        units = in.units;
        myDir = in.dir;
        if (birthRound < 0)
            birthRound = round;
        if (lastGrowRound < 0)
            lastGrowRound = round; // process start
        if (prevLen > 0 && myLen > prevLen)
            lastGrowRound = round; // ate
        prevLen = myLen;

        std::fill(visible.begin(), visible.end(), 0);
        std::fill(freeT.begin(), freeT.end(), 1);
        std::fill(occId.begin(), occId.end(), -1);
        std::fill(occTeam.begin(), occTeam.end(), 0);
        std::fill(occHead.begin(), occHead.end(), 0);
        std::fill(segAt.begin(), segAt.end(), -1);
        segs.clear();

        myHead = -1;
        for (auto& p : in.parts)
        {
            int t = w.idx(p.x, p.y);
            segAt[t] = static_cast<int>(segs.size());
            segs.push_back({t, p.id, p.team, p.facing, p.head});
            occId[t] = p.id;
            occTeam[t] = p.team;
            occHead[t] = p.head;
            if (p.id == w.myId && p.head)
                myHead = t;
        }
        int hx = myHead % w.W, hy = myHead / w.W;
        if (REVISIT_PEN > 0 && myHead >= 0)
        {
            if (static_cast<int>(headSeen.size()) != w.N)
                headSeen.assign(w.N, -1);
            headSeen[myHead] = round;
        }

        if (round == 0 || (w.known == nullptr && !w.candidates.empty() && w.lastSeen[myHead] < 0))
            w.identifyByStart(hx, hy);
        if (MATCH_STRICT && !w.msDead)
        {
            // a starting dragon (round 0, no ECHOES line yet) whose start tile/id fits no same-size known map: unseen map
            if (round == 0 && birthRound == 0 && !in.echoesLine && !w.known && !w.candidates.empty())
                w.msMarkUnseen();
            else if (!w.candidates.empty() || w.known)
                msReadUnseen(); // a split child: did our parent say "unseen"?
        }
        w.observeEdges(in, hx, hy);
        if (FRAME_FIX && w.swapState < 0 && w.known)
            guessFrame();

        filterByCountdowns();
        if (w.nkBirth < 0)
            w.nkBirth = (!w.known && w.candidates.empty()) ? 1 : 0; // QF1: decided at this process's first turn, sticky
        if ((UNK_KING || UNK_SMALL_RAMGUARD) && !w.known && w.candidates.empty())
        {
            // unseen map (notes/unseen/PLAN.md Q2/Q7): turn the king + feeding machinery on
            if (!unkKingSet)
            {
                unkKingSet = true;
                if (UNK_KING)
                {
                    RP.kingDeclare = 1;
                    RP.kingSeedRound = UNK_KING_SEED;
                    RP.feedStart = UNK_KING_FEED;
                }
                if (UNK_SMALL_RAMGUARD && w.N <= 750)
                    RP.ramGuard = 2;
                if (QPARK_UNK && UNK_KING)
                    RP.queenKing = QPG_CROWN, RP.qPark = 3, RP.qkCap = QPG_QKCAP, RP.qpLate = QPARK_UNK >= 2; // ROUND4: generic queen park on unseen maps
            }
            // a full team has nothing left to gain from more foragers: crown early
            if (UNK_KING && units >= w.unitLimit - 2)
                RP.kingSeedRound = std::min(RP.kingSeedRound, std::max(110, round));
        }
        // SPRINT_KING_FULL: known Sprint map gets UNK_KING's crown-early rule too
        if (SPRINT_KING_FULL && UNK_KING && w.known &&
            ((SPRINT_KNOWN && isSprintMap(w.known->name)) || w.qualOn()) && units >= w.unitLimit - 2)
            RP.kingSeedRound = std::min(RP.kingSeedRound, std::max(110, round));
        if (UNK_SIZE_PARAMS && !w.known && !unkParamsSet)
        {
            // Unseen map: pick king timing from the board size (big boards reward one
            // big king, small ones end in swarm fights).
            unkParamsSet = true;
            if (w.N >= UNK_BIG_TILES)
            {
                RP.kingDeclare = 1;
                RP.kingSeedRound = UNK_KS;
                RP.splitStopRound = UNK_SS;
                RP.feedStart = UNK_FS;
                RP.feedReserve = 4;
            }
        }
        if (PEARL_DISTRUST && w.known && !w.pearlDistrust)
        {
            // Same walls can come with a different pearl layout (the server runs
            // variants). If what we see contradicts the built-in gaps, stop trusting
            // them: keep walls/portals, learn pearls from our own observations.
            int bad = 0;
            for (int i = 0; i < 49; i++)
            {
                int t = w.idx(in.tx[i], in.ty[i]);
                int tin = in.tin[i];
                if ((tin >= 0 && w.gmax[t] == 0) || (tin < 0 && w.gmax[t] > 0) || (w.gmax[t] > 0 && tin > w.gmax[t]))
                    bad++;
            }
            w.pearlContradictions += bad;
            if (w.pearlContradictions >= PEARL_DISTRUST_MIN)
            {
                w.pearlDistrust = true;
                std::fill(w.gmin.begin(), w.gmin.end(), -1);
                std::fill(w.gmax.begin(), w.gmax.end(), -1);
            }
        }
        if (EXPLORE_LEARN && !w.known)
        {
            exploreHits *= EXPLORE_DECAY;
            exploreN *= EXPLORE_DECAY;
        }
        for (int i = 0; i < 49; i++)
        {
            int t = w.idx(in.tx[i], in.ty[i]);
            visible[t] = 1;
            // EXPLORE_LEARN: a tile we see for the first time is a sample of the never-seen
            // population (skip our birth view: it is the parent's picked-over neighbourhood)
            if (EXPLORE_LEARN && !w.known && w.lastSeen[t] < 0 && round > birthRound)
            {
                exploreN += 1;
                if (in.tpearl[i] || (in.tin[i] >= 0 && in.tin[i] <= EXPLORE_CD))
                    exploreHits += 1;
            }
            w.lastSeen[t] = round;
            w.pearlMem[t] = static_cast<char>(in.tpearl[i]);
            if (in.tin[i] < 0)
            {
                w.gmax[t] = 0;
                w.spawnAt[t] = -1;
            }
            else
            {
                if (w.gmax[t] == 0)
                    w.gmax[t] = -1; // learned map said never, but it does spawn
                if (static_cast<int>(w.gapSeen.size()) != w.N)
                    w.gapSeen.assign(w.N, 0);
                w.gapSeen[t] = std::max(w.gapSeen[t], in.tin[i] + 1);
                w.spawnAt[t] = round + in.tin[i];
                if (HOT_LEARN && !w.known)
                {
                    // unseen map: a tile showing countdown 1 on 3 consecutive rounds respawns every
                    // round ("hot"); wake the hot-tile logic for it. A longer countdown undoes it.
                    if (static_cast<int>(hotRun.size()) != w.N)
                        hotRun.assign(w.N, 0), hotLast.assign(w.N, -9);
                    if (in.tin[i] <= 1)
                        hotRun[t] = hotLast[t] == round - 1 ? hotRun[t] + 1 : 1;
                    else
                        hotRun[t] = 0;
                    hotLast[t] = round;
                    if (hotRun[t] >= 3 && w.gmax[t] != 1)
                        w.gmin[t] = w.gmax[t] = 1;
                    else if (in.tin[i] > 1 && w.gmin[t] == 1 && w.gmax[t] == 1)
                        w.gmin[t] = w.gmax[t] = -1;
                }
                int m = w.mirror(t);
                if (m >= 0 && m != t)
                    w.spawnAt[m] = round + in.tin[i];
            }
        }

        if (PORTAL_ALLY_COST)
        {
            for (auto& sg : segs)
                if (sg.head && sg.team == w.myTeam && sg.id != w.myId)
                    allyHeadMemory.push_back({sg.tile, round});
            allyHeadMemory.erase(std::remove_if(allyHeadMemory.begin(), allyHeadMemory.end(),
                                                [&](const std::pair<int, int>& e) { return round - e.second > 5; }),
                                 allyHeadMemory.end());
        }
#if MS_DEBUG
        if (const char* mt = std::getenv("MS_TRACE"))
        {
            static FILE* mf = nullptr;
            if (!mf)
                mf = std::fopen(mt, "a");
            if (mf)
            {
                std::fprintf(mf, "%d %d %c %s b%d e%d c%zu dead%d conf0 ev0/0 dis%d\n", round, w.myId, w.myTeam,
                             w.known ? w.known->name : "?", birthRound, in.echoesLine ? 1 : 0, w.candidates.size(),
                             w.msDead ? 1 : 0, w.pearlDistrust ? 1 : 0);
                std::fflush(mf);
            }
        }
#endif
        if (UNK_SCARCE_FIX && !w.known && !w.portalUse && myHead >= 0 && !(QNO_UNKPORTAL >= 2 && qNoUnkPortal()))
            scarceFixCheck(); // QNO_UNKPORTAL 2: the queen never links seen portal pairs into her paths either
        computePortalExits();
        computeFreeTimes();
        updateTrail();
        computeOtherDist();
        readMessages();
        qstUpdate();
        updateKingship();
    }

    // For each visible segment, the number of segments from it back to its
    // tail (inclusive), or INF if the chain runs out of view.
    void computeFreeTimes()
    {
        const int S = static_cast<int>(segs.size());
        // pred[s] = segment that points into s from the tail side
        std::vector<int> pred(S, -1);
        for (int s = 0; s < S; s++)
        {
            if (segs[s].head && segs[s].id == w.myId)
                continue;
            if (segs[s].head)
                continue; // a head points where it is going, not at another segment
            int to = step(segs[s].tile, segs[s].facing);
            if (to < 0)
                to = w.plainStep(segs[s].tile, segs[s].facing);
            int j = segAt[to];
            if (j >= 0 && segs[j].id == segs[s].id)
                pred[j] = s;
        }
        // tails: no pred, and every tile that could hold the pred is visible
        std::vector<int> cnt(S, 0);
        // resolve with memoised walk
        std::vector<char> state(S, 0);
        for (int s0 = 0; s0 < S; s0++)
        {
            std::vector<int> chain;
            int s = s0;
            while (s >= 0 && state[s] == 0 && cnt[s] == 0)
            {
                state[s] = 1;
                chain.push_back(s);
                s = pred[s];
            }
            int base;
            if (s >= 0 && cnt[s] > 0)
                base = cnt[s];
            else if (s >= 0)
                base = INF; // cycle guard
            else
            {
                int tail = chain.back();
                base = tailIsVisibleTail(tail) ? 1 : UNKNOWN_TAIL_EXTRA;
                chain.pop_back();
                cnt[tail] = base;
            }
            for (int i = static_cast<int>(chain.size()) - 1; i >= 0; i--)
            {
                base = base >= INF ? INF : base + 1;
                cnt[chain[i]] = base;
            }
        }
        // our own body: exact from length, walking from the head
        std::vector<int> fromHead(S, -1);
        {
            // succ: segment s points (via facing) to the next segment toward head
            if (myHead >= 0)
            {
                int cur = segAt[myHead];
                int i = 0;
                fromHead[cur] = 0;
                while (true)
                {
                    int p = pred[cur];
                    if (p < 0)
                        break;
                    fromHead[p] = ++i;
                    cur = p;
                }
            }
        }
        for (int s = 0; s < S; s++)
        {
            int t = segs[s].tile;
            int c;
            if (segs[s].id == w.myId && fromHead[s] >= 0)
                c = myLen - fromHead[s];
            else if (segs[s].id == w.myId)
                c = cnt[s];
            else
                c = cnt[s] >= INF ? INF : cnt[s] + 1; // margin: they might eat
            freeT[t] = c >= INF ? INF : c + 1;
        }
    }

    // True if segment s has no body behind it: all tiles that could hold the
    // previous segment are in view and none of them does.
    bool tailIsVisibleTail(int s)
    {
        int t = segs[s].tile;
        for (int d = 0; d < 4; d++)
        {
            // tiles n with step(n, e) == t: approximate with neighbours in the
            // reverse direction plus portal partners (known map)
            int n = step(t, d);
            if (n < 0)
                continue;
            if (!visible[n])
                return false;
        }
        return true;
    }

    void computeOtherDist()
    {
        std::fill(otherDist.begin(), otherDist.end(), INF);
        std::vector<int> q;
        for (auto& s : segs)
            if (s.head && s.id != w.myId)
            {
                otherDist[s.tile] = 0;
                q.push_back(s.tile);
            }
        for (size_t qi = 0; qi < q.size(); qi++)
        {
            int u = q[qi];
            if (otherDist[u] >= 16)
                continue;
            for (int d = 0; d < 4; d++)
            {
                int v = step(u, d);
                if (v < 0 || otherDist[v] <= otherDist[u] + 1)
                    continue;
                if (freeT[v] > otherDist[u] + 1)
                    continue;
                otherDist[v] = otherDist[u] + 1;
                q.push_back(v);
            }
        }
    }

    // Expected pearl value of tile t if we arrive on step s (s=1 this turn).
    double pearlValue(int t, int s) const
    {
        int arrive = round + s - 1;
        double v = 0;
        if (visible[t])
        {
            if (w.pearlMem[t])
                v = 1.0;
            else if (w.spawnAt[t] >= 0 && arrive >= w.spawnAt[t])
                v = 0.85;
        }
        else
        {
            int ls = w.lastSeen[t];
            if (ls >= 0 && w.pearlMem[t])
                v = std::pow(0.96, round - ls);
            else if (w.spawnAt[t] >= 0 && w.spawnAt[t] > ls && arrive >= w.spawnAt[t])
                v = 0.75 * std::pow(0.97, arrive - w.spawnAt[t]);
            else
            {
                double r = w.rate(t);
                if (EXPLORE_LEARN && !w.known && ls < 0 && w.spawnAt[t] < 0 && w.gmax[t] < 0)
                    v = exploreEst(); // learned from first sightings, not a time-growing guess
                else if (r > 0)
                {
                    int since = arrive - std::max(ls, w.spawnAt[t] >= 0 ? w.spawnAt[t] : 0);
                    if (ls < 0 && w.spawnAt[t] < 0)
                        since = arrive; // initial countdowns start somewhere in [min,max]
                    v = 0.5 * std::min(1.0, std::max(0, since) * r);
                }
            }
        }
        if (v <= 0)
            return (UNK_EXPLORE && exploreDesire && !lureTile.empty() && lureTile[t]) ? UNK_EXPLORE_LURE : 0;
        // someone else closer: they will probably take it
        int od = otherDist[t];
        if (od < s)
            v *= 0.25;
        else if (od == s)
            v *= TURN_ORDER_TIES ? 0.85 : 0.55; // we move first in every tie (notes/unseen/PLAN.md Q3)
        if (UNK_EXPLORE && exploreDesire && !lureTile.empty() && lureTile[t])
            v = std::max(v, UNK_EXPLORE_LURE); // an unexplored door is worth walking to
        return v;
    }

    // Time-aware BFS from a tile we enter on step 1. Returns pearl score and
    // number of reachable tiles (capped).
    std::vector<int> bfsDist, bfsQ;
#include "pearl_route.hpp"
    void bfsFrom(int start, double& pearlScore, int& area, int areaCap)
    {
#if PROFILE_POINTS
        PROF_BEGIN(b);
        bfsFromImpl(start, pearlScore, area, areaCap);
        PROF_END(b, 3);
    }
    void bfsFromImpl(int start, double& pearlScore, int& area, int areaCap)
    {
#endif
        if (bfsDist.size() != static_cast<size_t>(w.N))
            bfsDist.assign(w.N, INF);
        std::fill(bfsDist.begin(), bfsDist.end(), INF);
        bfsQ.clear();
        bfsDist[start] = 1;
        bfsQ.push_back(start);
        pearlScore = 0;
        area = 0;
        const double g = PEARL_GAMMA;
        std::vector<double> gp(1, 1.0);
        for (size_t qi = 0; qi < bfsQ.size(); qi++)
        {
            int u = bfsQ[qi];
            int du = bfsDist[u];
            if (!VORONOI_AREA || du < otherDist[u] || (TURN_ORDER_TIES && du == otherDist[u]))
                area++;
            while (static_cast<int>(gp.size()) <= du)
                gp.push_back(gp.back() * g);
            double pv = pearlValue(u, du);
            if (pv > 0)
                pearlScore += pv * gp[du];
            if (du > 60)
                continue;
            for (int d = 0; d < 4; d++)
            {
                int v = step(u, d);
                if (v < 0 || bfsDist[v] != INF)
                    continue;
                if (freeT[v] > du + 1)
                    continue;
                if (VORONOI_BLOCK && otherDist[v] < du + 1)
                    continue;
                bfsDist[v] = du + 1;
                bfsQ.push_back(v);
            }
        }
        (void)areaCap;
        // PEARL_ROUTE (Codex, codex-battlecode/notes/pearl-route.md): value the best single route,
        // not the sum over every branch. 1 = all maps, 2 = unknown maps only
        if (PEARL_ROUTE == 1 || (PEARL_ROUTE == 2 && (!w.known || (SPRINT_ROUTE && isSprintMap(w.known->name) && !(SPRINT_ROUTE_NOWEAK && std::string(w.known->name) == "weakhold")) || w.qualOn(QUAL_ROUTE))))
            pearlScore = PEARL_ROUTE_REGION * pearlScore + PEARL_ROUTE_SCALE * bestPearlRoute();
    }

    int enemyVisibleLength(int id) const
    {
        int n = 0;
        for (auto& s : segs)
            if (s.id == id)
                n++;
        return n;
    }

    // Enemy heads that could step onto tile t before our next turn.
    int enemyHeadThreat(int t) const
    {
        int threat = 0;
        for (auto& s : segs)
        {
            if (!s.head || s.team == w.myTeam)
                continue;
            for (int d = 0; d < 4; d++)
                if (step(s.tile, d) == t)
                    threat = std::max(threat, enemyVisibleLength(s.id));
        }
        return threat;
    }

    // How many moves can we make from here without dying, up to maxDepth?
    // Simulates our body exactly (no reversing, tail follows), treats other
    // dragons' segments as vacating on schedule. Assumes we don't eat.
    int surviveDepth(int firstTile, int maxDepth)
    {
#if PROFILE_POINTS
        PROF_BEGIN(s);
        int r = surviveDepthImpl(firstTile, maxDepth);
        PROF_END(s, 4);
        return r;
    }
    int surviveDepthImpl(int firstTile, int maxDepth)
    {
#endif
        if (static_cast<int>(bodyCnt.size()) != w.N)
            bodyCnt.assign(w.N, 0);
        if (static_cast<int>(eatenMark.size()) != w.N)
            eatenMark.assign(w.N, 0);
        int L = static_cast<int>(trail.size());
        if (L == 0)
            return maxDepth;
        const int L0 = L;
        int hotEaten = 0;
        const int cap = L + maxDepth + 4;
        simBody.assign(cap, -1);
        // ring: head at index h, body occupies h..h+L-1 (mod cap)
        int h = 0;
        for (int i = 0; i < L; i++)
        {
            simBody[i] = trail[i];
            bodyCnt[trail[i]]++;
        }
        int best = 0;
        nodes = 0;
        struct Frame
        {
            int tile, dir, tailTile; // tailTile -1: we ate here (tail stayed)
        };
        std::vector<Frame> stack;
        auto canEnter = [&](int v, int t) {
            if (v < 0 || bodyCnt[v] > 0)
                return false;
            if (REPLY_SEARCH && replyBanOn && t == 2 && replyBan[v])
                return false;
            if (FREE_SURVIVE)
            {
                const int F = freeSteps(L0); // up to F steps per turn: step t happens on turn ceil(t/F)
                return freeOther[v] <= (t + F - 1) / F;
            }
            return freeOther[v] <= t;
        };
        // a pearl we'd eat on this tile (seen now, or a pearl-every-round tile)
        auto eats = [&](int v) {
            if (!DFS_EATS || eatenMark[v])
                return false;
            return (visible[v] && w.pearlMem[v]) || (w.gmax[v] == 1 && w.gmin[v] == 1);
        };
        auto push = [&](int v) {
            h = (h - 1 + cap) % cap;
            simBody[h] = v;
            bodyCnt[v]++;
            if (eats(v))
            {
                eatenMark[v] = 1;
                L++;
                if (w.gmax[v] == 1)
                    hotEaten++;
                return -1;
            }
            int tailIdx = (h + L) % cap;
            int tail = simBody[tailIdx];
            bodyCnt[tail]--;
            return tail;
        };
        auto pop = [&](int tail) {
            if (tail < 0)
            {
                eatenMark[simBody[h]] = 0;
                if (w.gmax[simBody[h]] == 1)
                    hotEaten--;
                L--;
            }
            else
            {
                int tailIdx = (h + L) % cap;
                simBody[tailIdx] = tail;
                bodyCnt[tail]++;
            }
            bodyCnt[simBody[h]]--;
            h = (h + 1) % cap;
        };
        // small dragons that grow to 4 can split and send the tail half back out
        // R8 TIP_REV bit 2: a long non-queen that has eaten TR_NET here can tip-split; the child (the tail end) walks out
        auto tipEscape = [&]() {
            if (!(TIP_REV & 2) || L0 < TR_MINLEN || L - L0 < TR_NET || units >= w.unitLimit || amQueen())
                return false;
            int tl = simBody[(h + L - 1) % cap], st = static_cast<int>(stack.size()) + 1;
            for (int e = 0; e < 4; e++)
            {
                int v = step(tl, e);
                if (v >= 0 && bodyCnt[v] == 0 && freeOther[v] <= st)
                    return true;
            }
            return false;
        };
        auto escapes = [&]() {
            return (ESCAPE_SPLIT && L0 <= 3 && L >= 4 && units < w.unitLimit && (!RP.escapeHotOnly || hotEaten > 0) &&
                    (ESC_NET == 0 || L - L0 >= ESC_NET)) || // v44 ESC_NET
                   tipEscape();
        };
        auto cleanup = [&]() {
            while (!stack.empty())
            {
                pop(stack.back().tailTile);
                stack.pop_back();
            }
            for (int i = 0; i < L0; i++)
                bodyCnt[trail[i]]--;
        };
        if (!canEnter(firstTile, 1))
        {
            for (int i = 0; i < L0; i++)
                bodyCnt[trail[i]]--;
            return 0;
        }
        stack.push_back({firstTile, 0, push(firstTile)});
        best = 1;
        if (escapes())
        {
            cleanup();
            return maxDepth;
        }
        while (!stack.empty())
        {
            Frame& f = stack.back();
            int depth = static_cast<int>(stack.size());
            if (depth >= maxDepth || f.dir >= 4 || nodes > nodeCap)
            {
                if (depth >= maxDepth || nodes > nodeCap)
                {
                    best = std::max(best, depth);
                    if (depth >= maxDepth)
                        break;
                }
                pop(f.tailTile);
                stack.pop_back();
                continue;
            }
            int d = f.dir++;
            int v = step(f.tile, d);
            if (!canEnter(v, depth + 1))
                continue;
            if (survQBan && qparkBan(f.tile, d))
                continue; // ROUND6 QK_SURV: the park forbids this step, so the look-ahead may not use it
            nodes++;
            int tail = push(v);
            stack.push_back({v, 0, tail});
            best = std::max(best, depth + 1);
            if (escapes())
            {
                best = maxDepth;
                break;
            }
        }
        cleanup();
        return best;
    }

    // Free exits a head at tile h would have if we moved onto tile t.
    int exitsOf(int h, int t) const
    {
        int n = 0;
        for (int d = 0; d < 4; d++)
        {
            int v = step(h, d);
            if (v < 0 || v == t)
                continue;
            if (freeT[v] <= 1)
                n++;
        }
        return n;
    }

    // Moving onto t can trap a neighbouring head. Bad for allies, great for enemies.
    double boxEffect(int t) const
    {
        double e = 0;
        for (auto& s : segs)
        {
            if (!s.head || s.id == w.myId)
                continue;
            bool adjacent = false;
            for (int d = 0; d < 4; d++)
                if (step(s.tile, d) == t)
                    adjacent = true;
            if (!adjacent)
                continue;
            int before = exitsOf(s.tile, -1), after = exitsOf(s.tile, t);
            if (after == 0 && before > 0)
                e += s.team == w.myTeam ? -60.0 : 25.0 + 2.0 * enemyVisibleLength(s.id);
            else if (after == 1 && s.team == w.myTeam)
                e -= 3.0;
        }
        return e;
    }

    // R8 ALLY_BOX: our head on t next turn: exits left when ally bodies that may still be there count as walls.
    // Penalise only when an ally body takes an exit (kelp corridors and our own body are left to surviveDepth).
    double allyBoxPen(int t) const
    {
        int ex = 0, exTile = -1;
        bool allyWall = false;
        for (int d = 0; d < 4; d++)
        {
            int v = step(t, d);
            if (v < 0 || v == myHead || v == t)
                continue;
            if (occId[v] >= 0 && occId[v] != w.myId && occTeam[v] == w.myTeam && freeT[v] > 2 - ABX_SLACK)
            {
                allyWall = true;
                continue;
            }
            if (occId[v] >= 0 && freeT[v] > 2)
                continue;
            ex++, exTile = v;
        }
        if (!allyWall || ex > 1)
            return 0;
        if (ex == 0)
            return ABX_PEN0;
        double p = ABX_PEN1;
        for (auto& o : segs)
            if (o.head && o.id != w.myId && wrapDist(o.tile, exTile) <= 2)
            {
                p += ABX_CONT;
                break;
            }
        return p;
    }

    void emitMove(int d)
    {
        out += "MOVE ";
        out += DIRC[d];
        out += '\n';
        lastMoveDir = d;
        pending.clear();
        int t = step(myHead, d);
        if (t >= 0)
            pending.push_back(t);
        if (t >= 0 && t != w.plainStep(myHead, d))
            lastPortalRound = round;
    }

    // Keep an exact copy of our own body, including parts out of view (e.g.
    // after a portal). The body is always the last LENGTH tiles the head visited.
    void updateTrail()
    {
        if (!trail.empty() && !pendingSplit)
            for (int t : pending)
                trail.insert(trail.begin(), t);
        pending.clear();
        pendingSplit = false;
        if (UNK_EXPLORE && exploreRound == round - 1 && exploreFrom >= 0)
        {
            int A = exploreFrom, d = exploreDir, X = myHead;
            if (X != w.plainStep(A, d))
            {
                if (static_cast<int>(learnDest.size()) != w.N * 4)
                    learnDest.assign(w.N * 4, -1);
                int A2 = w.plainStep(A, d), C = w.plainStep(X, (d + 2) % 4);
                learnDest[A * 4 + d] = X;
                learnDest[X * 4 + (d + 2) % 4] = A;
                learnDest[A2 * 4 + (d + 2) % 4] = C;
                learnDest[C * 4 + d] = A2;
                if (!trail.empty() && trail.front() == A)
                    trail.insert(trail.begin(), X); // our body continues behind the portal
            }
            exploreRound = -100;
        }
        if (trail.empty() || trail.front() != myHead)
        {
            // rebuild from what we can see: walk from the head along our own chain
            trail.clear();
            int cur = segAt[myHead];
            std::vector<char> used(segs.size(), 0);
            while (cur >= 0 && !used[cur])
            {
                used[cur] = 1;
                trail.push_back(segs[cur].tile);
                int nextSeg = -1;
                for (size_t j = 0; j < segs.size(); j++)
                {
                    if (used[j] || segs[j].id != w.myId || segs[j].head)
                        continue;
                    int to = step(segs[j].tile, segs[j].facing);
                    if (to == segs[cur].tile)
                    {
                        nextSeg = static_cast<int>(j);
                        break;
                    }
                }
                cur = nextSeg;
            }
        }
        if (static_cast<int>(trail.size()) > myLen)
            trail.resize(myLen);
        if (NEWBORN_NECK_GUARD && myLen >= 2 && trail.size() == 1)
        {
            // A plain-adjacent neck would be in view, so an unseen neck (typically a
            // child born straddling a portal) sits on a portal exit next to the head.
            std::vector<int> cand;
            for (int d = 0; d < 4; d++)
            {
                int v = step(myHead, d);
                if (v >= 0 && v != w.plainStep(myHead, d) && occId[v] < 0)
                    cand.push_back(v);
            }
            if (cand.size() == 1)
                trail.push_back(cand[0]);
            else
                for (int v : cand)
                    freeT[v] = std::max(freeT[v], myLen);
        }
        freeOther = freeT;
        for (int t : trail)
            if (occId[t] == w.myId)
                freeOther[t] = 1;
        for (int i = 0; i < static_cast<int>(trail.size()); i++)
        {
            int t = trail[i];
            freeT[t] = std::max(freeT[t], myLen - i + 1);
            occId[t] = w.myId;
            occTeam[t] = w.myTeam;
            occHead[t] = i == 0;
        }
    }

    // ---------------------------------------------------------- king / sonar
    // What we believe about our team's biggest dragon.
    int kingId = -1, kingLen = 0, kingTile = -1, kingDir = 0, kingRound = -1000;
    uint64_t relayMsg = 0;
    bool haveRelay = false;

    static uint64_t mix(uint64_t x)
    {
        x ^= x >> 31;
        x *= 0x7fb5d329728ea185ULL;
        x ^= x >> 27;
        x *= 0x81dadef4bc2dd44dULL;
        x ^= x >> 33;
        return x;
    }
    static constexpr uint64_t SECRET = 0x5d1c0ffee15b00b5ULL;

    // SONAR_ENCRYPT (IMP_FINDINGS.md): our rays land in enemy dragons too; the king word's low bits
    // were plaintext (position/length/facing). A keyed bijection on the wire hides them.
    static constexpr uint64_t SK1 = 0x9e3779b97f4a7c15ULL, SK2 = 0xd1b54a32d192ed03ULL, SMUL = 0xbf58476d1ce4e5b9ULL;
    static constexpr uint64_t smulInv()
    {
        uint64_t x = SMUL; // Newton iteration for the inverse of an odd number mod 2^64
        for (int i = 0; i < 6; i++)
            x *= 2 - SMUL * x;
        return x;
    }
    static constexpr uint64_t rotl(uint64_t v, int r) { return (v << r) | (v >> (64 - r)); }
    static constexpr uint64_t sonarOut(uint64_t x)
    {
        if (!SONAR_ENCRYPT)
            return x;
        return rotl(x ^ SK1, 23) * SMUL + SK2;
    }
    static constexpr uint64_t sonarIn(uint64_t y)
    {
        return rotl((y - SK2) * smulInv(), 64 - 23) ^ SK1;
    }

    // ---- FRAME_FIX: which side of the map file are we? ("A" = the file's team 0 starts)
    char frameTeam() const
    {
        if (!FRAME_FIX || w.swapState != 1)
            return w.myTeam;
        return w.myTeam == 'A' ? 'B' : 'A';
    }
    // Split children never see the start: guess from the nearest start position
    // (children are born near home early on); an ally's sonar overrides the guess.
    void guessFrame()
    {
        const KnownMap* m = w.known;
        if (myHead < 0 || !m->dragons || m->dragonCount <= 0)
            return;
        int best = 1 << 30, bestTeam = -1;
        for (int i = 0; i < m->dragonCount; i++)
        {
            const int16_t* d = m->dragons + i * 4;
            int dd = wrapDist(myHead, w.idx(d[2], d[3]));
            if (dd < best)
                best = dd, bestTeam = d[0];
        }
        if (bestTeam >= 0)
            w.swapState = (bestTeam == 0 ? 'A' : 'B') != w.myTeam;
    }
    // Salt mixed into our sonar checksums: 0 with FRAME_FIX off (v16-compatible);
    // otherwise 1 + (0 as file / 1 swapped / 2 unknown) so receivers learn the frame.
    uint64_t frameSalt(int fr) const { return FRAME_FIX ? static_cast<uint64_t>(fr + 1) << 58 : 0; }
    int myFrameCode() const { return w.swapKnown ? w.swapState : 2; }
    int lastFrameCode = 2; // frame code of the last message decoded
    void learnFrame(int fr)
    {
        if (FRAME_FIX && fr < 2 && !w.swapKnown)
        {
            w.swapState = fr;
            w.swapKnown = true;
        }
    }

    // CONS status beacons use the king layout under their own key, so decodeKing (SECRET) rejects them
    static constexpr uint64_t STATUS_SECRET = 0x3c6ef372fe94f82bULL;
    // v68 LATE_HUNT: king words (SECRET) carry "our queen was alive <= LH_AGE[b] rounds ago" in a key salt
    static constexpr uint64_t LH_SALT[4] = {0, 0x51ed270b3c9a4f17ULL, 0x2b8e9d4471c6a305ULL, 0x6a09e667f3bcc909ULL};
    static constexpr int LH_AGE[4] = {0, 1, 4, 12};
    int lhAliveRound = -100000; // freshest round our queen is known alive (sight, beacon, relay, salted king word)
    int lastSaltIdx = 0;
    uint64_t lhSalt() const
    {
        int a = round - lhAliveRound;
        for (int b = 1; b < 4; b++)
            if (a <= LH_AGE[b])
                return LH_SALT[b];
        return 0;
    }
    // the king word's 10-bit id field; KW_QID keeps non-queens off our queen's ids 0/1
    static int kw10(int id) { return (KW_QID && id > 1 && (id & 1023) <= 1) ? ((id & 1023) | 2) : (id & 1023); }
    uint64_t encodeKing(int tile, int len, int id, int hop, int dir, int rnd, uint64_t key = SECRET) const
    {
        if (LATE_HUNT && LH_BEACON && key == SECRET)
            key ^= lhSalt();
        uint64_t x = static_cast<uint64_t>(tile % w.W) | (static_cast<uint64_t>(tile / w.W) << 6) |
                     (static_cast<uint64_t>(std::min(len, 255)) << 12) | (static_cast<uint64_t>(kw10(id)) << 20) |
                     (static_cast<uint64_t>(hop & 3) << 30) | (static_cast<uint64_t>(dir & 3) << 32) |
                     (static_cast<uint64_t>(rnd & 511) << 34);
        uint64_t check =
            mix(x ^ key ^ (static_cast<uint64_t>(w.myTeam) << 50) ^ frameSalt(myFrameCode())) & ((1ULL << 21) - 1);
        return x | (check << 43);
    }

    bool decodeKing(uint64_t m, int& tile, int& len, int& id, int& hop, int& dir, int& rnd, uint64_t key = SECRET)
    {
        uint64_t x = m & ((1ULL << 43) - 1);
        bool ok = false;
        lastSaltIdx = 0;
        for (int si = 0; si < (LATE_HUNT && LH_BEACON && key == SECRET ? 4 : 1) && !ok; si++)
            for (int fr = 0; fr < (FRAME_FIX ? 3 : 1) && !ok; fr++)
            {
                uint64_t check =
                    mix(x ^ key ^ LH_SALT[si] ^ (static_cast<uint64_t>(w.myTeam) << 50) ^ frameSalt(fr)) & ((1ULL << 21) - 1);
                if ((m >> 43) == check)
                    ok = true, lastFrameCode = fr, lastSaltIdx = si;
            }
        if (!ok)
            return false;
        int px = static_cast<int>(x & 63), py = static_cast<int>((x >> 6) & 63);
        if (px >= w.W || py >= w.H)
            return false;
        tile = w.idx(px, py);
        len = static_cast<int>((x >> 12) & 255);
        id = static_cast<int>((x >> 20) & 1023);
        hop = static_cast<int>((x >> 30) & 3);
        dir = static_cast<int>((x >> 32) & 3);
        int r9 = static_cast<int>((x >> 34) & 511);
        // reconstruct the full round: the most recent round <= now with these low bits
        rnd = round - ((round - r9) & 511);
        return true;
    }

    // "Someone is standing on this portal exit": sent back through the portal
    // so an ally about to cross (and unable to see the exit) doesn't land on us.
    static constexpr uint64_t WARN_SECRET = 0x9a3c55e1d2b47f08ULL;
    // PORTAL_WARN_MEMO: the sender's length rides along (bits 21-26), so receivers
    // keep the exit blocked while its body drains off it.
    static constexpr int WARN_XB = PORTAL_WARN_MEMO ? 27 : 21;
    uint64_t encodeWarn(int tile, int rnd) const
    {
        uint64_t x = static_cast<uint64_t>(tile % w.W) | (static_cast<uint64_t>(tile / w.W) << 6) |
                     (static_cast<uint64_t>(rnd & 511) << 12);
        if (PORTAL_WARN_MEMO)
            x |= static_cast<uint64_t>(std::min(myLen, 63)) << 21;
        uint64_t check = mix(x ^ WARN_SECRET ^ (static_cast<uint64_t>(w.myTeam) << 50) ^ frameSalt(myFrameCode())) &
                         ((1ULL << (64 - WARN_XB)) - 1);
        return x | (check << WARN_XB);
    }
    int lastWarnLen = 0;
    bool decodeWarn(uint64_t m, int& tile, int& rnd)
    {
        uint64_t x = m & ((1ULL << WARN_XB) - 1);
        bool ok = false;
        for (int fr = 0; fr < (FRAME_FIX ? 3 : 1) && !ok; fr++)
        {
            uint64_t check = mix(x ^ WARN_SECRET ^ (static_cast<uint64_t>(w.myTeam) << 50) ^ frameSalt(fr)) &
                             ((1ULL << (64 - WARN_XB)) - 1);
            if ((m >> WARN_XB) == check)
                ok = true, lastFrameCode = fr;
        }
        if (!ok)
            return false;
        int px = static_cast<int>(x & 63), py = static_cast<int>((x >> 6) & 63);
        if (px >= w.W || py >= w.H)
            return false;
        tile = w.idx(px, py);
        int r9 = static_cast<int>((x >> 12) & 511);
        rnd = round - ((round - r9) & 511);
        lastWarnLen = static_cast<int>((x >> 21) & 63);
        return true;
    }
    std::vector<std::pair<int, int>> warnMem; // (exit tile, round its last ally segment leaves)

    // MATCH_STRICT "unseen map" word (sent by msDead dragons on their split turns, so the child hears it)
    static constexpr uint64_t MAP_SECRET = 0x5be0cd19137e2179ULL;
    uint64_t encodeUnseen() const
    {
        uint64_t x = 255ULL | (static_cast<uint64_t>(myFrameCode() & 3) << 8) | (static_cast<uint64_t>(round & 511) << 10);
        uint64_t check = mix(x ^ MAP_SECRET ^ (static_cast<uint64_t>(w.myTeam) << 50)) & ((1ULL << 45) - 1);
        return x | (check << 19);
    }
    // QUAL_GOSSIP: "this is Qualifier map i" (same word layout as encodeUnseen, code 200 + i instead of 255)
    uint64_t encodeQualMap() const
    {
        uint64_t x = static_cast<uint64_t>(200 + w.qualIdx) | (static_cast<uint64_t>(myFrameCode() & 3) << 8) |
                     (static_cast<uint64_t>(round & 511) << 10);
        uint64_t check = mix(x ^ MAP_SECRET ^ (static_cast<uint64_t>(w.myTeam) << 50)) & ((1ULL << 45) - 1);
        return x | (check << 19);
    }
    // sure of a Qualifier map: adopted it and every other same-size map is ruled out, or an ally that was sure said so
    bool qualSure() const { return w.qualOn() && (w.candidates.size() == 1 || w.qualTold); }
    void msReadUnseen()
    {
        for (uint64_t raw : in.msgs)
        {
            uint64_t m = SONAR_ENCRYPT ? sonarIn(raw) : raw;
            uint64_t x = m & ((1ULL << 19) - 1);
            if ((m >> 19) != (mix(x ^ MAP_SECRET ^ (static_cast<uint64_t>(w.myTeam) << 50)) & ((1ULL << 45) - 1)))
                continue;
            if ((x & 255) == 255 && ((round - static_cast<int>((x >> 10) & 511)) & 511) <= 2)
            {
                w.msMarkUnseen();
                return;
            }
#if QUAL_KNOWN
            if (QUAL_GOSSIP && (x & 255) >= 200 && (x & 255) < 214 && ((round - static_cast<int>((x >> 10) & 511)) & 511) <= 2)
            {
                int c = KNOWN_MAP_COUNT - 14 + static_cast<int>((x & 255) - 200);
                // only a map this process still holds as a candidate (same size, nothing seen that contradicts it)
                if (std::find(w.candidates.begin(), w.candidates.end(), c) == w.candidates.end())
                    continue;
                w.qualTold = true;
                if (w.known != &KNOWN_MAPS[c] || w.candidates.size() > 1)
                {
                    w.candidates.assign(1, c);
                    if (w.known != &KNOWN_MAPS[c])
                        w.adopt(&KNOWN_MAPS[c]);
                }
                return;
            }
#endif
        }
    }
    void readMessages()
    {
        if (SONAR_ENCRYPT)
            for (auto& m : in.msgs)
                m = sonarIn(m); // undo our keyed scramble (enemy rays turn into noise the checksums reject)
        for (uint64_t m : in.msgs)
        {
            int tile, rnd;
            if (!PORTAL_WARN || !decodeWarn(m, tile, rnd))
                continue;
            if (PORTAL_WARN_MEMO && lastWarnLen > 0 && rnd + lastWarnLen + PORTAL_WARN_MEMO_SLACK > round)
                warnMem.push_back({tile, rnd + lastWarnLen + PORTAL_WARN_MEMO_SLACK});
            if (round - rnd > 1)
                continue;
            learnFrame(lastFrameCode);
            if (occId[tile] < 0)
            {
                // treat the exit as holding an ally head this turn
                occId[tile] = 1 << 20;
                occTeam[tile] = w.myTeam;
                occHead[tile] = 1;
                freeT[tile] = std::max(freeT[tile], WARN_FREE_T);
                freeOther[tile] = std::max(freeOther[tile], WARN_FREE_T);
            }
        }
        if (PORTAL_WARN_MEMO)
        {
            warnMem.erase(std::remove_if(warnMem.begin(), warnMem.end(),
                                         [&](const std::pair<int, int>& e) { return e.second <= round; }),
                          warnMem.end());
            for (auto& [tile, until] : warnMem)
                if (w.lastSeen[tile] != round && (occId[tile] < 0 || occId[tile] == (1 << 20)))
                {
                    // an ally's body is still draining off this unseen exit
                    occId[tile] = 1 << 20;
                    occTeam[tile] = w.myTeam;
                    freeT[tile] = std::max(freeT[tile], until - round + 1);
                    freeOther[tile] = std::max(freeOther[tile], until - round + 1);
                }
        }
        echoBodyDir[0] = echoBodyDir[1] = echoBodyDir[2] = echoBodyDir[3] = false;
        if (PORTAL_ECHO_GUARD && probeMask && probeRound == round - 1 && probeTile == myHead)
        {
            int heads = in.echoes[2] + in.echoes[4];  // ally_head + enemy_head
            int bodies = in.echoes[1] + in.echoes[3]; // ally (incl. own) + enemy bodies
            if (probeRays > __builtin_popcount(static_cast<unsigned>(probeMask)))
                bodies = 0; // king/relay rays in other directions pollute the body count
            for (int d = 0; d < 4; d++)
            {
                if (!((probeMask >> d) & 1))
                    continue;
                int x = step(myHead, d);
                if (x < 0 || x == w.plainStep(myHead, d) || w.lastSeen[x] == round)
                    continue;
                bool shortPath = false; // the ray dies on kelp soon after the exit
                int y = x;
                for (int k = 0; k <= PORTAL_ECHO_RANGE; k++)
                {
                    y = step(y, d);
                    if (y < 0)
                    {
                        shortPath = true;
                        break;
                    }
                }
                if (PORTAL_ECHO_BODY_PEN > 0 && heads == 0 && bodies > 0 && !shortPath)
                    echoBodyDir[d] = true; // a body somewhere past the exit: risky, not certain
                if (heads > 0 || (PORTAL_ECHO_GUARD >= 2 && bodies > 0 && shortPath))
                {
                    occId[x] = 1 << 20;
                    occTeam[x] = w.myTeam;
                    occHead[x] = heads > 0;
                    freeT[x] = std::max(freeT[x], 2);
                    freeOther[x] = std::max(freeOther[x], 2);
                }
            }
        }
        if (UNK_EXPLORE && probeMask && probeRound == round - 1 && probeTile == myHead)
        {
            unkEchoRound = round;
            unkEchoTile = myHead;
            unkEchoMask = probeMask;
            unkEchoClean = probeRays == __builtin_popcount(static_cast<unsigned>(probeMask)) &&
                           in.echoes[1] + in.echoes[2] + in.echoes[3] + in.echoes[4] == 0;
        }
        haveRelay = false;
        int bestHopRelay = 99;
        for (uint64_t m : in.msgs)
        {
            int tile, len, id, hop, dir, rnd;
            if (!decodeKing(m, tile, len, id, hop, dir, rnd))
                continue;
            learnFrame(lastFrameCode);
            if (LATE_HUNT && lastSaltIdx > 0)
                lhNoteAlive(round - 1 - LH_AGE[lastSaltIdx]); // v68: the sender knew our queen alive recently
            if (round - rnd > 4)
                continue;
            if (id == kw10(w.myId))
                continue;
            if (LATE_HUNT && id <= 1)
                lhNoteAlive(rnd); // v68: our queen is broadcasting as a king
            if (QSTATE && id <= 1 && !amQueen() && (rnd > qsOurRound || (rnd == qsOurRound && hop < qsOurHop)))
                qsOurRound = rnd, qsOurHop = hop, qsOurTile = tile, qsOurLen = len, qsOurId = id, qsOurDir = dir; // queen as king
            if (qkOn() && id <= 1 && (rnd > qRound || (rnd == qRound && hop < qHop)))
                qLen = len, qTile = tile, qDir = dir, qRound = rnd, qHop = hop, qId = id; // our queen's beacon
            {
                bool found = false;
                for (auto& k : kingsSeen)
                    if (k.id == id)
                    {
                        if (rnd >= k.round)
                            k = {id, len, tile, dir, rnd};
                        found = true;
                    }
                if (!found)
                    kingsSeen.push_back({id, len, tile, dir, rnd});
            }
            bool better = len > kingLen || id == kw10(kingId) || round - kingRound > 6;
            if (better && (rnd >= kingRound || len > kingLen))
            {
                kingId = id;
                kingLen = len;
                kingTile = tile;
                kingDir = dir;
                kingRound = rnd;
            }
            if (hop < KING_RELAY_HOPS && hop < bestHopRelay && id == kw10(kingId))
            {
                bestHopRelay = hop;
                relayMsg = encodeKing(tile, len, id, hop + 1, dir, rnd);
                haveRelay = true;
            }
        }
        if (KING_FOCUS && RP.kingDeclare)
        {
            // notes/21: follow (feed, relay) the LONGEST fresh king, not the last one heard
            const KingInfo* bk = nullptr;
            for (auto& k : kingsSeen)
                if (round - k.round <= 8 && (!bk || k.len > bk->len))
                    bk = &k;
            if (bk && (bk->len > kingLen || round - kingRound > 2))
            {
                if (bk->id != kw10(kingId))
                {
                    haveRelay = bk->round >= round - 4;
                    relayMsg = encodeKing(bk->tile, bk->len, bk->id, 1, bk->dir, bk->round);
                }
                kingId = bk->id, kingLen = bk->len, kingTile = bk->tile, kingDir = bk->dir, kingRound = bk->round;
            }
        }
        if (KING_CONSENSUS && KING_V2 && RP.kingDeclare)
        {
            // forensics RC1a: the longest king heard in KC_MEM rounds wins (a short fresh one can't replace it)
            const KingInfo* bk = nullptr;
            for (auto& k : kingsSeen)
                if (round - k.round <= KC_MEM && (!bk || k.len > bk->len))
                    bk = &k;
            if (bk && (bk->len >= kingLen || round - kingRound > KC_MEM))
            {
                if (bk->id != kw10(kingId))
                {
                    haveRelay = round - bk->round <= 4; // relay the longest, not the last heard
                    relayMsg = encodeKing(bk->tile, bk->len, bk->id, 1, bk->dir, bk->round);
                }
                kingId = bk->id, kingLen = bk->len, kingTile = bk->tile, kingDir = bk->dir, kingRound = bk->round;
            }
        }
        if (CONS_R && CONS_BEACON)
        {
            // CONS status beacons: position/length of longer allies (hosts); CONS_RELAY_HOPS relays the longest
            haveConsRelay = false;
            int relayLen = 0;
            for (uint64_t m : in.msgs)
            {
                int tile, len, id, hop, dir, rnd;
                if (!decodeKing(m, tile, len, id, hop, dir, rnd, STATUS_SECRET))
                    continue;
                learnFrame(lastFrameCode);
                if (round - rnd > CONS_MEM || id == kw10(w.myId))
                    continue;
                if (hop < CONS_RELAY_HOPS && round - rnd <= 2 && len > relayLen)
                {
                    relayLen = len;
                    consRelayMsg = encodeKing(tile, len, id, hop + 1, dir, rnd, STATUS_SECRET);
                    haveConsRelay = true;
                }
                bool found = false;
                for (auto& k : statusSeen)
                    if (k.id == id)
                    {
                        if (rnd >= k.round)
                            k = {id, len, tile, dir, rnd};
                        found = true;
                    }
                if (!found)
                    statusSeen.push_back({id, len, tile, dir, rnd});
            }
            statusSeen.erase(std::remove_if(statusSeen.begin(), statusSeen.end(),
                                            [&](const KingInfo& k) { return round - k.round > 2 * CONS_MEM; }),
                             statusSeen.end());
        }
        // we can see the king ourselves: use exact data
        if (kingId >= 0)
            for (auto& sg : segs)
                if (sg.head && sg.team == w.myTeam && kw10(sg.id) == kw10(kingId) && sg.id != w.myId)
                {
                    kingTile = sg.tile;
                    kingDir = sg.facing;
                    kingRound = round;
                }
        if (FEED_STALE_GUARD && kingId >= 0)
        {
            // the whole "king" is in view and short: it's e.g. our 2-long parent after a U-turn split
            int vis = 0;
            bool inside = true;
            for (auto& sg : segs)
                if (sg.team == w.myTeam && kw10(sg.id) == kw10(kingId) && sg.id != w.myId)
                {
                    vis++;
                    int dx = std::abs(sg.tile % w.W - myHead % w.W), dy = std::abs(sg.tile / w.W - myHead / w.W);
                    dx = std::min(dx, w.W - dx), dy = std::min(dy, w.H - dy);
                    if (std::max(dx, dy) > 2 || portalExit[sg.tile])
                        inside = false;
                }
            if (vis > 0 && inside && vis < kingLen)
                kingLen = vis;
        }
        if (qkOn() && !amQueen())
        {
            // we can see the queen ourselves: exact data
            int vis = 0;
            for (auto& sg : segs)
                if (sg.team == w.myTeam && sg.id <= 1)
                {
                    vis++;
                    if (sg.head)
                        qTile = sg.tile, qDir = sg.facing, qRound = round, qId = sg.id, qHop = 0;
                }
            if (vis > 0 && qRound == round)
                qLen = std::max(qLen, vis);
            if (queenAlive() && queenKingRound())
            {
                // while the queen is heard she is the only king we follow, feed and relay
                kingId = qId, kingLen = qLen, kingTile = qTile, kingDir = qDir, kingRound = qRound;
                haveRelay = round - qRound <= 4 && qHop < KING_RELAY_HOPS;
                if (haveRelay)
                    relayMsg = encodeKing(qTile, qLen, qId, qHop + 1, qDir, qRound);
            }
        }
        if (kingId >= 0 && round - kingRound > 12)
        {
            kingId = -1;
            kingLen = 0;
        }
    }

    // A declared king stops splitting and broadcasts. Declared late in the
    // game by a dragon that hasn't heard of any king (a small chance per turn so
    // a whole swarm doesn't declare at once); steps down if it hears a bigger one.
    bool kingSelf = false;
    bool candQb[4] = {false, false, false, false}; // ROUND2 P3 QAK_HARD (per first step, read by tryFreePath)
    bool candEg[4] = {false, false, false, false}; // ROUND2 P6 ENDGAME_GUARD
    struct KingInfo
    {
        int id, len, tile, dir, round;
    };
    std::vector<KingInfo> kingsSeen;
    int freshKings(int longerThan) const
    {
        int n = 0;
        for (auto& k : kingsSeen)
            if (round - k.round <= 8 && k.len > longerThan)
                n++;
        return n;
    }
    int bestKingLen(int mem) const // KING_CONSENSUS: longest king heard within mem rounds
    {
        int b = 0;
        for (auto& k : kingsSeen)
            if (round - k.round <= mem)
                b = std::max(b, k.len);
        return b;
    }
    // v36: dragons 0 and 1 are the queens (one per team; ids follow map DRAGON line order, and the team
    // that owns line 1 varies by map and by server start swap). Any dragon running this code is ours.
    bool amQueen() const { return w.myId == 0 || w.myId == 1; }
    // v43 WH_NOPUMP: on weakhold no pocket dives/pumps (the 3-tile pocket cycle there is mass-neutral, V43.md)
    bool whNoPump() const { return WH_NOPUMP && w.known && std::string(w.known->name) == "weakhold"; }
    // v44 WH_CENTRE: on weakhold the non-queen starter (ids 2/3, WHC_IDS) walks to the open pearl fields
    // (gap >= 100 tiles, centre + the two 100-rows) before the pocket treadmill swallows it (V44.md).
    std::vector<int> whcDist;
    bool isWeakhold() const { return w.known && std::string(w.known->name) == "weakhold"; }
    bool whcActive()
    {
        if (!WH_CENTRE || !isWeakhold() || amQueen() || round >= WHC_UNTIL)
            return false;
        bool idOk = (w.myId == 2 || w.myId == 3) || ((WHC_IDS & 2) && w.myId < 8);
        if (!idOk)
            return false;
        if (whcDist.empty())
        {
            whcDist.assign(w.N, INF);
            std::vector<int> q;
            for (int t = 0; t < w.N; t++)
                if (w.gmax[t] >= WHC_GAP)
                    whcDist[t] = 0, q.push_back(t);
            for (size_t i = 0; i < q.size(); i++)
                for (int d = 0; d < 4; d++)
                {
                    int v = step(q[i], d);
                    if (v >= 0 && whcDist[v] == INF)
                        whcDist[v] = whcDist[q[i]] + 1, q.push_back(v);
                }
        }
        return whcDist[myHead] > WHC_STOP;
    }
    // QS phase (sticky): before it the queen plays v35 (with the queenEarly() limits), after it QUEEN_SAFE rules
    bool qsOn = false;
    bool queenSafe() const { return (QUEEN_SAFE && amQueen() && qsOn) || (QSTATE && qstSafe()); }
    // ---- QSTATE (v37a step 4): what we know about both queens.
    // Sonar word (QSECRET key, king layout): id field bits 0-1 = kind (0/1 our queen's beacon, its id;
    // 2 = notice only; 3 = enemy-queen sighting, tile = her head), bit 9 = "the enemy queen is dead".
    static constexpr uint64_t QSECRET = 0x3b6e1f0a95c27d43ULL;
    int qsOurRound = -100000, qsOurHop = 99, qsOurTile = -1, qsOurLen = 0, qsOurId = 0, qsOurDir = 0;
    bool qsTheirDead = false;
    int qsTheirDeadRound = -1000;
    int qsTheirRound = -100000, qsTheirTile = -1, qsTheirHop = 99; // last sighting of the enemy queen's head
    int qsSawRound = -1000, qsSawTile = -1;                        // my own last direct sighting
    bool qstOurAlive() const { return amQueen() || round - qsOurRound <= QUEEN_ALIVE_MEM; }
    // ours dead && theirs alive: r500 is lost, hunt her
    bool qstHunt() const { return !amQueen() && !qstOurAlive() && !qsTheirDead; }
    // ours alive && theirs dead (r500 is won), or theirs unknown late: the queen plays safe
    bool qstSafe() const { return amQueen() && (qsTheirDead || round >= QS_LATE); }
    // v47 EQ_HUNT: per-turn hunter state (eqHuntPrep, before computeThreats)
    int eqStaleRound = -100000; // a sighting this old or older was checked (tile in view, she's not there)
    int qsTheirDir = 0, qsTheirLen = 0, eqMaxLen = 0; // her facing / visible length at the last sighting, max seen
    int eqAnchorTile = -1, eqAnchorRound = -100000;   // EQH_TARGET: where her sightings have stayed since
    void eqNoteSighting()
    {
        eqMaxLen = std::max(eqMaxLen, qsTheirLen);
        if (eqAnchorTile < 0 || wrapDist(qsTheirTile, eqAnchorTile) > EQH_STILL_R)
            eqAnchorTile = qsTheirTile, eqAnchorRound = qsTheirRound;
    }
    // EQH_TARGET: a queen worth hunting doesn't run: big (a queen-king) or parked in a small area
    bool eqTargetOk() const
    {
        if (!EQH_TARGET)
            return true;
        if (eqMaxLen >= EQH_BIGLEN)
            return true;
        return eqAnchorTile >= 0 && qsTheirRound - eqAnchorRound >= EQH_STILL_ROUNDS;
    }
    bool eqHuntOn = false;
    int eqHuntTile = -1;
    void eqHuntPrep()
    {
        eqHuntOn = false;
        eqHuntTile = -1;
        if (EQH_DEBUG && EQ_HUNT && !amQueen() && myHead >= 0)
        {
            char buf[160];
            std::snprintf(buf, sizeof buf, "LOG eqh r%d id%d L%d u%d tile%d age%d hop%d stale%d dead%d d%d\n", round, w.myId,
                          myLen, units, qsTheirTile, round - qsTheirRound, qsTheirHop, qsTheirRound <= eqStaleRound,
                          (int)qsTheirDead, qsTheirTile >= 0 ? wrapDist(myHead, qsTheirTile) : -1);
            if (qsTheirTile >= 0 && round - qsTheirRound <= EQH_MEM)
                logPending += buf;
        }
        if (!EQ_HUNT || amQueen() || myHead < 0 || qsTheirDead || qsTheirTile < 0)
            return;
        bool bigNow = EQH_TARGET && eqMaxLen >= EQH_BIGLEN;
        if (qsTheirRound <= eqStaleRound || round - qsTheirRound > (bigNow ? EQH_MEM_BIG : EQH_MEM))
            return;
        bool late = round >= EQH_LATE;
        if (EQ_HUNT == 2 && !late)
            return;
        if (!eqTargetOk())
            return;
        bool tgtBig = EQH_TARGET && eqMaxLen >= EQH_BIGLEN;
        if (!late && round < EQH_FROM && units < EQH_UNITS)
            return;
        if (units < EQH_MIN_UNITS || iAmKing())
            return;
        if (myLen > (late ? EQH_MAXLEN_LATE : (tgtBig ? EQH_MAXLEN_BIG : EQH_MAXLEN)))
            return;
        if (wrapDist(myHead, qsTheirTile) > std::max(late ? EQH_R_LATE : EQH_R, tgtBig ? EQH_R_BIG : 0))
            return;
        eqHuntOn = true;
        eqHuntTile = qsTheirTile;
        if ((EQH_LEAD > 0 || EQH_FLANK > 0) && wrapDist(myHead, qsTheirTile) > EQH_LEAD_NEAR)
        {
            // intercept: aim EQH_LEAD steps ahead of her facing, then EQH_FLANK to one side (id parity: two sides)
            int aim = qsTheirTile;
            for (int k = 0; k < EQH_LEAD; k++)
            {
                int nx = step(aim, qsTheirDir & 3);
                if (nx < 0)
                    break;
                aim = nx;
            }
            int side = (qsTheirDir + ((w.myId & 1) ? 1 : 3)) & 3;
            for (int k = 0; k < EQH_FLANK; k++)
            {
                int nx = step(aim, side);
                if (nx < 0)
                    break;
                aim = nx;
            }
            eqHuntTile = aim;
        }
        if (EQH_DEBUG)
            logPending += "LOG eqhON r" + std::to_string(round) + " id" + std::to_string(w.myId) + "\n";
    }
    // ---- v68 LATE_HUNT: "our queen is dead" (positive evidence only, so nothing changes while she lives)
    static constexpr uint64_t LH_SECRET = 0x7d1c4e93a2b56f81ULL;
    int lhSawRound = -1000, lhSawTile = -1; // my own last direct sighting of our queen's head
    int lhBirth = -1;                       // silence is counted from max(lhAliveRound, birth)
    bool lhHeard = false;                   // ever heard/seen her after my birth (silence counts only then)
    int lhDeadRound = -1;                   // round our queen died (-1 = not known)
    int lhLearnRound = -1;                  // when I learned it
    int lhRelayed = -100000, lhRelayRound = -1000; // alive relay: last round value sent, when
    int lhSweepIdx = -1;                    // sweep: index into the enemy spawn list
    int lhSweepDoneMask = 0;
    bool lhActive = false;                  // this turn: LATE_HUNT pull on (uses eqHuntOn / eqHuntTile)
    bool lhOurDead() const { return LATE_HUNT && lhDeadRound >= 0 && !amQueen(); }
    bool lhOn() const { return lhOurDead() && !qsTheirDead; }
    void lhTrace(const char* what, int v)
    {
        if (LH_DEBUG)
            if (const char* fn = std::getenv("LH_TRACE"))
                if (FILE* f = std::fopen(fn, "a"))
                {
                    std::fprintf(f, "%s r%d id%d L%d v%d alive%d\n", what, round, w.myId, myLen, v, lhAliveRound);
                    std::fclose(f);
                }
    }
    void lhNoteDead(int rnd, int why)
    {
        if (rnd <= lhAliveRound)
            return; // she was alive after that: a stale or false notice
        if (LH_DEBUG && lhDeadRound < 0)
            lhTrace(why == 0 ? "learnS" : why == 1 ? "learnN" : "learnQ", rnd);
        if (lhDeadRound < 0)
            lhLearnRound = round;
        if (lhDeadRound < 0 || rnd < lhDeadRound)
            lhDeadRound = rnd;
    }
    void lhNoteAlive(int rnd)
    {
        if (rnd > lhAliveRound)
            lhAliveRound = rnd;
        lhHeard = true;
    }
    // runs in qstUpdate (readMessages has already fed lhNoteAlive with king words from id 0/1)
    void lhUpdate()
    {
        if (!LATE_HUNT || myHead < 0)
            return;
        if (amQueen())
        {
            lhAliveRound = round;
            return;
        }
        if (lhBirth < 0)
            lhBirth = round; // newborn: assume she's alive (not relayed: lhAliveRound stays evidence-only)
        bool seeAny = false;
        int head = -1;
        for (auto& s : segs)
            if (s.id <= 1 && s.team == w.myTeam)
            {
                seeAny = true;
                if (s.head)
                    head = s.tile;
            }
        bool sawDie = false;
        if (head >= 0)
            lhSawRound = round, lhSawTile = head, lhNoteAlive(round);
        else if (lhSawRound == round - 1 && lhSawTile >= 0 && visible[lhSawTile] && !seeAny)
            sawDie = true; // seen alive on my last turn, nothing of her is in view now: she died
        for (uint64_t m : in.msgs)
        {
            int tile, len, id, hop, dir, rnd;
            if (!decodeKing(m, tile, len, id, hop, dir, rnd, LH_SECRET))
                continue;
            if (id == 1)
                lhNoteAlive(rnd);
            else if (id == 2)
                lhNoteDead(rnd, 1);
        }
        if (lhDeadRound >= 0 && lhAliveRound >= lhDeadRound)
        {
            if (LH_DEBUG)
                lhTrace("revoke", lhDeadRound);
            lhDeadRound = lhLearnRound = -1; // false alarm
        }
        if (sawDie)
            lhNoteDead(round, 0);
        else if (LH_BEACON && LH_SILENT > 0 && lhDeadRound < 0 && lhHeard && round - std::max(lhAliveRound, lhBirth) > LH_SILENT)
            lhNoteDead(std::max(lhAliveRound, lhBirth) + 1, 2); // nothing from her for a long time
    }
    // the LATE_HUNT word for the idle rays, or false. Before her death: the queen's beacon and sparse relays of it,
    // only on fully idle turns (callers check), so no v61 message or probe is displaced. After: the death notice.
    bool lhWord(uint64_t& m)
    {
        if (!LATE_HUNT)
            return false;
        int at = pending.empty() ? myHead : pending.back();
        if (lhOurDead())
        {
            if (round - lhLearnRound > LH_NOTICE_FULL && round % LH_NOTICE_EVERY != 0)
                return false;
            m = encodeKing(at, 0, 2, 0, 0, lhDeadRound, LH_SECRET);
            return true;
        }
        if (!LH_BEACON)
            return false;
        if (amQueen())
        {
            if (LH_BEACON_EVERY > 1 && round % LH_BEACON_EVERY != 0)
                return false;
            m = encodeKing(at, 0, 1, 0, 0, round, LH_SECRET);
            return true;
        }
        if (round - lhAliveRound > LH_RELAY_FRESH || lhAliveRound <= lhRelayed || round - lhRelayRound < LH_RELAY_GAP || !lhHeard)
            return false;
        lhRelayed = lhAliveRound, lhRelayRound = round;
        m = encodeKing(at, 0, 1, 0, 0, lhAliveRound, LH_SECRET);
        return true;
    }
    // enemy spawn tiles (known maps, file frame -> ours), the enemy queen's first
    std::vector<int> lhSpawns;
    bool lhSpawnsBuilt = false;
    void lhBuildSpawns()
    {
        lhSpawnsBuilt = true;
        const KnownMap* m = w.known;
        if (!m || !m->dragons || m->dragonCount <= 0 || (FRAME_FIX && w.swapState < 0))
            return;
        int enemyFile = frameTeam() == 'A' ? 1 : 0;
        for (int pass = 0; pass < 2; pass++)
            for (int i = 0; i < m->dragonCount; i++)
            {
                const int16_t* d = m->dragons + i * 4;
                if (d[0] != enemyFile || (pass == 0) != (i <= 1))
                    continue;
                int t = w.idx(d[2], d[3]);
                if (t >= 0 && t < w.N && static_cast<int>(lhSpawns.size()) < 30)
                    lhSpawns.push_back(t);
            }
    }
    // ROUND2 P1 LH_FINISH: local finisher on a small lone enemy queen I saw myself (our queen's state is irrelevant)
    bool lhFinishPrep()
    {
        if (!LATE_HUNT || amQueen() || myHead < 0 || iAmKing() || round < LHF_FROM || qsTheirDead || qsSawTile < 0 ||
            round - qsSawRound > LHF_MEM || eqMaxLen <= 0 || eqMaxLen > LHF_QLEN || qsTheirTile < 0 ||
            qsTheirRound <= eqStaleRound)
            return false;
        for (auto& s : segs)
            if (s.head && s.team != w.myTeam && s.id > 1)
                return false; // another enemy head in view: not a mop-up
        lhActive = eqHuntOn = true;
        eqHuntTile = qsTheirTile;
        return true;
    }
    void lhPrep()
    {
        lhActive = false;
        if (LH_FINISH && !lhOn() && lhFinishPrep())
        {
            r2log("lhf", eqHuntTile);
            return;
        }
        if (!lhOn() || myHead < 0 || iAmKing() || units < LH_MIN_UNITS)
            return;
        bool smallQ = eqMaxLen > 0 && eqMaxLen <= LH_SMALLQ;
        if (myLen > LH_MAXLEN && !smallQ)
            return;
        // evidence she outlived ours: a sighting at or after our queen's death (else she may have died unseen first,
        // and a hunt would only wreck the longest-dragon race)
        if (LH_EVID && (qsTheirTile < 0 || qsTheirRound < lhDeadRound))
            return;
        int tgt = -1;
        if (qsTheirTile >= 0 && qsTheirRound > eqStaleRound && round - qsTheirRound <= LH_MEM)
            tgt = qsTheirTile;
        else if (LH_SWEEP && round - qsTheirRound <= LH_SWEEP_MEM)
        {
            if (!lhSpawnsBuilt)
                lhBuildSpawns();
            int n = static_cast<int>(lhSpawns.size());
            if (n > 0)
            {
                if (lhSweepIdx < 0)
                    lhSweepIdx = 0; // the enemy queen's spawn first
                if (visible[lhSpawns[lhSweepIdx]])
                {
                    // checked: no queen head in view (else qsTheirRound == round). Next spawn, by id stride
                    lhSweepDoneMask |= 1 << lhSweepIdx;
                    if (__builtin_popcount(static_cast<unsigned>(lhSweepDoneMask)) >= n)
                        lhSweepDoneMask = 1 << lhSweepIdx;
                    int stride = 1 + (w.myId % std::max(1, n - 1));
                    for (int k = 0; k < n && (lhSweepDoneMask >> lhSweepIdx & 1); k++)
                        lhSweepIdx = (lhSweepIdx + stride) % n;
                    if (lhSweepDoneMask >> lhSweepIdx & 1)
                        for (int k = 0; k < n; k++)
                            if (!(lhSweepDoneMask >> k & 1))
                                lhSweepIdx = k;
                }
                tgt = lhSpawns[lhSweepIdx];
            }
        }
        if (tgt < 0)
            return;
        lhActive = eqHuntOn = true;
        eqHuntTile = tgt;
        if (LH_DEBUG)
            if (const char* fn = std::getenv("LH_TRACE"))
                if (FILE* f = std::fopen(fn, "a"))
                {
                    std::fprintf(f, "r%d id%d L%d tgt%d,%d age%d qd%d learn%d sweep%d\n", round, w.myId, myLen, tgt % w.W,
                                 tgt / w.W, round - qsTheirRound, lhDeadRound, lhLearnRound, lhSweepIdx);
                    std::fclose(f);
                }
    }
    void qstUpdate()
    {
        lhUpdate();
        if (!QSTATE && !EQ_HUNT && !LATE_HUNT)
            return;
        if (qsOurRound < -1000)
            qsOurRound = round; // newborn: assume our queen is alive
        if (amQueen())
            qsOurRound = round, qsOurHop = 0, qsOurId = w.myId;
        bool seeEq = false;
        int eqHead = -1, eqDirSeen = 0, eqLenSeen = 0;
        for (auto& s : segs)
        {
            if (s.id > 1)
                continue;
            if (s.team != w.myTeam)
                eqLenSeen++;
            if (s.team == w.myTeam)
            {
                if (s.head && s.id != w.myId)
                    qsOurRound = round, qsOurHop = 0, qsOurTile = s.tile, qsOurId = s.id, qsOurDir = s.facing;
            }
            else
            {
                seeEq = true;
                if (s.head)
                    eqHead = s.tile, eqDirSeen = s.facing;
            }
        }
        // seen alive on my last turn, her head tile is in view now, nothing of her is visible and the tile is empty
        if (!qsTheirDead && qsSawRound == round - 1 && qsSawTile >= 0 && visible[qsSawTile] && !seeEq &&
            occId[qsSawTile] < 0)
            qsTheirDead = true, qsTheirDeadRound = round;
        if (eqHead >= 0)
        {
            qsTheirDead = false;
            qsSawRound = round, qsSawTile = eqHead;
            qsTheirRound = round, qsTheirTile = eqHead, qsTheirHop = 0;
            qsTheirDir = eqDirSeen, qsTheirLen = eqLenSeen;
            eqNoteSighting();
        }
        for (uint64_t m : in.msgs)
        {
            int tile, len, id, hop, dir, rnd;
            if (!decodeKing(m, tile, len, id, hop, dir, rnd, QSECRET) || round - rnd > 4)
                continue;
            if ((id & 512) && !qsTheirDead && eqHead < 0)
                qsTheirDead = true, qsTheirDeadRound = round;
            int kind = id & 3;
            if (kind <= 1 && !amQueen() && (rnd > qsOurRound || (rnd == qsOurRound && hop < qsOurHop)))
                qsOurRound = rnd, qsOurHop = hop, qsOurTile = tile, qsOurLen = len, qsOurId = kind, qsOurDir = dir;
            if (kind == 3 && (rnd > qsTheirRound || (rnd == qsTheirRound && hop < qsTheirHop)))
            {
                bool newer = rnd > qsTheirRound;
                qsTheirRound = rnd, qsTheirHop = hop, qsTheirTile = tile, qsTheirDir = dir, qsTheirLen = len;
                if (newer)
                    eqNoteSighting();
            }
        }
        // v47 EQ_HUNT: the last sighting's tile is in view now and her head isn't there: stale for me
        if ((EQ_HUNT || LATE_HUNT) && eqHead < 0 && qsTheirTile >= 0 && qsTheirRound < round && visible[qsTheirTile])
            eqStaleRound = qsTheirRound;
    }
    // the word this dragon sends on its idle rays (false = nothing to say)
    bool qstWord(uint64_t& m)
    {
        int deadBit = qsTheirDead ? 512 : 0;
        int at = pending.empty() ? myHead : pending.back();
        int face = pending.empty() ? myDir : lastMoveDir;
        if (QSTATE && amQueen())
        {
            m = encodeKing(at, myLen, (w.myId & 1) | deadBit, 0, face, round, QSECRET);
            return true;
        }
        if ((qstHunt() || EQ_HUNT || lhOn()) && qsTheirHop == 0 && qsTheirRound == round)
        {
            m = encodeKing(qsTheirTile, qsTheirLen, 3 | deadBit, 0, qsTheirDir, round, QSECRET);
            return true;
        }
        if (QSTATE && round - qsOurRound <= 2 && qsOurHop < QS_RELAY_HOPS && qsOurTile >= 0)
        {
            m = encodeKing(qsOurTile, qsOurLen, (qsOurId & 1) | deadBit, qsOurHop + 1, qsOurDir, qsOurRound, QSECRET);
            return true;
        }
        if ((qstHunt() || EQ_HUNT || lhOn()) && round - qsTheirRound <= 2 && qsTheirHop < QS_RELAY_HOPS && qsTheirTile >= 0)
        {
            m = encodeKing(qsTheirTile, qsTheirLen, 3 | deadBit, qsTheirHop + 1, qsTheirDir, qsTheirRound, QSECRET);
            return true;
        }
        if (qsTheirDead && (round - qsTheirDeadRound <= 10 || (LATE_HUNT && lhOurDead() && round % 4 == 1)))
        {
            m = encodeKing(at, 0, 2 | deadBit, 0, 0, round, QSECRET);
            return true;
        }
        return false;
    }
    bool queenEarly() const { return QUEEN_SAFE && amQueen() && !qsOn; }
    // QF1: QE_KR acts only on maps this process never identified (sticky; QE_KR_ANYMAP=1 drops the gate = horse's prototype)
    // QUAL_QEKR: also on a known Qualifier map (qf1 played those with QE_KR on, as never-identified maps)
    bool qeKrOn() const { return queenEarly() && (QE_KR_ANYMAP || w.neverKnown() || w.qualOn(QUAL_QEKR)); }
    // QNO_UNKPORTAL: on never-identified maps the queen never knocks on / explore-crosses an unknown portal
    bool qNoUnkPortal() const { return QNO_UNKPORTAL && amQueen() && w.neverKnown(); }
    // ROUND3 P7 PM_QPARK: the queen is parked at home until the king seed round, then crowned (RP.queenKing).
    // Portals (qPark 1): she never crosses a portal and holds a spot far from every portal mouth/exit.
    // Maze (qPark 2): she stays inside the home field (frame x < PM_MAZE_QX).
    bool qparkQueen() const { return RP.qPark > 0 && amQueen(); }
    // R10 LANE_QSMALL helpers
    bool qsmOn = false; // sticky: set in qsmPrep once we have QSM_UNITS units
    bool qsmQueen() const { return LANE_QSMALL && RP.qSmall && amQueen() && qsmOn; }
    int qsmFloor() const { return std::max(2, std::min(QSM_KEEP, myLen - 2)); }
    int qsmSpawn = -1;
    bool qsmFlee = false;
    std::vector<int> qsmDist;
    void qsmPrep()
    {
        qsmFlee = false;
        if (LANE_QSMALL && RP.qSmall && amQueen() && myHead >= 0 && qsmSpawn < 0)
            qsmSpawn = myHead; // home = where she starts
        if (LANE_QSMALL && RP.qSmall && amQueen() && (RP.qSmall == 1 || units >= QSM_UNITS))
            qsmOn = true;
        if (!qsmQueen() || myHead < 0)
            return;
        if (qsmDist.empty())
        {
            qsmDist.assign(w.N, 99);
            qsmDist[qsmSpawn] = 0;
            std::vector<int> q{qsmSpawn};
            for (size_t i = 0; i < q.size(); i++)
                for (int d = 0; d < 4; d++)
                {
                    int v = step(q[i], d);
                    if (v >= 0 && v != q[i] && v == w.plainStep(q[i], d) && qsmDist[v] == 99 && qsmDist[q[i]] < 98)
                        qsmDist[v] = qsmDist[q[i]] + 1, q.push_back(v);
                }
        }
        for (auto& o : segs)
            if (o.head && o.team != w.myTeam && wrapDist(o.tile, myHead) <= PM_QP_FLEE)
                qsmFlee = true;
    }
    // DGU F4 PM_TD_PULL (root-lanes-b RLB C1): Tower Defense non-queen units walk to the centre field early.
    std::vector<int> tdDist;
    bool tdPullOn() const
    {
        return PM_TD_PULL > 0 && w.known && !amQueen() && round >= PM_TD_PULL_FROM && round < PM_TD_PULL_TO && myHead >= 0 &&
               std::string(w.known->name) == "Tower Defense";
    }
    void tdPrep()
    {
        if (!tdPullOn() || !tdDist.empty())
            return;
        tdDist.assign(w.N, 999);
        std::vector<int> q;
        for (int t = 0; t < w.N; t++)
            if (t % w.W >= 13 && t % w.W <= 18 && w.rate(t) > 0)
                tdDist[t] = 0, q.push_back(t);
        for (size_t i = 0; i < q.size(); i++)
            for (int d = 0; d < 4; d++)
            {
                int v = step(q[i], d);
                if (v >= 0 && v != q[i] && tdDist[v] == 999)
                    tdDist[v] = tdDist[q[i]] + 1, q.push_back(v);
            }
    }
    double tdPullScore(int t) const
    {
        if (!tdPullOn() || tdDist.empty() || tdDist[myHead] <= PM_TD_PULL_MIN || tdDist[t] >= 999)
            return 0.0;
        return PM_TD_PULL * (tdDist[myHead] - tdDist[t]);
    }
    double qsmScore(int t) const
    {
        if (!qsmQueen() || myHead < 0 || qsmDist.empty())
            return 0.0;
        double s = 0;
        if (QSM_POCKET > 0 && RP.qSmall == 1 && !pfDepth.empty() && pfDepth[t] > pfDepth[myHead])
            s -= QSM_POCKET;
        if (!qsmFlee)
            s -= QSM_PULL * std::max(0, qsmDist[t] - QSM_RAD);
        return s;
    }
    bool qparkNoDive() const { return (QSM_NODIVE && RP.qSmall == 1 && qsmQueen()) || (qparkQueen() && (RP.qPark == 1 || (RP.qPark == 3 ? qpgOn() : (PM_MAZE_QSTAY || round < RP.kingSeedRound)))); }
    // ROUND4 QPARK_GEN (qPark 3)
    bool qpStarted = false; // sticky; set in qparkPrep
    int qpUnits0 = 0;       // our unit count when the park started
    // economy rescue: the team is (nearly) gone before the feed round -> she forages (bans stay, no pull)
    bool qpRescue() const { return qpStarted && units <= QPG_RESCUE_UNITS && units < qpUnits0 && round < qkFeedRound(); }
    bool qpgOn() const { return RP.qPark == 3 && qpStarted && (QPG_STAY || round < qkFeedRound()); }
    int qpSpawn = -1, qpPlanRound = -1000;
    bool qpWeak = false;
    std::vector<char> qpNarrow; // 1-wide corridor / enemy-half tiles (soft)
    void qparkGenPlan()
    {
        if (qpSpawn < 0)
            qpSpawn = myHead;
        const bool unk = !w.known;
        if (qpAnchor >= 0 && (!unk || round >= QPG_REPLAN_TO || round - qpPlanRound < QPG_REPLAN_EVERY))
            return;
        qpPlanRound = round;
        if (POCKET_FACTORY)
            pfCompute();
        auto plain = [&](int u, int d) { int v = step(u, d); return (v >= 0 && v != u && v == w.plainStep(u, d)) ? v : -1; };
        auto seen = [&](int u) { return !unk || w.lastSeen[u] >= 0; };
        std::vector<int> comp{qpSpawn}, in(w.N, 0), dng(w.N, -1), q;
        in[qpSpawn] = 1;
        for (size_t i = 0; i < comp.size(); i++)
            for (int d = 0; d < 4; d++)
            {
                int v = plain(comp[i], d);
                if (v >= 0 && !in[v] && seen(v) && wrapDist(v, qpSpawn) <= QPG_HOME)
                    in[v] = 1, comp.push_back(v);
            }
        const int es = w.sym > 0 ? w.mirror(qpSpawn) : -1;
        qpNarrow.assign(w.N, 0);
        for (int u : comp)
        {
            int deg = 0, mask = 0;
            for (int d = 0; d < 4; d++)
                if (plain(u, d) >= 0)
                    deg++, mask |= 1 << d;
            bool corr = deg <= 1 || (deg == 2 && (mask == 5 || mask == 10));
            bool enemy = es >= 0 && es != qpSpawn && wrapDist(u, es) < wrapDist(u, qpSpawn);
            if (corr || enemy)
                qpNarrow[u] = 1;
            if (corr || enemy || isMouth(u) || (!portalExit.empty() && portalExit[u]) || (!pfDepth.empty() && pfDepth[u] > 0))
                dng[u] = 0, q.push_back(u);
        }
        for (size_t i = 0; i < q.size(); i++)
            for (int d = 0; d < 4; d++)
            {
                int v = plain(q[i], d);
                if (v >= 0 && in[v] && dng[v] < 0)
                    dng[v] = dng[q[i]] + 1, q.push_back(v);
            }
        auto open2 = [&](int u) {
            int n = 0;
            for (int d = 0; d < 4; d++)
            {
                int v = plain(u, d);
                if (v < 0 || !seen(v))
                    continue;
                n++;
                for (int e = 0; e < 4; e++)
                {
                    int x = e != (d + 2) % 4 ? plain(v, e) : -1;
                    if (x >= 0 && seen(x))
                        n++;
                }
            }
            return n;
        };
        auto blockOf = [&](int u, int* b) {
            int e = plain(u, 1), so = plain(u, 2);
            if (e < 0 || so < 0)
                return false;
            int se = plain(e, 2);
            if (se < 0 || plain(so, 1) != se)
                return false;
            b[0] = u, b[1] = e, b[2] = se, b[3] = so;
            return true;
        };
        int bestA = -1;
        double bestS = -1e18;
        for (int u : comp)
        {
            int b[4];
            if (!blockOf(u, b))
                continue;
            int o = 0, g = QPG_GCAP, hd = 0, routes = 0;
            bool ok = true;
            for (int k = 0; k < 4; k++)
            {
                int x = b[k];
                if (!in[x] || dng[x] == 0)
                    ok = false;
                o += open2(x) >= 16 ? 1 : 0;
                g = std::min(g, dng[x] < 0 ? QPG_GCAP : dng[x]);
                hd = std::max(hd, wrapDist(x, qpSpawn));
                // the two ring tiles this corner touches: roomy exits
                for (int d = 0; d < 4; d++)
                {
                    int r = plain(x, d);
                    if (r >= 0 && r != b[0] && r != b[1] && r != b[2] && r != b[3] && in[r] && dng[r] != 0 && open2(r) >= 10)
                        routes++;
                }
            }
            if (!ok || routes < 2)
                continue;
            double food = 0;
            for (int v : comp)
                if (wrapDist(v, u) <= QPG_RAD + 1 && dng[v] != 0)
                    food += w.rate(v);
            double s = QPG_WG * g + QPG_WO * o - QPG_WH * hd + QPG_WF * std::min(1.0, food) + 0.3 * routes;
            if (s > bestS)
                bestS = s, bestA = u;
        }
        qpWeak = bestA < 0;
        if (qpWeak)
        {
            // no open block in view: hold the known tile furthest from danger, nearest her spawn
            int bg = -2;
            for (int u : comp)
            {
                int g = dng[u] < 0 ? 99 : dng[u];
                if (g > bg || (g == bg && wrapDist(u, qpSpawn) < wrapDist(bestA, qpSpawn)))
                    bg = g, bestA = u;
            }
        }
        if (dbg)
            std::fprintf(dbg, "QPG r%d anchor (%d,%d) weak=%d score=%.1f comp=%zu\n", round, bestA % w.W, bestA / w.W, qpWeak ? 1 : 0, bestS, comp.size());
        if (bestA == qpAnchor)
            return;
        qpAnchor = bestA;
        qpDist.assign(w.N, 99);
        q.assign(1, bestA);
        qpDist[bestA] = 0;
        {
            int b[4];
            if (!qpWeak && blockOf(bestA, b))
                for (int k = 1; k < 4; k++)
                    qpDist[b[k]] = 0, q.push_back(b[k]);
        }
        for (size_t i = 0; i < q.size(); i++)
            for (int d = 0; d < 4; d++)
            {
                int v = plain(q[i], d);
                if (v >= 0 && qpDist[v] == 99)
                    qpDist[v] = qpDist[q[i]] + 1, q.push_back(v);
            }
    }
    int qpAnchor = -1, qpHomeLeft = -1;
    bool qpFlee = false;
    std::vector<int> qpDist;
#if QUAL_KNOWN
    std::vector<char> qpInHome; // QUAL_QPARK_IN: the portal-free region of the queen's spawn tile
    // QUAL_QHOME: the queen's spawn tile (her head on the first turn of her process; a look-alike map may be adopted
    // some rounds later, so it is recorded on every map) and plain walking distance from it
    int qhSpawn = -1;
    bool qhFlee = false;
    std::vector<int> qhDist;
    double qhomeScore(int t) const
    {
        if (RP.qHomeR <= 0 || !amQueen() || qhDist.empty() || qhFlee)
            return 0.0;
        return -QUAL_QHOME_W * std::max(0, qhDist[t] - RP.qHomeR);
    }
#endif
    void qparkPrep()
    {
        qpFlee = false;
#if QUAL_KNOWN
        if (amQueen() && myHead >= 0 && qhSpawn < 0)
            qhSpawn = myHead;
        qhFlee = false;
        if (RP.qHomeR > 0 && amQueen() && myHead >= 0)
        {
            if (qhDist.empty())
            {
                qhDist.assign(w.N, 99);
                std::vector<int> q{qhSpawn};
                qhDist[qhSpawn] = 0;
                for (size_t i = 0; i < q.size(); i++)
                    for (int d = 0; d < 4; d++)
                    {
                        int v = step(q[i], d);
                        if (v >= 0 && v == w.plainStep(q[i], d) && qhDist[v] == 99)
                            qhDist[v] = qhDist[q[i]] + 1, q.push_back(v);
                    }
            }
            for (auto& o : segs)
                if (o.head && o.team != w.myTeam && wrapDist(o.tile, myHead) <= PM_QP_FLEE)
                    qhFlee = true; // an enemy head in reach: normal queen evasion decides
        }
        if (RP.qParkIn && RP.qPark == 0 && amQueen() && myHead >= 0)
        {
            if (qpInHome.empty())
            {
                // first turn of the queen's process = her spawn tile
                qpInHome.assign(w.N, 0);
                std::vector<int> q{myHead};
                qpInHome[myHead] = 1;
                for (size_t i = 0; i < q.size(); i++)
                    for (int d = 0; d < 4; d++)
                    {
                        int v = step(q[i], d);
                        if (v >= 0 && v == w.plainStep(q[i], d) && !qpInHome[v])
                            qpInHome[v] = 1, q.push_back(v);
                    }
            }
            if (!qpInHome[myHead])
                RP.qPark = 1; // she is through a portal: park in this region from now on
        }
#endif
        if (!qparkQueen() || myHead < 0)
            return;
        for (auto& o : segs)
            if (o.head && o.team != w.myTeam && wrapDist(o.tile, myHead) <= PM_QP_FLEE)
                qpFlee = true; // an enemy head in reach: normal queen evasion decides
        if (qpHomeLeft < 0)
            qpHomeLeft = (myHead % w.W) * 2 < w.W ? 1 : 0;
        if (RP.qPark == 3)
        {
            if (qpSpawn < 0)
                qpSpawn = myHead;
            if (!qpStarted && (!RP.qpLate || units >= QPG_UNITS || round >= QPG_FROM))
                qpStarted = true, qpUnits0 = units;
            if (qpStarted)
                qparkGenPlan();
            return;
        }
        if (RP.qPark != 1 || qpAnchor >= 0)
            return;
        // portal-free component of her head; anchor = the tile furthest from every portal mouth / exit
        auto plain = [&](int u, int d) { int v = step(u, d); return (v >= 0 && v == w.plainStep(u, d)) ? v : -1; };
        std::vector<int> comp{myHead}, home(w.N, -1), dng(w.N, -1), q;
        home[myHead] = 0;
        for (size_t i = 0; i < comp.size(); i++)
            for (int d = 0; d < 4; d++)
            {
                int v = plain(comp[i], d);
                if (v >= 0 && home[v] < 0)
                    home[v] = home[comp[i]] + 1, comp.push_back(v);
            }
        for (int u : comp)
            if (isMouth(u) || (!portalExit.empty() && portalExit[u]) || w.gmax[u] > 0)
                dng[u] = 0, q.push_back(u);
        for (size_t i = 0; i < q.size(); i++)
            for (int d = 0; d < 4; d++)
            {
                int v = plain(q[i], d);
                if (v >= 0 && dng[v] < 0)
                    dng[v] = dng[q[i]] + 1, q.push_back(v);
            }
        // open ground first (all 12 tiles within 2 plain steps exist: feeders and walls cannot box her), then distance
        auto open2 = [&](int u) {
            int n = 0;
            for (int d = 0; d < 4; d++)
            {
                int v = plain(u, d);
                if (v < 0)
                    continue;
                n++;
                for (int e = 0; e < 4; e++)
                    if (e != (d + 2) % 4 && plain(v, e) >= 0)
                        n++;
            }
            return n; // 4 + 12 (diagonals counted twice) on open ground
        };
        // a fully open 2x2 block (an L3 queen circles it for ever); its top-left tile is the anchor
        auto blockOf = [&](int u, int* b) {
            int e = plain(u, 1), so = plain(u, 2);
            if (e < 0 || so < 0)
                return false;
            int se = plain(e, 2);
            if (se < 0 || plain(so, 1) != se)
                return false;
            b[0] = u, b[1] = e, b[2] = se, b[3] = so;
            return true;
        };
        int bestA = myHead, bestO = -1, bestG = -1;
        bool bestBlk = false;
        for (int u : comp)
        {
            int b[4] = {u, u, u, u};
            bool blk = blockOf(u, b);
            int o = 0, g = 99;
            for (int x : b)
                o += open2(x) >= 16 ? 1 : 0, g = std::min(g, dng[x] < 0 ? 99 : dng[x]);
            if ((blk && !bestBlk) || (blk == bestBlk && (g > bestG || (g == bestG && (o > bestO || (o == bestO && home[u] < home[bestA]))))))
                bestA = u, bestO = o, bestG = g, bestBlk = blk;
        }
        qpAnchor = bestA;
        if (dbg)
            std::fprintf(dbg, "QPARK anchor (%d,%d) blk=%d open=%d far=%d comp=%zu\n", bestA % w.W, bestA / w.W, bestBlk ? 1 : 0, bestO, bestG, comp.size());
        qpDist.assign(w.N, 99);
        q.assign(1, bestA);
        qpDist[bestA] = 0;
        {
            int b[4];
            if (blockOf(bestA, b))
                for (int k = 1; k < 4; k++)
                    qpDist[b[k]] = 0, q.push_back(b[k]);
        }
        for (size_t i = 0; i < q.size(); i++)
            for (int d = 0; d < 4; d++)
            {
                int v = plain(q[i], d);
                if (v >= 0 && qpDist[v] == 99)
                    qpDist[v] = qpDist[q[i]] + 1, q.push_back(v);
            }
    }
    // steps a free-step sprint of the parked queen may never contain (the path search only vetoes its endpoint)
    bool qparkBan(int from, int d) const
    {
        if (!qparkQueen())
            return false;
        int t = step(from, d);
        if (t < 0)
            return false;
        if (RP.qPark == 1)
            return t != w.plainStep(from, d) || w.gmax[t] > 0 || (!pfDepth.empty() && pfDepth[t] > 0);
        if (RP.qPark == 3)
            return qpgOn() && (t != w.plainStep(from, d) || (!pfDepth.empty() && pfDepth[t] > pfDepth[from]));
        if (!(PM_MAZE_QSTAY || round < RP.kingSeedRound))
            return false;
        int x = t % w.W;
        return (qpHomeLeft ? x : w.W - 1 - x) >= PM_MAZE_QX;
    }
    // score term for the parked queen stepping onto t in direction d; sets dead for steps the park forbids
    double qparkScore(int t, int d, bool& dead) const
    {
        if (!qparkQueen() || myHead < 0)
            return 0.0;
        double s = 0;
        if (RP.qPark == 1)
        {
            if (t != w.plainStep(myHead, d))
            {
                // never through a portal (vault HitSelf deaths, blind exits); with an enemy head in reach it is
                // only a cost below the threat penalty, so she may still escape through one
                // (a vault is fatal at any length and so is any pocket once she has been fed)
                if (!qpFlee || myLen >= 6 || w.gmax[t] > 0)
                    dead = true, s -= PM_QP_PEN;
                else
                    s -= PM_QP_FLEEPEN;
            }
            else if (w.gmax[t] > 0 || (!pfDepth.empty() && pfDepth[t] > 0))
                dead = true, s -= PM_QP_PEN; // every pearl spawn on Portals is a vault or the 1-wide centre sock; no pockets at all
            for (auto& o : segs)
                if (o.head && o.team == w.myTeam && o.id != w.myId && wrapDist(o.tile, t) <= 1)
                    s -= PM_QP_ALLY; // an ally head next to her next tile can seal it
            if (qpAnchor >= 0 && round < qkFeedRound())
            {
                // hold the block; half weight on the best next tile so she turns back instead of drifting off
                int nb = 99;
                for (int e = 0; e < 4; e++)
                {
                    int v = step(t, e);
                    if (v >= 0 && v != myHead && v == w.plainStep(t, e))
                        nb = std::min(nb, qpDist[v]);
                }
                s -= PM_QP_PULL * (std::max(0, qpDist[t] - myLen / 4) + 0.5 * std::min(nb, qpDist[t] + 1));
            }
            else if (qpAnchor >= 0)
                s -= PM_QP_PULL_FED * std::max(0, qpDist[t] - 3 - myLen / 4);
        }
        else if (RP.qPark == 3)
        {
            if (!qpgOn())
                return 0.0;
            if (t != w.plainStep(myHead, d))
            {
                if (!qpFlee || myLen >= 6)
                    dead = true, s -= PM_QP_PEN; // never through a portal (blind exit, vaults)
                else
                    s -= PM_QP_FLEEPEN;
            }
            else if (!pfDepth.empty() && pfDepth[t] > pfDepth[myHead])
                dead = true, s -= PM_QP_PEN; // never into / deeper into a pocket
            for (auto& o : segs)
                if (o.head && o.team == w.myTeam && o.id != w.myId && wrapDist(o.tile, t) <= 1)
                    s -= PM_QP_ALLY;
            if (qpRescue())
                return s;
            if (!qpNarrow.empty() && qpNarrow[t] && !qpFlee)
                s -= QPG_NARROW;
            if (qpAnchor >= 0 && !qpFlee && qpDist[t] < 99)
            {
                bool pre = round < qkFeedRound();
                s -= (pre ? QPG_PULL : PM_QP_PULL_FED) * std::max(0, qpDist[t] - QPG_RAD - (pre ? 0 : 1) - myLen / 4);
            }
        }
        else if (PM_MAZE_QSTAY || round < RP.kingSeedRound)
        {
            int x = t % w.W, fx = qpHomeLeft ? x : w.W - 1 - x;
            if (fx >= PM_MAZE_QX)
                s -= PM_QP_PEN + 20.0 * (fx - PM_MAZE_QX); // the doorway column and the maze beyond it
        }
        return s;
    }
    // v37e (QGUARD ported from v37b) helpers: K(L) = ceil(L/4) + (L-2) = kamikaze reach
    static int kReach(int L) { return (L + 3) / 4 + std::max(0, L - 2); }
    bool qGuard() const { return QGUARD && amQueen() && (round >= QG_FROM || units >= QG_UNITS); }
    // QGUARD: largest split the queen may make (child k) so she keeps >= QG_MIN; < 2 = no split
    // v38q: QG_MIN floor off when the queen's kelp-sealed region is < QG_REGION_MIN tiles (Schooltime box)
    bool qFloorOff() const { return (TROPHY_QSPLIT || PM_QOS_QSPLIT) && RP.queenKeep > 0 && amQueen() && units <= RP.queenKeep && round < RP.queenKeepR; }
    int qgCap(int k) const
    {
        int c = (qGuard() && !qFloorOff() && !(QG_REGION_MIN > 0 && qRegion < QG_REGION_MIN)) ? std::min(k, myLen - QG_MIN) : k;
        if (qsmQueen())
            c = std::min(k, myLen - qsmFloor()); // R10 LANE_QSMALL: small floor replaces QG_MIN
        if (qboxLate())
            c = std::min(c, myLen - 3); // QBOX: late, no voluntary split leaves the queen below L3
        return c;
    }
    // QBOX: queen's kelp-only flood size (bodies ignored), capped at QBOX_REGION_CAP; set each decide()
    int qRegion = 1000;
    bool qboxLate() const { return QBOX && amQueen() && round >= QBOX_LATE; }
    void computeQRegion()
    {
        qRegion = 1000;
        if (!amQueen() || myHead < 0)
            return;
        std::vector<int> q{myHead};
        for (size_t i = 0; i < q.size() && static_cast<int>(q.size()) < QBOX_REGION_CAP; i++)
            for (int d = 0; d < 4; d++)
            {
                int v = step(q[i], d);
                if (v >= 0 && std::find(q.begin(), q.end(), v) == q.end())
                    q.push_back(v);
            }
        if (static_cast<int>(q.size()) < QBOX_REGION_CAP)
            qRegion = static_cast<int>(q.size());
    }
    // ONEKING is not ported to v37e: no voluntary-split ban beyond QGUARD
    // ROUND2 P6 ENDGAME_GUARD: our queen and our king protect the lead from that round
    bool egOrigOn() const
    {
        return ENDGAME_GUARD > 0 && round >= ENDGAME_GUARD && (amQueen() || (myLen >= KING_MIN_LEN && iAmKing()));
    }
    // ROUND6 QK_EG: the crowned queen (L >= QK_EG_MINLEN) uses the endgame-guard reach/veto (not its split ban)
    bool qkEgOn() const { return QK_EG && amQueen() && queenKingRound() && myLen >= QK_EG_MINLEN; }
    bool egOn() const { return egOrigOn() || qkEgOn(); }
    bool noVolSplit() const { return egOrigOn(); }
    void updateQsPhase()
    {
        if (!qsOn && (round >= QS_FROM || (QS_UNITS > 0 && units >= QS_UNITS) || (RP.qPark == 1 && amQueen()) || (QPG_SAFE0 && RP.qPark == 3 && qpStarted && amQueen())))
            qsOn = true;
    }
    // QUEEN_KING: on king maps our queen is the only king from the seed round while she is alive
    int qId = -1, qLen = 0, qTile = -1, qDir = 0, qRound = -100000, qHop = 99;
    bool queenAlive() const { return qkOn() && qId >= 0 && round - qRound <= QUEEN_ALIVE_MEM; }
    bool queenKingRound() const { return qkOn() && RP.kingDeclare && round >= RP.kingSeedRound && round >= RP.qkFrom; }
    // ROUND3 P7: first round the parked queen is fed (before it she holds her spot and wants no food)
    int qkFeedRound() const { return std::max(RP.feedStart, std::max(RP.kingSeedRound, RP.qkFrom)); }
    static int freeSteps(int L) { return (L + 3) / 4; } // 1.2.3: the first ceil(L/4) steps of a move are free
    void updateKingship()
    {
        if (qsmQueen())
        {
            kingSelf = false; // R10 LANE_QSMALL
            return;
        }
        if (qkOn() && amQueen() && queenKingRound())
        {
            kingSelf = true; // she is the king: feeders come to her, she stops splitting
            return;
        }
        if (qkOn() && !amQueen() && queenKingRound() && queenAlive())
        {
            kingSelf = false; // no rival kings while our queen lives
            return;
        }
        if (queenSafe())
            return; // the queen never self-crowns (a big king is a ram magnet); map modules (trauma pen) still may
        if (!RP.kingDeclare)
            return;
        if (KING_V2)
        {
            // up to two candidates grow side by side; the longest is the king
            int clear = std::max(myLen + KING_FOCUS_GAP, 2 * myLen); // one clearly longer king
            int bestK = KING_CONSENSUS ? bestKingLen(KC_STEP_MEM) : 0; // RC1b: one clearly longer king is enough
            if (kingSelf)
            {
                if (freshKings(myLen + 2) >= 2 || (KING_FOCUS && freshKings(clear - 1) >= 1) ||
                    (KING_CONSENSUS && bestK >= myLen + std::max(3, myLen / 4)))
                    kingSelf = false;
                return;
            }
            // CROWN_INHERIT (notes/forensics/portals, notes/portals_v31): a child born this turn with >= CROWN_INHERIT
            // segments is the body of a big dragon that just reverse-split (usually the king). It keeps the crown
            // unless a king longer than its parent (whose last broadcast said myLen + 2) is fresh, so it neither
            // feeds itself to the parent's stale king message nor goes back to small splitting.
            if (CROWN_INHERIT && birthRound == round && round >= RP.kingSeedRound && myLen >= CROWN_INHERIT &&
                freshKings(myLen + 2) == 0)
            {
                kingSelf = true;
                return;
            }
            if (round >= RP.kingSeedRound && freshKings(-1) < 2 && myLen >= 3 &&
                !(KING_FOCUS && freshKings(clear - 1) >= 1) && !(KING_CONSENSUS && bestK >= myLen + 2) &&
                rng.uni() < KING_DECLARE_P)
                kingSelf = true;
            return;
        }
        bool heard = kingId >= 0 && round - kingRound <= 8;
        if (kingSelf)
        {
            if (heard && (kingLen > myLen + KING_STEPDOWN_MARGIN || (kingLen >= myLen && kw10(kingId) < kw10(w.myId))))
                kingSelf = false;
            return;
        }
        if (round >= RP.kingSeedRound && !heard && myLen >= RP.kingDeclareMinLen && rng.uni() < KING_DECLARE_P)
            kingSelf = true;
    }
    bool iAmKing() const
    {
        if (qsmQueen())
            return false; // R10 LANE_QSMALL: never the king, never fed
        if (qkOn() && queenKingRound() && (amQueen() || queenAlive()))
            return amQueen();
        if (queenSafe())
            return kingSelf; // only a map-module crown, never by length
        if (RP.kingDeclare)
            return kingSelf || (myLen >= KING_MIN_LEN && myLen >= kingLen);
        return myLen >= KING_MIN_LEN && myLen >= kingLen;
    }
    bool feedPhase() const { return round >= RP.feedStart; }

    void emitSonar()
    {
        if (PORTAL_WARN && pending.size() <= 1)
        {
            int at = pending.empty() ? myHead : pending.back();
            if (at >= 0 && at < w.N && portalExit[at])
                for (int d = 0; d < 4; d++)
                {
                    int v = step(at, d);
                    if (v >= 0 && v != w.plainStep(at, d))
                        warnDirs[d] = true;
                }
        }
        if (UNK_EXPLORE && !w.known && pending.size() <= 1 && !w.portalSide.empty() && !qNoUnkPortal())
        {
            int at = pending.empty() ? myHead : pending.back();
            int face = pending.empty() ? myDir : lastMoveDir;
            for (int d = 0; d < 4; d++)
                if (at >= 0 && w.portalSide[at * 4 + d] && step(at, d) < 0 && d != (face + 2) % 4)
                    warnDirs[d] = true; // knock: the ray passes the unknown portal
        }
        uint64_t warn = 0;
        bool anyWarn = warnDirs[0] || warnDirs[1] || warnDirs[2] || warnDirs[3];
        if (anyWarn)
            warn = encodeWarn(pending.empty() ? myHead : pending.back(), round);
        bool probing = PORTAL_PROBE_SOLO && anyWarn; // keep the echo counts clean (notes/20)
        if (!probing && iAmKing() && (round >= KING_BROADCAST_START || kingSelf))
        {
            uint64_t m = KING_POS_POSTMOVE && !pending.empty()
                             ? encodeKing(pending.back(), myLen, w.myId, 0, lastMoveDir, round) // where we are after this move
                             : encodeKing(myHead, myLen, w.myId, 0, myDir, round);
            for (int d = 0; d < 4; d++)
                if (!warnDirs[d])
                    out += std::string("SONAR ") + DIRC[d] + " " + std::to_string(sonarOut(m)) + "\n";
        }
        else if (uint64_t lm = 0; !probing && lhOurDead() && (!haveRelay || round % 3 == 0) &&
                                  (round % 2 == 0 || !lhOn()) && lhWord(lm))
        {
            // v68 LATE_HUNT: "our queen is dead" notice (even rounds; odd rounds carry enemy-queen sightings)
            for (int d = 0; d < 4; d++)
                if (!warnDirs[d])
                    out += std::string("SONAR ") + DIRC[d] + " " + std::to_string(sonarOut(lm)) + "\n";
        }
        else if (!probing && haveRelay)
        {
            for (int d = 0; d < 4; d++)
                if (!warnDirs[d])
                    out += std::string("SONAR ") + DIRC[d] + " " + std::to_string(sonarOut(relayMsg)) + "\n";
        }
        else if (uint64_t qm = 0; !probing && (QSTATE || EQ_HUNT || lhOurDead()) && qstWord(qm))
        {
            // QSTATE: queen beacon / relay / enemy-queen sighting / "enemy queen dead" notice
            for (int d = 0; d < 4; d++)
                if (!warnDirs[d])
                    out += std::string("SONAR ") + DIRC[d] + " " + std::to_string(sonarOut(qm)) + "\n";
        }
        else if (uint64_t bm = 0; LATE_HUNT && !anyWarn && !lhOurDead() && !(MATCH_STRICT && w.msDead) &&
                                  !(CONS_R && CONS_BEACON) && lhWord(bm))
        {
            // v68 LATE_HUNT: our queen's beacon / its sparse relay, fully idle turns only (no v61 word displaced)
            for (int d = 0; d < 4; d++)
                out += std::string("SONAR ") + DIRC[d] + " " + std::to_string(sonarOut(bm)) + "\n";
        }
        else if (!probing && CONS_R && CONS_BEACON && consMapOn() && round >= CONS_R - CONS_BEACON_LEAD &&
                 myLen >= CONS_BEACON_MIN)
        {
            // CONS status beacon on the idle rays: where we are after this move, how long we are
            uint64_t m = pending.empty() ? encodeKing(myHead, myLen, w.myId, 0, myDir, round, STATUS_SECRET)
                                         : encodeKing(pending.back(), myLen, w.myId, 0, lastMoveDir, round, STATUS_SECRET);
            for (int d = 0; d < 4; d++)
                if (!warnDirs[d])
                    out += std::string("SONAR ") + DIRC[d] + " " + std::to_string(sonarOut(m)) + "\n";
        }
        else if (!probing && CONS_R && CONS_BEACON && haveConsRelay && consMapOn() && round >= CONS_R - CONS_BEACON_LEAD)
        {
            for (int d = 0; d < 4; d++)
                if (!warnDirs[d])
                    out += std::string("SONAR ") + DIRC[d] + " " + std::to_string(sonarOut(consRelayMsg)) + "\n";
        }
        for (int d = 0; d < 4; d++)
            if (warnDirs[d])
                out += std::string("SONAR ") + DIRC[d] + " " + std::to_string(sonarOut(warn)) + "\n";
        if (MATCH_STRICT && w.msDead && !anyWarn && (out.find("SPLIT ") != std::string::npos || round < MS_GOSSIP_R) &&
            out.find("SONAR ") == std::string::npos)
        {
            uint64_t m = encodeUnseen(); // pass "unseen map" to the child (and anyone in line); split turns only
            for (int d = 0; d < 4; d++)
                out += std::string("SONAR ") + DIRC[d] + " " + std::to_string(sonarOut(m)) + "\n";
        }
#if QUAL_KNOWN
        if (QUAL_GOSSIP && qualSure() && !anyWarn && (out.find("SPLIT ") != std::string::npos || round < QUAL_GOSSIP_R) &&
            out.find("SONAR ") == std::string::npos)
        {
            uint64_t m = encodeQualMap(); // name the map for the child (split turns) and for allies in line (early idle turns)
            for (int d = 0; d < 4; d++)
                out += std::string("SONAR ") + DIRC[d] + " " + std::to_string(sonarOut(m)) + "\n";
        }
#endif
        if (PORTAL_ECHO_GUARD)
        {
            // remember what our warn rays probed: next turn's echo counts tell us
            // whether someone was standing on (or just past) the exit (notes/17)
            probeMask = 0;
            for (int d = 0; d < 4; d++)
                if (warnDirs[d])
                    probeMask |= 1 << d;
            probeRays = 0;
            for (size_t q = out.find("SONAR "); q != std::string::npos; q = out.find("SONAR ", q + 1))
                probeRays++;
            probeTile = pending.empty() ? myHead : pending.back();
            probeRound = round;
        }
        warnDirs[0] = warnDirs[1] = warnDirs[2] = warnDirs[3] = false;
    }
    bool warnDirs[4] = {false, false, false, false};
    int probeTile = -1, probeRound = -1000, probeMask = 0, probeRays = 0;
    bool echoBodyDir[4] = {false, false, false, false};
    int holdStreak = 0;
    // ECHO_EXIT_HOLD (notes/forensics/portals, notes/portals_v31): a big dragon whose only way on is a blind
    // portal crossing into a body its own probe echoed last turn splits 2 off its tail and stays, so the warn
    // ray re-probes the same exit next turn (the blocker is usually a small ally passing through).
    bool tryEchoHold(int bestD, double otherBest)
    {
        if (!ECHO_EXIT_HOLD || bestD < 0 || myLen < ECHO_EXIT_HOLD || units >= w.unitLimit || holdStreak >= ECHO_HOLD_MAX)
            return false;
        if (noVolSplit() || qgCap(2) < 2 || qsrBlock(2))
            return false; // v37e QGUARD (ONEKING not ported); v39 QSPLIT_ROOM
        if (!echoBodyDir[bestD] || otherBest >= -100)
            return false;
        int t = step(myHead, bestD);
        if (t < 0 || visible[t] || t == w.plainStep(myHead, bestD))
            return false;
        r2log("spH", 2);
        out += "SPLIT 2\n";
        pending.clear();
        pendingSplit = true;
        holdStreak++;
        if (dbg)
            std::fprintf(dbg, "  -> echo hold (split 2)\n");
        return true;
    }

    // Tile a feeder should die on: a couple of steps in front of the king.
    // ROUND3 P7: on a per-map queen-king map the crowned queen is fed whatever her length (a parked queen is L3)
    bool feedsQueen() const
    {
        return RP.queenKing && !amQueen() && queenKingRound() && queenAlive() && kingId >= 0 && kw10(kingId) <= 1;
    }
    // walking distance a -> b over static tiles (bodies ignored), capped: maxd + 1 = further / walled off
    int walkDist(int a, int b, int maxd) const
    {
        if (a == b)
            return 0;
        std::vector<int> q{a}, dd{0};
        for (size_t i = 0; i < q.size(); i++)
        {
            if (dd[i] >= maxd)
                continue;
            for (int d = 0; d < 4; d++)
            {
                int v = step(q[i], d);
                if (v < 0 || std::find(q.begin(), q.end(), v) != q.end())
                    continue;
                if (v == b)
                    return dd[i] + 1;
                q.push_back(v);
                dd.push_back(dd[i] + 1);
            }
        }
        return maxd + 1;
    }
    int feedTarget() const
    {
        if (kingId < 0 || kingTile < 0)
            return -1;
        int t = kingTile;
        for (int i = 0; i < FEED_AHEAD; i++)
        {
            int v = step(t, kingDir);
            if (v < 0)
                break;
            t = v;
        }
        return t;
    }

    int wrapDist(int a, int b) const
    {
        int dx = std::abs(a % w.W - b % w.W), dy = std::abs(a / w.W - b / w.W);
        return std::min(dx, w.W - dx) + std::min(dy, w.H - dy);
    }

    // UNK_KING: every dragon computes the same shrinking reserve (14 at r300 -> 3 at r490)
    int feedReserveNow() const
    {
        if (UNK_KING && (!w.known || (SPRINT_KING_FULL && ((SPRINT_KNOWN && isSprintMap(w.known->name)) || w.qualOn()))))
            return std::max(3, 14 - (std::clamp(round, 300, 490) - 300) * 11 / 190);
        return RP.feedReserve;
    }
    bool shouldFeed() const
    {
        if (FEED_STALE_GUARD && myLen >= 8 && birthRound >= 0 && round - birthRound < 3)
            return false; // a big fresh split child must not obey its parent's stale king message
        // FEED_FRESH: only feed a king we heard from recently (a dead king's remembered
        // length pulled our real longest dragon into suicide, e.g. L21 at r435)
        if (FEED_FRESH > 0 && (kingId < 0 || round - kingRound > FEED_FRESH || kingLen < myLen + 2))
            return false;
        // RC2: never feed a lesser king (< KC_FEED_FRAC of the longest heard in KC_FEED_MEM rounds)
        if (KING_CONSENSUS && KING_V2 && RP.kingDeclare && kingLen < KC_FEED_FRAC * bestKingLen(KC_FEED_MEM) && !feedsQueen())
            return false;
        if (RP.qkCap > 0 && feedsQueen() && kingLen >= RP.qkCap)
            return false; // ROUND3 P7: she is long enough; a longer queen only coils herself in and is a bigger ram prize
        if (KING_V2 && RP.kingDeclare)
            return FEED_ENABLE && feedPhase() && kingId >= 0 && (kingLen >= myLen + 2 || feedsQueen()) && !iAmKing() &&
                   units > feedReserveNow() &&
                   myLen <= (round >= RP.mergeRound ? 1000 : round >= RP.feed6Round ? 6 : KING_V2_FEED_LEN);
        return FEED_ENABLE && feedPhase() && kingId >= 0 && kingLen >= myLen + 2 && !iAmKing() &&
               (units > RP.feedReserve || (RP.lateFeedRound > 0 && round >= RP.lateFeedRound && units > 1)) && myLen <= FEED_MAX_LEN;
    }

    // ---- CONSOLIDATION (params.hpp CONS_*): local merge of small dragons into longer allies
    std::vector<KingInfo> statusSeen; // CONS status beacons heard
    bool haveConsRelay = false;
    uint64_t consRelayMsg = 0;
    bool consActive = false, consHostVis = false, consFirst = false;
    int consHostId = -1, consHostTile = -1, consHostDir = 0, consHostLen = 0, consTarget = -1;
    bool consMapOn() const
    {
        if (!CONS_R)
            return false;
        if (CONS_MAPS == 0)
            return RP.kingRace;
        if (CONS_MAPS == 1)
            return RP.kingDeclare;
        return true;
    }
    // would-be host: long enough to be fed, so it keeps its body together
    bool consHostKeep() const
    {
        return CONS_NOSPLIT && consMapOn() && round >= CONS_R && myLen >= CONS_HOST_MIN;
    }
    void pickConsHost()
    {
        consActive = consHostVis = consFirst = false;
        consHostId = consHostTile = consTarget = -1;
        if (!consMapOn() || round < CONS_R || myLen > CONS_MAXLEN || kingSelf || iAmKing())
            return;
        if (units <= std::max(CONS_KEEP, feedReserveNow()) || threatAt[myHead] > 0)
            return;
        int need = std::max(CONS_HOST_MIN, myLen + CONS_GAP);
        struct C
        {
            int id, len, tile, dir;
            bool vis;
        };
        C cand[96];
        int nc = 0;
        auto add = [&](int id, int len, int tile, int dir, bool vis) {
            for (int i = 0; i < nc; i++)
                if (cand[i].id == id)
                {
                    cand[i].len = std::max(cand[i].len, len);
                    if (vis)
                        cand[i].tile = tile, cand[i].dir = dir, cand[i].vis = true;
                    return;
                }
            if (nc < 96)
                cand[nc++] = {id, len, tile, dir, vis};
        };
        for (auto& sg : segs)
            if (sg.head && sg.team == w.myTeam && sg.id != w.myId)
            {
                int n = 0; // visible segments: a lower bound on its length
                for (auto& s2 : segs)
                    if (s2.id == sg.id)
                        n++;
                add(kw10(sg.id), n, sg.tile, sg.facing, true);
            }
        for (auto& k : kingsSeen)
            if (round - k.round <= CONS_MEM && k.id != kw10(w.myId))
                add(k.id, k.len, k.tile, k.dir, false);
        for (auto& k : statusSeen)
            if (round - k.round <= CONS_MEM)
                add(k.id, k.len, k.tile, k.dir, false);
        // one king, not a tier: only hosts within CONS_HOST_FRAC of the longest ally we know of
        // (the local-host version fed 4 big dragons evenly and lost the king race)
        int longest = KING_CONSENSUS ? bestKingLen(KC_FEED_MEM) : 0;
        for (int i = 0; i < nc; i++)
            longest = std::max(longest, cand[i].len);
        double bestC = 1e18;
        int bi = -1;
        for (int i = 0; i < nc; i++)
        {
            if (cand[i].len < need || cand[i].tile < 0 || cand[i].len < CONS_HOST_FRAC * longest)
                continue;
            int dd = wrapDist(myHead, cand[i].tile);
            if (dd > CONS_RANGE)
                continue;
            double c = dd - CONS_LEN_W * cand[i].len;
            if (c < bestC)
                bestC = c, bi = i;
        }
        if (bi < 0)
            return;
        const C& h = cand[bi];
        consActive = true;
        consHostId = h.id, consHostLen = h.len, consHostTile = h.tile, consHostDir = h.dir, consHostVis = h.vis;
        // first in line: the closest of our visible heads to the host (ties: lower id)
        int dk = wrapDist(myHead, h.tile);
        consFirst = true;
        for (auto& o : segs)
            if (o.head && o.team == w.myTeam && o.id != w.myId && kw10(o.id) != h.id)
            {
                int n = 0; // only other small heads (would-be feeders) queue with us
                for (auto& s2 : segs)
                    if (s2.id == o.id)
                        n++;
                if (n > CONS_MAXLEN)
                    continue;
                int od = wrapDist(o.tile, h.tile);
                if (od < dk || (od == dk && o.id < w.myId))
                    consFirst = false;
            }
        // walk to 2 ahead of the host (1 ahead, then its sides, when that is kelp or occupied)
        int a1 = step(h.tile, h.dir), a2 = a1 >= 0 ? step(a1, h.dir) : -1;
        int sl = step(h.tile, (h.dir + 3) % 4), sr = step(h.tile, (h.dir + 1) % 4);
        for (int t : {a2, a1, sl, sr, h.tile})
            if (t >= 0 && (t == myHead || occId[t] < 0 || t == h.tile))
            {
                consTarget = t;
                break;
            }
    }
    // die in the host's path when it is our turn in line (returns true when the suicide is emitted)
    bool tryConsFeed()
    {
        if (!consActive || !consHostVis || !consFirst)
            return false;
        int k = consHostTile, f = consHostDir;
        int dk = wrapDist(myHead, k);
        if (dk > 3)
            return false;
        int a1 = step(k, f), a2 = a1 >= 0 ? step(a1, f) : -1;
        int sl = step(k, (f + 3) % 4), sr = step(k, (f + 1) % 4);
        bool spot = myHead == a1 || myHead == a2 || myHead == sl || myHead == sr;
        if (CONS_LOOSE && !spot)
        {
            // in front of the host (not behind its head), close to where it goes next
            int ref = a2 >= 0 ? a2 : a1 >= 0 ? a1 : k;
            spot = dk >= 1 && wrapDist(myHead, ref) <= 2 && wrapDist(myHead, ref) <= dk;
        }
        if (!spot)
            return false;
        for (auto& o : segs)
            if (o.head && o.team != w.myTeam && wrapDist(o.tile, k) <= CONS_ENEMY_R)
                return false; // the corpse would feed them
        for (int t2 : {a1, a2, sl, sr})
            if (t2 >= 0 && visible[t2] && w.pearlMem[t2] && t2 != myHead)
                return false; // the last meal is still lying there
        if (CONS_STEAL)
        {
            // precise: no other small ally head is nearer than the host to where our head pearl lands
            // (43% of the first version's pearls went to bystanders)
            for (auto& o : segs)
                if (o.head && o.team == w.myTeam && o.id != w.myId && kw10(o.id) != consHostId &&
                    wrapDist(o.tile, myHead) <= dk)
                {
                    int n = 0;
                    for (auto& s2 : segs)
                        if (s2.id == o.id)
                            n++;
                    if (n <= CONS_MAXLEN + 2)
                        return false;
                }
        }
        out += std::string("MOVE ") + DIRC[(myDir + 2) % 4] + "\n";
        pending.clear();
        if (dbg)
            std::fprintf(dbg, "  -> cons feed host=%d L%d\n", consHostId, consHostLen);
#if CONS_TRACE
        if (const char* ct = std::getenv("CONS_TRACE_DIR"))
            if (FILE* tf = std::fopen((std::string(ct) + "/" + std::to_string(w.myId) + ".txt").c_str(), "a"))
            {
                std::fprintf(tf, "%d %d FEED host%d hl%d\n", round, w.myId, consHostId, consHostLen);
                std::fclose(tf);
            }
#endif
        return true;
    }

    // BFS distance from each enemy head over tiles free now, up to 6 steps.
    // threatAt[t] = how many enemy heads can reach t before our next turn,
    // given their visible length limits how far they can sprint.
    std::vector<int> threatAt, threatDist, tq;
    std::vector<int> sprintThreatAt;       // SMALL_SPRINT_THREAT: 2-step sprint reach of enemy heads (len >= 3)
    int localAllies = 0, localEnemies = 0; // heads in our view (allies include us)
    std::vector<int> threatPaidAt; // THREAT_FREE: reachable only with 1-2 paid steps
    // S4 QUEEN_LOOK: qlSlack[v] = min over enemy heads of (BFS dist to v) - 2F: <= 0 means a head can reply
    // (F free steps) and then ram v on its next turn. Unreached tiles keep INF.
    std::vector<int> qlSlack, qlDist, qlQ;
    void computeQueenLook()
    {
        qlSlack.assign(w.N, INF);
        if (static_cast<int>(qlDist.size()) != w.N)
            qlDist.assign(w.N, INF);
        for (auto& s : segs)
        {
            if (!s.head || s.team == w.myTeam)
                continue;
            int Lv = enemyVisibleLength(s.id);
            if (!enemyTailSeen(s))
                Lv = std::max(Lv, 4);
            int R2 = 2 * freeSteps(Lv);
            qlQ.clear();
            qlQ.push_back(s.tile);
            qlDist[s.tile] = 0;
            for (size_t i = 0; i < qlQ.size(); i++)
            {
                int u = qlQ[i];
                qlSlack[u] = std::min(qlSlack[u], qlDist[u] - R2);
                if (qlDist[u] >= R2)
                    continue;
                for (int d = 0; d < 4; d++)
                {
                    int v = step(u, d);
                    if (v < 0 || qlDist[v] != INF || (freeT[v] > 2 && v != myHead))
                        continue; // bodies that stay put block it
                    qlDist[v] = qlDist[u] + 1;
                    qlQ.push_back(v);
                }
            }
            for (int u : qlQ)
                qlDist[u] = INF;
        }
    }
    // the queen at t after the worst reply: exits a head can't reach by reply + ram
    int queenSafeExits(int t)
    {
        int n = 0;
        for (int d = 0; d < 4; d++)
        {
            int u = step(t, d);
            if (u < 0 || u == myHead || freeT[u] > 2)
                continue;
            if (qlSlack[u] > 0)
                n++;
        }
        return n;
    }
    // v44 QEXIT1: the queen stepping onto t walks a 1-wide corridor (static onward exits == 1) for up to QX_LEN
    // tiles. Penalty when a corridor tile is held by another body that won't clear in time, or another head
    // (ally or enemy) is within QX_R of it: an ally crossing her only exit boxed her in most late Maze deaths (V44.md).
    double qxPen(int t)
    {
        int prev = myHead, cur = t;
        for (int k = 1; k <= QX_LEN; k++)
        {
            int nOn = 0, on = -1;
            for (int d = 0; d < 4; d++)
            {
                int v = step(cur, d);
                if (v < 0 || v == prev || v == cur)
                    continue;
                nOn++, on = v;
            }
            if (nOn >= 2)
                return 0.0; // a junction: she can turn off
            if (nOn == 0)
                return QX_PEN; // static dead end
            if (occId[on] >= 0 && occId[on] != w.myId && freeT[on] > k + 1)
                return QX_PEN; // the only way on is blocked longer than she can wait
            for (auto& o : segs)
                if (o.head && o.id != w.myId && wrapDist(o.tile, on) <= QX_R)
                    return QX_PEN * (o.team == w.myTeam ? 1.0 : QX_ENEMY_MULT);
            prev = cur, cur = on;
        }
        return 0.0;
    }
    // v36q: tiles reachable from t with our whole body as a wall, capped (small = t closes a loop on her)
    std::vector<int> qoSeen, qoQ;
    int qoStamp = 0;
    int queenOpen(int t, int cap)
    {
        if (static_cast<int>(qoSeen.size()) != w.N)
            qoSeen.assign(w.N, 0);
        if (++qoStamp == (1 << 30))
        {
            std::fill(qoSeen.begin(), qoSeen.end(), 0);
            qoStamp = 1;
        }
        for (int b : trail)
            if (b >= 0 && b < w.N)
                qoSeen[b] = qoStamp;
        if (t < 0 || qoSeen[t] == qoStamp)
            return 0;
        qoQ.clear();
        qoQ.push_back(t);
        qoSeen[t] = qoStamp;
        for (size_t i = 0; i < qoQ.size() && static_cast<int>(qoQ.size()) < cap; i++)
            for (int d = 0; d < 4; d++)
            {
                int v = step(qoQ[i], d);
                if (v < 0 || qoSeen[v] == qoStamp || freeOther[v] > 2)
                    continue;
                qoSeen[v] = qoStamp;
                qoQ.push_back(v);
            }
        return std::min(cap, static_cast<int>(qoQ.size()));
    }
    // DIST veto: some visible enemy head ends within F(L)+1 (Manhattan, walls ignored) of t
    bool queenTooClose(int t)
    {
        for (auto& o : segs)
            if (o.head && o.team != w.myTeam)
            {
                int Lv = enemyVisibleLength(o.id);
                if (!enemyTailSeen(o))
                    Lv = std::max(Lv, 4);
                if (wrapDist(o.tile, t) <= freeSteps(Lv) + 1)
                    return true;
            }
        return false;
    }
    // the enemy's tail is in view (so its visible length is its real length)
    bool enemyTailSeen(const Seg& s)
    {
        for (int j = 0; j < static_cast<int>(segs.size()); j++)
        {
            if (segs[j].id != s.id || segs[j].head || !tailIsVisibleTail(j))
                continue;
            bool hasPrev = false; // some segment of it steps into j: j isn't the tail
            for (auto& o : segs)
                if (o.id == s.id && !o.head && step(o.tile, o.facing) == segs[j].tile)
                    hasPrev = true;
            if (!hasPrev)
                return true;
        }
        return false;
    }
    void computeThreats()
    {
        threatAt.assign(w.N, 0);
        threatPaidAt.assign(w.N, 0);
        if (SMALL_SPRINT_THREAT)
        {
            sprintThreatAt.assign(w.N, 0);
            localAllies = localEnemies = 0;
            for (auto& s : segs)
                if (s.head)
                    (s.team == w.myTeam ? localAllies : localEnemies)++;
            for (auto& s : segs)
            {
                if (myLen >= KING_MIN_LEN || !s.head || s.team == w.myTeam || enemyVisibleLength(s.id) < 3)
                    continue;
                if (eqHuntOn && EQH_NOTHREAT && s.id <= 1)
                    continue; // v47 EQ_HUNT: her ram on a hunter trades her away
                for (int d1 = 0; d1 < 4; d1++)
                {
                    int a = step(s.tile, d1);
                    if (a < 0 || freeT[a] > 1)
                        continue; // first sprint step must be free
                    for (int d2 = 0; d2 < 4; d2++)
                    {
                        int b = step(a, d2);
                        if (b >= 0 && b != s.tile)
                            sprintThreatAt[b]++;
                    }
                }
            }
        }
        if (static_cast<int>(threatDist.size()) != w.N)
            threatDist.assign(w.N, INF);
        for (auto& s : segs)
        {
            if (!s.head || s.team == w.myTeam)
                continue;
            if (eqHuntOn && EQH_NOTHREAT && s.id <= 1)
                continue; // v47 EQ_HUNT: her ram on a hunter trades her away
            int maxReach = myLen >= KING_MIN_LEN ? KING_THREAT_REACH : MAX_THREAT_REACH;
            int reach = std::max(1, enemyVisibleLength(s.id) - 1);
            if (THREAT_TAIL_UNKNOWN > 0 && myLen >= KING_MIN_LEN && reach < THREAT_TAIL_UNKNOWN)
            {
                // its tail is out of view: it may be longer (and sprint further) than it looks
                bool tailSeen = false;
                for (int j = 0; j < static_cast<int>(segs.size()) && !tailSeen; j++)
                {
                    if (segs[j].id != s.id || segs[j].head || !tailIsVisibleTail(j))
                        continue;
                    bool hasPrev = false; // some segment of it steps into j: j isn't the tail
                    for (auto& o : segs)
                        if (o.id == s.id && !o.head && step(o.tile, o.facing) == segs[j].tile)
                            hasPrev = true;
                    tailSeen = !hasPrev;
                }
                if (!tailSeen)
                    reach = THREAT_TAIL_UNKNOWN;
            }
            reach = std::min(reach, maxReach);
            int paidReach = 0; // THREAT_FREE: tiles beyond the free reach that 1-2 paid steps cover
            if (queenSafe() || THREAT_FREE)
            {
                int Lv = enemyVisibleLength(s.id);
                if (!enemyTailSeen(s))
                    Lv = std::max(Lv, queenSafe() ? 4 : THREAT_TAIL_UNKNOWN + 1);
                int F = freeSteps(Lv);
                if (queenSafe())
                {
                    // uncapped: full threat inside its free reach, the paid tier one step beyond (an L2 can't pay)
                    reach = F;
                    paidReach = std::min(F + 1, F + std::max(0, Lv - 2));
                }
                else
                {
                    reach = std::min(F, myLen >= KING_MIN_LEN ? KING_THREAT_REACH : THREAT_FREE_SMALL_CAP);
                    paidReach = std::min(F + 2, F + std::max(0, Lv - 2));
                }
            }
            if (KREACH && (myLen >= KREACH_MINLEN || (KREACH_QUEEN && amQueen())))
            {
                // v37a step 3: kamikaze reach K(Lv) = F + (Lv-2) (a head-on kills both, so paid steps are free for it)
                int Lv = enemyVisibleLength(s.id);
                if (!enemyTailSeen(s))
                    Lv = std::max(Lv, 3);
                int kr = std::min(freeSteps(Lv) + std::max(0, Lv - 2), static_cast<int>(KR_CAP));
                if (amQueen())
                    reach = std::max(reach, kr); // full strength for the queen
                else
                    paidReach = std::max(paidReach, kr);
            }
            if ((QK_EG >= 2 && qkEgOn()) || (QK_EG_KING && !amQueen() && myLen >= QK_EG_KINGLEN && iAmKing()))
            {
                // ROUND6 QK_EG=2 / QK_EG_KING: the crowned queen (king) sees the kamikaze reach K(Lv) up to QK_EG_KRCAP
                // (unseen tail: Lv >= QK_EG_UNSEEN_LEN) as full threat; a head that closed in on us two rounds in a row
                // gets one more step (lunge set-up: hunters close from 6-7 to 2-3 over 3-4 rounds, then strike)
                int Lv = enemyVisibleLength(s.id);
                if (!enemyTailSeen(s))
                    Lv = std::max(Lv, static_cast<int>(QK_EG_UNSEEN_LEN));
                int kr = std::min(kReach(Lv), static_cast<int>(QK_EG_KRCAP));
                if (QK_EG_TREND && myHead >= 0)
                {
                    auto& tr = qkTrend[s.id];
                    const int dd = wrapDist(myHead, s.tile);
                    if (tr[0] != round)
                    {
                        tr[2] = (tr[0] == round - 1 && dd < tr[1]) ? tr[2] + 1 : 0;
                        tr[0] = round, tr[1] = dd;
                    }
                    if (tr[2] >= 2)
                        kr++;
                }
                reach = std::max(reach, kr);
            }
            if (MIDSIZE && (MS_SAFE & 1) && myLen >= 5 && msUnit())
            {
                // R11 MIDSIZE bit 1: a mid-size unit sees the kamikaze reach K(Lv) (capped) as full threat
                int Lv = enemyVisibleLength(s.id);
                if (!enemyTailSeen(s))
                    Lv = std::max(Lv, 3);
                reach = std::max(reach, std::min(freeSteps(Lv) + std::max(0, Lv - 2), static_cast<int>(MS_KRCAP)));
            }
            if (KREACH_KING && myLen >= KING_MIN_LEN)
            {
                // v37a step 7: a big enemy rams our king for free from F(Lv) > KING_THREAT_REACH
                int Lv = enemyVisibleLength(s.id);
                if (Lv >= 17)
                    reach = std::max(reach, freeSteps(Lv));
            }
            if (QE_KR == 1 && qeKrOn())
            {
                // TOP4_HORSE QE_KR: before QS_FROM the queen sees each visible enemy head's kamikaze reach
                // K(Lv) = F(Lv) + (Lv-2) (a head-on kills both, so its paid steps cost it nothing), capped
                int Lv = enemyVisibleLength(s.id);
                if (!enemyTailSeen(s))
                    Lv = std::max(Lv, 3);
                reach = std::max(reach, std::min(freeSteps(Lv) + std::max(0, Lv - 2), static_cast<int>(QE_KR_CAP)));
            }
            if (QE_KR >= 2 && qeKrOn())
            {
                // TOP4_HORSE QE_KR=2: pearl-aware kamikaze reach. A paid step onto a pearl costs no length
                // (tail stays, then one segment goes), so an L3 crossing pearls lunges 3-4 tiles, not 2.
                int Lv = enemyVisibleLength(s.id);
                if (!enemyTailSeen(s))
                    Lv = std::max(Lv, 3);
                const int F = freeSteps(Lv), budget = std::max(0, Lv - 2), cap = static_cast<int>(QE_KR_CAP);
                std::vector<std::pair<int, int>> cur{{s.tile, 0}}, nxt; // (tile, paid used)
                std::vector<int> best(w.N, INF);
                best[s.tile] = 0;
                for (int st = 1; st <= cap && !cur.empty(); st++)
                {
                    nxt.clear();
                    for (auto [u, pu] : cur)
                        for (int d = 0; d < 4; d++)
                        {
                            int v = step(u, d);
                            if (v < 0 || v == s.tile)
                                continue;
                            int np = pu + (st > F ? 1 : 0) - (fsEats(v) ? 1 : 0); // a pearl on any step adds one segment
                            if (np > budget || np >= best[v])
                                continue;
                            if (best[v] == INF)
                                threatAt[v]++;
                            best[v] = np;
                            if (freeT[v] <= 1)
                                nxt.push_back({v, np});
                        }
                    std::swap(cur, nxt);
                }
            }
            int bfsReach = std::max(reach, paidReach);
            tq.clear();
            tq.push_back(s.tile);
            threatDist[s.tile] = 0;
            for (size_t qi = 0; qi < tq.size(); qi++)
            {
                int u = tq[qi];
                if (threatDist[u] >= bfsReach)
                    continue;
                for (int d = 0; d < 4; d++)
                {
                    int v = step(u, d);
                    if (v < 0 || threatDist[v] != INF)
                        continue;
                    threatDist[v] = threatDist[u] + 1;
                    tq.push_back(v);
                    if (threatDist[v] <= reach)
                        threatAt[v]++;
                    else
                        threatPaidAt[v]++;
                    // a head can't pass through bodies (it would die), except ours at the end
                    if (freeT[v] > 1)
                        threatDist[v] = bfsReach; // stop expanding here
                }
            }
            for (int u : tq)
                threatDist[u] = INF;
        }
        if (queenSafe() && QUEEN_ALLY_THREAT)
        {
            // an ally head next to a tile can step onto it too: head-on with an ally kills the queen as well
            for (auto& s : segs)
                if (s.head && s.team == w.myTeam && s.id != w.myId)
                    for (int d = 0; d < 4; d++)
                    {
                        int v = step(s.tile, d);
                        if (v >= 0)
                            threatAt[v]++;
                    }
        }
        if (TAIL_THREAT && (TAIL_THREAT == 1 || units <= LAST_FEW_UNITS || kingSelf || myLen >= 10))
        {
            // An enemy dragon of length 4+ can split: its tail becomes a new head
            // that moves later this round, so tiles next to its tail are ram-able.
            for (auto& s : segs)
            {
                if (s.head || s.team == w.myTeam)
                    continue;
                bool isTail = true, headSeen = false;
                for (int d = 0; d < 4 && isTail; d++)
                {
                    int n = step(s.tile, d);
                    if (n < 0)
                        continue;
                    int j = segAt[n];
                    if (j >= 0 && segs[j].id == s.id && !segs[j].head && step(n, segs[j].facing) == s.tile)
                        isTail = false;
                    if (!visible[n])
                        isTail = false;
                }
                if (!isTail)
                    continue;
                int len = 0;
                for (auto& o : segs)
                    if (o.id == s.id)
                    {
                        len++;
                        headSeen |= o.head;
                    }
                if (len < 4 && headSeen)
                    continue;
                for (int d = 0; d < 4; d++)
                {
                    int v = step(s.tile, d);
                    if (v >= 0 && freeT[v] <= 1)
                        threatAt[v]++;
                }
            }
        }
    }

    // Pocket pumping: a short dragon dives into a dead end with pearls, eats up to
    // length 4+ at the tip, then (reverse-)splits so the rear half walks back out.
    // Worth it only if the pocket's pearls get us to 4, no enemy guards the mouth,
    // and at most one teammate is already inside.
    // HOT_PULL (notes/22): entrances of dead-end pockets that hold a fast-refilling tile
    std::vector<int> hotMouth;
    int hotMouthRound = -1;
    bool fastTile(int u) const
    {
        return (w.gmax[u] > 0 && w.gmax[u] <= POCKET_FAST_GAP) ||
               (!w.gapSeen.empty() && w.gapSeen[u] > 0 && w.gapSeen[u] <= POCKET_FAST_GAP);
    }
    void computeHotMouths()
    {
        hotMouthRound = round;
        hotMouth.clear();
        std::vector<int> deg(w.N, 0);
        std::vector<char> pk(w.N, 0);
        std::vector<int> q;
        for (int t = 0; t < w.N; t++)
        {
            for (int d = 0; d < 4; d++)
                if (step(t, d) >= 0)
                    deg[t]++;
            if (deg[t] <= 1)
                q.push_back(t);
        }
        for (size_t i = 0; i < q.size(); i++) // leaf pruning: what's removed is dead-end pocket
        {
            int t = q[i];
            if (pk[t])
                continue;
            pk[t] = 1;
            for (int d = 0; d < 4; d++)
            {
                int v = step(t, d);
                if (v >= 0 && !pk[v] && --deg[v] == 1)
                    q.push_back(v);
            }
        }
        std::vector<int> comp(w.N, -1);
        for (int s0 = 0; s0 < w.N; s0++)
        {
            if (!pk[s0] || comp[s0] >= 0)
                continue;
            std::vector<int> cq{s0}, mouths;
            comp[s0] = s0;
            bool hot = false;
            for (size_t i = 0; i < cq.size(); i++)
            {
                int u = cq[i];
                hot |= fastTile(u);
                for (int d = 0; d < 4; d++)
                {
                    int v = step(u, d);
                    if (v < 0)
                        continue;
                    if (!pk[v])
                        mouths.push_back(u);
                    else if (comp[v] < 0)
                        comp[v] = s0, cq.push_back(v);
                }
            }
            if (hot)
                hotMouth.insert(hotMouth.end(), mouths.begin(), mouths.end());
        }
        if (dbg)
            std::fprintf(dbg, "HOTMOUTH mouths=%zu\n", hotMouth.size());
    }

    bool pocketWorthPumping(int t)
    {
        auto why = [&](const char* r) { if (dbg) std::fprintf(dbg, "POCKET %s len=%d\n", r, myLen); return false; };
        if (myLen < 2 || myLen > 3 || units >= w.unitLimit || iAmKing())
            return why("len/units/king");
        if (RP.diveStopRound > 0 && round >= RP.diveStopRound)
            return why("late");
        pocketPearlsLast = 0;
        if (POCKET_ENEMY_LOCAL == 0)
        {
            for (auto& o : segs)
                if (o.head && o.team != w.myTeam && wrapDist(o.tile, t) <= 3)
                    return why("enemy");
        }
        else
        {
            // POCKET_ENEMY_LOCAL (notes/autarky_calc/PLAN.md): an enemy head near the mouth is not by itself a
            // reason to walk off a full pocket (that hands the pocket over). Veto only when an enemy head can
            // reach the entry tile this turn (head-on / it dives first), or (mode 2) when enemy heads within 3
            // of the entry outnumber ours (the child would come out into a local majority).
            int en = 0, al = 1;
            for (auto& o : segs)
            {
                if (!o.head || o.id == w.myId)
                    continue;
                int dd = wrapDist(o.tile, t);
                if (o.team != w.myTeam)
                {
                    if (dd <= 1)
                        return why("enemy");
                    if (dd <= 3)
                        en++;
                }
                else if (dd <= 3)
                    al++;
            }
            if (POCKET_ENEMY_LOCAL >= 2 && en > al)
                return why("enemy-local");
        }
        // flood the pocket from its mouth, not crossing our own body or anything occupied
        std::vector<int> q{t}, seen{t};
        double pearls = 0;
        int allies = 0, hot = 0;
        for (size_t qi = 0; qi < q.size() && q.size() <= 24; qi++)
        {
            int u = q[qi];
            if (visible[u] && w.pearlMem[u])
                pearls += 1.0;
            else if (w.gmax[u] > 0 && w.gmax[u] <= POCKET_FAST_GAP)
                pearls += 0.5, hot++;
            else if (POCKET_OBSERVED && !w.gapSeen.empty() && w.gapSeen[u] > 0 && w.gapSeen[u] <= POCKET_FAST_GAP)
                pearls += 0.5, hot++; // we've watched this tile respawn quickly
            else if (POCKET_OBSERVED && w.spawnAt[u] >= 0 && w.spawnAt[u] - round <= 6)
                pearls += 0.7; // a pearl is about to appear here
            if (occHead[u] && occTeam[u] == w.myTeam && occId[u] != w.myId)
                allies++;
            for (int d = 0; d < 4; d++)
            {
                int v = step(u, d);
                if (v < 0 || v == myHead || std::find(seen.begin(), seen.end(), v) != seen.end())
                    continue;
                if (occId[v] >= 0 && !(occHead[v] && occTeam[v] == w.myTeam))
                    continue;
                seen.push_back(v);
                q.push_back(v);
            }
        }
        if (q.size() > 24)
            return why("big"); // not a pocket, just a region the area check didn't like
        if (allies > POCKET_MAX_ALLIES)
            return why("allies");
        // on an unseen map, only dive when we've seen evidence of fast pearls in there
        if ((POCKET_PUMP_HOT || (POCKET_UNK_NEEDS_HOT && !w.known)) && hot == 0)
            return why("nohot");
        if (myLen + pearls < POCKET_NEED)
            return why("fewpearls");
        if (DIVE_VALUE && (DV_PARTS & 2) && dvValue(t) < DV_MARGIN)
            return why("dv"); // pearls summed over branches are not one path's pearls
        if (dbg)
            std::fprintf(dbg, "POCKET YES len=%d pearls=%.1f\n", myLen, pearls);
        pocketPearlsLast = pearls;
        return true;
    }
    double pocketPearlsLast = 0; // pearls counted by the last pocketWorthPumping() that said yes

    // ---- POCKET_FACTORY (notes/pocket_factory/LOG.md): a general dead-end pocket cycle.
    // Pockets = tiles removed by leaf-pruning the (known) edge graph: 1-wide trees hanging off the core.
    // A dragon facing inward in one can never turn round, so its front 2 segments are lost whatever it
    // does; the cycle is worth (pearls eaten inside) - 2. So: dive only when >= PF_MIN_P pearls are
    // expected along the path (timed countdowns), one diver per pocket, keep eating while food lies
    // ahead, and split k=L-2 at the end so the tail-end child (facing out) carries the bulk out.
    std::vector<int> pfDepth, pfComp; // depth 1 = mouth tile (touches the core); 0 = not a pocket tile
    int pfRound = -1;
    double pfLastP = 0;               // expected pearls of the last pfDiveOK() yes
    void pfCompute()
    {
        if (pfRound >= 0 && (w.known || pfRound == round))
            return;
        pfRound = round;
        pfDepth.assign(w.N, 0);
        pfComp.assign(w.N, -1);
        std::vector<int> deg(w.N, 0), q;
        std::vector<char> pk(w.N, 0);
        for (int t = 0; t < w.N; t++)
        {
            for (int d = 0; d < 4; d++)
            {
                int v = step(t, d);
                if (v >= 0 && v != t)
                    deg[t]++;
            }
            if (deg[t] <= 1)
                q.push_back(t);
        }
        for (size_t i = 0; i < q.size(); i++)
        {
            int t = q[i];
            if (pk[t])
                continue;
            pk[t] = 1;
            for (int d = 0; d < 4; d++)
            {
                int v = step(t, d);
                if (v >= 0 && v != t && !pk[v] && --deg[v] == 1)
                    q.push_back(v);
            }
        }
        std::vector<int> bq;
        for (int t = 0; t < w.N; t++)
        {
            if (!pk[t])
                continue;
            for (int d = 0; d < 4; d++)
            {
                int v = step(t, d);
                if (v >= 0 && !pk[v])
                {
                    pfDepth[t] = 1;
                    pfComp[t] = t;
                    bq.push_back(t);
                    break;
                }
            }
        }
        for (size_t i = 0; i < bq.size(); i++)
        {
            int u = bq[i];
            for (int d = 0; d < 4; d++)
            {
                int v = step(u, d);
                if (v >= 0 && pk[v] && pfDepth[v] == 0)
                {
                    pfDepth[v] = pfDepth[u] + 1;
                    pfComp[v] = pfComp[u];
                    bq.push_back(v);
                }
            }
        }
        // isolated pruned trees (the whole map is a tree) have no mouth: leave them at depth 0
    }
    // Expected pearl on pocket tile u if our head arrives there on step s (s=1: this turn).
    double pfPearl(int u, int s) const
    {
        int arrive = round + s - 1;
        if (visible[u])
        {
            if (w.pearlMem[u])
                return 1.0;
            if (w.spawnAt[u] >= 0 && arrive >= w.spawnAt[u])
                return 1.0; // countdown seen: it spawns before we get there (the tile is ahead of us, free)
            return 0.0;
        }
        int ls = w.lastSeen[u];
        if (ls >= 0 && w.pearlMem[u])
            return 0.7;
        if (w.spawnAt[u] >= 0 && w.spawnAt[u] > ls && arrive >= w.spawnAt[u])
            return 0.7;
        if (fastTile(u))
            return (w.gmax[u] == 1 || (!w.gapSeen.empty() && w.gapSeen[u] == 1)) ? 0.7 : 0.4;
        return 0.0;
    }
    // Best expected pearls along one inward branch starting at pocket tile t (entered on step s).
    // Stops at tiles that will still be occupied when we arrive. firstStep = t.
    double pfBranch(int t, int s, int depthLimit, int* endSteps = nullptr, bool certain = false) const
    {
        if (t < 0 || pfDepth[t] == 0 || s > depthLimit || freeT[t] > s)
        {
            if (endSteps)
                *endSteps = s - 1;
            return 0.0;
        }
        double here = pfPearl(t, s);
        if (certain && here < 1.0)
            here = 0.0;
        double best = 0.0;
        int bestEnd = s;
        for (int d = 0; d < 4; d++)
        {
            int v = step(t, d);
            if (v < 0 || v == t || pfDepth[v] <= pfDepth[t])
                continue;
            int e = s;
            double b = pfBranch(v, s + 1, depthLimit, &e, certain);
            if (b > best)
                best = b, bestEnd = e;
        }
        if (endSteps)
            *endSteps = bestEnd;
        return here + best;
    }
    // Is the head in a pocket, facing inward, with the tail not parked in some other pocket?
    // (Starters lying in 1-wide corridors between two dead ends fail the tail test and keep old play.)
    bool pfInward() const
    {
        if (myHead < 0 || pfDepth.empty() || pfDepth[myHead] == 0 || static_cast<int>(trail.size()) < myLen || myLen < 2)
            return false;
        int neck = trail[1];
        if (pfDepth[neck] >= pfDepth[myHead] && !(pfDepth[neck] == 0))
            return false;
        if (pfDepth[neck] != 0 && pfComp[neck] != pfComp[myHead])
            return false;
        int tail = trail[myLen - 1];
        if (pfDepth[tail] != 0 && pfComp[tail] != pfComp[myHead])
            return false;
        return true;
    }
    // A split child's head is our tail, facing away from us. Born inside a pocket facing inward it is a
    // diver with no choice: only allow that when the dive ahead of it is worth it.
    bool pfChildInwardBad(int k)
    {
        if (pfDepth.empty() || static_cast<int>(trail.size()) < myLen || myLen < 3)
            return false;
        int tail = trail[myLen - 1], pre = trail[myLen - 2];
        if (pfDepth[tail] == 0 || pfDepth[pre] >= pfDepth[tail])
            return false;
        if (units > w.unitLimit - PF_UNIT_RESERVE)
            return true; // it could not split its way out at the end
        for (auto& o : segs)
            if (o.head && o.id != w.myId && pfDepth[o.tile] > 0 && pfComp[o.tile] == pfComp[tail])
                return true;
        double P = 0;
        int endS = 1;
        for (int d = 0; d < 4; d++)
        {
            int v = step(tail, d);
            if (v < 0 || v == pre || pfDepth[v] <= pfDepth[tail])
                continue;
            int e = 1;
            double b = pfBranch(v, 1, 24, &e);
            if (b > P)
                P = b, endS = e;
        }
        bool bad = k + P < 4.0 + PF_SAFETY || P < PF_MIN_P;
        if (DIVE_VALUE && (DV_PARTS & 4) && P - 2.0 - DV_TURN_COST * (endS + 1) < DV_MARGIN)
            bad = true;
        if (dbg)
            std::fprintf(dbg, "PF child-inward k=%d P=%.2f bad=%d\n", k, P, bad ? 1 : 0);
        return bad;
    }
    // Entry test for stepping from the core onto mouth tile t.
    bool pfDiveOK(int t)
    {
        auto why = [&](const char* r) { if (dbg) std::fprintf(dbg, "PF no %s len=%d\n", r, myLen); return false; };
        pfLastP = 0;
        if (myLen < 2 || myLen > PF_ENTER_MAXLEN || units > w.unitLimit - PF_UNIT_RESERVE || iAmKing())
            return why("len/units/king");
        if (qparkNoDive())
            return why("qpark");
        if (RP.diveStopRound > 0 && round >= RP.diveStopRound)
            return why("late");
        int comp = pfComp[t];
        // one diver per pocket: nobody's head inside (a diver ahead blocks the food and its child
        // comes out head-first into us; an exiting child would meet us head-on)
        for (auto& o : segs)
            if (o.head && o.id != w.myId && pfDepth[o.tile] > 0 && pfComp[o.tile] == comp)
                return why("occupied");
        int en = 0, al = 1, enAdj = 0;
        for (auto& o : segs)
        {
            if (!o.head || o.id == w.myId)
                continue;
            int dd = wrapDist(o.tile, t);
            if (o.team != w.myTeam)
            {
                if (dd <= 1)
                    enAdj++;
                if (dd <= 3)
                    en++;
            }
            else if (dd <= 3)
                al++;
        }
        if (enAdj > 0)
            return why("enemy-adj");
        if (PF_ENEMY == 0 && en > 0)
            return why("enemy");
        if (PF_ENEMY == 1 && en >= al)
            return why("enemy-local");
        if (PF_ENEMY == 2 && en > al)
            return why("enemy-local2");
        int endS = 0;
        double P = pfBranch(t, 1, 24, &endS);
        if (myLen + P < 4.0 + PF_SAFETY)
            return why("cannot-split");
        if (P < PF_MIN_P)
            return why("fewpearls");
        if (DIVE_VALUE && (DV_PARTS & 1) && dvNet(P * dvContest(t), endS + 1) < DV_MARGIN)
        {
            if (dbg)
                std::fprintf(dbg, "PF dv P=%.2f contest=%.2f end=%d units=%d/%d\n", P, dvContest(t), endS, units, w.unitLimit);
            return why("dv");
        }
        if (dbg)
            std::fprintf(dbg, "PF YES len=%d P=%.2f end=%d en=%d al=%d\n", myLen, P, endS, en, al);
        pfLastP = P;
        return true;
    }

    // ---- DIVE_VALUE (notes/slithery_pockets/LOG.txt): expected net length of entering a dead end.
    // Split possible at the tip: we keep everything but the 2-long stub, minus the turns spent;
    // otherwise (never reaches 4, or no unit slot) the whole dragon is lost.
    double dvNet(double P, int turns) const
    {
        bool canSplit = units <= w.unitLimit - DV_UNIT_RESERVE && myLen + P >= 4.0;
        if (!canSplit)
            return -static_cast<double>(myLen);
        return P - 2.0 - DV_TURN_COST * turns;
    }
    double dvContest(int mouth) const
    {
        int en = 0;
        for (auto& o : segs)
            if (o.head && o.team != w.myTeam && wrapDist(o.tile, mouth) <= 3)
                en++;
        return std::max(0.0, 1.0 - DV_CONTEST * en);
    }
    // best single path (no revisits) through a small dynamic dead end, timed like pfBranch
    int dvBudget = 0;
    double dvRegionPath(int u, int s, std::vector<char>& vis, int& endS)
    {
        endS = s;
        if (--dvBudget < 0 || s > 16)
            return 0.0;
        double here = pfPearl(u, s), best = 0.0;
        vis[u] = 1;
        for (int d = 0; d < 4; d++)
        {
            int v = step(u, d);
            if (v < 0 || v == u || vis[v] || v == myHead || freeT[v] > s + 1)
                continue;
            int e = s + 1;
            double b = dvRegionPath(v, s + 1, vis, e);
            if (b > best)
                best = b, endS = e;
        }
        vis[u] = 0;
        return here + best;
    }
    // V for stepping onto t: static pocket (pfDepth) or, when dynamic, the small region behind t.
    double dvValue(int t)
    {
        int endS = 1;
        double P;
        if (!pfDepth.empty() && pfDepth[t] > 0 && pfDepth[t] > pfDepth[myHead])
            P = pfBranch(t, 1, 24, &endS);
        else
        {
            std::vector<char> vis(w.N, 0);
            vis[myHead] = 1;
            dvBudget = 4000;
            P = dvRegionPath(t, 1, vis, endS);
        }
        P *= dvContest(t);
        double V = dvNet(P, endS + 1);
        if (dbg)
            std::fprintf(dbg, "DV t=(%d,%d) P=%.2f end=%d V=%.2f\n", t % w.W, t / w.W, P, endS, V);
        return V;
    }

    // PUMP_TIP2 (notes/autarky_calc/PLAN.md): is the head inside a static 1-wide dead end? Flood from the
    // head over kelp only (bodies ignored), never back through the neck. Returns the tiles ahead
    // (head included) or an empty vector when the region is larger than `cap`.
    std::vector<int> staticAhead(int cap)
    {
        std::vector<int> q;
        if (static_cast<int>(trail.size()) < 2)
            return q;
        int neck = trail[1];
        q.push_back(myHead);
        for (size_t qi = 0; qi < q.size(); qi++)
            for (int d = 0; d < 4; d++)
            {
                int v = step(q[qi], d);
                if (v < 0 || v == neck || std::find(q.begin(), q.end(), v) != q.end())
                    continue;
                q.push_back(v);
                if (static_cast<int>(q.size()) > cap)
                    return {};
            }
        return q;
    }

    // Sprint 2-3 steps along pearls when an enemy head could take them first.
    // Each extra step costs a segment, but a step onto a pearl pays it back, so a
    // run over pearls is free (or better) and denies them to the enemy.
    bool tryEatSprint()
    {
        if (myLen < 3 || feedPhase() && iAmKing() || threatAt[myHead] > 0)
            return false;
        auto pearlAt = [&](int t) { return t >= 0 && visible[t] && w.pearlMem[t]; };
        auto enemyNear = [&](int t) {
            for (auto& o : segs)
                if (o.head && o.team != w.myTeam && wrapDist(o.tile, t) <= EAT_SPRINT_CONTEST)
                    return true;
            return false;
        };
        auto inBody = [&](int t, int skipTail) {
            int L = static_cast<int>(trail.size());
            for (int i = 0; i < L - skipTail; i++)
                if (trail[i] == t)
                    return true;
            return false;
        };
        double bestVal = 0.0;
        std::string bestCmd;
        std::vector<int> bestPath;
        int maxSteps = std::min(EAT_SPRINT_MAX, myLen - 1);
        // depth-first over 2..maxSteps step paths
        std::vector<int> path;
        std::vector<int> dirs;
        std::function<void(int, int, int)> go = [&](int at, int eaten, int contested) {
            int steps = static_cast<int>(path.size());
            if (steps >= 2)
            {
                // net length change: +eaten - (steps-1); worth it only if it grabs contested pearls
                int net = eaten - std::max(0, steps - (FREE_FIX ? freeSteps(myLen) : 1));
                double val = net + 1.5 * contested;
                int landing = path.back();
                int exits = 0;
                for (int d = 0; d < 4; d++)
                {
                    int v = step(landing, d);
                    if (v >= 0 && freeOther[v] <= 1 && std::find(path.begin(), path.end(), v) == path.end() && !inBody(v, steps))
                        exits++;
                }
                if (exits >= 2 && threatAt[landing] == 0 && net >= 0 && contested > 0 && val > bestVal)
                {
                    bestVal = val;
                    bestPath = path;
                    bestCmd = "MOVE ";
                    for (int d : dirs)
                        bestCmd += DIRC[d];
                }
            }
            if (steps >= maxSteps)
                return;
            for (int d = 0; d < 4; d++)
            {
                int v = step(at, d);
                if (v < 0 || freeOther[v] > 1 || occId[v] >= 0 && occId[v] != w.myId)
                    continue;
                // our own body before this step: each earlier non-eating step moved the
                // tail once, and each paid step (2nd onwards) moved it once more; the
                // engine checks the destination before this step's tail moves
                int tailFreed = (steps - eaten) + std::max(0, steps - (FREE_FIX ? freeSteps(myLen) : 1));
                if (inBody(v, std::max(0, tailFreed)) || std::find(path.begin(), path.end(), v) != path.end())
                    continue;
                bool p = pearlAt(v);
                if ((steps >= 1 || EAT_SPRINT_STRICT) && !p)
                    continue; // only extend a sprint over pearls (strict: every step is a pearl)
                path.push_back(v);
                dirs.push_back(d);
                go(v, eaten + (p ? 1 : 0), contested + (p && enemyNear(v) ? 1 : 0));
                path.pop_back();
                dirs.pop_back();
            }
        };
        go(myHead, 0, 0);
        if (bestCmd.empty())
            return false;
        out += bestCmd + "\n";
        pending = bestPath;
        return true;
    }

    // QKILL (v37a step 1): the enemy queen's head (id <= 1, other team) does not move during our turn, so a
    // path of <= K(myLen) = F + (L-2) steps over empty tiles (or tiles our own tail freed this turn) that ends
    // on her head is a certain head-on kill. Own body simulated step by step: a free step frees 1 tail tile,
    // a paid step 2, eating holds 1; a paid step needs length >= 3. Shortest path wins.
    bool tryQueenKill(int capK = 1 << 30) // DGU F1: capK caps the path length (QKK_FREE)
    {
        int eq = -1;
        for (auto& s : segs)
            if (s.head && s.team != w.myTeam && s.id <= 1)
                eq = s.tile;
        if (eq < 0 || myHead < 0)
            return false;
        const int F = freeSteps(myLen);
        const int baseK = F + std::max(0, myLen - 2);
        int K = baseK;
        if (QKILL_FUEL && myLen <= QK_FUEL_MAXLEN)
        {
            int pearls = 0;
            for (int t = 0; t < w.N; ++t)
                pearls += visible[t] && w.pearlMem[t] && occId[t] < 0;
            K += std::min(pearls, QK_FUEL_EXTRA); // QKILL_FUEL (Codex): pearl-paid steps extend the certain-kill search
        }
        K = std::min(K, capK);
        const bool trailOk = static_cast<int>(trail.size()) == myLen;
        auto pass = [&](int t) { // may a path step through t at all (ignoring our own body timing)
            if (t < 0 || !visible[t] || freeOther[t] > 1)
                return false;
            return occId[t] < 0 || (occId[t] == w.myId && trailOk);
        };
        // BFS distance to her head over passable tiles (a lower bound used for pruning)
        std::vector<int> dist(w.N, INF);
        std::vector<int> q{eq};
        dist[eq] = 0;
        for (size_t i = 0; i < q.size(); i++)
        {
            int u = q[i];
            if (dist[u] >= K)
                continue;
            for (int d = 0; d < 4; d++)
            {
                int v = step(u, d);
                if (v < 0 || dist[v] != INF || !(pass(v) || v == myHead))
                    continue;
                dist[v] = dist[u] + 1;
                q.push_back(v);
            }
        }
        if (dist[myHead] > K)
            return false;
        // simulated body, head first; -1 = a segment we can't see
        std::deque<int> body;
        if (trailOk)
            body.assign(trail.begin(), trail.end());
        else
        {
            body.assign(trail.begin(), trail.end());
            while (static_cast<int>(body.size()) < myLen)
                body.push_back(-1);
        }
        std::vector<int> dirs;
        std::vector<char> fuelEaten;
        if (QKILL_FUEL) fuelEaten.assign(w.N, 0); // a pearl can only be eaten once along one path
        int nodes = 0;
        std::function<bool(int, int, int)> go = [&](int at, int curLen, int limit) -> bool {
            int k = static_cast<int>(dirs.size()); // steps taken so far
            if (++nodes > 20000)
                return false;
            bool paid = k >= F;
            if (paid && curLen < 3)
                return false;
            for (int d = 0; d < 4; d++)
            {
                int v = step(at, d);
                if (v < 0)
                    continue;
                if (v == eq)
                {
                    dirs.push_back(d);
                    return true;
                }
                if (k + 1 >= limit || dist[v] == INF || k + 1 + dist[v] > limit || !pass(v))
                    continue;
                if (std::find(body.begin(), body.end(), v) != body.end())
                    continue; // still our body when this step is checked (tail included)
                bool eat = visible[v] && w.pearlMem[v] && (!QKILL_FUEL || !fuelEaten[v]);
                if (QKILL_FUEL && eat) fuelEaten[v] = 1;
                std::deque<int> saved = body;
                body.push_front(v);
                int pops = (eat ? 0 : 1) + (paid ? 1 : 0);
                for (int p = 0; p < pops && !body.empty(); p++)
                    body.pop_back();
                dirs.push_back(d);
                if (go(v, curLen + (eat ? 1 : 0) - (paid ? 1 : 0), limit))
                    return true;
                dirs.pop_back();
                body = saved;
                if (QKILL_FUEL && eat) fuelEaten[v] = 0;
            }
            return false;
        };
        for (int limit = std::max(1, dist[myHead]); limit <= K; limit++)
        {
            dirs.clear();
            if (go(myHead, myLen, limit))
            {
                std::string cmd = "MOVE ";
                std::vector<int> path;
                int at = myHead;
                for (int d : dirs)
                {
                    cmd += DIRC[d];
                    at = step(at, d);
                    path.push_back(at);
                }
                out += cmd + "\n";
                pending = path;
                return true;
            }
        }
        return false;
    }

    // ROUND2 debug: one LOG line per event (R2_DEBUG=1 builds only; parsed from local replays)
    void r2log(const char* what, int v = 0)
    {
        if (R2_DEBUG)
            out += std::string("LOG r2 ") + what + " r" + std::to_string(round) + " id" + std::to_string(w.myId) + " L" +
                   std::to_string(myLen) + " v" + std::to_string(v) + "\n";
    }
    // ROUND2 P1 QKILL_KING: a long king keeps itself only when our queen is known alive and longer than the target looks
    bool qkkAllowed() const
    {
        if (myLen < QKK_KEEP_LEN)
            return true;
        int ours = 0, theirs = 0;
        for (auto& s : segs)
            if (s.id <= 1)
                (s.team == w.myTeam ? ours : theirs)++;
        if (ours == 0 && round - qsOurRound <= QKK_ALIVE_MEM)
            ours = std::max(qsOurLen, 1);
        return !(ours > 0 && ours > theirs);
    }
    // DGU F5 QG_RAM (root-portals-maze C3): an enemy head that threatens our crowned queen: near her last known tile,
    // or (Maze park) inside our home field (frame x <= QG_FIELD_X; non-queens rarely hear her beacon there)
    bool qgNearQueen(int tile) const
    {
        if (!RP.queenKing || amQueen() || !queenKingRound())
            return false;
        if (queenAlive() && qTile >= 0 && wrapDist(tile, qTile) <= QG_RAM)
            return true;
        if (RP.qPark == 2)
        {
            int x = tile % w.W, fx = w.myTeam == 'A' ? x : w.W - 1 - x;
            return fx <= QG_FIELD_X;
        }
        return false;
    }
    // Try a head-on ram at distance 1 or 2. Returns true if we emitted it.
    bool tryRam()
    {
        if (queenSafe())
            return false; // the queen never trades herself
        if (LATE_HUNT && LH_KING_KILL && lhOn() && ENABLE_RAM && iAmKing() && tryQueenKill())
        {
            r2log("lhk");
            return true;
        }
        if (QKILL_KING && ENABLE_RAM && units >= 2 && !amQueen() && feedPhase() && iAmKing() && qkkAllowed() && tryQueenKill(QKK_FREE ? freeSteps(myLen) : 1 << 30))
        {
            r2log("qkk"); // ROUND2 P1: a king (often a self-crowned L8+ camper) takes a certain queen kill too
            return true;
        }
        if (!ENABLE_RAM || units < 2 || (feedPhase() && iAmKing()))
            return false;
        if (!amQueen() && (QKILL || (QSTATE && qstHunt())) && tryQueenKill())
        {
            r2log("qk");
            return true;
        }
        double bestVal = 0;
        std::string bestCmd;
        for (auto& s : segs)
        {
            if (!s.head || s.team == w.myTeam)
                continue;
            int theirs = enemyVisibleLength(s.id);
            // QUEEN_HUNT: the enemy queen is worth any 1-for-1 trade (a dead queen scores 0 at r500)
            bool hunt = QUEEN_HUNT && s.id <= 1 && !amQueen() && units >= QH_MIN_UNITS;
            // worth it if they're at least as valuable as us, and we aren't the king
            bool worth = hunt || theirs >= myLen || (myLen <= RAM_MAX_OWN_LEN);
            // DGU F5 QG_RAM: an enemy head this close to our crowned queen is worth any small trade
            const bool qgRam = QG_RAM > 0 && myLen <= QG_RAM_MAXLEN && qgNearQueen(s.tile);
            if (qgRam)
                worth = true;
            if (!hunt && !qgRam && RP.ramGuard && theirs < myLen + 2)
            {
                // an even trade only helps when we have the numbers
                int allyHeads = 1, enemyHeads = 0;
                for (auto& o : segs)
                    if (o.head && o.id != w.myId)
                        (o.team == w.myTeam ? allyHeads : enemyHeads)++;
                if ((RP.ramGuard != 2 && units < RAM_MIN_UNITS) || allyHeads < enemyHeads + 1)
                    worth = false;
            }
            if (queenEarly() && (!QS_EARLY_RAM || theirs >= myLen))
                continue; // early queen: rams only shorter heads (head-on still kills both: QS_EARLY_RAM=0 bans it)
            if (!worth)
                continue;
            double val = 40.0 + 3.0 * theirs - 2.0 * myLen + (hunt ? QH_BONUS : 0.0);
            for (int d1 = 0; d1 < 4; d1++)
            {
                int m = step(myHead, d1);
                if (m < 0)
                    continue;
                if (m == s.tile)
                {
                    if (val + 5 > bestVal)
                    {
                        bestVal = val + 5;
                        bestCmd = std::string("MOVE ") + DIRC[d1];
                    }
                    continue;
                }
                if (myLen < 3 || freeT[m] > 1)
                    continue;
                for (int d2 = 0; d2 < 4; d2++)
                    if (step(m, d2) == s.tile && val > bestVal)
                    {
                        bestVal = val;
                        bestCmd = std::string("MOVE ") + DIRC[d1] + DIRC[d2];
                    }
            }
        }
        if (bestVal <= 0)
            return false;
        out += bestCmd + "\n";
        pending.clear();
        return true;
    }

    // UNK_SCARCE_FIX (notes/qualifier/SCARCE_PORTAL.md): on an unknown map, portals are kelp until we
    // see that a big share of the food we know of can only be reached through portal pairs whose two
    // ends we have both seen (so the destination is exact). Then we path through known pairs for good
    // (sticky). Shortcut-only portal maps never produce this evidence, so v35 behaviour is kept there.
    int scarceLogged = 0;
    void scarceFixCheck()
    {
        if (static_cast<int>(w.gapSeen.size()) != w.N || w.portalSeen.empty())
            return;
        bool pair = false;
        for (auto& [id, edges] : w.portalSeen)
            if (edges.size() == 2)
                pair = true;
        if (!pair)
            return;
        auto bfs = [&](std::vector<char>& seen) {
            seen.assign(w.N, 0);
            std::vector<int> q{myHead};
            seen[myHead] = 1;
            for (size_t i = 0; i < q.size(); i++)
                for (int d = 0; d < 4; d++)
                {
                    int v = w.nxt[q[i] * 4 + d];
                    if (v >= 0 && !seen[v])
                        seen[v] = 1, q.push_back(v);
                }
        };
        std::vector<char> walk, linked;
        bfs(walk);
        std::vector<int> save = w.nxt;
        for (auto& [id, edges] : w.portalSeen)
            if (edges.size() == 2)
                w.linkPortal(edges[0], edges[1]);
        bfs(linked);
        w.nxt.swap(save);
        int gainN = 0, walkN = 0;
        double walkRate = 0, gainRate = 0;
        for (int t = 0; t < w.N; t++)
        {
            if (w.gapSeen[t] <= 0 || w.gmax[t] == 0)
                continue;
            double r = 1.0 / std::max(2, w.gapSeen[t]);
            if (walk[t])
                walkN++, walkRate += r;
            else if (linked[t])
                gainN++, gainRate += r;
        }
        // USF_RICH: the portal-only food must also be much richer per spawner tile than what we can walk
        // to (Stripes ~90x, vaults 25-50x); room-grid maps where every room has food are ~1-2x and lose
        // (over-crossing, as with LEARN_PORTALS)
        bool rich = USF_RICH <= 0 || gainRate * std::max(1, walkN) >= USF_RICH * walkRate * gainN;
        if (gainN >= USF_MIN && gainRate >= USF_FRAC * (gainRate + walkRate) && rich)
        {
            w.enablePortalUse();
            if (USF_LOG && scarceLogged++ < 1)
            {
                char buf[160];
                std::snprintf(buf, sizeof buf, "LOG scarce-fix r%d id%d gain=%d/%.3f walk=%.3f\n", round, w.myId, gainN,
                              gainRate, walkRate);
                logPending += buf;
            }
        }
    }
    std::string logPending; // LOG lines produced in analyse() (decide() clears out)

    // a tile with a portal on one of its sides (known or not): crossers land here
    bool isMouth(int t) const
    {
        for (int d = 0; d < 4; d++)
        {
            int v = step(t, d);
            if ((v >= 0 && v != w.plainStep(t, d)) || (!w.portalSide.empty() && w.portalSide[t * 4 + d]))
                return true;
        }
        return false;
    }

    // UNK_SEALED_FOOD: BFS the portal-free walkable component from our head (unseen edges are
    // open, so "unreached" is a proof, not a guess). Count pearl spawners we have seen (any
    // countdown observed) inside vs outside it. Fire when enough seen food is sealed off and an
    // unexplored door is reachable. Mode 2 also counts nearby spawners whose only walk is a long
    // detour (weaker evidence: kelp corridors on shortcut maps can look like this).
    int sealedLogged = 0, lastExploreCross = -1000;
    // portal-free region around our head (bodies ignored), capped; crowd = other dragons' segments in it
    int roomSize(int cap, int* crowd = nullptr)
    {
        std::vector<char> seen(w.N, 0);
        std::vector<int> q{myHead};
        seen[myHead] = 1;
        int c = 0;
        for (size_t i = 0; i < q.size() && static_cast<int>(q.size()) < cap; i++)
            for (int d = 0; d < 4; d++)
            {
                int v = step(q[i], d);
                if (v < 0 || seen[v])
                    continue;
                seen[v] = 1;
                q.push_back(v);
                if (occId[v] >= 0 && occId[v] != w.myId)
                    c++;
            }
        if (crowd)
            *crowd = c;
        return static_cast<int>(q.size());
    }
    bool sealedFoodEvidence()
    {
        if (static_cast<int>(w.gapSeen.size()) != w.N || w.portalSide.empty())
            return false;
        std::vector<int> dist(w.N, -1), q{myHead};
        dist[myHead] = 0;
        bool door = false;
        for (size_t i = 0; i < q.size(); i++)
        {
            int u = q[i];
            for (int d = 0; d < 4; d++)
            {
                if (!door && w.portalSide[u * 4 + d] && step(u, d) < 0 &&
                    (static_cast<int>(edgeCrossRound.size()) != w.N * 4 ||
                     round - edgeCrossRound[u * 4 + d] >= UNK_EXPLORE_COOLDOWN))
                    door = true;
                int v = step(u, d);
                if (v < 0 || dist[v] >= 0)
                    continue;
                dist[v] = dist[u] + 1;
                q.push_back(v);
            }
        }
        if (!door)
            return false;
        // rate estimate from the largest countdown seen (a lower bound on the gap)
        int sealed = 0, reach = 0;
        double sealedRate = 0, reachRate = 0;
        for (int t = 0; t < w.N; t++)
        {
            if (w.gapSeen[t] <= 0 || w.gmax[t] == 0)
                continue;
            bool off = dist[t] < 0;
            if (!off && UNK_SEALED_FOOD >= 2)
            {
                int wd = wrapDist(t, myHead);
                off = wd <= UNK_SEALED_DETOUR_NEAR && dist[t] >= 2 * wd + UNK_SEALED_DETOUR;
            }
            double r = 1.0 / std::max(2, w.gapSeen[t]);
            if (off)
                sealed++, sealedRate += r;
            else
                reach++, reachRate += r;
        }
        // enough food is sealed off, it is a real share of the food we know, and per tile it is
        // at least as rich as what we can walk to (so a dragon that just entered a rich room
        // does not immediately want to leave it again)
        bool fire = sealed >= UNK_SEALED_MIN && sealedRate >= UNK_SEALED_FRAC * (sealedRate + reachRate) &&
                    sealedRate * std::max(1, reach) >= UNK_SEALED_RICH * reachRate * sealed;
        if (fire && UNK_SEALED_LOG && sealedLogged < 3)
        {
            sealedLogged++;
            char buf[160];
            std::snprintf(buf, sizeof buf, "LOG sealed-food r%d sealed=%d/%.3f reach=%d/%.3f comp=%d\n", round, sealed,
                          sealedRate, reach, reachRate, static_cast<int>(q.size()));
            out += buf;
        }
        return fire;
    }

    // UNK_PORTAL_EXPLORE: a remembered pearl, or a spawn due by the time we arrive, within UPE_RANGE walk steps
    bool walkableFood()
    {
        std::vector<int> dist(w.N, -1), q{myHead};
        dist[myHead] = 0;
        for (size_t i = 0; i < q.size(); i++)
        {
            int u = q[i];
            if (u != myHead && (w.pearlMem[u] || (w.spawnAt[u] >= 0 && w.spawnAt[u] - round <= dist[u] + UPE_SOON)))
                return true;
            if (dist[u] >= UPE_RANGE)
                continue;
            for (int d = 0; d < 4; d++)
            {
                int v = step(u, d);
                if (v >= 0 && dist[v] < 0)
                    dist[v] = dist[u] + 1, q.push_back(v);
            }
        }
        return false;
    }

    // UNK_EXPLORE desire gate: our walkable region is fully scouted and we're a bit hungry,
    // or we've been hungry a long time with no pearl in sight. Also marks door lures.
    void computeExploreDesire()
    {
        exploreDesire = false;
        if (myLen >= KING_MIN_LEN || w.portalSide.empty() || myHead < 0)
            return;
        int hunger = round - lastGrowRound;
        bool closed = true, allSeen = true, regionSmall = false;
        {
            std::vector<int> q{myHead};
            std::vector<char> seen(w.N, 0);
            seen[myHead] = 1;
            for (size_t i = 0; i < q.size() && q.size() < static_cast<size_t>(UNK_EXPLORE_BFS_CAP); i++)
                for (int d = 0; d < 4; d++)
                {
                    int v = step(q[i], d);
                    if (v < 0 || seen[v])
                        continue;
                    seen[v] = 1;
                    if (w.lastSeen[v] < 0)
                        closed = false, allSeen = false;
                    q.push_back(v);
                }
            if (q.size() >= static_cast<size_t>(UNK_EXPLORE_BFS_CAP))
                closed = false;
            // only "sealed in" if our portal-free region is a minor part of the board
            if (static_cast<double>(q.size()) >= UNK_EXPLORE_REGION_FRAC * w.N)
                closed = false;
            // UNK_EXPLORE=2: sealed in = a sizeable share of the board lies beyond portals
            regionSmall = q.size() < static_cast<size_t>(UNK_EXPLORE_BFS_CAP) &&
                          static_cast<double>(q.size()) < UNK_EXPLORE_SEALED_FRAC * w.N;
        }
        bool pearlNear = false;
        for (int t = 0; t < w.N && !pearlNear; t++)
            if (visible[t] && w.pearlMem[t] && wrapDist(t, myHead) <= 6)
                pearlNear = true;
        exploreDesire = (closed && hunger >= UNK_EXPLORE_HUNGER_CLOSED) || (hunger >= UNK_EXPLORE_HUNGER && !pearlNear);
        if (UNK_EXPLORE >= 2)
            exploreDesire = regionSmall && ((allSeen && hunger >= UNK_EXPLORE_HUNGER_CLOSED) ||
                                            (hunger >= UNK_EXPLORE_HUNGER && !pearlNear));
        // UNK_SEALED_FOOD (notes/levers/blocked-food.md): food we have SEEN but provably cannot
        // walk to (portals as kelp, unseen edges assumed open) means doors lead somewhere worth
        // going. Shortcut-only portal maps never produce this evidence, so v28 behaviour is kept.
        if (UNK_SEALED_FOOD)
        {
            // hunger counts from the later of our last meal and our last explore crossing
            int since = round - std::max(lastGrowRound, lastExploreCross);
            if (!exploreDesire && since >= UNK_SEALED_HUNGER && !pearlNear && sealedFoodEvidence())
                exploreDesire = true;
            // settle: after crossing into a new region give it a chance before leaving again,
            // unless the room is small and crowded with other dragons (then leave at once)
            int crowd = 0, room = roomSize(UNK_SEALED_ROOM_MIN, &crowd);
            bool cramped = room < UNK_SEALED_ROOM_MIN && crowd * 4 >= room;
            if (cramped)
                exploreDesire = true;
            else if (round - lastExploreCross < UNK_SEALED_SETTLE)
                exploreDesire = false;
        }
        // UNK_PORTAL_EXPLORE (calc's rule, notes/qualifier/SCARCE_PORTAL.md): no food we can walk to (no
        // remembered pearl, no fast spawner) -> a small non-queen dragon scouts an unexplored portal. The
        // existing UNK_EXPLORE machinery does the rest (door lure, knock, cross on a clean echo, learnDest).
        // Scouts are rationed without sonar: a rotating id slot, and no ally head next to us.
        if (UNK_PORTAL_EXPLORE && !exploreDesire && myLen <= UPE_MAXLEN && w.myId > 1 && round >= UPE_MIN_ROUND &&
            round - std::max(lastGrowRound, lastExploreCross) >= UPE_HUNGER &&
            (w.myId + round / UPE_SLOT) % UPE_MOD == 0)
        {
            bool allyNear = false;
            for (auto& sg : segs)
                if (sg.head && sg.team == w.myTeam && sg.id != w.myId && wrapDist(sg.tile, myHead) <= 3)
                    allyNear = true;
            if (!allyNear && !walkableFood())
            {
                exploreDesire = true;
                if (const char* td = std::getenv("UPE_TRACE_DIR"))
                    if (FILE* tf = std::fopen((std::string(td) + "/upe.txt").c_str(), "a"))
                    {
                        std::fprintf(tf, "%d %d %c L%d head(%d,%d)\n", round, w.myId, w.myTeam, myLen, myHead % w.W, myHead / w.W);
                        std::fclose(tf);
                    }
            }
        }
        if (qNoUnkPortal())
            exploreDesire = false; // QNO_UNKPORTAL: no door lure, no explore crossing for the queen
        if (UNK_EXPLORE_LURE > 0)
        {
            lureTile.assign(w.N, 0);
            if (exploreDesire)
                for (int t = 0; t < w.N; t++)
                    for (int d = 0; d < 4; d++)
                        if (w.portalSide[t * 4 + d] && step(t, d) < 0 &&
                            (static_cast<int>(edgeCrossRound.size()) != w.N * 4 ||
                             round - edgeCrossRound[t * 4 + d] >= UNK_EXPLORE_COOLDOWN))
                            lureTile[t] = 1;
        }
    }

    // REPLY_SEARCH (notes/levers/budget-lookahead.md, PLAN Q8): 1-ply opponent-reply check for big dragons.
    // Same reach rule as computeThreats (visible length - 1, tail-unknown bump, king cap).
    int replyEnemyReach(int si)
    {
        int r = replyEnemyReach0(si);
        if (KREACH && (myLen >= 5 || amQueen()))
        {
            const Seg& s = segs[si];
            int Lv = enemyVisibleLength(s.id);
            if (!enemyTailSeen(s))
                Lv = std::max(Lv, 3);
            r = std::max(r, std::min(freeSteps(Lv) + std::max(0, Lv - 2), static_cast<int>(KR_CAP)));
        }
        return r;
    }
    int replyEnemyReach0(int si)
    {
        const Seg& s = segs[si];
        if (THREAT_FREE || queenSafe())
        {
            // 1.2.3: a reply covers its free steps (F fixed at its turn-start length)
            int Lv = enemyVisibleLength(s.id);
            if (!enemyTailSeen(s))
                Lv = std::max(Lv, THREAT_TAIL_UNKNOWN + 1);
            int r = freeSteps(Lv);
            return queenSafe() ? r + 1 : std::min(r, KING_THREAT_REACH);
        }
        int reach = std::max(1, enemyVisibleLength(s.id) - 1);
        if (THREAT_TAIL_UNKNOWN > 0 && reach < THREAT_TAIL_UNKNOWN)
        {
            bool tailSeen = false;
            for (int j = 0; j < static_cast<int>(segs.size()) && !tailSeen; j++)
            {
                if (segs[j].id != s.id || segs[j].head || !tailIsVisibleTail(j))
                    continue;
                bool hasPrev = false;
                for (auto& o : segs)
                    if (o.id == s.id && !o.head && step(o.tile, o.facing) == segs[j].tile)
                        hasPrev = true;
                tailSeen = !hasPrev;
            }
            if (!tailSeen)
                reach = THREAT_TAIL_UNKNOWN;
        }
        return std::min(reach, KING_THREAT_REACH);
    }
    // After we step onto t, every nearby enemy head makes a 1-step reply (all joint combinations of the
    // nearest REPLY_MAX_ENEMIES within REPLY_RADIUS). Per combination: reply tiles become body, tiles the
    // replied heads can reach next turn are closed to our 2nd step, and surviveDepth is re-run.
    // Returns the penalty for the worst combination (0 if none hurts). -1 = skipped (budget).
    int replyWorst = -1, replyCombos = 0;
    double replyPenalty(int t, int baseDepth, int wantDepth)
    {
        replyWorst = -1;
        replyCombos = 0;
        if (pointsM() - turnT0 > REPLY_BUDGET_M)
            return -1;
        struct En
        {
            int si, dist, reach, len;
            int rep[4];
            int nrep;
        };
        En en[8];
        int ne = 0;
        for (int i = 0; i < static_cast<int>(segs.size()); i++)
        {
            const Seg& o = segs[i];
            if (!o.head || o.team == w.myTeam)
                continue;
            int dd = wrapDist(o.tile, t);
            if (dd > REPLY_RADIUS)
                continue;
            En e{i, dd, 0, enemyVisibleLength(o.id), {0, 0, 0, 0}, 0};
            for (int d = 0; d < 4; d++)
            {
                int r = step(o.tile, d);
                if (r < 0 || r == t || freeT[r] > 1)
                    continue; // kelp, the ram itself (threatAt covers it), or occupied when it moves
                e.rep[e.nrep++] = r;
            }
            if (e.nrep == 0)
                continue; // it dies anyway
            if (ne < 8)
                en[ne++] = e;
        }
        if (ne == 0)
            return 0;
        std::sort(en, en + ne, [](const En& a, const En& b) { return a.dist < b.dist; });
        ne = std::min(ne, static_cast<int>(REPLY_MAX_ENEMIES));
        for (int k = 0; k < ne; k++)
            en[k].reach = replyEnemyReach(en[k].si);
        if (static_cast<int>(replyBan.size()) != w.N)
            replyBan.assign(w.N, 0);
        if (static_cast<int>(threatDist.size()) != w.N)
            threatDist.assign(w.N, INF);
        int total = 1;
        for (int k = 0; k < ne; k++)
            total *= en[k].nrep;
        int worst = baseDepth;
        std::vector<int> banned, blocked, blockedOld;
        for (int code = 0; code < total && worst > 1; code++)
        {
            int c = code;
            banned.clear();
            blocked.clear();
            blockedOld.clear();
            for (int k = 0; k < ne; k++)
            {
                int r = en[k].rep[c % en[k].nrep];
                c /= en[k].nrep;
                // the replied head's old tile and r are now its body for at least its visible length
                blocked.push_back(r);
                blockedOld.push_back(freeOther[r]);
                freeOther[r] = std::max(freeOther[r], en[k].len + 2);
                // tiles it can reach on its next move (BFS over tiles free now, bodies stop it)
                tq.clear();
                tq.push_back(r);
                threatDist[r] = 0;
                for (size_t qi = 0; qi < tq.size(); qi++)
                {
                    int u = tq[qi];
                    if (threatDist[u] >= en[k].reach)
                        continue;
                    for (int d = 0; d < 4; d++)
                    {
                        int v = step(u, d);
                        if (v < 0 || threatDist[v] != INF)
                            continue;
                        threatDist[v] = threatDist[u] + 1;
                        tq.push_back(v);
                        if (!replyBan[v])
                        {
                            replyBan[v] = 1;
                            banned.push_back(v);
                        }
                        if (freeT[v] > 1)
                            threatDist[v] = en[k].reach;
                    }
                }
                for (int u : tq)
                    threatDist[u] = INF;
            }
            replyBanOn = true;
            nodeCap = REPLY_NODE_CAP;
            int dep = surviveDepth(t, wantDepth);
            nodeCap = 60000;
            replyBanOn = false;
            for (int v : banned)
                replyBan[v] = 0;
            for (int i = static_cast<int>(blocked.size()) - 1; i >= 0; i--)
                freeOther[blocked[i]] = blockedOld[i];
            replyCombos++;
            worst = std::min(worst, dep);
            if (pointsM() - turnT0 > REPLY_BUDGET_M + 10)
                break; // hard stop inside a candidate
        }
        replyWorst = worst;
        if (worst >= baseDepth)
            return 0;
        double pen = REPLY_SHORT_PEN * std::min(baseDepth - worst, 10);
        if (worst <= 1)
            pen += REPLY_FORCED_PEN + REPLY_FORCED_PER_LEN * myLen; // every 2nd step threatened or lethal
        // being forced next turn is less bad than a head that can ram us now (KING_ESCAPE still has
        // sprints/splits then): never outweigh the direct-threat penalty for a big dragon
        return std::min(pen, REPLY_CAP_FRAC * (25.0 + 4.0 * myLen));
    }

    // KING_ESCAPE (notes/18): a big dragon whose every 1-step move is inside an enemy
    // head's reach sprints 2 (or 3) steps to a threat-free tile, or reverse-splits.
    bool tryKingEscape(int bestD)
    {
        if ((myLen < KING_MIN_LEN && !(QUEEN_ESCAPE && queenSafe() && myLen >= 3)) || bestD < 0 ||
            threatAt[step(myHead, bestD)] == 0)
            return false;
        for (int d = 0; d < 4; d++)
        {
            int t = step(myHead, d);
            if (t >= 0 && !(occId[t] >= 0 && freeT[t] > 1) && threatAt[t] == 0)
            {
                if (ESCAPE_DEADEND_FIX && !(KE_BUDGET_M > 0 && pointsM() - turnT0 > KE_BUDGET_M))
                {
                    // notes/forensics: an unthreatened step into a dead end is not "safe" for a big dragon
                    double pv;
                    int area;
                    bfsFrom(t, pv, area, 3 * myLen + 30);
                    if (area < myLen || surviveDepth(t, SURVIVE_DEPTH) < SURVIVE_DEPTH / 2)
                        continue;
                }
                return false; // a plain step is safe after all
            }
        }
        auto ownIdx = [&](int t) {
            for (int i = 0; i < static_cast<int>(trail.size()); i++)
                if (trail[i] == t)
                    return i;
            return -1;
        };
        std::string bestSeq;
        std::vector<int> bestPath;
        double bs = -1e18;
        bool keOver = false; // KE_BUDGET_M reached
        for (int n = 2; n <= 3 && bestSeq.empty() && !keOver; n++)
        {
            const int paidN = std::max(0, n - (FREE_FIX ? freeSteps(myLen) : 1)); // segments this sprint costs
            if (myLen - paidN < 2)
                break;
            for (int code = 0; code < (n == 2 ? 16 : 64); code++)
            {
                int dirs[3] = {code & 3, (code >> 2) & 3, (code >> 4) & 3};
                int cur = myHead;
                bool ok = true;
                std::vector<int> path;
                int tailFreed = 0; // KING_ESCAPE_TAIL_FIX: own segments released so far
                for (int k = 0; k < n && ok; k++)
                {
                    int t = step(cur, dirs[k]);
                    if (t < 0 || t == myHead || qparkBan(cur, dirs[k])) // ROUND3 P7: the parked queen never escapes into a vault
                    {
                        ok = false;
                        break;
                    }
                    for (int q : path)
                        if (q == t)
                            ok = false;
                    int oi = ownIdx(t);
                    if (oi >= 0)
                    {
                        if (oi < myLen - (KING_ESCAPE_TAIL_FIX ? tailFreed : k + 1)) // occupied BEFORE this step moves
                            ok = false;
                    }
                    else if (occId[t] >= 0 || (!visible[t] && t != w.plainStep(cur, dirs[k])))
                        ok = false; // other dragons don't move during our turn; no blind crossings
                    path.push_back(t);
                    cur = t;
                    if (KING_ESCAPE_TAIL_FIX) // the tail moves unless we ate; each extra step costs one more
                        tailFreed += (visible[t] && w.pearlMem[t] ? 0 : 1) + (k >= (FREE_FIX ? freeSteps(myLen) : 1) ? 1 : 0);
                }
                if (!ok || threatAt[cur] > 0)
                    continue;
                if (KE_BUDGET_M > 0 && pointsM() - turnT0 > KE_BUDGET_M)
                {
                    keOver = true;
                    break;
                }
                double pv;
                int area;
                bfsFrom(cur, pv, area, 3 * myLen + 30);
                int dep = surviveDepth(cur, SURVIVE_DEPTH);
                if (area < myLen - paidN || dep < SURVIVE_DEPTH / 2)
                    continue;
                double sc = 10.0 * pv + dep - ESC_SPRINT_COST * paidN;
                if (sc > bs)
                {
                    bs = sc;
                    bestSeq.clear();
                    for (int k = 0; k < n; k++)
                        bestSeq += DIRC[dirs[k]];
                    bestPath = path;
                }
            }
        }
        if (!bestSeq.empty())
        {
            out += "MOVE " + bestSeq + "\n";
            pending = bestPath;
            if (dbg)
                std::fprintf(dbg, "  -> king escape sprint %s\n", bestSeq.c_str());
            return true;
        }
        int tail = static_cast<int>(trail.size()) >= myLen ? trail[myLen - 1] : -1;
        if (tail >= 0 && !queenSafe() && !queenEarly() && !qGuard() && !(EG_NOSWAP > 0 && ENDGAME_GUARD > 0 && round >= EG_NOSWAP) && units < w.unitLimit && tailHasExit(myLen - 2) && threatAt[tail] == 0)
        {
            bool enemyNearTail = false;
            for (auto& o : segs)
                if (o.head && o.team != w.myTeam && wrapDist(o.tile, tail) <= 2)
                    enemyNearTail = true;
            if (!enemyNearTail)
            {
                r2log("spK", myLen - 2);
                out += "SPLIT " + std::to_string(myLen - 2) + "\n";
                pending.clear();
                pendingSplit = true;
                kingSelf = false;
                if (dbg)
                    std::fprintf(dbg, "  -> king escape reverse split\n");
                return true;
            }
        }
        return false;
    }

    // SPLIT_VIABLE (notes/23): time-aware flood area for one half after SPLIT k (child head =
    // our tail, parent head = our head); own segments free as each half moves, others use freeOther.
    // v39 QSPLIT_ROOM: true if the queen must not split off k now (her side lacks room or an ally head is close)
    // DGU F2 QVAULT bit 1: a portal-only room = a component of the plain (non-portal) step graph of at most
    // QVAULT_MAX tiles whose every way out is a portal (Slithery Fight 2x2 vaults). Its exit lands next to its
    // entrance: on the queen's own neck, her newborn children and the allies trailing her, none of which she sees.
    std::vector<char> vaultT;
    int vaultRound = -1;
    const void* vaultKnown = nullptr; // a recognised map's topology is fixed: build the table once
    bool isVault(int t)
    {
        if (!(QVAULT & 1) || t < 0)
            return false;
        if (vaultRound != round && (!w.known || vaultKnown != w.known))
        {
            vaultRound = round;
            vaultKnown = w.known;
            vaultT.assign(w.N, 0);
            std::vector<int> comp(w.N, -1), q;
            for (int s0 = 0; s0 < w.N; s0++)
            {
                if (comp[s0] >= 0)
                    continue;
                q.clear();
                q.push_back(s0);
                comp[s0] = s0;
                bool portal = false;
                for (size_t i = 0; i < q.size(); i++)
                    for (int d = 0; d < 4; d++)
                    {
                        int v = step(q[i], d);
                        if (v < 0)
                            continue;
                        if (v != w.plainStep(q[i], d))
                        {
                            portal = true;
                            continue;
                        }
                        if (comp[v] < 0)
                            comp[v] = s0, q.push_back(v);
                    }
                if (static_cast<int>(q.size()) <= QVAULT_MAX && portal)
                    for (int u : q)
                        vaultT[u] = 1;
            }
        }
        return vaultT[t] != 0;
    }

    bool qsrBlock(int k)
    {
        if (!QSPLIT_ROOM || !amQueen())
            return false;
        if ((QVAULT & 1) && !RP.qPark && isVault(myHead))
            return true; // DGU F2 QVAULT: no voluntary split inside a portal-only room (the child is born on its exit)
        for (auto& o : segs)
            if (o.head && o.team == w.myTeam && o.id != w.myId && wrapDist(o.tile, myHead) <= QSR_ALLY)
                return true;
        return splitSideArea(false, k, QSR_A) < QSR_A;
    }

    int splitSideArea(bool childSide, int k, int cap)
    {
        int L = myLen, P = L - k;
        if (static_cast<int>(trail.size()) < L || L < 2)
            return cap; // tail unseen: don't block
        std::vector<int> rel(w.N, 0);
        for (int i = 0; i < P; i++)
            rel[trail[i]] = P - i;
        for (int m = 0; m < k; m++)
            rel[trail[L - 1 - m]] = k - m;
        int start = childSide ? trail[L - 1] : trail[0];
        int neck = childSide ? trail[L - 2] : trail[1];
        std::vector<int> q{start}, dist{0};
        std::vector<char> seen(w.N, 0);
        seen[start] = 1;
        int area = 0;
        for (size_t qi = 0; qi < q.size() && area < cap; qi++)
            for (int d = 0; d < 4; d++)
            {
                int v = step(q[qi], d), du = dist[qi] + 1;
                if (v < 0 || seen[v] || (qi == 0 && v == neck))
                    continue;
                if (freeOther[v] > du || rel[v] > du)
                    continue; // occupied when we'd get there
                seen[v] = 1;
                q.push_back(v);
                dist.push_back(du);
                area++;
            }
        return area;
    }

    // R11 MIDSIZE: mid-size units (params.hpp). msBornLen = our length on our first decide().
    int msBornLen = -1;
    bool msLineage = false;
    bool msUnit() const
    {
        if (!MIDSIZE || amQueen() || round < MS_FROM || round >= MS_TO || units < MS_MINUNITS || iAmKing())
            return false;
        if (msLineage)
            return true;
        return MS_MOD <= 1 || ((static_cast<unsigned>(w.myId) * 2654435761u) >> 13) % MS_MOD == 0;
    }

    // MS_SAFE bit 4: a threatened mid-size unit (L >= 5) sheds its bulk as a child from a safe, open tail
    bool msShed(bool threatened) const
    {
        if (!MIDSIZE || !(MS_SAFE & 4) || !threatened || myLen < 5 || !msUnit() || static_cast<int>(trail.size()) < myLen)
            return false;
        return threatAt[trail[myLen - 1]] == 0 && tailHasExit(myLen - 2);
    }

    // R8 SPLIT_DEFER (DEVTEST1 fix 2): the growth split waits up to SPLIT_DEFER consecutive turns for a free
    // tile at our tail, then goes anyway. Called last in the growth-split gate.
    int sdWait = 0, sdRound = -10;
    bool sdOk()
    {
        if (!SPLIT_DEFER)
            return true;
        if (sdRound != round - 1)
            sdWait = 0;
        if (tailHasExit(2) || sdWait >= SPLIT_DEFER)
        {
            sdWait = 0, sdRound = -10;
            return true;
        }
        sdWait++, sdRound = round;
        r2log("sdw", sdWait);
        return false;
    }

    // Can a split-off child whose head is our current tail get away?
    bool tailHasExit(int k) const
    {
        if (static_cast<int>(trail.size()) < myLen)
            return false;
        int tail = trail[myLen - 1];
        for (int d = 0; d < 4; d++)
        {
            int v = step(tail, d);
            if (v < 0)
                continue;
            bool own = false;
            for (int i = 0; i < myLen; i++)
                if (trail[i] == v)
                    own = true;
            if (own)
                continue;
            if (freeOther[v] <= 1)
                return true;
        }
        (void)k;
        return false;
    }

    // ---------------------------------------------------------- per-map modules
    // Each ranked map has its own file in maps/ with an override hook (scripted
    // behaviour) and a score hook (zones, routes). Unknown maps use neither.
#include "maps/schooltime.hpp"
#include "maps/portals.hpp"
#include "maps/trauma.hpp"
#include "maps/queen_of_spades.hpp"
#include "maps/slithery_fight.hpp"
#include "maps/dilemma.hpp"
#include "maps/trophy.hpp"
#include "maps/default.hpp"
#include "maps/autarky.hpp"
#include "maps/devil.hpp"
#include "maps/stripes.hpp"
    int mapKey() const
    {
        if (!w.known)
            return -1;
        static const char* names[] = {"Schooltime", "Portals", "Trauma", "Queen Of Spades", "Slithery Fight",
                                      "Prisoners Dilemma", "Trophy", "Default", "Autarky", "Devil"};
        for (int i = 0; i < 10; i++)
            if (std::strcmp(w.known->name, names[i]) == 0)
                return i;
        return -1;
    }
    bool mapOverride()
    {
        switch (mapKey())
        {
        case 0: return schooltimeOverride();
        case 1: return portalsOverride();
        case 2: return traumaOverride();
        case 3: return queenofspadesOverride();
        case 4: return slitheryfightOverride();
        case 5: return dilemmaOverride();
        case 6: return trophyOverride();
        case 7: return defaultOverride();
        case 8: return autarkyOverride();
        case 9: return devilOverride();
        default: return false;
        }
    }
    double mapScore(int t, int d)
    {
        if (STRIPES_LOOP && stripesOn())
            return stripesScore(t, d);
        switch (mapKey())
        {
        case 0: return schooltimeScore(t, d);
        case 1: return portalsScore(t, d);
        case 2: return traumaScore(t, d);
        case 3: return queenofspadesScore(t, d);
        case 4: return slitheryfightScore(t, d);
        case 5: return dilemmaScore(t, d);
        case 6: return trophyScore(t, d);
        case 7: return defaultScore(t, d);
        case 8: return autarkyScore(t, d);
        case 9: return devilScore(t, d);
        default: return 0.0;
        }
    }

    // ---------------------------------------------------------- v41 FREE_STEPS
    struct EvalOut
    {
        double score = 0, map = 0;
        int threat = 0, depth = 0;
        bool close = false, dead = false, rskip = false;
        bool qb = false; // ROUND2 P3 QAK_HARD: this step blocks our queen
        bool eg = false; // ROUND2 P6 ENDGAME_GUARD: this step ends inside an enemy head's kamikaze reach
    };
    struct FsSave
    {
        int tile, fT, fO, oId;
        char oTeam, oHead, pm;
    };
    std::vector<FsSave> fsSave;
    std::vector<int> fsTrailSave;
    int fsHead = -1, fsDir = 0, fsLen = 0, fsSch = 0, fsTra = 0;
    void fsTouch(int t) { fsSave.push_back({t, freeT[t], freeOther[t], occId[t], occTeam[t], occHead[t], w.pearlMem[t]}); }
    bool fsEats(int t) const { return visible[t] && w.pearlMem[t]; }
    // Virtual body after the free steps p[0..m-1] (no paid steps): each step that eats keeps the tail, each other
    // step releases one tail tile. Head/trail/occupancy/freeT/freeOther/pearls are patched; fsRestore undoes it.
    void fsApply(const std::vector<int>& p, int lastDir)
    {
        fsSave.clear();
        fsTrailSave = trail;
        fsHead = myHead, fsDir = myDir, fsLen = myLen, fsSch = schRusher, fsTra = traRusher;
        const int m = static_cast<int>(p.size());
        int e = 0;
        for (int t : p)
            e += fsEats(t) ? 1 : 0;
        const int newLen = myLen + e;
        const int keep = std::max(0, std::min(static_cast<int>(trail.size()), newLen - m));
        for (int j = keep; j < static_cast<int>(trail.size()); j++)
        {
            int t = trail[j];
            if (occId[t] != w.myId)
                continue;
            fsTouch(t);
            occId[t] = -1, occTeam[t] = 0, occHead[t] = 0, freeT[t] = 1, freeOther[t] = 1;
        }
        std::vector<int> nt;
        nt.reserve(m + keep);
        for (int i = m - 1; i >= 0; i--)
            nt.push_back(p[i]);
        for (int j = 0; j < keep; j++)
            nt.push_back(trail[j]);
        for (int t : p)
            if (fsEats(t))
            {
                fsTouch(t);
                w.pearlMem[t] = 0;
            }
        for (int i = 0; i < static_cast<int>(nt.size()); i++)
        {
            int t = nt[i];
            fsTouch(t);
            occId[t] = w.myId, occTeam[t] = w.myTeam, occHead[t] = i == 0;
            freeT[t] = std::max(2, newLen - i + 1), freeOther[t] = 1;
        }
        trail.swap(nt);
        myHead = p[m - 1], myDir = lastDir, myLen = newLen;
    }
    void fsRestore()
    {
        for (int i = static_cast<int>(fsSave.size()) - 1; i >= 0; i--)
        {
            const FsSave& s = fsSave[i];
            freeT[s.tile] = s.fT, freeOther[s.tile] = s.fO, occId[s.tile] = s.oId;
            occTeam[s.tile] = s.oTeam, occHead[s.tile] = s.oHead, w.pearlMem[s.tile] = s.pm;
        }
        fsSave.clear();
        trail.swap(fsTrailSave);
        myHead = fsHead, myDir = fsDir, myLen = fsLen, schRusher = fsSch, traRusher = fsTra;
    }
    long long fsTurns = 0, fsMulti = 0; // L>=5 plain-move turns / of them multi-step (FS_DEBUG)
    // Beam search over free paths of 2..F steps. Every node is scored by the normal per-move evaluation (evalDir)
    // of its last step on the virtual body left by the earlier steps, plus the mapScore of the earlier steps and
    // FS_EAT_W per pearl eaten before the endpoint. Endpoints must pass the same vetoes as the chosen 1-step move.
    template <class EV>
    bool tryFreePath(EV& evalDir, int bestD, const double* candScore, const double* candMap, const int* candThreat,
                     const int* candDepth, const bool* candClose, const bool* candDead)
    {
        const int F = std::min(freeSteps(myLen), static_cast<int>(FS_MAXF));
        if (F < 2 || bestD < 0 || candScore[bestD] < -1e17)
            return false;
        struct Node
        {
            std::vector<int> tiles, dirs;
            double score, mapAcc, eatAcc;
            EvalOut eo;
            bool qb = false;
        };
        std::vector<Node> beam, all;
        for (int d = 0; d < 4; d++)
        {
            int t = step(myHead, d);
            if (t < 0 || candScore[d] < -1e17 || !visible[t] || qparkBan(myHead, d))
                continue;
            Node n;
            n.tiles = {t};
            n.dirs = {d};
            n.score = candScore[d], n.mapAcc = candMap[d], n.eatAcc = 0;
            n.qb = candQb[d];
            beam.push_back(n);
        }
        auto byScore = [](const Node& a, const Node& b) { return a.score > b.score; };
        for (int k = 2; k <= F && !beam.empty(); k++)
        {
            std::sort(beam.begin(), beam.end(), byScore);
            if (static_cast<int>(beam.size()) > FS_BEAM)
                beam.resize(FS_BEAM);
            std::vector<Node> next;
            for (const Node& nd : beam)
            {
                if (pointsM() - turnT0 > FS_BUDGET_M)
                    break;
                const double eatAcc = nd.eatAcc + (fsEats(nd.tiles.back()) ? FS_EAT_W : 0.0); // before fsApply clears it
                fsApply(nd.tiles, nd.dirs.back());
                for (int d = 0; d < 4; d++)
                {
                    int t = step(myHead, d);
                    if (t < 0 || !visible[t] || qparkBan(myHead, d))
                        continue; // no blind steps inside a sprint (ROUND3 P7: nor steps the queen park forbids)
                    EvalOut eo;
                    inFreePath = true;
                    const bool evOk = evalDir(d, eo);
                    inFreePath = false;
                    if (!evOk || eo.rskip)
                        continue;
                    Node c;
                    c.tiles = nd.tiles;
                    c.tiles.push_back(t);
                    c.dirs = nd.dirs;
                    c.dirs.push_back(d);
                    c.eatAcc = eatAcc;
                    c.mapAcc = nd.mapAcc + eo.map;
                    c.score = eo.score + nd.mapAcc + eatAcc;
                    c.eo = eo;
                    c.qb = nd.qb || eo.qb;
                    next.push_back(c);
                }
                fsRestore();
            }
            for (auto& c : next)
                all.push_back(c);
            beam.swap(next);
        }
        const Node* bestN = nullptr;
        double need = candScore[bestD] + FS_MARGIN;
        for (Node& c : all)
        {
            if (c.eo.threat > 0 && candThreat[bestD] == 0)
                continue;
            if (c.eo.depth < std::min(candDepth[bestD], static_cast<int>(SURVIVE_DEPTH)))
                continue;
            if (c.eo.close && !candClose[bestD])
                continue;
            if (c.eo.dead && !candDead[bestD])
                continue;
            if (c.qb && !candQb[bestD])
                continue; // ROUND2 P3: no sprint through tiles next to our queen
            if (c.eo.eg && !candEg[bestD])
                continue; // ROUND2 P6: no sprint ending inside an enemy head's reach
            const int e = c.tiles.back(), b1 = step(myHead, bestD);
            if (FS_PAID_VETO && threatPaidAt[e] > 0 && threatPaidAt[b1] == 0 && candThreat[bestD] == 0)
                continue; // no new exposure to a paid-step ram that the plain move avoids
            if (FS_VIS)
            {
                // vision is 7x7 around the current head: an endpoint near its edge may have unseen heads beside it
                int blind1 = 0, blind2 = 0;
                for (int d1 = 0; d1 < 4; d1++)
                {
                    int u = step(e, d1);
                    if (u < 0)
                        continue;
                    if (!visible[u])
                        blind1++;
                    for (int d2 = 0; d2 < 4; d2++)
                    {
                        int v = step(u, d2);
                        if (v >= 0 && v != e && !visible[v])
                            blind2++;
                    }
                }
                if (blind1 > 0 || (blind2 > 0 && queenSafe()))
                    continue;
                c.score -= FS_BLIND_PEN * blind2;
            }
            if (c.score > need)
                need = c.score, bestN = &c;
        }
        if (dbg)
            std::fprintf(dbg, "  FS F=%d paths=%zu best1=%c %.2f -> %s\n", F, all.size(), DIRC[bestD], candScore[bestD],
                         bestN ? "multi" : "single");
        if (!bestN)
            return false;
        out += "MOVE ";
        int cur = myHead;
        for (size_t i = 0; i < bestN->dirs.size(); i++)
        {
            int d = bestN->dirs[i];
            out += DIRC[d];
            if (bestN->tiles[i] != w.plainStep(cur, d))
                lastPortalRound = round;
            cur = bestN->tiles[i];
        }
        out += '\n';
        lastMoveDir = bestN->dirs.back();
        pending = bestN->tiles;
        if (dbg)
            std::fprintf(dbg, "  -> free path %zu steps score %.2f\n", bestN->dirs.size(), bestN->score);
        return true;
    }

    void decide()
    {
        out.clear();
        if (!logPending.empty())
            out.swap(logPending);
        if (myHead < 0)
        {
            emitMove(myDir);
            return;
        }
        if (MIDSIZE && msBornLen < 0)
            msBornLen = myLen, msLineage = MS_INHERIT && round >= MS_FROM && myLen >= 3 && !amQueen();
        updateQsPhase();
        qparkPrep();
        qsmPrep();
        if (PM_TD_PULL > 0)
            tdPrep(); // DGU F4
        if (QBOX || QGUARD)
            computeQRegion();
        eqHuntPrep();
        lhPrep();
        PROF_BEGIN(th);
        computeThreats();
        PROF_END(th, 2);
        if (mapOverride())
            return;

        // ---- rams (distance 1-2)
        if (tryRam())
            return;

        // ---- CONSOLIDATION: a small dragon with a longer ally in range merges into it (replaces king feeding)
        if (CONS_R)
        {
            pickConsHost();
            if (!CONS_OVER_KING && consActive && shouldFeed())
                consActive = false; // the king's own feeder pipeline keeps priority
#if CONS_TRACE
            if (round >= CONS_R && myLen <= CONS_MAXLEN)
                if (const char* ct = std::getenv("CONS_TRACE_DIR"))
                    if (FILE* tf = std::fopen((std::string(ct) + "/" + std::to_string(w.myId) + ".txt").c_str(), "a"))
                    {
                        std::fprintf(tf, "%d %d L%d u%d act%d host%d hl%d vis%d first%d dk%d thr%d king%d kl%d\n", round, w.myId, myLen,
                                     units, consActive, consHostId, consHostLen, consHostVis, consFirst,
                                     consHostTile >= 0 ? wrapDist(myHead, consHostTile) : -1, threatAt[myHead], kingId, kingLen);
                        std::fclose(tf);
                    }
#endif
            if (!queenSafe() && tryConsFeed())
                return;
        }
        // ---- feeding the king: die just in front of it so it eats our body
        bool feeding = shouldFeed() && !consActive && !queenSafe(); // consActive is false with CONS_R off
        int target = feeding ? feedTarget() : -1;
        if (feeding && target >= 0)
        {
            bool kingVisible = false;
            for (auto& sg : segs)
                if (sg.head && sg.id != w.myId && kw10(sg.id) == kw10(kingId) && sg.team == w.myTeam)
                    kingVisible = true;
            int dk = wrapDist(myHead, kingTile);
            int feedDist = (RP.lateFeedRound > 0 && round >= RP.lateFeedRound) ? 6 : FEED_DIST;
            bool dieNow = kingVisible && dk >= 2 && dk <= feedDist && wrapDist(myHead, target) <= 2;
            if (KING_V2 && RP.kingDeclare)
            {
                // die 1-2 tiles straight ahead of the king or right beside it, when it's
                // safe and the previous feeder's pearls have been eaten
                int k = kingTile, f = kingDir;
                int a1 = step(k, f), a2 = a1 >= 0 ? step(a1, f) : -1;
                int sl = step(k, (f + 3) % 4), sr = step(k, (f + 1) % 4);
                bool spot = myHead == a1 || myHead == a2 || myHead == sl || myHead == sr;
                bool enemyNear = false, foodWaiting = false;
                for (auto& o : segs)
                    if (o.head && o.team != w.myTeam && wrapDist(o.tile, k) <= 4)
                        enemyNear = true;
                for (int t2 : {a1, a2, sl, sr})
                    if (t2 >= 0 && visible[t2] && w.pearlMem[t2])
                        foodWaiting = true;
                dieNow = kingVisible && !enemyNear && (spot || (KING_V2_LOOSE && dieNow)) && (!foodWaiting || KING_V2_LOOSE);
                if (FEED_QUEUE && dieNow)
                {
                    // one feeder at a time: the ally head closest to the king (ties: lower id),
                    // only right next to it, and not while its last meal is still lying there
                    bool closest = true;
                    for (auto& o : segs)
                        if (o.head && o.team == w.myTeam && o.id != w.myId && kw10(o.id) != kw10(kingId))
                        {
                            int od = wrapDist(o.tile, k);
                            if (od < dk || (od == dk && o.id < w.myId))
                                closest = false;
                        }
                    dieNow = closest && dk <= 3 && !foodWaiting;
                }
            }
            if (feedsQueen())
            {
                // ROUND3 P7: feeders of the queen-king never crowd her head (a boxed queen sheds 2 a turn):
                // die PM_QK_DMIN..PM_QK_DMAX walking steps away and let her come to the pearls
                // (an enemy head nearby does not stop it: feeders waiting round her are what boxes her)
                int wd = (kingVisible && dk <= PM_QK_DMAX) ? walkDist(myHead, kingTile, PM_QK_DMAX) : 99;
                dieNow = kingVisible && wd >= PM_QK_DMIN && wd <= PM_QK_DMAX;
            }
            if (dieNow)
            {
                // move into our own neck: we die here and leave pearls behind
                out += std::string("MOVE ") + DIRC[(myDir + 2) % 4] + "\n";
                pending.clear();
                if (dbg)
                    std::fprintf(dbg, "  -> feed suicide\n");
                return;
            }
        }

        // ---- sprint to grab contested pearls before an enemy can (EAT_SPRINT)
        if (EAT_SPRINT && tryEatSprint())
            return;

        // ---- splitting
        bool threatened = threatAt[myHead] > 0 || (PORTAL_NO_SPLIT && portalExit[myHead]);
        bool bigLate = RP.kingDeclare && round >= RP.kingSeedRound && myLen >= KING_MIN_LEN;
        if (RP.keepLen > 0 && myLen >= RP.keepLen)
        {
            // keep one long dragon; only peel 2-long pieces off when it's much longer
            bigLate = true;
            if (myLen >= RP.keepLen + 4 && units < w.unitLimit && round < RP.splitStopRound && !threatened && !noVolSplit() &&
                qgCap(2) >= 2 && !qsrBlock(2))
            {
                r2log("spA", 2);
                out += "SPLIT 2\n";
                pending.clear();
                pendingSplit = true;
                return;
            }
        }
        // PUMP_TIP_SPLIT (notes/19): inside a dead end with a pearl next to us, keep eating and split
        // at the tip, where the child takes L-2 out (a 2-long head dies there, not a 3-long one)
        int holdTile = -1;
        if (PUMP_TIP_SPLIT && myLen >= 4 && myLen <= 6 && !threatened && tailHasExit(myLen - 2))
        {
            for (int d = 0; d < 4 && holdTile < 0; d++)
            {
                int t = step(myHead, d);
                if (t < 0 || (occId[t] >= 0 && freeT[t] > 1) || !((visible[t] && w.pearlMem[t]) || (w.gmax[t] == 1 && w.gmin[t] == 1)))
                    continue;
                double pp;
                int area;
                bfsFrom(t, pp, area, myLen + 3);
                if (area < myLen + 3)
                    holdTile = t;
            }
        }
        int tipK = 0;
        if (PUMP_TIP2 && myLen >= 4 && myLen <= PUMP_TIP2_MAXLEN && !threatened && !(RP.kingDeclare && kingSelf) &&
            !bigLate)
        {
            std::vector<int> reg = staticAhead(PUMP_TIP2_REGION);
            bool clean = !reg.empty();
            for (size_t i = 1; i < reg.size() && clean; i++)
                if (occHead[reg[i]] && occId[reg[i]] != w.myId)
                    clean = false; // someone else's head in there: not our treadmill
            if (clean)
            {
                // nearest tile ahead that holds a pearl now or refills every round
                int bestStep = -1, bestDist = 1 << 20;
                for (int d = 0; d < 4; d++)
                {
                    int t = step(myHead, d);
                    if (t < 0 || std::find(reg.begin(), reg.end(), t) == reg.end() || (occId[t] >= 0 && freeT[t] > 1))
                        continue;
                    // static BFS inside the region from t
                    std::vector<int> q{t}, dist{0};
                    for (size_t qi = 0; qi < q.size(); qi++)
                    {
                        int u = q[qi];
                        if ((visible[u] && w.pearlMem[u]) || (w.gmax[u] == 1 && w.gmin[u] == 1))
                        {
                            if (dist[qi] < bestDist)
                                bestDist = dist[qi], bestStep = t;
                            break;
                        }
                        for (int d2 = 0; d2 < 4; d2++)
                        {
                            int v = step(u, d2);
                            if (v < 0 || v == myHead || std::find(reg.begin(), reg.end(), v) == reg.end() ||
                                std::find(q.begin(), q.end(), v) != q.end())
                                continue;
                            q.push_back(v);
                            dist.push_back(dist[qi] + 1);
                        }
                    }
                }
                if (bestStep >= 0 && tailHasExit(myLen - 2))
                    holdTile = bestStep; // keep eating toward the tip; the split happens there
                else if (bestStep < 0 && tailHasExit(myLen - 2) &&
                         (!PUMP_TIP2_ATE || round - lastGrowRound <= PUMP_TIP2_REGION))
                    tipK = myLen - 2; // harvested and nothing left ahead: the child (tail end) takes the bulk out
                if (dbg)
                    std::fprintf(dbg, "TIP2 reg=%zu hold=%d tipK=%d\n", reg.size(), holdTile, tipK);
            }
        }
        bool stLap = STRIPES_LOOP && stripesOn() && stripesLapper();
        if (stLap && threatAt[myHead] <= 0 && stripesLapSplit())
        {
            out += "SPLIT 2\n"; // R3 STRIPES_LOOP: the lapping queen peels a 2-child off on the open side of the loop
            pending.clear();
            pendingSplit = true;
            return;
        }
        bool pfIn = false;
        if (DIVE_VALUE && !POCKET_FACTORY)
            pfCompute();
        if (POCKET_FACTORY)
        {
            pfCompute();
            pfIn = pfInward() && myLen <= PF_MAXLEN && !(queenSafe() && threatAt[myHead] > 0) && !queenEarly() && !qGuard() && !qparkNoDive() && !whNoPump();
            if (pfIn)
            {
                // inside a pocket facing inward: eat on while food lies ahead, then split so the child
                // (our tail end, facing out) takes everything but a 2-long stub out
                holdTile = -1;
                tipK = 0;
                double bestP = 0;
                int bestT = -1, anyFree = -1;
                for (int d = 0; d < 4; d++)
                {
                    int t = step(myHead, d);
                    if (t < 0 || t == trail[1] || pfDepth[t] <= pfDepth[myHead] || freeT[t] > 1)
                        continue;
                    anyFree = t;
                    double P = pfBranch(t, 1, 24);
                    if (P > bestP)
                        bestP = P, bestT = t;
                }
                bool splitNow = bestT < 0 || bestP < PF_AHEAD_MIN;
                if (!splitNow)
                {
                    holdTile = bestT;
                    // early split (PF_EARLY): peel the bulk off now while the parent's own certain food
                    // still gets it back to 4 at the end; same total length out, one more unit sooner
                    if (PF_EARLY && myLen >= 4 && units <= w.unitLimit - PF_UNIT_RESERVE)
                    {
                        double Pc = pfBranch(bestT, 1, 24, nullptr, true);
                        int k = std::min(myLen - 2, static_cast<int>(myLen + Pc - 4.0 + 1e-6));
                        if (PF_CHILD_MAX > 0 && k > PF_CHILD_MAX)
                            k = PF_CHILD_MAX;
                        k = qgCap(k);
                        if (noVolSplit())
                            k = 0;
                        int A = std::min(PF_CHILD_AREA, k + 2);
                        if (k >= 2 && splitSideArea(true, k, A) >= A && !qsrBlock(k))
                        {
                            if (dbg)
                                std::fprintf(dbg, "PF early split k=%d Pc=%.1f\n", k, Pc);
                            r2log("spB", k);
                            out += "SPLIT " + std::to_string(k) + "\n";
                            pending.clear();
                            pendingSplit = true;
                            return;
                        }
                    }
                }
                else if (myLen >= 4 && units < w.unitLimit)
                {
                    int k = myLen - 2;
                    if (PF_CHILD_MAX > 0 && k > PF_CHILD_MAX + 1)
                        k = PF_CHILD_MAX; // several small children, one per turn (the parent stays >= 4)
                    k = qgCap(k);
                    bool pfBlock = k < 2 || noVolSplit() || qsrBlock(k); // v37e QGUARD; v39 QSPLIT_ROOM
                    int A = std::min(PF_CHILD_AREA, std::max(k, 2) + 2);
                    bool ok = !pfBlock && splitSideArea(true, k, A) >= A;
                    if (!pfBlock && (ok || anyFree < 0))
                    {
                        if (dbg)
                            std::fprintf(dbg, "PF split k=%d aheadP=%.2f childOK=%d\n", k, bestP, ok ? 1 : 0);
                        r2log(ok ? "spC" : "spCb", k);
                        out += "SPLIT " + std::to_string(k) + "\n";
                        pending.clear();
                        pendingSplit = true;
                        return;
                    }
                    holdTile = anyFree; // child blocked right now: step deeper and try again next turn
                }
                else if (anyFree >= 0)
                    holdTile = bestT >= 0 ? bestT : anyFree;
                if (dbg)
                    std::fprintf(dbg, "PF in depth=%d len=%d aheadP=%.2f hold=%d units=%d/%d any=%d\n", pfDepth[myHead], myLen, bestP, holdTile, units, w.unitLimit, anyFree);
            }
        }
        if (!pfIn && !stLap && holdTile < 0 && !(RP.kingDeclare && kingSelf) && !bigLate && !noVolSplit() && (!SPLIT_NEEDS_EXIT || tailHasExit(2)) &&
            !(CONS_R && CONS_NOSPLIT && (consActive || consHostKeep())) &&
            !(UNK_SEALED_FOOD && !w.known && UNK_SEALED_ROOM_MIN > 0 && roomSize(UNK_SEALED_ROOM_MIN) < UNK_SEALED_ROOM_MIN) && myLen >= (MIDSIZE && msUnit() ? (msShed(threatened) ? 5 : MS_LEN) : SPLIT_LEN) && myLen >= 4 && units < w.unitLimit && units < SPLIT_MAX_UNITS &&
            (round < RP.splitStopRound || (RP.lateSplitRound > 0 && round < RP.lateSplitRound && myLen <= LATE_SPLIT_MAXLEN)) &&
            (!threatened || msShed(threatened)) && sdOk())
        {
            int k = SPLIT_CHILD > 0 ? std::min(SPLIT_CHILD, myLen - 2) : myLen / 2;
            if (tipK > 0)
                k = tipK;
            else if (MIDSIZE && msUnit())
            {
                // R11 MIDSIZE: bulk (child L-2 leaves from the tail) or half; fall back if the tail end is closed
                int kb = MS_BULK || threatened ? myLen - 2 : myLen / 2;
                if (tailHasExit(kb))
                    k = kb;
                else if (tailHasExit(myLen / 2))
                    k = myLen / 2;
                r2log("msp", k);
            }
            else if (PUMP_TIP_SPLIT)
            {
                int exits = 0; // at a dead-end tip the child (our tail end) takes the bulk out
                for (int d = 0; d < 4; d++)
                {
                    int t = step(myHead, d);
                    if (t < 0 || (occId[t] >= 0 && freeT[t] > 1))
                        continue;
                    if (PUMP_TIP_DEADEND)
                    {
                        // a 1-2 tile tip only leads deeper into the pocket: not an exit (notes/22)
                        double pp;
                        int ar;
                        bfsFrom(t, pp, ar, 4);
                        if (ar < 3)
                            continue;
                    }
                    exits++;
                }
                if (exits == 0 && tailHasExit(myLen - 2))
                    k = myLen - 2;
            }
            bool viable = true;
            if (qsmQueen())
                k = myLen - qsmFloor(); // R10 LANE_QSMALL: split everything above the small floor off
            else if (queenEarly() && !qFloorOff() && myLen - k < 3)
            {
                k = myLen - 3; // the early queen keeps >= 3 of herself
                if (k < 2)
                    viable = false;
            }
            if (POCKET_FACTORY && pfChildInwardBad(k))
                viable = false; // the child would be born inside a pocket facing in, with too little to eat
            if (viable && SPLIT_VIABLE > 0)
            {
                // don't give birth into a sealed spot (37% of our splits at 50+ units; notes/23)
                int A = SPLIT_VIABLE + (units * 4 >= w.unitLimit * 3 ? SPLIT_VIABLE_DENSE : 0);
                if (splitSideArea(true, k, A) < A)
                    viable = false;
                else if (myLen >= 5 && splitSideArea(false, k, A) < A)
                    k = myLen - 2; // parent sealed at a tip: the bulk leaves as the child
            }
            if (qGuard() || qboxLate() || qsmQueen())
            {
                k = qgCap(k); // v37e QGUARD (from v37b): the queen keeps >= QG_MIN (covers every k=L-2 branch above)
                if (k < 2)
                    viable = false;
            }
            if (viable && qsrBlock(k))
                viable = false; // v39 QSPLIT_ROOM (covers the tip k=L-2 branches too)
            if (LH_LONG && lhActive && myLen - k < LHL_KEEP)
                viable = false, r2log("lhl", k); // ROUND2 P1: a hunter stays long enough to reach her (K(L) = F + L - 2)
            if (viable)
            {
                if (R2_DEBUG)
                    r2log(tipK > 0 ? "spDt" : (k == myLen - 2 && k != myLen / 2 ? "spDx" : "spD"), k * 100 + (tailHasExit(2) ? 1 : 0));
                out += "SPLIT " + std::to_string(k) + "\n";
                pending.clear();
                pendingSplit = true;
                return;
            }
        }

        if (UNK_EXPLORE && !w.known)
            computeExploreDesire();
        int hotTarget = -1;
        // PF_PULL: a short free dragon that is the nearest of us to a free, stocked pocket mouth walks to it
        int pfTarget = -1;
        if (POCKET_FACTORY && PF_PULL > 0 && !pfIn && myLen >= 2 && myLen <= PF_ENTER_MAXLEN && !feeding && !consActive && !iAmKing() && !qparkNoDive() &&
            units <= w.unitLimit - PF_UNIT_RESERVE && !pfDepth.empty() && pfDepth[myHead] == 0)
        {
            int bd = PF_PULL_RANGE + 1;
            for (int m = 0; m < w.N; m++)
            {
                if (pfDepth[m] != 1)
                    continue;
                int dd = wrapDist(myHead, m);
                if (dd >= bd || dd < 2)
                    continue; // adjacent: the entry test decides
                bool busy = false, nearer = false;
                int en = 0, al = 1;
                for (auto& o : segs)
                {
                    if (!o.head || o.id == w.myId)
                        continue;
                    if (pfDepth[o.tile] > 0 && pfComp[o.tile] == pfComp[m])
                        busy = true;
                    int od = wrapDist(o.tile, m);
                    if (o.team == w.myTeam)
                    {
                        if (od < dd || (od == dd && o.id < w.myId))
                            nearer = true;
                        if (od <= 3)
                            al++;
                    }
                    else if (od <= 3)
                        en++;
                }
                if (busy || nearer || en > al)
                    continue;
                if (pfBranch(m, dd, dd + 24) < PF_MIN_P)
                    continue;
                bd = dd, pfTarget = m;
            }
            if (dbg && pfTarget >= 0)
                std::fprintf(dbg, "PF pull (%d,%d) d=%d\n", pfTarget % w.W, pfTarget / w.W, bd);
        }
        if (HOT_PULL > 0 && myLen <= 3 && !feeding && !consActive && !iAmKing() && !qparkNoDive())
        {
            if (hotMouthRound < 0 || (!w.known && round - hotMouthRound >= 25))
                computeHotMouths();
            int bd = HOT_PULL_RANGE + 1;
            for (int mt : hotMouth)
            {
                int dd = wrapDist(myHead, mt);
                if (dd >= bd)
                    continue;
                int alliesAt = 0;
                for (auto& o : segs)
                    if (o.head && o.id != w.myId && o.team == w.myTeam && wrapDist(o.tile, mt) <= 2)
                        alliesAt++;
                if (alliesAt >= 2)
                    continue; // enough of us there already
                bd = dd, hotTarget = mt;
            }
        }
        if (queenSafe() && QUEEN_LOOK)
            computeQueenLook();
        // ---- score each direction
        double best = -1e18;
        int bestD = -1;
        int bestDepth = 0;
        int areaCap = 3 * myLen + 30;
        double candScore[4] = {-1e18, -1e18, -1e18, -1e18};
        int candThreat[4] = {0, 0, 0, 0}, candDepth[4] = {0, 0, 0, 0};
        bool candClose[4] = {false, false, false, false};
        bool candDead[4] = {false, false, false, false};
        double candMap[4] = {0, 0, 0, 0}; // v41: mapScore part of candScore (FREE_STEPS sums it along a path)
        int qgAllyHead = -1; // v37e QGUARD (from v37b): our queen's visible head (allies keep out of their own K of it)
        if (QGUARD && !amQueen() && (round >= QG_FROM || units >= QG_UNITS))
            for (auto& o : segs)
                if (o.head && o.team == w.myTeam && o.id <= 1)
                    qgAllyHead = o.tile;
        // v43 QEXIT_KEEP: non-queen allies don't take the last free exits of our queen's head (Maze/weakhold:
        // she was walled in by ally bodies, then trap-split to L2 and died on an ally body)
        int qekHead = -1, qekN0 = 0;
        auto qekCount = [&](int extra) -> int {
            int n = 0;
            for (int e = 0; e < 4; e++)
            {
                int u = step(qekHead, e);
                if (u < 0 || u == extra)
                    continue;
                if (occId[u] >= 0 && !(occId[u] == w.myId && freeT[u] <= 1))
                    continue;
                n++;
            }
            return n;
        };
        if (QEXIT_KEEP && !amQueen() && round >= QEK_FROM)
        {
            for (auto& o : segs)
                if (o.head && o.team == w.myTeam && o.id <= 1)
                    qekHead = o.tile;
            if (qekHead >= 0)
                qekN0 = qekCount(-1);
        }
        // v38 QALLY_KEEP (notes/newrules/V38.md): non-queen allies don't end a step within QAK_DIST of our queen's
        // head or on her best escape tiles (her open first step with the largest small flood + its next QAK_ESC_DEPTH
        // tiles). Late-game feeding of the queen is exempt. Queen known = seen this turn, else a fresh beacon.
        int qakHead = -1;
        std::vector<int> qakEsc;
        if (QALLY_KEEP && !amQueen() && round >= QAK_FROM &&
            (RP.queenKing || !(feedPhase() && kingId >= 0 && kw10(kingId) <= 1 && shouldFeed())))
        {
            for (auto& o : segs)
                if (o.head && o.team == w.myTeam && o.id <= 1)
                    qakHead = o.tile;
            if (qakHead < 0)
                for (auto& k : kingsSeen)
                    if (k.id <= 1 && k.round >= round - 1 && k.tile >= 0)
                        qakHead = k.tile;
            if (qakHead >= 0 && wrapDist(myHead, qakHead) <= ((RP.queenKing && queenKingRound()) ? PM_QK_KEEP : QAK_DIST) + 3)
            {
                int bestA = 0;
                std::vector<int> nodes;
                for (int qd = 0; qd < 4; qd++)
                {
                    int n = step(qakHead, qd);
                    if (n < 0 || (occId[n] >= 0 && freeT[n] > 1))
                        continue;
                    // small flood from n (cap QAK_CAP), keeping the nodes within QAK_ESC_DEPTH of n
                    std::vector<std::pair<int, int>> q{{n, 0}};
                    std::vector<int> near{n};
                    for (size_t i = 0; i < q.size() && static_cast<int>(q.size()) < QAK_CAP; i++)
                        for (int e = 0; e < 4; e++)
                        {
                            int v = step(q[i].first, e);
                            if (v < 0 || v == qakHead || (occId[v] >= 0 && freeT[v] > q[i].second + 2))
                                continue;
                            bool dup = false;
                            for (auto& [x, dx] : q)
                                if (x == v)
                                {
                                    dup = true;
                                    break;
                                }
                            if (dup)
                                continue;
                            q.push_back({v, q[i].second + 1});
                            if (q[i].second + 1 <= QAK_ESC_DEPTH)
                                near.push_back(v);
                        }
                    int A = static_cast<int>(q.size());
                    if (A > bestA)
                        bestA = A, nodes = near;
                    else if (A == bestA)
                        nodes.insert(nodes.end(), near.begin(), near.end());
                }
                qakEsc.swap(nodes);
            }
            else
                qakHead = -1;
        }
        // ROUND2 P3 QAK_HARD: our queen's visible head, for long allies (not while feeding her as the king)
        int qhHead = -1, qhN0 = 0, qhD0 = 0;
        auto qhCount = [&](int extra) -> int {
            int n = 0;
            for (int e = 0; e < 4; e++)
            {
                int u = step(qhHead, e);
                if (u < 0 || u == extra)
                    continue;
                if (occId[u] >= 0 && !(occId[u] == w.myId && freeT[u] <= 1))
                    continue;
                n++;
            }
            return n;
        };
        if (QAK_HARD && !amQueen() && myLen >= QAKH_LEN && round >= QAK_FROM &&
            !(feedPhase() && kingId >= 0 && kw10(kingId) <= 1 && shouldFeed()))
        {
            for (auto& o : segs)
                if (o.head && o.team == w.myTeam && o.id <= 1)
                    qhHead = o.tile;
            if (qhHead >= 0)
                qhN0 = qhCount(-1), qhD0 = wrapDist(myHead, qhHead);
        }
        for (int d = 0; d < 4; d++)
            candQb[d] = candEg[d] = false;
        const bool egGuard = egOn();
        const bool whcOn = whcActive(); // v44 WH_CENTRE
        // v41: the per-move evaluation as a lambda so FREE_STEPS can run it on a virtual (advanced) body
        auto evalDir = [&](int d, EvalOut& eo) -> bool {
            int t = step(myHead, d);
            if (t < 0)
                return false; // kelp
            if (occId[t] >= 0 && freeT[t] > 1)
                return false; // occupied (rams handled above)
            double score = 0;
            if ((QVAULT & 1) && !RP.qPark && amQueen() && !isVault(myHead))
            {
                // DGU F2 QVAULT: the queen doesn't walk into a portal-only room, nor onto its mouth when her own
                // body or others leave the room as the only way on
                if (isVault(t))
                    score -= QVAULT_PEN;
                else
                {
                    int vaultNb = 0, exits = 0;
                    for (int e = 0; e < 4; e++)
                    {
                        int v = step(t, e);
                        if (v < 0 || v == myHead)
                            continue;
                        if (isVault(v))
                            vaultNb++;
                        else if (!(occId[v] >= 0 && freeT[v] > 2))
                            exits++;
                    }
                    if (vaultNb > 0 && exits == 0)
                        score -= QVAULT_PEN;
                }
            }
            if (QBOX && amQueen() && visible[t] && w.pearlMem[t])
            {
                // QBOX: eating keeps the tail in place; with no free neighbour of t next turn she is boxed (L4 Schooltime)
                bool exitNext = false;
                for (int e = 0; e < 4 && !exitNext; e++)
                {
                    int v = step(t, e);
                    if (v < 0 || v == myHead || v == t)
                        continue;
                    if (occId[v] == w.myId)
                        continue; // own body: nothing moves when she eats
                    if (occId[v] >= 0 && freeT[v] > 2)
                        continue;
                    exitNext = true;
                }
                if (!exitNext)
                    score -= QBOX_EAT_PEN;
            }
            double pearls;
            int area;
            bfsFrom(t, pearls, area, areaCap);
            if (RP.qPark == 1 && amQueen() && round < qkFeedRound())
                pearls = 0; // ROUND3 P7: the parked Portals queen wants no food (it is all behind portals)
            score += 10.0 * pearls;
            int need = myLen + 3;
            bool pfEntry = POCKET_FACTORY && !pfIn && !pfDepth.empty() && pfDepth[t] > pfDepth[myHead];
            const bool msBig = MIDSIZE && myLen >= 5 && msUnit();
            if (msBig && area < need)
                score -= MS_POCKET; // R11 MIDSIZE: a mid-size unit stays out of pockets
            if (msBig && (MS_SAFE & 8))
                for (auto& o : segs)
                    if (o.head && o.team != w.myTeam && wrapDist(o.tile, t) <= MS_NEAR_R)
                        score -= MS_NEAR_PEN * (MS_NEAR_R + 1 - wrapDist(o.tile, t)); // MS_SAFE bit 8: keep off enemy heads
            bool pump = POCKET_PUMP && area < need && !msBig && !qGuard() && !qparkNoDive() && !whNoPump() && (t == holdTile || (pfEntry ? pfDiveOK(t) : pocketWorthPumping(t)));
            eo.dead = qGuard() && area < need; // v37e QGUARD (from v37b): a dead end she can't turn around in
            if (QNOPOCKET && amQueen() && round >= 1 && !pfDepth.empty() && pfDepth[t] > 0 && pfDepth[t] > pfDepth[myHead])
                eo.dead = true; // v43 QNOPOCKET: a leaf-pruned pocket is a tree; heading in, she can never turn back
            if (STRIPES_LOOP && eo.dead && stripesOn() && stripesLapNext(t))
                eo.dead = false; // R3 STRIPES_LOOP: the next tile of the loop is never a dead end (the loop closes behind her)
            if (pfEntry && pump && PF_BONUS > 0)
                score += PF_BONUS * (pfLastP - 2.0); // expected net length of the cycle, certain food
            if (POCKET_FACTORY && pfIn && t != holdTile && holdTile >= 0)
                score -= 50.0; // inside: the planned branch (the others are shorter or empty)
            if (area < need && !pump)
                score -= AREA_WEIGHT * (need - area) / need + 20;
            if ((QVAULT & 2) && !RP.qPark && amQueen() && w.known && std::strcmp(w.known->name, "Australia") == 0 && !queenSafe() && !visible[t] && t != w.plainStep(myHead, d) &&
                area < QVAULT_AUS_AREA)
                score -= QVAULT_AUS_PEN; // DGU F2 QVAULT bit 2: early queen never enters the Australia portal vault
            if (DIVE_VALUE && (DV_PARTS & 8) && !pump && !pfIn && t != holdTile && myLen <= PF_MAXLEN && !pfDepth.empty() &&
                pfDepth[t] > 0 && pfDepth[myHead] == 0)
            {
                double V = dvValue(t); // a dead-end entry nobody approved: pay for the length it loses
                if (V < DV_MARGIN)
                    score -= DV_PEN * (DV_MARGIN - V);
            }
            if (DIVE_VALUE && DV_FUNNEL > 0 && !pfIn && myLen <= PF_MAXLEN && !pfDepth.empty() && pfDepth[t] == 0)
            {
                // the same rule one step early: a core tile whose only core exit another head can take first
                // leaves a pocket entry as the only move next turn
                int coreX = -1, nCore = 0;
                double Vf = -1e9;
                for (int d2 = 0; d2 < 4; d2++)
                {
                    int v = step(t, d2);
                    if (v < 0 || v == t || v == myHead || freeT[v] > 2)
                        continue;
                    if (pfDepth[v] == 0)
                        nCore++, coreX = v;
                    else
                    {
                        int e = 2;
                        double P = pfBranch(v, 2, 26, &e) * dvContest(v);
                        Vf = std::max(Vf, dvNet(P, e));
                    }
                }
                if (nCore == 1 && Vf > -1e8 && Vf < DV_MARGIN)
                {
                    bool contested = false;
                    for (auto& o : segs)
                        if (o.head && o.id != w.myId && wrapDist(o.tile, coreX) <= 2)
                            contested = true;
                    if (contested)
                    {
                        score -= DV_FUNNEL * DV_PEN * (DV_MARGIN - Vf);
                        if (dbg)
                            std::fprintf(dbg, "DV funnel t=(%d,%d) Vf=%.2f\n", t % w.W, t / w.W, Vf);
                    }
                }
            }
            int wantDepth = myLen >= 10 ? std::max(SURVIVE_DEPTH, std::min(myLen, KING_SURVIVE_DEPTH)) : SURVIVE_DEPTH;
            // ROUND6 QK_SURV: crowned queen looks further, park bans block; bounded by nodes per call and a turn budget
            const bool qkSurv = QK_SURV && amQueen() && queenKingRound() && pointsM() - turnT0 < QK_SURV_BUDGET_M;
            if (qkSurv)
                wantDepth = std::max(wantDepth, std::min(myLen, static_cast<int>(QK_SURV_CAP))), survQBan = true,
                nodeCap = inFreePath ? QK_SURV_FSNODES : QK_SURV_NODES;
            int depth = surviveDepth(t, wantDepth);
            if (qkSurv)
                survQBan = false, nodeCap = 60000;
            if (depth < wantDepth && !pump)
                score -= 150.0 + 40.0 * (wantDepth - depth);
            if (pump)
                score += POCKET_PUMP_BONUS;
            if (pump && POCKET_CERTAIN > 0 && t != holdTile)
                score += POCKET_CERTAIN * pocketPearlsLast; // 3 pearls 1-3 steps away are certain, not a discounted guess
            if (REPLY_SEARCH && myLen >= REPLY_MIN_LEN && depth >= 2)
            {
                PROF_BEGIN(rp);
                double rpen = replyPenalty(t, std::min(depth, wantDepth), wantDepth);
                PROF_END(rp, 5);
                if (rpen > 0)
                    score -= rpen;
                if (rpen < 0)
                    eo.rskip = true; // over the reply budget: not evaluated
                if (dbg && replyCombos > 0)
                    std::fprintf(dbg, "  reply %c combos=%d worst=%d pen=%.1f\n", DIRC[d], replyCombos, replyWorst, rpen);
            }
            int threat = threatAt[t];
            // SMALL_SPRINT_THREAT (notes/19): not locally ahead, a ram costs the dragon AND the corpse race
            bool outnum = SMALL_SPRINT_THREAT && myLen < 6 && localAllies <= localEnemies;
            if (threat > 0)
                score -= (myLen >= 6 || (MIDSIZE && (MS_SAFE & 2) && myLen >= 5 && msUnit()) ? 25.0 + 4.0 * myLen : (outnum ? SMALL_THREAT_PEN_OUT : SMALL_THREAT_PEN)) * (units <= LAST_FEW_UNITS ? LAST_FEW_MULT : 1.0);
            else if (outnum && sprintThreatAt[t] > 0)
                score -= SMALL_SPRINT_PEN * (units <= LAST_FEW_UNITS ? LAST_FEW_MULT : 1.0);
            if (QE_KR && qeKrOn() && threat > 0)
                score -= QE_KR_PEN; // TOP4_HORSE QE_KR: on top of the small-unit threat penalty
            if ((THREAT_FREE || KREACH) && !queenSafe() && threat == 0 && threatPaidAt[t] > 0)
                score -= THREAT_PAID_MULT * (myLen >= 6 ? 25.0 + 4.0 * myLen : SMALL_THREAT_PEN) *
                         (units <= LAST_FEW_UNITS ? LAST_FEW_MULT : 1.0);
            if (queenSafe())
            {
                if (threat > 0)
                    score -= QUEEN_THREAT_PEN;
                else if (threatPaidAt[t] > 0)
                    score -= QUEEN_PAID_PEN;
                int ex = 0;
                for (int d2 = 0; d2 < 4; d2++)
                {
                    int v = step(t, d2);
                    if (v >= 0 && v != myHead && freeT[v] <= 2)
                        ex++;
                }
                score += QUEEN_EXIT_W * ex;
                if (QOPEN_PEN > 0)
                {
                    // v43 QOPEN: the queen stays out of kelp corridors (static exits < 3): she can't dodge or turn there
                    int kx = 0;
                    for (int d2 = 0; d2 < 4; d2++)
                        if (step(t, d2) >= 0)
                            kx++;
                    if (kx < 3)
                        score -= QOPEN_PEN * (3 - kx);
                }
                int nd = INF;
                for (auto& o : segs)
                    if (o.head && o.team != w.myTeam)
                        nd = std::min(nd, wrapDist(o.tile, t));
                if (nd <= 4)
                    score -= QUEEN_HEAD_W / std::max(nd, 1);
            }
            if (QSTATE && qstHunt() && qsTheirTile >= 0 && round - qsTheirRound <= QS_SEEN_MEM &&
                wrapDist(myHead, qsTheirTile) <= QS_HUNT_R)
                score -= QS_HUNT_W * wrapDist(t, qsTheirTile); // ours dead, theirs alive: close in on her
            if (eqHuntOn && !EQH_BFS)
                score -= EQH_W * wrapDist(t, eqHuntTile); // v47 EQ_HUNT: small units close in on the enemy queen
            if (queenEarly())
            {
                // early queen: never meet an equal-or-longer head head-on
                for (auto& o : segs)
                    if (o.head && o.team != w.myTeam && wrapDist(o.tile, t) <= 1 && enemyVisibleLength(o.id) >= myLen)
                    {
                        score -= QUEEN_THREAT_PEN;
                        break;
                    }
            }
            if (QEXIT1 && amQueen() && round >= QX_FROM)
                score -= qxPen(t); // v44 QEXIT1
            if (queenSafe() && QUEEN_LOOK)
            {
                int se = queenSafeExits(t);
                if (se < 2)
                    score -= QL_EXIT_PEN * (2 - se); // the worst reply leaves her < 2 safe ways out
            }
            if (queenSafe() && QUEEN_ENCLOSE_PEN > 0)
            {
                int cap = 3 * myLen + 20;
                int open = queenOpen(t, cap);
                if (open < cap)
                    score -= QUEEN_ENCLOSE_PEN * (cap - open) / cap;
            }
            eo.close = queenSafe() && QUEEN_DIST_VETO && queenTooClose(t);
            if (qgAllyHead >= 0 && wrapDist(t, qgAllyHead) <= std::min(kReach(myLen), QG_ALLY_KCAP))
                score -= QG_ALLY_PEN;
            if (qekHead >= 0 && wrapDist(t, qekHead) <= 2)
            {
                int n = qekCount(t);
                if (n < qekN0 && n <= QEK_MIN)
                    score -= QEK_PEN; // v43 QEXIT_KEEP
            }
            if (qhHead >= 0)
            {
                int dq = wrapDist(t, qhHead);
                if (dq <= QAKH_DIST && dq <= qhD0)
                    eo.qb = true; // ends near her without moving away
                else if (dq <= 2)
                {
                    int n = qhCount(t);
                    if (n < qhN0 && n <= QAKH_MIN)
                        eo.qb = true; // takes one of her last exits
                }
            }
            if (egGuard)
            {
                for (auto& o : segs)
                    if (o.head && o.team != w.myTeam)
                    {
                        int Lv = enemyVisibleLength(o.id);
                        if (!enemyTailSeen(o))
                            Lv = std::max(Lv, static_cast<int>(egOrigOn() ? EG_UNSEEN_LEN : QK_EG_UNSEEN_LEN));
                        int K = kReach(Lv), dd = wrapDist(o.tile, t);
                        if (dd <= K)
                            eo.eg = true;
                        if (dd <= K + 1)
                            score -= EG_W * (K + 2 - dd);
                    }
            }
            if (QPLUG_LOOK && amQueen() && round >= QPL_FROM)
            {
                // follow the 1-wide corridor behind t; a foreign body still there on arrival is a plug
                int prev = myHead, cur = t;
                for (int i = 0; i < QPL_DEPTH; i++)
                {
                    int nx = -1, cnt = 0;
                    for (int e = 0; e < 4; e++)
                    {
                        int v = step(cur, e);
                        if (v < 0 || v == prev || v == cur)
                            continue;
                        cnt++, nx = v;
                    }
                    if (cnt != 1)
                        break;
                    if (occId[nx] >= 0 && occId[nx] != w.myId && freeT[nx] > i + 2)
                    {
                        eo.dead = true;
                        if (R2_DEBUG)
                            r2log("qpl", t);
                        break;
                    }
                    prev = cur, cur = nx;
                }
            }
            if (qakHead >= 0)
            {
                bool hit = wrapDist(t, qakHead) <= ((RP.queenKing && queenKingRound()) ? PM_QK_KEEP : QAK_DIST); // ROUND3 P7: wider ring round a crowned queen
                for (int x : qakEsc)
                    hit = hit || x == t;
                if (hit)
                    score -= QAK_PEN; // v38 QALLY_KEEP
            }
            eo.threat = threat;
            eo.depth = depth;
            eo.map = mapScore(t, d);
            score += eo.map;
            if (RP.qPark)
                score += qparkScore(t, d, eo.dead); // ROUND3 P7 PM_QPARK
            if (RP.qSmall)
                score += qsmScore(t); // R10 LANE_QSMALL
#if QUAL_KNOWN
            if (RP.qHomeR > 0)
                score += qhomeScore(t); // QUAL_QHOME
#endif
            if (PM_TD_PULL > 0)
                score += tdPullScore(t); // DGU F4 PM_TD_PULL
            if (KING_CORRIDOR_PENALTY > 0 && myLen >= 10)
            {
                // big dragons stay out of 1-wide corridors: no room to dodge or turn
                int open = 0;
                for (int d2 = 0; d2 < 4; d2++)
                    if (step(t, d2) >= 0)
                        open++;
                if (open <= 2)
                    score -= KING_CORRIDOR_PENALTY;
            }
            if (KING_V2 && RP.kingDeclare && (kingSelf || myLen >= 10))
            {
                int keep = (myLen >= 15 ? 4 : 3) + RP.kingKeepExtra;
                for (auto& o : segs)
                    if (o.head && o.team != w.myTeam)
                    {
                        int dd = wrapDist(o.tile, t);
                        int ke = KREACH_KING ? std::max(keep, freeSteps(enemyVisibleLength(o.id)) + 1) : keep;
                        if (dd <= ke)
                            score -= 12.0 * (ke + 1 - dd) * (1.0 + myLen / 10.0);
                    }
            }
            if (KING_RAM_AVOID > 0 && myLen >= 10)
            {
                // big dragons: stay out of reach of any visible enemy head
                for (auto& o : segs)
                    if (o.head && o.team != w.myTeam)
                    {
                        int dd = wrapDist(o.tile, t);
                        if (dd <= 3)
                            score -= KING_RAM_AVOID * (4 - dd) * (1.0 + myLen / 10.0);
                    }
            }
            // stepping through a portal onto a tile we can't see: someone may be standing there
            if (!visible[t] && t != w.plainStep(myHead, d))
            {
                score -= PORTAL_BLIND_PENALTY + (myLen >= 10 ? RP.kingPortal : 0.0) + (w.known ? 0.0 : UNK_BLIND_PEN);
                if (PORTAL_ECHO_BODY_PEN > 0 && echoBodyDir[d])
                    score -= PORTAL_ECHO_BODY_PEN;
                if (PORTAL_ALLY_COST)
                {
                    // allies we've recently seen near the (invisible) exit make a blind crossing risky
                    int near = 0;
                    for (auto& [tile, rnd] : allyHeadMemory)
                        if (round - rnd <= 5 && wrapDist(tile, t) <= 3)
                            near++;
                    score -= PORTAL_COST_A + PORTAL_COST_B * near;
                    if (round - lastPortalRound <= 4)
                        score -= PORTAL_COST_C; // bouncing straight back through
                }
            }
            // standing on a portal exit: others can arrive on us blind
            if (portalExit[t])
                score -= PORTAL_EXIT_PENALTY + (queenSafe() ? QUEEN_PEXIT_PEN : 0.0);
            if (queenSafe() && !visible[t] && t != w.plainStep(myHead, d))
                score -= QUEEN_BLIND_PEN; // an unseen head may wait on the far side
            score += boxEffect(t);
            if (ALLY_BOX && !amQueen())
                score -= allyBoxPen(t); // R8 ALLY_BOX (DEVTEST1 fix 1B)
            if (PORTAL_LOITER_PEN > 0 && t == w.plainStep(myHead, d) && isMouth(t) && isMouth(myHead))
                score -= PORTAL_LOITER_PEN; // pacing beside portals is what crossers crash into
            const double crowdW = (RP.crowdEarly > 0 && round < RP.kingSeedRound) ? RP.crowdEarly : RP.crowd; // ROUND3 P7 (Maze)
            if (crowdW > 0)
            {
                // spread out: teammate heads close to where we'd go
                int near = 0;
                for (auto& o : segs)
                    if (o.head && o.team == w.myTeam && o.id != w.myId && wrapDist(o.tile, t) <= 2)
                        near++;
                score -= crowdW * near;
            }
            if (feeding && target >= 0)
            {
                int dt = bfsDist[target];
                score -= FEED_PULL * std::min(dt, 80);
            }
            if (consActive)
            {
                bool waiting = consHostVis && !consFirst && wrapDist(myHead, consHostTile) <= CONS_WAIT_R;
                if (waiting)
                {
                    if (wrapDist(t, consHostTile) <= 2)
                        score -= CONS_CLEAR; // keep the host's front clear for the one feeder in line
                }
                else if (consTarget >= 0)
                    score -= CONS_PULL * std::min(bfsDist[consTarget], CONS_PULL_CAP);
            }
            if (pfTarget >= 0 && !pump)
                score -= PF_PULL * std::min(bfsDist[pfTarget], PF_PULL_RANGE + 2);
            if (hotTarget >= 0 && !pump) // stay near fast pockets (presence wins them)
                score -= HOT_PULL * std::min(bfsDist[hotTarget], HOT_PULL_RANGE);
            if (whcOn)
                score -= WHC_PULL * std::min(whcDist[t], 80); // v44 WH_CENTRE
            if (eqHuntOn && EQH_BFS)
            {
                // v47 EQ_HUNT: walking distance (this move's time-aware BFS) to a tile next to her head;
                // unreachable = EQH_CAP, so a kelp-boxed queen pulls nobody
                int bd = INF;
                for (int d2 = 0; d2 < 4; d2++)
                {
                    int v = step(eqHuntTile, d2);
                    if (v >= 0)
                        bd = std::min(bd, v == t ? 0 : bfsDist[v]);
                }
                if (eqHuntTile == t)
                    bd = 0;
                if (lhActive)
                {
                    // v68 LATE_HUNT: map-wide; past the BFS horizon (or blocked) fall back to the straight distance
                    if (bd >= INF)
                        bd = wrapDist(t, eqHuntTile) + 4;
                    score -= LH_W * ((LH_LONG && myLen < LHL_SMALL) ? LHL_SMALL_MULT : 1.0) * std::min(bd, static_cast<int>(LH_CAP));
                }
                else
                score -= EQH_W * std::min(bd, static_cast<int>(EQH_CAP));
                if (EQH_DEBUG)
                    logPending += "LOG eqhBD r" + std::to_string(round) + " id" + std::to_string(w.myId) + " d" +
                                  std::to_string(d) + " bd" + std::to_string(bd) + " man" + std::to_string(wrapDist(t, eqHuntTile)) + "\n";
            }
            if (d == myDir)
                score += 0.3;
            if (SPAWN_BLOCK_PEN > 0 && w.spawnAt[t] >= round && w.spawnAt[t] - round <= myLen &&
                !(visible[t] && w.pearlMem[t]))
                score -= SPAWN_BLOCK_PEN; // our body would sit on it when it spawns: the pearl is lost (IMP_FINDINGS)
            if (REVISIT_PEN > 0 && !headSeen.empty() && headSeen[t] >= 0 && round - headSeen[t] <= REVISIT_WIN &&
                !(visible[t] && w.pearlMem[t]))
                score -= REVISIT_PEN; // coiling over our own recent path finds no new food (IMP_FINDINGS)
            score += rng.uni() * 0.2;
            if (dbg)
                std::fprintf(dbg, "  cand %c t=(%d,%d) pearls=%.2f area=%d depth=%d threat=%d freeT=%d score=%.2f\n", DIRC[d],
                             t % w.W, t / w.W, pearls, area, depth, threat, freeT[t], score);
            eo.score = score;
            return true;
        };
        for (int d = 0; d < 4; d++)
        {
            EvalOut eo;
            if (!evalDir(d, eo))
                continue;
            candDead[d] = eo.dead;
            candQb[d] = eo.qb;
            candEg[d] = eo.eg;
            candClose[d] = eo.close;
            candThreat[d] = eo.threat;
            candDepth[d] = eo.depth;
            candMap[d] = eo.map;
            candScore[d] = eo.score;
            if (eo.score > best)
            {
                best = eo.score;
                bestD = d;
                bestDepth = eo.depth;
            }
        }

        if (UNK_EXPLORE && exploreDesire && unkEchoRound == round && unkEchoTile == myHead && unkEchoClean && !qNoUnkPortal())
        {
            int hunger = round - lastGrowRound;
            int exD = -1;
            for (int d = 0; d < 4; d++)
            {
                if (!((unkEchoMask >> d) & 1) || step(myHead, d) >= 0 || !w.portalSide[myHead * 4 + d])
                    continue;
                if (static_cast<int>(edgeCrossRound.size()) == w.N * 4 &&
                    round - edgeCrossRound[myHead * 4 + d] < UNK_EXPLORE_COOLDOWN)
                    continue;
                if (threatAt[myHead] > 0 && myLen >= 6)
                    continue;
                double sc = UNK_EXPLORE_SCORE + 0.3 * std::min(hunger, 60);
                if (sc > best)
                    best = sc, bestD = d, bestDepth = SURVIVE_DEPTH, exD = d;
            }
            if (exD >= 0)
            {
                if (static_cast<int>(edgeCrossRound.size()) != w.N * 4)
                    edgeCrossRound.assign(w.N * 4, -1000);
                exploreFrom = myHead, exploreDir = exD, exploreRound = round;
                lastExploreCross = round;
                edgeCrossRound[myHead * 4 + exD] = round;
                lastPortalRound = round;
                if (dbg)
                    std::fprintf(dbg, "  -> explore unknown portal %c\n", DIRC[exD]);
            }
        }
        if (queenSafe() && bestD >= 0 && candThreat[bestD] > 0)
        {
            // hard veto: never step into reach when an unthreatened step that doesn't trap her exists
            int alt = -1;
            for (int d = 0; d < 4; d++)
                if (candScore[d] > -1e17 && candThreat[d] == 0 && candDepth[d] >= QUEEN_VETO_DEPTH &&
                    (alt < 0 || candScore[d] > candScore[alt]))
                    alt = d;
            if (alt >= 0)
            {
                if (dbg)
                    std::fprintf(dbg, "  queen veto %c -> %c\n", DIRC[bestD], DIRC[alt]);
                bestD = alt, best = candScore[alt], bestDepth = candDepth[alt];
            }
        }
        if (queenSafe() && QUEEN_DIST_VETO && bestD >= 0 && candClose[bestD])
        {
            // no enemy head within F+1 of her at the end of the turn, unless every step is that close
            int alt = -1;
            for (int d = 0; d < 4; d++)
                if (candScore[d] > -1e17 && !candClose[d] && candThreat[d] == 0 && candDepth[d] >= QUEEN_VETO_DEPTH &&
                    (alt < 0 || candScore[d] > candScore[alt]))
                    alt = d;
            if (alt >= 0)
                bestD = alt, best = candScore[alt], bestDepth = candDepth[alt];
        }
        if (egGuard && bestD >= 0 && candEg[bestD])
        {
            // ROUND2 P6: late, the queen / king leaves every visible enemy head's kamikaze reach when it can
            int alt = -1;
            for (int d = 0; d < 4; d++)
                if (candScore[d] > -1e17 && !candEg[d] && !candDead[d] && candThreat[d] == 0 && candDepth[d] >= QUEEN_VETO_DEPTH &&
                    (alt < 0 || candScore[d] > candScore[alt]))
                    alt = d;
            r2log(alt >= 0 ? "egveto" : "eg0", alt);
            if (alt >= 0)
                bestD = alt, best = candScore[alt], bestDepth = candDepth[alt];
        }
        else if (R2_DEBUG && egGuard)
            r2log("egfree");
        if (R2_DEBUG && qhHead >= 0)
            r2log("qakhsee", qhD0);
        if (QAK_HARD && bestD >= 0 && candQb[bestD])
        {
            // ROUND2 P3: a long ally stays off our queen when an unthreatened, open, surviving step exists
            int alt = -1;
            for (int d = 0; d < 4; d++)
                if (candScore[d] > -1e17 && !candQb[d] && !candDead[d] && candThreat[d] == 0 && candDepth[d] >= QUEEN_VETO_DEPTH &&
                    (alt < 0 || candScore[d] > candScore[alt]))
                    alt = d;
            if (alt >= 0)
            {
                r2log("qakh", alt);
                bestD = alt, best = candScore[alt], bestDepth = candDepth[alt];
            }
            else if (R2_DEBUG)
            {
                int legal = 0, nonqb = 0, ok = 0;
                for (int d = 0; d < 4; d++)
                    if (candScore[d] > -1e17)
                    {
                        legal++;
                        if (!candQb[d])
                            nonqb++, ok += (candThreat[d] == 0) + 10 * (candDepth[d] >= QUEEN_VETO_DEPTH);
                    }
                r2log("qakh0", legal * 1000 + nonqb * 100 + ok);
            }
        }
        if ((qGuard() || QNOPOCKET || QPLUG_LOOK || qparkQueen()) && bestD >= 0 && candDead[bestD])
        {
            // v37e QGUARD (from v37b): no dead end for the queen when an open step that survives exists
            int alt = -1;
            for (int d = 0; d < 4; d++)
                if (candScore[d] > -1e17 && !candDead[d] && candDepth[d] >= QUEEN_VETO_DEPTH &&
                    !(queenSafe() && candThreat[d] > 0) && // never undo the QUEEN_SAFE threat veto
                    (alt < 0 || candScore[d] > candScore[alt]))
                    alt = d;
            if (R2_DEBUG && alt < 0)
                r2log("qdead0");
            if (alt >= 0)
            {
                if (QPLUG_LOOK)
                    r2log("qplveto", alt);
                if (dbg)
                    std::fprintf(dbg, "  qguard dead-end veto %c -> %c\n", DIRC[bestD], DIRC[alt]);
                bestD = alt, best = candScore[alt], bestDepth = candDepth[alt];
            }
        }
        if (KING_ESCAPE && tryKingEscape(bestD))
            return;
        if (ECHO_EXIT_HOLD)
        {
            double otherBest = -1e18;
            for (int d = 0; d < 4; d++)
                if (d != bestD)
                    otherBest = std::max(otherBest, candScore[d]);
            if (tryEchoHold(bestD, otherBest))
                return;
            holdStreak = 0;
        }

        // ---- trapped: reverse-split so the bulk of the body escapes backwards
        bool trapped = bestD < 0 || (bestDepth < 4 && best < -100);
        if ((TIP_REV & 1) && !trapped && !amQueen() && myLen >= TR_MINLEN && bestDepth < TR_DEPTH && best < -100)
            trapped = true, r2log("trv", bestDepth); // R8 TIP_REV bit 1: the bulk leaves by the tail before the pocket closes
        // TRAP_SPLIT_BLIND: when every move is lethal, split even if the tail is out of view
        // (a young child's tail often is): losing both halves is no worse than dying whole.
        // QBOX (v38q): a queen with no legal move splits even when the tail has no exit (sealed Schooltime box)
        bool qboxSplit = QBOX && amQueen() && bestD < 0 && myLen >= 4 && units < w.unitLimit;
        if (qboxSplit ||
            (trapped && myLen >= 4 && !(queenSafe() && threatAt[myHead] > 0) && !(qGuard() && bestD >= 0) && units < w.unitLimit &&
             (tailHasExit(myLen - 2) || (TRAP_SPLIT_BLIND && bestD < 0 && static_cast<int>(trail.size()) < myLen))))
        {
            int trapK = myLen - 2;
            if (QBOX_K2 && amQueen() && bestD < 0 && myLen >= 5)
                trapK = 2; // v43 QBOX_K2: a boxed queen sheds 2 and waits (she can wait again while L >= 4)
            if (QBOX_ONESPLIT && amQueen() && bestD < 0 && round >= QB1_FROM && static_cast<int>(trail.size()) >= myLen)
            {
                // notes/top5/FTM_OCT5.md: a boxed queen whose head touches her own segment i keeps exactly i segments
                // in one split. The child's tail is then that tile and frees when the child moves, so she has a step
                // next turn about 10-18 rounds sooner, and the rest of her mass stays one ally (the K2 chain sheds it as ~17 L2s).
                // only when every open side is her own body (kelp and her own segments never move away; another
                // dragon's body may, and then the K2 wait keeps more of her)
                int keep = -1;
                bool ownOnly = true;
                for (int d = 0; d < 4 && ownOnly; d++)
                {
                    int t = step(myHead, d);
                    if (t < 0)
                        continue;
                    int idx = -1;
                    for (int i = 1; i < myLen && idx < 0; i++)
                        if (trail[i] == t)
                            idx = i;
                    if (idx < 0)
                        ownOnly = false;
                    else if (idx >= 2 && idx <= myLen - 2)
                        keep = std::max(keep, idx);
                }
                if (!ownOnly)
                    keep = -1;
                if (keep >= 2 && myLen - 2 * (499 - round) > keep)
                    keep = -1; // near r500 the K2 chain is still longer than keep when the game ends (queen tiebreak)
                if (keep >= 2)
                {
                    trapK = myLen - keep;
                    r2log("qb1", keep);
                    if (dbg)
                        std::fprintf(dbg, "  qbox one split: keep %d of %d\n", keep, myLen);
                }
            }
            r2log(bestD < 0 ? (amQueen() ? "spEq" : "spE0") : "spE1", trapK);
            out += "SPLIT " + std::to_string(trapK) + "\n";
            pending.clear();
            pendingSplit = true;
            if (trapK == myLen - 2)
                kingSelf = false; // the body (and the crown) moves to the child
            if (dbg)
                std::fprintf(dbg, "  -> reverse split\n");
            return;
        }

        if (bestD < 0)
        {
            // everything is lethal: take an enemy head with us if we can,
            // otherwise die alone; never hit an ally head (that kills both)
            int bestRank = -1;
            for (int d = 0; d < 4; d++)
            {
                int t = step(myHead, d);
                int rank;
                // ranks: ally head 0 < kelp 1 < body 2 < unknown portal 3 < enemy head 4
                if (t < 0 && UNK_PORTAL_ESCAPE && !w.known && !w.portalSide.empty() && w.portalSide[myHead * 4 + d])
                    rank = (UNK_NECK_ESCAPE_GUARD && d == (myDir + 2) % 4) ? 2 : 3; // not back into our neck (Codex)
                else if (t < 0)
                    rank = 1;
                else if (occHead[t] && occId[t] != w.myId)
                    rank = occTeam[t] == w.myTeam ? 0 : 4;
                else
                    rank = 2;
                if (rank > bestRank)
                {
                    bestRank = rank;
                    bestD = d;
                }
            }
        }
        if (FREE_STEPS && myLen >= 5 && !pfIn && holdTile < 0 &&
            tryFreePath(evalDir, bestD, candScore, candMap, candThreat, candDepth, candClose, candDead))
            return;
        emitMove(bestD);
        if (dbg)
            std::fprintf(dbg, "  -> %c\n", DIRC[bestD]);
#if DEBUG_INDICATOR
        out += "INDICATOR " + std::string(w.known ? w.known->name : "?") + " s=" + std::to_string(static_cast<int>(best)) + "\n";
#endif
    }

    void run()
    {
        std::setvbuf(stdout, nullptr, _IOFBF, 1 << 16);
        setup();
        if (const char* dd = std::getenv("BOTDBG"))
        {
            std::string path = std::string(dd) + "/" + std::to_string(w.myId) + ".txt";
            dbg = std::fopen(path.c_str(), "w");
        }
        while (true)
        {
            PROF_BEGIN(parse);
            if (!readTurn(in))
                break;
            PROF_END(parse, 0);
            turnT0 = pointsM();
            out.clear();
            try
            {
                PROF_BEGIN(an);
                analyse();
                PROF_END(an, 1);
                if (dbg)
                {
                    std::fprintf(dbg, "R%d id=%d len=%d dir=%c head=(%d,%d) map=%s\n", round, w.myId, myLen, DIRC[myDir],
                                 myHead % w.W, myHead / w.W, w.known ? w.known->name : "?");
                    if (EXPLORE_LEARN && !w.known)
                        std::fprintf(dbg, "  explore est=%.4f n=%.1f\n", exploreEst(), exploreN);
                    for (auto& sg : segs)
                        std::fprintf(dbg, "  seg %c%d (%d,%d) %c%s freeT=%d\n", sg.team, sg.id, sg.tile % w.W, sg.tile / w.W,
                                     DIRC[sg.facing], sg.head ? " H" : "", freeT[sg.tile]);
                }
                PROF_BEGIN(de);
                decide();
                PROF_END(de, 6);
            }
            catch (...)
            {
                out = "MOVE ";
                out += DIRC[in.dir];
                out += '\n';
            }
            try
            {
                PROF_BEGIN(so);
                if (myHead >= 0)
                    emitSonar();
                PROF_END(so, 7);
            }
            catch (...)
            {
            }
#if PROFILE_POINTS
            {
                char pb[200];
                std::snprintf(pb, sizeof pb, "LOG prof L=%d N=%d parse=%.2f an=%.2f thr=%.2f bfs=%.2f surv=%.2f reply=%.2f dec=%.2f son=%.2f\n",
                              myLen, w.N, profAcc[0], profAcc[1], profAcc[2], profAcc[3], profAcc[4], profAcc[5], profAcc[6], profAcc[7]);
                out += pb;
                for (double& x : profAcc)
                    x = 0;
            }
#endif
            out += "PROTOCOL 3\nENDTURN\n";
            std::fwrite(out.data(), 1, out.size(), stdout);
            std::fflush(stdout);
            if (dbg)
                std::fflush(dbg);
        }
    }
};

} // namespace

int main()
{
    static Bot bot;
    bot.run();
    return 0;
}
