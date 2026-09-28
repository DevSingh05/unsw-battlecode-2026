// UNSW Battlecode 2026 bot.
// Every dragon runs its own copy of this program. Each turn we read our 7x7
// view, update what we remember about the map, then pick a move by scoring
// each safe direction: pearls we can reach (time-aware BFS that knows when
// body segments will have moved away), room to manoeuvre, and enemy heads
// that could ram us.

#include "maps_data.hpp"
#include "params.hpp"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <functional>
#include <iostream>
#include <string>
#include <vector>
#include <cstdlib>

namespace {
FILE* dbg = nullptr;

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
};
RuntimeParams RP;

// Per-map overrides, keyed by the recognised map's name. Each value is a macro
// so local tests can flip one map at a time (e.g. -DPM_DEVIL_RG=0).
void applyMapParams(const char* name)
{
    RP = RuntimeParams{};
    std::string n(name ? name : "");
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
    if (KING_V2)
    {
        // notes/11: top-10 king timing on the big maps
        //                 map               seed  splitStop feed  reserve
        auto v2 = [&](const char* map, int ks, int ss, int fs, int res) {
            if (n == map)
            {
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
    if (n == "Prisoners Dilemma" && PM_DIL_KEEP >= 0)
        RP.keepLen = PM_DIL_KEEP;
    if (n == "Trauma" && PM_TRA_LATEFEED >= 0)
        RP.lateFeedRound = PM_TRA_LATEFEED;
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
            if (!NO_KNOWN_MAPS && KNOWN_MAPS[i].w == w && KNOWN_MAPS[i].h == h)
                candidates.push_back(i);
    }

    void adopt(const KnownMap* m)
    {
        known = m;
        applyMapParams(m->name);
        sym = m->sym;
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
    void notePortal(int t, int d, int pid)
    {
        int e = canonEdge(t, d);
        for (auto& [id, edges] : portalSeen)
            if (id == pid)
            {
                if (std::find(edges.begin(), edges.end(), e) == edges.end())
                    edges.push_back(e);
                if (edges.size() == 2)
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

    // Tile t, side d has edge kind k. Check it against a known map.
    static bool consistent(const KnownMap& m, int W, int t, int d, int k)
    {
        int v = m.nxt[t * 4 + d];
        int x = t % W, y = t / W;
        int H = m.h;
        int plain = ((y + DY[d] + H) % H) * W + ((x + DX[d] + W) % W);
        if (k == 1)
            return v == -1;
        if (k == 0)
            return v == plain;
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
        }
        if (!known)
        {
            for (auto& [td, k] : obs)
            {
                int t = td / 4, d = td % 4;
                if (k == 0)
                    nxt[td] = plainStep(t, d);
                else if (k == 1 || !LEARN_PORTALS || !portalKnown(t, d))
                    nxt[td] = -1; // kelp, or a portal whose far side we don't know yet
            }
            if (LEARN_PORTALS)
                for (auto& [td, pid] : portalObs)
                    notePortal(td / 4, td % 4, pid);
            if (portalSide.size() != nxt.size())
                portalSide.assign(nxt.size(), 0);
            for (auto& [td, pid] : portalObs)
                portalSide[td] = 1;
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
    bool unkParamsSet = false; // generic settings chosen for an unseen map
    std::vector<std::pair<int, int>> allyHeadMemory; // (tile, round) of ally heads seen lately
    int lastPortalRound = -100;                       // last round we stepped through a portal
    std::vector<int> trail;    // our body, head first (tracked across turns)
    std::vector<int> freeOther; // like freeT but ignoring our own body
    std::vector<int> bodyCnt;   // survival search: our simulated body
    std::vector<int> simBody;   // ring buffer
    std::vector<char> eatenMark; // survival search: pearls eaten on this path
    long long nodes = 0;
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
    }

    void analyse()
    {
        round = in.round;
        myLen = in.length;
        units = in.units;
        myDir = in.dir;

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

        if (round == 0 || (w.known == nullptr && !w.candidates.empty() && w.lastSeen[myHead] < 0))
            w.identifyByStart(hx, hy);
        w.observeEdges(in, hx, hy);
        if (FRAME_FIX && w.swapState < 0 && w.known)
            guessFrame();

        filterByCountdowns();
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
        for (int i = 0; i < 49; i++)
        {
            int t = w.idx(in.tx[i], in.ty[i]);
            visible[t] = 1;
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
        computePortalExits();
        computeFreeTimes();
        updateTrail();
        computeOtherDist();
        readMessages();
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
                if (r > 0)
                {
                    int since = arrive - std::max(ls, w.spawnAt[t] >= 0 ? w.spawnAt[t] : 0);
                    if (ls < 0 && w.spawnAt[t] < 0)
                        since = arrive; // initial countdowns start somewhere in [min,max]
                    v = 0.5 * std::min(1.0, std::max(0, since) * r);
                }
            }
        }
        if (v <= 0)
            return 0;
        // someone else closer: they will probably take it
        int od = otherDist[t];
        if (od < s)
            v *= 0.25;
        else if (od == s)
            v *= 0.55;
        return v;
    }

    // Time-aware BFS from a tile we enter on step 1. Returns pearl score and
    // number of reachable tiles (capped).
    std::vector<int> bfsDist, bfsQ;
    void bfsFrom(int start, double& pearlScore, int& area, int areaCap)
    {
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
            if (!VORONOI_AREA || du < otherDist[u])
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
        auto escapes = [&]() {
            return ESCAPE_SPLIT && L0 <= 3 && L >= 4 && units < w.unitLimit && (!RP.escapeHotOnly || hotEaten > 0);
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
            if (depth >= maxDepth || f.dir >= 4 || nodes > 60000)
            {
                if (depth >= maxDepth || nodes > 60000)
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

    void emitMove(int d)
    {
        out += "MOVE ";
        out += DIRC[d];
        out += '\n';
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

    uint64_t encodeKing(int tile, int len, int id, int hop, int dir, int rnd) const
    {
        uint64_t x = static_cast<uint64_t>(tile % w.W) | (static_cast<uint64_t>(tile / w.W) << 6) |
                     (static_cast<uint64_t>(std::min(len, 255)) << 12) | (static_cast<uint64_t>(id & 1023) << 20) |
                     (static_cast<uint64_t>(hop & 3) << 30) | (static_cast<uint64_t>(dir & 3) << 32) |
                     (static_cast<uint64_t>(rnd & 511) << 34);
        uint64_t check =
            mix(x ^ SECRET ^ (static_cast<uint64_t>(w.myTeam) << 50) ^ frameSalt(myFrameCode())) & ((1ULL << 21) - 1);
        return x | (check << 43);
    }

    bool decodeKing(uint64_t m, int& tile, int& len, int& id, int& hop, int& dir, int& rnd)
    {
        uint64_t x = m & ((1ULL << 43) - 1);
        bool ok = false;
        for (int fr = 0; fr < (FRAME_FIX ? 3 : 1) && !ok; fr++)
        {
            uint64_t check = mix(x ^ SECRET ^ (static_cast<uint64_t>(w.myTeam) << 50) ^ frameSalt(fr)) & ((1ULL << 21) - 1);
            if ((m >> 43) == check)
                ok = true, lastFrameCode = fr;
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

    void readMessages()
    {
        for (uint64_t m : in.msgs)
        {
            int tile, rnd;
            if (!PORTAL_WARN || !decodeWarn(m, tile, rnd))
                continue;
            if (PORTAL_WARN_MEMO && lastWarnLen > 0 && rnd + lastWarnLen > round)
                warnMem.push_back({tile, rnd + lastWarnLen});
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
        haveRelay = false;
        int bestHopRelay = 99;
        for (uint64_t m : in.msgs)
        {
            int tile, len, id, hop, dir, rnd;
            if (!decodeKing(m, tile, len, id, hop, dir, rnd))
                continue;
            learnFrame(lastFrameCode);
            if (round - rnd > 4)
                continue;
            if (id == (w.myId & 1023))
                continue;
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
            bool better = len > kingLen || id == (kingId & 1023) || round - kingRound > 6;
            if (better && (rnd >= kingRound || len > kingLen))
            {
                kingId = id;
                kingLen = len;
                kingTile = tile;
                kingDir = dir;
                kingRound = rnd;
            }
            if (hop < KING_RELAY_HOPS && hop < bestHopRelay && id == (kingId & 1023))
            {
                bestHopRelay = hop;
                relayMsg = encodeKing(tile, len, id, hop + 1, dir, rnd);
                haveRelay = true;
            }
        }
        // we can see the king ourselves: use exact data
        if (kingId >= 0)
            for (auto& sg : segs)
                if (sg.head && sg.team == w.myTeam && (sg.id & 1023) == (kingId & 1023) && sg.id != w.myId)
                {
                    kingTile = sg.tile;
                    kingDir = sg.facing;
                    kingRound = round;
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
    void updateKingship()
    {
        if (!RP.kingDeclare)
            return;
        if (KING_V2)
        {
            // up to two candidates grow side by side; the longest is the king
            if (kingSelf)
            {
                if (freshKings(myLen + 2) >= 2)
                    kingSelf = false;
                return;
            }
            if (round >= RP.kingSeedRound && freshKings(-1) < 2 && myLen >= 3 && rng.uni() < KING_DECLARE_P)
                kingSelf = true;
            return;
        }
        bool heard = kingId >= 0 && round - kingRound <= 8;
        if (kingSelf)
        {
            if (heard && (kingLen > myLen + KING_STEPDOWN_MARGIN || (kingLen >= myLen && (kingId & 1023) < (w.myId & 1023))))
                kingSelf = false;
            return;
        }
        if (round >= RP.kingSeedRound && !heard && myLen >= RP.kingDeclareMinLen && rng.uni() < KING_DECLARE_P)
            kingSelf = true;
    }
    bool iAmKing() const
    {
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
        uint64_t warn = 0;
        bool anyWarn = warnDirs[0] || warnDirs[1] || warnDirs[2] || warnDirs[3];
        if (anyWarn)
            warn = encodeWarn(pending.empty() ? myHead : pending.back(), round);
        if (iAmKing() && (round >= KING_BROADCAST_START || kingSelf))
        {
            uint64_t m = encodeKing(myHead, myLen, w.myId, 0, myDir, round);
            for (int d = 0; d < 4; d++)
                if (!warnDirs[d])
                    out += std::string("SONAR ") + DIRC[d] + " " + std::to_string(m) + "\n";
        }
        else if (haveRelay)
        {
            for (int d = 0; d < 4; d++)
                if (!warnDirs[d])
                    out += std::string("SONAR ") + DIRC[d] + " " + std::to_string(relayMsg) + "\n";
        }
        for (int d = 0; d < 4; d++)
            if (warnDirs[d])
                out += std::string("SONAR ") + DIRC[d] + " " + std::to_string(warn) + "\n";
        warnDirs[0] = warnDirs[1] = warnDirs[2] = warnDirs[3] = false;
    }
    bool warnDirs[4] = {false, false, false, false};

    // Tile a feeder should die on: a couple of steps in front of the king.
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

    bool shouldFeed() const
    {
        if (KING_V2 && RP.kingDeclare)
            return FEED_ENABLE && feedPhase() && kingId >= 0 && kingLen >= myLen + 2 && !iAmKing() &&
                   units > RP.feedReserve &&
                   myLen <= (round >= KING_V2_MERGE_ROUND ? 1000 : round >= 380 ? 6 : KING_V2_FEED_LEN);
        return FEED_ENABLE && feedPhase() && kingId >= 0 && kingLen >= myLen + 2 && !iAmKing() &&
               (units > RP.feedReserve || (RP.lateFeedRound > 0 && round >= RP.lateFeedRound && units > 1)) && myLen <= FEED_MAX_LEN;
    }

    // BFS distance from each enemy head over tiles free now, up to 6 steps.
    // threatAt[t] = how many enemy heads can reach t before our next turn,
    // given their visible length limits how far they can sprint.
    std::vector<int> threatAt, threatDist, tq;
    void computeThreats()
    {
        threatAt.assign(w.N, 0);
        if (static_cast<int>(threatDist.size()) != w.N)
            threatDist.assign(w.N, INF);
        for (auto& s : segs)
        {
            if (!s.head || s.team == w.myTeam)
                continue;
            int maxReach = myLen >= KING_MIN_LEN ? KING_THREAT_REACH : MAX_THREAT_REACH;
            int reach = std::min(std::max(1, enemyVisibleLength(s.id) - 1), maxReach);
            tq.clear();
            tq.push_back(s.tile);
            threatDist[s.tile] = 0;
            for (size_t qi = 0; qi < tq.size(); qi++)
            {
                int u = tq[qi];
                if (threatDist[u] >= reach)
                    continue;
                for (int d = 0; d < 4; d++)
                {
                    int v = step(u, d);
                    if (v < 0 || threatDist[v] != INF)
                        continue;
                    threatDist[v] = threatDist[u] + 1;
                    tq.push_back(v);
                    threatAt[v]++;
                    // a head can't pass through bodies (it would die), except ours at the end
                    if (freeT[v] > 1)
                        threatDist[v] = reach; // stop expanding here
                }
            }
            for (int u : tq)
                threatDist[u] = INF;
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
    bool pocketWorthPumping(int t)
    {
        auto why = [&](const char* r) { if (dbg) std::fprintf(dbg, "POCKET %s len=%d\n", r, myLen); return false; };
        if (myLen < 2 || myLen > 3 || units >= w.unitLimit || iAmKing())
            return why("len/units/king");
        for (auto& o : segs)
            if (o.head && o.team != w.myTeam && wrapDist(o.tile, t) <= 3)
                return why("enemy");
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
        if (dbg)
            std::fprintf(dbg, "POCKET YES len=%d pearls=%.1f\n", myLen, pearls);
        return true;
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
                int net = eaten - (steps - 1);
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
                int tailFreed = (steps - eaten) + std::max(0, steps - 1);
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

    // Try a head-on ram at distance 1 or 2. Returns true if we emitted it.
    bool tryRam()
    {
        if (!ENABLE_RAM || units < 2 || (feedPhase() && iAmKing()))
            return false;
        double bestVal = 0;
        std::string bestCmd;
        for (auto& s : segs)
        {
            if (!s.head || s.team == w.myTeam)
                continue;
            int theirs = enemyVisibleLength(s.id);
            // worth it if they're at least as valuable as us, and we aren't the king
            bool worth = theirs >= myLen || (myLen <= RAM_MAX_OWN_LEN);
            if (RP.ramGuard && theirs < myLen + 2)
            {
                // an even trade only helps when we have the numbers
                int allyHeads = 1, enemyHeads = 0;
                for (auto& o : segs)
                    if (o.head && o.id != w.myId)
                        (o.team == w.myTeam ? allyHeads : enemyHeads)++;
                if (units < RAM_MIN_UNITS || allyHeads < enemyHeads + 1)
                    worth = false;
            }
            if (!worth)
                continue;
            double val = 40.0 + 3.0 * theirs - 2.0 * myLen;
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

    void decide()
    {
        out.clear();
        if (myHead < 0)
        {
            emitMove(myDir);
            return;
        }
        computeThreats();
        if (mapOverride())
            return;

        // ---- rams (distance 1-2)
        if (tryRam())
            return;

        // ---- feeding the king: die just in front of it so it eats our body
        bool feeding = shouldFeed();
        int target = feeding ? feedTarget() : -1;
        if (feeding && target >= 0)
        {
            bool kingVisible = false;
            for (auto& sg : segs)
                if (sg.head && sg.id != w.myId && (sg.id & 1023) == (kingId & 1023) && sg.team == w.myTeam)
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
            if (myLen >= RP.keepLen + 4 && units < w.unitLimit && round < RP.splitStopRound && !threatened)
            {
                out += "SPLIT 2\n";
                pending.clear();
                pendingSplit = true;
                return;
            }
        }
        if (!(RP.kingDeclare && kingSelf) && !bigLate && (!SPLIT_NEEDS_EXIT || tailHasExit(2)) && myLen >= SPLIT_LEN && myLen >= 4 && units < w.unitLimit && units < SPLIT_MAX_UNITS &&
            round < RP.splitStopRound && !threatened)
        {
            int k = SPLIT_CHILD > 0 ? std::min(SPLIT_CHILD, myLen - 2) : myLen / 2;
            out += "SPLIT " + std::to_string(k) + "\n";
            pending.clear();
            pendingSplit = true;
            return;
        }

        // ---- score each direction
        double best = -1e18;
        int bestD = -1;
        int bestDepth = 0;
        int areaCap = 3 * myLen + 30;
        for (int d = 0; d < 4; d++)
        {
            int t = step(myHead, d);
            if (t < 0)
                continue; // kelp
            if (occId[t] >= 0 && freeT[t] > 1)
                continue; // occupied (rams handled above)
            double score = 0;
            double pearls;
            int area;
            bfsFrom(t, pearls, area, areaCap);
            score += 10.0 * pearls;
            int need = myLen + 3;
            bool pump = POCKET_PUMP && area < need && pocketWorthPumping(t);
            if (area < need && !pump)
                score -= AREA_WEIGHT * (need - area) / need + 20;
            int wantDepth = myLen >= 10 ? std::max(SURVIVE_DEPTH, std::min(myLen, KING_SURVIVE_DEPTH)) : SURVIVE_DEPTH;
            int depth = surviveDepth(t, wantDepth);
            if (depth < wantDepth && !pump)
                score -= 150.0 + 40.0 * (wantDepth - depth);
            if (pump)
                score += POCKET_PUMP_BONUS;
            int threat = threatAt[t];
            if (threat > 0)
                score -= (myLen >= 6 ? 25.0 + 4.0 * myLen : SMALL_THREAT_PEN) * (units <= LAST_FEW_UNITS ? LAST_FEW_MULT : 1.0);
            score += mapScore(t, d);
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
                        if (dd <= keep)
                            score -= 12.0 * (keep + 1 - dd) * (1.0 + myLen / 10.0);
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
                score -= PORTAL_EXIT_PENALTY;
            score += boxEffect(t);
            if (RP.crowd > 0)
            {
                // spread out: teammate heads close to where we'd go
                int near = 0;
                for (auto& o : segs)
                    if (o.head && o.team == w.myTeam && o.id != w.myId && wrapDist(o.tile, t) <= 2)
                        near++;
                score -= RP.crowd * near;
            }
            if (feeding && target >= 0)
            {
                int dt = bfsDist[target];
                score -= FEED_PULL * std::min(dt, 80);
            }
            if (d == myDir)
                score += 0.3;
            score += rng.uni() * 0.2;
            if (dbg)
                std::fprintf(dbg, "  cand %c t=(%d,%d) pearls=%.2f area=%d depth=%d threat=%d freeT=%d score=%.2f\n", DIRC[d],
                             t % w.W, t / w.W, pearls, area, depth, threat, freeT[t], score);
            if (score > best)
            {
                best = score;
                bestD = d;
                bestDepth = depth;
            }
        }

        // ---- trapped: reverse-split so the bulk of the body escapes backwards
        bool trapped = bestD < 0 || (bestDepth < 4 && best < -100);
        if (trapped && myLen >= 4 && units < w.unitLimit && tailHasExit(myLen - 2))
        {
            out += "SPLIT " + std::to_string(myLen - 2) + "\n";
            pending.clear();
            pendingSplit = true;
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
                    rank = 3; // an unknown portal is a gamble; certain death isn't
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
        while (readTurn(in))
        {
            out.clear();
            try
            {
                analyse();
                if (dbg)
                {
                    std::fprintf(dbg, "R%d id=%d len=%d dir=%c head=(%d,%d) map=%s\n", round, w.myId, myLen, DIRC[myDir],
                                 myHead % w.W, myHead / w.W, w.known ? w.known->name : "?");
                    for (auto& sg : segs)
                        std::fprintf(dbg, "  seg %c%d (%d,%d) %c%s freeT=%d\n", sg.team, sg.id, sg.tile % w.W, sg.tile / w.W,
                                     DIRC[sg.facing], sg.head ? " H" : "", freeT[sg.tile]);
                }
                decide();
            }
            catch (...)
            {
                out = "MOVE ";
                out += DIRC[in.dir];
                out += '\n';
            }
            try
            {
                if (myHead >= 0)
                    emitSonar();
            }
            catch (...)
            {
            }
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
