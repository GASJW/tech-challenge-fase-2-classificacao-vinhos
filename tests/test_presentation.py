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

    assert len(presentation.slides) == 9
    assert "Quando a química" in all_text
    assert "Random Forest" in all_text
    assert "deduplicação" in all_text
    assert "1.018" in all_text
