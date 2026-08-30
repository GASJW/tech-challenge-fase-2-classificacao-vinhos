# Escalonamento das variáveis — StandardScaler vs MinMaxScaler

## Resumo executivo

`StandardScaler` e `MinMaxScaler` são técnicas de pré-processamento. Eles não
são modelos de Machine Learning e não calculam acurácia, recall ou qualquer
outra métrica. Seu papel é transformar as variáveis de entrada antes do
treinamento, colocando-as em escalas comparáveis.

No Tech Challenge 2, o `StandardScaler` foi mantido como pipeline oficial da
Regressão Logística. Depois da deduplicação, o `MinMaxScaler` ficou ligeiramente
melhor no split de teste, mas o `StandardScaler` teve Average Precision média
ligeiramente maior na validação cruzada. O Random Forest não utiliza
escalonamento, pois modelos baseados em árvores trabalham com pontos de corte e
não dependem da escala numérica das variáveis.

## Contexto da nossa base

- 1.143 registros brutos e 1.018 perfis únicos usados na modelagem.
- 11 variáveis físico-químicas usadas como preditores.
- `Id` excluído dos preditores por ser apenas identificador.
- `quality` excluída dos preditores para evitar *target leakage*.
- Alvo binário: `quality >= 7` representa alta qualidade.
- 137 perfis positivos, equivalentes a 13,46% da base limpa.
- Divisão treino/teste estratificada, com 20% para teste e `random_state=42`.

As variáveis possuem escalas diferentes. Por exemplo, `density` fica próxima de
1, `pH` fica em torno de 3 a 4 e `total sulfur dioxide` pode assumir valores
bem maiores. Sem tratamento, uma variável pode influenciar a otimização da
Regressão Logística apenas por sua escala numérica.

## O que é o StandardScaler

O `StandardScaler` realiza a padronização pelo *z-score*:

```text
valor_padronizado = (valor - média) / desvio padrão
```

O resultado fica aproximadamente com:

- média igual a 0;
- desvio padrão igual a 1;
- valores sem limite fixo entre 0 e 1.

Conceitualmente, ele responde:

> Quantos desvios padrão este valor está distante da média?

Essa transformação é adequada para a Regressão Logística porque facilita a
otimização e torna os coeficientes mais comparáveis entre variáveis.

## O que é o MinMaxScaler

O `MinMaxScaler` transforma os valores para uma faixa, normalmente de 0 a 1:

```text
valor_transformado = (valor - mínimo) / (máximo - mínimo)
```

Conceitualmente, ele responde:

> Onde este valor está localizado entre o menor e o maior valor observado?

Por depender diretamente do mínimo e do máximo, o MinMaxScaler pode ser muito
afetado por valores extremos. Como os outliers da nossa base foram sinalizados,
mas não removidos automaticamente, esses valores podem ampliar o intervalo e
comprimir as observações mais comuns em uma faixa estreita.

## Comparação experimental na base limpa

Mantivemos constantes:

- dataset;
- definição do alvo;
- divisão treino/teste;
- `random_state=42`;
- `class_weight="balanced"`;
- Regressão Logística;
- limiar de classificação de 0,5.

Alteramos somente o escalonador.

| Métrica no teste | StandardScaler | MinMaxScaler |
|---|---:|---:|
| Accuracy | 78,4% | **79,9%** |
| Precision | 35,6% | **37,9%** |
| Recall | 77,8% | **81,5%** |
| F1-score | 48,8% | **51,8%** |
| ROC-AUC | 0,882 | **0,890** |
| Average Precision | 0,441 | **0,462** |

### Leitura dos resultados

- No split de teste, o `MinMaxScaler` foi ligeiramente melhor nas métricas
  apresentadas.
- Na validação cruzada estratificada de cinco partes, o `StandardScaler` teve
  Average Precision média de 0,546, contra 0,540 do `MinMaxScaler`; recall médio
  foi 0,827 nos dois.
- As diferenças são pequenas. Por isso, a escolha do scaler deve considerar o
  protocolo de validação e a estabilidade, não apenas um único split.
- A comparação foi feita depois da deduplicação e está registrada em
  `results/tables/scaler_comparison.csv`.

## Por que o pipeline oficial mantém o StandardScaler

A decisão não é que o `StandardScaler` seja sempre superior. Na base limpa, o
`MinMaxScaler` venceu o split de teste, enquanto o `StandardScaler` teve Average
Precision média ligeiramente maior na validação cruzada. Como o objetivo é
manter uma comparação reprodutível e priorizar a ordenação da classe positiva,
o StandardScaler permanece no pipeline oficial e o resultado do MinMax fica
documentado como alternativa experimental.

A escolha também é coerente com a presença de valores extremos: o MinMaxScaler
usa diretamente os extremos para definir os limites da transformação. O
StandardScaler também pode ser influenciado por outliers, mas não força todas as
observações a caberem em uma faixa determinada pelo mínimo e pelo máximo.

## Fluxo correto para evitar leakage

O escalonador deve ser ajustado somente com os dados de treino:

```text
Base validada
    ↓
Separar X e y
    ↓
Dividir treino e teste
    ↓
Ajustar o scaler em X_train
    ↓
Transformar X_train e X_test com o mesmo scaler
    ↓
Treinar o modelo com X_train transformado
    ↓
Prever X_test transformado
    ↓
Calcular as métricas comparando y_pred com y_test
```

Não escalonamos `quality` nem `high_quality`. O escalonamento transforma apenas
as variáveis de entrada.

No código, o pipeline oficial é:

```python
Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        (
            "model",
            LogisticRegression(
                class_weight="balanced",
                max_iter=2000,
                random_state=42,
            ),
        ),
    ]
)
```

Embora a base atual não possua valores ausentes, a imputação mediana permanece
no pipeline como proteção para novas amostras e para manter o pré-processamento
encapsulado junto ao modelo.

## Relação com o cálculo do recall

O escalonamento acontece antes do treinamento. O recall só é calculado depois
que o modelo faz previsões:

```python
from sklearn.metrics import recall_score

y_pred = model.predict(X_test)
recall = recall_score(y_test, y_pred, pos_label=1)
```

O recall da classe positiva é:

```text
Recall = verdadeiros positivos / (verdadeiros positivos + falsos negativos)
```

Portanto, o `StandardScaler` não calcula nem torna o recall mais relevante. O
recall é relevante porque a classe alta qualidade é minoritária e queremos
medir quantos vinhos realmente bons o modelo consegue encontrar.

## Relação com os outliers

Os outliers foram identificados por IQR, mas não removidos automaticamente. Eles
podem ser erros de medição, mas também podem representar condições legítimas de
produção ou uma população diferente.

Consequências para o escalonamento:

- `MinMaxScaler`: pode sofrer forte influência dos mínimos e máximos extremos.
- `StandardScaler`: pode sofrer influência da média e do desvio padrão, mas não
  fica limitado diretamente aos extremos da faixa.
- Random Forest: não precisa de escalonamento e tende a ser mais robusto à
  escala das variáveis.

A decisão atual é manter os outliers até que uma análise de domínio confirme se
eles são erros ou observações reais.

## Decisão final do projeto

```text
Base de modelagem    → deduplicação por `FEATURE_COLUMNS + quality`, 1.018 perfis
Regressão Logística  → imputação mediana + StandardScaler
Random Forest        → imputação mediana, sem escalonamento
```

Frase recomendada para a apresentação:

> Testamos o StandardScaler e o MinMaxScaler depois da deduplicação. No split de
> teste, o MinMaxScaler foi ligeiramente superior; na validação cruzada, o
> StandardScaler teve Average Precision média um pouco maior. Como a diferença é
> pequena, mantivemos o StandardScaler no pipeline oficial por estabilidade e
> registramos o MinMaxScaler como alternativa.

## Referências internas

- [Decisões metodológicas](decisoes-metodologicas.md)
- [Implementação dos modelos](../src/wine_quality/modeling.py)
- [Métricas oficiais](../results/metrics.json)
