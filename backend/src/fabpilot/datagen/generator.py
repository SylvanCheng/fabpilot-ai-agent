"""Deterministic synthetic fab data generator.

Produces plain Python rows per table so the same data can be written to PostgreSQL or CSV.
Two injected scenarios give later phases (agent tools, evals) a known ground truth:

1. ``etch_drift``: ETCH-03 starts drifting ``drift_days`` before ``end_time``. POLY_CD on lots
   etched there climbs towards/over USL, POLY DEFECT INSP counts rise, yield drops with an
   Edge-Ring signature, and ETCH-03 logs more RF alarms.
2. ``cmp_post_pm``: CMP-02 has a PM ``pm_days`` before ``end_time``; the next few lots through
   ILD CMP on CMP-02 show thin ILD (seasoning effect).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

import numpy as np

from fabpilot.datagen.model import (
    EQUIPMENT_FLEET,
    INSPECTION_STEPS,
    MAP_PATTERNS,
    PARAMS,
    PRODUCTS,
    ROUTE_TEMPLATE,
)

# Load order respects foreign keys.
TABLE_ORDER = [
    "product",
    "route",
    "process_step",
    "equipment",
    "lot",
    "wafer",
    "lot_step_history",
    "parameter_spec",
    "measurement",
    "defect_inspection",
    "wafer_yield",
    "equipment_event",
    "lot_hold",
]

COLUMNS: dict[str, list[str]] = {
    "product": ["product_id", "product_name", "technology_node", "wafer_size_mm", "gross_die"],
    "route": ["route_id", "product_id", "version"],
    "process_step": ["step_id", "route_id", "seq", "step_name", "module", "equipment_type"],
    "equipment": ["equipment_id", "equipment_type", "module", "bay", "chamber_count", "status"],
    "lot": [
        "lot_id",
        "product_id",
        "route_id",
        "priority",
        "wafer_qty",
        "start_time",
        "finish_time",
        "status",
    ],
    "wafer": ["wafer_id", "lot_id", "slot_no"],
    "lot_step_history": [
        "lot_id",
        "step_id",
        "equipment_id",
        "chamber",
        "recipe",
        "track_in",
        "track_out",
    ],
    "parameter_spec": ["param_name", "step_id", "unit", "target", "lsl", "usl"],
    "measurement": ["wafer_id", "step_id", "param_name", "site_no", "value", "measured_at"],
    "defect_inspection": ["wafer_id", "step_id", "defect_count", "inspected_at"],
    "wafer_yield": [
        "wafer_id",
        "gross_die",
        "good_die",
        "yield_pct",
        "map_pattern",
        "tested_at",
    ],
    "equipment_event": ["equipment_id", "event_time", "event_type", "code", "message"],
    "lot_hold": [
        "lot_id",
        "step_id",
        "hold_time",
        "release_time",
        "reason_code",
        "comment",
    ],
}

DRIFT_TOOL = "ETCH-03"
PM_TOOL = "CMP-02"


@dataclass
class GeneratorConfig:
    seed: int = 42
    lots_per_product: int = 60
    wafers_per_lot: int = 25
    sampled_wafers: int = 5  # wafers measured per lot at each metrology step
    sites_per_wafer: int = 5
    days: int = 60  # lots are started uniformly over this window
    end_time: datetime = field(default_factory=lambda: datetime(2026, 10, 31, tzinfo=UTC))
    drift_days: int = 21
    drift_max_nm: float = 7.0
    pm_days: int = 12
    post_pm_lots: int = 4


Rows = dict[str, list[tuple]]


def generate(cfg: GeneratorConfig | None = None) -> Rows:
    cfg = cfg or GeneratorConfig()
    return _Generator(cfg).run()


class _Generator:
    def __init__(self, cfg: GeneratorConfig) -> None:
        self.cfg = cfg
        self.rng = np.random.default_rng(cfg.seed)
        self.rows: Rows = {t: [] for t in TABLE_ORDER}
        self.drift_start = cfg.end_time - timedelta(days=cfg.drift_days)
        self.pm_time = cfg.end_time - timedelta(days=cfg.pm_days)
        self.post_pm_seen = 0
        self.tool_offset: dict[tuple[str, str], float] = {}

    # ---------------------------------------------------------------- static master data
    def run(self) -> Rows:
        self._equipment()
        steps_by_route = self._products_routes_steps()
        self._tool_offsets()
        start_span = self.cfg.days * 24 * 3600
        lot_no = 0
        for p in PRODUCTS:
            starts = sorted(
                self.cfg.end_time - timedelta(days=self.cfg.days) + timedelta(seconds=float(s))
                for s in self.rng.uniform(0, start_span, self.cfg.lots_per_product)
            )
            route_id = f"R-{p.route_code}"
            for start in starts:
                lot_no += 1
                self._lot(p, route_id, steps_by_route[route_id], start, lot_no)
        self._equipment_events()
        return self.rows

    def _equipment(self) -> None:
        for bay_no, (eq_type, (module, n)) in enumerate(EQUIPMENT_FLEET.items(), start=1):
            for i in range(1, n + 1):
                chambers = 2 if eq_type in {"ETCH", "CVD", "PVD"} else 1
                self.rows["equipment"].append(
                    (f"{eq_type}-{i:02d}", eq_type, module, f"BAY-{bay_no:02d}", chambers, "UP")
                )

    def _products_routes_steps(self) -> dict[str, list[tuple]]:
        steps_by_route: dict[str, list[tuple]] = {}
        for p in PRODUCTS:
            route_id = f"R-{p.route_code}"
            self.rows["product"].append((p.product_id, p.name, p.node, 300, p.gross_die))
            self.rows["route"].append((route_id, p.product_id, 1))
            steps = []
            for i, st in enumerate(ROUTE_TEMPLATE, start=1):
                seq = i * 10
                module = EQUIPMENT_FLEET[st.equipment_type][0]
                row = (f"{route_id}-{seq:04d}", route_id, seq, st.name, module, st.equipment_type)
                steps.append(row)
                self.rows["process_step"].append(row)
            steps_by_route[route_id] = steps
            step_id_by_name = {s[3]: s[0] for s in steps}
            for prm in PARAMS:
                self.rows["parameter_spec"].append(
                    (
                        prm.name,
                        step_id_by_name[prm.measure_step],
                        prm.unit,
                        prm.target,
                        prm.lsl,
                        prm.usl,
                    )
                )
        return steps_by_route

    def _tool_offsets(self) -> None:
        for prm in PARAMS:
            src_type = next(s.equipment_type for s in ROUTE_TEMPLATE if s.name == prm.source_step)
            for i in range(1, EQUIPMENT_FLEET[src_type][1] + 1):
                self.tool_offset[(prm.name, f"{src_type}-{i:02d}")] = float(
                    self.rng.normal(0, prm.tool_sigma)
                )

    # ---------------------------------------------------------------- lots
    def _lot(self, p, route_id: str, steps: list[tuple], start: datetime, lot_no: int) -> None:
        cfg, rng = self.cfg, self.rng
        lot_id = f"L{start:%y}{p.route_code}{lot_no:04d}"
        wafers = [f"{lot_id}.{s:02d}" for s in range(1, cfg.wafers_per_lot + 1)]
        priority = 1 if rng.random() < 0.05 else 3
        clock = start
        tool_by_step: dict[str, tuple[str, datetime]] = {}
        cd_offset = 0.0
        thin_ild = False
        status = "FINISHED"
        on_hold = False

        for step_id, _route, _seq, name, _module, eq_type in steps:
            queue = timedelta(hours=float(rng.uniform(0.5, 6 if priority > 1 else 1.5)))
            track_in = clock + queue
            if track_in >= cfg.end_time:
                status = "WIP"
                break
            n_tools = EQUIPMENT_FLEET[eq_type][1]
            tool = f"{eq_type}-{int(rng.integers(1, n_tools + 1)):02d}"
            chamber = int(rng.integers(1, 3)) if eq_type in {"ETCH", "CVD", "PVD"} else None
            track_out = track_in + timedelta(hours=float(rng.uniform(1, 4)))
            if track_out >= cfg.end_time:
                self._history(lot_id, step_id, tool, chamber, name, track_in, None)
                status = "WIP"
                break
            self._history(lot_id, step_id, tool, chamber, name, track_in, track_out)
            tool_by_step[name] = (tool, track_in)
            clock = track_out

            # --- scenario hooks on the process step itself
            if name == "POLY ETCH" and tool == DRIFT_TOOL and track_in > self.drift_start:
                frac = (track_in - self.drift_start) / (cfg.end_time - self.drift_start)
                cd_offset = cfg.drift_max_nm * frac
            if (
                name == "ILD CMP"
                and tool == PM_TOOL
                and track_in > self.pm_time
                and self.post_pm_seen < cfg.post_pm_lots
            ):
                self.post_pm_seen += 1
                thin_ild = True

            # --- metrology / inspection
            for prm in (x for x in PARAMS if x.measure_step == name):
                src_tool = tool_by_step[prm.source_step][0]
                extra = 0.0
                if prm.name == "POLY_CD":
                    extra = cd_offset
                elif prm.name == "ILD_THK" and thin_ild:
                    extra = -float(rng.uniform(25, 40))
                lot_mean = self._measure(prm, step_id, src_tool, extra, wafers, track_out)
                if not (prm.lsl <= lot_mean <= prm.usl):
                    hold_h = float(rng.uniform(4, 24))
                    release = track_out + timedelta(hours=hold_h)
                    if release >= cfg.end_time:
                        release, on_hold = None, True
                    self.rows["lot_hold"].append(
                        (
                            lot_id,
                            step_id,
                            track_out,
                            release,
                            "OOS",
                            f"{prm.name} lot mean {lot_mean:.2f} {prm.unit} out of spec",
                        )
                    )
                    if on_hold:
                        status = "HOLD"
                        break
                    clock = release
            if on_hold:
                break

            if name in INSPECTION_STEPS:
                for w in wafers[:: max(1, cfg.wafers_per_lot // cfg.sampled_wafers)]:
                    base = rng.poisson(8)
                    if name == "POLY DEFECT INSP" and cd_offset > 0:
                        base += rng.poisson(6 * cd_offset)
                    self.rows["defect_inspection"].append((w, step_id, int(base), track_out))

        finish = clock if status == "FINISHED" else None
        self.rows["lot"].append(
            (lot_id, p.product_id, route_id, priority, cfg.wafers_per_lot, start, finish, status)
        )
        self.rows["wafer"].extend((w, lot_id, i) for i, w in enumerate(wafers, start=1))
        if status == "FINISHED":
            self._yield(p.gross_die, wafers, cd_offset, thin_ild, clock)

    def _history(self, lot_id, step_id, tool, chamber, name, t_in, t_out) -> None:
        recipe = name.replace(" ", "_") + "_V1"
        self.rows["lot_step_history"].append((lot_id, step_id, tool, chamber, recipe, t_in, t_out))

    def _measure(self, prm, step_id, src_tool, extra, wafers, when) -> float:
        cfg, rng = self.cfg, self.rng
        offset = self.tool_offset[(prm.name, src_tool)] + extra
        values = []
        sampled = wafers[:: max(1, cfg.wafers_per_lot // cfg.sampled_wafers)][: cfg.sampled_wafers]
        for w in sampled:
            wafer_bias = rng.normal(0, prm.sigma * 0.5)
            for site in range(1, cfg.sites_per_wafer + 1):
                v = prm.target + offset + wafer_bias + rng.normal(0, prm.sigma)
                values.append(v)
                self.rows["measurement"].append(
                    (w, step_id, prm.name, site, round(float(v), 3), when)
                )
        return float(np.mean(values))

    def _yield(self, gross_die, wafers, cd_offset, thin_ild, tested_at) -> None:
        rng = self.rng
        for w in wafers:
            y = rng.normal(0.93, 0.02)
            pattern = None
            if cd_offset > 2.0:
                y -= (cd_offset - 2.0) * 0.045
                if rng.random() < min(0.9, cd_offset / 6):
                    pattern = "Edge-Ring"
            if thin_ild:
                y -= rng.uniform(0.03, 0.08)
            if pattern is None and rng.random() < 0.08:
                pattern = str(rng.choice(MAP_PATTERNS))
            if pattern is not None:
                y -= rng.uniform(0.05, 0.25)
            y = float(np.clip(y, 0.0, 1.0))
            good = round(gross_die * y)
            self.rows["wafer_yield"].append(
                (
                    w,
                    gross_die,
                    good,
                    round(100 * good / gross_die, 2),
                    pattern or "none",
                    tested_at + timedelta(hours=12),
                )
            )

    # ---------------------------------------------------------------- equipment events
    def _equipment_events(self) -> None:
        cfg, rng = self.cfg, self.rng
        window_start = cfg.end_time - timedelta(days=cfg.days)
        hours = cfg.days * 24
        for eq in self.rows["equipment"]:
            eq_id = eq[0]
            # Random background alarms.
            for h in sorted(rng.uniform(0, hours, rng.poisson(cfg.days / 6))):
                self.rows["equipment_event"].append(
                    (
                        eq_id,
                        window_start + timedelta(hours=float(h)),
                        "ALARM",
                        "GEN_WARN",
                        "Generic warning, auto-cleared",
                    )
                )
            # One routine PM per tool.
            pm = window_start + timedelta(hours=float(rng.uniform(0, hours - 12)))
            if eq_id == PM_TOOL:
                pm = self.pm_time - timedelta(hours=8)
            self.rows["equipment_event"].append((eq_id, pm, "PM_START", "PM", "Scheduled PM"))
            self.rows["equipment_event"].append(
                (eq_id, pm + timedelta(hours=8), "PM_END", "PM", "PM complete, released")
            )
        # Drift signature: RF alarms ramping up on the drifting etcher.
        drift_hours = cfg.drift_days * 24
        for h in sorted(rng.uniform(0, 1, 40) ** 0.5 * drift_hours):
            self.rows["equipment_event"].append(
                (
                    DRIFT_TOOL,
                    self.drift_start + timedelta(hours=float(h)),
                    "ALARM",
                    "RF_REFLECTED_PWR_HIGH",
                    "Reflected RF power above warning limit",
                )
            )
        self.rows["equipment_event"].sort(key=lambda r: (r[1], r[0]))
