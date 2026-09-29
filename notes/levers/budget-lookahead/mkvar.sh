#!/bin/sh
# usage: mkvar.sh <name> "FLAG=V FLAG2=V" -> builds/<name>/ = src/bot with the flags baked into params.hpp
set -e
cd "$(dirname "$0")"
mkdir -p builds
if [ -d "builds/$1.tmp" ]; then mkdir -p ../../../archive/levers_builds; mv "builds/$1.tmp" "../../../archive/levers_builds/$1.tmp.$(date +%s)"; fi; cp -R src/bot "builds/$1.tmp"
{ for kv in $2; do echo "#define ${kv%%=*} ${kv#*=}"; done; cat src/bot/params.hpp; } > "builds/$1.tmp/params.hpp"
if [ -d "builds/$1" ]; then mkdir -p ../../../archive/levers_builds; mv "builds/$1" "../../../archive/levers_builds/$1.$(date +%s)"; fi
mv "builds/$1.tmp" "builds/$1"
