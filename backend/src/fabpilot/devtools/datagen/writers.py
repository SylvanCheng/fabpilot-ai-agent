"""Write generated rows to PostgreSQL (COPY) or to CSV files."""

from __future__ import annotations

import csv
from pathlib import Path

import psycopg

from fabpilot.devtools.datagen.generator import COLUMNS, TABLE_ORDER, Rows


def write_csv(rows: Rows, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for table in TABLE_ORDER:
        with (out_dir / f"{table}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(COLUMNS[table])
            w.writerows(rows[table])


def write_postgres(rows: Rows, dsn: str, schema: str = "fab") -> None:
    """Replace all data in `schema` with `rows`. Must connect as the loader role."""
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(
            "TRUNCATE "
            + ", ".join(f"{schema}.{t}" for t in reversed(TABLE_ORDER))
            + " RESTART IDENTITY CASCADE"
        )
        for table in TABLE_ORDER:
            cols = ", ".join(COLUMNS[table])
            with cur.copy(f"COPY {schema}.{table} ({cols}) FROM STDIN") as copy:
                for row in rows[table]:
                    copy.write_row(row)
        conn.commit()
