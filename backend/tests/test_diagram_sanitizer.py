import pytest
from app.tools.project.diagram_generator import DiagramGenerator

@pytest.fixture
def generator():
    return DiagramGenerator()

def test_clean_mermaid_markup_strips_conversational_intro(generator):
    noisy_input = (
        "Here is the requested diagram for your backend API:\n\n"
        "```mermaid\n"
        "graph LR\n"
        "    Client -->|POST| Route1[\"[POST] /api/login\"]\n"
        "```\n\n"
        "Hope this helps!"
    )
    cleaned = generator._clean_mermaid_markup(noisy_input)
    assert cleaned.startswith("graph LR")
    assert "Here is the requested diagram" not in cleaned
    assert "Hope this helps!" not in cleaned

def test_clean_mermaid_markup_fixes_arrow_syntax_typo(generator):
    invalid_arrow = "graph LR\n    Client -->|POST|> Route1[\"[POST] /api/login\"]"
    cleaned = generator._clean_mermaid_markup(invalid_arrow)
    assert "-->|POST|>" not in cleaned
    assert "-->|POST|" in cleaned

def test_clean_mermaid_markup_strips_raw_backticks(generator):
    backtick_input = "```mermaid\nerDiagram\n    USER ||--o{ ORDER : places\n```"
    cleaned = generator._clean_mermaid_markup(backtick_input)
    assert not cleaned.startswith("```")
    assert cleaned.startswith("erDiagram")
