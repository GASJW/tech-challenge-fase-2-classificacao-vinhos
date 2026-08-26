"""Gera o notebook de auditoria inicial dos dados do Tech Challenge 2."""

from pathlib import Path
from textwrap import dedent

import nbformat as nbf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "00-validacoes-iniciais.ipynb"


def markdown(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip())


cells = [
    markdown(
        """
        # Tech Challenge Fase 2 — Validações iniciais

        Este notebook documenta o **saneamento inicial** antes da EDA e da modelagem.
        O objetivo é verificar se o CSV tem estrutura, tipos, identificadores, rótulos
        e distribuição compatíveis com o desafio.

        **Princípio:** validar e tornar explícitas as decisões; não apagar observações
        sem evidência de erro de medição ou justificativa de negócio.
        """
    ),
    code(
        """
        from pathlib import Path
        import sys

        import pandas as pd
        from IPython.display import display

        project_root = next(
            (
                candidate
                for candidate in [Path.cwd(), *Path.cwd().parents]
                if (candidate / "data" / "raw" / "WineQT.csv").exists()
            ),
            None,
        )
        if project_root is None:
            raise FileNotFoundError(
                "Execute o notebook a partir do projeto Tech-Challenge-Fase-2-"
                "Classificacao-de-Vinhos ou de uma pasta filha."
            )

        sys.path.insert(0, str(project_root / "src"))
        from wine_quality.data import FEATURE_COLUMNS, REQUIRED_COLUMNS, prepare_dataset

        data_path = project_root / "data" / "raw" / "WineQT.csv"
        frame = pd.read_csv(data_path)
        print(f"Arquivo: {data_path}")
        print(f"Dimensão bruta: {frame.shape[0]:,} linhas x {frame.shape[1]} colunas".replace(",", "."))
        """
    ),
    markdown("## 1. Contrato estrutural do arquivo"),
    code(
        """
        expected_columns = set(REQUIRED_COLUMNS)
        actual_columns = set(frame.columns)

        checks = [
            {
                "validação": "Arquivo não vazio",
                "resultado": not frame.empty,
                "evidência": f"{len(frame):,} linhas".replace(",", "."),
            },
            {
                "validação": "Colunas obrigatórias presentes",
                "resultado": expected_columns.issubset(actual_columns),
                "evidência": f"ausentes: {sorted(expected_columns - actual_columns) or 'nenhuma'}",
            },
            {
                "validação": "Nenhuma coluna inesperada",
                "resultado": actual_columns == expected_columns,
                "evidência": f"extras: {sorted(actual_columns - expected_columns) or 'nenhuma'}",
            },
            {
                "validação": "Tipos numéricos",
                "resultado": all(
                    pd.api.types.is_numeric_dtype(frame[column])
                    for column in REQUIRED_COLUMNS
                ),
                "evidência": "features, quality e Id",
            },
        ]

        contract_report = pd.DataFrame(checks)
        display(contract_report)
        assert contract_report["resultado"].all()
        """
    ),
    code(
        """
        profile = pd.DataFrame(
            {
                "tipo": frame.dtypes.astype(str),
                "nulos": frame.isna().sum(),
                "valores_únicos": frame.nunique(),
                "mínimo": frame.min(numeric_only=True),
                "máximo": frame.max(numeric_only=True),
            }
        )
        display(profile)
        """
    ),
    markdown("## 2. Nulos, duplicidades e rastreabilidade"),
    code(
        """
        duplicate_rows = int(frame.duplicated().sum())
        duplicate_ids = int(frame["Id"].duplicated().sum())
        missing_values = int(frame.isna().sum().sum())

        integrity_report = pd.DataFrame(
            [
                {
                    "validação": "Valores ausentes",
                    "quantidade": missing_values,
                    "resultado": missing_values == 0,
                    "decisão": "nenhuma imputação necessária na base bruta",
                },
                {
                    "validação": "Linhas duplicadas",
                    "quantidade": duplicate_rows,
                    "resultado": duplicate_rows == 0,
                    "decisão": "nenhuma linha removida",
                },
                {
                    "validação": "Id duplicado",
                    "quantidade": duplicate_ids,
                    "resultado": duplicate_ids == 0,
                    "decisão": "Id fica para rastreabilidade, não para predição",
                },
            ]
        )
        display(integrity_report)
        assert integrity_report["resultado"].all()
        """
    ),
    markdown(
        """
        O `Id` identifica a amostra, mas não é uma medição físico-química. Por isso,
        ele permanece no arquivo bruto para auditoria e é removido dos preditores.
        A coluna `quality` também não entra como feature: ela é a origem do rótulo e
        seu uso como entrada causaria *target leakage*.
        """
    ),
    markdown("## 3. Quais classificações são possíveis?"),
    code(
        """
        quality_distribution = (
            frame["quality"]
            .value_counts()
            .sort_index()
            .rename_axis("quality")
            .reset_index(name="amostras")
        )
        quality_distribution["participação"] = (
            quality_distribution["amostras"] / len(frame)
        )
        display(
            quality_distribution.style.format({"participação": "{:.1%}"})
        )
        print(
            "Classes originais observadas:",
            ", ".join(str(value) for value in quality_distribution["quality"]),
        )
        """
    ),
    code(
        """
        classification_options = pd.DataFrame(
            [
                {
                    "opção": "Multiclasse original",
                    "classes": "3, 4, 5, 6, 7 e 8",
                    "interpretação": "prever a nota discreta de qualidade",
                    "status": "possível, mas não é o recorte pedido",
                },
                {
                    "opção": "Binária adotada",
                    "classes": "0 = quality < 7; 1 = quality >= 7",
                    "interpretação": "priorizar amostras de alta qualidade",
                    "status": "recorte do enunciado",
                },
            ]
        )
        display(classification_options)
        """
    ),
    markdown(
        """
        Embora a base contenha seis notas distintas, o desafio orienta uma decisão
        binária. O limiar adotado é `7`: notas 3 a 6 ficam em **baixa/média** e notas
        7 e 8 ficam em **alta qualidade**.
        """
    ),
    code(
        """
        features, target = prepare_dataset(frame, threshold=7)
        binary_distribution = pd.DataFrame(
            {
                "classe": ["Baixa/média (< 7)", "Alta (>= 7)"],
                "rótulo": [0, 1],
                "amostras": [(target == 0).sum(), (target == 1).sum()],
            }
        )
        binary_distribution["participação"] = (
            binary_distribution["amostras"] / len(target)
        )
        display(
            binary_distribution.style.format({"participação": "{:.1%}"})
        )
        assert set(target.unique()) == {0, 1}
        """
    ),
    markdown("## 4. Saneamento aplicado e outliers sinalizados"),
    code(
        """
        outlier_rows = []
        for column in FEATURE_COLUMNS:
            q1 = frame[column].quantile(0.25)
            q3 = frame[column].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            count = int(((frame[column] < lower) | (frame[column] > upper)).sum())
            outlier_rows.append(
                {
                    "variável": column,
                    "limite_inferior": lower,
                    "limite_superior": upper,
                    "outliers_IQR": count,
                    "participação": count / len(frame),
                }
            )

        outlier_report = pd.DataFrame(outlier_rows).sort_values(
            "outliers_IQR", ascending=False
        )
        display(
            outlier_report.style.format(
                {
                    "limite_inferior": "{:.3f}",
                    "limite_superior": "{:.3f}",
                    "participação": "{:.1%}",
                }
            )
        )
        """
    ),
    code(
        """
        sanitation_summary = pd.DataFrame(
            [
                {
                    "item": "Nulos",
                    "tratamento": "nenhuma linha alterada; não há nulos",
                },
                {
                    "item": "Duplicidades",
                    "tratamento": "nenhuma linha removida; Id é único",
                },
                {
                    "item": "Id",
                    "tratamento": "mantido para rastreabilidade e excluído de X",
                },
                {
                    "item": "quality",
                    "tratamento": "mantido como origem do alvo e excluído de X",
                },
                {
                    "item": "Outliers",
                    "tratamento": "sinalizados por IQR, sem remoção automática",
                },
                {
                    "item": "Desbalanceamento",
                    "tratamento": "mantido; split estratificado e pesos balanceados",
                },
            ]
        )
        display(sanitation_summary)
        print(
            f"Matriz final de preditores: {features.shape[0]} linhas x "
            f"{features.shape[1]} features"
        )
        """
    ),
    markdown(
        """
        ### Conclusão

        A base está consistente para seguir à EDA: não há nulos, duplicidades ou
        `Id` repetido; todas as colunas são numéricas; e o alvo binário preserva as
        duas classes. Nenhum registro foi excluído. O principal cuidado para a
        modelagem é o desbalanceamento: apenas 13,91% das amostras são de alta
        qualidade.
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
