"""`uv run fabpilot-datasets {status,secom,wm811k}` - fetch public datasets."""

from __future__ import annotations

import argparse
import sys

from fabpilot.datasets.download import download_secom, download_wm811k
from fabpilot.datasets.registry import DATASETS


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["status", "secom", "wm811k", "all"])
    parser.add_argument("--force", action="store_true", help="re-download even if present")
    args = parser.parse_args(argv)

    if args.action == "status":
        for d in DATASETS.values():
            mark = "present" if d.is_present() else "missing"
            print(f"{d.key:<8} {mark:<8} {d.path}  ({d.license}; {d.homepage})")
        return
    try:
        if args.action in ("secom", "all"):
            print(f"secom  -> {download_secom(args.force).path}")
        if args.action in ("wm811k", "all"):
            print(f"wm811k -> {download_wm811k(args.force).path}")
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
