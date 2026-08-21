import pytest
from app.tools.project.diagram_generator import DiagramGenerator

@pytest.fixture
def generator():
    g = DiagramGenerator()
    g.clear_cache()
    return g

def test_clean_mermaid_markup_strips_think_tags(generator):
    think_input = (
        "<think>\n1. Analyzing classes...\n2. Building relationships...\n</think>\n\n"
        "```mermaid\n"
        "erDiagram\n"
        "    USER ||--o{ ORDER : places\n"
        "```"
    )
    cleaned = generator._clean_mermaid_markup(think_input)
    assert "<think>" not in cleaned
    assert "Analyzing classes" not in cleaned
    assert cleaned.startswith("erDiagram")

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

def test_clean_mermaid_markup_escapes_url_parameters(generator):
    route_param_input = 'graph LR\n    Client -->|GET| r_0["[GET] /api/users/<int:pk>/"]'
    cleaned = generator._clean_mermaid_markup(route_param_input)
    assert "<int:pk>" not in cleaned
    assert "&lt;int:pk&gt;" in cleaned

def test_clean_mermaid_markup_strips_raw_backticks(generator):
    backtick_input = "```mermaid\nerDiagram\n    USER ||--o{ ORDER : places\n```"
    cleaned = generator._clean_mermaid_markup(backtick_input)
    assert not cleaned.startswith("```")
    assert cleaned.startswith("erDiagram")

def test_in_memory_diagram_caching(generator):
    # Manually populate cache
    generator._cache["proj1_er"] = "erDiagram\n    MODEL"
    assert generator._cache.get("proj1_er") == "erDiagram\n    MODEL"
    
    # Test cache clearing for specific project
    generator.clear_cache("proj1")
    assert "proj1_er" not in generator._cache
