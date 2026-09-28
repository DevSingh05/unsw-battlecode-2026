#!/usr/bin/env python3
"""Run a command while sampling CPU (user/sys/idle), load, process count and thermal state.

usage: cpuwatch.py [--every 15] -- <command...>
"""
import re
import subprocess
import sys
import threading
import time


def sample():
    top = subprocess.run(["top", "-l", "1", "-n", "0"], capture_output=True, text=True).stdout
    cpu = re.search(r"CPU usage: ([\d.]+)% user, ([\d.]+)% sys, ([\d.]+)% idle", top)
    load = re.search(r"Load Avg: ([\d.]+)", top)
    procs = re.search(r"Processes: (\d+) total", top)
    therm = subprocess.run(["pmset", "-g", "therm"], capture_output=True, text=True).stdout
    speed = re.search(r"CPU_Speed_Limit\s*=\s*(\d+)", therm)
    warn = "warning" if re.search(r"(thermal|performance) warning level", therm, re.I) and "No " not in therm else "ok"
    return (float(cpu.group(1)), float(cpu.group(2)), float(cpu.group(3)), float(load.group(1)),
            int(procs.group(1)), speed.group(1) if speed else "100", warn)


def main():
    every = 15
    args = sys.argv[1:]
    if args[:1] == ["--every"]:
        every, args = int(args[1]), args[2:]
    if args[:1] == ["--"]:
        args = args[1:]
    samples, done = [], threading.Event()

    def loop():
        while not done.is_set():
            samples.append(sample())
            done.wait(every)

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    p = subprocess.run(args, capture_output=True, text=True)
    done.set()
    t.join()
    sys.stdout.write(p.stdout[-3000:])
    if samples:
        u = [s[0] for s in samples]; sy = [s[1] for s in samples]; ld = [s[3] for s in samples]; pr = [s[4] for s in samples]
        print(f"CPU samples={len(samples)}  user avg {sum(u)/len(u):.0f}% max {max(u):.0f}%  sys avg {sum(sy)/len(sy):.0f}% max {max(sy):.0f}%"
              f"  load max {max(ld):.1f}  procs max {max(pr)}  cpu speed limit min {min(s[5] for s in samples)}%  thermal {set(s[6] for s in samples)}")


if __name__ == "__main__":
    main()
