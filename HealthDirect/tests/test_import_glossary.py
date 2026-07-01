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

@pytest.fixture(autouse=True)
def mock_robots_txt_globally(request):
    if "test_is_crawl_allowed" in request.node.name:
        yield
        return
    with patch("import_glossary.is_crawl_allowed", return_value=True):
        from import_glossary import load_scrape_state, save_scrape_state
        
        def mock_load_state(filepath):
            if filepath == "dictionary/scrape_state.json":
                return set()
            return load_scrape_state(filepath)
            
        def mock_save_state(scraped_urls, filepath):
            if filepath == "dictionary/scrape_state.json":
                return
            return save_scrape_state(scraped_urls, filepath)
            
        with patch("import_glossary.load_scrape_state", side_effect=mock_load_state), \
             patch("import_glossary.save_scrape_state", side_effect=mock_save_state):
            yield

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
    
    # Run scraper on root page with max_letters=1, patching random.sample to choose first element
    with patch("random.sample", lambda pop, k: [pop[0]]):
        terms = scrape_healthdirect_page("https://www.healthdirect.gov.au/health-topics/conditions", max_letters=1)
    
    # Should only crawl subpage A, not B
    assert "abdominal pain" in terms
    assert "bronchitis" not in terms
    assert mock_get.call_count == 2


def test_export_to_csv(tmp_path):
    """Test exporting glossary terms to Translation V3 compliant multi-lingual CSV."""
    from import_glossary import export_to_csv
    
    glossary = {
        "otitis media": {
            "translations": {
                "Spanish": "otitis media (es)",
                "Vietnamese": "viêm tai giữa (vi)"
            }
        },
        "gastroenteritis": {
            "translations": {
                "Spanish": "gastroenteritis (es)",
                "Vietnamese": "viêm dạ dày ruột (vi)"
            }
        }
    }
    
    csv_file = tmp_path / "glossary.csv"
    export_to_csv(glossary, str(csv_file))
    
    assert csv_file.exists()
    content = csv_file.read_text(encoding="utf-8")
    lines = content.strip().split("\n")
    
    assert lines[0] == "en,es,vi"
    assert "otitis media,otitis media (es),viêm tai giữa (vi)" in lines
    assert "gastroenteritis,gastroenteritis (es),viêm dạ dày ruột (vi)" in lines


@patch("google.cloud.storage.Client")
def test_upload_to_gcs(mock_storage_client):
    """Verify that file is uploaded to correct GCS bucket and path."""
    from import_glossary import upload_to_gcs
    
    mock_client_inst = MagicMock()
    mock_storage_client.return_value = mock_client_inst
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    
    mock_client_inst.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    
    upload_to_gcs("/local/path/file.csv", "gs://test-bucket/path/to/file.csv")
    
    mock_client_inst.bucket.assert_called_once_with("test-bucket")
    mock_bucket.blob.assert_called_once_with("path/to/file.csv")
    mock_blob.upload_from_filename.assert_called_once_with("/local/path/file.csv")


@patch("google.cloud.translate_v3.TranslationServiceClient")
def test_recreate_gcp_glossary(mock_translate_client):
    """Verify Translation V3 glossary is recreated (deleted if exists, then created)."""
    from import_glossary import recreate_gcp_glossary
    
    mock_client_inst = MagicMock()
    mock_translate_client.return_value = mock_client_inst
    
    # Mock glossary path
    mock_client_inst.glossary_path.return_value = "projects/test-project/locations/us-central1/glossaries/test-glossary"
    
    # Mock delete & create operations
    mock_delete_op = MagicMock()
    mock_create_op = MagicMock()
    mock_client_inst.delete_glossary.return_value = mock_delete_op
    mock_client_inst.create_glossary.return_value = mock_create_op
    
    recreate_gcp_glossary(
        project_id="test-project",
        location="us-central1",
        glossary_id="test-glossary",
        gcs_uri="gs://test-bucket/glossary.csv"
    )
    
    # Check delete flow
    mock_client_inst.get_glossary.assert_called_once_with(name="projects/test-project/locations/us-central1/glossaries/test-glossary")
    mock_client_inst.delete_glossary.assert_called_once_with(name="projects/test-project/locations/us-central1/glossaries/test-glossary")
    mock_delete_op.result.assert_called_once()
    
    # Check create flow
    mock_client_inst.create_glossary.assert_called_once()
    mock_create_op.result.assert_called_once()


def test_load_and_save_glossary_json(tmp_path):
    """Verify loading list-based glossary.json and saving it back correctly."""
    from import_glossary import load_glossary_json, save_glossary_json
    
    sample_data = {
        "glossary": [
            {
                "english": "otitis media",
                "translations": {
                    "Vietnamese": "viêm tai giữa",
                    "Spanish": "otitis media"
                },
                "description": "middle ear infection",
                "url": "https://www.healthdirect.gov.au/otitis-media"
            }
        ]
    }
    
    json_file = tmp_path / "glossary.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(sample_data, f)
        
    flat = load_glossary_json(str(json_file))
    
    assert "otitis media" in flat
    assert flat["otitis media"]["translations"]["Vietnamese"] == "viêm tai giữa"
    assert flat["otitis media"]["url"] == "https://www.healthdirect.gov.au/otitis-media"
    
    # Save back
    json_file_out = tmp_path / "glossary_out.json"
    save_glossary_json(flat, str(json_file_out))
    
    with open(json_file_out, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
        
    assert "glossary" in saved_data
    assert len(saved_data["glossary"]) == 1
    assert saved_data["glossary"][0]["english"] == "otitis media"
    assert saved_data["glossary"][0]["translations"]["Spanish"] == "otitis media"
    assert saved_data["glossary"][0]["url"] == "https://www.healthdirect.gov.au/otitis-media"


@patch("import_glossary.scrape_healthdirect_page")
@patch("import_glossary.pre_translate_terms")
@patch("import_glossary.upload_to_gcs")
@patch("import_glossary.recreate_gcp_glossary")
def test_pipeline_execution(
    mock_recreate, mock_upload, mock_translate, mock_scrape, tmp_path
):
    """Test the full pipeline integration flow."""
    from import_glossary import run_pipeline, save_glossary_json
    
    # Create temp empty glossary
    glossary_json = tmp_path / "glossary.json"
    save_glossary_json({}, str(glossary_json))
    
    # Mock scraped results
    mock_scrape.return_value = {
        "bronchitis": {"url": "https://www.healthdirect.gov.au/bronchitis"}
    }
    
    # Mock pre-translation
    mock_translate.side_effect = lambda g, project_id, **kwargs: {
        "bronchitis": {
            "translations": {"Spanish": "bronquitis", "Vietnamese": "viêm phế quản"},
            "url": "https://www.healthdirect.gov.au/bronchitis"
        }
    }
    
    import argparse
    args = argparse.Namespace(
        scrape="https://www.healthdirect.gov.au/health-topics/conditions",
        max_letters=1,
        glossary_json=str(glossary_json),
        gcs_destination="gs://test-bucket/glossaries/glossary.csv",
        glossary_id="test-glossary",
        location="us-central1",
        project_id="test-project",
        pipeline=True
    )
        
    run_pipeline(args)
    
    # Verify sub-functions were called with correct parameters
    mock_scrape.assert_called_once_with(
        "https://www.healthdirect.gov.au/health-topics/conditions",
        max_letters=1,
        delay=1.0,
        force=False,
        state_path="dictionary/scrape_state.json"
    )
    mock_translate.assert_called_once()
    mock_upload.assert_called_once_with("dictionary/glossary.csv", "gs://test-bucket/glossaries/glossary.csv")
    mock_recreate.assert_called_once_with(
        project_id="test-project",
        location="us-central1",
        glossary_id="test-glossary",
        gcs_uri="gs://test-bucket/glossaries/glossary.csv"
    )
    
    # Check that glossary file was updated on disk
    with open(glossary_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["glossary"][0]["english"] == "bronchitis"
    assert data["glossary"][0]["translations"]["Spanish"] == "bronquitis"


def test_upload_to_gcs_invalid_uri():
    """Verify upload_to_gcs raises ValueError on invalid schema."""
    from import_glossary import upload_to_gcs
    with pytest.raises(ValueError, match="gcs_destination must start with gs://"):
        upload_to_gcs("local.csv", "https://invalid-uri")


def test_load_glossary_json_non_existent():
    """Verify load_glossary_json returns empty dict on non-existent file or exception."""
    from import_glossary import load_glossary_json
    assert load_glossary_json("non_existent_file.json") == {}


@patch("requests.get")
def test_scrape_healthdirect_page_error(mock_get):
    """Verify scrape_healthdirect_page handles exceptions gracefully."""
    mock_get.side_effect = Exception("Connection error")
    from import_glossary import scrape_healthdirect_page
    assert scrape_healthdirect_page("https://example.com") == {}


def test_build_search_query_spanish():
    from import_glossary import build_search_query
    q = build_search_query("bronquitis", "es")
    assert q == '"bronquitis" salud OR medicina'


def test_build_search_query_vietnamese():
    from import_glossary import build_search_query
    q = build_search_query("viêm phế quản", "vi")
    assert q == '"viêm phế quản" sức khỏe OR y tế OR bệnh'


def test_build_search_query_invalid():
    from import_glossary import build_search_query
    with pytest.raises(ValueError, match="Unsupported language"):
        build_search_query("bronchitis", "en")


def test_parse_search_results_success():
    from import_glossary import parse_search_results
    sample_html = """
    <html>
      <body>
        <div class="g">
          <a href="https://es.wikipedia.org/wiki/Bronquitis"><h3>Bronquitis - Wikipedia</h3></a>
          <span class="st">La bronquitis es una inflamación de las vías respiratorias...</span>
        </div>
        <div class="g">
          <a href="/url?q=https://www.mayoclinic.org/es-es/diseases-conditions/bronchitis/symptoms-causes/syc-20353727&sa=U"><h3>Bronquitis - Síntomas y causas - Mayo Clinic</h3></a>
          <div class="IsZC3b">La bronquitis es una inflamación del revestimiento de los bronquios...</div>
        </div>
      </body>
    </html>
    """
    results = parse_search_results(sample_html)
    assert len(results) == 2
    assert results[0]["url"] == "https://es.wikipedia.org/wiki/Bronquitis"
    assert "La bronquitis es una inflamación de las vías respiratorias" in results[0]["snippet"]
    assert results[1]["url"] == "https://www.mayoclinic.org/es-es/diseases-conditions/bronchitis/symptoms-causes/syc-20353727"
    assert "La bronquitis es una inflamación del revestimiento" in results[1]["snippet"]


def test_parse_search_results_no_results():
    from import_glossary import parse_search_results
    assert parse_search_results("<html><body>No results</body></html>") == []


@patch("google.genai.Client")
def test_search_google_success(mock_client_class):
    from import_glossary import search_google
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    # Structure of the mock response
    mock_response = MagicMock()
    mock_candidate = MagicMock()
    mock_metadata = MagicMock()
    mock_chunk = MagicMock()
    mock_web = MagicMock()
    
    mock_web.uri = "https://es.wikipedia.org/wiki/Bronquitis"
    mock_web.title = "Bronquitis"
    mock_chunk.web = mock_web
    mock_metadata.grounding_chunks = [mock_chunk]
    mock_candidate.grounding_metadata = mock_metadata
    mock_response.candidates = [mock_candidate]
    mock_response.text = "La bronquitis es..."
    
    mock_client.models.generate_content.return_value = mock_response
    
    results = search_google('"bronquitis" salud OR medicina')
    assert len(results) == 1
    assert results[0]["url"] == "https://es.wikipedia.org/wiki/Bronquitis"
    assert results[0]["snippet"] == "La bronquitis es..."
    
    # Verify mock was called with the correct model and parameters
    mock_client.models.generate_content.assert_called_once()
    kwargs = mock_client.models.generate_content.call_args[1]
    assert kwargs["model"] == "gemini-3.5-flash"
    assert "bronquitis" in kwargs["contents"]


@patch("google.genai.Client")
def test_search_google_rate_limit(mock_client_class):
    from import_glossary import search_google, GoogleRateLimitError
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_client.models.generate_content.side_effect = Exception("ResourceExhausted: 429 Too Many Requests")
    
    with pytest.raises(GoogleRateLimitError, match="Gemini API Rate Limit hit"):
        search_google('"bronquitis" salud OR medicina')


@patch("import_glossary.search_google")
def test_ground_term_success(mock_search):
    from import_glossary import ground_term
    mock_search.return_value = [
        {"url": "https://www.mayoclinic.org/es-es/bronchitis", "snippet": "La bronquitis es..."}
    ]
    res = ground_term("bronchitis", "bronquitis", "es")
    assert res["url"] == "https://www.mayoclinic.org/es-es/bronchitis"
    assert res["snippet"] == "La bronquitis es..."
    mock_search.assert_called_once_with('"bronquitis" salud OR medicina')


@patch("import_glossary.search_google")
def test_ground_term_failure(mock_search):
    from import_glossary import ground_term
    mock_search.return_value = []
    res = ground_term("bronchitis", "bronquitis", "es")
    assert res["url"] == ""
    assert res["snippet"] == ""


def test_load_and_save_glossary_json_with_grounding(tmp_path):
    """Verify loading and saving glossary.json with grounding URLs and snippets works correctly."""
    from import_glossary import load_glossary_json, save_glossary_json
    
    sample_data = {
        "glossary": [
            {
                "english": "bronchitis",
                "translations": {
                    "Spanish": "bronquitis",
                    "Vietnamese": "viêm phế quản"
                },
                "description": "inflammation of the bronchi",
                "url": "https://www.healthdirect.gov.au/bronchitis",
                "Spanish_grounding_url": "https://www.mayoclinic.org/es-es/bronchitis",
                "Spanish_grounding_snippet": "La bronquitis es una inflamación...",
                "Vietnamese_grounding_url": "https://suckhoedoisong.vn/viem-phe-quan",
                "Vietnamese_grounding_snippet": "Viêm phế quản là bệnh lý..."
            }
        ]
    }
    
    json_file = tmp_path / "glossary_grounding.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(sample_data, f)
        
    flat = load_glossary_json(str(json_file))
    
    assert "bronchitis" in flat
    assert flat["bronchitis"]["Spanish_grounding_url"] == "https://www.mayoclinic.org/es-es/bronchitis"
    assert flat["bronchitis"]["Spanish_grounding_snippet"] == "La bronquitis es una inflamación..."
    assert flat["bronchitis"]["Vietnamese_grounding_url"] == "https://suckhoedoisong.vn/viem-phe-quan"
    assert flat["bronchitis"]["Vietnamese_grounding_snippet"] == "Viêm phế quản là bệnh lý..."
    
    # Save back
    json_file_out = tmp_path / "glossary_grounding_out.json"
    save_glossary_json(flat, str(json_file_out))
    
    with open(json_file_out, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
        
    assert "glossary" in saved_data
    assert len(saved_data["glossary"]) == 1
    entry = saved_data["glossary"][0]
    assert entry["english"] == "bronchitis"
    assert entry["Spanish_grounding_url"] == "https://www.mayoclinic.org/es-es/bronchitis"
    assert entry["Spanish_grounding_snippet"] == "La bronquitis es una inflamación..."
    assert entry["Vietnamese_grounding_url"] == "https://suckhoedoisong.vn/viem-phe-quan"
    assert entry["Vietnamese_grounding_snippet"] == "Viêm phế quản là bệnh lý..."


@patch("import_glossary.scrape_healthdirect_page")
@patch("import_glossary.pre_translate_terms")
@patch("import_glossary.upload_to_gcs")
@patch("import_glossary.recreate_gcp_glossary")
@patch("import_glossary.ground_term")
def test_pipeline_execution_with_grounding(mock_ground, mock_recreate, mock_upload, mock_translate, mock_scrape, tmp_path):
    """Verify that the full pipeline correctly invokes search grounding when requested."""
    from import_glossary import run_pipeline, save_glossary_json
    
    mock_scrape.return_value = {
        "bronchitis": {"url": "https://www.healthdirect.gov.au/bronchitis"}
    }
    mock_translate.return_value = {
        "bronchitis": {
            "translations": {"Spanish": "bronquitis", "Vietnamese": "viêm phế quản"},
            "url": "https://www.healthdirect.gov.au/bronchitis"
        }
    }
    
    # Mock grounding outputs
    def side_effect_ground(term, translation, lang):
        if lang == "es":
            return {"url": "https://es.wikipedia.org/wiki/Bronquitis", "snippet": "La bronquitis es..."}
        else:
            return {"url": "https://vi.wikipedia.org/wiki/Viem_phe_quan", "snippet": "Viêm phế quản..."}
    mock_ground.side_effect = side_effect_ground
    
    glossary_json = tmp_path / "glossary.json"
    save_glossary_json({}, str(glossary_json))
    
    import argparse
    args = argparse.Namespace(
        scrape="https://www.healthdirect.gov.au/health-topics/conditions",
        max_letters=1,
        glossary_json=str(glossary_json),
        gcs_destination=None,
        glossary_id=None,
        location="us-central1",
        project_id="test-project",
        pipeline=True,
        ground=True
    )
    
    run_pipeline(args)
    
    assert mock_ground.call_count == 2
    
    # Check that glossary file was updated on disk with grounding
    with open(glossary_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    entry = data["glossary"][0]
    assert entry["english"] == "bronchitis"
    assert entry["Spanish_grounding_url"] == "https://es.wikipedia.org/wiki/Bronquitis"
    assert entry["Spanish_grounding_snippet"] == "La bronquitis es..."
    assert entry["Vietnamese_grounding_url"] == "https://vi.wikipedia.org/wiki/Viem_phe_quan"
    assert entry["Vietnamese_grounding_snippet"] == "Viêm phế quản..."


@patch("google.genai.Client")
def test_search_google_vertex_ai_auth(mock_client_class, monkeypatch):
    from import_glossary import search_google
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("PROJECT_ID", "test-project-123")
    monkeypatch.setenv("LOCATION", "us-east4")
    
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.models.generate_content.return_value = MagicMock(candidates=[])
    
    search_google("asthma")
    mock_client_class.assert_called_with(vertexai=True, project="test-project-123", location="global")


@patch("google.genai.Client")
def test_search_google_general_exception(mock_client_class):
    from import_glossary import search_google
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.models.generate_content.side_effect = Exception("Some arbitrary error")
    
    res = search_google("asthma")
    assert res == []


@patch("google.genai.Client")
def test_search_google_no_candidates(mock_client_class):
    from import_glossary import search_google
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.candidates = []
    mock_client.models.generate_content.return_value = mock_response
    
    res = search_google("asthma")
    assert res == []


@patch("google.genai.Client")
def test_search_google_no_metadata(mock_client_class):
    from import_glossary import search_google
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_candidate = MagicMock()
    mock_candidate.grounding_metadata = None
    mock_response.candidates = [mock_candidate]
    mock_client.models.generate_content.return_value = mock_response
    
    res = search_google("asthma")
    assert res == []


def test_search_google_import_error():
    from import_glossary import search_google
    import builtins
    original_import = builtins.__import__
    
    def mock_import(name, *args, **kwargs):
        if name.startswith("google"):
            raise ImportError("mocked import error")
        return original_import(name, *args, **kwargs)
        
    with patch("builtins.__import__", side_effect=mock_import):
        res = search_google("asthma")
        assert res == []


def test_pre_translate_terms_import_error():
    from import_glossary import pre_translate_terms
    import builtins
    original_import = builtins.__import__
    
    def mock_import(name, *args, **kwargs):
        if "translate_v3" in name:
            raise ImportError("mocked translate import error")
        return original_import(name, *args, **kwargs)
        
    with patch("builtins.__import__", side_effect=mock_import):
        # This should execute without raising an error but client will be None
        updated = pre_translate_terms({"test": {"translations": {}}}, project_id="test-project")
        assert updated["test"]["translations"] == {}


def test_load_glossary_json_exception():
    from import_glossary import load_glossary_json
    with patch("builtins.open", side_effect=Exception("permission error")):
        assert load_glossary_json("some_file.json") == {}


@patch("requests.get")
def test_scrape_healthdirect_page_leaf_filtering(mock_get):
    """Verify that terms scraped on leaf pages are filtered to only those matching the sub-page letter."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    # HTML contains some A-terms and some E-terms
    mock_response.text = """
    <html>
      <body>
        <ul class="article_lists">
          <li><a href="/health-topics/eczema">Eczema</a></li>
          <li><a href="/health-topics/earache">Earache</a></li>
          <li><a href="/health-topics/asthma">Asthma</a></li>
        </ul>
      </body>
    </html>
    """
    mock_get.return_value = mock_response

    # Test with health-topics subpage for E
    terms = scrape_healthdirect_page("https://www.healthdirect.gov.au/health-topics/E", is_subpage=True)
    assert "eczema" in terms
    assert "earache" in terms
    assert "asthma" not in terms


@patch("import_glossary.ground_term")
def test_pipeline_grounding_exhaustive_queue(mock_ground, tmp_path):
    """Verify that terms missing grounding are queued for grounding even if they were not scraped in this run."""
    from import_glossary import run_pipeline
    
    # Save an existing glossary to disk with one term fully grounded, and one translated but missing grounding
    glossary_json = tmp_path / "glossary.json"
    existing_glossary = {
        "glossary": [
            {
                "english": "bronchitis",
                "translations": {"Spanish": "bronquitis", "Vietnamese": "viêm phế quản"},
                "url": "https://www.healthdirect.gov.au/bronchitis",
                "Spanish_grounding_url": "https://es.wikipedia.org/wiki/Bronquitis",
                "Spanish_grounding_snippet": "La bronquitis es...",
                "Vietnamese_grounding_url": "https://vi.wikipedia.org/wiki/Viem_phe_quan",
                "Vietnamese_grounding_snippet": "Viêm phế quản..."
            },
            {
                "english": "diabetes",
                "translations": {"Spanish": "diabetes", "Vietnamese": "bệnh tiểu đường"},
                "url": "https://www.healthdirect.gov.au/diabetes"
                # Missing Spanish and Vietnamese grounding fields!
            }
        ]
    }
    with open(glossary_json, "w", encoding="utf-8") as f:
        json.dump(existing_glossary, f)
        
    mock_ground.side_effect = lambda term, translation, lang: {
        "url": f"https://mocked.org/{lang}/{translation}",
        "snippet": f"Mocked {lang} info"
    }
    
    import argparse
    # Run pipeline with ground=True but scrape=None (no scraped terms)
    args = argparse.Namespace(
        scrape=None,
        max_letters=None,
        glossary_json=str(glossary_json),
        gcs_destination=None,
        glossary_id=None,
        location="us-central1",
        project_id="test-project",
        pipeline=True,
        ground=True
    )
    
    run_pipeline(args)
    
    # ground_term should be called for the missing diabetes grounding (both es and vi)
    assert mock_ground.call_count == 2
    
    with open(glossary_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    flat_data = {entry["english"]: entry for entry in data["glossary"]}
    assert "Spanish_grounding_url" in flat_data["diabetes"]
    assert "Vietnamese_grounding_url" in flat_data["diabetes"]
    assert flat_data["diabetes"]["Spanish_grounding_url"] == "https://mocked.org/es/diabetes"
    assert flat_data["diabetes"]["Vietnamese_grounding_url"] == "https://mocked.org/vi/bệnh tiểu đường"


@patch("google.cloud.translate_v3.TranslationServiceClient")
def test_pre_translate_progressive_save(mock_client_class, tmp_path):
    """Verify that pre_translate_terms calls save_callback after translating each term."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_translation_es = MagicMock()
    mock_translation_es.translated_text = "asma"
    
    mock_client.translate_text.return_value = MagicMock(translations=[mock_translation_es])
    
    from import_glossary import pre_translate_terms
    
    glossary = {
        "asthma": {
            "translations": {},
            "url": "https://www.healthdirect.gov.au/asthma"
        }
    }
    
    mock_callback = MagicMock()
    # Run translation
    pre_translate_terms(glossary, project_id="test-project", save_callback=mock_callback)
    
    # Check that save_callback was triggered
    mock_callback.assert_called_once()


@patch("urllib.robotparser.RobotFileParser")
def test_is_crawl_allowed_success(mock_parser_class):
    """Verify that is_crawl_allowed parses robots.txt and correctly checks can_fetch."""
    from import_glossary import is_crawl_allowed, _robots_cache
    
    # Clear cache before run
    _robots_cache.clear()
    
    mock_parser = MagicMock()
    mock_parser_class.return_value = mock_parser
    mock_parser.can_fetch.return_value = True
    
    # Temporarily disable the global autouse mock for this test
    with patch("import_glossary.is_crawl_allowed", wraps=is_crawl_allowed):
        allowed = is_crawl_allowed("https://www.healthdirect.gov.au/medicines")
        
    assert allowed is True
    mock_parser.set_url.assert_called_once_with("https://www.healthdirect.gov.au/robots.txt")
    mock_parser.read.assert_called_once()
    mock_parser.can_fetch.assert_called_once_with(
        "HealthDirectGlossaryImporter/1.0 (Bilingual Translation Experiment)",
        "https://www.healthdirect.gov.au/medicines"
    )


@patch("requests.get")
@patch("time.sleep")
def test_scrape_healthdirect_page_idempotency(mock_sleep, mock_get, tmp_path):
    """Verify that scrape_healthdirect_page skips requests for already successfully scraped subpages."""
    from import_glossary import scrape_healthdirect_page, save_scrape_state
    
    state_file = str(tmp_path / "scrape_state.json")
    
    # Mark a subpage URL as successfully scraped
    url = "https://www.healthdirect.gov.au/medicines/search-results/A-excludeNonArtg"
    save_scrape_state({url}, state_file)
    
    # Try scraping it with force=False
    terms = scrape_healthdirect_page(
        url,
        is_subpage=True,
        force=False,
        delay=0.0,
        state_path=state_file
    )
    
    # It should skip request and return empty dictionary
    assert terms == {}
    mock_get.assert_not_called()
    
    # Try scraping with force=True
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body><a href='/medicines/aspirin'>Aspirin</a></body></html>"
    mock_get.return_value = mock_response
    
    terms_forced = scrape_healthdirect_page(
        url,
        is_subpage=True,
        force=True,
        delay=0.0,
        state_path=state_file
    )
    
    assert "aspirin" in terms_forced
    mock_get.assert_called_once()


@patch("requests.get")
@patch("time.sleep")
def test_scrape_healthdirect_page_politeness_delay(mock_sleep, mock_get):
    """Verify that scrape_healthdirect_page respects the requested politeness delay."""
    from import_glossary import scrape_healthdirect_page
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body><a href='/medicines/panadol'>Paracetamol</a></body></html>"
    mock_get.return_value = mock_response
    
    url = "https://www.healthdirect.gov.au/medicines/search-results/A-excludeNonArtg"
    
    # Scraping with delay = 2.5 seconds
    scrape_healthdirect_page(
        url,
        is_subpage=True,
        delay=2.5,
        force=True,
        state_path="dummy_state_path.json"
    )
    
    mock_sleep.assert_called_once_with(2.5)


@patch("google.cloud.translate_v3.TranslationServiceClient")
def test_pre_translate_terms_custom_languages(mock_client_class):
    """Verify that pre_translate_terms correctly supports custom target languages."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_translation = MagicMock()
    mock_translation.translated_text = "Fieber"
    mock_client.translate_text.return_value = MagicMock(translations=[mock_translation])
    
    from import_glossary import pre_translate_terms
    
    glossary = {
        "fever": {
            "translations": {},
            "url": "https://www.healthdirect.gov.au/fever"
        }
    }
    
    # Translate specifically to German (de)
    updated = pre_translate_terms(glossary, project_id="test-project", languages={"German": "de"})
    
    assert "German" in updated["fever"]["translations"]
    assert updated["fever"]["translations"]["German"] == "Fieber"
    # Ensure standard ones are NOT present unless specifically requested
    assert "Spanish" not in updated["fever"]["translations"]
    assert "Vietnamese" not in updated["fever"]["translations"]












