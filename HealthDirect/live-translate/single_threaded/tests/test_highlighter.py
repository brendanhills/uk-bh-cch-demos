import pytest
import os
import tempfile
import json
from glossary_highlighter import GlossaryHighlighter

@pytest.fixture
def temp_glossary():
    # Create a temporary glossary file for testing
    data = {
        "glossary": [
            {
                "english": "otitis media",
                "translations": {
                    "Vietnamese": "viêm tai giữa",
                    "Spanish": "otitis media",
                    "German": "Mittelohrentzündung"
                },
                "description": "middle ear infection"
            },
            {
                "english": "ear",
                "translations": {
                    "Vietnamese": "tai",
                    "Spanish": "oído",
                    "German": "Ohr"
                },
                "description": "the organ of hearing"
            },
            {
                "english": "abdominal aortic aneurysm",
                "translations": {
                    "Spanish": "aneurisma aórtico abdominal",
                    "Vietnamese": "chứng phình động mạch chủ bụng"
                },
                "description": "dangerous swelling in aorta"
            },
            {
                "english": "abdominal pain",
                "translations": {
                    "Spanish": "dolor abdominal",
                    "Vietnamese": "đau bụng"
                },
                "description": "stomach ache"
            }
        ]
    }
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        path = f.name
    yield path
    if os.path.exists(path):
        os.remove(path)

def test_highlighter_init(temp_glossary):
    highlighter = GlossaryHighlighter(temp_glossary)
    assert len(highlighter.glossary_entries) == 4

def test_highlighter_cli_english(temp_glossary):
    highlighter = GlossaryHighlighter(temp_glossary)
    text = "The patient has severe abdominal pain and otitis media."
    # Both english terms should be highlighted in bold green
    highlighted = highlighter.highlight_cli(text, "english")
    assert "\x1b[1;32mabdominal pain\x1b[0m" in highlighted
    assert "\x1b[1;32motitis media\x1b[0m" in highlighted

def test_highlighter_cli_spanish(temp_glossary):
    highlighter = GlossaryHighlighter(temp_glossary)
    text = "El paciente sufre de dolor abdominal."
    # Spanish term should be highlighted in bold magenta
    highlighted = highlighter.highlight_cli(text, "Spanish")
    assert "\x1b[1;35mdolor abdominal\x1b[0m" in highlighted

def test_highlighter_cli_vietnamese(temp_glossary):
    highlighter = GlossaryHighlighter(temp_glossary)
    text = "Chẩn đoán viêm tai giữa cấp tính."
    # Vietnamese term should be highlighted in bold magenta
    highlighted = highlighter.highlight_cli(text, "Vietnamese")
    assert "\x1b[1;35mviêm tai giữa\x1b[0m" in highlighted

def test_highlighter_boundary_safety(temp_glossary):
    highlighter = GlossaryHighlighter(temp_glossary)
    # "hearing" has substring "ear", but should NOT be highlighted since it's not a word boundary
    text = "He is hearing well with his left ear."
    highlighted = highlighter.highlight_cli(text, "english")
    assert "\x1b[1;32mear\x1b[0m" in highlighted
    assert "hearing" in highlighted
    assert "\x1b[1;32mhearing\x1b[0m" not in highlighted

def test_highlighter_case_insensitivity(temp_glossary):
    highlighter = GlossaryHighlighter(temp_glossary)
    text = "OTITIS MEDIA is common in children."
    highlighted = highlighter.highlight_cli(text, "english")
    assert "\x1b[1;32mOTITIS MEDIA\x1b[0m" in highlighted

def test_highlighter_length_sorting(temp_glossary):
    highlighter = GlossaryHighlighter(temp_glossary)
    text = "The scan showed an abdominal aortic aneurysm."
    highlighted = highlighter.highlight_cli(text, "english")
    assert "\x1b[1;32mabdominal aortic aneurysm\x1b[0m" in highlighted
    assert "\x1b[1;32mabdominal\x1b[0m" not in highlighted  # compound matched, not single word

def test_highlighter_fuzzy_matching(temp_glossary):
    highlighter = GlossaryHighlighter(temp_glossary)
    # Vietnamese entry "viêm tai giữa" should match fuzzy "viêm tai rất giữa" or "viêm tai hơi giữa"
    text = "Cháu bị viêm tai rất giữa và đau."
    highlighted = highlighter.highlight_cli(text, "Vietnamese")
    assert "\x1b[1;35mviêm tai rất giữa\x1b[0m" in highlighted

