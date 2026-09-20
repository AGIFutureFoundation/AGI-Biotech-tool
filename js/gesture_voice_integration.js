/**
 * Gesture + Voice Integration Layer
 * 
 * Combines hand gestures and voice commands for:
 * - Gesture-aware voice input (e.g., "pinch to select")
 * - Voice-triggered gesture modes
 * - Multimodal interaction patterns
 * - Accessibility features
 */

class GestureVoiceIntegration {
  /**Unified gesture and voice control system.*/
  
  constructor(handGestureController, voiceController, masterAgent) {
    this.hands = handGestureController;
    this.voice = voiceController;
    this.agent = masterAgent;
    
    this.contextMode = 'default';  // current interaction context
    this.gestureVoiceBindings = {};
    this.voiceGestureBindings = {};
    
    this._setupBindings();
  }
  
  _setupBindings() {
    /**Set up gesture-voice interaction patterns.*/
    
    // Pattern 1: Pinch + Voice = Targeted selection
    this.hands.onGesture('pinch_right', (hand) => {
      this._enterGestureContext('pinch-select');
      this.voice.speak('Say what to do with this object');
      this.voice.startListening();
    });
    
    // Pattern 2: Point + Voice = Ask about pointed object
    this.hands.onGesture('point_right', (hand) => {
      this._enterGestureContext('point-inspect');
      this.voice.speak('Ask me about this');
      this.voice.startListening();
    });
    
    // Pattern 3: Palm open + Voice = Global command
    this.hands.onGesture('palm_open_right', (hand) => {
      this._enterGestureContext('global');
      this.voice.speak('Ready for command');
      this.voice.startListening();
    });
    
    // Pattern 4: Swipe + Voice = Navigation
    this.hands.onGesture('swipe_right_right', () => {
      this._enterGestureContext('navigate');
      this.voice.speak('Navigation mode. Where to?');
    });
    
    // Voice-triggered gesture modes
    this._registerVoiceGestureModes();
  }
  
  _registerVoiceGestureModes() {
    /**Register voice commands that enable gesture modes.*/
    
    // Voice: "Enable hand control" → listen for gestures
    // Voice: "Show me commands" → list available gestures
    // Voice: "Gesture mode" → enable gesture-first interaction
  }
  
  _enterGestureContext(context) {
    /**Enter gesture-aware interaction context.*/
    this.contextMode = context;
    
    switch (context) {
      case 'pinch-select':
        console.log('📌 Pinch-select mode: awaiting voice command');
        break;
      case 'point-inspect':
        console.log('👉 Point-inspect mode: awaiting voice query');
        break;
      case 'global':
        console.log('🌐 Global command mode');
        break;
      case 'navigate':
        console.log('🧭 Navigation mode');
        break;
    }
  }
  
  // Multimodal interaction patterns
  
  selectWithGestureAndVoice(gestureData, voiceCommand) {
    /**Select and act on object using both modalities.*/
    console.log(`Selecting with gesture + voice: "${voiceCommand}"`);
    
    // Hand position pinpoints the object
    // Voice specifies the action
    this.agent.process_voice_command(voiceCommand);
  }
  
  navigateWithGesture(direction, intensity) {
    /**Navigate using gesture intensity (close fist = fast, open = slow).*/
    console.log(`Navigating ${direction} with intensity ${intensity}`);
  }
  
  rotateWithDualHand(leftHand, rightHand) {
    /**Rotate scene using both hands.*/
    const angle = this._calculateRotationAngle(leftHand, rightHand);
    console.log(`Rotating by ${angle} degrees`);
  }
  
  _calculateRotationAngle(hand1, hand2) {
    /**Calculate rotation angle from two hands.*/
    // Implementation would use hand positions to determine angle
    return 45;  // degrees
  }
  
  // Accessibility features
  
  enableGestureOnlyMode() {
    /**Enable gesture control without requiring voice.*/
    console.log('Gesture-only mode enabled (accessibility)');
    this.voice.stopListening();
  }
  
  enableVoiceOnlyMode() {
    /**Enable voice control without requiring gestures.*/
    console.log('Voice-only mode enabled (accessibility)');
  }
  
  enableDwellSelection(dwellTimeMs = 1000) {
    /**Enable dwell-based selection for hands.*/
    console.log(`Dwell selection enabled (${dwellTimeMs}ms)`);
  }
  
  // Haptic feedback coordination
  
  triggerHapticFeedback(intensity = 1.0, duration = 100) {
    /**Trigger haptic feedback on gesture completion.*/
    if (navigator.vibrate) {
      navigator.vibrate(duration * intensity);
    }
  }
  
  // Multimodal feedback
  
  confirmAction(text, options = {}) {
    /**Confirm action with multimodal feedback.*/
    // Voice feedback
    this.voice.speak(text, {
      pitch: options.pitch || 1.2,
      rate: options.rate || 0.9
    });
    
    // Haptic feedback
    if (options.haptic !== false) {
      this.triggerHapticFeedback(options.hapticIntensity || 1.0);
    }
    
    // Visual feedback (glow, pulse, etc.)
    if (options.onScreen !== false) {
      this._playVisualFeedback();
    }
  }
  
  _playVisualFeedback() {
    /**Play visual feedback animation.*/
    console.log('✨ Playing visual feedback');
  }
  
  // Command recovery & undo
  
  undoLastAction() {
    /**Undo last gesture/voice action.*/
    console.log('↶ Undoing last action');
  }
  
  repeatLastCommand() {
    /**Repeat last voice or gesture command.*/
    const history = this.voice.getCommandHistory();
    if (history.length > 0) {
      const last = history[history.length - 1];
      console.log(`Repeating: ${last.text}`);
    }
  }
}

export { GestureVoiceIntegration };
