/**
 * Complete Voice Assistant with Speech Recognition AND Speech Synthesis
 * Now with "Ballsy" personality and voice responses
 */

// Configuration
const SPEECH_TIMEOUT = 10000; // 10 seconds max
const CLICK_DEBOUNCE = 2000; // 2 seconds between clicks

// State
let speechRecognition = null;
let speechSynthesis = window.speechSynthesis;
let isListening = false;
let isInitializing = false;
let isSpeaking = false;
let speechTimeout = null;
let lastClickTime = 0;
let clickHandlerAttached = false;

// Voice settings (matching your main.py)
let voiceSettings = {
    voice: 'Daniel',
    rate: 1.0,
    pitch: 1.0,
    volume: 1.0
};

/**
 * Initialize text-to-speech
 */
function initTextToSpeech() {
    if (!speechSynthesis) {
        console.warn('❌ Text-to-speech not supported');
        return false;
    }
    
    // Load voices
    let voices = speechSynthesis.getVoices();
    
    // If voices not loaded yet, wait for them
    if (voices.length === 0) {
        speechSynthesis.onvoiceschanged = () => {
            voices = speechSynthesis.getVoices();
            console.log('🔊 Voices loaded:', voices.length);
        };
    }
    
    console.log('🔊 Text-to-speech initialized');
    return true;
}

/**
 * Speak text using browser's text-to-speech
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
    
    // Configure voice
    const voices = speechSynthesis.getVoices();
    const voice = voices.find(v => v.name.includes('Daniel')) || 
                 voices.find(v => v.name.includes('Male')) ||
                 voices.find(v => v.lang.startsWith('en-')) || 
                 voices[0];
    
    if (voice) {
        utterance.voice = voice;
    }
    
    utterance.rate = voiceSettings.rate;
    utterance.pitch = voiceSettings.pitch;
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
        updateUIStateFallback('idle');
    };
    
    utterance.onerror = (event) => {
        console.error('🔊 Speech error:', event.error);
        isSpeaking = false;
        updateUIStateFallback('idle');
    };
    
    // Speak
    speechSynthesis.speak(utterance);
}

/**
 * Initialize browser speech recognition
 */
function initSpeechRecognition() {
    if (speechRecognition) {
        console.log('🎤 Speech recognition already initialized');
        return true;
    }
    
    console.log('🎤 Initializing speech recognition...');
    
    // Check if browser supports speech recognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.error('❌ Speech recognition not supported');
        return false;
    }
    
    // Create speech recognition instance
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    speechRecognition = new SpeechRecognition();
    
    // Configure speech recognition
    speechRecognition.continuous = false;
    speechRecognition.interimResults = false;
    speechRecognition.lang = 'en-US';
    speechRecognition.maxAlternatives = 1;
    
    // Event handlers
    speechRecognition.onstart = function() {
        console.log('🎤 Speech recognition started successfully');
        isListening = true;
        isInitializing = false;
        updateUIStateFallback('listening');
    };
    
    speechRecognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript.trim();
        console.log('🎯 Speech recognized:', transcript);
        
        if (transcript) {
            // Add user message to conversation
            addMessageToConversationFallback('user', transcript);
            
            // Update UI to processing
            updateUIStateFallback('processing');
            
            // Send command to backend
            setTimeout(() => {
                sendCommandFallback(transcript);
            }, 200);
        }
    };
    
    speechRecognition.onerror = function(event) {
        console.error('❌ Speech recognition error:', event.error);
        isListening = false;
        isInitializing = false;
        
        let message = 'I couldn\'t start listening. Please try again.';
        
        switch(event.error) {
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
        speakText(message); // Speak the error message
        updateUIStateFallback('idle');
    };
    
    speechRecognition.onend = function() {
        console.log('🛑 Speech recognition ended');
        isListening = false;
        isInitializing = false;
        clearTimeout(speechTimeout);
        updateUIStateFallback('idle');
    };
    
    console.log('✅ Speech recognition initialized successfully');
    return true;
}

/**
 * Start listening with proper state management
 */
async function startListening() {
    const now = Date.now();
    
    // Debounce clicks
    if (now - lastClickTime < CLICK_DEBOUNCE) {
        console.log('⚠️ Click debounced, too soon');
        return;
    }
    lastClickTime = now;
    
    console.log('🎤 startListening called');
    
    // Stop any ongoing speech
    if (isSpeaking) {
        speechSynthesis.cancel();
        isSpeaking = false;
    }
    
    // Check current state
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
        
        // Set timeout
        speechTimeout = setTimeout(() => {
            if (isListening || isInitializing) {
                console.log('⏰ Speech timeout');
                stopListening();
            }
        }, SPEECH_TIMEOUT);
        
        // Start recognition
        speechRecognition.start();
        
    } catch (error) {
        console.error('❌ Error starting speech:', error);
        isInitializing = false;
        isListening = false;
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
    isListening = false;
    isInitializing = false;
    updateUIStateFallback('idle');
}

/**
 * Send command to backend (now with Ballsy personality)
 */
async function sendCommandFallback(command) {
    console.log('📤 Sending command to Ballsy:', command);
    
    try {
        const response = await fetch('http://localhost:8000/api/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                command: command,
                user_id: 1
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Ballsy response:', data);
        
        // Add response to conversation
        addMessageToConversationFallback('assistant', data.response);
        
        // SPEAK the response (this was missing!)
        speakText(data.response);
        
        // Handle actions
        if (data.action === 'open_url' && data.data?.url) {
            window.open(data.data.url, '_blank');
        }
        
        // Don't immediately return to idle - let speech finish
        
    } catch (error) {
        console.error('❌ Error sending command:', error);
        const errorMsg = 'Sorry, I had an error. Please try again.';
        addMessageToConversationFallback('assistant', errorMsg);
        speakText(errorMsg);
        updateUIStateFallback('idle');
    }
}

/**
 * Add message to conversation (fallback)
 */
function addMessageToConversationFallback(sender, text) {
    console.log(`💬 ${sender}: ${text}`);
    
    // Try main function first
    if (window.appFunctions && window.appFunctions.addMessageToConversation) {
        window.appFunctions.addMessageToConversation(sender, text);
        return;
    }
    
    // Fallback: add to conversation history
    const conversationHistory = document.getElementById('conversation-history');
    if (conversationHistory) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(`${sender}-message`);
        messageElement.textContent = text;
        conversationHistory.appendChild(messageElement);
        conversationHistory.scrollTop = conversationHistory.scrollHeight;
    }
}

/**
 * Update UI state (fallback)
 */
function updateUIStateFallback(state) {
    console.log('🎨 UI state:', state);
    
    // Try main function first
    if (window.appFunctions && window.appFunctions.updateUIState) {
        window.appFunctions.updateUIState(state);
        return;
    }
    
    // Fallback: update orb and status
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
 * Setup click handler for voice orb
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
 */
function handleVoiceOrbClick(event) {
    event.preventDefault();
    event.stopPropagation();
    
    console.log('🎤 Ballsy voice orb clicked');
    
    if (isListening || isInitializing) {
        console.log('Stopping current session');
        stopListening();
    } else if (isSpeaking) {
        console.log('Stopping speech');
        speechSynthesis.cancel();
        isSpeaking = false;
        updateUIStateFallback('idle');
    } else {
        console.log('Starting new session');
        startListening();
    }
}

// Make functions available globally
window.voiceFunctions = {
    startListening,
    stopListening,
    speakText,
    initSpeechRecognition,
    initTextToSpeech,
    setupVoiceOrbClickHandler
};

window.startListening = startListening;
window.stopListening = stopListening;
window.speakText = speakText;

console.log('🎤 Ballsy Voice Assistant loaded successfully');

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎤 DOM ready - initializing Ballsy');
    
    // Initialize speech recognition and synthesis
    initSpeechRecognition();
    initTextToSpeech();
    
    // Setup click handler after a short delay
    setTimeout(() => {
        setupVoiceOrbClickHandler();
    }, 500);
    
    // Update the title to show "Ballsy"
    const title = document.querySelector('h1');
    if (title && title.textContent.includes('Voice Assistant')) {
        title.textContent = 'Ballsy - Voice Assistant';
    }
});

console.log('🎤 Ballsy Voice Assistant script completed');