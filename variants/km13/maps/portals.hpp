// Map-specific logic for "Portals". Included inside struct Bot. All ideas are off by default.
// Each team's half is a separate 240-tile component; all of a team's pearls sit in
// the OTHER half and are reached only through portals:
//  - 6 "tubes" per team: 4 pearl tiles [1,10] spliced into one main-area edge e->x
//    (enter from e moving d, 4 tiles, come out on x = plain neighbour of e in d);
//  - 8 "pockets": single pearl tiles with 1 exit (dead end);
//  - 1 "sock": 9-tile dead-end corridor with 4 hot [1,1] tiles.
// POR_PULL: value tubes/sock correctly (full after 10 rounds, not 0.5) and pull to them.
// POR_EXIT: never enter a tube whose exit tile holds our body / an ally that stays.

#ifndef POR_PULL
#define POR_PULL 1
#endif
#ifndef POR_W
#define POR_W 16.0 // score per expected pearl in the best tube
#endif
#ifndef POR_G
#define POR_G 0.88 // discount per step to the tube
#endif
#ifndef POR_EXIT
#define POR_EXIT 1
#endif
#ifndef POR_EXIT_PEN
#define POR_EXIT_PEN 300.0
#endif
#ifndef POR_SOCK_MAXLEN
#define POR_SOCK_MAXLEN 3 // only dragons this short are pulled into the sock
#endif
#ifndef POR_KING_PULL
#define POR_KING_PULL 1 // 0: no tube pull for kings / L>=10
#endif
#ifndef POR_ONEKING
#define POR_ONEKING 0 // one king: the 2nd candidate steps down from POR_MERGE_R
#endif
#ifndef POR_MERGE_R
#define POR_MERGE_R 400
#endif
#ifndef POR_MERGE_GAP
#define POR_MERGE_GAP 2
#endif
#ifndef POR_KS
#define POR_KS -1 // RP overrides, -1 = keep applyMapParams' value (v2: 250/360/300/3)
#endif
#ifndef POR_SS
#define POR_SS -1
#endif
#ifndef POR_FS
#define POR_FS -1
#endif
#ifndef POR_RES
#define POR_RES -1
#endif
#ifndef POR_EXIT_HEADS
#define POR_EXIT_HEADS 0 // radius: ally head this close to the exit tile blocks tube entry
#endif
#ifndef POR_EXIT_HEADS_LEN
#define POR_EXIT_HEADS_LEN 6 // ...for dragons at least this long
#endif
#ifndef POR_BIG_NOTUBE
#define POR_BIG_NOTUBE 0 // dragons this long never enter tubes (0 = off)
#endif
#ifndef POR_SPLICE_CLEAR
#define POR_SPLICE_CLEAR 0 // keep off tube entry/exit tiles unless entering the tube next
#endif
#ifndef POR_SPLICE_PEN
#define POR_SPLICE_PEN 4.0
#endif
#ifndef POR_ONEWAY
#define POR_ONEWAY 0 // tubes only entered in their canonical direction
#endif
#ifndef POR_POCKET_PEN
#define POR_POCKET_PEN 0.0 // extra penalty for stepping into a pocket (non-feeders)
#endif

struct PorEntry
{
    int e, d, x; // step from e in direction d enters; x = exit tile (-1 sock/pocket)
    std::vector<int> tiles;
    bool sock;
    bool canon = true; // canonical (one-way) direction
};
std::vector<char> porSplice; // tube entry/exit tiles
std::vector<PorEntry> porEnt;
std::vector<int> porKind; // 0 main, 1 tube, 2 pocket, 3 sock
std::vector<int> porBfs, porQ;
bool porReady = false;

void porInit()
{
    if (porReady || w.known == nullptr)
        return;
    porReady = true;
    if (POR_KS >= 0) RP.kingSeedRound = POR_KS;
    if (POR_SS >= 0) RP.splitStopRound = POR_SS;
    if (POR_FS >= 0) RP.feedStart = POR_FS;
    if (POR_RES >= 0) RP.feedReserve = POR_RES;
    porKind.assign(w.N, 0);
    auto pearlT = [&](int t) { return w.gmax[t] > 0 && !(w.gmin[t] == 1 && w.gmax[t] == 1); };
    for (int e = 0; e < w.N; e++)
    {
        if (w.gmax[e] != 0)
            continue;
        for (int d = 0; d < 4; d++)
        {
            int v = step(e, d);
            if (v < 0 || !pearlT(v))
                continue;
            PorEntry en{e, d, -1, {v}, false};
            int prev = e, cur = v;
            bool pocket = false;
            for (int it = 0; it < 8; it++)
            {
                int nx = -1, cnt = 0;
                for (int d2 = 0; d2 < 4; d2++)
                {
                    int n = step(cur, d2);
                    if (n >= 0 && n != prev)
                    {
                        nx = n;
                        cnt++;
                    }
                }
                if (cnt == 0)
                {
                    pocket = true;
                    break;
                }
                if (pearlT(nx))
                {
                    en.tiles.push_back(nx);
                    prev = cur;
                    cur = nx;
                    continue;
                }
                en.x = nx;
                break;
            }
            if (pocket)
            {
                for (int t : en.tiles)
                    porKind[t] = 2;
                continue;
            }
            if (en.x < 0)
                continue;
            for (int t : en.tiles)
                porKind[t] = 1;
            porEnt.push_back(en);
        }
    }
    // splice tiles + canonical directions (team A table; B is the 180-degree rotation)
    porSplice.assign(w.N, 0);
    static const int CAN[6][3] = {{12, 13, 1}, {3, 15, 0}, {8, 11, 1}, {12, 5, 1}, {3, 6, 2}, {8, 2, 1}};
    for (auto& en : porEnt)
    {
        porSplice[en.e] = 1;
        porSplice[en.x] = 1;
        int ex = en.e % w.W, ey = en.e / w.W;
        bool c = false;
        for (auto& k : CAN)
        {
            if (ex == k[0] && ey == k[1] && en.d == k[2])
                c = true;
            if (w.W == 32 && w.H == 16 && ex == 31 - k[0] && ey == 15 - k[1] && en.d == (k[2] + 2) % 4)
                c = true;
        }
        en.canon = c;
    }
    // socks (hard-coded; B's is A's rotated by 180 degrees)
    auto sock = [&](int ex, int ey, int d, std::vector<std::pair<int, int>> ts) {
        PorEntry en{w.idx(ex, ey), d, -1, {}, true};
        for (auto& p : ts)
        {
            en.tiles.push_back(w.idx(p.first, p.second));
            porKind[en.tiles.back()] = 3;
        }
        porEnt.push_back(en);
    };
    if (w.W == 32 && w.H == 16)
    {
        sock(14, 0, 1, {{15, 0}, {15, 1}, {15, 2}, {15, 3}, {15, 4}, {15, 5}, {15, 6}, {15, 7}, {16, 7}});
        sock(17, 15, 3, {{16, 15}, {16, 14}, {16, 13}, {16, 12}, {16, 11}, {16, 10}, {16, 9}, {16, 8}, {15, 8}});
    }
}

// probability that tile t holds a pearl when our head reaches it on round r
double porP(int t, int r) const
{
    if (w.gmin[t] == 1 && w.gmax[t] == 1)
    {
        if (visible[t])
            return w.pearlMem[t] ? 1.0 : (r > round ? 0.95 : 0.0);
        return 0.9;
    }
    if (w.gmax[t] <= 0)
        return 0.0;
    if (visible[t])
    {
        if (w.pearlMem[t])
            return 1.0;
        return (w.spawnAt[t] >= 0 && r >= w.spawnAt[t]) ? 0.95 : 0.0;
    }
    int ls = w.lastSeen[t];
    if (ls < 0)
        return std::min(1.0, (r + 1.0) / w.gmax[t]);
    if (w.pearlMem[t])
        return 0.9;
    if (w.spawnAt[t] > ls)
        return r >= w.spawnAt[t] ? 0.9 : 0.0;
    return 0.9 * std::min(1.0, double(r - ls) / w.gmax[t]);
}

double porValue(const PorEntry& en, int arrive) const
{
    double v = 0;
    for (size_t i = 0; i < en.tiles.size(); i++)
        v += porP(en.tiles[i], arrive + static_cast<int>(i));
    return v;
}

// Return true after writing an action to `out` to override normal play this turn.
bool portalsOverride()
{
    porInit();
#if POR_ONEKING
    // no enemy can reach us here: a second king candidate is wasted length.
    // From POR_MERGE_R, a candidate that hears a longer fresh king steps down
    // (and, being short of the king, becomes a feeder/merger).
    if (kingSelf && round >= POR_MERGE_R)
        for (auto& k : kingsSeen)
            if (round - k.round <= 8 && kw10(k.id) != kw10(w.myId) && k.len >= myLen + POR_MERGE_GAP)
            {
                kingSelf = false;
                break;
            }
#endif
    return false;
}

// Extra score for moving onto tile t (direction d). Added to the normal score.
double portalsScore(int t, int d)
{
    porInit();
    if (!porReady || myHead < 0 || t < 0)
        return 0.0;
    double s = 0;
    // ---- entering a structure this move
    for (auto& en : porEnt)
    {
        if (en.e != myHead || en.d != d)
            continue;
        if (!en.sock && POR_ONEWAY && !en.canon)
            s -= POR_EXIT_PEN;
        if (!en.sock && POR_EXIT)
        {
            int x = en.x;
            bool bad = false;
            if (occId[x] >= 0)
            {
                if (occId[x] == w.myId)
                    bad = true; // our own body stays put while we eat 4 pearls
                else if (occTeam[x] == w.myTeam && (occHead[x] || freeT[x] > 5))
                    bad = true;
            }
            // an ally head near the exit can step onto it while we are blind inside
            if (!bad && POR_EXIT_HEADS > 0 && myLen >= POR_EXIT_HEADS_LEN)
                for (auto& o : segs)
                    if (o.head && o.team == w.myTeam && o.id != w.myId && wrapDist(o.tile, x) <= POR_EXIT_HEADS)
                        bad = true;
            if (POR_BIG_NOTUBE > 0 && myLen >= POR_BIG_NOTUBE && !shouldFeed())
                bad = true;
            if (bad)
                s -= POR_EXIT_PEN;
        }
    }
#if POR_SPLICE_CLEAR
    if (porSplice[t])
    {
        bool enterNext = false;
        for (auto& en : porEnt)
        {
            if (en.sock || en.e != t || (POR_ONEWAY && !en.canon))
                continue;
            if (en.d == d || (POR_PULL && !shouldFeed() && porValue(en, round + 1) >= 2.0))
                enterNext = true;
        }
        if (!enterNext)
            s -= POR_SPLICE_PEN;
    }
#endif
    if (porKind[t] == 2 && POR_POCKET_PEN > 0 && !shouldFeed())
        s -= POR_POCKET_PEN;
#if POR_PULL
    if (shouldFeed() || qparkQueen()) // ROUND3 P7: the parked queen takes no tube pull
        return s;
    if (!POR_KING_PULL && (kingSelf || myLen >= 10))
        return s;
    // BFS over the main area from t
    if (static_cast<int>(porBfs.size()) != w.N)
        porBfs.assign(w.N, INF);
    std::fill(porBfs.begin(), porBfs.end(), INF);
    porQ.clear();
    bool inside = porKind[t] != 0;
    if (!inside)
    {
        porBfs[t] = 1;
        porQ.push_back(t);
        for (size_t qi = 0; qi < porQ.size(); qi++)
        {
            int u = porQ[qi];
            int du = porBfs[u];
            if (du > 40)
                continue;
            for (int d2 = 0; d2 < 4; d2++)
            {
                int v = step(u, d2);
                if (v < 0 || porKind[v] != 0 || porBfs[v] != INF)
                    continue;
                if (freeT[v] > du + 1)
                    continue;
                porBfs[v] = du + 1;
                porQ.push_back(v);
            }
        }
    }
    double best = 0;
    for (auto& en : porEnt)
    {
        if (en.sock && myLen > POR_SOCK_MAXLEN)
            continue;
        if (POR_ONEWAY && !en.sock && !en.canon)
            continue;
        int dist; // moves until our head is on the first structure tile
        if (en.e == myHead && en.d == d)
            dist = 1;
        else if (!inside && porBfs[en.e] != INF)
            dist = porBfs[en.e] + 1;
        else
            continue;
        if (dist > 1 && !en.sock)
        {
            // someone standing on / next to the exit tile: skip for planning
            if (occId[en.x] == w.myId && dist <= 3)
                continue;
        }
        double v = porValue(en, round + dist - 1);
        // an ally head nearer the entry will probably take it
        if (dist > 1)
            for (auto& o : segs)
                if (o.head && o.team == w.myTeam && o.id != w.myId && wrapDist(o.tile, en.e) + 1 < dist)
                {
                    v *= 0.4;
                    break;
                }
        v *= std::pow(POR_G, dist - 1);
        best = std::max(best, v);
    }
    s += POR_W * best;
#endif
    return s;
}
