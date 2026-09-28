// PROTOTYPE (scratchpad) - Slithery Fight. 63x27, xy symmetry: B tile = (62-x, 26-y).
#ifndef SLI_FEED
#define SLI_FEED 0      // S1: unit-reserve feeding schedule (keep the swarm alive to ~r400)
#endif
#ifndef SLI_FEED_MINK
#define SLI_FEED_MINK 0 // S1b: no feeding until the heard king is at least this long (before r420)
#endif
#ifndef SLI_DEEP
#define SLI_DEEP 0      // S2: survival look-ahead for L>=12 = min(len, SLI_DEEP) (0 off)
#endif
#ifndef SLI_ZONE
#define SLI_ZONE 0.0    // S3: penalty for L>=12 stepping into ram/trap zones (A frame)
#endif
#ifndef SLI_ALLYGAP
#define SLI_ALLYGAP 0.0 // S4: L>=12 penalty per allied head within 1 of the target tile
#endif
#ifndef SLI_COMBY
#define SLI_COMBY 2     // S3: comb rows counted as danger (y <= SLI_COMBY)
#endif
#ifndef SLI_RAMZ
#define SLI_RAMZ 1      // S3: include the ram zones (x>=34, bottom band) in the danger set
#endif
#ifndef SLI_SS
#define SLI_SS 0        // S1c: split-stop round override (0 = keep RP)
#endif

int sliReserve() const
{
    if (SLI_FEED == 2)
    {
        // keep the r250 burst that builds the king, then ration feeders so the swarm lasts
        if (round < 300) return KING_V2_RES_BIG;
        if (round < 400) return 24;
        if (round < 450) return 12;
        return KING_V2_RES_BIG;
    }
    if (round < 300) return 56;
    if (round < 350) return 50;
    if (round < 400) return 40;
    if (round < 450) return 26;
    if (round < 475) return 12;
    return 4;
}

bool slitheryfightOverride()
{
    if (SLI_SS > 0)
        RP.splitStopRound = SLI_SS;
    if (SLI_FEED)
        RP.feedReserve = sliReserve();
    if (SLI_FEED_MINK > 0 && round < 420 && kingLen < SLI_FEED_MINK)
        RP.feedReserve = 1000;
    return false;
}

double slitheryfightScore(int t, int d)
{
    (void)d;
    double s = 0;
    if (myLen >= 12 && SLI_ZONE > 0)
    {
        int x = t % w.W, y = t / w.W;
        if (w.myTeam == 'B')
        {
            x = 62 - x;
            y = 26 - y;
        }
        bool danger = (SLI_RAMZ && (x >= 34 || (y >= 19 && x >= 18))) || (y <= SLI_COMBY && x >= 19 && x <= 33);
        if (danger)
            s -= SLI_ZONE;
    }
    if (SLI_ALLYGAP > 0 && myLen >= 12)
        for (auto& o : segs)
            if (o.head && o.team == w.myTeam && o.id != w.myId && wrapDist(o.tile, t) <= 1)
                s -= SLI_ALLYGAP;
    if (SLI_DEEP > 12 && myLen >= 12)
    {
        int want = std::min(myLen, SLI_DEEP);
        if (want > 12)
        {
            int dep = surviveDepth(t, want);
            if (dep < want)
                s -= 100.0 + 25.0 * (want - dep);
        }
    }
    return s;
}
