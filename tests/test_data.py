from pathlib import Path

import pandas as pd
import pytest

from wine_quality.data import (
    deduplicate_profiles,
    prepare_dataset,
    split_dataset,
    validate_dataset,
)


REQUIRED_COLUMNS = [
    "fixed acidity",
    "volatile acidity",
    "citric acid",
    "residual sugar",
    "chlorides",
    "free sulfur dioxide",
    "total sulfur dioxide",
    "density",
    "pH",
    "sulphates",
    "alcohol",
    "quality",
    "Id",
]


def sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            **{column: [1.0, 2.0, 3.0, 4.0] for column in REQUIRED_COLUMNS[:-2]},
            "quality": [6, 7, 5, 8],
            "Id": [10, 11, 12, 13],
        }
    )


def test_prepare_dataset_creates_binary_target_and_removes_identifiers() -> None:
    frame = sample_frame()

    features, target = prepare_dataset(frame, threshold=7)

    assert target.tolist() == [0, 1, 0, 1]
    assert target.name == "high_quality"
    assert "Id" not in features.columns
    assert "quality" not in features.columns
    assert len(features.columns) == 11


def test_validate_dataset_rejects_missing_required_columns() -> None:
    frame = sample_frame().drop(columns=["alcohol"])

    with pytest.raises(ValueError, match="colunas obrigatórias"):
        validate_dataset(frame)


def test_validate_dataset_rejects_missing_values_and_duplicate_ids() -> None:
    frame = sample_frame()
    frame.loc[0, "alcohol"] = None

    with pytest.raises(ValueError, match="valores ausentes"):
        validate_dataset(frame)

    frame = sample_frame()
    frame.loc[1, "Id"] = frame.loc[0, "Id"]

    with pytest.raises(ValueError, match="Id duplicado"):
        validate_dataset(frame)


def test_deduplicate_profiles_keeps_one_row_per_physical_profile() -> None:
    frame = sample_frame()
    duplicate = frame.iloc[[0]].copy()
    duplicate.loc[:, "Id"] = 99
    duplicated = pd.concat([frame, duplicate], ignore_index=True)

    clean = deduplicate_profiles(duplicated)

    assert len(clean) == len(frame)
    assert clean["Id"].tolist() == [10, 11, 12, 13]
    assert clean.duplicated(subset=REQUIRED_COLUMNS[:-1]).sum() == 0


def test_split_dataset_preserves_both_classes() -> None:
    frame = pd.DataFrame({"feature": range(20)})
    target = pd.Series([0] * 16 + [1] * 4, name="high_quality")

    X_train, X_test, y_train, y_test = split_dataset(
        frame, target, test_size=0.2, random_state=42
    )

    assert len(X_train) == 16
    assert len(X_test) == 4
    assert y_train.sum() == 3
    assert y_test.sum() == 1
