"""The committed API contract must match the code. Fix with `uv run fabpilot-export-openapi`."""

from fabpilot.devtools.export_openapi import CONTRACT_PATH, render


def test_openapi_contract_is_up_to_date():
    assert CONTRACT_PATH.exists(), "run `uv run fabpilot-export-openapi`"
    assert CONTRACT_PATH.read_text(encoding="utf-8") == render(), (
        "API changed but contracts/openapi.json was not regenerated: "
        "run `uv run fabpilot-export-openapi` and commit the diff"
    )
