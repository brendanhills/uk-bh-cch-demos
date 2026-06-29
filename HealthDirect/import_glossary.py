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
    
    # 1. Look for HealthTopics/Conditions/Symptoms lists: ul.article_lists-column or section.article_lists
    topic_containers = soup.find_all(class_=re.compile(r"article_lists"))
    
    # 2. Look for Medicines brand results lists: ul with class containing product-list or brand-results results
    meds_containers = soup.find_all(class_=re.compile(r"(product-list|brand-results)"))
    
    # Combine containers to search in
    containers = topic_containers + meds_containers
    
    if containers:
        for container in containers:
            for a in container.find_all("a", href=True):
                href = a["href"]
                # Skip any relative anchor links, or parent category links if they don't look like actual items
                if href.startswith("#") or href == "/health-topics" or href == "/medicines":
                    continue
                term_text = a.get_text()
                cleaned_name = clean_term_name(term_text)
                if cleaned_name:
                    if href.startswith("/"):
                        full_url = f"https://www.healthdirect.gov.au{href}"
                    else:
                        full_url = href
                    terms[cleaned_name] = {"url": full_url}
    
    # Fallback to general matching if no specific containers were found
    if not terms:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            # Exclude top level directory paths as terms themselves
            if href.rstrip("/") in ["/medicines", "/health-topics", "/health-topics/conditions", "/health-topics/symptoms", "/health-topics/procedures"]:
                continue
            if "/medicines/" in href or "/health-topics/" in href:
                term_text = a.get_text()
                cleaned_name = clean_term_name(term_text)
                if cleaned_name:
                    if href.startswith("/"):
                        full_url = f"https://www.healthdirect.gov.au{href}"
                    else:
                        full_url = href
                    terms[cleaned_name] = {"url": full_url}
                    
    return terms

def scrape_healthdirect_page(url: str, max_letters: int = None, is_subpage: bool = False) -> dict:
    """Scrapes a HealthDirect webpage and extracts clinical terms, recursively crawling if it is an index."""
    headers = {
        "User-Agent": "HealthDirectGlossaryImporter/1.0 (Bilingual Translation Experiment)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        return {}

    soup = BeautifulSoup(html, "html.parser")
    
    # If we are already on a subpage (A-Z leaf page), do not attempt recursive crawl of navigation links.
    if is_subpage:
        return parse_html_terms(html)
    
    # Check if the page is a directory index containing alphabetical A-Z links.
    # On healthdirect, these links are like: href="/health-topics/A" or href="/medicines/search-results/A-excludeNonArtg"
    sub_links = []
    seen_hrefs = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Match alphabetical sub-page patterns
        if re.search(r"/health-topics/[A-Z]$", href) or re.search(r"/medicines/search-results/[A-Z]-excludeNonArtg", href):
            if href not in seen_hrefs:
                seen_hrefs.add(href)
                if href.startswith("/"):
                    sub_links.append(f"https://www.healthdirect.gov.au{href}")
                else:
                    sub_links.append(href)
                    
    if sub_links:
        # Sort sub_links to ensure alphabetical order (A-Z)
        sub_links.sort()
        if max_letters is not None:
            sub_links = sub_links[:max_letters]
            
        # Recursive crawling: Scrape each alphabetical subpage and merge
        consolidated_terms = {}
        for link in sub_links:
            sub_terms = scrape_healthdirect_page(link, is_subpage=True)
            consolidated_terms.update(sub_terms)
        return consolidated_terms
    else:
        # No sub-links found, so this is an individual alphabetical page.
        # Parse terms directly on this page.
        return parse_html_terms(html)

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
    
    # Handle single-dash options like -scrape and -max as standard argparse
    args_to_parse = []
    for arg in sys.argv[1:]:
        if arg == "-scrape":
            args_to_parse.append("--scrape")
        elif arg == "-max":
            args_to_parse.append("--max-letters")
        else:
            args_to_parse.append(arg)
            
    parser = argparse.ArgumentParser(description="HealthDirect Glossary Importer & Scraper Utility")
    parser.add_argument("--scrape", "-s", type=str, help="URL to scrape terms from")
    parser.add_argument("--max-letters", "-m", type=int, default=None, help="Maximum alphabetical letters to crawl")
    
    parsed_args = parser.parse_args(args_to_parse)
    
    if parsed_args.scrape:
        terms = scrape_healthdirect_page(parsed_args.scrape, max_letters=parsed_args.max_letters)
        print(json.dumps(terms, indent=2))
