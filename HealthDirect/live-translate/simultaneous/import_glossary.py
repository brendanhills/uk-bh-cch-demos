import os
# Force standard TLS/HTTPS over Application Default Credentials (ADC) to prevent mTLS client certificate errors on VM
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import re
import requests
from bs4 import BeautifulSoup

try:
    from google.cloud import storage
except ImportError:
    storage = None


def clean_term_name(text: str) -> str:
    """Cleans a term name by removing parenthetical remarks and extra whitespace."""
    # Remove anything inside parenthesis, e.g., "Amoxicillin (antibiotic)" -> "Amoxicillin"
    text = re.sub(r'\s*\([^)]*\)', '', text)
    # Strip whitespace and convert to lowercase
    return text.strip().lower()

def extract_parenthetical_term(text: str, href: str) -> tuple[str, str | None]:
    """Helper to parse 'Primary (Synonym)' structures using URL slug comparison.
    
    Returns a tuple of (primary_clinical_key, informal_synonym_or_none).
    """
    text = text.strip()
    href_slug = href.rstrip("/").split("/")[-1].lower().replace("-", " ").strip()
    
    match = re.match(r"^(.*?)\s*\((.*?)\)$", text)
    if match:
        outside = match.group(1).strip().lower()
        inside = match.group(2).strip().lower()
        
        # If the inside term matches the URL slug, the inside term is the generic clinical key,
        # and the outside term is a brand name / colloquial synonym.
        # e.g., 'Amoxil (amoxicillin)' on '/medicines/amoxicillin'
        if inside == href_slug or inside in href_slug or href_slug in inside:
            return inside, outside
            
        # If the outside term matches the slug, the outside term is the generic clinical key,
        # e.g., 'Amoxicillin (antibiotic)' on '/medicines/amoxicillin' or 'Middle ear infection (otitis media)'
        if outside == href_slug or outside in href_slug or href_slug in outside:
            # Check if inside text is a known generic class keyword to ignore it as synonym
            if inside in ["antibiotic", "brand name", "generic", "procedures", "symptoms", "conditions"]:
                return outside, None
            return outside, inside
            
        # Fallback if slug matching is inconclusive: treat outside as main term, inside as synonym if not a class word
        if inside in ["antibiotic", "brand name", "generic", "procedures", "symptoms", "conditions"]:
            return outside, None
        return outside, inside
        
    return clean_term_name(text), None

def parse_html_terms(html_content: str) -> dict:
    """Parses term list from HealthDirect directory HTML content with parenthetical synonyms."""
    soup = BeautifulSoup(html_content, "html.parser")
    terms = {}
    
    def add_term_link(term_text, href):
        if href.startswith("#") or href in ["/health-topics", "/medicines", "/health-topics/conditions", "/health-topics/symptoms", "/health-topics/procedures"]:
            return
        
        full_url = f"https://www.healthdirect.gov.au{href}" if href.startswith("/") else href
        primary_key, synonym = extract_parenthetical_term(term_text, href)
        
        if primary_key:
            if primary_key not in terms:
                terms[primary_key] = {"url": full_url, "synonyms": []}
            elif "synonyms" not in terms[primary_key]:
                # If it was added as an alias reference first, upgrade it to a main term
                terms[primary_key]["synonyms"] = []
                terms[primary_key].pop("formal_name", None)

            if synonym and synonym != primary_key and synonym not in terms[primary_key]["synonyms"]:
                terms[primary_key]["synonyms"].append(synonym)
                
            # Also add the synonym as a reference key in the parsed dict pointing to same URL 
            # to make sure the crawling pipeline matches it and doesn't skip it!
            if synonym and synonym not in terms:
                terms[synonym] = {"url": full_url, "formal_name": primary_key}

    # 1. Look for HealthTopics/Conditions/Symptoms lists: ul.article_lists-column or section.article_lists
    topic_containers = soup.find_all(class_=re.compile(r"article_lists"))
    
    # 2. Look for Medicines brand results lists: ul with class containing product-list or brand-results results
    meds_containers = soup.find_all(class_=re.compile(r"(product-list|brand-results)"))
    
    # Combine containers to search in
    containers = topic_containers + meds_containers
    
    if containers:
        for container in containers:
            for a in container.find_all("a", href=True):
                add_term_link(a.get_text(), a["href"])
    
    # Fallback to general matching if no specific containers were found
    if not terms:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.rstrip("/") in ["/medicines", "/health-topics", "/health-topics/conditions", "/health-topics/symptoms", "/health-topics/procedures"]:
                continue
            if "/medicines/" in href or "/health-topics/" in href:
                add_term_link(a.get_text(), href)
                
    return terms

_robots_cache = {}

def is_crawl_allowed(url: str, user_agent: str = "HealthDirectGlossaryImporter/1.0 (Bilingual Translation Experiment)") -> bool:
    """Checks robots.txt to verify if crawling the specified URL is allowed."""
    from urllib.robotparser import RobotFileParser
    from urllib.parse import urlparse
    
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain not in _robots_cache:
        robots_url = f"{parsed_url.scheme}://{domain}/robots.txt"
        rp = RobotFileParser()
        try:
            print(f"[INFO] Fetching and parsing {robots_url} to check crawling restrictions...")
            rp.set_url(robots_url)
            rp.read()
            _robots_cache[domain] = rp
        except Exception as e:
            print(f"[INFO] Could not fetch/parse robots.txt from {robots_url} ({e}). Defaulting to allowed.")
            _robots_cache[domain] = None
            
    rp = _robots_cache[domain]
    if rp is None:
        return True
    
    allowed = rp.can_fetch(user_agent, url)
    if not allowed:
        print(f"[WARNING] Crawl disallowed by robots.txt for URL: {url}")
    return allowed


def load_scrape_state(filepath: str) -> set:
    """Loads the set of successfully scraped URLs from the state file."""
    import json
    if not os.path.exists(filepath):
        return set()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("scraped_urls", []))
    except Exception as e:
        print(f"[WARNING] Error reading scrape state file: {e}. Starting with empty state.")
        return set()


def save_scrape_state(scraped_urls: set, filepath: str) -> None:
    """Saves the set of successfully scraped URLs to the state file."""
    import json
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"scraped_urls": sorted(list(scraped_urls))}, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[WARNING] Error saving scrape state file: {e}")


def scrape_healthdirect_page(
    url: str,
    max_letters: int = None,
    is_subpage: bool = False,
    delay: float = 1.0,
    force: bool = False,
    state_path: str = "glossary/scrape_state.json"
) -> dict:
    """Scrapes a HealthDirect webpage and extracts clinical terms, recursively crawling if it is an index."""
    user_agent = "HealthDirectGlossaryImporter/1.0 (Bilingual Translation Experiment)"
    
    # 1. Check crawling restrictions via robots.txt
    if not is_crawl_allowed(url, user_agent=user_agent):
        print(f"Skipping crawl for disallowed URL: {url}")
        return {}
        
    # 2. For sub-pages (actual leaf letters), check if already scraped
    if is_subpage:
        scraped_set = load_scrape_state(state_path)
        if url in scraped_set and not force:
            print(f"Idempotency: URL '{url}' already successfully scraped in a previous run. Skipping request.")
            return {}

    # 3. Apply politeness delay
    if delay > 0:
        import time
        print(f"Politeness delay: sleeping for {delay} seconds before requesting {url}...")
        time.sleep(delay)

    print(f"Scraping page: {url} ...")
    headers = {
        "User-Agent": user_agent
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {}

    soup = BeautifulSoup(html, "html.parser")
    
    # If we are already on a subpage (A-Z leaf page), do not attempt recursive crawl of navigation links.
    if is_subpage:
        terms = parse_html_terms(html)
        # Extract target letter from the sub-page URL (e.g., /health-topics/E or /medicines/search-results/P-excludeNonArtg)
        target_letter = None
        match = re.search(r"/health-topics/([A-Za-z])$", url)
        if not match:
            match = re.search(r"/medicines/search-results/([A-Za-z])(?:-|$)", url)
        if match:
            target_letter = match.group(1).upper()
            
        if target_letter:
            filtered_terms = {k: v for k, v in terms.items() if k.upper().startswith(target_letter)}
            print(f"  Extracted {len(terms)} terms, filtered down to {len(filtered_terms)} matching '{target_letter}' from leaf page {url}")
            terms = filtered_terms
        else:
            print(f"  Extracted {len(terms)} terms from leaf page {url}")
            
        # Successfully scraped leaf page: save to state to ensure idempotency
        if terms:
            scraped_set = load_scrape_state(state_path)
            scraped_set.add(url)
            save_scrape_state(scraped_set, state_path)
            
        return terms
    
    # Check if the page is a directory index containing alphabetical A-Z links.
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
        if max_letters is not None:
            import random
            # Randomly sample sub-pages/letters from all available ones
            sampled_links = random.sample(sub_links, min(max_letters, len(sub_links)))
            # Sort them so they are processed in alphabetical order
            sampled_links.sort()
            print(f"Found {len(sub_links)} sub-pages. Randomly selected {len(sampled_links)} letters (as requested).")
            sub_links = sampled_links
        else:
            # Sort all sub_links to ensure alphabetical order when crawling everything
            sub_links.sort()
            print(f"Found {len(sub_links)} sub-pages to crawl.")
            
        # Recursive crawling: Scrape each alphabetical subpage and merge
        consolidated_terms = {}
        for link in sub_links:
            sub_terms = scrape_healthdirect_page(
                link,
                is_subpage=True,
                delay=delay,
                force=force,
                state_path=state_path
            )
            consolidated_terms.update(sub_terms)
        print(f"Consolidated a total of {len(consolidated_terms)} terms from index crawl.")
        return consolidated_terms
    else:
        # No sub-links found, so this is an individual alphabetical page.
        terms = parse_html_terms(html)
        print(f"Extracted {len(terms)} terms from single page {url}")
        return terms


def build_search_query(term: str, language: str) -> str:
    """Constructs a Google search query for a term in Spanish or Vietnamese with auxiliary terms."""
    cleaned_lang = language.lower().strip()
    if cleaned_lang == "es":
        return f'"{term}" salud OR medicina'
    elif cleaned_lang == "vi":
        return f'"{term}" sức khỏe OR y tế OR bệnh'
    else:
        raise ValueError(f"Unsupported language: {language}")


def parse_search_results(html: str) -> list[dict]:
    """Parses Google Search results from HTML and extracts URLs and snippets."""
    from urllib.parse import urlparse, parse_qs
    soup = BeautifulSoup(html, "html.parser")
    results = []
    
    for g in soup.find_all(class_="g"):
        a_tag = g.find("a", href=True)
        if not a_tag:
            continue
            
        href = a_tag["href"]
        parsed = urlparse(href)
        if parsed.path == "/url":
            qs = parse_qs(parsed.query)
            if "q" in qs:
                href = qs["q"][0]
                
        # Exclude Google's own internal URLs
        domain = urlparse(href).netloc.lower()
        if domain == "google.com" or domain.endswith(".google.com") or not href.startswith("http"):
            continue
            
        # Extract snippet
        snippet_el = (
            g.find(class_="st") or 
            g.find(class_="IsZC3b") or 
            g.find(class_="VwiC3b") or 
            g.find(class_="aCO63b")
        )
        if snippet_el:
            snippet = snippet_el.get_text()
        else:
            # Fallback: get all text from elements in the div that are not part of the anchor
            text_blocks = []
            for child in g.descendants:
                if child.name in ["span", "div", "p"] and child.get_text() and child not in a_tag.descendants:
                    text_blocks.append(child.get_text())
            snippet = " ".join(text_blocks) if text_blocks else ""
            
        snippet = re.sub(r'\s+', ' ', snippet).strip()
        results.append({
            "url": href,
            "snippet": snippet
        })
        
    return results


class GoogleRateLimitError(Exception):
    """Exception raised when Google Search returns a 429 Too Many Requests status code."""
    pass


def search_google(query: str) -> list[dict]:
    """Performs search grounding using the Gemini API (Gemini 3 or later) with Google Search Tool."""
    import os
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: The 'google-genai' SDK is not installed. Please install it or check dependencies.")
        return []

    # Initialize the genai client.
    # Check for GEMINI_API_KEY first. If not present, use Vertex AI.
    gemini_key = os.environ.get("GEMINI_API_KEY")
    try:
        if gemini_key:
            client = genai.Client(api_key=gemini_key)
        else:
            project_id = os.environ.get("PROJECT_ID") or os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
            # Always use 'global' location for Vertex AI in search grounding.
            # Preview and current generation Gemini 3.x/3.5 models are served globally,
            # whereas regional endpoints (like us-central1) are often restricted.
            location = "global"
            if project_id:
                client = genai.Client(vertexai=True, project=project_id, location=location)
            else:
                # Fallback to default Client initialization (picks up credentials/variables from env)
                client = genai.Client()
                
        # Fallback list of models (trying Gemini 3.x first)
        models_to_try = ["gemini-3.5-flash", "gemini-3.1-flash-lite"]
        response = None
        last_err = None
        
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=f"Perform a search to find the correct medical definition and source URL for: {query}. Respond with a single concise sentence describing the term.",
                    config=types.GenerateContentConfig(
                        tools=[{"google_search": {}}]
                    )
                )
                break
            except Exception as e:
                err_msg = str(e).lower()
                # If it's a rate limit error, raise it immediately to halt the loop
                if "429" in err_msg or "resource_exhausted" in err_msg or "too many requests" in err_msg or "resourceexhausted" in err_msg:
                    raise GoogleRateLimitError(f"Gemini API Rate Limit hit: {e}")
                # Otherwise, log and try next model
                print(f"  Model {model_name} search grounding failed or not available in global region: {e}. Trying fallback...")
                last_err = e
                
        if response is None:
            if last_err:
                print(f"Gemini search grounding failed for query '{query}' after trying all fallback models: {last_err}")
            return []
        
        if not response.candidates:
            return []
            
        metadata = response.candidates[0].grounding_metadata
        if not metadata:
            return []
            
        snippet = response.text.strip() if response.text else ""
        results = []
        if metadata.grounding_chunks:
            for chunk in metadata.grounding_chunks:
                if chunk.web and chunk.web.uri:
                    results.append({
                        "url": chunk.web.uri,
                        "snippet": snippet or chunk.web.title or ""
                    })
                    
        return results
    except Exception as e:
        err_msg = str(e).lower()
        if "429" in err_msg or "resource_exhausted" in err_msg or "too many requests" in err_msg or "resourceexhausted" in err_msg:
            raise GoogleRateLimitError(f"Gemini API Rate Limit hit: {e}")
        print(f"Gemini search grounding error for query '{query}': {e}")
        return []


def ground_term(term: str, translation: str, language: str) -> dict:
    """Constructs a medical query for a translated term, runs a search, and returns top result metadata."""
    if not translation:
        return {"url": "", "snippet": ""}
    try:
        query = build_search_query(translation, language)
        results = search_google(query)
        if results:
            return {
                "url": results[0]["url"],
                "snippet": results[0]["snippet"]
            }
    except GoogleRateLimitError:
        # Re-raise so calling functions can stop the loop
        raise
    except Exception as e:
        print(f"Grounding failed for term '{term}' ({translation}, {language}): {e}")
    return {"url": "", "snippet": ""}


def merge_glossaries(existing_glossary: dict, scraped_glossary: dict) -> dict:
    """Merges scraped terms into an existing glossary, avoiding duplicates."""
    merged = existing_glossary.copy()
    
    for term, data in scraped_glossary.items():
        # If the scraped entry has a formal_name, we skip it here as it was added as an alias reference in parse_html_terms,
        # but its synonyms are already mapped under the main clinical term.
        if "formal_name" in data:
            continue
            
        if term not in merged:
            merged[term] = {
                "translations": {},
                "url": data["url"]
            }
        else:
            if "url" not in merged[term]:
                merged[term]["url"] = data["url"]
                
        # Merge synonyms into informal_english
        if "synonyms" in data and data["synonyms"]:
            if "informal_english" not in merged[term]:
                merged[term]["informal_english"] = []
            for syn in data["synonyms"]:
                if syn not in merged[term]["informal_english"]:
                    merged[term]["informal_english"].append(syn)
                    
    return merged

def pre_translate_terms(glossary: dict, project_id: str = None, save_callback: callable = None, languages: dict = None) -> dict:
    """Pre-populates missing translations using Google Cloud Translation V3."""
    import os
    updated = {}
    
    # Deep copy glossary structure
    for term, data in glossary.items():
        updated[term] = data.copy()
        updated[term]["translations"] = data.get("translations", {}).copy()
            
    if not project_id:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
        
    client = None
    if project_id:
        try:
            from google.cloud import translate_v3
            client = translate_v3.TranslationServiceClient()
            print(f"GCP Translation Service Client initialized using project '{project_id}'")
        except ImportError:
            print("Google Cloud Translation library is not installed.")
            pass
        except Exception as e:
            print(f"Failed to initialize GCP Translation client: {e}")
            pass
    else:
        print("No GCP project_id specified or found in environment. Skipping API translations.")
            
    if languages is None:
        languages = {"Spanish": "es", "Vietnamese": "vi", "Arabic": "ar"}

    missing_counts = {}
    for lang_name in languages:
        missing_terms = [t for t, d in updated.items() if lang_name not in d.get("translations", {}) or not d["translations"][lang_name]]
        missing_counts[lang_name] = missing_terms

    print("Translation pipeline counts:")
    for lang_name, missing_terms in missing_counts.items():
        print(f"  - {lang_name}: {len(missing_terms)} translations need generating.")
            
    for term, data in updated.items():
        if "translations" not in data:
            data["translations"] = {}
            
        translated_any = False
        for lang_name, lang_code in languages.items():
            if lang_name not in data["translations"] or not data["translations"][lang_name]:
                if client and project_id:
                    try:
                        print(f"  Translating '{term}' -> {lang_name} ({lang_code})...")
                        informal_list = data.get("informal_english", [])
                        contents_to_translate = [term] + list(informal_list)
                        
                        response = client.translate_text(
                            request={
                                "parent": f"projects/{project_id}/locations/global",
                                "contents": contents_to_translate,
                                "mime_type": "text/plain",
                                "source_language_code": "en",
                                "target_language_code": lang_code,
                            }
                        )
                        if response.translations:
                            formal_translated = response.translations[0].translated_text
                            informal_translated_list = [trans.translated_text for trans in response.translations[1:]]
                            
                            if informal_translated_list:
                                data["translations"][lang_name] = {
                                    "formal": formal_translated,
                                    "informal": informal_translated_list
                                }
                            else:
                                data["translations"][lang_name] = formal_translated
                                
                            print(f"    {lang_name}: {data['translations'][lang_name]}")
                            translated_any = True
                    except Exception as e:
                        print(f"    Failed translating '{term}' to {lang_name}: {e}")
                        pass
                    
        if translated_any and save_callback:
            save_callback(updated)
                    
    return updated

def load_glossary_json(filepath: str) -> dict:
    """Loads dictionary/glossary.json into our flat internal dict format."""
    import json
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        flat = {}
        for entry in data.get("glossary", []):
            eng = entry.get("english", "").lower().strip()
            if eng:
                flat[eng] = {
                    "translations": entry.get("translations", {}),
                    "description": entry.get("description", ""),
                    "url": entry.get("url", ""),
                    "informal_english": entry.get("informal_english", []),
                    "Spanish_grounding_url": entry.get("Spanish_grounding_url", ""),
                    "Spanish_grounding_snippet": entry.get("Spanish_grounding_snippet", ""),
                    "Vietnamese_grounding_url": entry.get("Vietnamese_grounding_url", ""),
                    "Vietnamese_grounding_snippet": entry.get("Vietnamese_grounding_snippet", "")
                }
        return flat
    except Exception:
        return {}


def save_glossary_json(flat_glossary: dict, filepath: str) -> None:
    """Saves our flat internal dict format back to the standard dictionary/glossary.json list format."""
    import json
    glossary_list = []
    for term, data in flat_glossary.items():
        entry = {
            "english": term,
            "translations": data.get("translations", {}),
            "description": data.get("description", "")
        }
        if data.get("url"):
            entry["url"] = data["url"]
        if data.get("informal_english"):
            entry["informal_english"] = data["informal_english"]
            
        # Add grounding fields if present
        for field in [
            "Spanish_grounding_url", "Spanish_grounding_snippet",
            "Vietnamese_grounding_url", "Vietnamese_grounding_snippet"
        ]:
            if data.get(field):
                entry[field] = data[field]
                
        glossary_list.append(entry)

        
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"glossary": glossary_list}, f, indent=2, ensure_ascii=False)

def export_to_csv(glossary: dict, csv_path: str, languages: dict = None) -> int:
    """Exports local glossary terms and translations into a Google Translation V3 multi-lingual CSV.
    Returns the number of fully-translated entries successfully exported.
    """
    import csv
    
    if languages is None:
        # Discover languages dynamically from the database
        discovered_languages = set()
        for term, data in glossary.items():
            for lang in data.get("translations", {}).keys():
                discovered_languages.add(lang)
        
        language_code_map = {
            "spanish": "es",
            "vietnamese": "vi",
            "arabic": "ar",
            "german": "de",
            "french": "fr",
            "italian": "it",
            "japanese": "ja",
            "chinese": "zh",
            "korean": "ko",
            "portuguese": "pt",
            "russian": "ru",
        }
        
        preferred_order = ["Spanish", "Vietnamese", "Arabic"]
        discovered_langs = sorted(list(discovered_languages))
        
        ordered_langs = []
        for pref in preferred_order:
            if pref in discovered_langs:
                ordered_langs.append(pref)
                discovered_langs.remove(pref)
        ordered_langs.extend(discovered_langs)
        
        languages = {}
        for lang in ordered_langs:
            code = language_code_map.get(lang.lower(), lang.lower()[:2])
            languages[lang] = code

    count = 0
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Build headers list: e.g. ["en", "es", "vi", "ar"]
        headers = ["en"]
        lang_columns = [] # list of (lang_name, lang_code)
        for lang_name, lang_code in languages.items():
            headers.append(lang_code)
            lang_columns.append((lang_name, lang_code))
            
        writer.writerow(headers)
        
        for term, data in glossary.items():
            translations = data.get("translations", {})
            row = [term]
            has_all_translations = True
            
            for lang_name, lang_code in lang_columns:
                trans_val = translations.get(lang_name, "")
                
                # Helper to format field (which can be a string or a dict)
                def format_field(val):
                    if isinstance(val, dict):
                        formal = val.get("formal", "")
                        informal_list = val.get("informal", [])
                        if isinstance(informal_list, str):
                            informal_list = [informal_list]
                        parts = []
                        if formal:
                            parts.append(f"formal: {formal}")
                        if informal_list:
                            parts.append(f"informal: {', '.join(informal_list)}")
                        return " | ".join(parts)
                    return str(val).strip()

                formatted_str = format_field(trans_val)
                if not formatted_str:
                    has_all_translations = False
                    break
                row.append(formatted_str)
                
            # GCP Translation V3 requires all language fields to be populated in multilingual glossaries.
            # Only export entries that are fully translated across all requested languages.
            if term and has_all_translations:
                writer.writerow(row)
                count += 1
                
    return count

def upload_to_gcs(local_file_path: str, gcs_destination: str) -> None:
    """Uploads a local file to a GCS path like gs://bucket/path/to/blob."""
    from google.cloud import storage
    if not gcs_destination.startswith("gs://"):
        raise ValueError("gcs_destination must start with gs://")
    
    path_without_scheme = gcs_destination[5:]
    bucket_name, _, blob_path = path_without_scheme.partition("/")
    
    print(f"Uploading local CSV '{local_file_path}' to GCS destination: '{gcs_destination}' ...")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(local_file_path)
    print("  GCS Upload complete.")

def recreate_gcp_glossary(project_id: str, location: str, glossary_id: str, gcs_uri: str) -> None:
    """Recreates a GCP Translation V3 multi-lingual glossary using an uploaded CSV."""
    from google.cloud import translate_v3
    client = translate_v3.TranslationServiceClient()
    
    glossary_path = client.glossary_path(project_id, location, glossary_id)
    print(f"Updating GCP Translation Glossary resource: '{glossary_path}' ...")
    
    # Glossaries are immutable, so we must delete existing one if it exists
    try:
        print(f"  Checking if glossary '{glossary_id}' already exists...")
        client.get_glossary(name=glossary_path)
        print("  Glossary found. Deleting existing resource to perform update...")
        delete_op = client.delete_glossary(name=glossary_path)
        delete_op.result()
        print("    Existing glossary deleted successfully.")
    except Exception as e:
        print(f"  No existing glossary to delete or check failed (carrying on to creation): {e}")
        pass
        
    parent = f"projects/{project_id}/locations/{location}"
    glossary_config = {
        "name": glossary_path,
        "language_codes_set": {
            "language_codes": ["en", "es", "vi"]
        },
        "input_config": {
            "gcs_source": {
                "input_uri": gcs_uri
            }
        }
    }
    
    print(f"  Registering new glossary '{glossary_id}' in region '{location}' using CSV from '{gcs_uri}'...")
    create_op = client.create_glossary(parent=parent, glossary=glossary_config)
    create_op.result()
    print("  GCP Glossary resource registered successfully.")

def download_from_gcs(gcs_csv_uri: str, local_json_path: str, local_csv_path: str) -> None:
    """Downloads glossary.csv and glossary.json from GCS destination directory.
    
    Given a GCS URI like gs://my-bucket/path/to/glossary.csv, it will download:
    - glossary.csv from gs://my-bucket/path/to/glossary.csv
    - glossary.json from gs://my-bucket/path/to/glossary.json
    """
    if not storage:
        raise ImportError("google-cloud-storage is not installed or available.")
    
    if not gcs_csv_uri.startswith("gs://"):
        raise ValueError("gcs_csv_uri must start with gs://")
        
    path_without_scheme = gcs_csv_uri[5:]
    bucket_name, _, csv_blob_path = path_without_scheme.partition("/")
    
    if csv_blob_path.endswith(".csv"):
        json_blob_path = csv_blob_path[:-4] + ".json"
    else:
        json_blob_path = csv_blob_path + ".json"
        
    print(f"Syncing pre-compiled glossary from GCS bucket '{bucket_name}' ...")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    local_dir = os.path.dirname(local_csv_path)
    if local_dir:
        os.makedirs(local_dir, exist_ok=True)
        
    # Download CSV
    print(f"  Downloading CSV to: {local_csv_path} ...")
    blob_csv = bucket.blob(csv_blob_path)
    blob_csv.download_to_filename(local_csv_path)
    
    # Download JSON
    print(f"  Downloading JSON to: {local_json_path} ...")
    blob_json = bucket.blob(json_blob_path)
    blob_json.download_to_filename(local_json_path)
    
    print("  GCS Synchronization completed successfully.")

def run_pipeline(args) -> None:
    """Executes the full terminology ingestion and GCP Glossary registration pipeline."""
    import json
    import os
    
    if getattr(args, "download_gcs", False):
        download_from_gcs(
            gcs_csv_uri=args.gcs_destination,
            local_json_path=args.glossary_json,
            local_csv_path=args.csv_path
        )
        print("GCS synchronization completed. Exiting pipeline.")
        return
        
    print("=" * 60)
    print("STARTING HEALTHDIRECT TERMINOLOGY IMPORT PIPELINE")
    print("=" * 60)
    
    # 1. Load existing glossary
    existing = {}
    if os.path.exists(args.glossary_json):
        print(f"Loading local glossary database from '{args.glossary_json}'...")
        existing = load_glossary_json(args.glossary_json)
        print(f"  Loaded {len(existing)} existing terminology mappings.")
    else:
        print(f"No existing local database found at '{args.glossary_json}'. Initiating new glossary database.")
        
    # 2. Scrape new terms
    scraped = {}
    if args.scrape:
        print(f"Initiating active crawl on reference site: '{args.scrape}'")
        scraped = scrape_healthdirect_page(
            args.scrape,
            max_letters=args.max_letters,
            delay=getattr(args, "delay", 1.0),
            force=getattr(args, "force", False),
            state_path=getattr(args, "state_file", "glossary/scrape_state.json")
        )
        print(f"  Scraped {len(scraped)} term references from crawl.")
        limit_val = getattr(args, "limit_terms", None)
        if limit_val is not None and limit_val > 0:
            sliced_keys = list(scraped.keys())[:limit_val]
            scraped = {k: scraped[k] for k in sliced_keys}
            print(f"  Limited ingestion to the first {len(scraped)} scraped terms (as requested by -limit).")
    # Ensure parent directories exist early
    os.makedirs(os.path.dirname(os.path.abspath(args.glossary_json)), exist_ok=True)
    os.makedirs("glossary", exist_ok=True)
    
    csv_temp_path = getattr(args, "csv_path", None) or "glossary/glossary.csv"
    
    def save_progress(current_glossary):
        save_glossary_json(current_glossary, args.glossary_json)
        export_to_csv(current_glossary, csv_temp_path)

    # 3. Merge terms
    print("Merging crawled term list into local glossary...")
    merged = merge_glossaries(existing, scraped)
    print(f"  Integrated database contains {len(merged)} distinct term mappings.")
    # Save immediately after merging so we don't lose the crawled URL structure
    save_progress(merged)
    
    # 4. Pre-translate new terms
    project_id = args.project_id or os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
    print("Evaluating bilingual translations...")
    
    languages = None
    if getattr(args, "add_language", None):
        parts = args.add_language.split("=")
        if len(parts) == 2:
            languages = {parts[0].strip(): parts[1].strip()}
            print(f"Adding translation target: {parts[0]} ({parts[1]})")
        else:
            print(f"[ERROR] Invalid format for --add-language: '{args.add_language}'. Expected 'Name=code', e.g. 'German=de'")
            import sys
            sys.exit(1)
            
    updated = pre_translate_terms(merged, project_id=project_id, save_callback=save_progress, languages=languages)
    
    # Optional search grounding and validation step
    if getattr(args, "ground", False):
        print("Executing translation search-grounding and validation...")
        
        # Prioritize newly scraped terms first so they are processed immediately,
        # followed by other historical terms in the database that are missing grounding.
        scraped_terms = sorted(list(scraped.keys())) if scraped else []
        other_terms = []
        for term, data in updated.items():
            if term in scraped_terms:
                continue
            translations = data.get("translations", {})
            has_spanish = bool(translations.get("Spanish"))
            has_vietnamese = bool(translations.get("Vietnamese"))
            missing_es_ground = not data.get("Spanish_grounding_url")
            missing_vi_ground = not data.get("Vietnamese_grounding_url")
            
            if (has_spanish and missing_es_ground) or (has_vietnamese and missing_vi_ground):
                other_terms.append(term)
                
        other_terms.sort()
        terms_to_ground = scraped_terms + other_terms
        print(f"  Grounding queue contains {len(terms_to_ground)} terms (Prioritized: {len(scraped_terms)} newly scraped, {len(other_terms)} outstanding).")
        
        rate_limit_hit = False
        for term in terms_to_ground:
            if rate_limit_hit:
                break
            if term not in updated:
                continue
            data = updated[term]
            translations = data.get("translations", {})
            
            grounded_any = False
            # Spanish Grounding
            spanish_term = translations.get("Spanish")
            if spanish_term:
                if not data.get("Spanish_grounding_url"):
                    print(f"  Grounding Spanish term '{spanish_term}' (English: '{term}')...")
                    try:
                        res = ground_term(term, spanish_term, "es")
                        if res and res.get("url"):
                            data["Spanish_grounding_url"] = res["url"]
                            data["Spanish_grounding_snippet"] = res.get("snippet", "")
                            grounded_any = True
                    except GoogleRateLimitError:
                        print("\n[WARNING] Google Search Rate Limit (429) hit. Aborting search grounding for remaining terms in this run.\n")
                        rate_limit_hit = True
                        break
                else:
                    print(f"  Spanish grounding already exists for '{term}'. Skipping.")
                    
            # Vietnamese Grounding
            if rate_limit_hit:
                break
            vietnamese_term = translations.get("Vietnamese")
            if vietnamese_term:
                if not data.get("Vietnamese_grounding_url"):
                    print(f"  Grounding Vietnamese term '{vietnamese_term}' (English: '{term}')...")
                    try:
                        res = ground_term(term, vietnamese_term, "vi")
                        if res and res.get("url"):
                            data["Vietnamese_grounding_url"] = res["url"]
                            data["Vietnamese_grounding_snippet"] = res.get("snippet", "")
                            grounded_any = True
                    except GoogleRateLimitError:
                        print("\n[WARNING] Google Search Rate Limit (429) hit. Aborting search grounding for remaining terms in this run.\n")
                        rate_limit_hit = True
                        break
                else:
                    print(f"  Vietnamese grounding already exists for '{term}'. Skipping.")
                    
            if grounded_any:
                save_progress(updated)
                    
    # 5. Save updated glossary to JSON & CSV (Final save to ensure everything is written)
    print(f"Persisting updated dictionary database to '{args.glossary_json}' and '{csv_temp_path}'...")
    save_progress(updated)
    print("  Local database and CSV saved.")
    
    # 7. Upload CSV to GCS
    if args.gcs_destination:
        def is_populated(val):
            if isinstance(val, dict):
                return bool(val.get("formal") or val.get("informal"))
            return bool(str(val).strip())

        exported_count = sum(
            1 for term, data in updated.items()
            if term and is_populated(data.get("translations", {}).get("Spanish", "")) and is_populated(data.get("translations", {}).get("Vietnamese", ""))
        )
        if exported_count > 0:
            upload_to_gcs(csv_temp_path, args.gcs_destination)
            
            # Derived JSON destination path in GCS (e.g. glossary.csv -> glossary.json)
            gcs_json_destination = args.gcs_destination.rsplit(".", 1)[0] + ".json"
            upload_to_gcs(args.glossary_json, gcs_json_destination)
            
            # 8. Recreate GCP Translation Glossary resource
            if project_id and args.glossary_id:
                recreate_gcp_glossary(
                    project_id=project_id,
                    location=args.location,
                    glossary_id=args.glossary_id,
                    gcs_uri=args.gcs_destination
                )
        else:
            print("\n[NOTICE] No fully-translated entries to upload. Skipping GCP Glossary resource creation to prevent empty-file failures.\n")
            
    print("=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    import argparse
    import sys
    
    # Handle single-dash options like -scrape, -max, -limit and -ground as standard argparse
    args_to_parse = []
    for arg in sys.argv[1:]:
        if arg == "-scrape":
            args_to_parse.append("--scrape")
        elif arg == "-max":
            args_to_parse.append("--max-letters")
        elif arg == "-limit":
            args_to_parse.append("--limit-terms")
        elif arg == "-ground":
            args_to_parse.append("--ground")
        elif arg == "-delay":
            args_to_parse.append("--delay")
        elif arg == "-force":
            args_to_parse.append("--force")
        elif arg == "-state-file":
            args_to_parse.append("--state-file")
        elif arg == "-add-language" or arg == "-al":
            args_to_parse.append("--add-language")
        else:
            args_to_parse.append(arg)
            
    parser = argparse.ArgumentParser(
        description="HealthDirect Glossary Importer & Scraper Utility",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--scrape", "-s", type=str,
        help=(
            "URL to scrape terms from. Supported HealthDirect sources include:\n"
            "  - Medicines: https://www.healthdirect.gov.au/medicines\n"
            "  - Conditions: https://www.healthdirect.gov.au/health-topics/conditions\n"
            "  - Symptoms: https://www.healthdirect.gov.au/health-topics/symptoms\n"
            "  - Procedures: https://www.healthdirect.gov.au/health-topics/procedures"
        )
    )
    parser.add_argument("--max-letters", "-m", type=int, default=None, help="Maximum alphabetical letters to crawl")
    parser.add_argument("--limit-terms", "-l", type=int, default=None, help="Limit number of scraped terms to process")
    parser.add_argument("--glossary-json", default="glossary/glossary.json", help="Path to local glossary.json")
    parser.add_argument("--csv-path", default="glossary/glossary.csv", help="Path to local glossary.csv")
    parser.add_argument("--gcs-destination", default="gs://uk-bh-experiments-argolis-us/HealthDirect/glossaries/glossary.csv", help="GCS destination URI")
    parser.add_argument("--download-gcs", action="store_true", help="Download pre-compiled glossary JSON and CSV from GCS and exit")
    parser.add_argument("--glossary-id", default="healthdirect_glossary", help="GCP Translation glossary ID")
    parser.add_argument("--location", default="us-central1", help="GCP Location")
    parser.add_argument("--project-id", help="GCP Project ID")
    parser.add_argument("--ground", "-g", action="store_true", help="Perform automated Google Search grounding to verify and provide context for translated terms")
    parser.add_argument("--delay", "-d", type=float, default=1.0, help="Politeness delay in seconds between HTTP requests (default: 1.0)")
    parser.add_argument("--force", "-f", action="store_true", help="Ignore scrape_state.json cache and force scraping of all URLs")
    parser.add_argument("--state-file", default="glossary/scrape_state.json", help="Path to local scrape state JSON cache file")
    parser.add_argument("--add-language", "-al", type=str, default=None, help="Add and translate existing terms to a new language (Format: Name=code, e.g. German=de) without re-scraping")
    
    parsed_args = parser.parse_args(args_to_parse)
    
    run_pipeline(parsed_args)
