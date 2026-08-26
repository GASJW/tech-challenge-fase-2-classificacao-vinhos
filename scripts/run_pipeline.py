"""Executa a pipeline do Tech Challenge 2 a partir da raiz do projeto."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from wine_quality.pipeline import run_experiment  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-path",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw" / "WineQT.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "results",
    )
    parser.add_argument("--threshold", type=int, default=7)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_experiment(
        data_path=args.data_path,
        output_dir=args.output_dir,
        threshold=args.threshold,
        random_state=args.random_state,
    )
    summary = {
        "rows": result["dataset"]["rows"],
        "positive_rate": result["dataset"]["positive_rate"],
        "models": list(result["models"]),
        "output_dir": str(args.output_dir.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
