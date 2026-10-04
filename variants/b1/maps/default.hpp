// Map-specific logic for "Default". Included inside struct Bot, so it can use
// every Bot member (myHead, myLen, round, units, segs, step(), w, trail, ...).
// Only called when the recognised map is "Default".

// Return true after writing an action to `out` to override normal play this turn.
bool defaultOverride()
{
    return false;
}

// Extra score for moving onto tile t (direction d). Added to the normal score.
double defaultScore(int t, int d)
{
    (void)t;
    (void)d;
    return 0.0;
}
