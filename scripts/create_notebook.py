"""Gera o notebook narrativo do Tech Challenge 2."""

from pathlib import Path
from textwrap import dedent

import nbformat as nbf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "01-eda-modelagem.ipynb"


def markdown(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip())


cells = [
    markdown(
        """
        # Tech Challenge Fase 2 — Classificação de Vinhos

        **Pergunta de negócio:** é possível priorizar amostras com maior probabilidade de alta qualidade a partir de medições físico-químicas?

        O alvo binário segue o enunciado: `quality >= 7` representa alta qualidade. A análise usa o mesmo pacote Python chamado pelo script da pipeline, evitando divergência entre notebook e resultados oficiais.
        """
    ),
    code(
        """
        from pathlib import Path
        import sys

        import matplotlib.pyplot as plt
        import pandas as pd
        import seaborn as sns
        from IPython.display import display

        project_root = Path.cwd()
        sys.path.insert(0, str(project_root / "src"))

        from wine_quality.data import load_dataset, prepare_dataset, split_dataset
        from wine_quality.modeling import build_models, evaluate_model, feature_importance, fit_models

        data_path = project_root / "data" / "raw" / "WineQT.csv"
        results_path = project_root / "results"
        sns.set_theme(style="whitegrid")
        """
    ),
    markdown("## 1. Compreensão dos dados"),
    code(
        """
        frame = load_dataset(data_path)
        print(f"Linhas: {len(frame):,}".replace(",", "."))
        print(f"Colunas: {frame.shape[1]}")
        print(f"Valores ausentes: {int(frame.isna().sum().sum())}")
        print(f"Ids duplicados: {int(frame['Id'].duplicated().sum())}")
        display(frame.head())
        """
    ),
    code(
        """
        features, target = prepare_dataset(frame, threshold=7)
        summary = pd.DataFrame({
            "classe": ["Baixa/média (< 7)", "Alta (>= 7)"],
            "quantidade": [(target == 0).sum(), (target == 1).sum()],
            "participação": [(target == 0).mean(), (target == 1).mean()],
        })
        display(summary.style.format({"participação": "{:.1%}"}))
        """
    ),
    markdown(
        """
        A classe positiva representa uma parcela pequena do dataset. Por isso, accuracy isolada não é suficiente: a avaliação acompanha precision, recall, F1, ROC-AUC e Average Precision.
        """
    ),
    markdown("## 2. Análise exploratória"),
    code(
        """
        display(frame[features.columns.tolist() + ["quality"]].describe().T.round(3))
        """
    ),
    code(
        """
        outlier_summary = pd.read_csv(results_path / "tables" / "outlier_summary.csv")
        display(outlier_summary.style.format({"outlier_share": "{:.1%}"}))
        """
    ),
    markdown(
        """
        O critério IQR serve como sinalização inicial. Os valores extremos permanecem na base até que uma análise de domínio determine se são erros de medição ou observações legítimas.
        """
    ),
    code(
        """
        fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
        sns.countplot(data=frame, x="quality", color="#ED145B", ax=axes[0])
        axes[0].set_title("Distribuição do rótulo original", loc="left", fontweight="bold")
        axes[0].set_xlabel("Nota de qualidade")
        axes[0].set_ylabel("Amostras")
        sns.heatmap(
            frame[features.columns.tolist() + ["quality"]].corr(),
            cmap="vlag",
            center=0,
            ax=axes[1],
            cbar_kws={"shrink": 0.8},
        )
        axes[1].set_title("Correlação linear", loc="left", fontweight="bold")
        fig.tight_layout()
        plt.show()
        """
    ),
    code(
        """
        correlation_with_quality = (
            frame[features.columns.tolist() + ["quality"]]
            .corr()["quality"]
            .drop("quality")
            .sort_values(ascending=False)
            .to_frame("correlação")
        )
        display(correlation_with_quality.round(3))
        """
    ),
    markdown(
        """
        A associação linear mais forte aparece em `alcohol` (positiva) e `volatile acidity` (negativa). Isso orienta a investigação, mas não prova causalidade nem substitui validação fora da amostra.
        """
    ),
    markdown("## 3. Modelagem e comparação"),
    code(
        """
        X_train, X_test, y_train, y_test = split_dataset(
            features, target, test_size=0.2, random_state=42
        )
        models = build_models(random_state=42)
        fitted_models = fit_models(models, X_train, y_train)
        metrics = pd.DataFrame(
            {
                name: evaluate_model(model, X_test, y_test)
                for name, model in fitted_models.items()
            }
        ).T
        display(metrics.round(3))
        """
    ),
    code(
        """
        comparison = pd.read_csv(results_path / "tables" / "model_comparison.csv")
        display(comparison.style.format({column: "{:.3f}" for column in comparison.columns if column != "model"}))
        """
    ),
    code(
        """
        importance = pd.concat(
            [
                feature_importance(model, list(features.columns)).assign(model=name)
                for name, model in fitted_models.items()
            ],
            ignore_index=True,
        )
        display(importance.groupby("model").head(5))
        """
    ),
    markdown("## 4. Conclusões executivas"),
    code(
        """
        best_model = metrics["average_precision"].idxmax()
        print(
            f"O melhor desempenho no conjunto de teste foi do {best_model}, "
            f"com Average Precision de {metrics.loc[best_model, 'average_precision']:.3f}."
        )
        print(
            "Recomendação: usar o classificador como triagem de amostras e apoio ao enólogo, "
            "com calibração de limiar e validação sensorial antes de automatizar decisões."
        )
        """
    ),
    markdown(
        """
        ### Limitações

        - O rótulo de qualidade é uma avaliação especializada e pode conter subjetividade.
        - A classe positiva é pequena, o que aumenta a incerteza das métricas.
        - O dataset não contém custos, lote, região, processo de produção ou medidas sensoriais detalhadas.
        - Correlação e importância de variável indicam associação preditiva, não causalidade.
        """
    ),
]


notebook = nbf.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
    },
)
NOTEBOOK_PATH.write_text(nbf.writes(notebook), encoding="utf-8")
print(NOTEBOOK_PATH)
