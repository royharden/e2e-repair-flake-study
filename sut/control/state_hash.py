"""Read logical business state from an existing demo database."""

import argparse
import json
from pathlib import Path

from sut.store import Store


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(Store(args.state_dir / "harbour.sqlite").state_hash(), sort_keys=True))


if __name__ == "__main__":
    main()
