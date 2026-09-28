// Map-specific logic for "Schooltime". Included inside struct Bot, so it can use
// every Bot member (myHead, myLen, round, units, segs, step(), w, trail, ...).
// Only called when the recognised map is "Schooltime".

// Return true after writing an action to `out` to override normal play this turn.
bool schooltimeOverride()
{
    return false;
}

// Extra score for moving onto tile t (direction d). Added to the normal score.
double schooltimeScore(int t, int d)
{
    (void)t;
    (void)d;
    return 0.0;
}
