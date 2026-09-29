// Included inside Bot. Optimistic static walking distances ignore bodies,
// so congestion alone cannot claim that food is behind a wall.
bool blockedFoodNeedsDoor()
{
    bool doorSeen = false;
    std::vector<int> targets;
    for (int i = 0; i < 49; ++i)
    {
        int t = w.idx(in.tx[i], in.ty[i]);
        if (in.tpearl[i] && wrapDist(t, myHead) <= UNK_BLOCKED_DIRECT)
            targets.push_back(t);
        if (!w.portalSide.empty())
            for (int d = 0; d < 4; ++d)
                if (w.portalSide[4 * t + d] && step(t, d) < 0)
                    doorSeen = true;
    }
    if (!doorSeen || targets.empty()) return false;
    std::vector<int> distance(w.N, -1), queue{myHead};
    distance[myHead] = 0;
    for (size_t at = 0; at < queue.size(); ++at)
    {
        int u = queue[at];
        if (distance[u] + 1 >= UNK_BLOCKED_DETOUR) continue;
        for (int d = 0; d < 4; ++d)
        {
            int v = step(u, d);
            if (v >= 0 && distance[v] < 0)
            {
                distance[v] = distance[u] + 1;
                queue.push_back(v);
            }
        }
    }
    for (int t : targets)
        if (distance[t] < 0)
        {
            if (UNK_BLOCKED_LOG)
                out += "LOG blocked-food " + std::to_string(t % w.W) + "," + std::to_string(t / w.W) + "\n";
            return true;
        }
    return false;
}
