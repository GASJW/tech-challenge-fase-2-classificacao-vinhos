import numpy as np
import pandas as pd

from wine_quality.modeling import (
    build_logistic_model,
    build_models,
    evaluate_model,
    fit_models,
)


def test_build_models_exposes_two_required_classifiers() -> None:
    models = build_models(random_state=42)

    assert set(models) == {"logistic_regression", "random_forest"}
    assert all(hasattr(model, "fit") for model in models.values())


def test_build_logistic_model_supports_minmax_scaler() -> None:
    model = build_logistic_model(random_state=42, scaler="minmax")

    assert model.named_steps["scaler"].__class__.__name__ == "MinMaxScaler"


def test_fit_and_evaluate_model_returns_required_metrics() -> None:
    X = pd.DataFrame({"feature_a": np.linspace(0, 1, 20), "feature_b": np.linspace(1, 0, 20)})
    y = pd.Series([0, 1] * 10, name="high_quality")
    models = build_models(random_state=42)
    fitted = fit_models(models, X.iloc[:16], y.iloc[:16])

    metrics = evaluate_model(fitted["logistic_regression"], X.iloc[16:], y.iloc[16:])

    assert {
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "average_precision",
    } <= metrics.keys()
    assert all(0 <= value <= 1 for value in metrics.values())
