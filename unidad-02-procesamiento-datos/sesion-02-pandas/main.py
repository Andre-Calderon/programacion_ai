"""Build reproducible tabular and numerical artifacts for the next sessions."""

import argparse
from pathlib import Path

import numpy as np

from titanic.analysis import (
    load_passengers,
    missing_age_by_class,
    numerical_arrays,
    prepare_passengers,
    survival_by_group,
)

DEFAULT_CSV = Path(__file__).resolve().parents[2] / "datasets" / "Titanic-Dataset.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare the Titanic dataset")
    parser.add_argument("csv", nargs="?", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()

    passengers = load_passengers(args.csv)
    prepared = prepare_passengers(passengers)
    summary = survival_by_group(prepared)
    missing_ages = missing_age_by_class(prepared)
    features, labels = numerical_arrays(prepared)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    prepared.to_csv(args.output_dir / "passengers_prepared.csv", index=False)
    summary.to_csv(args.output_dir / "survival_by_group.csv", index=False)
    missing_ages.to_csv(args.output_dir / "missing_age_by_class.csv", index=False)
    np.save(args.output_dir / "features.npy", features)
    np.save(args.output_dir / "labels.npy", labels)

    print(f"Passengers: {len(prepared)}")
    print(f"Missing ages: {int(prepared['age_missing'].sum())}")
    print(f"Feature matrix: {features.shape}; labels: {labels.shape}")
    print(f"Files written to: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
