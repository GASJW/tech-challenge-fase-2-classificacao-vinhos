# Decisões metodológicas — Tech Challenge Fase 2

## Alvo binário

O enunciado propõe separar `quality >= 7` de `quality < 7`. O projeto mantém `quality` no dataset bruto para auditoria e cria `high_quality` como alvo de modelagem.

## Deduplicação por perfil

O CSV bruto tem 1.143 registros e `Id` único, mas há 114 grupos de perfis com as mesmas 11 medições físico-químicas e a mesma `quality`, totalizando 239 linhas e 125 ocorrências redundantes. A fonte bruta não é sobrescrita. A pipeline mantém a primeira ocorrência de cada combinação de `FEATURE_COLUMNS + quality` e treina os modelos em 1.018 perfis únicos.

## Exclusão do `Id`

`Id` é único, não é uma medição físico-química e não aparece como variável de negócio no enunciado. Ele fica disponível para rastreabilidade, mas é removido da matriz de preditores. Usá-lo poderia permitir que o modelo aprendesse padrões artificiais de ordenação da base.

## Desbalanceamento

Há 137 perfis positivos em 1.018 perfis únicos (13,46%). O split é estratificado e os classificadores usam `class_weight` balanceado. O relatório prioriza Average Precision, precision, recall e F1, além de ROC-AUC; accuracy é apenas complementar.

## Modelos

- **Regressão Logística:** baseline interpretável, com imputação mediana e StandardScaler.
- **Random Forest:** modelo não linear capaz de capturar interações entre as variáveis, com imputação mediana e `class_weight="balanced_subsample"`.

Os modelos compartilham o mesmo split e a mesma seed para manter a comparação justa. O split é realizado depois da deduplicação.

## Escalonamento

O `StandardScaler` permanece no pipeline oficial da Regressão Logística. Na base limpa, o `MinMaxScaler` foi ligeiramente melhor no split de teste, mas as diferenças na validação cruzada foram pequenas e o `StandardScaler` teve Average Precision média de 0,546 contra 0,540. A tabela `results/tables/scaler_comparison.csv` registra os dois testes.

## Outliers

A EDA usa IQR para sinalizar extremos em `residual sugar`, `chlorides`, `fixed acidity` e `sulphates`. Nenhum registro é removido automaticamente: antes disso seria necessário confirmar se o valor representa erro de medição, condição legítima de produção ou uma população diferente.

## Interpretação

Correlação, coeficientes e importância de variável ajudam a explicar o comportamento do modelo, mas não demonstram causalidade. A recomendação é usar o classificador como triagem e apoio ao enólogo, com validação sensorial e calibração de threshold antes de qualquer decisão automatizada.

## Reprodutibilidade

Todas as execuções usam `random_state=42`. O `scripts/run_pipeline.py` gera `data/processed/WineQT_deduplicated.csv`, treina os modelos apenas nessa base limpa e produz `results/metrics.json` como fonte de verdade para as tabelas e a apresentação.
