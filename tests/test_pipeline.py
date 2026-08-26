from pathlib import Path

from wine_quality.pipeline import run_experiment


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "WineQT.csv"


def test_run_experiment_generates_reproducible_result_contract(tmp_path: Path) -> None:
    result = run_experiment(DATA_PATH, tmp_path, random_state=42)

    assert result["dataset"]["rows"] == 1143
    assert result["dataset"]["positive_count"] == 159
    assert result["dataset"]["positive_rate"] == 159 / 1143
    assert set(result["models"]) == {"logistic_regression", "random_forest"}
    assert (tmp_path / "metrics.json").exists()
    assert (tmp_path / "tables" / "model_comparison.csv").exists()
    assert (tmp_path / "tables" / "target_distribution.csv").exists()
    assert (tmp_path / "tables" / "outlier_summary.csv").exists()
    assert (tmp_path / "figures" / "feature_importance_random_forest.png").exists()
