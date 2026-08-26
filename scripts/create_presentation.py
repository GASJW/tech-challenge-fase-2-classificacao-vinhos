"""Gera a apresentação executiva do Tech Challenge 2."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT_ROOT / "results"
OUTPUT = PROJECT_ROOT / "presentation" / "Tech-Challenge-2-Storytelling.pptx"

BLACK = RGBColor(9, 9, 9)
INK = RGBColor(245, 245, 245)
MUTED = RGBColor(178, 178, 178)
MAGENTA = RGBColor(237, 20, 91)
TEAL = RGBColor(38, 166, 154)
PURPLE = RGBColor(123, 31, 162)
CARD = RGBColor(26, 26, 26)
LINE = RGBColor(58, 58, 58)


def rgb(hex_value: str) -> RGBColor:
    value = hex_value.lstrip("#")
    return RGBColor(int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def add_text(
    slide,
    text: str,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    size: float = 18,
    color: RGBColor = INK,
    bold: bool = False,
    font: str = "Arial",
    align=PP_ALIGN.LEFT,
    valign=MSO_ANCHOR.TOP,
    margin: float = 0.04,
):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(width), Inches(height))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(margin)
    frame.margin_right = Inches(margin)
    frame.margin_top = Inches(margin)
    frame.margin_bottom = Inches(margin)
    frame.vertical_anchor = valign
    paragraph = frame.paragraphs[0]
    paragraph.text = text
    paragraph.alignment = align
    paragraph.font.name = font
    paragraph.font.size = Pt(size)
    paragraph.font.bold = bold
    paragraph.font.color.rgb = color
    return box


def add_bullets(
    slide,
    bullets: list[str],
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    size: float = 17,
    color: RGBColor = INK,
    accent: RGBColor = MAGENTA,
):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(width), Inches(height))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(0.04)
    frame.margin_right = Inches(0.04)
    for index, bullet in enumerate(bullets):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = f"›  {bullet}"
        paragraph.font.name = "Arial"
        paragraph.font.size = Pt(size)
        paragraph.font.color.rgb = color
        paragraph.space_after = Pt(10)
        if index == 0:
            paragraph.font.bold = False
    return box


def add_rect(slide, x: float, y: float, width: float, height: float, fill: RGBColor, line: RGBColor | None = None):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(1)
    return shape


def add_brand(slide, slide_number: int) -> None:
    add_text(slide, "FIAP / POSTECH", 0.55, 0.25, 2.1, 0.3, size=10, color=MAGENTA, bold=True)
    add_text(slide, f"TECH CHALLENGE 2   ·   {slide_number:02d}", 10.5, 0.25, 2.3, 0.3, size=9, color=MUTED, align=PP_ALIGN.RIGHT)
    add_rect(slide, 0.55, 0.68, 12.25, 0.012, LINE)
    add_text(slide, "Guilherme Augusto  ·  06.08.2026", 0.55, 7.12, 4.0, 0.2, size=8, color=MUTED)


def new_slide(prs: Presentation, title: str, slide_number: int):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BLACK
    add_brand(slide, slide_number)
    add_text(slide, title, 0.55, 0.88, 12.0, 0.55, size=27, bold=True)
    return slide


def add_image_contain(slide, path: Path, x: float, y: float, width: float, height: float):
    if not path.exists():
        add_text(slide, f"Imagem ausente: {path.name}", x, y, width, 0.4, size=12, color=MAGENTA)
        return
    with Image.open(path) as image:
        image_width, image_height = image.size
    box_ratio = width / height
    image_ratio = image_width / image_height
    if image_ratio > box_ratio:
        final_width = width
        final_height = width / image_ratio
        final_x = x
        final_y = y + (height - final_height) / 2
    else:
        final_height = height
        final_width = height * image_ratio
        final_x = x + (width - final_width) / 2
        final_y = y
    slide.shapes.add_picture(str(path), Inches(final_x), Inches(final_y), Inches(final_width), Inches(final_height))


def add_kpi_card(slide, value: str, label: str, x: float, color: RGBColor = MAGENTA):
    add_rect(slide, x, 1.75, 3.8, 1.55, CARD, LINE)
    add_rect(slide, x, 1.75, 0.08, 1.55, color)
    add_text(slide, value, x + 0.25, 1.96, 3.25, 0.55, size=30, color=color, bold=True)
    add_text(slide, label, x + 0.25, 2.64, 3.25, 0.35, size=12, color=MUTED)


def fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%".replace(".", ",")


def fmt_num(value: float) -> str:
    return f"{value:.3f}".replace(".", ",")


def build_deck() -> None:
    metrics = json.loads((RESULTS / "metrics.json").read_text(encoding="utf-8"))
    logistic = metrics["models"]["logistic_regression"]["test"]
    forest = metrics["models"]["random_forest"]["test"]

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Slide 1 — cover
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BLACK
    add_rect(slide, 0, 0, 0.18, 7.5, MAGENTA)
    add_text(slide, "FIAP / POSTECH", 0.72, 0.42, 2.4, 0.3, size=11, color=MAGENTA, bold=True)
    add_text(slide, "TECH CHALLENGE 2", 0.72, 1.35, 4.5, 0.35, size=13, color=MUTED, bold=True)
    add_text(slide, "QUALIDADE\nDE VINHOS", 0.72, 1.82, 6.5, 1.35, size=40, bold=True)
    add_text(slide, "Classificação binária com Machine Learning", 0.76, 3.45, 5.8, 0.4, size=19, color=INK)
    add_text(slide, "Podemos priorizar amostras promissoras\nantes da avaliação sensorial?", 0.76, 4.45, 5.4, 0.75, size=23, color=MUTED)
    add_rect(slide, 9.05, 1.02, 3.45, 5.45, MAGENTA)
    add_text(slide, "7", 9.45, 1.35, 2.6, 1.45, size=96, color=BLACK, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "NOTA DE CORTE", 9.45, 2.98, 2.6, 0.35, size=12, color=BLACK, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "Alta qualidade\nquality >= 7", 9.45, 4.1, 2.6, 0.65, size=18, color=BLACK, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "Guilherme Augusto  ·  06.08.2026", 0.72, 7.12, 4.0, 0.2, size=8, color=MUTED)

    # Slide 2 — dataset
    slide = new_slide(prs, "A decisão começa pelo rótulo", 2)
    add_kpi_card(slide, f"{metrics['dataset']['rows']:,}".replace(",", "."), "amostras analisadas", 0.55, MAGENTA)
    add_kpi_card(slide, fmt_pct(metrics["dataset"]["positive_rate"]), "alta qualidade (quality >= 7)", 4.75, TEAL)
    add_kpi_card(slide, str(metrics["dataset"]["feature_count"]), "variáveis físico-químicas", 8.95, PURPLE)
    add_text(slide, "Contrato analítico", 0.62, 4.15, 3.2, 0.35, size=15, color=MAGENTA, bold=True)
    add_bullets(
        slide,
        [
            "Sem valores ausentes e sem Ids duplicados.",
            "Id preservado para rastreabilidade, excluído do treinamento.",
            "Treino/teste estratificado para respeitar a classe minoritária.",
        ],
        0.62,
        4.58,
        11.7,
        1.6,
        size=16,
    )

    # Slide 3 — EDA
    slide = new_slide(prs, "A classe de interesse é minoritária", 3)
    add_image_contain(slide, RESULTS / "figures" / "target_distribution.png", 0.5, 1.45, 7.0, 4.8)
    add_text(slide, "86,1%", 8.15, 1.7, 3.5, 0.65, size=37, color=MUTED, bold=True)
    add_text(slide, "baixa/média qualidade", 8.2, 2.35, 3.7, 0.35, size=15, color=INK)
    add_text(slide, "13,9%", 8.15, 3.15, 3.5, 0.65, size=37, color=MAGENTA, bold=True)
    add_text(slide, "alta qualidade", 8.2, 3.8, 3.7, 0.35, size=15, color=INK)
    add_bullets(
        slide,
        [
            "Accuracy isolada favorece a classe mais comum.",
            "Average Precision, recall e F1 entram na decisão.",
        ],
        8.1,
        4.55,
        4.4,
        1.3,
        size=15,
    )

    # Slide 4 — drivers
    slide = new_slide(prs, "Álcool e acidez organizam o sinal preditivo", 4)
    add_image_contain(slide, RESULTS / "figures" / "feature_importance_random_forest.png", 0.45, 1.35, 7.75, 5.35)
    add_text(slide, "Principais sinais observados", 8.55, 1.6, 4.1, 0.35, size=15, color=MAGENTA, bold=True)
    add_bullets(
        slide,
        [
            "Teor alcoólico aparece como o sinal mais forte.",
            "Sulfatos e ácido cítrico também contribuem para a separação.",
            "Acidez volátil tem associação linear negativa com quality.",
        ],
        8.5,
        2.05,
        4.25,
        2.1,
        size=15,
    )
    add_rect(slide, 8.55, 4.75, 3.95, 1.18, CARD, LINE)
    add_text(slide, "Leitura correta", 8.78, 4.98, 2.0, 0.25, size=12, color=TEAL, bold=True)
    add_text(slide, "Importância indica associação preditiva — não causalidade.", 8.78, 5.3, 3.4, 0.45, size=13, color=INK)

    # Slide 5 — model comparison
    slide = new_slide(prs, "Random Forest entrega o melhor equilíbrio", 5)
    table = slide.shapes.add_table(3, 6, Inches(0.55), Inches(1.55), Inches(12.2), Inches(2.0)).table
    widths = [2.9, 1.75, 1.75, 1.75, 2.0, 2.05]
    for index, width in enumerate(widths):
        table.columns[index].width = Inches(width)
    headers = ["Modelo", "Precision", "Recall", "F1", "ROC-AUC", "Avg Precision"]
    values = [
        ["Regressão Logística", logistic["precision"], logistic["recall"], logistic["f1"], logistic["roc_auc"], logistic["average_precision"]],
        ["Random Forest", forest["precision"], forest["recall"], forest["f1"], forest["roc_auc"], forest["average_precision"]],
    ]
    for col, header in enumerate(headers):
        cell = table.cell(0, col)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = MAGENTA
    for row_index, row in enumerate(values, start=1):
        for col, value in enumerate(row):
            cell = table.cell(row_index, col)
            cell.text = row[0] if col == 0 else fmt_num(value)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(37, 37, 37) if row_index == 2 else CARD
            if row_index == 2:
                cell.fill.fore_color.rgb = RGBColor(54, 24, 35)
    for row in table.rows:
        for cell in row.cells:
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.05)
            cell.margin_bottom = Inches(0.05)
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.name = "Arial"
                paragraph.font.size = Pt(12)
                paragraph.font.color.rgb = INK
                paragraph.font.bold = row is table.rows[0]
                paragraph.alignment = PP_ALIGN.CENTER
    add_text(slide, "O ganho principal está na precisão e no Average Precision; o recall da Regressão Logística continua útil quando perder um positivo é mais caro.", 0.7, 4.15, 11.7, 0.65, size=20, color=INK, bold=True)
    add_bullets(
        slide,
        [
            f"Random Forest: {fmt_pct(forest['precision'])} de precisão e {fmt_pct(forest['average_precision'])} de Average Precision.",
            f"Regressão Logística: {fmt_pct(logistic['recall'])} de recall, com maior volume de falsos positivos.",
        ],
        0.72,
        5.15,
        11.6,
        1.0,
        size=15,
    )

    # Slide 6 — cost of error
    slide = new_slide(prs, "A escolha do modelo depende do custo do erro", 6)
    add_rect(slide, 0.6, 1.55, 5.8, 4.65, RGBColor(40, 24, 32), LINE)
    add_rect(slide, 6.95, 1.55, 5.8, 4.65, RGBColor(22, 43, 42), LINE)
    add_text(slide, "RANDOM FOREST", 0.95, 1.9, 4.5, 0.35, size=14, color=MAGENTA, bold=True)
    add_text(slide, "Mais seletivo", 0.95, 2.35, 4.6, 0.55, size=28, bold=True)
    add_bullets(slide, [f"Precision: {fmt_pct(forest['precision'])}", f"Recall: {fmt_pct(forest['recall'])}", "Bom candidato para fila de triagem"], 0.95, 3.25, 4.9, 1.6, size=17)
    add_text(slide, "REGRESSÃO LOGÍSTICA", 7.3, 1.9, 4.8, 0.35, size=14, color=TEAL, bold=True)
    add_text(slide, "Mais abrangente", 7.3, 2.35, 4.6, 0.55, size=28, bold=True)
    add_bullets(slide, [f"Precision: {fmt_pct(logistic['precision'])}", f"Recall: {fmt_pct(logistic['recall'])}", "Captura mais positivos, revisa mais amostras"], 7.3, 3.25, 4.9, 1.6, size=17, accent=TEAL)
    add_text(slide, "Não existe um vencedor universal: o threshold deve refletir o custo de cada erro.", 1.25, 6.55, 10.8, 0.4, size=18, color=INK, bold=True, align=PP_ALIGN.CENTER)

    # Slide 7 — recommendation
    slide = new_slide(prs, "Recomendação: triagem com revisão humana", 7)
    steps = [
        ("01", "Pontuar", "Medições físico-químicas entram no modelo."),
        ("02", "Priorizar", "Amostras com maior score entram primeiro na fila."),
        ("03", "Validar", "Enólogo confirma a qualidade antes da decisão."),
    ]
    for index, (number, label, text) in enumerate(steps):
        x = 0.65 + index * 4.18
        add_rect(slide, x, 1.75, 3.7, 2.55, CARD, LINE)
        add_text(slide, number, x + 0.25, 2.0, 0.8, 0.45, size=21, color=MAGENTA, bold=True)
        add_text(slide, label, x + 0.25, 2.62, 3.05, 0.42, size=23, color=INK, bold=True)
        add_text(slide, text, x + 0.25, 3.25, 3.05, 0.65, size=14, color=MUTED)
        if index < 2:
            add_text(slide, "→", x + 3.82, 2.7, 0.35, 0.4, size=23, color=TEAL, bold=True, align=PP_ALIGN.CENTER)
    add_rect(slide, 0.65, 4.95, 12.0, 1.2, RGBColor(54, 24, 35), MAGENTA)
    add_text(slide, "Decisão de negócio", 0.95, 5.22, 2.5, 0.3, size=13, color=MAGENTA, bold=True)
    add_text(slide, "O modelo organiza a fila. O especialista continua responsável pela aprovação.", 3.05, 5.15, 8.9, 0.45, size=20, color=INK, bold=True)

    # Slide 8 — next steps
    slide = new_slide(prs, "Próximos passos", 8)
    add_text(slide, "Agora", 0.7, 1.55, 4.3, 0.4, size=17, color=MAGENTA, bold=True)
    add_bullets(
        slide,
        [
            "Calibrar thresholds com custos reais.",
            "Testar em lotes futuros e perfis diferentes.",
            "Incorporar variáveis de processo e sensoriais.",
            "Monitorar concordância com especialistas.",
        ],
        0.7,
        2.05,
        5.4,
        2.5,
        size=17,
    )
    add_text(slide, "Limites atuais", 7.0, 1.55, 4.5, 0.4, size=17, color=TEAL, bold=True)
    add_bullets(
        slide,
        [
            "Rótulo subjetivo e classe positiva pequena.",
            "Sem lote, processo produtivo ou custos.",
            "Associação preditiva não é causalidade.",
            "Modelo não substitui avaliação sensorial.",
        ],
        7.0,
        2.05,
        5.4,
        2.5,
        size=17,
        accent=TEAL,
    )
    add_rect(slide, 0.7, 5.25, 11.9, 1.0, MAGENTA)
    add_text(slide, "MODELO AJUDA A PRIORIZAR.\nESPECIALISTA DECIDE.", 0.95, 5.4, 11.3, 0.58, size=25, color=BLACK, bold=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build_deck()
