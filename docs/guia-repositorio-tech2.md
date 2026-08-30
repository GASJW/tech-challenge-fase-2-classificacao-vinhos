# Guia rápido do repositório — Tech Challenge 2

Este repositório contém a análise e o protótipo de Machine Learning para classificar amostras de vinho como **alta qualidade** ou **baixa/média qualidade** a partir de medições físico-químicas.

## Objetivo

Transformamos a nota original `quality` em um alvo binário:

- `quality >= 7` → alta qualidade (`1`);
- `quality < 7` → baixa/média qualidade (`0`).

A ideia é usar o modelo para **priorizar amostras para avaliação**, e não substituir a validação sensorial do especialista.

## Estrutura principal

```text
data/
├── raw/WineQT.csv                         # fonte bruta preservada
└── processed/WineQT_deduplicated.csv      # base limpa usada no treino

notebooks/
├── 00-validacoes-iniciais.ipynb            # saneamento, duplicidade e outliers
└── 01-eda-modelagem.ipynb                  # EDA, treinamento e avaliação

src/wine_quality/
├── data.py                                  # carga, deduplicação e preparação
├── modeling.py                              # pipelines dos modelos
└── pipeline.py                              # execução e geração dos resultados

scripts/
├── run_pipeline.py                          # executa o experimento completo
├── create_initial_validation_notebook.py    # gera o notebook de validações
└── create_notebook.py                       # gera o notebook de EDA/modelagem

results/
├── metrics.json                             # fonte de verdade das métricas
├── tables/                                  # tabelas, previsões e comparações
└── figures/                                 # gráficos usados na análise

docs/
├── decisoes-metodologicas.md                # decisões técnicas do projeto
├── escalonamento-standard-vs-minmax.md      # comparação dos escalonadores
├── roteiro-video-executivo-5min.md          # roteiro do vídeo
└── guia-repositorio-tech2.md                # este documento

presentation/
├── Tech-Challenge-2-Storytelling.pptx      # apresentação oficial
└── tech-challenge-2-executiva.html          # versão navegável de apoio
```

## Fluxo da análise

1. A base bruta é carregada e validada quanto a colunas, tipos, nulos e identificadores.
2. Perfis físico-químicos repetidos são deduplicados usando as 11 features e `quality`. A primeira ocorrência é preservada.
3. A fonte bruta não é sobrescrita. A base limpa é gravada em `data/processed/`.
4. O `Id` fica somente para rastreabilidade; não entra como variável do modelo. `quality` também fica fora das features e é usada apenas para criar o alvo.
5. Os dados são divididos de forma estratificada em treino e teste, usando `random_state=42`.
6. Os modelos oficiais são treinados na base limpa:
   - **Regressão Logística:** imputação mediana, `StandardScaler` e `class_weight="balanced"`;
   - **Random Forest:** imputação mediana e `class_weight="balanced_subsample"`, sem necessidade de escalonamento.
7. A avaliação considera `accuracy`, `precision`, `recall`, `F1`, `ROC-AUC` e `Average Precision`, com validação cruzada estratificada de cinco partes.

## Resultado do saneamento

- 1.143 linhas na fonte bruta;
- 114 grupos de perfis repetidos, totalizando 239 linhas;
- 125 linhas redundantes removidas da base de modelagem;
- 1.018 perfis únicos usados pelos modelos;
- 137 perfis de alta qualidade, equivalentes a 13,46% da base limpa;
- zero duplicidade de perfil e zero duplicidade de `Id` na base processada.

Os outliers são identificados pelo método IQR, mas não são removidos automaticamente. Um valor extremo pode ser erro de medição ou uma condição real de produção.

## Como executar

A partir da raiz do repositório:

```powershell
python -m venv .venv-tc2
.\.venv-tc2\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/run_pipeline.py
python -m pytest -q
```

O comando `run_pipeline.py` recria a base deduplicada, treina os modelos e atualiza `results/`. Os notebooks devem ser lidos nesta ordem:

1. `00-validacoes-iniciais.ipynb`;
2. `01-eda-modelagem.ipynb`.

## Onde consultar cada informação

- Métricas oficiais: [`results/metrics.json`](../results/metrics.json);
- comparação dos modelos: [`results/tables/model_comparison.csv`](../results/tables/model_comparison.csv);
- comparação StandardScaler vs MinMaxScaler: [`results/tables/scaler_comparison.csv`](../results/tables/scaler_comparison.csv);
- decisões técnicas: [`decisoes-metodologicas.md`](decisoes-metodologicas.md);
- roteiro do vídeo: [`roteiro-video-executivo-5min.md`](roteiro-video-executivo-5min.md);
- apresentação: [`../presentation/Tech-Challenge-2-Storytelling.pptx`](../presentation/Tech-Challenge-2-Storytelling.pptx).

## Interpretação final

O Random Forest foi o candidato mais seletivo para triagem, enquanto a Regressão Logística encontrou mais positivos, aceitando mais falsos positivos. A escolha do limiar deve depender do custo de cada erro.

Portanto, o projeto entrega um **apoio à priorização**. A aprovação da qualidade continua dependendo da avaliação sensorial e da validação em novos lotes.
