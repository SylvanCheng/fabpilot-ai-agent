"""Download public datasets into `data/raw/<key>/`."""

from __future__ import annotations

import io
import shutil
import subprocess
import zipfile

import httpx

from fabpilot.datasets.registry import SECOM, WM811K, Dataset


def download_secom(force: bool = False) -> Dataset:
    if SECOM.is_present() and not force:
        return SECOM
    SECOM.path.mkdir(parents=True, exist_ok=True)
    assert SECOM.url
    with httpx.Client(follow_redirects=True, timeout=120) as client:
        resp = client.get(SECOM.url)
        resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        for name in zf.namelist():
            if name.endswith((".data", ".names")):
                (SECOM.path / name.rsplit("/", 1)[-1]).write_bytes(zf.read(name))
    return SECOM


def download_wm811k(force: bool = False) -> Dataset:
    """Uses the Kaggle CLI (`pip install kaggle` + ~/.kaggle/kaggle.json) if available."""
    if WM811K.is_present() and not force:
        return WM811K
    if shutil.which("kaggle") is None:
        raise RuntimeError(
            "WM-811K is hosted on Kaggle. Either install the Kaggle CLI and an API token, or "
            f"download it manually from {WM811K.homepage} and put LSWMD.pkl in {WM811K.path}."
        )
    WM811K.path.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "kaggle",
            "datasets",
            "download",
            "-d",
            "qingyi/wm811k-wafer-map",
            "-p",
            str(WM811K.path),
            "--unzip",
        ],
        check=True,
    )
    return WM811K
