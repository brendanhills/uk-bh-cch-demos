/* ==========================================================================
   STATE MANAGEMENT & UI INITIALIZATION
   ========================================================================== */
let socket = null;
let audioCtx = null;
let glossaryTerms = [];

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
    }
};

// UI Elements
const presetSelector = document.getElementById("preset-selector");
const pacingSelector = document.getElementById("pacing-selector");
const pauseInput = document.getElementById("pause-input");
const startBtn = document.getElementById("start-btn");
const pauseBtn = document.getElementById("pause-btn");
const endBtn = document.getElementById("end-btn");
const resetBtn = document.getElementById("reset-btn");
const nextBtn = document.getElementById("next-btn");
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

/* ==========================================================================
   CLINICAL GLOSSARY INTEGRATION
   ========================================================================== */
async function fetchGlossary() {
    const preset = presetSelector.value;
    const meta = PRESET_UI_METADATA[preset];
    if (!meta) return;
    
    try {
        const response = await fetch(`/api/glossary?language=${meta.shortLang}`);
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

function renderGlossaryList() {
    const listDiv = document.getElementById("glossary-list");
    const countBadge = document.getElementById("glossary-count");
    if (!listDiv) return;
    
    listDiv.innerHTML = "";
    
    if (countBadge) {
        countBadge.innerText = `${glossaryTerms.length} Term${glossaryTerms.length === 1 ? "" : "s"}`;
    }
    
    if (glossaryTerms.length === 0) {
        listDiv.innerHTML = '<div class="glossary-empty">No glossary terms loaded.</div>';
        return;
    }
    
    const preset = presetSelector.value;
    const meta = PRESET_UI_METADATA[preset];
    const targetLang = meta ? meta.shortLang : "";
    
    // Sort glossary terms alphabetically by their English term
    glossaryTerms.sort((a, b) => (a.english || "").localeCompare(b.english || ""));
    
    glossaryTerms.forEach(entry => {
        const itemDiv = document.createElement("div");
        itemDiv.className = "glossary-item";
        
        const trans = entry.translations || {};
        const transKey = Object.keys(trans).find(k => k.toLowerCase() === targetLang.toLowerCase());
        const translationVal = transKey ? trans[transKey] : "";
        
        const termRow = document.createElement("div");
        termRow.className = "item-term-row";
        
        const englishSpan = document.createElement("span");
        englishSpan.className = "item-english";
        englishSpan.innerText = entry.english;
        termRow.appendChild(englishSpan);
        
        if (translationVal) {
            const transSpan = document.createElement("span");
            transSpan.className = "item-translation";
            transSpan.innerText = translationVal;
            termRow.appendChild(transSpan);
        }
        
        itemDiv.appendChild(termRow);
        
        if (entry.description) {
            const descDiv = document.createElement("div");
            descDiv.className = "item-desc";
            descDiv.innerText = entry.description;
            itemDiv.appendChild(descDiv);
        }
        
        listDiv.appendChild(itemDiv);
    });
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function applyHTMLHighlight(text, matchLanguage, targetLang) {
    if (!text || !glossaryTerms || glossaryTerms.length === 0) return text;
    
    const terms = [];
    const termToEntryMap = new Map();
    
    glossaryTerms.forEach(entry => {
        let termVal = "";
        if (matchLanguage.toLowerCase() === "english") {
            termVal = entry.english;
        } else {
            const trans = entry.translations || {};
            const key = Object.keys(trans).find(k => k.toLowerCase() === matchLanguage.toLowerCase());
            if (key) {
                termVal = trans[key];
            }
        }
        
        if (termVal && termVal.trim()) {
            const cleanTerm = termVal.trim();
            terms.push(cleanTerm);
            termToEntryMap.set(cleanTerm.toLowerCase(), entry);
        }
    });
    
    if (terms.length === 0) return text;
    
    // Sort terms descending by length to handle multi-word compound phrases first
    const sortedTerms = Array.from(new Set(terms)).sort((a, b) => b.length - a.length);
    const escapedTerms = sortedTerms.map(t => escapeRegExp(t));
    const patternStr = "(?<!\\p{L})(" + escapedTerms.join("|") + ")(?!\\p{L})";
    const regex = new RegExp(patternStr, "gui");
    
    return text.replace(regex, (matched) => {
        const entry = termToEntryMap.get(matched.toLowerCase());
        if (entry) {
            const englishTerm = entry.english || "";
            const translations = entry.translations || {};
            const transKey = Object.keys(translations).find(k => k.toLowerCase() === targetLang.toLowerCase());
            const translationVal = transKey ? translations[transKey] : "";
            const desc = entry.description || "";
            
            console.log(`[Glossary Match] Matched term: "${matched}" -> English: "${englishTerm}"${translationVal ? ` (Translation: "${translationVal}")` : ""}`);
            
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
    }
}

presetSelector.addEventListener("change", updatePresetUI);

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

// Initialize on page load
updatePresetUI();

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
    // This allows contiguous stitching for minor network jitters under 150ms.
    const JITTER_THRESHOLD = 0.15;      // 150ms safety window
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
    
    // If a new original turn starts, reset the bubble reference
    if (eventType === "original") {
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
            transSpan = document.createElement("div");
            transSpan.classList.add("translation-text");
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
    
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    socket = new WebSocket(wsUrl);
    
    // Update connection statuses
    headerPulse.className = "pulse-indicator status-connecting";
    connectionText.innerText = "Connecting...";
    startBtn.disabled = true;
    presetSelector.disabled = true;
    pacingSelector.disabled = true;
    if (pauseInput) pauseInput.disabled = true;
    resetBtn.disabled = true;
    nextBtn.disabled = true;
    nextBtn.classList.remove("waiting-pulse");
    
    socket.onopen = () => {
        logger("WebSocket connection established. Initializing preset...");
        // Send initial starting instruction with selected preset, pacing mode, and pause/timeout
        socket.send(JSON.stringify({
            action: "start",
            preset: presetSelector.value,
            pacing: pacingSelector.value,
            pause: pauseInput ? parseFloat(pauseInput.value) : 0,
            timeout: pauseInput ? parseFloat(pauseInput.value) : 0
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
                    
                case "waiting_for_next":
                    logger(`Backend waiting for manual 'Next' trigger after ${msg.speaker}'s turn.`);
                    // Set active visual state on the card that just finished to highlight the completed turn
                    if (msg.speaker === "patient") {
                        patientStatus.innerText = "Waiting for Next...";
                        patientCard.classList.add("active-speaker");
                    } else {
                        nurseStatus.innerText = "Waiting for Next...";
                        nurseCard.classList.add("active-speaker");
                    }
                    nextBtn.disabled = false;
                    nextBtn.classList.add("waiting-pulse");
                    nextBtn.focus();
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
    pacingSelector.disabled = false;
    if (pauseInput) pauseInput.disabled = false;
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
    nextBtn.disabled = true;
    nextBtn.classList.remove("waiting-pulse");
    
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

nextBtn.addEventListener("click", () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
        logger("Sending manual next_turn signal to server.");
        socket.send(JSON.stringify({ action: "next_turn" }));
    }
    nextBtn.disabled = true;
    nextBtn.classList.remove("waiting-pulse");
    
    // Reset status labels
    if (patientStatus.innerText.includes("Waiting")) {
        patientStatus.innerText = "Listening";
        patientCard.classList.remove("active-speaker");
    }
    if (nurseStatus.innerText.includes("Waiting")) {
        nurseStatus.innerText = "Listening";
        nurseCard.classList.remove("active-speaker");
    }
});

// Spacebar global keyboard shortcut for Manual Next Turn
window.addEventListener("keydown", (e) => {
    if (e.code === "Space") {
        if (nextBtn && !nextBtn.disabled) {
            e.preventDefault(); // Prevent page scrolling
            logger("Spacebar pressed. Triggering manual Next Turn.");
            nextBtn.click();
        }
    }
});

resetBtn.addEventListener("click", () => {
    logger("Resetting call UI and conversation state.");
    chatFeed.innerHTML = `
        <div class="system-message" id="welcome-message">
            Select a consultation scenario above and click "Start Call" to begin the real-time AI interpreter demo.
        </div>
    `;
    
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

