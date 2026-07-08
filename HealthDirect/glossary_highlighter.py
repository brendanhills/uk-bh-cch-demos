import os
import json
import re

class GlossaryHighlighter:
    def __init__(self, glossary_path: str = "glossary/glossary.json"):
        self.glossary_entries = []
        
        # Resolve path robustly
        if not os.path.exists(glossary_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            fallback_path = os.path.join(base_dir, "glossary/glossary.json")
            if os.path.exists(fallback_path):
                glossary_path = fallback_path
                
        if os.path.exists(glossary_path):
            try:
                with open(glossary_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.glossary_entries = data.get("glossary", [])
            except Exception:
                # Silently handle JSON load errors or keep empty
                self.glossary_entries = []

    def highlight_cli(self, text: str, language: str) -> str:
        if not text or not self.glossary_entries:
            return text
            
        # Highlight English terms
        if language.lower() == "english":
            english_terms = [entry["english"] for entry in self.glossary_entries if entry.get("english")]
            if english_terms:
                pattern = self._compile_pattern(english_terms)
                text = pattern.sub(lambda m: f"\x1b[1;32m{m.group(0)}\x1b[0m", text)
        else:
            # Highlight target foreign language terms
            target_terms = []
            for entry in self.glossary_entries:
                translations = entry.get("translations", {})
                for lang_key, trans_val in translations.items():
                    if lang_key.lower() == language.lower() and trans_val:
                        # Split by comma or semicolon to support multiple synonyms
                        parts = [t.strip() for t in re.split(r'[,;]+', trans_val) if t.strip()]
                        target_terms.extend(parts)
            if target_terms:
                pattern = self._compile_pattern(target_terms)
                text = pattern.sub(lambda m: f"\x1b[1;35m{m.group(0)}\x1b[0m", text)
                
        return text

    def _compile_pattern(self, terms: list[str]) -> re.Pattern:
        # Sort terms by length in descending order to match longer phrases first
        sorted_terms = sorted(list(set(terms)), key=len, reverse=True)
        
        patterns = []
        for t in sorted_terms:
            if not t.strip():
                continue
            words = t.split()
            if len(words) > 1:
                # Allow 0 to 2 intermediate words in between each word of a multi-word phrase
                pattern = r"\s+(?:\w+\s+){0,2}?".join(re.escape(w) for w in words)
            else:
                pattern = re.escape(t)
            patterns.append(pattern)
            
        # Compile case-insensitive regex using word boundaries \b
        pattern_str = r"\b(" + "|".join(patterns) + r")\b"
        return re.compile(pattern_str, re.IGNORECASE)

