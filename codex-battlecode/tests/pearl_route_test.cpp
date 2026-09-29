#define PEARL_ROUTE 1
#define main battlecode_program_main
#include "../bot/main.cpp"
#undef main
#include <cassert>

int main()
{
    Bot b;
    b.w.init(10, 10);
    b.round = 0;
    b.visible.assign(100, 1);
    b.otherDist.assign(100, INF);
    b.freeT.assign(100, 1);
    std::fill(b.w.nxt.begin(), b.w.nxt.end(), -1);
    b.w.nxt[0] = 1;
    b.w.nxt[1] = 2;
    b.w.pearlMem[1] = b.w.pearlMem[2] = 1;
    double score;
    int area;
    b.bfsFrom(0, score, area, 100);
    assert(area == 3);
    // A fork offers two pearls at the same arrival time; only one is collectable.
    assert(std::abs(b.bestPearlRoute() - 0.82 * 0.82) < 1e-12);
    // A route through both pearls earns both, without revisiting a tile.
    b.w.nxt[1] = -1;
    b.w.nxt[4] = 2;
    b.w.nxt[8] = 0; // loop must not count the start twice
    b.bfsFrom(0, score, area, 100);
    assert(std::abs(b.bestPearlRoute() - (0.82 * 0.82 + 0.82 * 0.82 * 0.82)) < 1e-12);
    // The time-aware BFS excludes bodies which will not vacate in time.
    b.freeT[2] = INF;
    b.bfsFrom(0, score, area, 100);
    assert(area == 2);
    assert(std::abs(b.bestPearlRoute() - 0.82 * 0.82) < 1e-12);
    // Future food uses the same arrival-timer model as the existing planner.
    b.freeT[2] = 1;
    b.w.pearlMem[2] = 0;
    b.w.spawnAt[2] = 2;
    b.bfsFrom(0, score, area, 100);
    assert(std::abs(b.bestPearlRoute() - (0.82 * 0.82 + 0.85 * 0.82 * 0.82 * 0.82)) < 1e-12);
    std::cout << "PASS: mutually exclusive branches, sequential food, loops, body blocking, spawn timing\n";
}
