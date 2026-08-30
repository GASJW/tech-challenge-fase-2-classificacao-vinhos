# Roteiro — Vídeo Executivo do Tech Challenge 2

**Duração-alvo:** até 5 minutos<br>
**Público:** diretoria, liderança de qualidade e produção<br>
**Linguagem:** executiva, sem depender de termos técnicos

## 0:00–0:30 — Problema

“A avaliação da qualidade de um vinho depende da experiência de especialistas, pode consumir tempo e está sujeita a variações de julgamento. Nosso projeto investiga se medições físico-químicas simples conseguem indicar quais amostras merecem atenção prioritária.”

## 0:30–1:10 — Base analisada

“Trabalhamos com 1.143 registros brutos e 11 medições, como acidez, açúcar residual, sulfatos e teor alcoólico. A auditoria encontrou 114 grupos de perfis repetidos; mantivemos uma ocorrência por perfil e treinamos os modelos em 1.018 perfis únicos. Para transformar a pergunta em uma decisão objetiva, classificamos como alta qualidade uma nota igual ou superior a 7. Esse grupo tem 137 perfis, 13,5% da base limpa.”

## 1:10–2:00 — O que os dados mostram

“A distribuição continua concentrada nas notas 5 e 6. Isso significa que um sistema que sempre escolhesse a categoria mais comum pareceria preciso, mas falharia justamente no grupo de maior interesse. Nos perfis únicos, maior teor alcoólico aparece relacionado a notas melhores, com correlação de 0,486, enquanto maior acidez volátil aparece relacionada a notas menores, com menos 0,409. Essas relações orientam a análise, mas não provam causa.”

## 2:00–3:00 — Comparação dos modelos

“Comparamos dois modelos. A Regressão Logística encontra relações mais simples e identificou 77,8% dos perfis de alta qualidade, mas trouxe mais falsos positivos. O Random Forest teve o melhor equilíbrio: acertou 90,2% das classificações, alcançou precisão de 73,3% entre as amostras indicadas e obteve Average Precision de 0,692.”

“Na prática, o modelo não deve ser lido como um certificado automático. Ele é um filtro para priorizar inspeções e reduzir o esforço de análise.”

## 3:00–4:10 — Recomendação de negócio

“Nossa recomendação é adotar o Random Forest como candidato para uma etapa de triagem. A equipe pode direcionar primeiro as amostras com maior probabilidade de alta qualidade, mantendo a validação sensorial como decisão final. Se o custo de deixar passar uma amostra boa for maior que o custo de revisar amostras adicionais, o limiar de decisão deve ser reduzido e recalibrado.”

“O benefício esperado é organizar a fila de avaliação, acelerar a identificação de lotes promissores e criar uma base objetiva para discutir o processo produtivo.”

## 4:10–5:00 — Limitações e próximos passos

“O estudo ainda é um protótipo. A base não contém lote, região, processo produtivo, custos ou todas as dimensões sensoriais. A fonte bruta foi preservada e a modelagem foi feita após a deduplicação por perfil; ainda assim, recomendamos validar o comportamento em novos lotes antes de automatizar qualquer decisão.”

“Os próximos passos são calibrar o limiar com os custos reais, testar o modelo em novos lotes, incorporar variáveis do processo e acompanhar a concordância com a avaliação dos especialistas. A mensagem final é simples: os dados já ajudam a priorizar a análise, mas a decisão de qualidade continua sendo humana e validada.”
