import pytest
import os
import json
from unittest.mock import patch, MagicMock

# Import the crawler and parser modules
# Note: This import will fail initially (Red Phase) since the file doesn't exist yet
try:
    from import_glossary import scrape_healthdirect_page, parse_html_terms, merge_glossaries
except ImportError:
    # Allow imports to fail gracefully if needed, but we want the test runner to show failures
    pass

def test_parse_html_terms_basic():
    """Test parsing HealthDirect alphabetical dictionary pages."""
    # HealthDirect pages typically list topics under alphabetically styled elements
    # Or in lists/links inside of main container. We want our parser to match standard link selectors.
    sample_html = """
    <html>
      <body>
        <div class="content">
          <ul class="directory-list">
            <li><a href="/medicines/aspirin">Aspirin</a></li>
            <li><a href="/medicines/amoxicillin">Amoxicillin (antibiotic)</a></li>
            <li><a href="https://www.healthdirect.gov.au/health-topics/asthma">Asthma in children</a></li>
          </ul>
        </div>
      </body>
    </html>
    """
    terms = parse_html_terms(sample_html)
    
    # We should have extracted and normalized the keys to lowercase
    assert "aspirin" in terms
    assert "amoxicillin" in terms
    assert "asthma in children" in terms
    
    # Verify the URLs are absolute
    assert terms["aspirin"]["url"] == "https://www.healthdirect.gov.au/medicines/aspirin"
    assert terms["asthma in children"]["url"] == "https://www.healthdirect.gov.au/health-topics/asthma"

@patch("requests.get")
def test_scrape_healthdirect_page_success(mock_get):
    """Test successful scrape with rate-limiting & timeout handling."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body><a href='/medicines/panadol'>Paracetamol</a></body></html>"
    mock_get.return_value = mock_response

    terms = scrape_healthdirect_page("https://www.healthdirect.gov.au/medicines")
    
    assert "paracetamol" in terms
    assert terms["paracetamol"]["url"] == "https://www.healthdirect.gov.au/medicines/panadol"
    mock_get.assert_called_once_with(
        "https://www.healthdirect.gov.au/medicines",
        headers={"User-Agent": "HealthDirectGlossaryImporter/1.0 (Bilingual Translation Experiment)"},
        timeout=10
    )

def test_merge_glossaries_no_duplicates():
    """Verify that merging preserves existing manual translations and adds new keys."""
    existing = {
        "otitis media": {
            "translations": {
                "Spanish": "otitis media",
                "Vietnamese": "viêm tai giữa"
            },
            "description": "middle ear infection"
        }
    }
    
    scraped = {
        "otitis media": {"url": "https://www.healthdirect.gov.au/health-topics/conditions/otitis-media"},
        "gastroenteritis": {"url": "https://www.healthdirect.gov.au/health-topics/conditions/gastroenteritis"}
    }
    
    merged = merge_glossaries(existing, scraped)
    
    assert "otitis media" in merged
    assert "gastroenteritis" in merged
    
    # Existing translations must be preserved exactly
    assert merged["otitis media"]["translations"]["Spanish"] == "otitis media"
    assert merged["otitis media"]["translations"]["Vietnamese"] == "viêm tai giữa"
    assert merged["otitis media"]["description"] == "middle ear infection"
    
    # New term is merged and initialized
    assert "translations" in merged["gastroenteritis"]
    assert merged["gastroenteritis"]["url"] == "https://www.healthdirect.gov.au/health-topics/conditions/gastroenteritis"

@patch("google.cloud.translate_v3.TranslationServiceClient")
def test_pre_translate_terms_success(mock_client_class):
    """Verify that terms with missing translations are translated via GCP Translation V3."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    # Mock return value for translate_text call
    mock_translation_response = MagicMock()
    mock_translation_es = MagicMock()
    mock_translation_es.translated_text = "otitis media (es)"
    mock_translation_vi = MagicMock()
    mock_translation_vi.translated_text = "viêm tai giữa (vi)"
    
    # We want translate_text to be called twice (once for Spanish, once for Vietnamese)
    mock_client.translate_text.side_effect = [
        mock_translation_response,  # First call (Spanish)
        mock_translation_response   # Second call (Vietnamese)
    ]
    
    # Let's set the translated text list
    # TranslationServiceClient.translate_text returns TranslateTextResponse which has translations
    mock_client.translate_text.side_effect = [
        MagicMock(translations=[mock_translation_es]),
        MagicMock(translations=[mock_translation_vi])
    ]
    
    glossary = {
        "otitis media": {
            "translations": {},  # Missing translations
            "url": "https://www.healthdirect.gov.au/health-topics/conditions/otitis-media"
        },
        "gastroenteritis": {
            "translations": {
                "Spanish": "gastroenteritis",
                "Vietnamese": "viêm dạ dày ruột"
            },
            "url": "https://www.healthdirect.gov.au/health-topics/conditions/gastroenteritis"
        }
    }
    
    from import_glossary import pre_translate_terms
    
    # Run pre-translation
    updated = pre_translate_terms(glossary, project_id="test-project")
    
    # Verify mock translation was called for missing terms
    assert updated["otitis media"]["translations"]["Spanish"] == "otitis media (es)"
    assert updated["otitis media"]["translations"]["Vietnamese"] == "viêm tai giữa (vi)"
    
    # Verify existing translations were NOT overwritten
    assert updated["gastroenteritis"]["translations"]["Spanish"] == "gastroenteritis"
    assert updated["gastroenteritis"]["translations"]["Vietnamese"] == "viêm dạ dày ruột"
    
    # Should call translate_text twice
    assert mock_client.translate_text.call_count == 2


def test_parse_html_terms_health_topics_subpage():
    """Verify terms are parsed correctly from health-topics alphabetical subpages class structure."""
    sample_html = """
    <html>
      <body>
        <section class="article_lists veyron-alphabet-section">
          <h2>A</h2>
          <ul class="article_lists-column">
            <li><a href="/guide-to-menopause">A guide to menopause</a></li>
            <li><a href="/abdominal-pain">Abdominal pain</a></li>
          </ul>
        </section>
      </body>
    </html>
    """
    terms = parse_html_terms(sample_html)
    assert "a guide to menopause" in terms
    assert "abdominal pain" in terms
    assert terms["abdominal pain"]["url"] == "https://www.healthdirect.gov.au/abdominal-pain"


def test_parse_html_terms_medicines_subpage():
    """Verify terms are parsed correctly from medicines alphabetical subpages class structure."""
    sample_html = """
    <html>
      <body>
        <div class="main_content-medicines-products-list">
          <ul class="cines-acive_product-list-a">
            <li><a href="/medicines/brand/amt,1293591000168106/a-little-bit-of-relief">A Little Bit of Relief</a></li>
          </ul>
        </div>
      </body>
    </html>
    """
    terms = parse_html_terms(sample_html)
    assert "a little bit of relief" in terms
    assert terms["a little bit of relief"]["url"] == "https://www.healthdirect.gov.au/medicines/brand/amt,1293591000168106/a-little-bit-of-relief"


@patch("requests.get")
def test_scrape_healthdirect_page_recursive(mock_get):
    """Verify that root index page crawling recursively crawls sub-pages up to max_letters."""
    root_html = """
    <html>
      <body>
        <nav class="alphabet-nav">
          <a href="/health-topics/A">A</a>
          <a href="/health-topics/B">B</a>
        </nav>
      </body>
    </html>
    """
    subpage_a_html = """
    <html>
      <body>
        <section class="article_lists">
          <ul class="article_lists-column">
            <li><a href="/abdominal-pain">Abdominal pain</a></li>
          </ul>
        </section>
      </body>
    </html>
    """
    subpage_b_html = """
    <html>
      <body>
        <section class="article_lists">
          <ul class="article_lists-column">
            <li><a href="/bronchitis">Bronchitis</a></li>
          </ul>
        </section>
      </body>
    </html>
    """
    
    mock_root_response = MagicMock()
    mock_root_response.status_code = 200
    mock_root_response.text = root_html
    
    mock_subpage_a_response = MagicMock()
    mock_subpage_a_response.status_code = 200
    mock_subpage_a_response.text = subpage_a_html
    
    mock_subpage_b_response = MagicMock()
    mock_subpage_b_response.status_code = 200
    mock_subpage_b_response.text = subpage_b_html
    
    # We want it to fetch root, then fetch subpage A and subpage B
    mock_get.side_effect = [
        mock_root_response,
        mock_subpage_a_response,
        mock_subpage_b_response
    ]
    
    # Run scraper on root page
    terms = scrape_healthdirect_page("https://www.healthdirect.gov.au/health-topics/conditions")
    
    # We should have merged terms from both sub-pages
    assert "abdominal pain" in terms
    assert "bronchitis" in terms
    assert mock_get.call_count == 3


@patch("requests.get")
def test_scrape_healthdirect_page_recursive_with_max_letters(mock_get):
    """Verify that specifying max_letters limits the recursive scraping of alphabetical pages."""
    root_html = """
    <html>
      <body>
        <nav class="alphabet-nav">
          <a href="/health-topics/A">A</a>
          <a href="/health-topics/B">B</a>
        </nav>
      </body>
    </html>
    """
    subpage_a_html = """
    <html>
      <body>
        <section class="article_lists">
          <ul class="article_lists-column">
            <li><a href="/abdominal-pain">Abdominal pain</a></li>
          </ul>
        </section>
      </body>
    </html>
    """
    
    mock_root_response = MagicMock()
    mock_root_response.status_code = 200
    mock_root_response.text = root_html
    
    mock_subpage_a_response = MagicMock()
    mock_subpage_a_response.status_code = 200
    mock_subpage_a_response.text = subpage_a_html
    
    mock_get.side_effect = [
        mock_root_response,
        mock_subpage_a_response
    ]
    
    # Run scraper on root page with max_letters=1
    terms = scrape_healthdirect_page("https://www.healthdirect.gov.au/health-topics/conditions", max_letters=1)
    
    # Should only crawl subpage A, not B
    assert "abdominal pain" in terms
    assert "bronchitis" not in terms
    assert mock_get.call_count == 2


