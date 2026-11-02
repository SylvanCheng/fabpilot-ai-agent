"""Where public datasets come from and where they land locally."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def data_root() -> Path:
    """`$FABPILOT_DATA_DIR`, else `<repo>/data/raw` (git-ignored)."""
    env = os.environ.get("FABPILOT_DATA_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[5] / "data" / "raw"


@dataclass(frozen=True)
class Dataset:
    key: str
    title: str
    homepage: str
    license: str
    url: str | None  # direct download, if one exists
    files: tuple[str, ...]  # files expected after download/extract

    @property
    def path(self) -> Path:
        return data_root() / self.key

    def is_present(self) -> bool:
        return all((self.path / f).exists() for f in self.files)


SECOM = Dataset(
    key="secom",
    title="SECOM semiconductor manufacturing process data (UCI)",
    homepage="https://archive.ics.uci.edu/dataset/179/secom",
    license="CC BY 4.0",
    url="https://archive.ics.uci.edu/static/public/179/secom.zip",
    files=("secom.data", "secom_labels.data"),
)

WM811K = Dataset(
    key="wm811k",
    title="WM-811K wafer map dataset (MIR lab, via Kaggle mirror)",
    homepage="https://www.kaggle.com/datasets/qingyi/wm811k-wafer-map",
    license="See dataset page; research/educational use",
    url=None,  # Kaggle requires an account + API token
    files=("LSWMD.pkl",),
)

DATASETS = {d.key: d for d in (SECOM, WM811K)}
