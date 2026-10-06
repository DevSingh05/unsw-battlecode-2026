#!/usr/bin/env python3
"""Decision replay for SERVER games: rebuild the exact stdin one of our dragons received on the judge, feed it
to a fresh build of the bot, and show what the bot says (and why) on any round.

How the input is rebuilt (exact, not an approximation):
  The server replay holds the map, the match seed and every dragon's action and sonar pings. We run the real
  engine (the toolkit's unswbc_engine.wasm, same code the judge runs) with the replay's seed and a puppet for
  EVERY dragon (both teams) that answers each turn with exactly the action + sonars recorded on the server. The
  engine then produces, byte for byte, the init block and every round block (vision, pearl countdowns, bodies,
  edges, sonar inbox, ECHOES) the dragon got on the server. The rebuilt game is checked event-by-event against
  the server replay (moves, deaths, splits, pearl spawns); any divergence is reported.

Bot engines:
  sandbox  (default) the bot built to wasm with the judge's clang, run in the toolkit's judge sandbox: CPU-point
           clock (budget cutoffs), memory and RNG as on the server. Exact reproduction.
  native   clang++ -O2 build on this Mac. Fast; supports --debug (the bot's own BOTDBG trace: per-candidate
           scores, vetoes, chosen move). Its clock is wall time, so budget-limited searches can differ.

usage (run from the project root; the script re-runs itself under the toolkit's Python, which has wasmtime):
  python3 tools/decision_replay.py show 1166037 --dragon 1 --round 120              # round input + bot reply
  python3 tools/decision_replay.py show 1166037 --dragon 1 --round 120 --debug      # + candidate scores (native)
  python3 tools/decision_replay.py show 1166037 --dragon 1 --round 120 --input      # + raw protocol block
  python3 tools/decision_replay.py verify 1166037 --dragons all                     # fidelity: bot vs server moves
  python3 tools/decision_replay.py dump 1166037 --dragon 1 --upto 120 -o d1.txt     # raw stdin stream to a file
  python3 tools/decision_replay.py check 1166037                                    # rebuilt game == server game?
common options:
  GAME is a game id (replay looked up in replays/**/<id>.replay, else downloaded from the public endpoint) or a
  .replay path.   --side A|B  our team (default: from replays/ab_server/games.json, team 952)
  --src DIR       bot source dir (default bot/)    --sub NAME|ID  use our server submission's exact zip instead
                  (downloaded once to replays/decision_replay/subs/<id>/; NAME = latest upload with that name)
  -D FLAG=V       extra compile-time defines (repeatable)       --engine sandbox|native
  --topn N        with --debug: how many candidate lines to show (sorted by score), default 6
Caches: rebuilt input streams in replays/decision_replay/<gameId>/streams.pkl.gz; builds in the scratch dir
($DR_BUILD, default /private/tmp/.../scratchpad/dgu/harness/build).
"""
import argparse
import gzip
import hashlib
import json
import os
import pathlib
import pickle
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLKIT_PY = pathlib.Path.home() / ".local/share/uv/tools/unswbc/bin/python"

try:
    import wasmtime  # noqa: F401
except ImportError:
    if TOOLKIT_PY.exists() and os.environ.get("DR_REEXEC") != "1":
        os.environ["DR_REEXEC"] = "1"
        os.execv(str(TOOLKIT_PY), [str(TOOLKIT_PY), __file__, *sys.argv[1:]])
    sys.exit("decision_replay: needs the unswbc toolkit's Python (wasmtime); not found at " + str(TOOLKIT_PY))

sys.path.insert(0, str(ROOT / "notes" / "tools"))
sys.path.insert(0, str(ROOT / "tools"))
import replay_decode as RD  # noqa: E402

CACHE = ROOT / "replays" / "decision_replay"
BUILD = pathlib.Path(os.environ.get(
    "DR_BUILD",
    "/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/"
    "scratchpad/dgu/harness/build"))
OUR_TEAM_ID = 952
STREAM_VER = 5


# ------------------------------------------------------------------ replay loading
def find_replay(game):
    p = pathlib.Path(game)
    if p.suffix == ".replay" and p.is_file():
        return p, (int(p.stem) if p.stem.isdigit() else None)
    gid = int(game)
    for q in (ROOT / "replays").rglob(f"{gid}.replay"):
        return q, gid
    out = CACHE / str(gid) / f"{gid}.replay"
    out.parent.mkdir(parents=True, exist_ok=True)
    import api
    for attempt in range(5):
        try:
            api.download_replay(gid, out)
            return out, gid
        except Exception as e:  # 429 etc.
            if "429" in str(e):
                time.sleep(30)
                continue
            raise
    raise SystemExit(f"could not download replay {gid}")


def our_side(gid, override):
    if override:
        return override.upper()
    if gid is not None:
        for f in (ROOT / "replays" / "ab_server" / "games.json",):
            try:
                g = json.loads(f.read_text())["games"].get(str(gid))
            except Exception:
                g = None
            if g:
                if g["a"]["id"] == OUR_TEAM_ID:
                    return "A"
                if g["b"]["id"] == OUR_TEAM_ID:
                    return "B"
        # ab_server --json style lists
        for f in ROOT.glob("replays/ab_mech/*/rows.json"):
            try:
                rows = json.loads(f.read_text())
            except Exception:
                continue
            it = rows.values() if isinstance(rows, dict) else rows
            for r in it:
                if isinstance(r, dict) and str(r.get("id", r.get("game"))) == str(gid) and r.get("side"):
                    return r["side"]
    raise SystemExit("cannot tell our side for this game; pass --side A|B")


def server_script(o):
    """(id, round) -> {'act': action dict or None, 'tle': bool, 'sonar': [(dir, value)]} from the server replay."""
    # The replay's sonarPing 'dir' is the direction the ray travelled: a ray requested opposite the facing leaves
    # from the tail along the tail's outward direction (engine sonar.cc). Recover the requested direction from
    # the origin: head -> as recorded; tail -> opposite of the sender's facing.
    opp = {"N": "S", "S": "N", "E": "W", "W": "E"}
    head, facing = {}, {}
    sc = {}
    rnd = 0
    for e in o["events"]:
        t = e["t"]
        if t == "roundStart":
            rnd = e["round"]
        elif t == "dragonAction":
            sc[(e["id"], rnd)] = {"act": e["action"], "tle": bool(e["tle"]), "sonar": []}
        elif t == "dragonUpdate":
            head[e["id"]], facing[e["id"]] = e["head"], e["facing"]
        elif t == "dragonSplit":
            head[e["parent"]] = e["parentBody"][0]
            head[e["child"]], facing[e["child"]] = e["childBody"][0], e["childFacing"]
        elif t == "sonarPing":
            s = e["sender"]
            k = (s, rnd)
            if k in sc:
                d = e["dir"] if e["origin"] == head.get(s) else opp[facing[s]]
                sc[k]["sonar"].append((d, e["value"]))
    return sc


def reply_text(s):
    a = s["act"]
    if s["tle"] or a is None or "suicide" in a:
        return b""
    out = []
    if "move" in a:
        out.append("MOVE " + "".join(a["move"]))
    elif "split" in a:
        out.append(f"SPLIT {a['split']}")
    for d, v in s["sonar"]:
        out.append(f"SONAR {d} {v}")
    out += ["PROTOCOL 3", "ENDTURN", ""]
    return "\n".join(out).encode()


def act_str(a):
    if a is None or "suicide" in a:
        return "SUICIDE"
    if "move" in a:
        return "MOVE " + "".join(a["move"])
    return f"SPLIT {a['split']}"


# ------------------------------------------------------------------ rebuild the game with puppets
def compare_events(srv, loc):
    keep = ("dragonAction", "dragonUpdate", "dragonSplit", "dragonDeath", "tileChange", "roundStart", "sonarPing")

    def norm(evs):
        out = []
        for e in evs:
            if e["t"] not in keep:
                continue
            e = dict(e)
            e.pop("instr", None)
            e.pop("tle", None)
            out.append(e)
        return out
    a, b = norm(srv), norm(loc)
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            rnd = max((x["round"] for x in a[:i] if x["t"] == "roundStart"), default=0)
            return f"first divergence at event {i} (round {rnd}): server {a[i]} vs rebuilt {b[i]}"
    if len(a) != len(b):
        return f"event count differs: server {len(a)} vs rebuilt {len(b)}"
    return None


def engine_map(o):
    """The replay's map text carries the real geometry (edges, starts, the game's team order) but every TILE
    spawn gap is zeroed. Take the pearl gaps from a local map file with the same MAP_NAME and size:
    maps/server_live/, maps/, and the fitted alternate layouts in replays/decision_replay/maps/ (the server
    runs two layouts for some maps, see tools/pearl_infer.py). Each candidate is checked by emulating the pearl
    tick against this game (exact, ~0.1 s): the first one that reproduces every tick spawn wins, else the one
    that holds longest."""
    import pearl_infer as PI
    rt = o["map"]
    rl = [ln.strip() for ln in rt.split("\n") if ln.strip()]
    name = next((ln[9:].strip() for ln in rl if ln.startswith("MAP_NAME ")), None)
    size = next((ln for ln in rl if ln.startswith("MAP ")), None)
    if any(ln.startswith("TILE ") and ln.split()[4] != "0" for ln in rl):
        return rt.encode(), "replay map (has spawn gaps)"
    obs = None
    best = None
    files = (sorted((ROOT / "maps" / "server_live").glob("*.map")) + sorted((ROOT / "maps").glob("*.map"))
             + sorted((CACHE / "maps").glob("*.map")))
    tried = set()
    for f in files:
        ml = [ln.strip() for ln in f.read_text().split("\n") if ln.strip()]
        if f"MAP_NAME {name}" not in ml or size not in ml:
            continue
        tiles = {tuple(ln.split()[1:3]): ln for ln in ml if ln.startswith("TILE ")}
        key = tuple(sorted(tiles.values()))
        if key in tried:
            continue
        tried.add(key)
        out = [tiles.get(tuple(ln.split()[1:3]), ln) if ln.startswith("TILE ") else ln for ln in rl]
        text = "\n".join(out) + "\n"
        if obs is None:
            obs = PI.observed(o)
        W, H, sym, beds = PI.parse_map(text)
        r, _ = PI.emulate(W, H, sym, beds, PI.MT64(o["seed"] or 0), obs)
        src = str(f.relative_to(ROOT))
        if r is None:
            return text.encode(), src
        if best is None or r > best[0]:
            best = (r, text.encode(), src)
    if best is None:
        print(f"WARNING: no local map file named {name!r}: pearls will never spawn in the rebuild", file=sys.stderr)
        return rt.encode(), "replay map (NO spawn gaps)"
    print(f"WARNING: no known pearl layout of {name!r} reproduces this game (best: {best[2]}, holds to round "
          f"{best[0]}); fit one with: python3 tools/pearl_infer.py --auto --base maps/server_live/<map>.map",
          file=sys.stderr)
    return best[1], best[2] + f" (pearls diverge from r{best[0]})"


def rebuild(o, record=lambda team, did: True):
    from unswbc.engine import EngineModule
    sc = server_script(o)
    rnd_of = {}
    streams = {}  # id -> {'team','init','blocks':[(round, bytes)]}
    teams = {}

    def spawn(did, init):
        team = re.search(rb"TEAM (\w)", init).group(1).decode()
        teams[did] = team
        if record(team, did):
            streams[did] = {"team": team, "init": init, "blocks": []}

    def reply(did, block):
        m = re.match(rb"ROUND (\d+)", block)
        r = int(m.group(1)) if m else -1
        if did in streams:
            streams[did]["blocks"].append((r, block))
        s = sc.get((did, r))
        if s is None:
            return b""
        return reply_text(s)

    eng = EngineModule()
    seed = o["seed"] or 0
    mtext, msrc = engine_map(o)
    res = eng.run(mtext, reply, None, spawn, lambda line: None, 0, seed)
    blob = eng.replay("A", "B")
    with tempfile.NamedTemporaryFile(suffix=".replay", delete=False) as f:
        f.write(blob)
        tmp = f.name
    loc = RD.load(tmp)
    os.unlink(tmp)
    diff = compare_events(o["events"], loc["events"])
    return {"streams": streams, "teams": teams, "diff": diff, "winner": res.winner, "rounds": res.rounds,
            "map_source": msrc}


def get_streams(path, gid, o):
    key = hashlib.sha1(path.read_bytes()).hexdigest()[:12]
    cdir = CACHE / str(gid if gid is not None else path.stem)
    cf = cdir / "streams.pkl.gz"
    if cf.is_file():
        with gzip.open(cf, "rb") as f:
            d = pickle.load(f)
        if d.get("ver") == STREAM_VER and d.get("key") == key:
            return d
    t0 = time.time()
    d = rebuild(o)
    d["ver"], d["key"] = STREAM_VER, key
    cdir.mkdir(parents=True, exist_ok=True)
    with gzip.open(cf, "wb", compresslevel=6) as f:
        pickle.dump(d, f)
    print(f"[rebuilt game with the engine in {time.time() - t0:.1f}s; "
          f"{'IDENTICAL to server replay' if d['diff'] is None else 'DIVERGES: ' + d['diff']}]", file=sys.stderr)
    return d


def payload(block):
    # unswbc/turn.py payload(): a block that does not end in a blank line gets one newline
    return block + (b"" if block.endswith(b"\n\n") else b"\n")


def stream_bytes(st, upto=None):
    out = bytearray()
    first = True
    for r, b in st["blocks"]:
        if upto is not None and r > upto:
            break
        out += payload((st["init"] if first else b"") + b)
        first = False
    return bytes(out)


# ------------------------------------------------------------------ bot sources and builds
def sub_source(sel):
    import api
    import urllib.error
    import urllib.request
    if str(sel).isdigit() and (CACHE / "subs" / str(sel) / "main.cpp").is_file():
        return CACHE / "subs" / str(sel)
    names = CACHE / "subs" / "names.json"
    try:
        nm = json.loads(names.read_text())
    except Exception:
        nm = {}
    if sel in nm and (CACHE / "subs" / str(nm[sel]) / "main.cpp").is_file():
        return CACHE / "subs" / str(nm[sel])
    subs = api.get("/api/v1/submissions")
    subs = subs if isinstance(subs, list) else subs.get("submissions", subs)
    pick = None
    for s in subs:  # newest first
        if str(s["id"]) == str(sel) or s.get("name") == sel:
            pick = s
            break
    if pick is None:
        raise SystemExit(f"no submission named/id {sel}")
    d = CACHE / "subs" / str(pick["id"])
    if not str(sel).isdigit():
        nm[sel] = pick["id"]
        names.parent.mkdir(parents=True, exist_ok=True)
        names.write_text(json.dumps(nm))
    if (d / "main.cpp").is_file():
        return d
    d.mkdir(parents=True, exist_ok=True)

    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    req = urllib.request.Request(api.BASE + f"/api/v1/submissions/{pick['id']}/download",
                                 headers={"Authorization": "Bearer " + api.key(), **api.UA})
    time.sleep(1.5)
    try:
        data = urllib.request.build_opener(NoRedir).open(req, timeout=60).read()
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location")
        if not loc:
            raise
        data = urllib.request.urlopen(urllib.request.Request(loc, headers=api.UA), timeout=60).read()
    z = d / "sub.zip"
    z.write_bytes(data)
    import zipfile
    zipfile.ZipFile(z).extractall(d)
    print(f"[submission {pick['name']} id {pick['id']} -> {d}]", file=sys.stderr)
    return d


def stage_source(src, defines):
    """Copy the bot to a build dir with -D defines prepended to main.cpp (the sandbox build has no -D)."""
    src = pathlib.Path(src).resolve()
    files = sorted(p for p in src.rglob("*") if p.is_file() and p.suffix in (".cpp", ".hpp", ".h", ".cc", ".c", ".toml")
                   and ".unswbc-build" not in p.parts)
    h = hashlib.sha1()
    for p in files:
        h.update(str(p.relative_to(src)).encode())
        h.update(p.read_bytes())
    h.update(repr(sorted(defines)).encode())
    tag = h.hexdigest()[:14]
    d = BUILD / f"src-{tag}"
    if not (d / "main.cpp").is_file():
        tmp = BUILD / f"src-{tag}.tmp{os.getpid()}"
        shutil.rmtree(tmp, ignore_errors=True)
        for p in files:
            q = tmp / p.relative_to(src)
            q.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, q)
        if defines:
            m = tmp / "main.cpp"
            pre = "".join(f"#define {k} {v}\n" for k, v in defines)
            m.write_text(pre + m.read_text())
        tmp.rename(d)
    return d, tag


def build_native(src, defines):
    d, tag = stage_source(src, defines)
    exe = BUILD / f"native-{tag}"
    if not exe.is_file():
        r = subprocess.run(["clang++", "-std=c++20", "-O2", "-I", str(d), "-o", str(exe), str(d / "main.cpp")],
                           capture_output=True, text=True)
        if r.returncode:
            raise SystemExit("native build failed:\n" + r.stderr[-3000:])
    return exe


def build_wasm(src, defines):
    d, tag = stage_source(src, defines)
    from unswbc import clangtool
    return clangtool.build(d)


# ------------------------------------------------------------------ running the bot
def split_replies(out):
    reps = []
    cur = []
    for line in out.decode(errors="replace").split("\n"):
        line = line.rstrip("\r")
        if line == "ENDTURN":
            reps.append("\n".join(cur))
            cur = []
        else:
            cur.append(line)
    return reps


def parse_reply(text):
    act, sonar, other = None, {}, []
    for line in text.split("\n"):
        f = line.split()
        if not f:
            continue
        if f[0] == "MOVE" and len(f) == 2 and re.fullmatch(r"[NESW]+", f[1]):
            act = {"move": list(f[1])}
        elif f[0] == "SPLIT" and len(f) == 2:
            act = {"split": int(f[1])}
        elif f[0] == "SONAR" and len(f) == 3:
            sonar[f[1]] = int(f[2])
        elif f[0] != "PROTOCOL":
            other.append(line)
    return act, sonar, other


def run_native(exe, st, upto=None, debug_dir=None):
    env = dict(os.environ)
    if debug_dir:
        env["BOTDBG"] = str(debug_dir)
    data = stream_bytes(st, upto)
    r = subprocess.run([str(exe)], input=data, capture_output=True, env=env, timeout=600)
    reps = split_replies(r.stdout)
    rounds = [rr for rr, _ in st["blocks"] if upto is None or rr <= upto]
    return [(rounds[i], reps[i] if i < len(reps) else None, None) for i in range(len(rounds))]


def _debug_pool(wasm, key, dbg_dir):
    """A WasmPool whose bots see BOTDBG=/dbg (a writable mount of dbg_dir). Writes to that file are not charged
    CPU points (stdout still is), so the bot's own trace costs only its in-wasm formatting work."""
    import threading
    from unswbc.sandbox import Rng, Sandbox, WasmPool, _drive, _Pipe

    class DebugPool(WasmPool):
        def _boot(self):
            cv = threading.Condition()
            stdin, stdout = _Pipe(cv), _Pipe(cv)
            try:
                box = Sandbox(wasm_path=self.wasm, root=self.root, argv=["bot"], environ=["TERM=dumb", "BOTDBG=/dbg"],
                              mounts={"/dbg": pathlib.Path(dbg_dir)}, writable=("/dbg",),
                              stderr=bytearray(), stdin=stdin, stdout=stdout, needs_zygote=False)
                w = "wasi_snapshot_preview1."
                for k in (w + "fd_write", w + "fd_pwrite"):
                    orig = box._impl[k]

                    def free(*args, _orig=orig, _box=box):
                        node = _box._fds.get(args[0])
                        if node is not None and getattr(node, "handle", None) is not None:
                            saved = _box.charge_write
                            _box.charge_write = lambda total: None
                            try:
                                return _orig(*args)
                            finally:
                                _box.charge_write = saved
                        return _orig(*args)
                    box._impl[k] = free
                box.rng = Rng(self.key, "")
                box.instantiate()
            except BaseException as e:  # noqa: BLE001
                print("debug sandbox failed:", e, file=sys.stderr)
                self._offer(None)
                return
            threading.Thread(target=_drive, args=(box, stdout, None), daemon=True).start()
            self._offer((box, stdin, stdout, False))
    return DebugPool([str(wasm)], key=key)


def run_sandbox(wasm, st, seed, did, upto=None, debug_dir=None):
    from unswbc.sandbox import SandboxBot, WasmPool
    key = f"{seed:016x}-{st['team'].lower()}"
    pool = _debug_pool(wasm, key, debug_dir) if debug_dir else WasmPool([str(wasm)], key=key)
    try:
        bot = SandboxBot(pool, init=st["init"], name=str(did))
        res = []
        for r, b in st["blocks"]:
            if upto is not None and r > upto:
                break
            out = bot.ask(b)
            pts = bot.live[0] if bot.error is None else None
            txt = out.decode(errors="replace")
            res.append((r, txt if bot.error is None else None, pts if bot.error is None else bot.error))
        bot.stop()
        # warm spare instances wake on close, read EOF as their init and fopen("<id>.txt", "w"): keep a copy
        snap = {f: f.read_bytes() for f in pathlib.Path(debug_dir).glob("*.txt")} if debug_dir else {}
    finally:
        pool.close()
    time.sleep(0.2 if debug_dir else 0)
    for f, data in snap.items():
        f.write_bytes(data)
    return res


# ------------------------------------------------------------------ commands
def load_game(args):
    path, gid = find_replay(args.game)
    o = RD.load(str(path))
    side = our_side(gid, args.side)
    d = get_streams(path, gid, o)
    if getattr(args, "dragon", None) is not None and not isinstance(args.dragon, int):
        if str(args.dragon).lower() in ("q", "queen"):
            args.dragon = next(i for i in (0, 1) if d["streams"].get(i, {}).get("team") == side)
        else:
            args.dragon = int(args.dragon)
    return path, gid, o, side, d


def bot_source(args):
    return sub_source(args.sub) if args.sub else pathlib.Path(args.src)


def defines_of(args):
    out = []
    for x in args.D or []:
        k, _, v = x.partition("=")
        out.append((k, v or "1"))
    return out


def debug_section(dbgfile, rnd, topn):
    if not dbgfile.is_file():
        return ["(no debug file)"], []
    lines = dbgfile.read_text(errors="replace").split("\n")
    sec, on = [], False
    for ln in lines:
        if re.match(r"R\d+ id=", ln):
            on = ln.startswith(f"R{rnd} ")
        if on:
            sec.append(ln)
    cands = [ln for ln in sec if ln.strip().startswith("cand ")]
    rest = [ln for ln in sec if not ln.strip().startswith("cand ") and not ln.strip().startswith("seg ")]

    def sc(ln):
        m = re.search(r"score=(-?[\d.e+]+)", ln)
        return float(m.group(1)) if m else -1e18
    cands.sort(key=sc, reverse=True)
    segs = [ln for ln in sec if ln.strip().startswith("seg ")]
    out = rest[:1] + [f"  ({len(segs)} body segments in view; --segs to list)"] if segs else rest[:1]
    out += [f"  top {min(topn, len(cands))}/{len(cands)} candidates by score:"] + cands[:topn]
    out += rest[1:]
    return out, segs


def map_name(o):
    return next((ln[9:].strip() for ln in o["map"].split("\n") if ln.startswith("MAP_NAME ")), "?")


def cmd_check(args):
    path, gid, o, side, d = load_game(args)
    print(f"game {gid} map {map_name(o)} seed {o['seed']} our side {side}; pearl gaps from {d.get('map_source')}")
    print("rebuilt game vs server replay:", "IDENTICAL" if d["diff"] is None else d["diff"])
    ours = [(i, s) for i, s in sorted(d["streams"].items()) if s["team"] == side and s["blocks"]]
    print(f"our dragons with turns ({len(ours)}):",
          " ".join(f"{i}[r{s['blocks'][0][0]}-{s['blocks'][-1][0]}]" for i, s in ours))


def cmd_dump(args):
    path, gid, o, side, d = load_game(args)
    st = d["streams"][args.dragon]
    data = stream_bytes(st, args.upto)
    if args.o:
        pathlib.Path(args.o).write_bytes(data)
        print(f"wrote {len(data)} bytes ({sum(1 for r, _ in st['blocks'] if args.upto is None or r <= args.upto)} turns)"
              f" to {args.o}")
    else:
        sys.stdout.buffer.write(data)


def summarize_block(block):
    t = block.decode().split("\n")
    head = [ln for ln in t[:12] if ln and not ln[0].isdigit()]
    return head


def cmd_show(args):
    path, gid, o, side, d = load_game(args)
    st = d["streams"].get(args.dragon)
    if st is None or not st["blocks"]:
        raise SystemExit(f"dragon {args.dragon} never took a turn in this game")
    if st["team"] != side:
        print(f"note: dragon {args.dragon} is team {st['team']} (not ours, side {side}); replaying it with OUR bot",
              file=sys.stderr)
    sc = server_script(o)
    src = bot_source(args)
    defs = defines_of(args)
    r_to = args.to if args.to is not None else args.round
    rounds = [r for r, _ in st["blocks"] if args.round <= r <= r_to]
    if not rounds:
        raise SystemExit(f"dragon {args.dragon} has no turn in rounds {args.round}..{r_to} "
                         f"(alive r{st['blocks'][0][0]}-r{st['blocks'][-1][0]})")
    print(f"== game {gid} {map_name(o)} ({'input rebuilt IDENTICAL to the server game' if d['diff'] is None else 'REBUILD DIVERGES: ' + d['diff']})")
    print(f"   dragon {args.dragon} team {st['team']} (our side {side})  src {src}"
          f"{'  -D ' + ' '.join(f'{k}={v}' for k, v in defs) if defs else ''}")
    # exact run (sandbox: judge clock, so budget cutoffs match the server) unless --engine native
    if args.engine == "sandbox":
        exact = run_sandbox(build_wasm(src, defs), st, o["seed"] or 0, args.dragon, r_to)
    else:
        exact = run_native(build_native(src, defs), st, r_to)
    exact = {r: (t, p) for r, t, p in exact}
    dbg = {}
    if args.debug:
        ddefs = defs + [("DECISION_DEBUG", "1")]
        ddir = BUILD / f"dbg-{gid}-{args.dragon}-{os.getpid()}"
        ddir.mkdir(parents=True, exist_ok=True)
        if args.engine == "sandbox":
            dres = run_sandbox(build_wasm(src, ddefs), st, o["seed"] or 0, args.dragon, r_to, debug_dir=ddir)
        else:
            dres = run_native(build_native(src, ddefs), st, r_to, ddir)
        dbg = {r: (t, p) for r, t, p in dres}
        dfile = ddir / f"{args.dragon}.txt"
    eng = args.engine
    for rnd in rounds:
        blk = next(b for r, b in st["blocks"] if r == rnd)
        s = sc.get((args.dragon, rnd))
        txt, pts = exact.get(rnd, (None, "no reply"))
        act, son, other = parse_reply(txt or "")
        same = s is not None and act_str(act) == act_str(s["act"])
        print(f"-- round {rnd}: " + " | ".join(summarize_block(blk)))
        if args.input:
            print(blk.decode().rstrip())
        print(f"   server: {act_str(s['act']) if s else '?':<12} bot({eng}): {act_str(act) if txt is not None else 'NO REPLY ' + str(pts):<12}"
              f"[{'MATCH' if same else 'DIFFERENT'}]{'  %.1fM points' % (pts / 1e6) if isinstance(pts, int) else ''}")
        if args.sonar:
            print(f"   sonar server {' '.join(f'{a}:{b}' for a, b in s['sonar']) if s else '-'}  bot "
                  f"{' '.join(f'{k}:{v}' for k, v in son.items())}")
        for ln in other:
            print("   bot> " + ln)
        if args.debug:
            dt, dp = dbg.get(rnd, (None, None))
            dact = parse_reply(dt or "")[0]
            note = "" if act_str(dact) == act_str(act) else f"  (WARNING: debug build chose {act_str(dact)}: trace explains that move)"
            sec, segs = debug_section(dfile, rnd, args.topn)
            print(f"   ---- bot trace (BOTDBG){note}")
            print("\n".join("   " + x for x in sec))
            if args.segs:
                print("\n".join("   " + x for x in segs))


def cmd_verify(args):
    path, gid, o, side, d = load_game(args)
    sc = server_script(o)
    src = bot_source(args)
    defs = defines_of(args)
    ours = sorted(i for i, s in d["streams"].items() if s["team"] == side and s["blocks"])
    if args.dragons != "all":
        ours = [int(x) for x in args.dragons.split(",")]
    runner = None
    if args.engine == "sandbox":
        wasm = build_wasm(src, defs)
        runner = lambda st, did: run_sandbox(wasm, st, o["seed"] or 0, did)  # noqa: E731
    else:
        exe = build_native(src, defs)
        runner = lambda st, did: run_native(exe, st)  # noqa: E731
    tot = ok = son_tot = son_ok = 0
    rows = []
    mism = []
    t0 = time.time()
    for did in ours:
        st = d["streams"][did]
        res = runner(st, did)
        n = m = 0
        for r, txt, pts in res:
            s = sc.get((did, r))
            if s is None:
                continue
            n += 1
            act, son, _ = parse_reply(txt or "")
            if act_str(act) == act_str(s["act"]):
                m += 1
            else:
                mism.append((did, r, act_str(act), act_str(s["act"]), pts))
            if s["sonar"]:
                son_tot += 1
                srv = {a: b for a, b in s["sonar"]}
                son_ok += int(srv == son)
        tot += n
        ok += m
        rows.append((did, n, m))
    print(f"game {gid} side {side} engine {args.engine} src {src}: {len(ours)} dragons, {tot} turns, "
          f"action match {ok}/{tot} = {100.0 * ok / max(1, tot):.2f}%, sonar match {son_ok}/{son_tot}"
          f"  ({time.time() - t0:.0f}s){'' if d['diff'] is None else '  REBUILD DIVERGES: ' + d['diff']}")
    if args.per_dragon:
        for did, n, m in rows:
            print(f"  dragon {did}: {m}/{n}")
    for x in mism[: args.show_mismatch]:
        print(f"  mismatch dragon {x[0]} r{x[1]}: bot {x[2]} vs server {x[3]}  ({x[4]})")
    if args.json:
        js = {"game": gid, "side": side, "engine": args.engine, "turns": tot, "match": ok, "sonar_turns": son_tot,
              "sonar_match": son_ok, "dragons": rows, "mismatches": mism, "rebuild_diff": d["diff"]}
        pathlib.Path(args.json).write_text(json.dumps(js))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("game")
        p.add_argument("--side")
        p.add_argument("--src", default=str(ROOT / "bot"))
        p.add_argument("--sub")
        p.add_argument("-D", action="append")
        p.add_argument("--engine", choices=("sandbox", "native"), default="sandbox")
    p = sub.add_parser("check")
    common(p)
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("dump")
    common(p)
    p.add_argument("--dragon", required=True, help="dragon id, or q = our queen")
    p.add_argument("--upto", type=int)
    p.add_argument("-o")
    p.set_defaults(fn=cmd_dump)
    p = sub.add_parser("show")
    common(p)
    p.add_argument("--dragon", required=True, help="dragon id, or q = our queen")
    p.add_argument("--round", type=int, required=True)
    p.add_argument("--to", type=int, help="show every turn from --round to this round")
    p.add_argument("--sonar", action="store_true")
    p.add_argument("--debug", action="store_true")
    p.add_argument("--input", action="store_true")
    p.add_argument("--segs", action="store_true")
    p.add_argument("--topn", type=int, default=6)
    p.set_defaults(fn=cmd_show)
    p = sub.add_parser("verify")
    common(p)
    p.add_argument("--dragons", default="all")
    p.add_argument("--per-dragon", action="store_true")
    p.add_argument("--show-mismatch", type=int, default=10)
    p.add_argument("--json")
    p.set_defaults(fn=cmd_verify)
    args = ap.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    args.fn(args)


if __name__ == "__main__":
    main()
