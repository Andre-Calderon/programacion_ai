"""Prepare a labeled table and a numerical array from the same data."""

from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = (
    "PassengerId",
    "Survived",
    "Pclass",
    "Sex",
    "Age",
    "SibSp",
    "Parch",
    "Fare",
    "Embarked",
)
FEATURE_COLUMNS = ("Pclass", "age_filled", "Fare", "family_size")


def load_passengers(path: Path) -> pd.DataFrame:
    """Read the supplied CSV and check the columns used in this lesson."""
    passengers = pd.read_csv(path)
    missing = sorted(set(REQUIRED_COLUMNS) - set(passengers.columns))
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")
    if passengers.empty:
        raise ValueError("The passenger table is empty")
    return passengers


def prepare_passengers(passengers: pd.DataFrame) -> pd.DataFrame:
    """Keep useful columns and record how missing ages were handled."""
    prepared = passengers.loc[:, list(REQUIRED_COLUMNS)].copy()
    if prepared["PassengerId"].isna().any():
        raise ValueError("PassengerId must not be missing")
    if not prepared["Survived"].isin([0, 1]).all():
        raise ValueError("Survived must contain only 0 or 1")
    if prepared["PassengerId"].duplicated().any():
        raise ValueError("PassengerId must be unique")
    if prepared["Age"].notna().sum() == 0:
        raise ValueError("At least one age is required")

    prepared["age_missing"] = prepared["Age"].isna()
    prepared["age_filled"] = prepared["Age"].fillna(prepared["Age"].median())
    prepared["family_size"] = prepared["SibSp"] + prepared["Parch"] + 1
    return prepared


def survival_by_group(prepared: pd.DataFrame) -> pd.DataFrame:
    """Report counts and observed survival proportions for each group."""
    return prepared.groupby(["Pclass", "Sex"], as_index=False, dropna=False).agg(
        passengers=("Survived", "size"),
        survival_rate=("Survived", "mean"),
    )


def missing_age_by_class(prepared: pd.DataFrame) -> pd.DataFrame:
    """Report passengers and the share of missing ages for each class."""
    return prepared.groupby("Pclass", as_index=False, dropna=False).agg(
        passengers=("age_missing", "size"),
        missing_age_rate=("age_missing", "mean"),
    )


def numerical_arrays(prepared: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Return numerical features and labels for later tensor exploration."""
    if not prepared["Survived"].isin([0, 1]).all():
        raise ValueError("Survived must contain only 0 or 1")
    features = prepared.loc[:, list(FEATURE_COLUMNS)].to_numpy(dtype=np.float32)
    labels = prepared["Survived"].to_numpy(dtype=np.int64)
    if not np.isfinite(features).all():
        raise ValueError("Numerical features must be finite")
    return features, labels
