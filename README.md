## English summary

**FIAP Data Analytics Tech Challenge — Wine Quality Classification**

This academic project explores how physicochemical measurements can support the classification of wine quality. It combines data quality checks, exploratory analysis, binary classification and an executive presentation of the findings.

- **Data preparation:** validate the CSV structure, examine missing values and outliers, and remove duplicate profiles. The modeling dataset contains 1,018 unique profiles after removing 125 redundant rows.
- **Modeling:** compare Logistic Regression and Random Forest on a binary target (quality score of 7 or above versus below 7). Preprocessing is included in the modeling pipelines; the ID and original quality score are excluded from the predictors to avoid data leakage.
- **Evaluation:** report accuracy, precision, recall, F1, ROC-AUC and average precision. See [model metrics](results/metrics.json) and [methodological decisions](docs/decisoes-metodologicas.md).
- **Deliverables:** reproducible Python code and notebooks, automated tests, documented results, and an executive presentation. The model is intended to support screening, not replace sensory validation.

To run the project, follow the **Execução** section below. The detailed documentation and executive materials are currently in Portuguese.

---

# Entrega final — Tech Challenge FIAP Fase 2

Pacote consolidado para os três entregáveis oficiais do Tech Challenge FIAP Fase 2: repositório técnico, apresentação executiva e vídeo executivo.

## Entregáveis oficiais

1. **Repositório técnico:** código, notebooks, dados, resultados, testes, documentação e instruções de execução.
2. **Apresentação executiva:** versão PowerPoint em `presentation/`; a versão HTML é um apoio navegável.
3. **Vídeo executivo:** roteiro de até cinco minutos em `docs/roteiro-video-executivo-5min.md`.

## Ordem recomendada

1. [`docs/guia-repositorio-tech2.md`](docs/guia-repositorio-tech2.md) — visão geral da estrutura e do fluxo do projeto.
2. [`notebooks/00-validacoes-iniciais.ipynb`](notebooks/00-validacoes-iniciais.ipynb) — saneamento, contrato do CSV, deduplicação por perfil, nulos, outliers e criação das classificações possíveis.
3. [`notebooks/01-eda-modelagem.ipynb`](notebooks/01-eda-modelagem.ipynb) — EDA, preparação da base limpa, treinamento dos modelos e avaliação.
4. [`results/metrics.json`](results/metrics.json) — métricas oficiais dos modelos.
5. [`presentation/Tech-Challenge-2-Storytelling.pptx`](presentation/Tech-Challenge-2-Storytelling.pptx) — apresentação oficial.
6. [`presentation/tech-challenge-2-executiva.html`](presentation/tech-challenge-2-executiva.html) — versão navegável de apoio.
7. [`docs/roteiro-video-executivo-5min.md`](docs/roteiro-video-executivo-5min.md) — roteiro do vídeo obrigatório.

## Conteúdo

| Pasta | Conteúdo |
|---|---|
| `data/` | Dataset bruto e snapshot deduplicado usado na modelagem |
| `notebooks/` | Validações iniciais e notebook completo de EDA/modelagem |
| `src/` | Código Python reutilizável da preparação e dos modelos |
| `scripts/` | Scripts de execução da pipeline e geração dos artefatos |
| `results/` | Métricas, tabelas e figuras produzidas |
| `docs/` | Decisões metodológicas, escalonamento e roteiro do vídeo |
| `presentation/` | Apresentações HTML e PowerPoint |
| `tests/` | Testes automatizados do projeto |

## Principais decisões

- Alvo binário: `quality >= 7` representa alta qualidade; `quality < 7` representa baixa/média qualidade.
- Deduplicação: a fonte bruta tem 1.143 registros; perfis com as mesmas 11 medições e a mesma `quality` são reduzidos a uma ocorrência, preservando o primeiro `Id`. A base de modelagem tem 1.018 perfis únicos e 125 linhas redundantes removidas.
- `Id` e `quality` não entram como preditores, evitando vazamento de informação.
- Outliers são sinalizados por IQR, mas não removidos automaticamente.
- A Regressão Logística usa imputação mediana e `StandardScaler` dentro do pipeline; o `MinMaxScaler` é mantido como comparação experimental.
- O Random Forest usa imputação mediana, sem necessidade de escalonamento.
- A avaliação considera accuracy, precision, recall, F1, ROC-AUC e Average Precision.
- Os modelos oficiais foram treinados na base limpa: Regressão Logística e Random Forest. Os dois modelos atendem ao requisito mínimo de “pelo menos dois modelos”.
- KNN e Árvore de Decisão permanecem como referência do trabalho dos colegas, mas não entram como resultado oficial sem reexecução no mesmo protocolo.

Detalhes: [`docs/decisoes-metodologicas.md`](docs/decisoes-metodologicas.md) e [`docs/escalonamento-standard-vs-minmax.md`](docs/escalonamento-standard-vs-minmax.md).

## Execução

Abra um terminal nesta pasta e execute:

```powershell
python -m venv .venv-tc2
.\.venv-tc2\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/run_pipeline.py
python -m pytest -q
```

Para os notebooks, abra primeiro `00-validacoes-iniciais.ipynb` e depois `01-eda-modelagem.ipynb`. Execute o Jupyter a partir da raiz desta pasta para que os caminhos relativos de dados, código e resultados sejam encontrados corretamente.

Para a apresentação, use o PowerPoint como artefato principal e o HTML como apoio de navegação. Para o vídeo, siga o roteiro e priorize linguagem de negócio: o modelo apoia a triagem, mas não substitui a validação sensorial.

## Escopo da entrega

Este repositório contém somente os artefatos pertinentes ao Tech Challenge Fase 2. O material experimental de outros membros e arquivos de desenvolvimento permanecem fora desta entrega oficial.
