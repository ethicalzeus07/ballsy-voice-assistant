/**
 * Complete Voice Assistant with Speech Recognition AND Speech Synthesis
 * Now with Ballsy personality and voice responses
 *
 * This version uses “one‐shot” (non‐continuous) recognition, so it only fires
 * a single final result when you stop speaking. It no longer auto‐restarts itself.
 */


// Configuration
const SPEECH_TIMEOUT = 10000; // (not actively used)
// Remove the global click debounce - this was preventing multiple users from using the system
// const CLICK_DEBOUNCE = 2000;  // 2 seconds between orb clicks

// Determine API and WebSocket endpoints dynamically for local, Render, and Vercel.
const backendOrigin = (window.BALLSY_BACKEND_URL || window.location.origin).replace(/\/$/, '');
const API_BASE_URL = backendOrigin;
const backendUrl = new URL(backendOrigin);
const WS_BASE_URL = backendUrl.protocol === "https:"
    ? "wss://" + backendUrl.host
    : "ws://"  + backendUrl.host;

// State - Make these per-user instead of global
let speechRecognition      = null;
let speechSynthesis        = window.speechSynthesis;
let isListening            = false;
let isInitializing         = false;
let isSpeaking             = false;
let isProcessing           = false;  // Track if a request is in progress
let speechTimeout          = null;
// Remove global lastClickTime - this was causing conflicts between users
// let lastClickTime          = 0;
let clickHandlerAttached   = false;

// Voice settings (matching your backend defaults)
let voiceSettings = {
    voice: 'Jamie(Premium)',
    rate:  0.95,
    pitch: 0.98,
    volume:1.0
};


/**
 * Initialize text-to-speech
 * Loads and caches available voices.
 */
function initTextToSpeech() {
    if (!speechSynthesis) {
        console.warn('❌ Text-to-speech not supported');
        return false;
    }

    // Load voices; Chrome may load them asynchronously
    let voices = speechSynthesis.getVoices();
    if (voices.length === 0) {
        speechSynthesis.onvoiceschanged = () => {
            voices = speechSynthesis.getVoices();
            console.log('🔊 Voices loaded:', voices.length);
        };
    } else {
        console.log('🔊 Voices already available:', voices.length);
    }

    console.log('🔊 Text-to-speech initialized');
    return true;
}


/**
 * Play backend TTS audio from a base64-encoded payload.
 * @param {string} audioBase64 - Base64-encoded audio data
 */
function playGeminiAudio(audioBase64) {
    try {
        // Decode base64 audio and infer MIME from common file signatures.
        const audioBytes = Uint8Array.from(atob(audioBase64), c => c.charCodeAt(0));
        const mimeType = audioBase64.startsWith('UklG') ? 'audio/wav' : 'audio/mpeg';
        const blob = new Blob([audioBytes], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        
        isSpeaking = true;
        isProcessing = true;  // Keep processing flag until audio finishes
        updateUIStateFallback('speaking');
        
        audio.onended = () => {
            console.log('🔊 Finished playing backend TTS audio');
            URL.revokeObjectURL(url);
            isSpeaking = false;
            isProcessing = false;
            updateUIStateFallback('idle');
        };
        
        audio.onerror = (err) => {
            console.error('❌ Error playing backend TTS audio:', err);
            URL.revokeObjectURL(url);
            isSpeaking = false;
            isProcessing = false;
            updateUIStateFallback('idle');
            // Fallback to browser TTS
            const lastMessage = document.querySelector('.assistant-message:last-child');
            if (lastMessage && lastMessage.textContent) {
                speakText(lastMessage.textContent);
            }
        };
        
        audio.play();
        console.log(`🔊 Started playing backend TTS audio (${mimeType})`);
        
    } catch (error) {
        console.error('❌ Error playing backend TTS audio, falling back to browser TTS:', error);
        isProcessing = false;
        // Fallback to browser TTS if audio playback fails
        const lastMessage = document.querySelector('.assistant-message:last-child');
        if (lastMessage && lastMessage.textContent) {
            speakText(lastMessage.textContent);
        } else if (window.appState && window.appState.lastResponse) {
            speakText(window.appState.lastResponse);
        }
    }
}

/**
 * Speak text using browser's text-to-speech API
 */
function speakText(text) {
    if (!speechSynthesis || isSpeaking) {
        console.log('Speech synthesis not available or already speaking');
        return;
    }

    // Cancel any ongoing speech
    speechSynthesis.cancel();

    // Create utterance
    const utterance = new SpeechSynthesisUtterance(text);

    // Select a voice (prefer “Daniel” if available)
    const voices = speechSynthesis.getVoices();
    const voice = voices.find(v => v.name.includes('Jamie')) ||
                  voices.find(v => v.name.includes('Male'))    ||
                  voices.find(v => v.lang.startsWith('en-'))  ||
                  voices[0];

    if (voice) {
        utterance.voice = voice;
    }
    utterance.rate   = voiceSettings.rate;
    utterance.pitch  = voiceSettings.pitch;
    utterance.volume = voiceSettings.volume;

    // Event handlers
    utterance.onstart = () => {
        console.log('🔊 Started speaking:', text);
        isSpeaking = true;
        updateUIStateFallback('speaking');
    };
    utterance.onend = () => {
        console.log('🔊 Finished speaking');
        isSpeaking = false;
        isProcessing = false;  // Clear processing flag
        updateUIStateFallback('idle');
    };
    utterance.onerror = (event) => {
        console.error('🔊 Speech error:', event.error);
        isSpeaking = false;
        isProcessing = false;  // Clear processing flag
        updateUIStateFallback('idle');
    };

    // Speak
    speechSynthesis.speak(utterance);
}


/**
 * Initialize browser speech recognition
 * Uses one-shot (non-continuous) mode so it only fires once per spoken phrase.
 */
function initSpeechRecognition() {
    if (speechRecognition) {
        console.log('🎤 Speech recognition already initialized');
        return true;
    }

    console.log('🎤 Initializing speech recognition...');

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.error('❌ Speech recognition not supported');
        return false;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    speechRecognition = new SpeechRecognition();

    // CONFIGURE for one-shot recognition:
    speechRecognition.continuous      = false;  // listen once, then end
    speechRecognition.interimResults  = false;  // only final result
    speechRecognition.lang            = 'en-US';
    speechRecognition.maxAlternatives = 1;

    // When recognition starts:
    speechRecognition.onstart = function() {
        console.log('🎤 Speech recognition started (one-shot)');
        isListening    = true;
        isInitializing = false;
        updateUIStateFallback('listening');
    };

    // Only one final result will fire when you pause:
    speechRecognition.onresult = function(event) {
        // event.results[0][0] is the full transcript of your speech until pause
        const transcript = event.results[0][0].transcript.trim();
        console.log('🎯 Full transcript:', transcript);

        // Send the entire phrase as a command immediately
        addMessageToConversationFallback('user', transcript);
        // sendCommandFallback will set processing state itself
        sendCommandFallback(transcript);
    };

    speechRecognition.onerror = function(event) {
        console.error('❌ Speech recognition error:', event.error);
        isListening    = false;
        isInitializing = false;

        let message = 'I couldn\'t start listening. Please try again.';
        switch (event.error) {
            case 'no-speech':
                message = 'I didn\'t hear anything. Please try again.';
                break;
            case 'audio-capture':
                message = 'Microphone access denied. Please allow microphone access.';
                break;
            case 'not-allowed':
                message = 'Microphone permission required. Please allow and refresh the page.';
                break;
            case 'network':
                message = 'Network error. Please check your internet connection.';
                break;
            case 'aborted':
                console.log('Speech recognition aborted by user');
                updateUIStateFallback('idle');
                return;
        }

        addMessageToConversationFallback('assistant', message);
        speakText(message);
        updateUIStateFallback('idle');
    };

    // When recognition ends (either after onresult or error), do NOT restart automatically
    speechRecognition.onend = function() {
        console.log('🛑 Speech recognition ended (one-shot).');
        isListening    = false;
        isInitializing = false;
        updateUIStateFallback('idle');

        // We removed the automatic restart here so Ballsy stops until user clicks again.
        // If you ever want to re-enable continuous listening, uncomment the next line:
        // speechRecognition.start();
    };

    console.log('✅ Speech recognition initialized successfully');
    return true;
}


/**
 * Start listening with proper state management
 */
async function startListening() {
    console.log('🎤 startListening (one-shot) called');

    // If currently speaking, cancel that
    if (isSpeaking) {
        speechSynthesis.cancel();
        isSpeaking = false;
    }

    // Already listening or initializing?
    if (isListening || isInitializing) {
        console.log('⚠️ Already listening or initializing');
        return;
    }

    // Initialize if needed
    if (!speechRecognition && !initSpeechRecognition()) {
        console.log('❌ Could not initialize speech recognition');
        return;
    }

    try {
        isInitializing = true;
        console.log('🎯 Starting speech recognition...');
        speechRecognition.start();
    } catch (error) {
        console.error('❌ Error starting speech recognition:', error);
        isInitializing = false;
        isListening    = false;
        const errorMsg = 'I couldn\'t start listening. Please try again.';
        addMessageToConversationFallback('assistant', errorMsg);
        speakText(errorMsg);
        updateUIStateFallback('idle');
    }
}


/**
 * Stop listening
 */
function stopListening() {
    console.log('🛑 stopListening called');

    if (speechRecognition && (isListening || isInitializing)) {
        try {
            speechRecognition.stop();
        } catch (error) {
            console.error('Error stopping speech recognition:', error);
        }
    }

    clearTimeout(speechTimeout);
    isListening    = false;
    isInitializing = false;
    updateUIStateFallback('idle');
}


/**
 * Send command to backend
 * Uses dynamic API_BASE_URL instead of hardcoded localhost
 */
async function sendCommandFallback(command) {
    console.log('📤 Sending command to Ballsy:', command);

    // Prevent concurrent requests - block if already processing
    if (isProcessing) {
        console.warn('⚠️ Request already in progress, ignoring duplicate command');
        return;
    }

    // Set processing state BEFORE sending
    isProcessing = true;
    updateUIStateFallback('processing');

    try {
        // Generate or get user ID for this session
        // Backend expects numeric user_id; use a stable numeric ID for this client
        const userId = 1;
        
        const response = await fetch(`${API_BASE_URL}/api/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                command: command,
                user_id: userId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        console.log('✅ Ballsy response:', data);

        // Display Ballsy's response in the conversation UI
        addMessageToConversationFallback('assistant', data.response);

        console.log('🎤 Using browser Web Speech TTS');
        speakText(data.response);

        // Handle “open_url” action if provided
        if (data.action === 'open_url' && data.data?.url) {
            window.open(data.data.url, '_blank');
        }

        // No need to force‐stop or restart recognition here—
        // onend will take over once speakText finishes.

    } catch (error) {
        console.error('❌ Error sending command:', error);
        const errorMsg = 'Sorry, I had an error. Please try again.';
        addMessageToConversationFallback('assistant', errorMsg);
        speakText(errorMsg);
        updateUIStateFallback('idle');
    }
}


/**
 * Add message to conversation UI (fallback)
 * If main appFunctions.addMessageToConversation is available, use that; otherwise, manually append.
 */
function addMessageToConversationFallback(sender, text) {
    console.log(`💬 ${sender}: ${text}`);

    if (window.appFunctions && window.appFunctions.addMessageToConversation) {
        window.appFunctions.addMessageToConversation(sender, text);
        return;
    }

    const conversationHistory = document.getElementById('conversation-history');
    if (conversationHistory) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        messageElement.textContent = text;
        conversationHistory.appendChild(messageElement);
        conversationHistory.scrollTop = conversationHistory.scrollHeight;
    }
}


/**
 * Update UI state (fallback)
 * Tries window.appFunctions.updateUIState first; otherwise, updates the orb/status manually.
 */
function updateUIStateFallback(state) {
    console.log('🎨 UI state:', state);

    if (window.appFunctions && window.appFunctions.updateUIState) {
        window.appFunctions.updateUIState(state);
        return;
    }

    const voiceOrb = document.querySelector('.voice-orb');
    if (voiceOrb) {
        voiceOrb.classList.remove('idle', 'listening', 'processing', 'speaking', 'error');
        voiceOrb.classList.add(state);
    }

    const statusText = document.getElementById('status-text');
    if (statusText) {
        switch (state) {
            case 'idle':
                statusText.textContent = 'Click to activate';
                break;
            case 'listening':
                statusText.textContent = 'Listening...';
                break;
            case 'processing':
                statusText.textContent = 'Processing...';
                break;
            case 'speaking':
                statusText.textContent = 'Speaking...';
                break;
            case 'error':
                statusText.textContent = 'Error occurred';
                break;
        }
    }
}


/**
 * Setup click handler for the voice orb
 */
function setupVoiceOrbClickHandler() {
    if (clickHandlerAttached) {
        console.log('Click handler already attached');
        return;
    }

    const voiceOrb = document.querySelector('.voice-orb');
    if (!voiceOrb) {
        console.log('Voice orb not found');
        return;
    }

    // Remove any existing listeners
    voiceOrb.removeEventListener('click', handleVoiceOrbClick);

    // Add new listener
    voiceOrb.addEventListener('click', handleVoiceOrbClick, { passive: true });
    clickHandlerAttached = true;

    console.log('✅ Ballsy voice orb click handler attached');
}


/**
 * Handle voice orb click
 * Toggling between listening, speaking, and idle states
 */
function handleVoiceOrbClick(event) {
    event.preventDefault();
    event.stopPropagation();

    console.log('🎤 Ballsy voice orb clicked');

    if (isListening || isInitializing) {
        console.log('Stopping current listening session');
        stopListening();
    } else if (isSpeaking) {
        console.log('Stopping speech synthesis');
        speechSynthesis.cancel();
        isSpeaking = false;
        updateUIStateFallback('idle');
    } else {
        console.log('Starting new listening session');
        startListening();
    }
}


// Expose key functions globally so other scripts (app.js, ui.js) can call them
window.voiceFunctions = {
    startListening,
    stopListening,
    speakText,
    playGeminiAudio,
    initSpeechRecognition,
    initTextToSpeech,
    setupVoiceOrbClickHandler
};

window.startListening = startListening;
window.stopListening  = stopListening;
window.speakText      = speakText;
window.playGeminiAudio = playGeminiAudio;
window.isProcessing = false;  // Expose for checking in sendMessage


// ──────────────────────────────────────────────────────────────────────────────

console.log('🎤 Ballsy Voice Assistant (voice.js) loaded successfully');

// Initialize speech recognition and synthesis when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎤 DOM ready - initializing Ballsy voice features');

    initSpeechRecognition();
    initTextToSpeech();

    // Attach click handler to the orb after a short delay (allow DOM to settle)
    setTimeout(() => {
        setupVoiceOrbClickHandler();
    }, 500);

    // Keep the Ballsy product name if legacy markup is loaded.
    const title = document.querySelector('h1');
    if (title && title.textContent.includes('Voice Assistant')) {
        title.textContent = 'Ballsy';
    }
});

console.log('🎤 Ballsy Voice Assistant script initialization complete');
