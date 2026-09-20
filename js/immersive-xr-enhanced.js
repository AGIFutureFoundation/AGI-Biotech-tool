/**
 * Enhanced Immersive AR/VR Interface with Hand Gestures & Voice Control
 *
 * Complete multimodal interaction system integrating:
 * - Hand gesture recognition (pinch, grab, point, palm open, swipes)
 * - Advanced voice command processing
 * - Gesture-voice context switching
 * - Multimodal feedback (audio, haptic, visual)
 * - Agent team avatars with responsive animations
 * - Real-time molecular visualization streaming
 */

import { HandGestureController } from './hand_gesture_control.js';
import { AdvancedVoiceControl } from './advanced_voice_control.js';
import { GestureVoiceIntegration } from './gesture_voice_integration.js';
import * as THREE from 'three';

const XR_FEATURES = {
  HAND_TRACKING: true,
  GESTURE_CONTROL: true,
  VOICE_INPUT: true,
  VOICE_OUTPUT: true,
  GESTURE_VOICE_MULTIMODAL: true,
  AGENT_AVATARS: true,
  HUD_DISPLAY: true,
  REAL_TIME_VIZ: true,
  HAPTIC_FEEDBACK: true,
};

class EnhancedVoiceInterface {
  /**Advanced voice recognition with gesture awareness.*/

  constructor() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';

    this.synthesis = window.speechSynthesis;
    this.isListening = false;
    this.transcript = '';
    this.onTranscript = null;
    this.onFinal = null;

    this.recognition.onstart = () => {
      this.isListening = true;
      console.log('🎤 Voice: Listening...');
    };

    this.recognition.onresult = (event) => {
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          this.transcript += t + ' ';
        } else {
          interim += t;
        }
      }

      if (this.onTranscript) {
        this.onTranscript(this.transcript + interim);
      }

      if (event.isFinal && this.onFinal) {
        this.onFinal(this.transcript.trim());
        this.transcript = '';
      }
    };

    this.recognition.onend = () => {
      this.isListening = false;
    };
  }

  startListening() {
    this.transcript = '';
    this.recognition.start();
  }

  stopListening() {
    this.recognition.stop();
    return this.transcript.trim();
  }

  speak(text, options = {}) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = options.rate || 1.0;
    utterance.pitch = options.pitch || 1.0;
    utterance.volume = options.volume || 1.0;
    this.synthesis.speak(utterance);
  }
}

class AgentAvatar {
  /**Visual representation of team agent with gesture-responsive animations.*/

  constructor(agentName, agentRole, position) {
    this.name = agentName;
    this.role = agentRole;
    this.group = new THREE.Group();
    this.group.position.copy(position);

    this.state = 'idle';  // idle, working, communicating, celebrating
    this.animations = {};

    // Head (sphere)
    const headGeom = new THREE.SphereGeometry(0.15, 16, 16);
    const headMat = new THREE.MeshPhongMaterial({
      color: this._roleColor(),
      emissive: 0x333333,
    });
    this.head = new THREE.Mesh(headGeom, headMat);
    this.head.position.y = 1.5;
    this.group.add(this.head);

    // Body (cylinder)
    const bodyGeom = new THREE.CylinderGeometry(0.15, 0.1, 0.8, 8);
    const bodyMat = new THREE.MeshPhongMaterial({
      color: this._roleColor(),
      emissive: 0x222222,
    });
    this.body = new THREE.Mesh(bodyGeom, bodyMat);
    this.body.position.y = 0.9;
    this.group.add(this.body);

    // Label
    this._createLabel();

    // Status aura for state indication
    this.statusAura = new THREE.Mesh(
      new THREE.SphereGeometry(0.25, 16, 16),
      new THREE.MeshBasicMaterial({
        color: 0x00ff00,
        transparent: true,
        opacity: 0,
      })
    );
    this.statusAura.position.y = 1.5;
    this.group.add(this.statusAura);

    // Hand indicators for gesture feedback
    this.handIndicators = this._createHandIndicators();
  }

  _roleColor() {
    const colors = {
      'optimizer': 0x39d98a,
      'analyst': 0xa8d8ff,
      'orchestrator': 0xffa500,
    };
    return colors[this.role] || 0xcccccc;
  }

  _createLabel() {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 64;
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, 256, 64);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 20px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(this.name, 128, 40);

    const texture = new THREE.CanvasTexture(canvas);
    const spriteMat = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(spriteMat);
    sprite.position.y = 1.9;
    sprite.scale.set(2, 0.5, 1);
    this.group.add(sprite);
  }

  _createHandIndicators() {
    const indicators = [];
    const positions = [
      new THREE.Vector3(-0.15, 1.3, 0),
      new THREE.Vector3(0.15, 1.3, 0),
    ];

    positions.forEach(pos => {
      const geo = new THREE.SphereGeometry(0.05, 8, 8);
      const mat = new THREE.MeshBasicMaterial({ color: 0xffff00, transparent: true, opacity: 0 });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.copy(pos);
      this.group.add(mesh);
      indicators.push(mesh);
    });

    return indicators;
  }

  setState(newState) {
    this.state = newState;

    const stateColors = {
      'idle': 0x00ff00,
      'working': 0xffff00,
      'communicating': 0x00ccff,
      'celebrating': 0xff00ff,
    };

    this.statusAura.material.color.setHex(stateColors[newState] || 0x00ff00);
    this.statusAura.material.opacity = newState === 'idle' ? 0 : 0.3;
  }

  indicateGestureResponse() {
    this.handIndicators.forEach((indicator, idx) => {
      indicator.material.opacity = 0.8;
      setTimeout(() => {
        indicator.material.opacity = 0;
      }, 300);
    });
  }

  pulse() {
    if (this.state !== 'idle') {
      const scale = 0.25 + 0.1 * Math.sin(Date.now() * 0.005);
      this.statusAura.scale.set(scale, scale, scale);
    }
  }

  getGroup() {
    return this.group;
  }
}

class EnhancedImmersiveXRInterface {
  /**Complete multimodal XR interface with hand gesture and voice control.*/

  constructor(renderer, scene, workspace, masterAgent) {
    this.renderer = renderer;
    this.scene = scene;
    this.workspace = workspace;
    this.masterAgent = masterAgent;

    // Initialize multimodal input systems
    this.voiceInterface = new EnhancedVoiceInterface();
    this.handGestureController = null;
    this.advancedVoiceControl = null;
    this.gestureVoiceIntegration = null;

    this.teamAvatars = {};
    this.conversationHUD = null;
    this.agentStatusHUD = null;
    this.controlModesHUD = null;

    // State tracking
    this.activeControlMode = 'voice';  // voice, gesture, gesture+voice
    this.commandHistory = [];
    this.workflowInProgress = false;

    this._initializeMultimodal();
    this._initializeTeam();
    this._initializeHUD();
    this._setupEventHandling();
  }

  _initializeMultimodal() {
    /**Initialize hand tracking and voice control systems.*/
    // Hand gesture controller
    this.handGestureController = new HandGestureController();

    // Advanced voice control
    this.advancedVoiceControl = new AdvancedVoiceControl(this.masterAgent);

    // Gesture-voice integration
    this.gestureVoiceIntegration = new GestureVoiceIntegration(
      this.handGestureController,
      this.advancedVoiceControl,
      this.masterAgent
    );

    console.log('✅ Multimodal systems initialized');
  }

  _initializeTeam() {
    /**Create agent avatars.*/
    const positions = [
      new THREE.Vector3(-0.5, 0, 0),
      new THREE.Vector3(0.5, 0, 0),
      new THREE.Vector3(0, 0, 0.5),
    ];

    const agents = [
      { name: 'Optimizer', role: 'optimizer' },
      { name: 'Analyst', role: 'analyst' },
      { name: 'Orchestrator', role: 'orchestrator' },
    ];

    agents.forEach((agent, i) => {
      const avatar = new AgentAvatar(agent.name, agent.role, positions[i]);
      this.workspace.add(avatar.getGroup());
      this.teamAvatars[agent.role] = avatar;
    });
  }

  _initializeHUD() {
    /**Create UI panels for conversation, status, and control modes.*/

    // Conversation panel
    this.conversationHUD = {
      element: document.createElement('div'),
      messages: [],
    };
    this.conversationHUD.element.id = 'conversation-hud';
    this.conversationHUD.element.style.cssText = `
      position: absolute;
      top: 20px;
      left: 20px;
      width: 400px;
      max-height: 350px;
      background: rgba(10, 15, 24, 0.95);
      border: 2px solid #39d98a;
      color: #e8f1ff;
      padding: 15px;
      font-family: monospace;
      font-size: 12px;
      overflow-y: auto;
      z-index: 100;
      border-radius: 8px;
    `;
    document.body.appendChild(this.conversationHUD.element);

    // Agent status panel
    this.agentStatusHUD = {
      element: document.createElement('div'),
    };
    this.agentStatusHUD.element.id = 'agent-status-hud';
    this.agentStatusHUD.element.style.cssText = `
      position: absolute;
      top: 20px;
      right: 20px;
      width: 320px;
      background: rgba(10, 15, 24, 0.95);
      border: 2px solid #a8d8ff;
      color: #e8f1ff;
      padding: 15px;
      font-family: monospace;
      font-size: 12px;
      z-index: 100;
      border-radius: 8px;
    `;
    document.body.appendChild(this.agentStatusHUD.element);

    // Control modes panel
    this.controlModesHUD = {
      element: document.createElement('div'),
    };
    this.controlModesHUD.element.id = 'control-modes-hud';
    this.controlModesHUD.element.style.cssText = `
      position: absolute;
      bottom: 20px;
      left: 20px;
      width: 350px;
      background: rgba(10, 15, 24, 0.95);
      border: 2px solid #ffa500;
      color: #e8f1ff;
      padding: 15px;
      font-family: monospace;
      font-size: 12px;
      z-index: 100;
      border-radius: 8px;
    `;
    document.body.appendChild(this.controlModesHUD.element);

    this._updateControlModesHUD();
  }

  _setupEventHandling() {
    /**Wire up event handlers for multimodal interaction.*/

    // Voice interface final transcript handling
    this.voiceInterface.onFinal = (transcript) => {
      this._updateConversationHUD('You', transcript);

      // Route to appropriate handler based on control mode
      if (this.activeControlMode === 'voice' || this.activeControlMode === 'gesture+voice') {
        this.advancedVoiceControl._processVoiceInput(transcript);
      }
    };

    // Hand gesture callbacks
    this.handGestureController.onGesture('pinch_right', (hand) => {
      console.log('🤌 Pinch detected - entering selection mode');
      this.gestureVoiceIntegration._enterGestureContext('pinch-select');
      this._updateControlModesHUD();
    });

    this.handGestureController.onGesture('point_right', (hand) => {
      console.log('👉 Point detected - inspection mode');
      this.gestureVoiceIntegration._enterGestureContext('point-inspect');
    });

    this.handGestureController.onGesture('palm_open_right', (hand) => {
      console.log('🤲 Palm open - global command mode');
      this.gestureVoiceIntegration._enterGestureContext('global');
      this.voiceInterface.startListening();
    });

    this.handGestureController.onGesture('grab_right', (hand) => {
      console.log('✋ Grab detected');
    });
  }

  _updateConversationHUD(speaker, message) {
    /**Add message to conversation display with multimodal formatting.*/
    const timestamp = new Date().toLocaleTimeString();
    const entry = `[${timestamp}] ${speaker}: ${message}`;
    this.commandHistory.push({text: message, speaker, timestamp});

    // Keep last 12 messages
    if (this.commandHistory.length > 12) {
      this.commandHistory.shift();
    }

    this.conversationHUD.element.innerHTML = this.commandHistory
      .map(msg => `<div style="margin-bottom: 8px; color: ${msg.speaker === 'You' ? '#a8d8ff' : '#39d98a'};">[${msg.timestamp}] <strong>${msg.speaker}:</strong> ${msg.text}</div>`)
      .join('');

    this.conversationHUD.element.scrollTop = this.conversationHUD.element.scrollHeight;
  }

  _updateControlModesHUD() {
    /**Update control modes display showing active input methods.*/
    const modeDisplay = `
      🎮 INPUT MODES:
      ${this.activeControlMode === 'voice' ? '✓ Voice' : '○ Voice'} |
      ${this.activeControlMode === 'gesture' ? '✓ Gesture' : '○ Gesture'} |
      ${this.activeControlMode === 'gesture+voice' ? '✓ Multimodal' : '○ Multimodal'}

      ACTIVE: ${this.gestureVoiceIntegration.contextMode || 'none'}

      Hand tracking: ${this.handGestureController.isTracking ? '✓ ON' : '✗ OFF'}
      Voice listening: ${this.voiceInterface.isListening ? '🎤 ON' : 'OFF'}
      Workflow: ${this.workflowInProgress ? '⚙️ RUNNING' : '⏸ IDLE'}
    `;

    this.controlModesHUD.element.textContent = modeDisplay;
  }

  _updateAgentStatusHUD() {
    /**Update agent team status display.*/
    let statusHTML = '<div style="margin-bottom: 5px;"><strong>TEAM STATUS:</strong></div>';

    Object.entries(this.teamAvatars).forEach(([role, avatar]) => {
      const stateSymbol = avatar.state === 'working' ? '⚙️' : avatar.state === 'communicating' ? '💬' : '✓';
      statusHTML += `<div style="margin-bottom: 5px;">${stateSymbol} <strong>${avatar.name}</strong>: ${avatar.state}</div>`;
    });

    this.agentStatusHUD.element.innerHTML = statusHTML;
  }

  processMasterAgentResponse(response) {
    /**Display and execute master agent response with multimodal feedback.*/

    // Voice response
    if (response.voice_response) {
      this._updateConversationHUD('Dr. Sarah', response.voice_response);
      this.voiceInterface.speak(response.voice_response, { pitch: 1.1 });
    }

    // Animate agents
    if (response.action && response.action.agents_involved) {
      response.action.agents_involved.forEach(agentRole => {
        if (this.teamAvatars[agentRole]) {
          const avatar = this.teamAvatars[agentRole];
          avatar.setState('working');
          avatar.indicateGestureResponse();
        }
      });

      // Haptic feedback
      this.gestureVoiceIntegration.triggerHapticFeedback(1.0, 100);

      const duration = this._parseEstimatedTime(response.action.estimated_time || '5-10 seconds');
      setTimeout(() => {
        response.action.agents_involved.forEach(agentRole => {
          if (this.teamAvatars[agentRole]) {
            this.teamAvatars[agentRole].setState('idle');
          }
        });
      }, duration);
    }

    this._updateAgentStatusHUD();
  }

  _parseEstimatedTime(timeStr) {
    const match = timeStr.match(/(\d+)-(\d+)\s+(seconds|minutes)/);
    if (match) {
      const minutes = match[3] === 'minutes';
      const duration = parseInt(match[2]) * (minutes ? 60000 : 1000);
      return duration;
    }
    return 5000;
  }

  startVoiceSession() {
    this.voiceInterface.startListening();
    this._updateConversationHUD('System', '🎤 Voice session started...');
  }

  stopVoiceSession() {
    return this.voiceInterface.stopListening();
  }

  enableHandTracking() {
    if (this.handGestureController) {
      this.handGestureController.startTracking();
      this._updateControlModesHUD();
    }
  }

  animate() {
    /**Update all animations.*/
    Object.values(this.teamAvatars).forEach(avatar => {
      avatar.pulse();
    });

    if (this.handGestureController && this.handGestureController.isTracking) {
      this.handGestureController.update();
    }
  }
}

export {
  EnhancedVoiceInterface,
  AgentAvatar,
  EnhancedImmersiveXRInterface,
  XR_FEATURES,
};
