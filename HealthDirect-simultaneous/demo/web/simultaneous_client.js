/**
 * HealthDirect Simultaneous Split-View Web Audio & WebSocket Client.
 * Handles dual-channel panner mixing, presenter focus tab muting, gapless PCM 
 * audio queuing, and bilingual medical glossary reference highlights.
 */

const PRESET_UI_METADATA = {
    "german": { lang: "German", shortLang: "de" },
    "spanish": { lang: "Spanish", shortLang: "es" },
    "vietnamese": { lang: "Vietnamese", shortLang: "vi" },
    "arabic": { lang: "Arabic", shortLang: "ar" }
};

let currentRole = null; // "nurse" or "patient"
let socket = null;
let heartbeatInterval = null;
let audioCtx = null;

// Audio Graph nodes
let gainOriginal = null;
let gainTranslation = null;
let pannerOriginal = null;
let pannerTranslation = null;
let gainMaster = null;

let isTabMuted = false;

// Playhead queue timelines
let patientOriginalPlayhead = 0;
let nurseOriginalPlayhead = 0;
let patientTranslatedPlayhead = 0;
let nurseTranslatedPlayhead = 0;

// State management
let glossaryTerms = [];
let encounteredTerms = new Set();
let currentPreset = "german";

// Active chat elements (separated to prevent overlapping conjoined turns)
let currentPatientOriginalBubble = null;
let currentPatientTranslationBubble = null;
let currentNurseOriginalBubble = null;
let currentNurseTranslationBubble = null;
let lastElapsedSeconds = 0;

/**
 * Initializes the client based on their room role ("nurse" or "patient").
 */
function initSimultaneousClient(role) {
    currentRole = role;
    console.log(`[Simultaneous Client] Initializing for role: ${role}`);
    
    // Bind UI elements based on role
    const btnMuteTab = document.getElementById("btn-mute-tab");
    if (btnMuteTab) {
        btnMuteTab.addEventListener("click", toggleTabMute);
    }

    const panSlider = document.getElementById("pan-slider");
    if (panSlider) {
        panSlider.addEventListener("input", updateMixerVolumes);
    }

    if (role === "nurse") {
        const btnStart = document.getElementById("btn-start");
        const btnEnd = document.getElementById("btn-end");
        const presetSelector = document.getElementById("preset-selector");
        const modelSelector = document.getElementById("model-selector");

        btnStart.addEventListener("click", () => {
            initAudio();
            btnStart.disabled = true;
            btnEnd.disabled = false;
            presetSelector.disabled = true;
            modelSelector.disabled = true;
            
            // Clear previous chats
            document.getElementById("patient-feed").innerHTML = "";
            document.getElementById("nurse-feed").innerHTML = "";
            encounteredTerms.clear();
            renderEncounteredSidebar();

            socket.send(JSON.stringify({
                action: "start"
            }));
        });

        btnEnd.addEventListener("click", () => {
            socket.send(JSON.stringify({
                action: "stop"
            }));
            btnStart.disabled = false;
            btnEnd.disabled = true;
            presetSelector.disabled = false;
            modelSelector.disabled = false;
        });

        presetSelector.addEventListener("change", () => {
            currentPreset = presetSelector.value;
            syncConfiguration();
        });

        modelSelector.addEventListener("change", syncConfiguration);

        const btnReset = document.getElementById("btn-reset");
        if (btnReset) {
            btnReset.addEventListener("click", () => {
                socket.send(JSON.stringify({
                    action: "reset"
                }));
            });
        }
    }

    connectWebSocket();
}

/**
 * Connects the WebSocket routing proxy.
 */
function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/${currentRole}`;
    console.log(`[WebSocket] Connecting to: ${wsUrl}`);
    
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log("[WebSocket] Connection open.");
        if (currentRole === "nurse") {
            syncConfiguration();
        }
        // Start a 5s keepalive heartbeat ping to prevent connection timeout by network proxies
        if (heartbeatInterval) clearInterval(heartbeatInterval);
        heartbeatInterval = setInterval(() => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ action: "ping" }));
            }
        }, 5000);
    };

    socket.onmessage = async (event) => {
        try {
            const msg = JSON.parse(event.data);
            handleServerMessage(msg);
        } catch (e) {
            console.error("[WebSocket] Failed to parse message:", e);
        }
    };

    socket.onclose = () => {
        if (heartbeatInterval) {
            clearInterval(heartbeatInterval);
            heartbeatInterval = null;
        }
        console.warn("[WebSocket] Connection closed. Retrying in 3 seconds...");
        setTimeout(connectWebSocket, 3000);
    };
}

/**
 * Synchronizes nurse's configurations with the session coordinator.
 */
function syncConfiguration() {
    if (currentRole !== "nurse" || !socket || socket.readyState !== WebSocket.OPEN) return;
    
    const preset = document.getElementById("preset-selector").value;
    const model = document.getElementById("model-selector").value;
    const meta = PRESET_UI_METADATA[preset];
    
    socket.send(JSON.stringify({
        action: "config_update",
        preset: preset,
        model: model,
        language: meta ? meta.lang : "German"
    }));
}

/**
 * Routes and handles all incoming messages from the backend server.
 */
function handleServerMessage(msg) {
    switch (msg.type) {
        case "prewarm_status":
            updatePrewarmUI(msg.status);
            break;

        case "state_sync":
        case "config_update":
            console.log("[State Sync]", msg);
            currentPreset = msg.preset;
            const meta = PRESET_UI_METADATA[msg.preset];
            
            // Sync local inputs if nurse
            if (currentRole === "nurse") {
                document.getElementById("preset-selector").value = msg.preset;
                document.getElementById("model-selector").value = msg.model;
            } else {
                // If patient, update indicator
                const bar = document.getElementById("triage-status-bar");
                if (bar) {
                    bar.innerText = `Line Connected: Nurse translates into ${meta ? meta.lang : "Native"}`;
                    bar.className = "triage-indicator triage-live";
                }
            }
            
            // Trigger glossary download (using full language name for key matching)
            if (meta) {
                fetchGlossary(meta.lang);
                const tag = document.getElementById("patient-lang-tag");
                if (tag) tag.innerText = meta.lang;
            }

            // Update audio panning labels dynamically to reflect active languages
            const labelLeft = document.getElementById("pan-label-left");
            const labelRight = document.getElementById("pan-label-right");
            if (labelLeft && labelRight && meta) {
                if (currentRole === "nurse") {
                    labelLeft.innerText = `${meta.lang} (Left)`;
                    labelRight.innerText = `English / Interpreter (Right)`;
                } else {
                    labelLeft.innerText = `Nurse (Left)`;
                    labelRight.innerText = `${meta.lang} / Interpreter (Right)`;
                }
            }
            break;

        case "status":
            if (msg.status === "ready") {
                updatePrewarmUI("disconnected");
                initAudio();
                patientOriginalPlayhead = audioCtx.currentTime + 0.1;
                nurseOriginalPlayhead = audioCtx.currentTime + 0.1;
                patientTranslatedPlayhead = audioCtx.currentTime + 0.1;
                nurseTranslatedPlayhead = audioCtx.currentTime + 0.1;
                
                // Clear feeds
                document.getElementById("patient-feed").innerHTML = "";
                const nurseFeed = document.getElementById("nurse-feed");
                if (nurseFeed) nurseFeed.innerHTML = "";
                
                currentPatientOriginalBubble = null;
                currentPatientTranslationBubble = null;
                currentNurseOriginalBubble = null;
                currentNurseTranslationBubble = null;
                encounteredTerms.clear();
                renderEncounteredSidebar();
            } else if (msg.status === "completed") {
                console.log("[Streaming Completed]");
                if (currentRole === "nurse") {
                    document.getElementById("btn-start").disabled = false;
                    document.getElementById("btn-end").disabled = true;
                    document.getElementById("preset-selector").disabled = false;
                    document.getElementById("model-selector").disabled = false;
                }
            } else if (msg.status === "waiting_for_nurse") {
                const bar = document.getElementById("triage-status-bar");
                if (bar) {
                    bar.innerText = "Waiting for Nurse to Start Session...";
                    bar.className = "triage-indicator triage-waiting";
                }
            }
            break;

        case "original_audio":
            // Stream raw PCM chunks
            const origBuffer = decodePCM(msg.data, 16000);
            if (origBuffer) {
                schedulePlayback(origBuffer, "original", msg.speaker);
            }
            break;

        case "translated_audio":
            // Stream translated Live PCM chunks
            const transBuffer = decodePCM(msg.data, 24000);
            if (transBuffer) {
                schedulePlayback(transBuffer, "translated", msg.stream);
            }
            break;

        case "playhead":
            const elapsedMs = msg.elapsed_ms;
            lastElapsedSeconds = Math.floor(elapsedMs / 1000);
            
            const playheadFill = document.getElementById("playhead-fill");
            const playheadTime = document.getElementById("playhead-time");
            if (playheadFill && playheadTime) {
                const durationMs = msg.duration_ms;
                const pct = Math.min(100, (elapsedMs / durationMs) * 100);
                playheadFill.style.width = `${pct}%`;
                
                const mm = String(Math.floor(lastElapsedSeconds / 60)).padStart(2, '0');
                const ss = String(lastElapsedSeconds % 60).padStart(2, '0');
                playheadTime.innerText = `${mm}:${ss}`;
            }
            break;

        case "transcript":
            updateSpeechText(msg.speaker, msg.event, msg.text, msg.final);
            break;

        case "turn_complete":
            completeTurn(msg.speaker);
            break;

        case "reset":
            console.log("[WebSocket] Received reset command from server. Performing cache-busted page reload...");
            window.location.href = window.location.origin + window.location.pathname + "?t=" + Date.now() + window.location.hash;
            break;

        case "error":
            alert(`Interpretation Error: ${msg.message}`);
            break;
    }
}

/**
 * Initializes the local Web Audio context and establishes the panning graph.
 */
function initAudio() {
    if (audioCtx) return;
    
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    audioCtx = new AudioContextClass();
    
    // Create gain and panner nodes
    gainOriginal = audioCtx.createGain();
    gainTranslation = audioCtx.createGain();
    
    pannerOriginal = audioCtx.createStereoPanner();
    pannerOriginal.pan.value = -0.6; // Panned Left-ish
    
    pannerTranslation = audioCtx.createStereoPanner();
    pannerTranslation.pan.value = 0.6; // Panned Right-ish
    
    gainMaster = audioCtx.createGain();
    gainMaster.gain.setValueAtTime(isTabMuted ? 0 : 1, audioCtx.currentTime);

    // Assemble the Audio Graph
    gainOriginal.connect(pannerOriginal);
    pannerOriginal.connect(gainMaster);
    
    gainTranslation.connect(pannerTranslation);
    pannerTranslation.connect(gainMaster);
    
    gainMaster.connect(audioCtx.destination);
    
    updateMixerVolumes();
}

/**
 * Updates relative gain node volumes based on the crossfader pan-slider.
 */
function updateMixerVolumes() {
    if (!gainOriginal || !gainTranslation) return;
    
    const panVal = parseFloat(document.getElementById("pan-slider").value);
    let volOrig = 1.0;
    let volTrans = 1.0;
    
    if (panVal < 0) {
        // Fade translation towards Left original voice
        volTrans = 1.0 + panVal;
    } else if (panVal > 0) {
        // Fade original towards Right interpreter
        volOrig = 1.0 - panVal;
    }
    
    gainOriginal.gain.setTargetAtTime(volOrig, audioCtx.currentTime, 0.01);
    gainTranslation.gain.setTargetAtTime(volTrans, audioCtx.currentTime, 0.01);
}

/**
 * Toggles single-machine presenter tab-muting to prevent Meet audio loop echoes.
 */
function toggleTabMute() {
    isTabMuted = !isTabMuted;
    const btn = document.getElementById("btn-mute-tab");
    
    if (btn) {
        if (isTabMuted) {
            btn.classList.add("active");
            btn.innerText = "🔇 Demo Focus: Tab Muted";
            if (gainMaster) {
                gainMaster.gain.setTargetAtTime(0, audioCtx.currentTime, 0.01);
            }
        } else {
            btn.classList.remove("active");
            btn.innerText = "🔊 Demo Focus: Mute Tab Audio";
            if (gainMaster) {
                gainMaster.gain.setTargetAtTime(1, audioCtx.currentTime, 0.01);
            }
        }
    }
}

/**
 * Decodes base64-encoded binary PCM chunks into a Web Audio Float32 wave.
 */
function decodePCM(base64Str, sampleRate) {
    try {
        const binaryString = window.atob(base64Str);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        
        const int16Array = new Int16Array(bytes.buffer);
        const float32Array = new Float32Array(int16Array.length);
        for (let i = 0; i < int16Array.length; i++) {
            float32Array[i] = int16Array[i] / 32768.0;
        }
        
        const buffer = audioCtx.createBuffer(1, float32Array.length, sampleRate);
        buffer.copyToChannel(float32Array, 0);
        return buffer;
    } catch (e) {
        console.error("[Audio] Failed to decode PCM segment:", e);
        return null;
    }
}

/**
 * Gaplessly stitches and schedules chunks on the playhead timelines.
 */
function schedulePlayback(buffer, streamType, speakerOrStream) {
    if (!audioCtx || !buffer) return;
    
    if (audioCtx.state === "suspended") {
        audioCtx.resume();
    }
    
    const source = audioCtx.createBufferSource();
    source.buffer = buffer;
    
    const now = audioCtx.currentTime;
    const JITTER_THRESHOLD = 0.35;
    const Headroom = 0.05;
    
    if (streamType === "original") {
        if (speakerOrStream === "patient") {
            if (patientOriginalPlayhead < now - JITTER_THRESHOLD) {
                patientOriginalPlayhead = now + Headroom;
            }
            source.connect(gainOriginal);
            source.start(patientOriginalPlayhead);
            patientOriginalPlayhead += buffer.duration;
        } else {
            if (nurseOriginalPlayhead < now - JITTER_THRESHOLD) {
                nurseOriginalPlayhead = now + Headroom;
            }
            source.connect(gainOriginal);
            source.start(nurseOriginalPlayhead);
            nurseOriginalPlayhead += buffer.duration;
        }
    } else {
        if (speakerOrStream === "p_to_n") {
            if (patientTranslatedPlayhead < now - JITTER_THRESHOLD) {
                patientTranslatedPlayhead = now + Headroom;
            }
            source.connect(gainTranslation);
            source.start(patientTranslatedPlayhead);
            patientTranslatedPlayhead += buffer.duration;
        } else {
            if (nurseTranslatedPlayhead < now - JITTER_THRESHOLD) {
                nurseTranslatedPlayhead = now + Headroom;
            }
            source.connect(gainTranslation);
            source.start(nurseTranslatedPlayhead);
            nurseTranslatedPlayhead += buffer.duration;
        }
    }
}

/**
 * Creates scrolling bubbles and prints real-time original & translated texts.
 */
function updateSpeechText(speaker, eventType, text, isFinal) {
    // Filter redundant self-translations and unneeded language feeds
    if (currentRole === "nurse") {
        // Nurse screen (/nurse) doesn't need "Nurse (Translated)" (German version)
        if (eventType === "translation" && speaker === "nurse") {
            return;
        }
    }
    
    if (currentRole === "patient") {
        // Patient screen (/patient) only understands German (or the active preset native language)
        // So filter out English originals from the nurse, and English translations from the patient:
        if (speaker === "nurse" && eventType === "original") {
            return; // Filter out "Nurse (Original)" (English)
        }
        if (speaker === "patient" && eventType === "translation") {
            return; // Filter out "Patient (Translated)" (English)
        }
    }

    const feedId = (currentRole === "patient") ? "patient-feed" : `${speaker}-feed`;
    const feed = document.getElementById(feedId);
    if (!feed) return;

    // Cross-speaker turn-taking bubble finalization:
    // If the active speaker is actually speaking new text, the other speaker's turns are complete.
    if (text && text.trim().length > 0) {
        if (speaker === "patient") {
            currentNurseOriginalBubble = null;
            currentNurseTranslationBubble = null;
        } else {
            currentPatientOriginalBubble = null;
            currentPatientTranslationBubble = null;
        }
    }

    // Determine which specific bubble tracking anchor to use (original vs translated)
    let bubble = null;
    if (speaker === "patient") {
        if (eventType === "original") {
            bubble = currentPatientOriginalBubble;
        } else {
            bubble = currentPatientTranslationBubble;
        }
    } else {
        if (eventType === "original") {
            bubble = currentNurseOriginalBubble;
        } else {
            bubble = currentNurseTranslationBubble;
        }
    }
    
    if (!bubble) {
        // Clear connection prompt
        const waitingPrompt = feed.querySelector(".system-message");
        if (waitingPrompt) waitingPrompt.remove();

        bubble = document.createElement("div");
        const typeClass = (eventType === "original") ? "original-turn" : "translated-turn";
        bubble.className = `chat-turn ${speaker}-turn ${typeClass}`;
        
        let headerLabel = "";
        if (speaker === "patient") {
            headerLabel = (eventType === "original") ? "Patient (Native)" : "Patient (Translated)";
        } else {
            headerLabel = (eventType === "original") ? "Nurse (Original)" : "Nurse (Translated)";
        }

        const mm = String(Math.floor(lastElapsedSeconds / 60)).padStart(2, '0');
        const ss = String(lastElapsedSeconds % 60).padStart(2, '0');
        const timestamp = `${mm}:${ss}`;

        console.log(`%c[UI - NEW BUBBLE] Created NEW bubble for speaker="${speaker}", type="${eventType}" at ${timestamp} (playhead: ${lastElapsedSeconds}s)`, "color: #10b981; font-weight: bold;");

        bubble.innerHTML = `
            <div class="bubble-meta" style="font-weight:600; font-size:0.8rem; margin-bottom:4px; color:var(--text-secondary);">
                ${headerLabel} • ${timestamp}
            </div>
            <div class="bubble-body">
                <span class="original-text ${isFinal ? '' : 'interim'}"></span>
            </div>
        `;
        feed.appendChild(bubble);
        feed.scrollTop = feed.scrollHeight;

        if (speaker === "patient") {
            if (eventType === "original") {
                currentPatientOriginalBubble = bubble;
            } else {
                currentPatientTranslationBubble = bubble;
            }
        } else {
            if (eventType === "original") {
                currentNurseOriginalBubble = bubble;
            } else {
                currentNurseTranslationBubble = bubble;
            }
        }
    } else {
        console.log(`%c[UI - REUSE BUBBLE] Appending text to existing bubble for speaker="${speaker}", type="${eventType}"`, "color: #3b82f6;");
    }

    const bodySpan = bubble.querySelector(".original-text");
    if (bodySpan) {
        const appended = bodySpan.innerText + text;
        bodySpan.innerText = appended;
        
        // Highlight terms using full language name
        const meta = PRESET_UI_METADATA[currentPreset];
        if (meta) {
            const matchLang = (speaker === "nurse") ? "english" : meta.lang;
            const highlightedHtml = applyHTMLHighlight(appended, matchLang, meta.lang);
            bodySpan.innerHTML = highlightedHtml;
        }

        if (isFinal) {
            bodySpan.classList.remove("interim");
            console.log(`%c[UI - UTTERANCE FINAL] Utterance is FINAL for speaker="${speaker}", type="${eventType}". Clearing active bubble tracking anchor.`, "color: #f59e0b; font-weight: bold;");
            // Set tracking bubble to null so the next utterance starts a fresh bubble
            if (speaker === "patient") {
                if (eventType === "original") {
                    currentPatientOriginalBubble = null;
                } else {
                    currentPatientTranslationBubble = null;
                }
            } else {
                if (eventType === "original") {
                    currentNurseOriginalBubble = null;
                } else {
                    currentNurseTranslationBubble = null;
                }
            }
        }
    }
    
    feed.scrollTop = feed.scrollHeight;
}

/**
 * Terminates turn markers, clearing the active bubble to force a new bubble on next turn.
 */
function completeTurn(speaker) {
    console.log(`%c[UI - TURN COMPLETE] Received turn_complete event for speaker="${speaker}". Clearing all tracking anchors for this speaker.`, "color: #ef4444; font-weight: bold;");
    if (speaker === "patient") {
        currentPatientOriginalBubble = null;
        currentPatientTranslationBubble = null;
    } else {
        currentNurseOriginalBubble = null;
        currentNurseTranslationBubble = null;
    }
}

/* ==========================================================================
   CLINICAL BILINGUAL GLOSSARY PARSING & HIGHLIGHTS
   ========================================================================== */

async function fetchGlossary(langCode) {
    try {
        const response = await fetch(`/api/glossary?language=${langCode}&_=${Date.now()}`);
        if (response.ok) {
            const data = await response.json();
            glossaryTerms = data.glossary || [];
            console.log(`[Glossary] Loaded ${glossaryTerms.length} terms for: ${langCode}`);
        }
    } catch (e) {
        console.error("[Glossary] Error loading terms:", e);
    }
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function escapeHTML(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/**
 * Implements the Robust Glossary Schema Parsing rule to recurse nested translations.
 */
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
            return Object.values(val).map(v => getTranslationString(v)).filter(Boolean).join(", ");
        }
        return filteredParts.join(", ");
    }
    return String(val).trim();
}

/**
 * Highlights glossary matches inside transcripts and records detected terms.
 */
function applyHTMLHighlight(text, matchLanguage, targetLang) {
    if (!text || !glossaryTerms || glossaryTerms.length === 0) return escapeHTML(text);
    
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
            const synonyms = termVal.split(/[,;]+/).map(s => s.trim()).filter(Boolean);
            synonyms.forEach(syn => {
                const words = syn.split(/\s+/);
                let patternStr;
                if (words.length > 1) {
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
    
    if (termsWithPatterns.length === 0) return escapeHTML(text);
    
    termsWithPatterns.sort((a, b) => b.canonical.length - a.canonical.length);
    
    const overallPatternStr = "(?<!\\p{L})(" + termsWithPatterns.map(item => item.patternStr).join("|") + ")(?!\\p{L})";
    const regex = new RegExp(overallPatternStr, "gui");
    
    // Convert text to escaped string before doing match-replacements
    const escapedText = escapeHTML(text);
    
    return escapedText.replace(regex, (matched) => {
        const matchItem = termsWithPatterns.find(item => item.regex.test(matched));
        if (matchItem) {
            const entry = matchItem.entry;
            
            // Trigger Sidebar card rendering on detection
            if (!encounteredTerms.has(entry.english)) {
                encounteredTerms.add(entry.english);
                renderEncounteredSidebar();
            }

            const englishTerm = entry.english || "";
            const translations = entry.translations || {};
            const transKey = Object.keys(translations).find(k => k.toLowerCase() === targetLang.toLowerCase());
            const translationVal = transKey ? getTranslationString(translations[transKey]) : "";
            const desc = entry.description || "";
            
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

function getTermUrl(entry, targetLang) {
    if (entry.url) return entry.url;
    const trans = entry.translations || {};
    const key = Object.keys(trans).find(k => k.toLowerCase() === targetLang.toLowerCase());
    if (key && entry[`url_${key.toLowerCase()}`]) {
        return entry[`url_${key.toLowerCase()}`];
    }
    return `https://www.healthdirect.gov.au/search-results?q=${encodeURIComponent(entry.english)}`;
}

/**
 * Renders clinical cards to the nurse's sidebar console.
 */
function renderEncounteredSidebar() {
    const sidebar = document.getElementById("glossary-sidebar");
    if (!sidebar) return;
    
    sidebar.innerHTML = "";
    
    if (encounteredTerms.size === 0) {
        sidebar.innerHTML = `
            <div class="system-message" style="text-align: center; color: var(--text-muted); margin-top: 50px; font-size: 0.8rem;">
                Terms detected in transcription will appear here with approved translations and clinical advice.
            </div>
        `;
        return;
    }
    
    const sorted = Array.from(encounteredTerms).sort();
    const meta = PRESET_UI_METADATA[currentPreset];
    const targetLang = meta ? meta.shortLang : "de";
    
    sorted.forEach(term => {
        const entry = glossaryTerms.find(e => e.english === term);
        if (!entry) return;
        
        const trans = entry.translations || {};
        const key = Object.keys(trans).find(k => k.toLowerCase() === targetLang.toLowerCase());
        const translationVal = key ? getTranslationString(trans[key]) : "";
        const groundingUrl = getTermUrl(entry, targetLang);
        
        const card = document.createElement("div");
        card.className = "glossary-card";
        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <span class="glossary-term">${entry.english}</span>
                <a href="${groundingUrl}" target="_blank" rel="noopener noreferrer" style="font-size:0.75rem; text-decoration:none; color:var(--brand-teal);">
                    Grounding Advice 🔗
                </a>
            </div>
            ${translationVal ? `<div class="glossary-translation">Approved: ${translationVal}</div>` : ""}
            <div class="glossary-desc">${entry.description || "No clinical description provided."}</div>
        `;
        sidebar.appendChild(card);
    });
}

/**
 * Resets local transcript boxes, audio playheads, progress counters, and glossary sidebars.
 */
function resetLocalSession() {
    console.log("[Client] Cleaning local session state...");
    lastElapsedSeconds = 0;
    
    // Clear scrolling feeds with descriptive placeholder system message
    const patientFeed = document.getElementById("patient-feed");
    if (patientFeed) {
        patientFeed.innerHTML = `
            <div class="system-message" style="margin: auto; text-align: center; color: var(--text-muted);">
                ${currentRole === "patient" ? 
                  "When the nurse starts the session, translations of your conversation will stream here in real-time." : 
                  "Dialogue feed cleared."}
            </div>
        `;
    }
    
    const nurseFeed = document.getElementById("nurse-feed");
    if (nurseFeed) {
        nurseFeed.innerHTML = `
            <div class="system-message" style="margin: auto; text-align: center; color: var(--text-muted);">
                Dialogue feed cleared.
            </div>
        `;
    }

    // Reset gapless playback playheads to current audio time
    if (audioCtx) {
        const now = audioCtx.currentTime;
        patientOriginalPlayhead = now;
        nurseOriginalPlayhead = now;
        patientTranslatedPlayhead = now;
        nurseTranslatedPlayhead = now;
    }

    // Clear glossary sidebar cards and sets
    encounteredTerms.clear();
    renderEncounteredSidebar();

    // Reset progress/playhead UI
    const playheadFill = document.getElementById("playhead-fill");
    const playheadTime = document.getElementById("playhead-time");
    if (playheadFill) playheadFill.style.width = "0%";
    if (playheadTime) playheadTime.innerText = "00:00";

    // Re-enable Start button & settings selectors for nurse
    if (currentRole === "nurse") {
        document.getElementById("btn-start").disabled = false;
        document.getElementById("btn-end").disabled = true;
        document.getElementById("preset-selector").disabled = false;
        document.getElementById("model-selector").disabled = false;
    }
}

/**
 * Updates the pre-warm connection standby badge and indicators.
 */
function updatePrewarmUI(status) {
    const badge = document.getElementById("prewarm-badge");
    const dot = document.getElementById("prewarm-dot");
    const text = document.getElementById("prewarm-text");
    if (!badge || !dot || !text) return;

    badge.style.display = "inline-flex";

    if (currentRole === "patient") {
        // Patient styling overrides for dark teal background card
        if (status === "connecting") {
            badge.style.backgroundColor = "rgba(234, 179, 8, 0.25)";
            badge.style.borderColor = "rgba(234, 179, 8, 0.4)";
            dot.style.backgroundColor = "#facc15";
            dot.style.boxShadow = "0 0 10px #eab308";
            text.innerText = "Standby: Pre-warming...";
        } else if (status === "ready") {
            badge.style.backgroundColor = "rgba(45, 212, 191, 0.25)";
            badge.style.borderColor = "rgba(45, 212, 191, 0.4)";
            dot.style.backgroundColor = "#2dd4bf";
            dot.style.boxShadow = "0 0 10px #2dd4bf";
            text.innerText = "Standby: Hot & Ready";
        } else {
            badge.style.backgroundColor = "rgba(255, 255, 255, 0.15)";
            badge.style.borderColor = "rgba(255, 255, 255, 0.25)";
            dot.style.backgroundColor = "rgba(255, 255, 255, 0.6)";
            dot.style.boxShadow = "0 0 6px rgba(255, 255, 255, 0.4)";
            text.innerText = "Standby: Off";
        }
    } else {
        // Nurse standard light/dark mode styling overrides
        if (status === "connecting") {
            badge.style.backgroundColor = "#fef9c3";
            badge.style.color = "#854d0e";
            dot.style.backgroundColor = "#eab308";
            dot.style.boxShadow = "0 0 10px #eab308";
            text.innerText = "Standby: Pre-warming...";
        } else if (status === "ready") {
            badge.style.backgroundColor = "#ccfbf1";
            badge.style.color = "#115e59";
            dot.style.backgroundColor = "#0d9488";
            dot.style.boxShadow = "0 0 10px #0d9488";
            text.innerText = "Standby: Hot & Ready";
        } else {
            badge.style.backgroundColor = "#f1f5f9";
            badge.style.color = "#475569";
            dot.style.backgroundColor = "#94a3b8";
            dot.style.boxShadow = "0 0 6px #cbd5e1";
            text.innerText = "Standby: Off";
        }
    }
}
