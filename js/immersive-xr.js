/**
 * Immersive AR/VR Interface with Voice Control & Master Agent
 * 
 * Features:
 * - Speech-to-text for voice commands
 * - Master agent responding with text-to-speech
 * - Agent team visualization in VR (avatars for optimizer, analyst, orchestrator)
 * - Real-time docking/MD visualization in AR
 * - Gesture controls (grab, rotate, scale)
 * - HUD showing agent status and conversation
 */

import * as THREE from 'three';

const XR_FEATURES = {
  VOICE_INPUT: true,
  VOICE_OUTPUT: true,
  AGENT_AVATARS: true,
  GESTURE_CONTROL: true,
  HUD_DISPLAY: true,
  SCENE_ANNOTATION: true,
};

class VoiceInterface {
  /**Speech recognition and synthesis for VR.*/
  
  constructor() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';
    
    this.synthesis = window.speechSynthesis;
    this.isListening = false;
    this.transcript = '';
    this.onTranscript = null;
    
    this.recognition.onstart = () => {
      this.isListening = true;
      console.log('🎤 Listening...');
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
    };
    
    this.recognition.onend = () => {
      this.isListening = false;
      console.log('🎤 Stopped listening');
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
  
  speak(text) {
    /**Use text-to-speech for agent responses.*/
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    this.synthesis.speak(utterance);
  }
}

class AgentAvatar {
  /**Visual representation of a team agent in VR.*/
  
  constructor(agent_name, agent_role, position) {
    this.name = agent_name;
    this.role = agent_role;
    this.group = new THREE.Group();
    this.group.position.copy(position);
    
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
    
    // Name label above head
    this._createLabel();
    
    // Status indicator (pulsing aura when working)
    this.statusAura = new THREE.Mesh(
      new THREE.SphereGeometry(0.25, 16, 16),
      new THREE.MeshBasicMaterial({ color: 0x00ff00, transparent: true, opacity: 0 })
    );
    this.statusAura.position.y = 1.5;
    this.group.add(this.statusAura);
    
    this.isWorking = false;
  }
  
  _roleColor() {
    /**Color per agent role.*/
    const colors = {
      'optimizer': 0x39d98a,     // mint green
      'analyst': 0xa8d8ff,       // light blue
      'orchestrator': 0xffa500,  // orange
    };
    return colors[this.role] || 0xcccccc;
  }
  
  _createLabel() {
    /**Create floating text label above agent.*/
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
  
  setWorking(isWorking) {
    /**Pulse aura to indicate agent is working.*/
    this.isWorking = isWorking;
    if (isWorking) {
      this.statusAura.material.opacity = 0.3;
    } else {
      this.statusAura.material.opacity = 0;
    }
  }
  
  pulse() {
    /**Animate pulsing when working.*/
    if (this.isWorking) {
      const scale = 0.25 + 0.1 * Math.sin(Date.now() * 0.005);
      this.statusAura.scale.set(scale, scale, scale);
    }
  }
  
  getGroup() {
    return this.group;
  }
}

class ImmersiveXRInterface {
  /**Main XR interface with voice control and agent team.*/
  
  constructor(renderer, scene, workspace) {
    this.renderer = renderer;
    this.scene = scene;
    this.workspace = workspace;
    
    this.voiceInterface = new VoiceInterface();
    this.masterAgent = null;
    this.teamAvatars = {};
    
    this.conversationHUD = null;
    this.agentStatusHUD = null;
    
    this._initializeTeam();
    this._initializeHUD();
    this._setupVoiceHandling();
  }
  
  _initializeTeam() {
    /**Create agent avatars in the workspace.*/
    const positions = [
      new THREE.Vector3(-0.5, 0, 0),   // optimizer
      new THREE.Vector3(0.5, 0, 0),    // analyst
      new THREE.Vector3(0, 0, 0.5),    // orchestrator
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
    /**Create UI elements for conversation and status.*/
    // Conversation panel (upper left)
    this.conversationLog = [];
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
      max-height: 300px;
      background: rgba(10, 15, 24, 0.9);
      border: 2px solid #39d98a;
      color: #e8f1ff;
      padding: 15px;
      font-family: monospace;
      font-size: 12px;
      overflow-y: auto;
      z-index: 100;
    `;
    document.body.appendChild(this.conversationHUD.element);
    
    // Agent status panel (upper right)
    this.agentStatusHUD = {
      element: document.createElement('div'),
    };
    this.agentStatusHUD.element.id = 'agent-status-hud';
    this.agentStatusHUD.element.style.cssText = `
      position: absolute;
      top: 20px;
      right: 20px;
      width: 300px;
      background: rgba(10, 15, 24, 0.9);
      border: 2px solid #a8d8ff;
      color: #e8f1ff;
      padding: 15px;
      font-family: monospace;
      font-size: 12px;
      z-index: 100;
    `;
    document.body.appendChild(this.agentStatusHUD.element);
  }
  
  _setupVoiceHandling() {
    /**Wire voice input to master agent.*/
    this.voiceInterface.onTranscript = (transcript) => {
      this._updateConversationHUD('You', transcript);
    };
  }
  
  processMasterAgentResponse(response) {
    /**Display and execute agent response.*/
    // Show message in HUD
    this._updateConversationHUD('Dr. Sarah', response.voice_response);
    
    // Speak response
    this.voiceInterface.speak(response.voice_response);
    
    // Animate relevant agents
    if (response.action.agents_involved) {
      response.action.agents_involved.forEach(agentRole => {
        if (this.teamAvatars[agentRole]) {
          this.teamAvatars[agentRole].setWorking(true);
        }
      });
      
      // Stop animation after action completes
      const duration = this._parseEstimatedTime(response.action.estimated_time);
      setTimeout(() => {
        response.action.agents_involved.forEach(agentRole => {
          if (this.teamAvatars[agentRole]) {
            this.teamAvatars[agentRole].setWorking(false);
          }
        });
      }, duration);
    }
    
    // Update visualization
    if (response.vr_visualization) {
      this._updateVRScene(response.vr_visualization);
    }
  }
  
  _updateConversationHUD(speaker, message) {
    /**Add message to conversation display.*/
    const entry = `[${new Date().toLocaleTimeString()}] ${speaker}: ${message}`;
    this.conversationLog.push(entry);
    
    // Keep only last 10 messages
    if (this.conversationLog.length > 10) {
      this.conversationLog.shift();
    }
    
    this.conversationHUD.element.innerHTML = this.conversationLog
      .map(msg => `<div style="margin-bottom: 8px;">${msg}</div>`)
      .join('');
    
    // Auto-scroll to bottom
    this.conversationHUD.element.scrollTop = this.conversationHUD.element.scrollHeight;
  }
  
  _updateVRScene(vizParams) {
    /**Update VR scene based on action parameters.*/
    const scene = vizParams.scene;
    
    if (scene === 'docking_progress') {
      // Show protein structure + ligand positions
      // This would update the molecular viewer in real-time
      console.log('📊 Showing docking progress...');
    } else if (scene === 'results_analysis') {
      // Highlight hotspots in structure
      console.log('🔍 Analyzing results...');
    } else if (scene === 'md_simulation') {
      // Show MD trajectory animation
      console.log('🎬 Running MD simulation...');
    }
  }
  
  _parseEstimatedTime(timeStr) {
    /**Convert time string to milliseconds.*/
    const match = timeStr.match(/(\d+)-(\d+)\s+(seconds|minutes)/);
    if (match) {
      const minutes = match[3] === 'minutes';
      const duration = parseInt(match[2]) * (minutes ? 60000 : 1000);
      return duration;
    }
    return 5000;  // default 5 seconds
  }
  
  startVoiceSession() {
    /**Begin listening for voice commands.*/
    this.voiceInterface.startListening();
    this._updateConversationHUD('System', '🎤 Listening...');
  }
  
  stopVoiceSession() {
    /**Stop listening and process final transcript.*/
    const transcript = this.voiceInterface.stopListening();
    return transcript;
  }
  
  animate() {
    /**Update agent avatars and animations.*/
    Object.values(this.teamAvatars).forEach(avatar => {
      avatar.pulse();
    });
  }
}

export { VoiceInterface, AgentAvatar, ImmersiveXRInterface, XR_FEATURES };
