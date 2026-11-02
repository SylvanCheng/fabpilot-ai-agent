"""Loaders for public datasets. P0 provides SECOM parsing; WM-811K is a stub for P3."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import numpy as np

from fabpilot.devtools.datasets.registry import SECOM, WM811K


@dataclass
class SecomData:
    features: np.ndarray  # (1567, 590) float, NaN for missing
    labels: np.ndarray  # (1567,) int, -1 = pass, 1 = fail
    timestamps: list[datetime]


def load_secom() -> SecomData:
    if not SECOM.is_present():
        raise FileNotFoundError(f"SECOM not found in {SECOM.path}; run `fabpilot-datasets secom`")
    features = np.genfromtxt(SECOM.path / "secom.data", delimiter=" ", dtype=float)
    labels, stamps = [], []
    for line in (SECOM.path / "secom_labels.data").read_text().splitlines():
        label, ts = line.split(" ", 1)
        labels.append(int(label))
        stamps.append(datetime.strptime(ts.strip().strip('"'), "%d/%m/%Y %H:%M:%S"))
    return SecomData(features=features, labels=np.array(labels), timestamps=stamps)


def load_wm811k():
    """WM-811K ships as a pickled pandas DataFrame; loading it needs pandas (added in P3)."""
    if not WM811K.is_present():
        raise FileNotFoundError(
            f"WM-811K not found in {WM811K.path}; run `fabpilot-datasets wm811k`"
        )
    raise NotImplementedError("WM-811K loader arrives with the wafer-map tool in P3")
