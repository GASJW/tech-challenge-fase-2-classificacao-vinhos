"""Gera a apresentação executiva HTML autocontida do Tech Challenge 2."""

from __future__ import annotations

import base64
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT_ROOT / "results"
FIGURES = RESULTS / "figures"
OUTPUT = PROJECT_ROOT / "presentation" / "tech-challenge-2-executiva.html"


def fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%".replace(".", ",")


def fmt_num(value: float) -> str:
    return f"{value:.3f}".replace(".", ",")


def image_data_uri(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Figura não encontrada: {path}")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def build_replacements(metrics: dict) -> dict[str, str]:
    dataset = metrics["dataset"]
    logistic = metrics["models"]["logistic_regression"]["test"]
    forest = metrics["models"]["random_forest"]["test"]

    replacement = {
        "__ROWS__": f"{dataset['rows']:,}".replace(",", "."),
        "__FEATURES__": str(dataset["feature_count"]),
        "__POSITIVE__": str(dataset["positive_count"]),
        "__POS_RATE__": fmt_pct(dataset["positive_rate"]),
        "__FOREST_PRECISION__": fmt_pct(forest["precision"]),
        "__FOREST_RECALL__": fmt_pct(forest["recall"]),
        "__FOREST_F1__": fmt_pct(forest["f1"]),
        "__FOREST_ROC__": fmt_num(forest["roc_auc"]),
        "__FOREST_AP__": fmt_num(forest["average_precision"]),
        "__LOG_PRECISION__": fmt_pct(logistic["precision"]),
        "__LOG_RECALL__": fmt_pct(logistic["recall"]),
        "__LOG_F1__": fmt_pct(logistic["f1"]),
        "__LOG_ROC__": fmt_num(logistic["roc_auc"]),
        "__LOG_AP__": fmt_num(logistic["average_precision"]),
        "__IMG_TARGET__": image_data_uri(FIGURES / "target_distribution.png"),
        "__IMG_CORRELATION__": image_data_uri(FIGURES / "correlation_heatmap.png"),
        "__IMG_MODELS__": image_data_uri(FIGURES / "model_comparison.png"),
    }
    return replacement


HTML_TEMPLATE = r'''<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#0B0B0F">
  <meta name="description" content="Apresentação executiva do Tech Challenge 2 sobre classificação da qualidade de vinhos.">
  <title>FIAP · Qualidade de vinhos · Tech Challenge 2</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --fiap-magenta: #ED145B;
      --magenta-bright: #FF1E6E;
      --magenta-deep: #B00C44;
      --preto: #0B0B0F;
      --grafite: #16171F;
      --grafite-2: #1D1E28;
      --linha: #2A2C38;
      --branco: #FFFFFF;
      --nevoa: #A9ACBC;
      --verde: #2BB673;
      --amarelo: #F5A623;
      --slide-pad: clamp(1.45rem, 4.5vw, 4.8rem);
    }

    * { box-sizing: border-box; }
    html, body { margin: 0; min-height: 100%; background: var(--preto); }
    body {
      color: var(--branco);
      font-family: "Inter", system-ui, sans-serif;
      overflow: hidden;
      -webkit-font-smoothing: antialiased;
    }
    button { font: inherit; }
    .deck { position: relative; min-height: 100vh; }
    .slide {
      display: none;
      min-height: 100vh;
      padding: 2.2rem var(--slide-pad) 4.5rem;
      position: relative;
      overflow: hidden;
      background:
        radial-gradient(80rem 38rem at 95% -10%, rgba(237, 20, 91, .12), transparent 58%),
        var(--preto);
    }
    .slide.active { display: flex; flex-direction: column; }
    .slide::after {
      content: "";
      position: absolute;
      width: 20rem;
      height: 20rem;
      right: -13rem;
      bottom: -12rem;
      border: 1px solid rgba(237, 20, 91, .18);
      transform: rotate(45deg);
      pointer-events: none;
    }
    .cover { background: radial-gradient(60rem 40rem at 88% 18%, rgba(237,20,91,.25), transparent 58%), var(--preto); }
    .cover::before {
      content: "";
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: .42rem;
      background: var(--fiap-magenta);
    }
    .slide-inner { width: min(100%, 80rem); margin: auto; position: relative; z-index: 1; }
    .topline { display: flex; justify-content: space-between; gap: 1rem; align-items: center; }
    .brand {
      color: var(--fiap-magenta);
      font-family: "Sora", sans-serif;
      font-size: .85rem;
      font-weight: 800;
      letter-spacing: .13em;
      text-transform: uppercase;
    }
    .brand span { color: var(--nevoa); font-size: .72em; letter-spacing: .08em; }
    .slide-no { color: var(--nevoa); font: 600 .72rem "Sora", sans-serif; letter-spacing: .12em; }
    .rule { height: 1px; margin: 1rem 0 3.2rem; background: var(--linha); }
    .eyebrow, .section-label {
      color: var(--fiap-magenta);
      font: 700 .74rem "Sora", sans-serif;
      letter-spacing: .14em;
      text-transform: uppercase;
    }
    .section-label::before { content: "»"; margin-right: .45rem; font-size: 1.2em; }
    h1, h2, h3 { margin: 0; font-family: "Sora", sans-serif; line-height: 1.08; letter-spacing: -.04em; }
    h1 { font-size: clamp(3.4rem, 10vw, 8.4rem); font-weight: 800; }
    h2 { max-width: 45rem; font-size: clamp(2rem, 4vw, 4rem); font-weight: 700; }
    h3 { font-size: clamp(1.1rem, 1.8vw, 1.55rem); }
    p { margin: 0; }
    .muted { color: var(--nevoa); }
    .magenta { color: var(--fiap-magenta); }
    .lead { color: #D9DBE6; font-size: clamp(1.05rem, 1.8vw, 1.4rem); line-height: 1.45; }
    .claim { max-width: 38rem; margin-top: 1.5rem; color: #E5E6EE; font-size: clamp(1.15rem, 2.3vw, 1.85rem); line-height: 1.3; }
    .cover-grid { display: grid; grid-template-columns: 1.15fr .85fr; gap: clamp(2rem, 8vw, 8rem); align-items: center; }
    .cover h1 span { color: var(--fiap-magenta); }
    .cover-card { justify-self: end; width: min(100%, 21rem); padding: 2.5rem 1.5rem; background: var(--fiap-magenta); color: var(--preto); text-align: center; }
    .cover-card .cut { font: 800 clamp(7rem, 13vw, 11rem) "Sora", sans-serif; line-height: .8; }
    .cover-card .label { margin-top: 1.5rem; font: 800 .74rem "Sora", sans-serif; letter-spacing: .12em; }
    .cover-card p { margin-top: 1.15rem; font-weight: 700; line-height: 1.3; }
    code { font: 600 .9em "Sora", sans-serif; }
    .meta { margin-top: 3.8rem; color: var(--nevoa); font-size: .82rem; }
    .section-head { display: flex; flex-direction: column; gap: .85rem; margin-bottom: 2rem; }
    .section-head .lead { max-width: 52rem; }
    .kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 2.4rem 0; }
    .kpi { min-height: 8.5rem; padding: 1.35rem; border: 1px solid var(--linha); border-top: 3px solid var(--fiap-magenta); background: var(--grafite); }
    .kpi .value { color: var(--branco); font: 800 clamp(1.8rem, 3vw, 2.8rem) "Sora", sans-serif; line-height: 1; }
    .kpi:first-child .value, .kpi:nth-child(2) .value { color: var(--fiap-magenta); }
    .kpi .label { display: block; margin-top: .8rem; color: var(--nevoa); font-size: .83rem; line-height: 1.35; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1.3rem; align-items: stretch; }
    .two-col.wide-left { grid-template-columns: 1.25fr .75fr; }
    .two-col.wide-right { grid-template-columns: .75fr 1.25fr; }
    .card { padding: 1.35rem 1.5rem; background: var(--grafite); border: 1px solid var(--linha); }
    .card.accent { border-left: 4px solid var(--fiap-magenta); }
    .card.green { border-left: 4px solid var(--verde); }
    .card h3 { margin-bottom: .8rem; }
    .card p, .card li { color: var(--nevoa); font-size: .93rem; line-height: 1.5; }
    ul.arrow-list { list-style: none; padding: 0; margin: 0; }
    ul.arrow-list li { position: relative; padding: .7rem 0 .7rem 1.7rem; border-bottom: 1px dashed var(--linha); }
    ul.arrow-list li::before { content: "›"; position: absolute; left: .2rem; top: .55rem; color: var(--fiap-magenta); font: 800 1.35rem "Sora", sans-serif; }
    .chart { min-width: 0; padding: .8rem; background: var(--grafite); border: 1px solid var(--linha); }
    .chart img { display: block; width: 100%; height: auto; border-radius: .35rem; }
    .chart.compact img { max-height: 23rem; object-fit: contain; }
    .chart.tiny img { max-height: 16rem; object-fit: contain; }
    #slide-3 .chart.compact img { max-height: 19rem; }
    .chart figcaption { margin-top: .55rem; color: var(--nevoa); font-size: .76rem; text-align: center; }
    .callout { margin-top: 1.2rem; padding: 1.15rem 1.35rem; border-left: 4px solid var(--fiap-magenta); background: linear-gradient(90deg, rgba(237,20,91,.14), transparent); }
    .callout strong { color: var(--fiap-magenta); }
    .big-number { color: var(--fiap-magenta); font: 800 clamp(2.8rem, 5vw, 5rem) "Sora", sans-serif; line-height: .95; }
    .big-number.muted-number { color: var(--nevoa); }
    .stat-pair { display: grid; grid-template-columns: 1fr 1fr; gap: 1.4rem; margin: 1rem 0 1.5rem; }
    .stat-pair .stat { padding: 1rem 0; border-bottom: 1px solid var(--linha); }
    .stat .caption { margin-top: .45rem; font-size: .88rem; color: var(--nevoa); }
    .corr-list { display: grid; gap: .65rem; margin-top: 1.2rem; }
    .corr-row { display: grid; grid-template-columns: minmax(9rem, 1fr) 5rem; gap: .8rem; align-items: center; }
    .corr-row .name { font: 600 .9rem "Sora", sans-serif; }
    .corr-row .score { color: var(--fiap-magenta); font: 800 1rem "Sora", sans-serif; text-align: right; }
    .bar { height: .32rem; margin-top: .2rem; background: var(--linha); }
    .bar i { display: block; height: 100%; background: var(--fiap-magenta); }
    .bar i.negative { background: var(--verde); }
    .model-table { width: 100%; border-collapse: collapse; margin-top: .6rem; font-size: .86rem; }
    .model-table th, .model-table td { padding: .8rem .7rem; border-bottom: 1px solid var(--linha); text-align: right; }
    .model-table th:first-child, .model-table td:first-child { text-align: left; }
    .model-table th { color: var(--nevoa); font: 600 .72rem "Sora", sans-serif; letter-spacing: .04em; text-transform: uppercase; }
    .model-table td { color: #E9EAF0; }
    .model-table tr:last-child td { background: rgba(237, 20, 91, .13); color: var(--branco); font-weight: 700; }
    .model-table tr:last-child td:first-child { color: var(--fiap-magenta); }
    .flow { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2rem; align-items: stretch; margin-top: 2rem; }
    .flow-card { position: relative; min-height: 12rem; padding: 1.5rem; background: var(--grafite); border: 1px solid var(--linha); }
    .flow-card:not(:last-child)::after { content: "→"; position: absolute; right: -1.1rem; top: 4.6rem; z-index: 2; color: var(--fiap-magenta); font: 800 1.6rem "Sora", sans-serif; }
    .flow-card .number { color: var(--fiap-magenta); font: 800 1.15rem "Sora", sans-serif; }
    .flow-card h3 { margin-top: 1.1rem; }
    .flow-card p { margin-top: .6rem; color: var(--nevoa); font-size: .9rem; line-height: 1.45; }
    .decision { margin-top: 2rem; padding: 1.5rem; background: var(--fiap-magenta); color: var(--preto); }
    .decision .kicker { font: 800 .75rem "Sora", sans-serif; letter-spacing: .12em; text-transform: uppercase; }
    .decision p { margin-top: .5rem; font: 800 clamp(1.2rem, 2.2vw, 1.8rem) "Sora", sans-serif; line-height: 1.2; }
    .closing { display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; margin-top: 1.5rem; }
    .closing h3 { margin-bottom: 1rem; }
    .footer { position: absolute; right: var(--slide-pad); bottom: 2.35rem; left: var(--slide-pad); display: flex; justify-content: space-between; gap: 1rem; color: var(--nevoa); font-size: .72rem; }
    .progress { position: fixed; right: 0; bottom: 0; left: 0; z-index: 10; height: .22rem; background: var(--linha); }
    .progress i { display: block; width: 12.5%; height: 100%; background: var(--fiap-magenta); transition: width .25s ease; }
    .controls { position: fixed; right: 1.2rem; bottom: 1.05rem; z-index: 11; display: flex; gap: .4rem; }
    .controls button { width: 2.2rem; height: 2.2rem; color: var(--branco); background: rgba(22,23,31,.9); border: 1px solid var(--linha); cursor: pointer; }
    .controls button:hover, .controls button:focus-visible { color: var(--fiap-magenta); border-color: var(--fiap-magenta); outline: none; }
    .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
    @media (max-width: 800px) {
      body { overflow: auto; }
      .slide, .slide.active { min-height: 100svh; overflow: visible; }
      .cover-grid, .two-col, .two-col.wide-left, .two-col.wide-right, .closing { grid-template-columns: 1fr; }
      .cover-card { justify-self: start; max-width: 15rem; padding: 1.4rem; }
      .cover-card .cut { font-size: 5.2rem; }
      .meta { margin-top: 2rem; }
      .kpis { grid-template-columns: repeat(2, 1fr); }
      .flow { grid-template-columns: 1fr; }
      .flow-card:not(:last-child)::after { right: auto; top: auto; bottom: -1.25rem; left: 50%; transform: rotate(90deg); }
      .rule { margin-bottom: 2rem; }
      .model-table { font-size: .72rem; }
      .model-table th, .model-table td { padding: .55rem .3rem; }
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; }
    }
    @media print {
      body { overflow: visible; background: #fff; }
      .slide, .slide.active { display: flex; min-height: 100vh; height: 100vh; page-break-after: always; color: #14151C; }
      .slide { background: #fff; }
      .slide::after, .controls, .progress { display: none; }
      .brand, .eyebrow, .section-label, .magenta, .big-number, .kpi:first-child .value, .kpi:nth-child(2) .value { color: #B00C44; }
      .muted, .lead, .card p, .card li, .chart figcaption, .footer, .stat .caption { color: #5B5E6E; }
      .card, .chart, .kpi, .flow-card { background: #F4F5F8; border-color: #E7E8EE; }
      .callout { background: #FDE8EF; }
    }
  </style>
</head>
<body>
  <main class="deck" aria-live="polite">
    <section class="slide cover active" id="slide-1" aria-label="Capa">
      <div class="slide-inner cover-grid">
        <div>
          <div class="brand">FIAP <span>/ POSTECH</span></div>
          <div class="eyebrow" style="margin-top: 4.3rem;">Tech Challenge 2 · Machine Learning</div>
          <h1 style="margin-top: 1.1rem;">QUALIDADE<br><span>DE VINHOS</span></h1>
          <p class="claim">Classificar é priorizar. A base físico-química encontra os sinais; o especialista fecha a decisão.</p>
          <p class="meta">Guilherme Augusto · 06.08.2026</p>
        </div>
        <div class="cover-card" aria-label="Nota de corte do projeto">
          <div class="cut">7</div>
          <div class="label">Nota de corte</div>
          <p>Alta qualidade<br><code>quality &gt;= 7</code></p>
        </div>
      </div>
      <div class="footer"><span>Classificação binária com Machine Learning</span><span>01 / 08</span></div>
    </section>

    <section class="slide" id="slide-2" aria-label="Problema e base">
      <div class="slide-inner">
        <div class="topline"><div class="brand">FIAP <span>/ POSTECH</span></div><div class="slide-no">TECH CHALLENGE 2 · 02</div></div>
        <div class="rule"></div>
        <div class="section-head"><div class="section-label">Contexto</div><h2>A decisão começa pelo rótulo</h2><p class="lead">A pergunta é objetiva: podemos priorizar amostras com maior probabilidade de alta qualidade antes da avaliação sensorial?</p></div>
        <div class="kpis">
          <div class="kpi"><div class="value">__ROWS__</div><span class="label">amostras analisadas</span></div>
          <div class="kpi"><div class="value">__POS_RATE__</div><span class="label">alta qualidade (`quality &gt;= 7`)</span></div>
          <div class="kpi"><div class="value">__FEATURES__</div><span class="label">variáveis físico-químicas</span></div>
          <div class="kpi"><div class="value">0</div><span class="label">valores ausentes na base</span></div>
        </div>
        <div class="two-col">
          <div class="card accent"><h3>Contrato analítico</h3><ul class="arrow-list"><li><strong>Id</strong> preservado para rastreabilidade, excluído do treinamento.</li><li><strong>quality</strong> usada para criar o alvo, fora das features.</li><li>Split treino/teste estratificado para respeitar a classe minoritária.</li></ul></div>
          <div class="card"><h3>Saneamento sem apagar sinal</h3><p>Não removemos observações. Outliers foram sinalizados por IQR para investigação de domínio; a decisão de excluir um valor precisa distinguir erro de medição de condição real de produção.</p><div class="callout"><strong>Resultado:</strong> a base chega consistente à EDA e à modelagem.</div></div>
        </div>
      </div>
      <div class="footer"><span>Fonte: WineQT.csv · auditoria inicial</span><span>02 / 08</span></div>
    </section>

    <section class="slide" id="slide-3" aria-label="Distribuição do alvo">
      <div class="slide-inner">
        <div class="topline"><div class="brand">FIAP <span>/ POSTECH</span></div><div class="slide-no">TECH CHALLENGE 2 · 03</div></div>
        <div class="rule"></div>
        <div class="section-head"><div class="section-label">Diagnóstico</div><h2>A classe de interesse é minoritária</h2><p class="lead">A nota original tem seis valores observados — 3 a 8. O desafio transforma essa escala em uma decisão binária.</p></div>
        <div class="two-col wide-left">
          <figure class="chart compact"><img src="__IMG_TARGET__" alt="Distribuição das classes baixa/média e alta qualidade"><figcaption>Distribuição do alvo binário: alta qualidade é a classe positiva.</figcaption></figure>
          <div>
            <div class="stat-pair"><div class="stat"><div class="big-number muted-number">86,1%</div><div class="caption">baixa/média qualidade<br>984 amostras</div></div><div class="stat"><div class="big-number">13,9%</div><div class="caption">alta qualidade<br>__POSITIVE__ amostras</div></div></div>
            <div class="card accent"><h3>Implicação de negócio</h3><p>Accuracy isolada pode parecer alta mesmo ignorando a classe de interesse. Por isso, a avaliação prioriza precision, recall, F1, ROC-AUC e Average Precision.</p></div>
          </div>
        </div>
        <div class="callout"><strong>Recorte adotado:</strong> `quality &lt; 7` = baixa/média · `quality &gt;= 7` = alta qualidade.</div>
      </div>
      <div class="footer"><span>Alvo binário definido pelo enunciado</span><span>03 / 08</span></div>
    </section>

    <section class="slide" id="slide-4" aria-label="Correlações e sinais">
      <div class="slide-inner">
        <div class="topline"><div class="brand">FIAP <span>/ POSTECH</span></div><div class="slide-no">TECH CHALLENGE 2 · 04</div></div>
        <div class="rule"></div>
        <div class="section-head"><div class="section-label">Sinais</div><h2>Álcool e acidez organizam o sinal preditivo</h2><p class="lead">Na correlação linear com a nota original, dois indicadores concentram o sinal mais forte da base.</p></div>
        <div class="two-col wide-left">
          <figure class="chart compact"><img src="__IMG_CORRELATION__" alt="Heatmap de correlação entre propriedades físico-químicas e quality"><figcaption>Correlação de Pearson com `quality`; associação não implica causalidade.</figcaption></figure>
          <div>
            <div class="corr-list">
              <div class="corr-row"><div><span class="name">alcohol</span><div class="bar"><i style="width: 100%;"></i></div></div><div class="score">+0,485</div></div>
              <div class="corr-row"><div><span class="name">volatile acidity</span><div class="bar"><i class="negative" style="width: 84%;"></i></div></div><div class="score">−0,407</div></div>
              <div class="corr-row"><div><span class="name">sulphates</span><div class="bar"><i style="width: 53%;"></i></div></div><div class="score">+0,258</div></div>
              <div class="corr-row"><div><span class="name">citric acid</span><div class="bar"><i style="width: 50%;"></i></div></div><div class="score">+0,241</div></div>
            </div>
            <div class="card accent" style="margin-top: 1.4rem;"><h3>Leitura executiva</h3><p>Mais álcool aparece associado a notas maiores. Mais acidez volátil aparece associada a notas menores. Sulfatos e ácido cítrico formam o segundo bloco de sinais positivos.</p></div>
          </div>
        </div>
      </div>
      <div class="footer"><span>EDA · correlação linear e interpretação preditiva</span><span>04 / 08</span></div>
    </section>

    <section class="slide" id="slide-5" aria-label="Comparação de modelos">
      <div class="slide-inner">
        <div class="topline"><div class="brand">FIAP <span>/ POSTECH</span></div><div class="slide-no">TECH CHALLENGE 2 · 05</div></div>
        <div class="rule"></div>
        <div class="section-head"><div class="section-label">Modelagem</div><h2>Random Forest entrega o melhor equilíbrio</h2><p class="lead">O modelo não linear supera o baseline na precisão e na capacidade de ordenar as amostras promissoras.</p></div>
        <div class="two-col wide-right">
          <div>
            <table class="model-table" aria-label="Comparação de métricas dos modelos"><thead><tr><th>Modelo</th><th>Precision</th><th>Recall</th><th>F1</th><th>ROC-AUC</th><th>Avg Precision</th></tr></thead><tbody><tr><td>Regressão Logística</td><td>__LOG_PRECISION__</td><td>__LOG_RECALL__</td><td>__LOG_F1__</td><td>__LOG_ROC__</td><td>__LOG_AP__</td></tr><tr><td>Random Forest</td><td>__FOREST_PRECISION__</td><td>__FOREST_RECALL__</td><td>__FOREST_F1__</td><td>__FOREST_ROC__</td><td>__FOREST_AP__</td></tr></tbody></table>
            <div class="callout"><strong>Escolha principal:</strong> Random Forest combina __FOREST_PRECISION__ de precisão, ROC-AUC __FOREST_ROC__ e Average Precision __FOREST_AP__ no teste.</div>
          </div>
          <figure class="chart tiny"><img src="__IMG_MODELS__" alt="Comparação visual das métricas dos modelos"><figcaption>Métricas no conjunto de teste; a classe positiva é alta qualidade.</figcaption></figure>
        </div>
        <div class="card" style="margin-top: 1.25rem;"><p><strong>Trade-off:</strong> a Regressão Logística alcança recall de __LOG_RECALL__ — útil quando perder um positivo é mais caro — mas gera mais falsos positivos e apresenta Average Precision de __LOG_AP__.</p></div>
      </div>
      <div class="footer"><span>Split estratificado · random_state 42 · 5-fold CV</span><span>05 / 08</span></div>
    </section>

    <section class="slide" id="slide-6" aria-label="Custo do erro">
      <div class="slide-inner">
        <div class="topline"><div class="brand">FIAP <span>/ POSTECH</span></div><div class="slide-no">TECH CHALLENGE 2 · 06</div></div>
        <div class="rule"></div>
        <div class="section-head"><div class="section-label">Decisão</div><h2>A escolha do modelo depende do custo do erro</h2><p class="lead">Precisão evita revisar amostras demais. Recall reduz o risco de deixar uma amostra promissora passar.</p></div>
        <div class="two-col">
          <div class="card accent"><h3>RANDOM FOREST · mais seletivo</h3><div class="stat-pair"><div class="stat"><div class="big-number">__FOREST_PRECISION__</div><div class="caption">precision</div></div><div class="stat"><div class="big-number">__FOREST_RECALL__</div><div class="caption">recall</div></div></div><p>Bom candidato para uma fila de triagem com capacidade limitada de revisão.</p></div>
          <div class="card green"><h3>REGRESSÃO LOGÍSTICA · mais abrangente</h3><div class="stat-pair"><div class="stat"><div class="big-number muted-number">__LOG_PRECISION__</div><div class="caption">precision</div></div><div class="stat"><div class="big-number muted-number">__LOG_RECALL__</div><div class="caption">recall</div></div></div><p>Captura mais positivos, aceitando revisar mais amostras classificadas como alta qualidade.</p></div>
        </div>
        <div class="callout"><strong>Não existe vencedor universal:</strong> o threshold deve refletir o custo de cada erro e a capacidade operacional de revisão.</div>
      </div>
      <div class="footer"><span>Precision e recall traduzidos para a decisão</span><span>06 / 08</span></div>
    </section>

    <section class="slide" id="slide-7" aria-label="Recomendação">
      <div class="slide-inner">
        <div class="topline"><div class="brand">FIAP <span>/ POSTECH</span></div><div class="slide-no">TECH CHALLENGE 2 · 07</div></div>
        <div class="rule"></div>
        <div class="section-head"><div class="section-label">Recomendação</div><h2>Recomendação: triagem com revisão humana</h2><p class="lead">O modelo organiza a fila de análise. A aprovação continua com o especialista.</p></div>
        <div class="flow">
          <div class="flow-card"><div class="number">01</div><h3>Pontuar</h3><p>Medições físico-químicas entram no Random Forest e geram uma probabilidade.</p></div>
          <div class="flow-card"><div class="number">02</div><h3>Priorizar</h3><p>Amostras com maior score entram primeiro na fila de avaliação sensorial.</p></div>
          <div class="flow-card"><div class="number">03</div><h3>Validar</h3><p>O enólogo confirma a qualidade antes de uma decisão produtiva.</p></div>
        </div>
        <div class="decision"><div class="kicker">Decisão de negócio</div><p>O modelo organiza a fila. O especialista continua responsável pela aprovação.</p></div>
        <div class="two-col" style="margin-top: 1.4rem;"><div class="card accent"><h3>Por que agora?</h3><p>O teste já mostra separação útil: Average Precision de __FOREST_AP__ e ROC-AUC de __FOREST_ROC__.</p></div><div class="card"><h3>O que ainda falta?</h3><p>Calibrar o threshold, validar em lotes futuros e medir a concordância com especialistas.</p></div></div>
      </div>
      <div class="footer"><span>Recomendação executiva</span><span>07 / 08</span></div>
    </section>

    <section class="slide" id="slide-8" aria-label="Próximos passos e limitações">
      <div class="slide-inner">
        <div class="topline"><div class="brand">FIAP <span>/ POSTECH</span></div><div class="slide-no">TECH CHALLENGE 2 · 08</div></div>
        <div class="rule"></div>
        <div class="section-head"><div class="section-label">Próximo movimento</div><h2>O próximo passo é validar no mundo real</h2><p class="lead">O resultado é um ponto de partida sólido — não uma decisão automática pronta.</p></div>
        <div class="closing">
          <div class="card accent"><h3>Agora</h3><ul class="arrow-list"><li>Calibrar thresholds com custos reais.</li><li>Testar em lotes futuros e perfis diferentes.</li><li>Incorporar variáveis de processo e sensoriais.</li><li>Monitorar concordância com especialistas.</li></ul></div>
          <div class="card green"><h3>Limites atuais</h3><ul class="arrow-list"><li>Rótulo subjetivo e classe positiva pequena.</li><li>Sem lote, processo produtivo ou custos.</li><li>Associação preditiva não é causalidade.</li><li>Modelo não substitui avaliação sensorial.</li></ul></div>
        </div>
        <div class="decision" style="margin-top: 2.2rem;"><p>MODELO AJUDA A PRIORIZAR.<br>ESPECIALISTA DECIDE.</p></div>
        <p class="muted" style="margin-top: 1.5rem; font-size: .78rem;">Fonte: WineQT.csv · Tech Challenge FIAP/POSTECH Fase 2 · métricas de teste com split estratificado.</p>
      </div>
      <div class="footer"><span>Guilherme Augusto · 06.08.2026</span><span>08 / 08</span></div>
    </section>
  </main>

  <div class="progress" aria-hidden="true"><i id="progress-bar"></i></div>
  <div class="controls" aria-label="Controles da apresentação">
    <button type="button" id="previous" aria-label="Slide anterior">‹</button>
    <button type="button" id="next" aria-label="Próximo slide">›</button>
    <button type="button" id="print" aria-label="Imprimir apresentação">⎙</button>
  </div>
  <div class="sr-only" id="slide-status" aria-live="polite">Slide 1 de 8</div>

  <script>
    (() => {
      const slides = Array.from(document.querySelectorAll('.slide'));
      const progressBar = document.getElementById('progress-bar');
      const status = document.getElementById('slide-status');
      let current = 0;

      function showSlide(index, updateHash = true) {
        current = (index + slides.length) % slides.length;
        slides.forEach((slide, position) => {
          slide.classList.toggle('active', position === current);
          slide.setAttribute('aria-hidden', position === current ? 'false' : 'true');
        });
        progressBar.style.width = `${((current + 1) / slides.length) * 100}%`;
        status.textContent = `Slide ${current + 1} de ${slides.length}`;
        if (updateHash) history.replaceState(null, '', `#slide-${current + 1}`);
      }

      function go(delta) { showSlide(current + delta); }

      document.getElementById('previous').addEventListener('click', () => go(-1));
      document.getElementById('next').addEventListener('click', () => go(1));
      document.getElementById('print').addEventListener('click', () => window.print());
      document.addEventListener('keydown', (event) => {
        const forward = ['ArrowRight', 'PageDown', ' '].includes(event.key);
        const backward = ['ArrowLeft', 'PageUp'].includes(event.key);
        if (forward || backward) {
          event.preventDefault();
          go(forward ? 1 : -1);
        } else if (event.key === 'Home') {
          event.preventDefault();
          showSlide(0);
        } else if (event.key === 'End') {
          event.preventDefault();
          showSlide(slides.length - 1);
        }
      });

      const initial = Number.parseInt(window.location.hash.replace('#slide-', ''), 10);
      showSlide(Number.isInteger(initial) && initial >= 1 && initial <= slides.length ? initial - 1 : 0, false);
    })();
  </script>
</body>
</html>
'''


def build_presentation() -> Path:
    metrics = json.loads((RESULTS / "metrics.json").read_text(encoding="utf-8"))
    html = HTML_TEMPLATE
    for token, value in build_replacements(metrics).items():
        html = html.replace(token, value)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    return OUTPUT


if __name__ == "__main__":
    print(build_presentation())
