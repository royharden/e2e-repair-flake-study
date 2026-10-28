"""Later authorized local destructive demo reset; never run during construction."""

import argparse
import json
from pathlib import Path

from sut.store import Store


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--confirm-authored-demo-reset", action="store_true", required=True)
    args = parser.parse_args()
    store = Store(args.state_dir / "harbour.sqlite")
    store.initialize()
    print(json.dumps(store.reset(), sort_keys=True))


if __name__ == "__main__":
    main()
