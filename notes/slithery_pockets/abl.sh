#!/bin/bash
cd /Users/devsingh/Developer/UNSW_Battlecode
S=/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad
L="bot:-DPOCKET_FACTORY=1 -DPF_EARLY=1 -DPF_CHILD_MAX=2 -DUNK_NECK_ESCAPE_GUARD=1 -DKING_CONSENSUS=1 -DESCAPE_DEADEND_FIX=1"
MAPS=${MAPS:-slithery_fight}
for cfg in "$@"; do
  tag=$(echo "$cfg" | tr -d ' -' | tr '=' '_'); [ -z "$tag" ] && tag=base
  mkdir -p $S/abl/$tag/lesson
  python3 notes/pocket_factory/mech.py "$L $cfg" --base variants/v31 --maps $MAPS --seeds ${SEEDS:-3} --seed-base 8000 --jobs 3 --keep $S/abl/$tag > $S/abl/$tag.txt 2>&1
  for mp in ${MAPS//,/ }; do
    args=""; for f in $S/abl/$tag/${mp}_*_A.replay; do args="$args $f:A"; done; for f in $S/abl/$tag/${mp}_*_B.replay; do args="$args $f:B"; done
    echo "== $tag $mp $(grep "^$mp .*cand" $S/abl/$tag.txt)"
    python3 notes/slithery_pockets/entries2.py $args | head -3
  done
done
echo ABL_DONE
