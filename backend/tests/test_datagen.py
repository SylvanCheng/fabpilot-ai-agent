from collections import Counter
from datetime import timedelta

import numpy as np

from fabpilot.datagen.generator import COLUMNS, TABLE_ORDER, GeneratorConfig, generate

CFG = GeneratorConfig(lots_per_product=40)
ROWS = generate(CFG)


def test_deterministic():
    again = generate(GeneratorConfig(lots_per_product=40))
    assert all(ROWS[t] == again[t] for t in TABLE_ORDER)


def test_row_shapes_match_columns():
    for t in TABLE_ORDER:
        assert ROWS[t], f"{t} is empty"
        assert all(len(r) == len(COLUMNS[t]) for r in ROWS[t]), t


def test_primary_keys_unique():
    assert len({r[0] for r in ROWS["lot"]}) == len(ROWS["lot"])
    assert len({r[0] for r in ROWS["wafer"]}) == len(ROWS["wafer"])
    assert len({(r[0], r[1]) for r in ROWS["lot_step_history"]}) == len(ROWS["lot_step_history"])


def test_lot_status_mix():
    statuses = Counter(r[7] for r in ROWS["lot"])
    assert statuses["FINISHED"] > 0 and statuses["WIP"] > 0


def _poly_cd_by_tool(after_drift: bool):
    """Mean POLY_CD per etch tool, for lots etched before/after the drift start."""
    drift_start = CFG.end_time - timedelta(days=CFG.drift_days)
    etch = {
        r[0]: (r[2], r[5])
        for r in ROWS["lot_step_history"]
        if r[1].endswith("-0130")  # POLY ETCH is seq 130 in the route template
    }
    vals: dict[str, list[float]] = {}
    for wafer_id, _step, param, _site, value, _t in ROWS["measurement"]:
        if param != "POLY_CD":
            continue
        tool, t_in = etch[wafer_id.split(".")[0]]
        if (t_in > drift_start) == after_drift:
            vals.setdefault(tool, []).append(value)
    return {k: float(np.mean(v)) for k, v in vals.items()}


def test_etch_drift_scenario_visible():
    after = _poly_cd_by_tool(after_drift=True)
    others = [v for k, v in after.items() if k != "ETCH-03"]
    assert after["ETCH-03"] > max(others) + 1.5


def test_drift_lots_have_lower_yield_and_edge_ring():
    edge_ring = [r for r in ROWS["wafer_yield"] if r[4] == "Edge-Ring"]
    normal = [float(r[3]) for r in ROWS["wafer_yield"] if r[4] == "none"]
    assert edge_ring
    assert np.mean([float(r[3]) for r in edge_ring]) < np.mean(normal)
