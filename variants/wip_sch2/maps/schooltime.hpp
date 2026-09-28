// Map-specific logic for "Schooltime". Included inside struct Bot, so it can use
// every Bot member (myHead, myLen, round, units, segs, step(), w, trail, ...).
// Only called when the recognised map is "Schooltime".
//
// The "yard" (x22-37, y24-39) is reachable only through portals 0 and 1; its
// inside mouths are (28..31, 25). The "pool" inside it (x27-32, y34-38, gap
// [1,20]) is about a third of the map's spawn income. See notes/maps/schooltime.md.

#ifndef SCH_RUSH
#define SCH_RUSH 1 // S1: opening rush of the inner/middle starters' halves to the yard
#endif
#ifndef SCH_RUSH_D
#define SCH_RUSH_D 37 // max pool distance at r<=3 to become a rusher
#endif
#ifndef SCH_RUSH_W
#define SCH_RUSH_W 8.0 // pull per step closer to the pool
#endif
#ifndef SCH_RUSH_INNER
#define SCH_RUSH_INNER 1 // 1: only the inner starter's two halves rush (x 20-39 at r<=3)
#endif
#ifndef SCH_RUSH_POOL
#define SCH_RUSH_POOL 1 // keep pulling inside the yard until the head reaches the pool
#endif
#ifndef SCH_YKING_PULL
#define SCH_YKING_PULL 1 // S3: also pull big dragons outside the yard towards it
#endif
#ifndef SCH_HOLD
#define SCH_HOLD 0 // S2: one-way yard doors + don't park on the inside mouths
#endif
#ifndef SCH_YKING
#define SCH_YKING 0 // S3: big dragons / king live in the yard
#endif
// ---- pass 2 (notes/maps/schooltime-pass2.md). All default OFF.
#ifndef SCH_LAYOUT
#define SCH_LAYOUT 0 // detect the server's second spawn layout ("B": no pool) and patch gaps
#endif
#ifndef SCH_LAYOUT_PATCH
#define SCH_LAYOUT_PATCH 1 // with SCH_LAYOUT: on B, replace the pearl gaps with the B table
#endif
#ifndef SCH_LAYOUT_NOYARD
#define SCH_LAYOUT_NOYARD 1 // with SCH_LAYOUT: on B, switch off all yard behaviour (rush etc.)
#endif
#ifndef SCH_CROWD
#define SCH_CROWD 0 // (a) yard congestion: spread inside the yard, mid/long dragons don't walk in after r60
#endif
#ifndef SCH_CROWD_W
#define SCH_CROWD_W 6.0
#endif
#ifndef SCH_CONTEST
#define SCH_CONTEST 0 // (b) small dragons in/at the yard chase enemy heads; long ones avoid an enemy-held yard
#endif
#ifndef SCH_FALLBACK
#define SCH_FALLBACK 0 // (c) on B / lost yard: big dragons stay out of the maze band (y 8-21)
#endif
#ifndef SCH_FB_W
#define SCH_FB_W 6.0
#endif
#ifndef SCH_NORUSH_KID
#define SCH_NORUSH_KID 0 // (d) only r<=3 starters rush; split children near the mouths don't get the pull
#endif

std::vector<int> schD, schYard, schMouthDist;
int schRusher = -1;
// pass 2 state (per process)
int schLayout = 0;          // 0 unknown (treated as A), 1 = A (pool), 2 = B (no pool)
int schEnemyYardSeen = -1000; // last round we saw an enemy head inside the yard
int schEnemyYardN = 0;        // enemy heads seen in the yard that round
// Layout B spawn tiles {x, y, gmin, gmax}, reconstructed from 10 ladder replays (ch9).
static constexpr int SCH_B_N = 178;
static constexpr int16_t SCH_B_TILES[SCH_B_N][4] = {{8,2,20,50},{51,2,20,50},{14,3,20,50},{45,3,20,50},{20,4,20,200},{29,4,20,50},{30,4,20,50},{39,4,20,200},{9,5,20,50},{14,5,20,50},{45,5,20,50},{50,5,20,50},{10,7,20,200},{49,7,20,200},{16,8,20,80},{17,8,20,80},{18,8,20,80},{41,8,20,80},{42,8,20,80},{43,8,20,80},{18,9,20,80},{19,9,20,80},{26,9,20,50},{33,9,20,50},{40,9,20,80},{41,9,20,80},{16,10,20,80},{17,10,20,80},{18,10,20,80},{19,10,20,80},{21,10,20,50},{38,10,20,50},{40,10,20,80},{41,10,20,80},{42,10,20,80},{43,10,20,80},{16,11,20,80},{17,11,20,80},{18,11,20,80},{41,11,20,80},{42,11,20,80},{43,11,20,80},{8,12,20,50},{51,12,20,50},{4,14,20,200},{55,14,20,200},{25,15,20,200},{34,15,20,200},{8,16,20,80},{25,16,20,200},{34,16,20,200},{51,16,20,80},{4,17,20,50},{13,17,20,200},{24,17,20,200},{35,17,20,200},{46,17,20,200},{55,17,20,50},{6,18,20,200},{13,18,20,200},{24,18,20,200},{25,18,20,200},{34,18,20,200},{35,18,20,200},{46,18,20,200},{53,18,20,200},{19,19,20,80},{20,19,20,80},{24,19,20,200},{25,19,20,200},{26,19,20,200},{33,19,20,200},{34,19,20,200},{35,19,20,200},{39,19,20,80},{40,19,20,80},{24,20,20,200},{25,20,20,200},{34,20,20,200},{35,20,20,200},{1,21,20,200},{14,21,20,200},{15,21,20,200},{44,21,20,200},{45,21,20,200},{58,21,20,200},{22,22,20,200},{37,22,20,200},{22,23,20,200},{37,23,20,200},{10,25,20,200},{11,25,20,200},{28,25,20,200},{29,25,20,200},{30,25,20,200},{31,25,20,200},{48,25,20,200},{49,25,20,200},{8,28,20,200},{9,28,20,200},{10,28,20,200},{11,28,20,200},{12,28,20,200},{13,28,20,200},{46,28,20,200},{47,28,20,200},{48,28,20,200},{49,28,20,200},{50,28,20,200},{51,28,20,200},{8,29,20,200},{9,29,20,200},{10,29,20,200},{11,29,20,200},{12,29,20,200},{13,29,20,200},{46,29,20,200},{47,29,20,200},{48,29,20,200},{49,29,20,200},{50,29,20,200},{51,29,20,200},{8,30,20,200},{9,30,20,200},{10,30,20,200},{11,30,20,200},{48,30,20,200},{49,30,20,200},{50,30,20,200},{51,30,20,200},{10,31,20,200},{11,31,20,200},{48,31,20,200},{49,31,20,200},{2,32,20,200},{3,32,20,200},{56,32,20,200},{57,32,20,200},{1,33,20,200},{2,33,20,200},{3,33,20,200},{4,33,20,200},{55,33,20,200},{56,33,20,200},{57,33,20,200},{58,33,20,200},{1,34,20,200},{2,34,20,200},{57,34,20,200},{58,34,20,200},{2,35,20,200},{22,35,20,200},{23,35,20,200},{36,35,20,200},{37,35,20,200},{57,35,20,200},{22,36,20,200},{23,36,20,200},{24,36,20,200},{35,36,20,200},{36,36,20,200},{37,36,20,200},{22,37,20,200},{23,37,20,200},{24,37,20,200},{35,37,20,200},{36,37,20,200},{37,37,20,200},{21,38,20,200},{22,38,20,200},{23,38,20,200},{36,38,20,200},{37,38,20,200},{38,38,20,200},{21,39,20,200},{22,39,20,200},{37,39,20,200},{38,39,20,200}};

// Compare visible countdowns with both layouts. Called every turn.
void schDetect()
{
    if (schLayout != 0 || !w.known)
        return;
    static std::vector<char> bSpawn;
    if (bSpawn.empty())
    {
        bSpawn.assign(w.N, 0);
        for (int i = 0; i < SCH_B_N; i++)
            bSpawn[w.idx(SCH_B_TILES[i][0], SCH_B_TILES[i][1])] = 1;
    }
    for (int i = 0; i < 49; i++)
    {
        int t = w.idx(in.tx[i], in.ty[i]);
        bool spawns = in.tin[i] >= 0, aSp = w.known->gmax[t] > 0, bSp = bSpawn[t];
        if (aSp == bSp)
            continue;
        schLayout = spawns == aSp ? 1 : 2;
        break;
    }
    if (schLayout == 2 && SCH_LAYOUT_PATCH)
    {
        for (int t = 0; t < w.N; t++)
        {
            w.gmin[t] = 0;
            w.gmax[t] = 0;
        }
        for (int i = 0; i < SCH_B_N; i++)
        {
            int t = w.idx(SCH_B_TILES[i][0], SCH_B_TILES[i][1]);
            w.gmin[t] = SCH_B_TILES[i][2];
            w.gmax[t] = SCH_B_TILES[i][3];
        }
        for (int i = 0; i < 49; i++) // keep what we see this turn
            if (in.tin[i] < 0)
                w.gmax[w.idx(in.tx[i], in.ty[i])] = 0;
    }
}

void schInit()
{
    if (!schD.empty())
        return;
    const int INF = 1 << 20;
    schD.assign(w.N, INF);
    schYard.assign(w.N, 0);
    schMouthDist.assign(w.N, INF);
    // static portal-aware BFS distance to the pool; D[t] = steps from t to the pool,
    // so search backwards: edges u->v with step(u,d)==v. Build reverse adjacency.
    std::vector<std::vector<int>> rev(w.N);
    for (int u = 0; u < w.N; u++)
        for (int d = 0; d < 4; d++)
        {
            int v = step(u, d);
            if (v >= 0)
                rev[v].push_back(u);
        }
    std::vector<int> q;
    for (int y = 34; y <= 38; y++)
        for (int x = 27; x <= 32; x++)
        {
            int t = w.idx(x, y);
            if (w.gmin[t] == 1 && w.gmax[t] == 20)
            {
                schD[t] = 0;
                q.push_back(t);
            }
        }
    for (size_t i = 0; i < q.size(); i++)
        for (int u : rev[q[i]])
            if (schD[u] > schD[q[i]] + 1)
            {
                schD[u] = schD[q[i]] + 1;
                q.push_back(u);
            }
    q.assign(1, w.idx(29, 36));
    schYard[q[0]] = 1;
    for (size_t i = 0; i < q.size(); i++)
        for (int d = 0; d < 4; d++)
        {
            int v = step(q[i], d);
            if (v >= 0 && v == w.plainStep(q[i], d) && !schYard[v])
            {
                schYard[v] = 1;
                q.push_back(v);
            }
        }
    for (int t = 0; t < w.N; t++)
    {
        int x = t % w.W, y = t / w.W;
        for (int mx = 28; mx <= 31; mx++)
            schMouthDist[t] = std::min(schMouthDist[t], std::abs(x - mx) + std::abs(y - 25));
    }
}

bool schMouth(int t) const
{
    int x = t % w.W, y = t / w.W;
    return y == 25 && x >= 28 && x <= 31;
}

// Return true after writing an action to `out` to override normal play this turn.
bool schooltimeOverride()
{
#if SCH_LAYOUT
    schDetect();
#endif
#if SCH_CONTEST || SCH_FALLBACK
    schInit();
    {
        int n = 0;
        for (auto& o : segs)
            if (o.head && o.team != w.myTeam && schYard[o.tile])
                n++;
        if (n > 0)
        {
            schEnemyYardSeen = round;
            schEnemyYardN = n;
        }
    }
#endif
    return false;
}

// (c) big dragons stay out of the maze band (y 8-21), where 10 of 11 big deaths per loss happened.
double schFallbackScore(int t)
{
    if (myLen < 8 && !kingSelf)
        return 0.0;
    auto band = [&](int u) { int y = u / w.W; return y >= 8 && y <= 21 ? 1 : 0; };
    return -SCH_FB_W * (band(t) - band(myHead)) - (band(t) ? 0.5 * SCH_FB_W : 0.0);
}

// Extra score for moving onto tile t (direction d). Added to the normal score.
double schooltimeScore(int t, int d)
{
    schInit();
    if (myHead < 0 || t < 0)
        return 0.0;
    double s = 0;
    bool inYard = schYard[myHead], toYard = schYard[t];
#if SCH_LAYOUT && SCH_LAYOUT_NOYARD
    if (schLayout == 2)
    {
        schRusher = 0;
#if SCH_FALLBACK
        s += schFallbackScore(t);
#endif
        return s;
    }
#endif
#if SCH_NORUSH_KID
    if (schRusher < 0 && round > 3)
        schRusher = 0;
#endif
#if SCH_RUSH
    if (schRusher < 0)
    {
        int hx = myHead % w.W;
        bool early = round <= 3 && schD[myHead] <= SCH_RUSH_D && (!SCH_RUSH_INNER || (hx >= 20 && hx <= 39));
        schRusher = early || (!inYard && schD[myHead] <= 14);
    }
    if (SCH_RUSH_POOL ? schD[myHead] <= 1 : inYard)
        schRusher = 0;
    if (schRusher && round < 90 && myLen <= 6)
        s += SCH_RUSH_W * (schD[myHead] - schD[t]);
#endif
#if SCH_HOLD
    if (round < 350 && inYard && !toYard)
    {
        bool exempt = feedPhase() && kingTile >= 0 && !schYard[kingTile];
        if (!exempt)
            s -= 30.0;
    }
    if (toYard && schMouth(t))
        s -= 6.0;
#endif
#if SCH_YKING
    if (round >= RP.kingSeedRound && (kingSelf || iAmKing() || myLen >= 10))
    {
        if (!inYard)
        {
            bool enemyClose = false;
            for (auto& o : segs)
                if (o.head && o.team != w.myTeam && wrapDist(o.tile, myHead) <= 3)
                    enemyClose = true;
            if (SCH_YKING_PULL && !enemyClose)
            {
                s += 5.0 * (schD[myHead] - schD[t]);
                // cancel the blind-portal king penalty on the crossing into the yard
                if (toYard && myLen >= 10 && !visible[t] && t != w.plainStep(myHead, d))
                    s += RP.kingPortal;
            }
        }
        else if (toYard)
        {
            int m = schMouthDist[t];
            if (m <= 3)
                s -= (4 - m) * (10.0 + myLen);
        }
        else
            s -= 5.0 * (10.0 + myLen); // leaving must look worse than the mouth band
#if SCH_DEBUGD
        if (dbg)
            std::fprintf(dbg, "  sch yking t=(%d,%d) s=%.1f\n", t % w.W, t / w.W, s);
#endif
    }
#endif
#if SCH_CROWD
    if (inYard && toYard)
    {
        // spread: tiles next to another ally head, and near-dead-end tiles when crowded
        int allyHeads = 0, adj = 0;
        for (auto& o : segs)
            if (o.head && o.team == w.myTeam && o.tile != myHead)
            {
                allyHeads++;
                int dd = wrapDist(o.tile, t);
                if (dd <= 1)
                    adj += 2;
                else if (dd == 2)
                    adj += 1;
            }
        s -= SCH_CROWD_W * adj;
        if (allyHeads >= 3)
        {
            int exits = 0;
            for (int e = 0; e < 4; e++)
            {
                int v = step(t, e);
                if (v >= 0 && v != myHead && freeT[v] <= 1)
                    exits++;
            }
            if (exits <= 1)
                s -= SCH_CROWD_W * (allyHeads >= 6 ? 2 : 1);
        }
    }
    else if (!inYard && toYard && round >= 60 && myLen >= 4 && !(schRusher > 0))
        s -= 10.0 + myLen; // the yard fills itself by births; walking in only adds jams
#endif
#if SCH_CONTEST
    if (myLen <= 3 && (inYard || schMouthDist[myHead] <= 4 || schD[myHead] <= 16))
    {
        // chase the nearest visible enemy head that is at least as long as us
        int best = -1, bd = 99;
        for (auto& o : segs)
            if (o.head && o.team != w.myTeam && (inYard ? schYard[o.tile] : true))
            {
                int dd = wrapDist(o.tile, myHead);
                if (dd < bd)
                {
                    bd = dd;
                    best = o.tile;
                }
            }
        if (best >= 0 && bd >= 3 && bd <= 6)
            s += 4.0 * (bd - wrapDist(best, t));
    }
    if (myLen >= 6 && !inYard && toYard && round - schEnemyYardSeen <= 40 && schEnemyYardN >= 2)
        s -= 40.0; // don't feed long dragons into a contested yard
#endif
#if SCH_FALLBACK
    if (round - schEnemyYardSeen <= 40 && schEnemyYardN >= 3)
        s += schFallbackScore(t);
#endif
    (void)d;
    return s;
}
