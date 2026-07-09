/* ==========================================================================
   STATE MANAGEMENT & UI INITIALIZATION
   ========================================================================== */
let socket = null;
let audioCtx = null;
let glossaryTerms = [];
let glossarySearchQuery = "";
let glossaryActiveFilter = "all";
let encounteredTerms = new Set();

// Gain and Panner Nodes for Foreign and English channels (Immersive Stereo separation)
let gainForeign = null;
let gainEnglish = null;
let pannerForeign = null;
let pannerEnglish = null;

// Playback playhead times (seconds) to schedule contiguous gapless chunks
let patientOriginalPlayhead = 0;
let nurseOriginalPlayhead = 0;
let patientTranslatedPlayhead = 0;
let nurseTranslatedPlayhead = 0;

// Track active chat bubbles for updating text dynamically in real-time
let currentNurseBubble = null;
let currentPatientBubble = null;

// Track whether the current speech turn is completed to start a new bubble on next speech
let nurseTurnFinished = false;
let patientTurnFinished = false;
let lastOriginalSpeaker = null;
let shouldStartNewBubble = false;

// Preset Metadata for UI refinement
const PRESET_UI_METADATA = {
    "german": {
        name: "Herr Müller",
        lang: "German (DE)",
        shortLang: "German",
        avatar: "👴"
    },
    "spanish": {
        name: "Señor Gomez",
        lang: "Spanish (ES)",
        shortLang: "Spanish",
        avatar: "🧔"
    },
    "vietnamese": {
        name: "Mrs. Nguyen",
        lang: "Vietnamese (VI)",
        shortLang: "Vietnamese",
        avatar: "👵"
    },
    "arabic": {
        name: "Ahmad",
        lang: "Arabic (AR)",
        shortLang: "Arabic",
        avatar: "🧔"
    }
};

// UI Elements
const presetSelector = document.getElementById("preset-selector");
const modelSelector = document.getElementById("model-selector");
const modelBadge = document.getElementById("model-badge");
// Pacing Sliders UI Elements
const pacingTurnTimeout = document.getElementById("pacing-turn-timeout");
const pacingCeasedAudio = document.getElementById("pacing-ceased-audio");
const pacingStartupAudio = document.getElementById("pacing-startup-audio");
const pacingAdditionalPause = document.getElementById("pacing-additional-pause");

const valTurnTimeout = document.getElementById("val-turn-timeout");
const valCeasedAudio = document.getElementById("val-ceased-audio");
const valStartupAudio = document.getElementById("val-startup-audio");
const valAdditionalPause = document.getElementById("val-additional-pause");

const startBtn = document.getElementById("start-btn");
const pauseBtn = document.getElementById("pause-btn");
const endBtn = document.getElementById("end-btn");
const resetBtn = document.getElementById("reset-btn");
const headerPulse = document.getElementById("header-pulse");

let isCallPaused = false;
const connectionText = document.getElementById("connection-text");
const chatFeed = document.getElementById("chat-feed");
const welcomeMessage = document.getElementById("welcome-message");
const crossFader = document.getElementById("cross-fader");

const nurseCard = document.getElementById("nurse-card");
const nurseStatus = document.getElementById("nurse-status");

const patientCard = document.getElementById("patient-card");
const patientName = document.getElementById("patient-name");
const patientLang = document.getElementById("patient-lang");
const patientStatus = document.getElementById("patient-status");
const patientAvatar = document.querySelector(".patient-avatar");

// Dynamic Audio Mixer Labels
const sliderLangLeft = document.getElementById("slider-lang-left");
const sliderLangRight = document.getElementById("slider-lang-right");
const tickLeft = document.getElementById("tick-left");
const tickRight = document.getElementById("tick-right");

// Clinical Glossary Sidebar Elements
const reloadGlossaryBtn = document.getElementById("reload-glossary-btn");
const glossarySearchInput = document.getElementById("glossary-search");
const clearSearchBtn = document.getElementById("clear-search-btn");
const filterChips = document.querySelectorAll(".filter-chip");

/* ==========================================================================
   CLINICAL GLOSSARY INTEGRATION
   ========================================================================== */
function formatSnippet(text) {
    if (!text) return "";
    // Escape HTML to prevent XSS
    let escaped = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
        
    // Bold: **text**
    escaped = escaped.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    
    // Links: [text](url)
    escaped = escaped.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="snippet-inline-link">$1</a>');
    
    return escaped;
}

function getTermUrl(entry, targetLang) {
    if (!entry) return "";
    
    // 1. Language-specific grounding URL
    const urlKey = `${targetLang}_grounding_url`;
    if (entry[urlKey]) {
        return entry[urlKey];
    }
    
    // 2. Generic global URL
    if (entry.url) {
        return entry.url;
    }
    
    // 3. Constructed search fallback
    return `https://www.healthdirect.gov.au/search-results?q=${encodeURIComponent(entry.english)}`;
}

function addEncounteredTerm(entry, targetLang) {
    const termKey = entry.english;
    if (!termKey) return;
    
    if (!encounteredTerms.has(termKey)) {
        encounteredTerms.add(termKey);
        renderEncounteredReferences(targetLang);
    }
}

function renderEncounteredReferences(targetLang) {
    const listDiv = document.getElementById("references-list");
    const countBadge = document.getElementById("references-count");
    if (!listDiv) return;
    
    listDiv.innerHTML = "";
    
    const count = encounteredTerms.size;
    if (countBadge) {
        countBadge.innerText = `${count} Link${count === 1 ? "" : "s"}`;
    }
    
    if (count === 0) {
        listDiv.innerHTML = '<div class="references-empty">No clinical terms encountered in this conversation yet.</div>';
        return;
    }
    
    // Sort encountered terms alphabetically
    const sortedTerms = Array.from(encounteredTerms).sort();
    
    sortedTerms.forEach(termKey => {
        const entry = glossaryTerms.find(e => e.english === termKey);
        if (!entry) return;
        
        const groundingUrl = getTermUrl(entry, targetLang);
        if (!groundingUrl) return;
        
        const trans = entry.translations || {};
        const transKey = Object.keys(trans).find(k => k.toLowerCase() === targetLang.toLowerCase());
        const translationVal = transKey ? trans[transKey] : "";
        
        const pillAnchor = document.createElement("a");
        pillAnchor.className = "reference-pill";
        pillAnchor.href = groundingUrl;
        pillAnchor.target = "_blank";
        pillAnchor.rel = "noopener noreferrer";
        
        if (translationVal) {
            pillAnchor.innerText = `${entry.english} (${translationVal}) 🔗`;
        } else {
            pillAnchor.innerText = `${entry.english} 🔗`;
        }
        
        listDiv.appendChild(pillAnchor);
    });
}

async function fetchGlossary() {
    const preset = presetSelector.value;
    const meta = PRESET_UI_METADATA[preset];
    if (!meta) return;
    
    try {
        const response = await fetch(`/api/glossary?language=${meta.shortLang}&_=${Date.now()}`);
        if (response.ok) {
            const data = await response.json();
            glossaryTerms = data.glossary || [];
            console.log(`[Glossary] Loaded ${glossaryTerms.length} terms for ${meta.shortLang}`);
        } else {
            console.error(`[Glossary] Failed to fetch glossary: ${response.statusText}`);
            glossaryTerms = [];
        }
    } catch (err) {
        console.error("[Glossary] Error fetching glossary:", err);
        glossaryTerms = [];
    }
    renderGlossaryList();
}

function escapeHTML(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function highlightText(text, query) {
    const escaped = escapeHTML(text);
    if (!query) return escaped;
    const escapedQuery = escapeRegExp(query);
    const regex = new RegExp(`(${escapedQuery})`, "gi");
    return escaped.replace(regex, "<span class='search-highlight'>$1</span>");
}

function getTranslationString(val) {
    if (!val) return "";
    if (Array.isArray(val)) {
        return val.map(item => getTranslationString(item)).filter(Boolean).join(", ");
    }
    if (typeof val === "object") {
        const parts = [];
        if (val.formal) parts.push(getTranslationString(val.formal));
        if (val.informal) {
            if (Array.isArray(val.informal)) {
                parts.push(...val.informal.map(item => getTranslationString(item)));
            } else {
                parts.push(getTranslationString(val.informal));
            }
        }
        const filteredParts = parts.map(p => p.trim()).filter(Boolean);
        if (filteredParts.length === 0) {
            // Fallback for other dictionary shapes
            return Object.values(val).map(v => getTranslationString(v)).filter(Boolean).join(", ");
        }
        return filteredParts.join(", ");
    }
    return String(val).trim();
}

function renderGlossaryList() {
    const listDiv = document.getElementById("glossary-list");
    const countBadge = document.getElementById("glossary-count");
    if (!listDiv) return;
    
    listDiv.innerHTML = "";
    
    // Toggle clear search button visibility
    if (clearSearchBtn) {
        clearSearchBtn.style.display = glossarySearchQuery ? "flex" : "none";
    }
    
    const preset = presetSelector.value;
    const meta = PRESET_UI_METADATA[preset];
    const targetLang = meta ? meta.shortLang : "";
    
    // Filter glossary terms based on active filter and search query
    const queryLower = glossarySearchQuery.toLowerCase();
    const filteredTerms = glossaryTerms.filter(entry => {
        const trans = entry.translations || {};
        const transKey = Object.keys(trans).find(k => k.toLowerCase() === targetLang.toLowerCase());
        const translationVal = transKey ? getTranslationString(trans[transKey]) : "";
        
        // 1. Filter by Active Category Chip
        const urlKey = `${targetLang}_grounding_url`;
        if (glossaryActiveFilter === "verified" && !entry[urlKey]) {
            return false;
        }
        if (glossaryActiveFilter === "desc" && !entry.description) {
            return false;
        }
        
        // 2. Filter by Search Query (matches English, Translation, or Description)
        if (queryLower) {
            const matchEnglish = (entry.english || "").toLowerCase().includes(queryLower);
            const matchTranslation = translationVal.toLowerCase().includes(queryLower);
            const matchDescription = (entry.description || "").toLowerCase().includes(queryLower);
            
            if (!matchEnglish && !matchTranslation && !matchDescription) {
                return false;
            }
        }
        
        return true;
    });
    
    // Update badge count with "X of Y" if search/filter is active
    if (countBadge) {
        if (glossarySearchQuery || glossaryActiveFilter !== "all") {
            countBadge.innerText = `${filteredTerms.length} of ${glossaryTerms.length} Term${glossaryTerms.length === 1 ? "" : "s"}`;
        } else {
            countBadge.innerText = `${glossaryTerms.length} Term${glossaryTerms.length === 1 ? "" : "s"}`;
        }
    }
    
    if (filteredTerms.length === 0) {
        if (glossarySearchQuery || glossaryActiveFilter !== "all") {
            listDiv.innerHTML = '<div class="glossary-empty">No matching terms found.</div>';
        } else {
            listDiv.innerHTML = '<div class="glossary-empty">No glossary terms loaded.</div>';
        }
        return;
    }
    
    // Sort filtered terms alphabetically by their English term
    filteredTerms.sort((a, b) => (a.english || "").localeCompare(b.english || ""));
    
    filteredTerms.forEach(entry => {
        const itemDiv = document.createElement("div");
        itemDiv.className = "glossary-item";
        
        const trans = entry.translations || {};
        const transKey = Object.keys(trans).find(k => k.toLowerCase() === targetLang.toLowerCase());
        const translationVal = transKey ? getTranslationString(trans[transKey]) : "";
        
        const termRow = document.createElement("div");
        termRow.className = "item-term-row";
        
        const englishSpan = document.createElement("span");
        englishSpan.className = "item-english";
        englishSpan.innerHTML = highlightText(entry.english, glossarySearchQuery);
        termRow.appendChild(englishSpan);
        
        if (translationVal) {
            const transSpan = document.createElement("span");
            transSpan.className = "item-translation";
            transSpan.innerHTML = highlightText(translationVal, glossarySearchQuery);
            termRow.appendChild(transSpan);
        }
        
        itemDiv.appendChild(termRow);
        
        if (entry.description) {
            const descDiv = document.createElement("div");
            descDiv.className = "item-desc";
            descDiv.innerHTML = highlightText(entry.description, glossarySearchQuery);
            itemDiv.appendChild(descDiv);
        }
        
        // Add clinical grounding source if present
        const groundingUrl = getTermUrl(entry, targetLang);
        const snippetKey = `${targetLang}_grounding_snippet`;
        const groundingSnippet = entry[snippetKey];
        
        if (groundingUrl) {
            const groundingDiv = document.createElement("div");
            groundingDiv.className = "item-grounding";
            
            const labelSpan = document.createElement("span");
            labelSpan.className = "grounding-label";
            labelSpan.innerText = "Medical Reference Source: ";
            groundingDiv.appendChild(labelSpan);
            
            const linkAnchor = document.createElement("a");
            linkAnchor.className = "grounding-link";
            linkAnchor.href = groundingUrl;
            linkAnchor.target = "_blank";
            linkAnchor.rel = "noopener noreferrer";
            linkAnchor.innerText = "Verified Source 🔗";
            groundingDiv.appendChild(linkAnchor);
            
            if (groundingSnippet) {
                const snippetDiv = document.createElement("div");
                snippetDiv.className = "grounding-snippet";
                snippetDiv.innerHTML = formatSnippet(groundingSnippet);
                groundingDiv.appendChild(snippetDiv);
            }
            
            itemDiv.appendChild(groundingDiv);
        }
        
        listDiv.appendChild(itemDiv);
    });
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function applyHTMLHighlight(text, matchLanguage, targetLang) {
    if (!text || !glossaryTerms || glossaryTerms.length === 0) return text;
    
    const termsWithPatterns = [];
    
    glossaryTerms.forEach(entry => {
        let termVal = "";
        if (matchLanguage.toLowerCase() === "english") {
            termVal = entry.english;
        } else {
            const trans = entry.translations || {};
            const key = Object.keys(trans).find(k => k.toLowerCase() === matchLanguage.toLowerCase());
            if (key) {
                termVal = getTranslationString(trans[key]);
            }
        }
        
        if (termVal && termVal.trim()) {
            // Split by comma or semicolon to support multiple synonyms
            const synonyms = termVal.split(/[,;]+/).map(s => s.trim()).filter(Boolean);
            synonyms.forEach(syn => {
                const words = syn.split(/\s+/);
                let patternStr;
                if (words.length > 1) {
                    // Allow up to 2 intermediate words in between each word of a multi-word phrase
                    patternStr = words.map(w => escapeRegExp(w)).join("\\s+(?:\\p{L}+\\s+){0,2}?");
                } else {
                    patternStr = escapeRegExp(syn);
                }
                const termRegex = new RegExp("^(?:" + patternStr + ")$", "ui");
                termsWithPatterns.push({
                    canonical: syn,
                    patternStr: patternStr,
                    regex: termRegex,
                    entry: entry
                });
            });
        }
    });
    
    if (termsWithPatterns.length === 0) return text;
    
    // Sort descending by canonical term length to ensure longer compound matches are tried first in the alternation
    termsWithPatterns.sort((a, b) => b.canonical.length - a.canonical.length);
    
    const overallPatternStr = "(?<!\\p{L})(" + termsWithPatterns.map(item => item.patternStr).join("|") + ")(?!\\p{L})";
    const regex = new RegExp(overallPatternStr, "gui");
    
    return text.replace(regex, (matched) => {
        // Find which entry matched by testing each item's pattern against the matched string
        const matchItem = termsWithPatterns.find(item => item.regex.test(matched));
        if (matchItem) {
            const entry = matchItem.entry;
            const englishTerm = entry.english || "";
            const translations = entry.translations || {};
            const transKey = Object.keys(translations).find(k => k.toLowerCase() === targetLang.toLowerCase());
            const translationVal = transKey ? getTranslationString(translations[transKey]) : "";
            const desc = entry.description || "";
            
            logger(`[UI Event] [Glossary Match] Matched term: "${matched}" -> English: "${englishTerm}"${translationVal ? ` (Translation: "${translationVal}")` : ""}`);
            
            // Track as encountered term
            addEncounteredTerm(entry, targetLang);
            
            let tooltipText = "";
            if (translationVal) {
                tooltipText = `${englishTerm} (${translationVal}): ${desc}`;
            } else {
                tooltipText = `${englishTerm}: ${desc}`;
            }
            
            const escapedTooltip = tooltipText.replace(/"/g, "&quot;");
            return `<mark class="glossary-highlight" data-tooltip="${escapedTooltip}">${matched}</mark>`;
        }
        return matched;
    });
}

function highlightGlossaryTerms(bubble, speaker) {
    if (!bubble || !glossaryTerms || glossaryTerms.length === 0) return;
    
    const bodyDiv = bubble.querySelector(".bubble-body");
    if (!bodyDiv) return;
    
    const origSpan = bodyDiv.querySelector(".original-text");
    const transSpan = bodyDiv.querySelector(".translation-text");
    
    const preset = presetSelector.value;
    const meta = PRESET_UI_METADATA[preset];
    if (!meta) return;
    
    const targetLang = meta.shortLang;
    
    if (speaker === "nurse") {
        if (origSpan) {
            const rawText = origSpan.getAttribute("data-raw") || origSpan.innerText;
            origSpan.innerHTML = applyHTMLHighlight(rawText, "english", targetLang);
        }
        if (transSpan) {
            const rawText = transSpan.getAttribute("data-raw") || transSpan.innerText;
            transSpan.innerHTML = applyHTMLHighlight(rawText, targetLang, targetLang);
        }
    } else {
        if (origSpan) {
            const rawText = origSpan.getAttribute("data-raw") || origSpan.innerText;
            origSpan.innerHTML = applyHTMLHighlight(rawText, targetLang, targetLang);
        }
        if (transSpan) {
            const rawText = transSpan.getAttribute("data-raw") || transSpan.innerText;
            transSpan.innerHTML = applyHTMLHighlight(rawText, "english", targetLang);
        }
    }
}

/* ==========================================================================
   PRESET CHANGE LISTENER
   ========================================================================== */
function updatePresetUI() {
    const preset = presetSelector.value;
    const meta = PRESET_UI_METADATA[preset];
    if (meta) {
        patientName.innerText = meta.name;
        patientLang.innerText = meta.lang;
        patientAvatar.innerText = meta.avatar;
        
        // Update slider labels and ticks dynamically
        if (sliderLangLeft) sliderLangLeft.innerText = meta.lang;
        if (sliderLangRight) sliderLangRight.innerText = "English (EN)";
        if (tickLeft) tickLeft.innerText = `100% ${meta.shortLang}`;
        if (tickRight) tickRight.innerText = "100% English";
        
        // Fetch glossary terms for selected preset language
        fetchGlossary();
        
        // Reset encountered references for the new preset
        encounteredTerms.clear();
        renderEncounteredReferences(meta.shortLang);
        
        // Reset glossary search & filter states on scenario/preset change
        glossarySearchQuery = "";
        glossaryActiveFilter = "all";
        if (glossarySearchInput) {
            glossarySearchInput.value = "";
        }
        if (filterChips) {
            filterChips.forEach(chip => {
                if (chip.getAttribute("data-filter") === "all") {
                    chip.classList.add("active");
                } else {
                    chip.classList.remove("active");
                }
            });
        }
    }
}

function updateModelBadge() {
    if (modelSelector && modelBadge) {
        if (modelSelector.value === "gemini-3.5-live-translate-preview") {
            modelBadge.innerText = "Gemini 3.5 Live Translate";
            modelBadge.style.backgroundColor = "var(--border-color)";
        } else {
            modelBadge.innerText = "Gemini 3.1 Flash Live + Glossary";
            modelBadge.style.backgroundColor = "rgba(37, 99, 235, 0.2)"; // Premium highlight for glossary mode
        }
    }
}

presetSelector.addEventListener("change", updatePresetUI);
if (modelSelector) {
    modelSelector.addEventListener("change", updateModelBadge);
}

if (reloadGlossaryBtn) {
    reloadGlossaryBtn.addEventListener("click", async () => {
        reloadGlossaryBtn.classList.add("spinning");
        try {
            await fetchGlossary();
        } finally {
            // Keep spinning for at least 500ms to make the animation satisfyingly premium
            setTimeout(() => {
                reloadGlossaryBtn.classList.remove("spinning");
            }, 500);
        }
    });
}

// Search input listener (real-time instant filtering)
if (glossarySearchInput) {
    glossarySearchInput.addEventListener("input", (e) => {
        glossarySearchQuery = e.target.value.trim();
        renderGlossaryList();
    });
}

// Clear search button listener
if (clearSearchBtn) {
    clearSearchBtn.addEventListener("click", () => {
        if (glossarySearchInput) {
            glossarySearchInput.value = "";
            glossarySearchInput.focus();
        }
        glossarySearchQuery = "";
        renderGlossaryList();
    });
}

// Filter chips listener
if (filterChips) {
    filterChips.forEach(chip => {
        chip.addEventListener("click", () => {
            // Remove active class from all chips
            filterChips.forEach(c => c.classList.remove("active"));
            // Add active class to clicked chip
            chip.classList.add("active");
            // Set active filter state
            glossaryActiveFilter = chip.getAttribute("data-filter") || "all";
            // Re-render
            renderGlossaryList();
        });
    });
}

// Parse URL query parameters for easier automated testing and presets
const urlParams = new URLSearchParams(window.location.search);
const queryPreset = urlParams.get("preset");
const queryModel = urlParams.get("model");
const queryAutostart = urlParams.get("autostart");

if (queryPreset && presetSelector) {
    const validPresets = ["german", "spanish", "vietnamese", "arabic"];
    const normalized = queryPreset.toLowerCase();
    if (validPresets.includes(normalized)) {
        presetSelector.value = normalized;
        console.log(`[URL Params] Auto-selected preset: ${normalized}`);
    }
}

if (queryModel && modelSelector) {
    const validModels = ["gemini-3.5-live-translate-preview", "gemini-3.1-flash-live-preview"];
    const normalized = queryModel.toLowerCase();
    if (validModels.includes(normalized)) {
        modelSelector.value = normalized;
        console.log(`[URL Params] Auto-selected model: ${normalized}`);
    }
}

// Initialize on page load
updatePresetUI();
updateModelBadge();
fetchPacingConfig();
initPacingSliderListeners();

// Auto-start session if autostart parameter is set
if (queryAutostart === "true") {
    console.log("[URL Params] Detected autostart=true. Scheduling automatic call start...");
    // Slight delay to ensure glossary and configurations are fully loaded
    setTimeout(() => {
        if (startBtn && !startBtn.disabled) {
            console.log("[URL Params] Triggering click on start-btn.");
            startBtn.click();
        }
    }, 1200);
}

/* ==========================================================================
   PACING CONFIGURATION INTEGRATION
   ========================================================================== */
async function fetchPacingConfig() {
    try {
        const response = await fetch("/api/pacing-config");
        if (response.ok) {
            const config = await response.json();
            console.log("[Pacing Config] Loaded defaults from server:", config);
            
            if (pacingTurnTimeout && config.turn_timeout_sec !== undefined) {
                pacingTurnTimeout.value = config.turn_timeout_sec;
                valTurnTimeout.innerText = `${parseFloat(config.turn_timeout_sec).toFixed(1)}s`;
            }
            if (pacingCeasedAudio && config.ceased_audio_threshold !== undefined) {
                pacingCeasedAudio.value = config.ceased_audio_threshold;
                valCeasedAudio.innerText = `${parseFloat(config.ceased_audio_threshold).toFixed(1)}s`;
            }
            if (pacingStartupAudio && config.startup_audio_threshold !== undefined) {
                pacingStartupAudio.value = config.startup_audio_threshold;
                valStartupAudio.innerText = `${parseFloat(config.startup_audio_threshold).toFixed(1)}s`;
            }
            if (pacingAdditionalPause && config.additional_pause_sec !== undefined) {
                pacingAdditionalPause.value = config.additional_pause_sec;
                valAdditionalPause.innerText = `${parseFloat(config.additional_pause_sec).toFixed(1)}s`;
            }
        } else {
            console.error("[Pacing Config] Failed to fetch pacing config:", response.statusText);
        }
    } catch (err) {
        console.error("[Pacing Config] Error fetching pacing config:", err);
    }
}

function initPacingSliderListeners() {
    if (pacingTurnTimeout) {
        pacingTurnTimeout.addEventListener("input", (e) => {
            valTurnTimeout.innerText = `${parseFloat(e.target.value).toFixed(1)}s`;
        });
    }
    if (pacingCeasedAudio) {
        pacingCeasedAudio.addEventListener("input", (e) => {
            valCeasedAudio.innerText = `${parseFloat(e.target.value).toFixed(1)}s`;
        });
    }
    if (pacingStartupAudio) {
        pacingStartupAudio.addEventListener("input", (e) => {
            valStartupAudio.innerText = `${parseFloat(e.target.value).toFixed(1)}s`;
        });
    }
    if (pacingAdditionalPause) {
        pacingAdditionalPause.addEventListener("input", (e) => {
            valAdditionalPause.innerText = `${parseFloat(e.target.value).toFixed(1)}s`;
        });
    }
}

/* ==========================================================================
   AUDIO CONTEXT & GAIN CONTROLS
   ========================================================================== */
function initAudio() {
    if (audioCtx) return;
    
    // Create modern standard AudioContext
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    audioCtx = new AudioContextClass();
    
    // Create gain nodes for mixing
    gainForeign = audioCtx.createGain();
    gainEnglish = audioCtx.createGain();
    
    // Create stereo panner nodes for spatial separation (Foreign in Left, English in Right)
    try {
        pannerForeign = audioCtx.createStereoPanner();
        pannerForeign.pan.value = -1.0; // 100% Left
        
        pannerEnglish = audioCtx.createStereoPanner();
        pannerEnglish.pan.value = 1.0; // 100% Right
        
        // Connect Gains to Panners, and Panners to Destination
        gainForeign.connect(pannerForeign);
        pannerForeign.connect(audioCtx.destination);
        
        gainEnglish.connect(pannerEnglish);
        pannerEnglish.connect(audioCtx.destination);
    } catch (e) {
        console.warn("[Interpreter Client] StereoPannerNode not supported or failed. Falling back to standard mono/stereo routing.", e);
        // Fallback without panning if StereoPanner is not available
        gainForeign.connect(audioCtx.destination);
        gainEnglish.connect(audioCtx.destination);
    }
    
    // Set initial volumes based on the slider value
    updateMixerVolumes();
}

function updateMixerVolumes() {
    if (!gainForeign || !gainEnglish) return;
    
    const value = parseInt(crossFader.value);
    let volForeign = 1.0;
    let volEnglish = 1.0;
    
    // Equal mix at 50, fade foreign language above 50, fade English below 50
    if (value <= 50) {
        volForeign = 1.0;
        volEnglish = value / 50.0;
    } else {
        volForeign = (100 - value) / 50.0;
        volEnglish = 1.0;
    }
    
    // Apply gain changes immediately or ramp over a small window
    gainForeign.gain.setTargetAtTime(volForeign, audioCtx.currentTime, 0.01);
    gainEnglish.gain.setTargetAtTime(volEnglish, audioCtx.currentTime, 0.01);
}

crossFader.addEventListener("input", updateMixerVolumes);

/* ==========================================================================
   PCM DECODING & GAPLESS PLAYBACK
   ========================================================================== */
function base64ToArrayBuffer(base64) {
    const binaryString = window.atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
}

function decodePCM(base64Data, sampleRate) {
    try {
        if (!base64Data) return null;
        const arrayBuffer = base64ToArrayBuffer(base64Data);
        const byteLength = arrayBuffer.byteLength;
        if (byteLength < 2) return null;
        
        const alignedLength = byteLength - (byteLength % 2);
        const slicedBuffer = arrayBuffer.slice(0, alignedLength);
        const int16Array = new Int16Array(slicedBuffer);
        if (int16Array.length === 0) return null;
        
        const float32Array = new Float32Array(int16Array.length);
        
        // Convert 16-bit Int16 signed to 32-bit Float32 float [-1.0, 1.0]
        for (let i = 0; i < int16Array.length; i++) {
            float32Array[i] = int16Array[i] / 32768.0;
        }
        
        const buffer = audioCtx.createBuffer(1, float32Array.length, sampleRate);
        buffer.copyToChannel(float32Array, 0);
        return buffer;
    } catch (e) {
        console.error("[Interpreter Client] Error decoding PCM audio payload:", e);
        return null;
    }
}

function schedulePlayback(buffer, streamType, speakerOrStream) {
    if (!audioCtx || !buffer) return;
    
    // Resume context if suspended (browser security policy)
    if (audioCtx.state === "suspended") {
        audioCtx.resume();
    }
    
    const source = audioCtx.createBufferSource();
    source.buffer = buffer;
    
    const now = audioCtx.currentTime;
    
    // Safety buffer configuration: only snap the playhead to "now" 
    // if it has fallen significantly behind (e.g. after a hold pause).
    // This allows contiguous stitching for minor network jitters and accounts for the 200ms chunk size.
    const JITTER_THRESHOLD = 0.35;      // 350ms safety window (must be > 200ms chunk duration)
    const RESUME_LATENCY_BUFFER = 0.05;  // 50ms scheduling headroom to prevent clicks/cuts
    
    if (streamType === "original") {
        if (speakerOrStream === "patient") {
            // Patient Original (Foreign/Native Language) -> LEFT channel (gainForeign)
            if (patientOriginalPlayhead < now - JITTER_THRESHOLD) {
                patientOriginalPlayhead = now + RESUME_LATENCY_BUFFER;
            }
            source.connect(gainForeign);
            source.start(patientOriginalPlayhead);
            patientOriginalPlayhead += buffer.duration;
        } else {
            // Nurse Original (English) -> RIGHT channel (gainEnglish)
            if (nurseOriginalPlayhead < now - JITTER_THRESHOLD) {
                nurseOriginalPlayhead = now + RESUME_LATENCY_BUFFER;
            }
            source.connect(gainEnglish);
            source.start(nurseOriginalPlayhead);
            nurseOriginalPlayhead += buffer.duration;
        }
    } else {
        if (speakerOrStream === "p_to_n") {
            // Patient Translated (English) -> RIGHT channel (gainEnglish)
            if (patientTranslatedPlayhead < now - JITTER_THRESHOLD) {
                patientTranslatedPlayhead = now + RESUME_LATENCY_BUFFER;
            }
            source.connect(gainEnglish);
            source.start(patientTranslatedPlayhead);
            patientTranslatedPlayhead += buffer.duration;
        } else {
            // Nurse Translated (Foreign/Native Language) -> LEFT channel (gainForeign)
            if (nurseTranslatedPlayhead < now - JITTER_THRESHOLD) {
                nurseTranslatedPlayhead = now + RESUME_LATENCY_BUFFER;
            }
            source.connect(gainForeign);
            source.start(nurseTranslatedPlayhead);
            nurseTranslatedPlayhead += buffer.duration;
        }
    }
}

/* ==========================================================================
   TRANSCRIPT & BUBBLES UI LOGIC
   ========================================================================== */
function createSpeechBubble(speaker) {
    logger(`[UI Event] [Speech Bubble] Creating new speech bubble for speaker: "${speaker}"`);
    // Stop pulsing ellipses of previous bubbles of this speaker
    const targetTurnClass = speaker === "nurse" ? "nurse-turn" : "patient-turn";
    const existingTurns = chatFeed.querySelectorAll(`.${targetTurnClass}`);
    existingTurns.forEach(turn => {
        const interimSpan = turn.querySelector(".original-text.interim");
        if (interimSpan) {
            interimSpan.classList.remove("interim");
        }
    });

    const turnDiv = document.createElement("div");
    turnDiv.classList.add("chat-turn");
    
    const isNurse = (speaker === "nurse");
    turnDiv.classList.add(isNurse ? "nurse-turn" : "patient-turn");
    
    // Timestamp meta
    const metaDiv = document.createElement("div");
    metaDiv.classList.add("bubble-meta");
    const nameLabel = isNurse ? "Nurse Sarah" : (PRESET_UI_METADATA[presetSelector.value]?.name || "Patient");
    const timeLabel = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    metaDiv.innerHTML = `<strong>${nameLabel}</strong> <span>${timeLabel}</span>`;
    turnDiv.appendChild(metaDiv);
    
    // Bubble body
    const bodyDiv = document.createElement("div");
    bodyDiv.classList.add("bubble-body");
    
    // Original text segment
    const originalSpan = document.createElement("div");
    originalSpan.classList.add("original-text", "interim");
    if (!isNurse && presetSelector.value === "arabic") {
        originalSpan.classList.add("rtl-text");
    }
    originalSpan.innerText = "";
    bodyDiv.appendChild(originalSpan);
    
    turnDiv.appendChild(bodyDiv);
    chatFeed.appendChild(turnDiv);
    
    // Scroll to bottom smoothly
    chatFeed.scrollTop = chatFeed.scrollHeight;
    
    return turnDiv;
}

function updateSpeechText(speaker, eventType, text, isFinal) {
    // If it's a translation event, map it back to the speaker of the original speech.
    // The server sends the English translation of the Patient with speaker="nurse", 
    // and the target language translation of the Nurse with speaker="patient".
    let bubbleSpeaker = speaker;
    if (eventType === "translation") {
        bubbleSpeaker = (speaker === "nurse" ? "patient" : "nurse");
    }
    
    // Reset/new-bubble logic: trigger whenever a new turn starts (on original OR translation!)
    if (shouldStartNewBubble || bubbleSpeaker !== lastOriginalSpeaker) {
        // New turn requested, or speaker changed! Reset both bubble references.
        currentNurseBubble = null;
        currentPatientBubble = null;
        lastOriginalSpeaker = bubbleSpeaker;
        nurseTurnFinished = false;
        patientTurnFinished = false;
        shouldStartNewBubble = false; // Reset the flag
    } else if (nurseTurnFinished || patientTurnFinished) {
        // Same speaker, but the turn finished (e.g. back-to-back utterances after hold)
        currentNurseBubble = null;
        currentPatientBubble = null;
        nurseTurnFinished = false;
        patientTurnFinished = false;
    }
    
    let bubble = bubbleSpeaker === "nurse" ? currentNurseBubble : currentPatientBubble;
    
    // If no bubble exists for this turn, create one
    if (!bubble) {
        bubble = createSpeechBubble(bubbleSpeaker);
        if (bubbleSpeaker === "nurse") {
            currentNurseBubble = bubble;
        } else {
            currentPatientBubble = bubble;
        }
    }
    
    const bodyDiv = bubble.querySelector(".bubble-body");
    
    if (eventType === "original") {
        const origSpan = bodyDiv.querySelector(".original-text");
        if (origSpan) {
            let raw = origSpan.getAttribute("data-raw") || "";
            raw += text;
            origSpan.setAttribute("data-raw", raw);
            origSpan.innerText = raw;
            if (isFinal) {
                origSpan.classList.remove("interim");
            }
        }
    } else if (eventType === "translation") {
        let transSpan = bodyDiv.querySelector(".translation-text");
        if (!transSpan) {
            logger(`[UI Event] [Translation] Starting translation block to ${bubbleSpeaker === "nurse" ? "target language" : "English"} for speaker: "${bubbleSpeaker}"`);
            transSpan = document.createElement("div");
            transSpan.classList.add("translation-text");
            if (bubbleSpeaker === "nurse" && presetSelector.value === "arabic") {
                transSpan.classList.add("rtl-text");
            }
            bodyDiv.appendChild(transSpan);
        }
        let raw = transSpan.getAttribute("data-raw") || "";
        raw += text;
        transSpan.setAttribute("data-raw", raw);
        transSpan.innerText = raw;
    }
    
    // Highlight in real-time as text streams!
    highlightGlossaryTerms(bubble, bubbleSpeaker);
    
    // Ensure active speaking visual state is triggered for the correct speaker
    setSpeakerActive(bubbleSpeaker, true);
    
    // Auto Scroll
    chatFeed.scrollTop = chatFeed.scrollHeight;
}

function setSpeakerActive(speaker, isActive) {
    if (speaker === "nurse") {
        if (isActive) {
            nurseCard.classList.add("active-speaker");
            nurseStatus.innerText = "Speaking...";
        } else {
            nurseCard.classList.remove("active-speaker");
            nurseStatus.innerText = "Listening";
        }
    } else {
        if (isActive) {
            patientCard.classList.add("active-speaker");
            patientStatus.innerText = "Speaking...";
        } else {
            patientCard.classList.remove("active-speaker");
            patientStatus.innerText = "Listening";
        }
    }
}

function completeTurn(speaker) {
    setSpeakerActive(speaker, false);
    if (speaker === "nurse") {
        nurseTurnFinished = true;
        if (currentNurseBubble) {
            highlightGlossaryTerms(currentNurseBubble, "nurse");
        }
    } else {
        patientTurnFinished = true;
        if (currentPatientBubble) {
            highlightGlossaryTerms(currentPatientBubble, "patient");
        }
    }
}

/* ==========================================================================
   WEBSOCKET INTERACTION & COORDINATION
   ========================================================================== */
function connectCall() {
    initAudio();
    
    // Clear previous transcript and welcome messages
    chatFeed.innerHTML = "";
    
    // Clear and reset encountered references
    encounteredTerms.clear();
    const preset = presetSelector.value;
    const meta = PRESET_UI_METADATA[preset];
    const targetLang = meta ? meta.shortLang : "";
    renderEncounteredReferences(targetLang);
    
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    socket = new WebSocket(wsUrl);
    
    // Update connection statuses
    headerPulse.className = "pulse-indicator status-connecting";
    connectionText.innerText = "Connecting...";
    startBtn.disabled = true;
    presetSelector.disabled = true;
    if (modelSelector) modelSelector.disabled = true;
    if (pacingTurnTimeout) pacingTurnTimeout.disabled = true;
    if (pacingCeasedAudio) pacingCeasedAudio.disabled = true;
    if (pacingStartupAudio) pacingStartupAudio.disabled = true;
    if (pacingAdditionalPause) pacingAdditionalPause.disabled = true;
    resetBtn.disabled = true;
    
    socket.onopen = () => {
        logger("WebSocket connection established. Initializing preset...");
        
        const turnTimeoutVal = pacingTurnTimeout ? parseFloat(pacingTurnTimeout.value) : 15.0;
        const ceasedAudioVal = pacingCeasedAudio ? parseFloat(pacingCeasedAudio.value) : 4.5;
        const startupAudioVal = pacingStartupAudio ? parseFloat(pacingStartupAudio.value) : 15.0;
        const additionalPauseVal = pacingAdditionalPause ? parseFloat(pacingAdditionalPause.value) : 2.0;

        // Send initial starting instruction with selected preset, pacing configuration thresholds
        socket.send(JSON.stringify({
            action: "start",
            preset: presetSelector.value,
            model: modelSelector ? modelSelector.value : "gemini-3.5-live-translate-preview",
            pacing: "auto",
            pause: turnTimeoutVal,
            timeout: turnTimeoutVal,
            ceased_audio_threshold: ceasedAudioVal,
            startup_audio_threshold: startupAudioVal,
            additional_pause_sec: additionalPauseVal
        }));
    };
    
    socket.onmessage = async (event) => {
        try {
            const msg = JSON.parse(event.data);
            
            switch (msg.type) {
                case "status":
                    if (msg.status === "ready") {
                        // Pre-prepared
                        if (welcomeMessage) welcomeMessage.style.display = "none";
                        connectionText.innerText = `Preparing ${msg.language}...`;
                        patientOriginalPlayhead = audioCtx.currentTime + 0.1;
                        nurseOriginalPlayhead = audioCtx.currentTime + 0.1;
                        patientTranslatedPlayhead = audioCtx.currentTime + 0.1;
                        nurseTranslatedPlayhead = audioCtx.currentTime + 0.1;
                        
                        nurseTurnFinished = false;
                        patientTurnFinished = false;
                        currentNurseBubble = null;
                        currentPatientBubble = null;
                        lastOriginalSpeaker = null;
                        shouldStartNewBubble = false;
                    } else if (msg.status === "connected") {
                        headerPulse.className = "pulse-indicator status-connected";
                        connectionText.innerText = "LIVE (Bidirectional)";
                        endBtn.disabled = false;
                        if (pauseBtn) pauseBtn.disabled = false;
                        setSpeakerActive("nurse", false);
                        setSpeakerActive("patient", false);
                        
                        // Log call system message
                        const sysMsg = document.createElement("div");
                        sysMsg.className = "system-message";
                        sysMsg.innerHTML = `🟢 <strong>Live Translation Connected!</strong> Call started in ${PRESET_UI_METADATA[presetSelector.value]?.lang || 'Foreign Language'}.`;
                        chatFeed.appendChild(sysMsg);
                    } else if (msg.status === "completed") {
                        endCall(true);
                    }
                    break;
                    
                case "original_audio":
                    // Original pre-recorded WAV stream chunk (16kHz PCM)
                    const origBuffer = decodePCM(msg.data, 16000);
                    if (origBuffer) {
                        schedulePlayback(origBuffer, "original", msg.speaker);
                    }
                    break;
                    
                case "translated_audio":
                    // Gemini's translated voice output stream chunk (24kHz PCM)
                    const transBuffer = decodePCM(msg.data, 24000);
                    if (transBuffer) {
                        schedulePlayback(transBuffer, "translated", msg.stream);
                    }
                    break;
                    
                case "transcript":
                    // Update live scrolling bubbles
                    updateSpeechText(msg.speaker, msg.event, msg.text, msg.final);
                    break;
                    
                case "turn_complete":
                    completeTurn(msg.speaker);
                    logger(`Turn complete for ${msg.speaker}.`);
                    shouldStartNewBubble = true;
                    break;
                    
                case "stream_paused":
                    logger(`Backend stream paused after ${msg.speaker}'s turn.`);
                    if (msg.speaker === "patient") {
                        patientStatus.innerText = "Processing...";
                    } else {
                        nurseStatus.innerText = "Processing...";
                    }
                    shouldStartNewBubble = true;
                    break;
                    
                case "interrupted":
                    completeTurn(msg.speaker);
                    break;
                    
                case "error":
                    alert(`Backend Error: ${msg.message}`);
                    endCall(false);
                    break;
            }
        } catch (err) {
            console.error("[Interpreter Client] Error processing WebSocket message:", err, event.data);
        }
    };
    
    socket.onclose = () => {
        logger("WebSocket connection closed.");
        endCall(false);
    };
    
    socket.onerror = (err) => {
        console.error("WebSocket Error: ", err);
        endCall(false);
    };
}

function endCall(isNaturalCompletion = false) {
    if (socket) {
        socket.close();
        socket = null;
    }
    
    headerPulse.className = "pulse-indicator status-disconnected";
    connectionText.innerText = "Not Connected";
    
    startBtn.disabled = false;
    presetSelector.disabled = false;
    if (modelSelector) modelSelector.disabled = false;
    if (pacingTurnTimeout) pacingTurnTimeout.disabled = false;
    if (pacingCeasedAudio) pacingCeasedAudio.disabled = false;
    if (pacingStartupAudio) pacingStartupAudio.disabled = false;
    if (pacingAdditionalPause) pacingAdditionalPause.disabled = false;
    endBtn.disabled = true;
    if (pauseBtn) {
        pauseBtn.disabled = true;
        pauseBtn.innerHTML = "⏸️ Pause Call";
        pauseBtn.className = "btn btn-warning";
    }
    isCallPaused = false;
    
    if (audioCtx && audioCtx.state === "suspended") {
        audioCtx.resume();
    }
    
    resetBtn.disabled = false;
    
    setSpeakerActive("nurse", false);
    setSpeakerActive("patient", false);
    
    currentNurseBubble = null;
    currentPatientBubble = null;
    nurseTurnFinished = false;
    patientTurnFinished = false;
    lastOriginalSpeaker = null;
    shouldStartNewBubble = false;
    
    if (isNaturalCompletion) {
        const sysMsg = document.createElement("div");
        sysMsg.className = "system-message";
        sysMsg.innerHTML = `🏁 <strong>Call Completed successfully.</strong> Audio streams finished.`;
        chatFeed.appendChild(sysMsg);
    }
}

// Bind Button Listeners
startBtn.addEventListener("click", connectCall);
endBtn.addEventListener("click", () => endCall(false));

if (pauseBtn) {
    pauseBtn.addEventListener("click", () => {
        if (!socket || socket.readyState !== WebSocket.OPEN) return;
        isCallPaused = !isCallPaused;
        if (isCallPaused) {
            if (audioCtx) {
                audioCtx.suspend();
            }
            socket.send(JSON.stringify({ action: "pause" }));
            pauseBtn.innerHTML = "▶️ Resume Call";
            pauseBtn.classList.replace("btn-warning", "btn-primary");
        } else {
            if (audioCtx) {
                audioCtx.resume();
            }
            socket.send(JSON.stringify({ action: "resume_call" }));
            pauseBtn.innerHTML = "⏸️ Pause Call";
            pauseBtn.classList.replace("btn-primary", "btn-warning");
        }
    });
}

resetBtn.addEventListener("click", () => {
    logger("Resetting call UI, clearing cache, and conversation state.");
    
    // Force stylesheet reload to bust browser CSS cache
    document.querySelectorAll("link[rel='stylesheet']").forEach(link => {
        try {
            const url = new URL(link.href, window.location.href);
            url.searchParams.set("v", Date.now());
            link.href = url.toString();
        } catch (e) {
            link.href = 'style.css?v=' + Date.now();
        }
    });

    // Clear local storage and session storage
    try {
        localStorage.clear();
        sessionStorage.clear();
    } catch (e) {
        console.warn("Storage clear blocked: ", e);
    }

    chatFeed.innerHTML = `
        <div class="system-message" id="welcome-message">
            Select a consultation scenario above and click "Start Call" to begin the real-time AI interpreter demo.
        </div>
    `;
    
    // Clear and reset encountered references
    encounteredTerms.clear();
    const preset = presetSelector.value;
    const meta = PRESET_UI_METADATA[preset];
    const targetLang = meta ? meta.shortLang : "";
    renderEncounteredReferences(targetLang);
    
    // Fetch latest glossary terms with cache-busting
    fetchGlossary();
    
    // Reset playheads to current audio time or 0
    if (audioCtx) {
        patientOriginalPlayhead = audioCtx.currentTime;
        nurseOriginalPlayhead = audioCtx.currentTime;
        patientTranslatedPlayhead = audioCtx.currentTime;
        nurseTranslatedPlayhead = audioCtx.currentTime;
    } else {
        patientOriginalPlayhead = 0;
        nurseOriginalPlayhead = 0;
        patientTranslatedPlayhead = 0;
        nurseTranslatedPlayhead = 0;
    }
    
    currentNurseBubble = null;
    currentPatientBubble = null;
    nurseTurnFinished = false;
    patientTurnFinished = false;
    
    if (pauseBtn) {
        pauseBtn.disabled = true;
        pauseBtn.innerHTML = "⏸️ Pause Call";
        pauseBtn.className = "btn btn-warning";
    }
    isCallPaused = false;
    if (audioCtx && audioCtx.state === "suspended") {
        audioCtx.resume();
    }
    
    setSpeakerActive("nurse", false);
    setSpeakerActive("patient", false);
});

// Simple Console Logger helper
function logger(msg) {
    console.log(`[Interpreter Client] ${msg}`);
}

