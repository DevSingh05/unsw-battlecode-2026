#!/usr/bin/env python3
"""Compatibility entry point visible to the team's documented pool.py process check."""
import pathlib
import runpy

runpy.run_path(str(pathlib.Path(__file__).with_name("evaluate.py")), run_name="__main__")
