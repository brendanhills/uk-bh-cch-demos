import pytest
import os
import json
from unittest.mock import patch, MagicMock

# Import the parsing and exporting functions from import_glossary
try:
    from import_glossary import parse_html_terms, export_to_csv, pre_translate_terms
except ImportError:
    parse_html_terms = None
    export_to_csv = None
    pre_translate_terms = None

def test_imports_exist():
    """Verify that parsing and export functions exist."""
    assert parse_html_terms is not None, "parse_html_terms must be imported"
    assert export_to_csv is not None, "export_to_csv must be imported"

def test_parse_html_terms_synonyms_extraction():
    """Verify that parse_html_terms parses and splits parentheticals using the URL slug matching logic."""
    sample_html = """
    <div class="article_lists">
      <a href="/medicines/amoxicillin">Amoxil (amoxicillin)</a>
      <a href="/health-topics/conditions/otitis-media">Middle ear infection (otitis media)</a>
      <a href="/medicines/amoxicillin">Amoxicillin (antibiotic)</a>
    </div>
    """
    
    terms = parse_html_terms(sample_html)
    
    # Assert Amoxil (amoxicillin)
    # Since 'amoxicillin' matches the slug, 'amoxicillin' should be the primary key, and 'amoxil' the synonym
    assert "amoxicillin" in terms
    assert "amoxil" in terms["amoxicillin"]["synonyms"]
    
    # Assert Middle ear infection (otitis media)
    # Since 'otitis media' matches the slug 'otitis-media', 'otitis media' is primary, 'middle ear infection' is synonym
    assert "otitis media" in terms
    assert "middle ear infection" in terms["otitis media"]["synonyms"]
    
    # Assert Amoxicillin (antibiotic)
    # Since 'amoxicillin' matches the slug, 'amoxicillin' is primary.
    # 'antibiotic' is a generic classification and should not be added as a clinical synonym
    assert "amoxicillin" in terms
    assert "antibiotic" not in terms["amoxicillin"].get("synonyms", [])

def test_csv_export_flattening_of_nested_dictionaries(tmp_path):
    """Verify that export_to_csv flattens nested formal/informal dictionaries into standard format."""
    glossary = {
        "otitis media": {
            "translations": {
                "Spanish": {
                    "formal": "otitis media",
                    "informal": ["infección del oído medio"]
                },
                "Vietnamese": {
                    "formal": "viêm tai giữa",
                    "informal": ["nhiễm trùng tai giữa"]
                }
            }
        },
        "paracetamol": {
            "translations": {
                "Spanish": "paracetamol",
                "Vietnamese": "paracetamol"
            }
        }
    }
    
    csv_file = tmp_path / "glossary_output.csv"
    export_to_csv(glossary, str(csv_file))
    
    import csv
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        
    assert reader[0] == ["en", "es", "vi"]
    
    # Assert otitis media flat strings
    # 'otitis media' Spanish translation must be 'formal: otitis media | informal: infección del oído medio'
    # 'otitis media' Vietnamese translation must be 'formal: viêm tai giữa | informal: nhiễm trùng tai giữa'
    assert reader[1][0] == "otitis media"
    assert reader[1][1] == "formal: otitis media | informal: infección del oído medio"
    assert reader[1][2] == "formal: viêm tai giữa | informal: nhiễm trùng tai giữa"
    
    # Assert paracetamol remains normal simple string
    assert reader[2][0] == "paracetamol"
    assert reader[2][1] == "paracetamol"
    assert reader[2][2] == "paracetamol"

@patch("requests.get")
@patch("google.cloud.translate_v3.TranslationServiceClient")
def test_interruption_and_restart_idempotency(mock_translate_client_class, mock_get, tmp_path):
    """Verify that restarting the pipeline after an interruption does not result in redundant crawl or translate requests."""
    from import_glossary import scrape_healthdirect_page, pre_translate_terms, save_scrape_state
    
    state_file = str(tmp_path / "scrape_state.json")
    url = "https://www.healthdirect.gov.au/health-topics/conditions/otitis-media"
    
    # 1. Simulate previous successful crawl by adding URL to state
    save_scrape_state({url}, state_file)
    
    # 2. Try crawling again: it should instantly bypass and make zero request calls
    terms = scrape_healthdirect_page(url, is_subpage=True, state_path=state_file, delay=0.0)
    assert terms == {}
    mock_get.assert_not_called()
    
    # 3. Simulate pre_translate_terms with a glossary that already has all translations
    mock_translate_client = MagicMock()
    mock_translate_client_class.return_value = mock_translate_client
    
    glossary = {
        "otitis media": {
            "translations": {
                "Spanish": "otitis media",
                "Vietnamese": "viêm tai giữa"
            }
        }
    }
    
    updated = pre_translate_terms(glossary, project_id="test-project", languages={"Spanish": "es", "Vietnamese": "vi"})
    
    # It should bypass translate client entirely because everything is already translated
    mock_translate_client.translate_text.assert_not_called()
    assert updated == glossary
