#!/bin/zsh
# usage: ident.sh <botdir> [maps...] -> fingerprint per map/side (sandbox = deterministic, seed 1000) + result + our CPU max
cd /Users/devsingh/Developer/UNSW_Battlecode
D=$1; shift
if [ $# -gt 0 ]; then MAPS=("$@"); else MAPS=(maps/sprint/maze.map maps/devil.map maps/portals.map maps/dilemma.map maps/sprint/tower_defense.map maps/sprint/australia.map maps/schooltime.map); fi
touch $D/main.cpp
for m in $MAPS; do
  for side in A B; do
    if [ $side = A ]; then a=$D; b=variants/v55; else a=variants/v55; b=$D; fi
    o=$(unswbc run $m $a $b --seed 1000 --no-replay --no-logs --sandbox 2>&1)
    fp=$(echo "$o" | grep -E "^round |wins|draw" | sed -E 's/ \([0-9.]+s\)//' | md5 | cut -c1-10)
    res=$(echo "$o" | grep -E "wins|draw" | sed -E 's/ \([0-9.]+s\)//')
    cpu=$(echo "$o" | grep "team $side points" | sed -E 's/.*max ([0-9.]+M).*/\1/')
    echo "$(basename $m) $side $fp | $res | cpu_max $cpu"
  done
done
