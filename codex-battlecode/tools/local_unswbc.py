#!/usr/bin/env python3
"""Run the installed toolkit with caches and error logs in our sandbox."""
import os
import pathlib
import resource
import shutil
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parents[1]
os.environ["UNSWBC_NO_UPDATE"] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["TMPDIR"] = str(HERE / "build")
soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
resource.setrlimit(resource.RLIMIT_NOFILE, (max(soft, min(8192, hard)), hard))

# The toolkit normally deletes build/sandbox temporary directories on exit.
# Preserve them under archive/ to honour this workspace's no-deletion rule.
def archive_temporary(path, *args, **kwargs):
    path = pathlib.Path(path).resolve()
    if not path.exists():
        return
    assert path.is_relative_to(HERE), f"Refusing cleanup outside sandbox: {path}"
    archive = HERE / "archive" / "toolkit-temporaries"
    archive.mkdir(parents=True, exist_ok=True)
    path.rename(archive / (path.name + "-" + str(time.monotonic_ns())))

shutil.rmtree = archive_temporary
from unswbc import errors, sandbox
errors.log_path = lambda: HERE / "results" / "toolkit-errors.log"
sandbox._cache_dir = lambda: HERE / "build" / "toolkit-cache"
from unswbc.cli import main

if __name__ == "__main__":
    # This wrapper is strictly for local matches, never account/server commands.
    assert sys.argv[1:2] == ["run"]
    sys.exit(main())
