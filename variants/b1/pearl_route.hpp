// Included inside Bot. The BFS order forms a DAG of increasing arrival times.
// Keep one continuation at a fork; a single dragon cannot eat both branches.
std::vector<double> routeValue;
double bestPearlRoute()
{
    routeValue.assign(w.N, 0.0);
    for (auto it = bfsQ.rbegin(); it != bfsQ.rend(); ++it)
    {
        int u = *it;
        double continuation = 0;
        for (int d = 0; d < 4; ++d)
        {
            int v = step(u, d);
            if (v >= 0 && bfsDist[v] == bfsDist[u] + 1)
                continuation = std::max(continuation, routeValue[v]);
        }
        routeValue[u] = pearlValue(u, bfsDist[u]) + PEARL_GAMMA * continuation;
    }
    return bfsQ.empty() ? 0.0 : PEARL_GAMMA * routeValue[bfsQ.front()];
}
