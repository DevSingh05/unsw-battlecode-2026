#!/bin/zsh
# mkstage.sh <name> [FLAG=VAL ...] : copy of bot/ with defines prepended to params.hpp -> r10/stage/<name>
R6=/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/r11
SRC=/Users/devsingh/Developer/UNSW_Battlecode/bot
n=$1; shift; D=$R6/stage/$n; mkdir -p $D
rsync -a --delete --exclude .unswbc-build --exclude main.cpp.orig --exclude .DS_Store $SRC/ $D/
hdr="// STAGED BUILD $n: $*\n"
for kv in "$@"; do hdr="$hdr#define ${kv%%=*} ${kv#*=}\n"; done
printf "$hdr" | cat - $SRC/params.hpp > $D/params.hpp
touch $D/main.cpp; echo $D
