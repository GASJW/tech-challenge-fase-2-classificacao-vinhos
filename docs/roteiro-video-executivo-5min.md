# Roteiro — Vídeo Executivo do Tech Challenge 2

**Duração-alvo:** até 5 minutos<br>
**Público:** diretoria, liderança de qualidade e produção<br>
**Linguagem:** executiva, sem depender de termos técnicos

## 0:00–0:30 — Problema

“A avaliação da qualidade de um vinho depende da experiência de especialistas, pode consumir tempo e está sujeita a variações de julgamento. Nosso projeto investiga se medições físico-químicas simples conseguem indicar quais amostras merecem atenção prioritária.”

## 0:30–1:10 — Base analisada

“Trabalhamos com 1.143 amostras e 11 medições, como acidez, açúcar residual, sulfatos e teor alcoólico. Para transformar a pergunta em uma decisão objetiva, classificamos como alta qualidade uma nota igual ou superior a 7. Esse grupo tem 159 amostras, apenas 13,9% da base.”

## 1:10–2:00 — O que os dados mostram

“A distribuição é concentrada nas notas 5 e 6. Isso significa que um sistema que sempre escolhesse a categoria mais comum pareceria preciso, mas falharia justamente no grupo de maior interesse. Nas associações observadas, maior teor alcoólico aparece relacionado a notas melhores, enquanto maior acidez volátil aparece relacionado a notas menores. Essas relações orientam a análise, mas não provam causa.”

## 2:00–3:00 — Comparação dos modelos

“Comparamos dois modelos. A Regressão Logística encontra relações mais simples e identificou 68,8% das amostras de alta qualidade, mas trouxe mais falsos positivos. O Random Forest teve o melhor equilíbrio: acertou 91,3% das classificações, alcançou precisão de 73,1% entre as amostras indicadas e obteve Average Precision de 0,709.”

“Na prática, o modelo não deve ser lido como um certificado automático. Ele é um filtro para priorizar inspeções e reduzir o esforço de análise.”

## 3:00–4:10 — Recomendação de negócio

“Nossa recomendação é adotar o Random Forest como candidato para uma etapa de triagem. A equipe pode direcionar primeiro as amostras com maior probabilidade de alta qualidade, mantendo a validação sensorial como decisão final. Se o custo de deixar passar uma amostra boa for maior que o custo de revisar amostras adicionais, o limiar de decisão deve ser reduzido e recalibrado.”

“O benefício esperado é organizar a fila de avaliação, acelerar a identificação de lotes promissores e criar uma base objetiva para discutir o processo produtivo.”

## 4:10–5:00 — Limitações e próximos passos

“O estudo ainda é um protótipo. A base não contém lote, região, processo produtivo, custos ou todas as dimensões sensoriais. Por isso, não recomendamos automatizar aprovação de produto com os resultados atuais.”

“Os próximos passos são calibrar o limiar com os custos reais, testar o modelo em novos lotes, incorporar variáveis do processo e acompanhar a concordância com a avaliação dos especialistas. A mensagem final é simples: os dados já ajudam a priorizar a análise, mas a decisão de qualidade continua sendo humana e validada.”
