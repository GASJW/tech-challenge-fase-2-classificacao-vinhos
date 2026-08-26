"""Leitura, validação e preparação dos dados do Tech Challenge 2."""

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


FEATURE_COLUMNS = [
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
]
REQUIRED_COLUMNS = [*FEATURE_COLUMNS, "quality", "Id"]


def validate_dataset(frame: pd.DataFrame) -> None:
    """Valida o contrato mínimo do CSV antes de qualquer modelagem."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in frame]
    if missing_columns:
        raise ValueError(
            "Há colunas obrigatórias ausentes: " + ", ".join(missing_columns)
        )
    if frame.empty:
        raise ValueError("O dataset está vazio.")
    if frame[REQUIRED_COLUMNS].isna().any().any():
        raise ValueError("O dataset contém valores ausentes.")
    if frame["Id"].duplicated().any():
        raise ValueError("O dataset contém Id duplicado.")
    if not all(pd.api.types.is_numeric_dtype(frame[column]) for column in REQUIRED_COLUMNS):
        raise ValueError("As colunas do dataset devem ser numéricas.")
    if frame["quality"].nunique() < 2:
        raise ValueError("A coluna quality precisa conter pelo menos duas classes.")


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Carrega e valida um CSV de qualidade de vinhos."""
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset não encontrado: {csv_path}")
    frame = pd.read_csv(csv_path)
    validate_dataset(frame)
    return frame


def prepare_dataset(
    frame: pd.DataFrame, threshold: int = 7
) -> tuple[pd.DataFrame, pd.Series]:
    """Separa preditores e cria o alvo binário de alta qualidade."""
    validate_dataset(frame)
    if not isinstance(threshold, int):
        raise TypeError("threshold deve ser inteiro.")

    features = frame[FEATURE_COLUMNS].copy()
    target = (frame["quality"] >= threshold).astype("int8")
    target.name = "high_quality"
    if target.nunique() < 2:
        raise ValueError("O threshold não produz duas classes no alvo.")
    return features, target


def split_dataset(
    features: pd.DataFrame,
    target: pd.Series,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Divide os dados preservando a proporção das classes."""
    return train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=random_state,
        stratify=target,
    )
