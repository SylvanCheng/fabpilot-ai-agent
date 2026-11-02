"""Write the API contract to `contracts/openapi.json`: `uv run fabpilot-export-openapi`.

The file is committed; CI fails if it differs from what the code generates, so every API change
is visible in review and the frontend client can be checked against it.
"""

import json
from pathlib import Path

from fabpilot.main import create_app

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "contracts" / "openapi.json"


def render() -> str:
    return json.dumps(create_app().openapi(), indent=2, sort_keys=True) + "\n"


def main() -> None:
    CONTRACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONTRACT_PATH.write_text(render(), encoding="utf-8")
    print(f"wrote {CONTRACT_PATH}")


if __name__ == "__main__":
    main()
