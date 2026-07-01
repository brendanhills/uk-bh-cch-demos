import pytest
import re
from unittest.mock import patch
from live_translate_demo import print_row

def len_visible(text: str) -> int:
    # Helper to strip ANSI codes and get visible length
    return len(re.sub(r'\x1b\[[0-9;]*m', '', text))

def test_print_row_basic_alignment(capsys):
    # Test printing simple text with no highlighting
    print_row("Hello nurse", "Hola paciente")
    captured = capsys.readouterr().out
    
    # Grid lines look like: "║ [col1 padded] ║ [col2 padded] ║"
    lines = [line for line in captured.splitlines() if "║" in line]
    assert len(lines) == 1
    line = lines[0]
    
    assert line.startswith("║ ")
    assert line.endswith(" ║")
    # Columns are separated by " ║ "
    parts = line.split(" ║ ")
    assert len(parts) == 2
    
    left_content = parts[0].replace("║ ", "").strip()
    right_content = parts[1].replace(" ║", "").strip()
    
    assert left_content == "Hello nurse"
    assert right_content == "Hola paciente"

def test_print_row_wrapping_with_highlights(capsys):
    # Test with a simulated highlighted word using ANSI escapes.
    # A word with 10 visible chars + 12 chars of ANSI sequence = 22 total chars.
    highlighted_en = "\x1b[1;32mabdominal\x1b[0m \x1b[1;32mpain\x1b[0m"
    highlighted_es = "\x1b[1;35mdolor abdominal\x1b[0m"
    
    # We pass the highlighted text. Let's make sure the padding is correct.
    # Note: until we integrate GlossaryHighlighter inside print_row, we will pass highlights directly.
    # Once integrated, we will pass regular text and language="Spanish" to trigger print_row's highlighter.
    
    print_row(f"Patient has {highlighted_en} today.", f"Paciente tiene {highlighted_es} hoy.", language="Spanish")
    captured = capsys.readouterr().out
    
    lines = [line for line in captured.splitlines() if "║" in line]
    assert len(lines) > 0
    
    for line in lines:
        # Check overall visual width of each column
        # Total line should be "║ " (2) + col1 (54) + " ║ " (3) + col2 (54) + " ║" (2) = 115 chars visible
        parts = line.split(" ║ ")
        assert len(parts) == 2
        
        # Col 1 should have visible length of 54 (padded right)
        c1 = parts[0][2:] # strip "║ "
        c2 = parts[1][:-2] # strip " ║"
        
        assert len_visible(c1) == 54
        assert len_visible(c2) == 54

def test_print_row_integration_highlighting(capsys):
    # Test print_row with language parameter to verify it applies GlossaryHighlighter
    # We should expect:
    # - col1 (English): "abdominal pain" -> bold green
    # - col2 (Spanish): "dolor abdominal" -> bold magenta
    
    print_row("The patient has severe abdominal pain.", "El paciente sufre de dolor abdominal.", language="Spanish")
    captured = capsys.readouterr().out
    
    # Verify that English terms in col1 are bold green (\x1b[1;32m)
    assert "\x1b[1;32mabdominal pain\x1b[0m" in captured
    # Verify that Spanish terms in col2 are bold magenta (\x1b[1;35m)
    assert "\x1b[1;35mdolor abdominal\x1b[0m" in captured
    
    # Verify that the lines are correctly padded and aligned
    lines = [line for line in captured.splitlines() if "║" in line]
    for line in lines:
        parts = line.split(" ║ ")
        c1 = parts[0][2:]
        c2 = parts[1][:-2]
        assert len_visible(c1) == 54
        assert len_visible(c2) == 54
