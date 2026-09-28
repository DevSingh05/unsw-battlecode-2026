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
#include <iostream>
#include <string>
#include <vector>
#include <cstdlib>

namespace {
FILE* dbg = nullptr;

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
            if (KNOWN_MAPS[i].w == w && KNOWN_MAPS[i].h == h)
                candidates.push_back(i);
    }

    void adopt(const KnownMap* m)
    {
        known = m;
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
        for (int row = 0; row <= VS; row++)
            for (int col = 0; col < VS; col++)
            {
                int k = edgeKind(in.hEdges[row][col]);
                if (row < VS)
                    obs.push_back({tileAt(col, row) * 4 + 0, k});
                if (row > 0)
                    obs.push_back({tileAt(col, row - 1) * 4 + 2, k});
            }
        for (int row = 0; row < VS; row++)
            for (int col = 0; col <= VS; col++)
            {
                int k = edgeKind(in.vEdges[row][col]);
                if (col < VS)
                    obs.push_back({tileAt(col, row) * 4 + 3, k});
                if (col > 0)
                    obs.push_back({tileAt(col - 1, row) * 4 + 1, k});
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
                else
                    nxt[td] = -1; // kelp, or a portal whose far side we don't know
            }
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
            if (team == myTeam && d[2] == headX && d[3] == headY)
            {
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
            return 0.01; // unknown map: guess
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
    std::vector<int> trail;    // our body, head first (tracked across turns)
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
                w.spawnAt[t] = round + in.tin[i];
                int m = w.mirror(t);
                if (m >= 0 && m != t)
                    w.spawnAt[m] = round + in.tin[i];
            }
        }

        computeFreeTimes();
        updateTrail();
        computeOtherDist();
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
        for (int i = 0; i < static_cast<int>(trail.size()); i++)
        {
            int t = trail[i];
            freeT[t] = std::max(freeT[t], myLen - i + 1);
            occId[t] = w.myId;
            occTeam[t] = w.myTeam;
            occHead[t] = i == 0;
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

        // ---- splitting
        bool threatened = false;
        for (auto& s : segs)
            if (s.head && s.team != w.myTeam)
            {
                int dx = std::abs(s.tile % w.W - myHead % w.W), dy = std::abs(s.tile / w.W - myHead / w.W);
                dx = std::min(dx, w.W - dx);
                dy = std::min(dy, w.H - dy);
                if (dx + dy <= 2)
                    threatened = true;
            }
        if (myLen >= SPLIT_LEN && myLen >= 4 && units < w.unitLimit && units < SPLIT_MAX_UNITS &&
            round < SPLIT_STOP_ROUND && !threatened)
        {
            int k = myLen / 2;
            out += "SPLIT " + std::to_string(k) + "\n";
            pending.clear();
            pendingSplit = true;
            return;
        }

        // ---- score each direction
        double best = -1e18;
        int bestD = -1;
        int areaCap = 3 * myLen + 30;
        for (int d = 0; d < 4; d++)
        {
            int t = step(myHead, d);
            if (t < 0)
                continue; // kelp
            double score = 0;
            if (occId[t] >= 0 && freeT[t] > 1)
            {
                // occupied: only an enemy head is worth entering (both die)
                if (ENABLE_RAM && occHead[t] && occTeam[t] != w.myTeam && units >= 2)
                {
                    int theirs = enemyVisibleLength(occId[t]);
                    if (theirs >= myLen)
                    {
                        score = 50.0 + theirs - myLen;
                        if (score > best)
                        {
                            best = score;
                            bestD = d;
                        }
                    }
                }
                continue;
            }
            double pearls;
            int area;
            bfsFrom(t, pearls, area, areaCap);
            score += 10.0 * pearls;
            int need = myLen + 3;
            if (area < need)
                score -= 200.0 * (need - area) / need + 50;
            int threat = enemyHeadThreat(t);
            if (threat > 0)
                score -= 30.0 + 2.0 * myLen;
            score += boxEffect(t);
            // mild preference to keep going straight (fewer self-tangles)
            if (d == myDir)
                score += 0.3;
            score += rng.uni() * 0.2;
            if (dbg)
                std::fprintf(dbg, "  cand %c t=(%d,%d) pearls=%.2f area=%d threat=%d freeT=%d score=%.2f\n", DIRC[d],
                             t % w.W, t / w.W, pearls, area, threat, freeT[t], score);
            if (score > best)
            {
                best = score;
                bestD = d;
            }
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
                if (t < 0)
                    rank = 1;
                else if (occHead[t] && occId[t] != w.myId)
                    rank = occTeam[t] == w.myTeam ? 0 : 3;
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
