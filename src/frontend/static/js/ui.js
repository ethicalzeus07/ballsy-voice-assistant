/**
 * UI interaction module for the Voice Assistant
 * Handles UI events, animations, and user interactions
 */

// Initialize UI event listeners when the page loads
document.addEventListener('DOMContentLoaded', () => {
    initUIListeners();
});

/**
 * Initialize all UI event listeners
 */
function initUIListeners() {
    // Voice orb click
    const voiceOrb = document.querySelector('.voice-orb');
    voiceOrb.addEventListener('click', handleVoiceOrbClick);
    
    // Activate button
    const activateButton = document.getElementById('activate-button');
    activateButton.addEventListener('click', handleActivateButtonClick);
    
    // Stop button
    const stopButton = document.getElementById('stop-button');
    stopButton.addEventListener('click', handleStopButtonClick);
    
    // Text input button
    const textInputButton = document.getElementById('text-input-button');
    textInputButton.addEventListener('click', toggleTextInput);
    
    // Send text button
    const sendTextButton = document.getElementById('send-text-button');
    sendTextButton.addEventListener('click', handleSendTextButtonClick);
    
    // Text command input (for Enter key)
    const textCommandInput = document.getElementById('text-command');
    textCommandInput.addEventListener('keydown', handleTextCommandKeydown);
    
    // Settings button
    const settingsButton = document.querySelector('.settings-button');
    settingsButton.addEventListener('click', openSettings);
    
    // Close settings button
    const closeSettingsButton = document.getElementById('close-settings');
    closeSettingsButton.addEventListener('click', closeSettings);
    
    // Save settings button
    const saveSettingsButton = document.getElementById('save-settings');
    saveSettingsButton.addEventListener('click', handleSaveSettingsClick);
    
    // Reset settings button
    const resetSettingsButton = document.getElementById('reset-settings');
    resetSettingsButton.addEventListener('click', handleResetSettingsClick);
    
    // Voice speed slider
    const voiceSpeedSlider = document.getElementById('voice-speed');
    voiceSpeedSlider.addEventListener('input', handleVoiceSpeedChange);
    
    // Sensitivity slider
    const sensitivitySlider = document.getElementById('sensitivity-slider');
    sensitivitySlider.addEventListener('input', handleSensitivityChange);
    
    // Theme select
    const themeSelect = document.getElementById('theme-select');
    themeSelect.addEventListener('change', handleThemeChange);
    
    // Color select
    const colorSelect = document.getElementById('color-select');
    colorSelect.addEventListener('change', handleColorChange);
    
    // Voice select
    const voiceSelect = document.getElementById('voice-select');
    voiceSelect.addEventListener('change', handleVoiceChange);
    
    // Auto-listen checkbox
    const autoListenCheckbox = document.getElementById('auto-listen');
    autoListenCheckbox.addEventListener('change', handleAutoListenChange);
    
    // System theme change detection
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (window.appState && window.appState.settings.theme === 'system') {
            applyTheme();
        }
    });
    
    // Populate voice options
    populateVoiceOptions();
}

/**
 * Handle voice orb click
 */
function handleVoiceOrbClick() {
    if (!window.appState.isListening && !window.appState.isProcessing && !window.appState.isSpeaking) {
        window.voiceFunctions.startListening();
    } else if (window.appState.isListening) {
        window.voiceFunctions.stopListening();
    }
}

/**
 * Handle activate button click
 */
function handleActivateButtonClick() {
    if (!window.appState.isListening && !window.appState.isProcessing && !window.appState.isSpeaking) {
        window.voiceFunctions.startListening();
    }
}

/**
 * Handle stop button click
 */
function handleStopButtonClick() {
    if (window.appState.isListening) {
        window.voiceFunctions.stopListening();
    }
}

/**
 * Toggle text input visibility
 */
function toggleTextInput() {
    const textInputContainer = document.getElementById('text-input-container');
    textInputContainer.classList.toggle('hidden');
    
    if (!textInputContainer.classList.contains('hidden')) {
        document.getElementById('text-command').focus();
    }
}

/**
 * Handle send text button click
 */
function handleSendTextButtonClick() {
    const textCommandInput = document.getElementById('text-command');
    const command = textCommandInput.value.trim();
    
    if (command) {
        window.appFunctions.sendCommand(command);
        textCommandInput.value = '';
        
        // Hide text input after sending
        document.getElementById('text-input-container').classList.add('hidden');
    }
}

/**
 * Handle text command keydown (for Enter key)
 * @param {KeyboardEvent} event - The keydown event
 */
function handleTextCommandKeydown(event) {
    if (event.key === 'Enter') {
        handleSendTextButtonClick();
    }
}

/**
 * Open settings panel
 */
function openSettings() {
    document.getElementById('settings-panel').classList.remove('hidden');
}

/**
 * Close settings panel
 */
function closeSettings() {
    document.getElementById('settings-panel').classList.add('hidden');
}

/**
 * Handle save settings button click
 */
function handleSaveSettingsClick() {
    window.appFunctions.saveSettings();
    closeSettings();
}

/**
 * Handle reset settings button click
 */
function handleResetSettingsClick() {
    // Reset to defaults
    window.appState.settings = {
        voice: 'Daniel',
        voiceSpeed: 180,
        theme: 'light',
        accentColor: 'blue',
        sensitivity: 5,
        autoListen: true
    };
    
    // Update UI
    document.getElementById('voice-select').value = 'Daniel';
    document.getElementById('voice-speed').value = 180;
    document.getElementById('voice-speed-value').textContent = 180;
    document.getElementById('theme-select').value = 'light';
    document.getElementById('color-select').value = 'blue';
    document.getElementById('sensitivity-slider').value = 5;
    document.getElementById('sensitivity-value').textContent = 5;
    document.getElementById('auto-listen').checked = true;
    
    // Apply settings
    applyTheme();
    
    // Save to server
    window.appFunctions.saveSettings();
}

/**
 * Handle voice speed slider change
 */
function handleVoiceSpeedChange() {
    const value = document.getElementById('voice-speed').value;
    document.getElementById('voice-speed-value').textContent = value;
    window.appState.settings.voiceSpeed = parseInt(value);
}

/**
 * Handle sensitivity slider change
 */
function handleSensitivityChange() {
    const value = document.getElementById('sensitivity-slider').value;
    document.getElementById('sensitivity-value').textContent = value;
    window.appState.settings.sensitivity = parseInt(value);
    
    // Update silence threshold based on sensitivity
    // Higher sensitivity = lower threshold
    window.SILENCE_THRESHOLD = 0.02 - (parseInt(value) * 0.001);
}

/**
 * Handle theme select change
 */
function handleThemeChange() {
    const value = document.getElementById('theme-select').value;
    window.appState.settings.theme = value;
    applyTheme();
}

/**
 * Handle color select change
 */
function handleColorChange() {
    const value = document.getElementById('color-select').value;
    window.appState.settings.accentColor = value;
    applyTheme();
}

/**
 * Handle voice select change
 */
function handleVoiceChange() {
    const value = document.getElementById('voice-select').value;
    window.appState.settings.voice = value;
}

/**
 * Handle auto-listen checkbox change
 */
function handleAutoListenChange() {
    const checked = document.getElementById('auto-listen').checked;
    window.appState.settings.autoListen = checked;
}

/**
 * Populate voice options from available system voices
 */
function populateVoiceOptions() {
    if (!('speechSynthesis' in window)) {
        console.warn('Speech synthesis not supported');
        return;
    }
    
    // Function to populate the select
    const populateVoiceList = () => {
        const voices = window.speechSynthesis.getVoices();
        const voiceSelect = document.getElementById('voice-select');
        
        // Clear existing options
        voiceSelect.innerHTML = '';
        
        // Filter for English voices
        const englishVoices = voices.filter(voice => voice.lang.startsWith('en-'));
        
        // Add options
        englishVoices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.name;
            option.textContent = `${voice.name} (${voice.lang})`;
            voiceSelect.appendChild(option);
        });
        
        // Set current value
        if (window.appState && window.appState.settings.voice) {
            voiceSelect.value = window.appState.settings.voice;
        }
    };
    
    // Chrome loads voices asynchronously
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = populateVoiceList;
    }
    
    // Try to load immediately as well (for Firefox/Safari)
    populateVoiceList();
}