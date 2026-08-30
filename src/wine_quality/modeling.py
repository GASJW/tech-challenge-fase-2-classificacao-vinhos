"""Modelos, treinamento e avaliação da classificação de vinhos."""

from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler


METRIC_NAMES = [
    "accuracy",
    "precision",
    "recall",
    "f1",
    "roc_auc",
    "average_precision",
]


def build_logistic_model(
    random_state: int = 42, scaler: str = "standard"
) -> Pipeline:
    """Cria a Regressão Logística com o escalonador solicitado."""
    scalers = {
        "standard": StandardScaler(),
        "minmax": MinMaxScaler(),
    }
    if scaler not in scalers:
        raise ValueError("scaler deve ser 'standard' ou 'minmax'.")
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", scalers[scaler]),
            (
                "model",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=random_state,
                ),
            ),
        ]
    )


def build_models(random_state: int = 42) -> dict[str, Pipeline]:
    """Cria as duas abordagens oficiais exigidas pelo enunciado."""
    return {
        "logistic_regression": build_logistic_model(
            random_state=random_state, scaler="standard"
        ),
        "random_forest": Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "model",
                    RandomForestClassifier(
                        class_weight="balanced_subsample",
                        n_estimators=400,
                        min_samples_leaf=2,
                        n_jobs=-1,
                        random_state=random_state,
                    ),
                ),
            ]
        ),
    }


def fit_models(
    models: dict[str, Pipeline],
    features: pd.DataFrame,
    target: pd.Series,
) -> dict[str, Pipeline]:
    """Treina cada pipeline e retorna os modelos ajustados."""
    return {name: model.fit(features, target) for name, model in models.items()}


def evaluate_model(
    model: Pipeline, features: pd.DataFrame, target: pd.Series
) -> dict[str, float]:
    """Calcula métricas adequadas para o desbalanceamento do alvo."""
    predictions = model.predict(features)
    probabilities = model.predict_proba(features)[:, 1]
    return {
        "accuracy": float(accuracy_score(target, predictions)),
        "precision": float(precision_score(target, predictions, zero_division=0)),
        "recall": float(recall_score(target, predictions, zero_division=0)),
        "f1": float(f1_score(target, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(target, probabilities)),
        "average_precision": float(average_precision_score(target, probabilities)),
    }


def predict_with_scores(
    model: Pipeline, features: pd.DataFrame, target: pd.Series
) -> pd.DataFrame:
    """Retorna rótulos e probabilidades para gráficos e auditoria."""
    return pd.DataFrame(
        {
            "actual": target.to_numpy(),
            "predicted": model.predict(features),
            "probability": model.predict_proba(features)[:, 1],
        },
        index=target.index,
    )


def feature_importance(model: Pipeline, feature_names: list[str]) -> pd.DataFrame:
    """Extrai importância comparável dos dois modelos."""
    estimator: Any = model.named_steps["model"]
    if hasattr(estimator, "feature_importances_"):
        values = np.asarray(estimator.feature_importances_, dtype=float)
        direction = np.where(values >= 0, "positive", "positive")
    elif hasattr(estimator, "coef_"):
        values = np.asarray(estimator.coef_[0], dtype=float)
        direction = np.where(values >= 0, "positive", "negative")
    else:
        raise TypeError("Modelo não expõe coeficientes nem feature_importances_.")

    return pd.DataFrame(
        {
            "feature": feature_names,
            "importance": np.abs(values),
            "direction": direction,
            "signed_value": values,
        }
    ).sort_values("importance", ascending=False, ignore_index=True)
