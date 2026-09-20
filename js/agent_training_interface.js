/**
 * Agent Training Interface for VR
 * 
 * Displays agent training progress, expertise levels, and workflow management
 * in the immersive VR environment.
 */

class AgentTrainingInterface {
  /**Live training dashboard in VR."""
  
  constructor(vrInterface, masterAgent) {
    this.vr = vrInterface;
    this.masterAgent = masterAgent;
    
    this.trainingMode = false;
    this.activeTraining = null;
    this.agentMetrics = {};
    this.trainingHUD = null;
    
    this._initializeTrainingPanel();
  }
  
  _initializeTrainingPanel() {
    /**Create training HUD panel in VR."""
    this.trainingHUD = {
      element: document.createElement('div'),
    };
    
    this.trainingHUD.element.id = 'training-hud';
    this.trainingHUD.element.style.cssText = `
      position: absolute;
      bottom: 20px;
      right: 20px;
      width: 400px;
      max-height: 400px;
      background: rgba(10, 15, 24, 0.95);
      border: 2px solid #00d98a;
      color: #e8f1ff;
      padding: 20px;
      font-family: monospace;
      font-size: 11px;
      border-radius: 8px;
      z-index: 100;
      overflow-y: auto;
    `;
    
    document.body.appendChild(this.trainingHUD.element);
  }
  
  startTraining(agentRole, trainingPhase) {
    /**Start agent training in VR."""
    this.trainingMode = true;
    this.activeTraining = {
      agent: agentRole,
      phase: trainingPhase,
      startTime: Date.now(),
      episodes: 0,
      totalReward: 0,
    };
    
    this._updateTrainingHUD();
    this.vr.voice.speak(`Starting ${trainingPhase} phase training for ${agentRole}`);
  }
  
  updateAgentMetrics(metrics) {
    /**Update agent performance metrics."""
    this.agentMetrics[metrics.agent_id] = {
      expertise: metrics.expertise,
      performanceScore: metrics.performance_score,
      episodeReward: metrics.episode_reward,
      successRate: metrics.success_rate,
      timestamp: new Date().toLocaleTimeString(),
    };
    
    this._updateTrainingHUD();
  }
  
  displayAgentState(agentId, state) {
    /**Display agent current state in VR."""
    const display = `
      🤖 ${agentId.toUpperCase()}
      State: ${JSON.stringify(state).substring(0, 50)}...
      Expertise: ${(state.expertise * 100).toFixed(1)}%
    `;
    
    this.trainingHUD.element.innerHTML += `<div>${display}</div>`;
  }
  
  trackWorkflowExecution(workflowId, steps) {
    /**Track workflow execution with agent insights."""
    const tracker = {
      id: workflowId,
      steps: steps,
      currentStep: 0,
      agentActions: [],
      rewards: [],
    };
    
    return tracker;
  }
  
  _updateTrainingHUD() {
    /**Update HUD with current training status."""
    let content = '<div style="margin-bottom: 10px;"><strong>🎓 AGENT TRAINING</strong></div>';
    
    if (this.activeTraining) {
      const elapsed = Math.floor((Date.now() - this.activeTraining.startTime) / 1000);
      content += `
        <div style="margin-bottom: 8px;">
          📚 Phase: ${this.activeTraining.phase}
          ⏱️ Elapsed: ${elapsed}s
          📊 Episodes: ${this.activeTraining.episodes}
        </div>
      `;
    }
    
    content += '<div style="margin-bottom: 8px;"><strong>Agent Metrics:</strong></div>';
    
    Object.entries(this.agentMetrics).forEach(([agentId, metrics]) => {
      const expertiseBar = this._createProgressBar(metrics.expertise);
      content += `
        <div style="margin-bottom: 6px;">
          ${agentId}: ${expertiseBar} ${(metrics.expertise * 100).toFixed(0)}%
          <br/>Success: ${(metrics.successRate * 100).toFixed(0)}%
        </div>
      `;
    });
    
    this.trainingHUD.element.innerHTML = content;
  }
  
  _createProgressBar(value, width = 20) {
    /**Create ASCII progress bar."""
    const filled = Math.floor(value * width);
    const empty = width - filled;
    return '[' + '█'.repeat(filled) + '░'.repeat(empty) + ']';
  }
  
  displayLearningInsights(insights) {
    /**Display agent learning insights in VR."""
    const insightText = `
      💡 LEARNING INSIGHTS:
      - Discovered pattern: ${insights.pattern}
      - Confidence: ${(insights.confidence * 100).toFixed(0)}%
      - Expected improvement: ${(insights.improvement * 100).toFixed(1)}%
    `;
    
    this.vr.confirmAction(insightText, {
      pitch: 1.2,
      rate: 0.95,
      hapticIntensity: 0.8,
    });
  }
  
  visualizeTeamCoordination(teamState) {
    /**Visualize team agent coordination in VR.**

    const coordination = {
      optimizer_load: teamState.optimizer.load,
      analyst_load: teamState.analyst.load,
      orchestrator_load: teamState.orchestrator.load,
      collaboration_score: teamState.collaboration,
      efficiency: teamState.efficiency,
    };
    
    return coordination;
  }
  
  enableHandGestureTraining() {
    /**Enable gesture-based training control."""
    // Pinch = zoom into agent expertise details
    // Point = inspect specific step
    // Palm open = reset training view
    console.log('✓ Hand gesture training control enabled');
  }
  
  enableVoiceCommandTraining() {
    /**Enable voice commands for training control."""
    const commands = {
      'start training': () => this.startTraining('optimizer', 'basic'),
      'show metrics': () => this._updateTrainingHUD(),
      'increase difficulty': () => this._increaseDifficulty(),
      'pause training': () => this._pauseTraining(),
    };
    
    return commands;
  }
  
  _increaseDifficulty() {
    if (this.activeTraining) {
      this.activeTraining.difficulty = Math.min(1.0, (this.activeTraining.difficulty || 0.5) + 0.1);
    }
  }
  
  _pauseTraining() {
    this.trainingMode = false;
    this.vr.voice.speak('Training paused');
  }
}

export { AgentTrainingInterface };
