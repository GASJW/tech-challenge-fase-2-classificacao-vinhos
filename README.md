# Entrega final — Tech Challenge FIAP Fase 2

Pacote consolidado para os três entregáveis oficiais do Tech Challenge FIAP Fase 2: repositório técnico, apresentação executiva e vídeo executivo.

## Entregáveis oficiais

1. **Repositório técnico:** código, notebooks, dados, resultados, testes, documentação e instruções de execução.
2. **Apresentação executiva:** versão PowerPoint em `presentation/`; a versão HTML é um apoio navegável.
3. **Vídeo executivo:** roteiro de até cinco minutos em `docs/roteiro-video-executivo-5min.md`.

## Ordem recomendada

1. [`notebooks/00-validacoes-iniciais.ipynb`](notebooks/00-validacoes-iniciais.ipynb) — saneamento, contrato do CSV, duplicidades, nulos, outliers e criação das classificações possíveis.
2. [`notebooks/01-eda-modelagem.ipynb`](notebooks/01-eda-modelagem.ipynb) — EDA, preparação, treinamento dos modelos e avaliação.
3. [`results/metrics.json`](results/metrics.json) — métricas oficiais dos modelos.
4. [`presentation/Tech-Challenge-2-Storytelling.pptx`](presentation/Tech-Challenge-2-Storytelling.pptx) — apresentação oficial.
5. [`presentation/tech-challenge-2-executiva.html`](presentation/tech-challenge-2-executiva.html) — versão navegável de apoio.
6. [`docs/roteiro-video-executivo-5min.md`](docs/roteiro-video-executivo-5min.md) — roteiro do vídeo obrigatório.

## Conteúdo

| Pasta | Conteúdo |
|---|---|
| `data/` | Dataset `WineQT.csv` usado no projeto |
| `notebooks/` | Validações iniciais e notebook completo de EDA/modelagem |
| `src/` | Código Python reutilizável da preparação e dos modelos |
| `scripts/` | Scripts de execução da pipeline e geração dos artefatos |
| `results/` | Métricas, tabelas e figuras produzidas |
| `docs/` | Decisões metodológicas, escalonamento e roteiro do vídeo |
| `presentation/` | Apresentações HTML e PowerPoint |
| `tests/` | Testes automatizados do projeto |

## Principais decisões

- Alvo binário: `quality >= 7` representa alta qualidade; `quality < 7` representa baixa/média qualidade.
- `Id` e `quality` não entram como preditores, evitando vazamento de informação.
- Outliers são sinalizados por IQR, mas não removidos automaticamente.
- A Regressão Logística usa imputação mediana e `StandardScaler` dentro do pipeline.
- O Random Forest usa imputação mediana, sem necessidade de escalonamento.
- A avaliação considera accuracy, precision, recall, F1, ROC-AUC e Average Precision.
- A comparação oficial utiliza Regressão Logística e Random Forest; os dois modelos já atendem ao requisito mínimo de “pelo menos dois modelos”.
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
