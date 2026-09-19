/**
 * VR Data Consumer: Receives and visualizes real-time streaming data in WebXR
 * 
 * Handles:
 * - Live docking progress visualization
 * - MD trajectory animation
 * - Real-time analysis updates
 * - Agent communication display
 */

import * as THREE from 'three';

class VRDataConsumer {
  /**Consumes WebSocket streams and updates VR visualization in real-time.*/
  
  constructor(scene, masterAgent) {
    this.scene = scene;
    this.masterAgent = masterAgent;
    
    this.ws = null;
    this.isConnected = false;
    this.messageHandlers = {};
    this.activeStreams = {};
    
    this._registerHandlers();
  }
  
  connect(wsUrl = 'ws://localhost:8000/ws') {
    /**Connect to WebSocket streaming server.*/
    this.ws = new WebSocket(wsUrl);
    
    this.ws.onopen = () => {
      this.isConnected = true;
      console.log('✅ Connected to VR data stream');
      this.masterAgent.voiceInterface.speak('Data stream connected. Ready for real-time visualization.');
    };
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this._handleMessage(message);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.masterAgent.voiceInterface.speak('Data stream error. Falling back to local visualization.');
    };
    
    this.ws.onclose = () => {
      this.isConnected = false;
      console.log('Data stream closed');
    };
  }
  
  _registerHandlers() {
    /**Register message type handlers.*/
    this.messageHandlers = {
      'docking_progress': (msg) => this._handleDockingProgress(msg),
      'md_frame': (msg) => this._handleMDFrame(msg),
      'hotspot_found': (msg) => this._handleHotspotFound(msg),
      'sa_score': (msg) => this._handleSynthesisScore(msg),
      'agent_message': (msg) => this._handleAgentMessage(msg),
    };
  }
  
  _handleMessage(message) {
    /**Route incoming message to appropriate handler.*/
    const handler = this.messageHandlers[message.type];
    if (handler) {
      handler(message);
    } else {
      console.log('Unknown message type:', message.type);
    }
  }
  
  _handleDockingProgress(message) {
    /**Handle real-time docking progress updates.*/
    const { campaign_id, progress, current_compound, recent_poses } = message;
    
    // Update progress indicator in HUD
    const progressPercent = Math.round(progress * 100);
    console.log(`🎯 Docking progress: ${progressPercent}% (compound ${current_compound})`);
    
    // Visualize top poses in real-time
    if (recent_poses && recent_poses.length > 0) {
      this._visualizePoses(recent_poses);
    }
    
    // Update conversation HUD
    this.masterAgent._updateConversationHUD('Docking', 
      `Processing compound ${current_compound}... ${progressPercent}% complete`);
  }
  
  _handleMDFrame(message) {
    /**Handle molecular dynamics trajectory frames.*/
    const { simulation_id, frame_number, ligand_coords, energy, rmsd, temperature } = message;
    
    // Update ligand position in real-time
    if (ligand_coords) {
      this._updateLigandPosition(ligand_coords);
    }
    
    // Display energy landscape
    this._updateEnergyTrace(energy, frame_number);
    
    // Update HUD with simulation metrics
    console.log(`📊 MD Frame ${frame_number}: E=${energy.toFixed(2)} kcal/mol, RMSD=${rmsd.toFixed(2)}Å, T=${temperature}K`);
  }
  
  _handleHotspotFound(message) {
    /**Handle analysis hotspot discovery.*/
    const { analysis_id, hotspot, index, total_hotspots } = message;
    
    // Highlight hotspot scaffold in 3D view
    this._highlightScaffold(hotspot);
    
    // Notify user via voice
    this.masterAgent.voiceInterface.speak(
      `Found hotspot ${index + 1} of ${total_hotspots}: ${hotspot.name}. Highlighted in the structure.`
    );
    
    console.log(`🔥 Hotspot found: ${hotspot.name} (frequency: ${hotspot.frequency}%)`);
  }
  
  _handleSynthesisScore(message) {
    /**Handle synthesis accessibility predictions.*/
    const { compound, sa_score, difficulty } = message;
    
    // Color ligands by synthesis difficulty
    this._colorByDifficulty(compound, difficulty, sa_score);
    
    console.log(`🧪 ${compound}: SA Score ${sa_score.toFixed(1)} (${difficulty})`);
  }
  
  _handleAgentMessage(message) {
    /**Handle inter-agent communication.*/
    const { sender, receiver, message: msg } = message;
    
    console.log(`💬 ${sender} → ${receiver}: ${msg.text || msg.type}`);
    
    // Show agent-to-agent communication in HUD (optional)
    // Could visualize as thought bubbles between avatars
  }
  
  _visualizePoses(poses) {
    /**Render top scoring poses in real-time.*/
    // Clear previous pose geometries
    this.scene.children
      .filter(obj => obj.userData?.type === 'pose')
      .forEach(obj => this.scene.remove(obj));
    
    // Render new poses
    poses.forEach((pose, idx) => {
      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array(pose.atoms.flatMap(a => [a.x, a.y, a.z]));
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      
      const material = new THREE.PointsMaterial({
        color: 0x39d98a,
        size: 0.1,
      });
      
      const points = new THREE.Points(geometry, material);
      points.userData.type = 'pose';
      this.scene.add(points);
    });
  }
  
  _updateLigandPosition(coords) {
    /**Update ligand position for MD trajectory visualization.*/
    // Find ligand mesh in scene
    let ligand = this.scene.getObjectByName('ligand');
    if (ligand) {
      ligand.position.set(coords[0], coords[1], coords[2]);
    }
  }
  
  _updateEnergyTrace(energy, frameNum) {
    /**Draw energy landscape as trajectory unfolds.*/
    // This would update a canvas or graph in the HUD
    console.log(`Energy history: ${energy.toFixed(2)} kcal/mol`);
  }
  
  _highlightScaffold(hotspot) {
    /**Highlight a scaffold motif in the structure.*/
    console.log(`Highlighting: ${hotspot.name}`);
    // Would apply glow effect or color change to matching atoms
  }
  
  _colorByDifficulty(compound, difficulty, score) {
    /**Color compound representation by synthesis difficulty.*/
    const colors = {
      'easy': 0x39d98a,      // green
      'moderate': 0xffa500,  // orange
      'difficult': 0xff6b6b, // red
    };
    
    const color = colors[difficulty] || 0xcccccc;
    console.log(`Color ${compound} as ${difficulty}: ${color.toString(16)}`);
  }
  
  closeConnection() {
    /**Close WebSocket connection gracefully.*/
    if (this.ws && this.isConnected) {
      this.ws.close();
    }
  }
}

class CollaborativeSession {
  /**Manages multi-user collaboration in shared VR workspace.*/
  
  constructor(sessionId, userId) {
    this.sessionId = sessionId;
    this.userId = userId;
    this.peers = new Map();  // Map<userId, PeerState>
    this.sharedState = {};
  }
  
  async joinSession(websocketUrl) {
    /**Join a collaborative session.*/
    // Establish connection
    // Sync current state with peers
    console.log(`Joining collaborative session: ${this.sessionId}`);
  }
  
  broadcastStateChange(key, value) {
    /**Broadcast state change to all peers.*/
    this.sharedState[key] = value;
    
    // Send via WebSocket to all peers
    const message = {
      type: 'state_change',
      user_id: this.userId,
      key,
      value,
      timestamp: new Date().toISOString(),
    };
    
    console.log('Broadcast:', message);
  }
  
  subscribeToStateChange(key, callback) {
    /**Subscribe to changes on a specific state key.*/
    // In production: use Observer pattern or WebSocket handlers
  }
}

export { VRDataConsumer, CollaborativeSession };
