#include "../archive/symmetry-v13-20260928/unseen_symmetry.hpp"
#include <algorithm>
#include <cassert>
#include <fstream>
#include <iostream>
#include <numeric>
#include <random>
#include <sstream>
#include <string>

int main(int argc, char** argv)
{
    // Every reflection is an involution, including seam edges and odd sizes.
    for (auto size : {std::pair{10, 8}, std::pair{25, 35}, std::pair{64, 64}})
    {
        UnseenSymmetry m;
        m.init(size.first, size.second);
        for (int s = 0; s < 3; ++s)
            for (int e = 0; e < 4 * size.first * size.second; ++e)
                assert(m.edgeMirrors[s][m.edgeMirrors[s][e]] == e);
        assert(m.edgeMirrors[0][0] == 4 * (size.second - 1) * size.first + 2);
        assert(m.edgeMirrors[1][3] == 4 * (size.first - 1) + 1);
    }
    // Contradict a formerly unique hypothesis; all its inferred facts vanish.
    {
        UnseenSymmetry m;
        m.init(12, 10);
        m.observeEdge(14, 0, 1);
        m.observeSpawner(14, false);
        m.observeSpawner(15, false);
        m.observeSpawner(m.mirrors[1][14], true);
        m.observeSpawner(m.mirrors[2][14], true);
        assert(m.mask == 1);
        std::vector<int> next(480), gaps(120, -1);
        m.apply(next, gaps);
        int edge = m.edgeMirrors[0][56], tile = m.mirrors[0][14];
        assert(next[edge] == -1 && gaps[tile] == 0);
        int otherBarren = m.mirrors[0][15];
        assert(gaps[otherBarren] == 0);
        m.observeEdge(tile, 1, 2); // portal observation keeps destination unknown
        m.observeSpawner(tile, true);
        assert(m.mask == 0);
        m.apply(next, gaps);
        assert(next[edge] == m.plain(edge / 4, edge % 4));
        assert(next[tile * 4 + 1] == -1);
        // The caller subsequently updates directly visible spawner gaps.
        assert(!m.barrenOverlay[tile]);
        assert(gaps[otherBarren] == -1);
    }

    long long checked = 0;
    for (int arg = 1; arg < argc; ++arg)
    {
        std::ifstream input(argv[arg]);
        assert(input);
        std::string line, tok;
        int w = 0, h = 0;
        std::vector<int> edge, spawn;
        while (std::getline(input, line))
        {
            std::istringstream row(line);
            row >> tok;
            if (tok == "MAP")
            {
                row >> w >> h;
                edge.assign(w * h * 4, 0);
                spawn.assign(w * h, 0);
            }
            if (tok == "TILE")
            {
                int x, y, low, high;
                row >> x >> y >> low >> high;
                spawn[y * w + x] = high > 0;
            }
            if (tok == "EDGE")
            {
                int index, kind, portal;
                row >> index >> kind >> portal;
                int r = index / (w + 1), x = index % (w + 1), y = r / 2;
                if (r % 2 == 0)
                {
                    edge[((y % h) * w + x % w) * 4] = kind;
                    edge[(((y + h - 1) % h) * w + x % w) * 4 + 2] = kind;
                }
                else
                {
                    edge[(y * w + x % w) * 4 + 3] = kind;
                    edge[(y * w + (x + w - 1) % w) * 4 + 1] = kind;
                }
            }
        }
        UnseenSymmetry m;
        m.init(w, h);
        std::vector<int> next(w * h * 4), gaps(w * h, -1), order(w * h);
        std::iota(order.begin(), order.end(), 0);
        std::mt19937 random(9026);
        std::shuffle(order.begin(), order.end(), random);
        int truth = 7;
        for (int s = 0; s < 3; ++s)
            for (int t = 0; t < w * h; ++t)
            {
                if (spawn[t] != spawn[m.mirrors[s][t]]) truth &= ~(1 << s);
                for (int d = 0; d < 4; ++d)
                    if (edge[4 * t + d] != edge[m.edgeMirrors[s][4 * t + d]]) truth &= ~(1 << s);
            }
        assert(truth); // these are the symmetric development fixtures
        for (int i = 0; i < w * h; ++i)
        {
            int t = order[i];
            for (int d = 0; d < 4; ++d) m.observeEdge(t, d, edge[4 * t + d]);
            m.observeSpawner(t, spawn[t]);
            assert((m.mask & truth) == truth);
            if (i % 17 && i + 1 != w * h) continue;
            m.apply(next, gaps);
            for (int u = 0; u < w * h; ++u)
            {
                if (m.barrenOverlay[u]) assert(!spawn[u]);
                for (int d = 0; d < 4; ++d)
                {
                    int k = m.inferredKind(4 * u + d);
                    if (k >= 0) { assert(k == edge[4 * u + d]); ++checked; }
                }
            }
        }
    }
    std::cout << "PASS: wrap/reflection, contradiction rollback, portal blocking; "
              << argc - 1 << " maps, " << checked << " inferred/direct edge checks\n";
}
