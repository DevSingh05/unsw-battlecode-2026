// Map-specific logic for "Trauma". Included inside struct Bot, so it can use
// every Bot member (myHead, myLen, round, units, segs, step(), w, trail, ...).
// Only called when the recognised map is "Trauma".

// Return true after writing an action to `out` to override normal play this turn.
bool traumaOverride()
{
    return false;
}

// Extra score for moving onto tile t (direction d). Added to the normal score.
double traumaScore(int t, int d)
{
    (void)t;
    (void)d;
    return 0.0;
}
