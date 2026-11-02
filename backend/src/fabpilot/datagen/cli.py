"""`uv run fabpilot-datagen` - generate synthetic fab data into PostgreSQL or CSV."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from fabpilot.datagen.generator import TABLE_ORDER, GeneratorConfig, generate
from fabpilot.datagen.writers import write_csv, write_postgres

DEFAULT_DSN = "postgresql://fab_loader:fab_loader@localhost:5432/fab_business"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--lots-per-product", type=int, default=60)
    parser.add_argument("--days", type=int, default=60)
    target = parser.add_mutually_exclusive_group()
    target.add_argument(
        "--dsn",
        default=os.environ.get("FAB_LOADER_DSN", DEFAULT_DSN),
        help="loader-role DSN (env FAB_LOADER_DSN)",
    )
    target.add_argument("--csv", type=Path, help="write CSV files to this directory instead")
    args = parser.parse_args(argv)

    cfg = GeneratorConfig(seed=args.seed, lots_per_product=args.lots_per_product, days=args.days)
    rows = generate(cfg)
    if args.csv:
        write_csv(rows, args.csv)
        where = str(args.csv)
    else:
        write_postgres(rows, args.dsn)
        where = args.dsn.split("@")[-1]
    for t in TABLE_ORDER:
        print(f"{t:<20} {len(rows[t]):>8}")
    print(f"-> {where}")


if __name__ == "__main__":
    main()
