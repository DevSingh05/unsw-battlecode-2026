#!/bin/bash
# usage: ent_dir.sh DIR map1 map2 ...   (cand is A in *_A.replay, B in *_B.replay)
D=$1; shift
for mp in "$@"; do
  args=(); for f in $D/${mp}_*_A.replay; do args+=("$f:A"); done; for f in $D/${mp}_*_B.replay; do args+=("$f:B"); done
  echo "== $(basename $D) $mp"; python3 notes/slithery_pockets/entries2.py "${args[@]}" 2>&1 | sed -n '1p;3p' | cut -c1-210
done
