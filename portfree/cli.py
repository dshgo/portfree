"""Command line entry point."""

from __future__ import annotations

import argparse
import sys

from .core import find, is_free, wait_open, who


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="portfree",
        description="Find free ports, inspect what holds one, wait for one to open.",
    )
    ap.add_argument("port", type=int)
    ap.add_argument("--who", action="store_true", help="show the process holding it")
    ap.add_argument("--wait", action="store_true", help="block until it opens")
    ap.add_argument("--timeout", type=float, default=10.0)
    ap.add_argument("--tries", type=int, default=100)
    args = ap.parse_args(argv)

    if args.who:
        holder = who(args.port)
        if holder is None:
            print(f"nothing listening on {args.port}")
            return 1
        print(holder)
        return 0

    if args.wait:
        try:
            waited = wait_open(args.port, args.timeout)
        except TimeoutError as e:
            print(e, file=sys.stderr)
            return 1
        print(f"{args.port} open after {waited:.1f}s")
        return 0

    if is_free(args.port):
        print(args.port)
        return 0
    try:
        print(find(args.port, tries=args.tries))
    except OSError as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
