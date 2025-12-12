/**
 * Main application script for the Voice Assistant
 * Handles core functionality, API communication, and state management
 */

// Configuration - use the current origin so deployed environments work
const appApiBaseUrl = typeof API_BASE_URL !== 'undefined'
    ? API_BASE_URL
    : window.location.origin;
const appWsBaseUrl = window.location.protocol === 'https:'
    ? `wss://${window.location.host}`
    : `ws://${window.location.host}`;

// Backend expects numeric user_id; use a stable numeric ID (1) for this client
const DEFAULT_USER_ID = 1;

// Application state
const appState = {
    isListening: false,
    isProcessing: false,
    isSpeaking: false,
    webSocket: null,
    currentUserId: DEFAULT_USER_ID,
    settings: {
        voice: 'Daniel',
        voiceSpeed: 180,
        theme: 'light',
        accentColor: 'blue',
        sensitivity: 5,
        autoListen: true
    },
    conversation: []
};

// DOM Elements
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the application
    initApp();
});

/**
 * Initialize the application
 */
async function initApp() {
    // Load user settings
    await loadSettings();
    
    // Apply theme and accent color
    applyTheme();
    
    // Initialize WebSocket connection
    initWebSocket();
    
    // Initialize UI event listeners
    initUIListeners();
    
    // Load conversation history
    //await loadConversationHistory();
    
    // Set initial UI state
    updateUIState('idle');
    
    console.log('Voice Assistant initialized');
}

/**
 * Initialize WebSocket connection
 */
function initWebSocket() {
    // Close existing connection if any
    if (appState.webSocket) {
        appState.webSocket.close();
    }
    
    // Create new WebSocket connection
    appState.webSocket = new WebSocket(`${appWsBaseUrl}/ws/voice/${appState.currentUserId}`);
    
    // WebSocket event handlers
    appState.webSocket.onopen = () => {
        console.log('WebSocket connection established');
        // Send ready status
        appState.webSocket.send(JSON.stringify({
            status: 'listening'
        }));
    };
    
    appState.webSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    appState.webSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateUIState('error');
    };
    
    appState.webSocket.onclose = () => {
        console.log('WebSocket connection closed');
        // Attempt to reconnect after a delay
        setTimeout(() => {
            if (document.visibilityState === 'visible') {
                initWebSocket();
            }
        }, 3000);
    };
}

/**
 * Handle incoming WebSocket messages
 * @param {Object} data - The message data
 */
function handleWebSocketMessage(data) {
    console.log('WebSocket message received:', data);
    
    switch (data.type) {
        case 'status_update':
            // Handle status updates
            if (data.status === 'ready') {
                updateUIState('idle');
            }
            break;
            
        case 'command_response':
            // Handle command responses
            handleCommandResponse(data.data);
            break;
            
        case 'error':
            // Handle errors
            console.error('Server error:', data.message);
            updateUIState('error');
            addMessageToConversation('assistant', 'Sorry, I encountered an error. Please try again.');
            break;
            
        default:
            console.warn('Unknown message type:', data.type);
    }
}

/**
 * Handle command response from the server
 * @param {Object} response - The command response
 */
function handleCommandResponse(response) {
    // Add assistant response to conversation
    addMessageToConversation('assistant', response.response);
    
    // Update UI state
    updateUIState('speaking');
    
    // Speak the response
    speakText(response.response);
    
    // Handle any actions
    if (response.action) {
        handleResponseAction(response.action, response.data);
    }
    
    // Return to idle state after speaking
    setTimeout(() => {
        updateUIState('idle');
        
        // Auto-listen if enabled
        if (appState.settings.autoListen) {
            setTimeout(() => {
                startListening();
            }, 1000);
        }
    }, calculateSpeakingDuration(response.response));
}

/**
 * Handle response actions
 * @param {string} action - The action to perform
 * @param {Object} data - The action data
 */
function handleResponseAction(action, data) {
    switch (action) {
        case 'open_url':
            // Open URL in a new tab
            window.open(data.url, '_blank');
            break;
            
        case 'search':
            // Perform a search
            const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(data.query)}`;
            window.open(searchUrl, '_blank');
            break;
            
        case 'open_app':
            // Display message that this is a web app and can't open native apps
            addMessageToConversation('assistant', `This is a web application and cannot open native apps like ${data.app_name}. You would need to use the desktop version for this functionality.`);
            break;
            
        case 'exit':
            // Handle exit command
            addMessageToConversation('assistant', 'Goodbye! Refresh the page to restart the assistant.');
            break;
            
        default:
            console.warn('Unknown action:', action);
    }
}

/**
 * Send a command to the server
 * @param {string} command - The command text
 */
async function sendCommand(command) {
    // Add user message to conversation
    addMessageToConversation('user', command);
    
    // Update UI state
    updateUIState('processing');
    
    try {
        // Try WebSocket first if connected
        if (appState.webSocket && appState.webSocket.readyState === WebSocket.OPEN) {
            appState.webSocket.send(JSON.stringify({
                command: command
            }));
        } else {
            // Fall back to REST API
            const response = await fetch(`${appApiBaseUrl}/api/command`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    command: command,
                    user_id: appState.currentUserId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            handleCommandResponse(data);
        }
    } catch (error) {
        console.error('Error sending command:', error);
        updateUIState('error');
        addMessageToConversation('assistant', 'Sorry, I encountered an error. Please try again.');
        
        // Return to idle state after a delay
        setTimeout(() => {
            updateUIState('idle');
        }, 2000);
    }
}

/**
 * Send audio data to the server
 * @param {Blob} audioBlob - The audio data
 */
async function sendAudioData(audioBlob) {
    // Update UI state
    updateUIState('processing');
    
    try {
        // Create form data
        const formData = new FormData();
        formData.append('file', audioBlob, 'voice.wav');
        formData.append('user_id', appState.currentUserId);
        
        // Send to server
        const response = await fetch(`${appApiBaseUrl}/api/voice`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        handleCommandResponse(data);
    } catch (error) {
        console.error('Error sending audio data:', error);
        updateUIState('error');
        addMessageToConversation('assistant', 'Sorry, I encountered an error processing your voice. Please try again.');
        
        // Return to idle state after a delay
        setTimeout(() => {
            updateUIState('idle');
        }, 2000);
    }
}

/**
 * Add a message to the conversation
 * @param {string} sender - 'user' or 'assistant'
 * @param {string} text - The message text
 */
function addMessageToConversation(sender, text) {
    // Add to state
    appState.conversation.push({
        sender,
        text,
        timestamp: new Date().toISOString()
    });
    
    // Add to UI
    const conversationHistory = document.getElementById('conversation-history');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.classList.add(`${sender}-message`);
    messageElement.textContent = text;
    conversationHistory.appendChild(messageElement);
    
    // Scroll to bottom
    scrollToBottom();
}

/**
 * Load conversation history from the server
 */
async function loadConversationHistory() {
    try {
        const response = await fetch(`${appApiBaseUrl}/api/history/${appState.currentUserId}?limit=10`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Clear existing conversation
        appState.conversation = [];
        const conversationHistory = document.getElementById('conversation-history');
        conversationHistory.innerHTML = '';
        
        // Add messages to conversation
        data.history.forEach(item => {
            const sender = item.is_user ? 'user' : 'assistant';
            addMessageToConversation(sender, item.content);
        });
    } catch (error) {
        console.error('Error loading conversation history:', error);
        // Continue without history
    }
}

/**
 * Load user settings from the server
 */
async function loadSettings() {
    try {
        const response = await fetch(`${appApiBaseUrl}/api/settings/${appState.currentUserId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update settings
        appState.settings.voice = data.settings.voice || 'Daniel';
        appState.settings.voiceSpeed = data.settings.voice_speed || 180;
        appState.settings.theme = data.settings.theme || 'light';
        
        // Update UI
        document.getElementById('voice-select').value = appState.settings.voice;
        document.getElementById('voice-speed').value = appState.settings.voiceSpeed;
        document.getElementById('voice-speed-value').textContent = appState.settings.voiceSpeed;
        document.getElementById('theme-select').value = appState.settings.theme;
    } catch (error) {
        console.error('Error loading settings:', error);
        // Continue with default settings
    }
}

/**
 * Save user settings to the server
 */
async function saveSettings() {
    try {
        const response = await fetch(`${appApiBaseUrl}/api/settings/${appState.currentUserId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                voice: appState.settings.voice,
                voice_speed: appState.settings.voiceSpeed,
                theme: appState.settings.theme
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        // Apply settings
        applyTheme();
        
        // Show success message
        addMessageToConversation('assistant', 'Settings saved successfully.');
    } catch (error) {
        console.error('Error saving settings:', error);
        addMessageToConversation('assistant', 'Failed to save settings. Please try again.');
    }
}

/**
 * Apply theme and accent color
 */
function applyTheme() {
    // Apply theme
    if (appState.settings.theme === 'dark' || 
        (appState.settings.theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.body.classList.add('dark-theme');
    } else {
        document.body.classList.remove('dark-theme');
    }
    
    // Apply accent color
    document.body.classList.remove('accent-blue', 'accent-purple', 'accent-green', 'accent-orange');
    document.body.classList.add(`accent-${appState.settings.accentColor}`);
}

/**
 * Update UI state
 * @param {string} state - The new state ('idle', 'listening', 'processing', 'speaking', 'error')
 */
function updateUIState(state) {
    // Update state
    appState.isListening = state === 'listening';
    appState.isProcessing = state === 'processing';
    appState.isSpeaking = state === 'speaking';
    
    // Update voice orb
    const voiceOrb = document.querySelector('.voice-orb');
    voiceOrb.classList.remove('idle', 'listening', 'processing', 'speaking', 'error');
    voiceOrb.classList.add(state);
    
    // Update status text
    const statusText = document.getElementById('status-text');
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
    
    // Update buttons
    const activateButton = document.getElementById('activate-button');
    const stopButton = document.getElementById('stop-button');
    
    if (state === 'listening' || state === 'processing') {
        activateButton.classList.add('hidden');
        stopButton.classList.remove('hidden');
    } else {
        activateButton.classList.remove('hidden');
        stopButton.classList.add('hidden');
    }
}

/**
 * Calculate speaking duration based on text length
 * @param {string} text - The text to speak
 * @returns {number} - Duration in milliseconds
 */
function calculateSpeakingDuration(text) {
    // Average speaking rate is about 150 words per minute
    // So each word takes about 400ms
    const words = text.split(' ').length;
    return Math.max(1500, words * 400);
}

/**
 * Speak text using the Web Speech API
 * @param {string} text - The text to speak
 */
function speakText(text) {
    // Check if speech synthesis is available
    if (!('speechSynthesis' in window)) {
        console.warn('Speech synthesis not supported');
        return;
    }
    
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    
    // Create utterance
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Set voice
    const voices = window.speechSynthesis.getVoices();
    const voice = voices.find(v => v.name === appState.settings.voice) || 
                 voices.find(v => v.lang.startsWith('en-')) || 
                 voices[0];
    
    if (voice) {
        utterance.voice = voice;
    }
    
    // Set rate (convert from 120-250 range to 0.5-1.5 range)
    const normalizedRate = (appState.settings.voiceSpeed - 120) / (250 - 120);
    utterance.rate = 0.5 + normalizedRate;
    
    // Speak
    window.speechSynthesis.speak(utterance);
}

// Export functions for use in other modules
window.appFunctions = {
    sendCommand,
    sendAudioData,
    startListening,
    stopListening,
    updateUIState,
    addMessageToConversation,
    saveSettings
};

/**
 * Helper: Scroll the chat to the bottom
 */
function scrollToBottom() {
    const conversationHistory = document.getElementById('conversation-history');
    if (conversationHistory) {
        // Wait a tiny bit so the new message finishes rendering,
        // then scroll to the very bottom.
        setTimeout(() => {
            conversationHistory.scrollTop = conversationHistory.scrollHeight;
        }, 50);
    }
}
