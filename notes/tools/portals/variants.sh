#!/bin/zsh
# usage: variants.sh BASEFLAGS SEEDS BASE name1 "flags1" name2 "flags2" ...
SP=/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad
cd $SP
BF=$1; SEEDS=$2; BASE=$3; shift 3
c++ -std=c++20 -O2 ${=BF} -o bins/vbase proto/bot/main.cpp || exit 1
while [ $# -gt 0 ]; do
  n=$1; f=$2; shift 2
  c++ -std=c++20 -O2 ${=BF} ${=f} -o bins/v_$n proto/bot/main.cpp || exit 1
  echo "### $n [$f] vs base [$BF]"
  python3 prun.py $n $SP/bins/v_$n $SP/bins/vbase --seeds $SEEDS --base $BASE 2>&1 | tail -5 | head -3
done
