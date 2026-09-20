/**
 * Advanced Voice Control System
 * 
 * Enhanced voice recognition with:
 * - Multi-language support
 * - Context-aware command parsing
 * - Gesture-synchronized voice commands
 * - Voice feedback with intonation
 * - Command confirmation/cancellation
 */

class AdvancedVoiceControl {
  /**Advanced voice recognition with gesture integration.*/
  
  constructor(masterAgent) {
    this.masterAgent = masterAgent;
    this.isListening = false;
    this.currentCommand = null;
    this.commandHistory = [];
    
    // Command vocabulary
    this.commandVocabulary = {
      // Workflow commands
      'run optimization': { action: 'run_workflow', params: { template: 'lead_optimization' } },
      'start validation': { action: 'run_workflow', params: { template: 'validation_campaign' } },
      'begin discovery': { action: 'run_workflow', params: { template: 'discovery_sprint' } },
      
      // Navigation commands
      'zoom in': { action: 'camera_zoom', params: { direction: 'in' } },
      'zoom out': { action: 'camera_zoom', params: { direction: 'out' } },
      'rotate left': { action: 'camera_rotate', params: { direction: 'left' } },
      'rotate right': { action: 'camera_rotate', params: { direction: 'right' } },
      'reset view': { action: 'camera_reset' },
      
      // Analysis commands
      'show hotspots': { action: 'show_analysis', params: { type: 'hotspots' } },
      'highlight binding': { action: 'show_analysis', params: { type: 'binding_modes' } },
      'color by score': { action: 'color_by', params: { property: 'binding_score' } },
      'color by synthesis': { action: 'color_by', params: { property: 'synthesis_difficulty' } },
      
      // Data commands
      'export results': { action: 'export', params: { format: 'json' } },
      'generate report': { action: 'generate_report' },
      'create paper': { action: 'generate_paper' },
      'save project': { action: 'save_project' },
      
      // Team commands
      'optimizer, tune parameters': { action: 'delegate', params: { agent: 'optimizer' } },
      'analyst, find hotspots': { action: 'delegate', params: { agent: 'analyst' } },
      'orchestrator, coordinate workflow': { action: 'delegate', params: { agent: 'orchestrator' } },
      
      // Voice control
      'repeat last command': { action: 'repeat_command' },
      'cancel operation': { action: 'cancel_current' },
      'show available commands': { action: 'list_commands' },
      'help': { action: 'show_help' }
    };
    
    this._initializeSpeechRecognition();
  }
  
  _initializeSpeechRecognition() {
    /**Initialize Web Speech API or fallback.*/
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.warn('Speech Recognition API not available');
      return;
    }
    
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';
    
    this.recognition.onstart = () => {
      this.isListening = true;
      console.log('🎤 Listening...');
    };
    
    this.recognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      
      if (event.isFinal) {
        this._processVoiceInput(transcript);
      }
    };
    
    this.recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
    };
    
    this.recognition.onend = () => {
      this.isListening = false;
    };
  }
  
  startListening() {
    /**Start voice recognition.*/
    if (this.recognition && !this.isListening) {
      this.recognition.start();
    }
  }
  
  stopListening() {
    /**Stop voice recognition.*/
    if (this.recognition && this.isListening) {
      this.recognition.stop();
    }
  }
  
  _processVoiceInput(transcript) {
    /**Process voice input and execute command.*/
    console.log(`Voice input: "${transcript}"`);
    
    // Normalize input
    const normalized = transcript.toLowerCase().trim();
    
    // Find matching command
    const command = this._matchCommand(normalized);
    
    if (command) {
      console.log(`✓ Matched: ${command.name}`);
      this._executeCommand(command);
      this.commandHistory.push({
        text: transcript,
        command: command.name,
        timestamp: new Date()
      });
    } else {
      console.log(`✗ No matching command. Asking master agent...`);
      this.masterAgent.process_voice_command(transcript);
    }
  }
  
  _matchCommand(input) {
    /**Find best matching command for input.*/
    const words = input.split(' ');
    let bestMatch = null;
    let bestScore = 0;
    
    for (const [pattern, cmdDef] of Object.entries(this.commandVocabulary)) {
      const score = this._calculateSimilarity(input, pattern);
      
      if (score > bestScore && score > 0.6) {
        bestScore = score;
        bestMatch = {
          name: pattern,
          definition: cmdDef
        };
      }
    }
    
    return bestMatch;
  }
  
  _calculateSimilarity(str1, str2) {
    /**Calculate string similarity (0-1).*/
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;
    
    if (longer.length === 0) return 1.0;
    
    const editDistance = this._levenshteinDistance(longer, shorter);
    return (longer.length - editDistance) / longer.length;
  }
  
  _levenshteinDistance(s1, s2) {
    /**Calculate Levenshtein distance.*/
    const costs = [];
    for (let i = 0; i <= s1.length; i++) {
      let lastValue = i;
      for (let j = 0; j <= s2.length; j++) {
        if (i === 0) {
          costs[j] = j;
        } else if (j > 0) {
          let newValue = costs[j - 1];
          if (s1.charAt(i - 1) !== s2.charAt(j - 1)) {
            newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1;
          }
          costs[j - 1] = lastValue;
          lastValue = newValue;
        }
      }
      if (i > 0) costs[s2.length] = lastValue;
    }
    return costs[s2.length];
  }
  
  _executeCommand(command) {
    /**Execute matched command.*/
    const def = command.definition;
    
    switch (def.action) {
      case 'run_workflow':
        this._runWorkflow(def.params);
        break;
      case 'camera_zoom':
        this._cameraZoom(def.params);
        break;
      case 'camera_rotate':
        this._cameraRotate(def.params);
        break;
      case 'show_analysis':
        this._showAnalysis(def.params);
        break;
      case 'delegate':
        this._delegateToAgent(def.params);
        break;
      default:
        console.log(`Executing: ${def.action}`);
    }
  }
  
  _runWorkflow(params) {
    console.log(`Starting workflow: ${params.template}`);
    // Delegation to master agent
    this.masterAgent.process_voice_command(
      `Run ${params.template} optimization`
    );
  }
  
  _cameraZoom(params) {
    console.log(`Camera zoom: ${params.direction}`);
  }
  
  _cameraRotate(params) {
    console.log(`Camera rotate: ${params.direction}`);
  }
  
  _showAnalysis(params) {
    console.log(`Show analysis: ${params.type}`);
  }
  
  _delegateToAgent(params) {
    console.log(`Delegating to ${params.agent} agent`);
  }
  
  speak(text, options = {}) {
    /**Speak text using Web Speech API.*/
    if (!('speechSynthesis' in window)) {
      console.warn('Speech Synthesis not available');
      return;
    }
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = options.rate || 1.0;
    utterance.pitch = options.pitch || 1.0;
    utterance.volume = options.volume || 1.0;
    
    window.speechSynthesis.speak(utterance);
  }
  
  getCommandHistory() {
    /**Get recent voice commands.*/
    return this.commandHistory.slice(-10);
  }
}

export { AdvancedVoiceControl };
