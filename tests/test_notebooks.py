import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "00-validacoes-iniciais.ipynb"
MODELING_NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "01-eda-modelagem.ipynb"


def test_initial_validation_notebook_contains_audit_sections() -> None:
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    source = "\n".join(
        "".join(cell.get("source", [])) for cell in notebook["cells"]
    )

    assert NOTEBOOK_PATH.exists()
    assert "Valores ausentes" in source
    assert "Id duplicado" in source
    assert "Multiclasse original" in source
    assert "Binária adotada" in source
    assert "Outliers" in source
    assert "deduplicate_profiles" in source
    assert "Perfis físico-químicos repetidos" in source
    assert "1.018" in source


def test_modeling_notebook_resolves_project_root_independently_of_working_directory() -> None:
    notebook = json.loads(MODELING_NOTEBOOK_PATH.read_text(encoding="utf-8"))
    source = "\n".join(
        "".join(cell.get("source", [])) for cell in notebook["cells"]
    )

    assert "project_root = next(" in source
    assert "(candidate / \"data\" / \"raw\" / \"WineQT.csv\").exists()" in source
