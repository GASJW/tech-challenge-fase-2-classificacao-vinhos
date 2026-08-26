# Decisões metodológicas — Tech Challenge Fase 2

## Alvo binário

O enunciado propõe separar `quality >= 7` de `quality < 7`. O projeto mantém `quality` no dataset bruto para auditoria e cria `high_quality` como alvo de modelagem.

## Exclusão do `Id`

`Id` é único, não é uma medição físico-química e não aparece como variável de negócio no enunciado. Ele fica disponível para rastreabilidade, mas é removido da matriz de preditores. Usá-lo poderia permitir que o modelo aprendesse padrões artificiais de ordenação da base.

## Desbalanceamento

Há 159 amostras positivas em 1.143 registros (13,91%). O split é estratificado e os classificadores usam `class_weight` balanceado. O relatório prioriza Average Precision, precision, recall e F1, além de ROC-AUC; accuracy é apenas complementar.

## Modelos

- **Regressão Logística:** baseline interpretável, com imputação mediana e StandardScaler.
- **Random Forest:** modelo não linear capaz de capturar interações entre as variáveis, com imputação mediana e `class_weight="balanced_subsample"`.

Os modelos compartilham o mesmo split e a mesma seed para manter a comparação justa.

## Outliers

A EDA usa IQR para sinalizar extremos em `residual sugar`, `chlorides`, `fixed acidity` e `sulphates`. Nenhum registro é removido automaticamente: antes disso seria necessário confirmar se o valor representa erro de medição, condição legítima de produção ou uma população diferente.

## Interpretação

Correlação, coeficientes e importância de variável ajudam a explicar o comportamento do modelo, mas não demonstram causalidade. A recomendação é usar o classificador como triagem e apoio ao enólogo, com validação sensorial e calibração de threshold antes de qualquer decisão automatizada.

## Reprodutibilidade

Todas as execuções usam `random_state=42`. O `results/metrics.json` é gerado pelo pipeline e serve como fonte de verdade para as tabelas e a apresentação.
