#!/usr/bin/env python3
"""Summarize judge outcomes and stream replay events without storing all events."""
import collections
import gzip
import json
import pathlib
import re
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / "notes" / "tools"))
import replay_decode as R


def replay_metrics(path):
    raw = pathlib.Path(path).read_bytes()
    if raw[:2] == b"\x1f\x8b": raw = gzip.decompress(raw)
    message = R.Msg(R.unpack(raw))
    root = R.S(message, message.resolve(0, 0))
    version = root.data("I", 0)
    text = root.text(0)
    teams = {}
    starts = collections.Counter()
    for line in text.splitlines():
        f = line.split()
        if f and f[0] == "DRAGON":
            team = "AB"[int(f[1])]
            teams[len(teams)] = team
            starts[team] += 1
    # Inline composite list, using the same layout as the team's decoder.
    _, segment, start, element_size, _ = root.ptr(3)
    assert element_size == 7
    tag = message.word(segment, start)
    count, data_words, pointers = tag >> 2 & 0x3fffffff, tag >> 32 & 0xffff, tag >> 48
    actor, round_num = None, -1
    eats = collections.Counter()
    deaths = {"A": collections.Counter(), "B": collections.Counter()}
    errors, first_actions, first_deaths = [], [], []
    for i in range(count):
        event = R.ev(R.S(message, ("s", segment, start + 1 + i * (data_words + pointers), data_words, pointers)), version)
        kind = event["t"]
        if kind == "roundStart": round_num, actor = event["round"], None
        elif kind == "turnStart": actor = event["id"]
        elif kind == "dragonSplit": teams[event["child"]] = event["team"]
        elif kind == "tileChange" and not event["hasPearl"] and actor in teams: eats[teams[actor]] += 1
        elif kind == "dragonAction":
            if len(first_actions) < 12:
                first_actions.append(dict(round=round_num, id=event["id"], team=teams.get(event["id"]), action=event["action"]))
            if event.get("tle"):
                errors.append(dict(round=round_num, id=event["id"], team=teams.get(event["id"]), error="time limit"))
        elif kind == "dragonDeath":
            team = teams[event["id"]]
            deaths[team][event["reason"]] += 1
            if len(first_deaths) < 12:
                first_deaths.append(dict(round=round_num, team=team, **event))
            if event["reason"] == "NoValidAction":
                errors.append(dict(round=round_num, team=team, **event))
    result = root.struct(4)
    def stats(s):
        return dict(dragons=s.data("i", 0), longest=s.data("i", 4), total=s.data("i", 8))
    return dict(rounds=round_num + 1, starts=dict(starts), eats=dict(eats), deaths=deaths,
                errors=errors, first_actions=first_actions, first_deaths=first_deaths,
                final={"A": stats(result.struct(0)), "B": stats(result.struct(1))})


def main():
    source, output = map(pathlib.Path, sys.argv[1:3])
    assert output.resolve().is_relative_to(HERE)
    assert not output.exists()
    rows = []
    for line in source.read_text().splitlines():
        row = json.loads(line)
        item = {k: row[k] for k in ("map", "seed", "side", "opponent", "returncode", "replay")}
        item["cpu"] = [line for line in row["output"].splitlines() if "points per turn:" in line]
        item["runtime_messages"] = [line for line in row["output"].splitlines()
                                    if re.search(r"error:|no valid action|timeout|budget|trap|out of bounds", line, re.I)]
        if row["replay"] and pathlib.Path(row["replay"]).exists():
            item["metrics"] = replay_metrics(row["replay"])
        rows.append(item)
        print(pathlib.Path(item["map"]).stem, item["side"], "errors", len(item.get("metrics", {}).get("errors", [])), flush=True)
    output.write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    main()
