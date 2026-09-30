// Map-specific logic for "Trophy". Included inside struct Bot, so it can use
// every Bot member (myHead, myLen, round, units, segs, step(), w, trail, ...).
// Only called when the recognised map is "Trophy".

// Return true after writing an action to `out` to override normal play this turn.
bool trophyOverride()
{
    return false;
}

// Extra score for moving onto tile t (direction d). Added to the normal score.
double trophyScore(int t, int d)
{
    (void)t;
    (void)d;
    return 0.0;
}
