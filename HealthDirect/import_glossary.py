import re
import requests
from bs4 import BeautifulSoup

def clean_term_name(text: str) -> str:
    """Cleans a term name by removing parenthetical remarks and extra whitespace."""
    # Remove anything inside parenthesis, e.g., "Amoxicillin (antibiotic)" -> "Amoxicillin"
    text = re.sub(r'\s*\([^)]*\)', '', text)
    # Strip whitespace and convert to lowercase
    return text.strip().lower()

def parse_html_terms(html_content: str) -> dict:
    """Parses term list from HealthDirect directory HTML content."""
    soup = BeautifulSoup(html_content, "html.parser")
    terms = {}
    
    # Extract links that contain medicines or health-topics paths
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Match relative or absolute HealthDirect URLs
        if "/medicines/" in href or "/health-topics/" in href:
            term_text = a.get_text()
            cleaned_name = clean_term_name(term_text)
            if cleaned_name:
                # Resolve relative URL to absolute URL
                if href.startswith("/"):
                    full_url = f"https://www.healthdirect.gov.au{href}"
                else:
                    full_url = href
                terms[cleaned_name] = {"url": full_url}
                
    return terms

def scrape_healthdirect_page(url: str) -> dict:
    """Scrapes a HealthDirect webpage and extracts clinical terms."""
    headers = {
        "User-Agent": "HealthDirectGlossaryImporter/1.0 (Bilingual Translation Experiment)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return parse_html_terms(response.text)
    except Exception as e:
        # Return empty dictionary in case of scraping failure
        return {}

def merge_glossaries(existing_glossary: dict, scraped_glossary: dict) -> dict:
    """Merges scraped terms into an existing glossary, avoiding duplicates."""
    merged = existing_glossary.copy()
    
    for term, data in scraped_glossary.items():
        if term not in merged:
            merged[term] = {
                "translations": {},
                "url": data["url"]
            }
        else:
            # If the term exists, ensure we keep its translations and description,
            # but preserve or update URL if missing.
            if "url" not in merged[term]:
                merged[term]["url"] = data["url"]
                
    return merged

def pre_translate_terms(glossary: dict, project_id: str = None) -> dict:
    """Pre-populates missing Spanish and Vietnamese translations using Google Cloud Translation V3."""
    import os
    updated = {}
    
    # Deep copy glossary structure
    for term, data in glossary.items():
        updated[term] = {
            "translations": data.get("translations", {}).copy(),
            "url": data.get("url", "")
        }
        if "description" in data:
            updated[term]["description"] = data["description"]
            
    if not project_id:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
        
    client = None
    if project_id:
        try:
            from google.cloud import translate_v3
            client = translate_v3.TranslationServiceClient()
        except ImportError:
            pass
            
    for term, data in updated.items():
        if "translations" not in data:
            data["translations"] = {}
            
        # Translate to Spanish
        if "Spanish" not in data["translations"] or not data["translations"]["Spanish"]:
            if client and project_id:
                try:
                    response = client.translate_text(
                        request={
                            "parent": f"projects/{project_id}/locations/global",
                            "contents": [term],
                            "mime_type": "text/plain",
                            "source_language_code": "en",
                            "target_language_code": "es",
                        }
                    )
                    if response.translations:
                        data["translations"]["Spanish"] = response.translations[0].translated_text
                except Exception as e:
                    pass
                    
        # Translate to Vietnamese
        if "Vietnamese" not in data["translations"] or not data["translations"]["Vietnamese"]:
            if client and project_id:
                try:
                    response = client.translate_text(
                        request={
                            "parent": f"projects/{project_id}/locations/global",
                            "contents": [term],
                            "mime_type": "text/plain",
                            "source_language_code": "en",
                            "target_language_code": "vi",
                        }
                    )
                    if response.translations:
                        data["translations"]["Vietnamese"] = response.translations[0].translated_text
                except Exception as e:
                    pass
                    
    return updated

if __name__ == "__main__":
    import argparse
    import json
    import sys
    
    # Handle single-dash -scrape as standard argparse --scrape
    args_to_parse = []
    for arg in sys.argv[1:]:
        if arg == "-scrape":
            args_to_parse.append("--scrape")
        else:
            args_to_parse.append(arg)
            
    parser = argparse.ArgumentParser(description="HealthDirect Glossary Importer & Scraper Utility")
    parser.add_argument("--scrape", "-s", type=str, help="URL to scrape terms from")
    
    parsed_args = parser.parse_args(args_to_parse)
    
    if parsed_args.scrape:
        terms = scrape_healthdirect_page(parsed_args.scrape)
        print(json.dumps(terms, indent=2))
