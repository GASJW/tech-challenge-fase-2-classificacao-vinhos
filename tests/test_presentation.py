from pathlib import Path

from pptx import Presentation


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRESENTATION_PATH = PROJECT_ROOT / "presentation" / "Tech-Challenge-2-Storytelling.pptx"


def test_presentation_contains_executive_storyline() -> None:
    presentation = Presentation(PRESENTATION_PATH)
    all_text = " ".join(
        shape.text.strip()
        for slide in presentation.slides
        for shape in slide.shapes
        if hasattr(shape, "text") and shape.text.strip()
    ).replace("\n", " ").replace("\v", " ")

    assert len(presentation.slides) == 8
    assert "QUALIDADE DE VINHOS" in all_text
    assert "Random Forest entrega o melhor equilíbrio" in all_text
    assert "Recomendação: triagem com revisão humana" in all_text
