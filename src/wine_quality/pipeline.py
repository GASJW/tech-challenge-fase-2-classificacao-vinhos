"""Orquestração da análise exploratória, treinamento e geração de artefatos."""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    average_precision_score,
    precision_recall_curve,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_validate

from .data import FEATURE_COLUMNS, load_dataset, prepare_dataset, split_dataset
from .modeling import (
    METRIC_NAMES,
    build_models,
    evaluate_model,
    feature_importance,
    fit_models,
    predict_with_scores,
)


CV_SCORING = {metric: metric for metric in METRIC_NAMES}
PLOT_COLORS = {
    "logistic_regression": "#ED145B",
    "random_forest": "#26A69A",
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=float),
        encoding="utf-8",
    )


def _configure_plot(title: str, ax: plt.Axes) -> None:
    ax.set_title(title, loc="left", fontweight="bold", pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.2)


def _save_target_distribution(target: pd.Series, path: Path) -> None:
    distribution = target.value_counts().sort_index()
    labels = ["Baixa/média (< 7)", "Alta (>= 7)"]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, distribution.values, color=["#505050", "#ED145B"])
    ax.set_ylabel("Quantidade de amostras")
    _configure_plot("A classe de alta qualidade é minoritária", ax)
    for bar, value in zip(bars, distribution.values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 12, f"{value:,}".replace(",", "."), ha="center")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _outlier_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for feature in FEATURE_COLUMNS:
        q1, q3 = frame[feature].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        mask = (frame[feature] < lower_fence) | (frame[feature] > upper_fence)
        rows.append(
            {
                "feature": feature,
                "outlier_count": int(mask.sum()),
                "outlier_share": float(mask.mean()),
                "lower_fence": float(lower_fence),
                "upper_fence": float(upper_fence),
            }
        )
    return pd.DataFrame(rows).sort_values("outlier_count", ascending=False, ignore_index=True)


def _save_standardized_boxplot(frame: pd.DataFrame, path: Path) -> None:
    standardized = (frame[FEATURE_COLUMNS] - frame[FEATURE_COLUMNS].mean()) / frame[FEATURE_COLUMNS].std()
    fig, ax = plt.subplots(figsize=(10, 6))
    boxplot_kwargs = {
        "patch_artist": True,
        "flierprops": {
            "marker": ".",
            "markersize": 3,
            "markerfacecolor": "#ED145B",
            "markeredgecolor": "#ED145B",
        },
    }
    try:
        boxplot = ax.boxplot(
            standardized.to_numpy(),
            orientation="horizontal",
            tick_labels=FEATURE_COLUMNS,
            **boxplot_kwargs,
        )
    except TypeError:
        boxplot = ax.boxplot(
            standardized.to_numpy(),
            vert=False,
            labels=FEATURE_COLUMNS,
            **boxplot_kwargs,
        )
    for box in boxplot["boxes"]:
        box.set_facecolor("#ED145B")
        box.set_alpha(0.65)
    ax.set_xlabel("Desvios-padrão em relação à média")
    ax.set_ylabel("")
    _configure_plot("Boxplots padronizados sinalizam extremos para investigação", ax)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _save_correlation_heatmap(frame: pd.DataFrame, path: Path) -> None:
    columns = [*FEATURE_COLUMNS, "quality"]
    correlation = frame[columns].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PendingDeprecationWarning)
        sns.heatmap(
            correlation,
            cmap="vlag",
            center=0,
            square=True,
            linewidths=0.4,
            cbar_kws={"shrink": 0.7},
            ax=ax,
        )
    _configure_plot("Correlação linear entre variáveis físico-químicas", ax)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _save_model_comparison(model_metrics: pd.DataFrame, path: Path) -> None:
    metrics_to_plot = ["average_precision", "f1", "recall", "roc_auc"]
    plot_frame = model_metrics.set_index("model")[metrics_to_plot]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    plot_frame.plot(kind="bar", ax=ax, color=["#ED145B", "#7B1FA2", "#26A69A", "#505050"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Métrica no conjunto de teste")
    ax.set_xlabel("")
    ax.legend(title="Métrica", ncol=4, frameon=False)
    _configure_plot("Comparação: o modelo precisa equilibrar detecção e precisão", ax)
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _save_feature_importance(importance: pd.DataFrame, path: Path) -> None:
    random_forest = importance[importance["model"] == "random_forest"].copy()
    random_forest = random_forest.nlargest(10, "importance").sort_values("importance")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(random_forest["feature"], random_forest["importance"], color="#ED145B")
    ax.set_xlabel("Importância relativa")
    ax.set_ylabel("")
    _configure_plot("Random Forest prioriza variáveis ligadas a álcool e acidez", ax)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _save_confusion_matrices(predictions: dict[str, pd.DataFrame], directory: Path) -> None:
    for name, frame in predictions.items():
        fig, ax = plt.subplots(figsize=(5, 4.5))
        ConfusionMatrixDisplay.from_predictions(
            frame["actual"],
            frame["predicted"],
            display_labels=["< 7", ">= 7"],
            cmap="RdPu",
            colorbar=False,
            ax=ax,
        )
        _configure_plot(f"Matriz de confusão — {name}", ax)
        fig.tight_layout()
        fig.savefig(directory / f"confusion_matrix_{name}.png", dpi=160)
        plt.close(fig)


def _save_curves(predictions: dict[str, pd.DataFrame], path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for name, frame in predictions.items():
        color = PLOT_COLORS[name]
        fpr, tpr, _ = roc_curve(frame["actual"], frame["probability"])
        precision, recall, _ = precision_recall_curve(
            frame["actual"], frame["probability"]
        )
        roc_auc = np.trapezoid(tpr, fpr)
        ap = average_precision_score(frame["actual"], frame["probability"])
        axes[0].plot(fpr, tpr, label=f"{name} (AUC {roc_auc:.3f})", color=color)
        axes[1].plot(recall, precision, label=f"{name} (AP {ap:.3f})", color=color)

    axes[0].plot([0, 1], [0, 1], "--", color="#999999", linewidth=1)
    axes[0].set(xlabel="False positive rate", ylabel="True positive rate")
    axes[1].set(xlabel="Recall", ylabel="Precision")
    axes[0].legend(frameon=False, fontsize=8)
    axes[1].legend(frameon=False, fontsize=8)
    _configure_plot("Curvas ROC", axes[0])
    _configure_plot("Curvas Precision-Recall", axes[1])
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def run_experiment(
    data_path: str | Path,
    output_dir: str | Path,
    threshold: int = 7,
    random_state: int = 42,
) -> dict:
    """Executa a pipeline completa e persiste os artefatos do experimento."""
    output_path = Path(output_dir)
    table_path = output_path / "tables"
    figure_path = output_path / "figures"
    table_path.mkdir(parents=True, exist_ok=True)
    figure_path.mkdir(parents=True, exist_ok=True)

    frame = load_dataset(data_path)
    features, target = prepare_dataset(frame, threshold=threshold)
    X_train, X_test, y_train, y_test = split_dataset(
        features, target, test_size=0.2, random_state=random_state
    )

    models = build_models(random_state=random_state)
    fitted_models = fit_models(models, X_train, y_train)
    predictions = {
        name: predict_with_scores(model, X_test, y_test)
        for name, model in fitted_models.items()
    }

    test_metrics = {
        name: evaluate_model(model, X_test, y_test)
        for name, model in fitted_models.items()
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    cv_metrics: dict[str, dict[str, dict[str, float]]] = {}
    for name, model in models.items():
        scores = cross_validate(
            model,
            X_train,
            y_train,
            cv=cv,
            scoring=CV_SCORING,
            n_jobs=1,
        )
        cv_metrics[name] = {
            "mean": {
                metric: float(np.mean(scores[f"test_{metric}"]))
                for metric in METRIC_NAMES
            },
            "std": {
                metric: float(np.std(scores[f"test_{metric}"]))
                for metric in METRIC_NAMES
            },
        }

    target_distribution = (
        target.value_counts()
        .sort_index()
        .rename_axis("target")
        .reset_index(name="count")
    )
    target_distribution["label"] = target_distribution["target"].map(
        {0: "Baixa/média (< 7)", 1: "Alta (>= 7)"}
    )
    target_distribution["share"] = target_distribution["count"] / len(target)
    target_distribution.to_csv(table_path / "target_distribution.csv", index=False)
    outlier_summary = _outlier_summary(frame)
    outlier_summary.to_csv(table_path / "outlier_summary.csv", index=False)

    model_rows = []
    for name in fitted_models:
        row = {"model": name}
        row.update({f"test_{key}": value for key, value in test_metrics[name].items()})
        row.update({f"cv_mean_{key}": value for key, value in cv_metrics[name]["mean"].items()})
        row.update({f"cv_std_{key}": value for key, value in cv_metrics[name]["std"].items()})
        model_rows.append(row)
    model_comparison = pd.DataFrame(model_rows)
    model_comparison.to_csv(table_path / "model_comparison.csv", index=False)

    importance_frames = []
    for name, model in fitted_models.items():
        importance = feature_importance(model, list(features.columns))
        importance.insert(0, "model", name)
        importance_frames.append(importance)
    feature_importance_table = pd.concat(importance_frames, ignore_index=True)
    feature_importance_table.to_csv(
        table_path / "feature_importance.csv", index=False
    )

    frame[[*FEATURE_COLUMNS, "quality"]].describe().transpose().to_csv(
        table_path / "descriptive_statistics.csv"
    )
    for name, prediction_frame in predictions.items():
        prediction_frame.to_csv(table_path / f"predictions_{name}.csv", index=False)

    dataset_summary = {
        "rows": int(len(frame)),
        "feature_count": int(len(FEATURE_COLUMNS)),
        "features": FEATURE_COLUMNS,
        "quality_distribution": {
            str(int(key)): int(value) for key, value in frame["quality"].value_counts().sort_index().items()
        },
        "positive_count": int(target.sum()),
        "positive_rate": float(target.mean()),
        "missing_values": int(frame.isna().sum().sum()),
        "duplicate_ids": int(frame["Id"].duplicated().sum()),
        "excluded_columns": ["Id", "quality"],
    }
    result = {
        "experiment": {
            "target_definition": f"quality >= {threshold}",
            "random_state": random_state,
            "test_size": 0.2,
            "cv_folds": 5,
        },
        "dataset": dataset_summary,
        "split": {
            "train_rows": int(len(X_train)),
            "test_rows": int(len(X_test)),
            "train_positive_rate": float(y_train.mean()),
            "test_positive_rate": float(y_test.mean()),
        },
        "models": {
            name: {"test": test_metrics[name], "cross_validation": cv_metrics[name]}
            for name in fitted_models
        },
    }
    _write_json(output_path / "metrics.json", result)

    model_comparison_for_plot = model_comparison.rename(
        columns={column: column.removeprefix("test_") for column in model_comparison.columns}
    )
    _save_target_distribution(target, figure_path / "target_distribution.png")
    _save_standardized_boxplot(frame, figure_path / "standardized_boxplots.png")
    _save_correlation_heatmap(frame, figure_path / "correlation_heatmap.png")
    _save_model_comparison(model_comparison_for_plot, figure_path / "model_comparison.png")
    _save_feature_importance(
        feature_importance_table,
        figure_path / "feature_importance_random_forest.png",
    )
    _save_confusion_matrices(predictions, figure_path)
    _save_curves(predictions, figure_path / "roc_pr_curves.png")

    return result
