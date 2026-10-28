"""Exec-only observation cursor; no model-facing or HTTP observer."""

import argparse
import json
from pathlib import Path

from sut.store import Store


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--epoch")
    parser.add_argument("--since", type=int)
    args = parser.parse_args()
    if (args.epoch is None) != (args.since is None):
        parser.error("Provide both --epoch and --since, or neither for current cursor")
    store = Store(args.state_dir / "harbour.sqlite")
    result = store.observation_start() if args.epoch is None else store.observe(args.epoch, args.since)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
