"""CLI bootstrap. `crmp run` starts the engine, `crmp list` dumps profiles."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from crmp.config.loader import ProfileStore
from crmp.engine.dispatcher import InputDispatcher
from crmp.engine.watcher import ForegroundWatcher
from crmp.utils.logging import configure_logging


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="crmp", description="Per-game controller remapper.")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--profiles", type=Path, default=Path("profiles"))
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run", help="Run the remap engine.")
    sub.add_parser("list", help="List loaded profiles.")
    sub.add_parser("validate", help="Validate every profile on disk.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    configure_logging(logging.DEBUG if args.verbose else logging.INFO)
    log = logging.getLogger("crmp")

    store = ProfileStore(args.profiles)
    store.reload()

    if args.cmd == "list":
        for name, prof in store.profiles.items():
            log.info("%-24s -> %s", name, prof.target_summary())
        return 0

    if args.cmd == "validate":
        bad = store.validate_all()
        for name, err in bad.items():
            log.error("profile %s: %s", name, err)
        return 1 if bad else 0

    dispatcher = InputDispatcher(store)
    watcher = ForegroundWatcher(store, dispatcher, poll_hz=4.0)
    try:
        watcher.run_forever()
    except KeyboardInterrupt:
        log.info("engine stopped by user")
    return 0


if __name__ == "__main__":
    sys.exit(main())