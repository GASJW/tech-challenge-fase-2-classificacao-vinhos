import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = PROJECT_ROOT / "presentation" / "tech-challenge-2-executiva.html"


def test_html_presentation_contains_eight_fiap_slides_and_official_results() -> None:
    assert HTML_PATH.exists()
    html = HTML_PATH.read_text(encoding="utf-8")

    slide_ids = re.findall(r'id="slide-(\d+)"', html)
    assert slide_ids == [str(number) for number in range(1, 9)]
    assert "#ED145B" in html
    assert "#0B0B0F" in html
    assert "FIAP" in html
    assert "POSTECH" in html
    assert "QUALIDADE" in html
    assert "VINHOS" in html
    assert "Random Forest entrega o melhor equilíbrio" in html
    assert "Recomendação: triagem com revisão humana" in html
    assert "0,709" in html
    assert "0,909" in html
    assert "13,9%" in html
    assert html.count("data:image/png;base64,") >= 3
    assert "addEventListener('keydown'" in html
    assert "prefers-reduced-motion" in html
