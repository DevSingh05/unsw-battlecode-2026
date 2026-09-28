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

std::vector<int> schD, schYard, schMouthDist;
int schRusher = -1;

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
    return false;
}

// Extra score for moving onto tile t (direction d). Added to the normal score.
double schooltimeScore(int t, int d)
{
    schInit();
    if (myHead < 0 || t < 0)
        return 0.0;
    double s = 0;
    bool inYard = schYard[myHead], toYard = schYard[t];
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
    (void)d;
    return s;
}
