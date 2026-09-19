"""Master Agent: Orchestrates team agents and responds to researcher voice commands.

The Master Agent:
- Listens to natural language research requests
- Interprets intent (dock compounds, analyze results, generate reports, run MD)
- Delegates to specialized agents (optimizer, analyst, orchestrator)
- Coordinates multi-step workflows
- Provides real-time guidance in AR/VR
- Learns from researcher feedback

Example interactions:
- "Dock these 50 compounds against SOD1"
- "Show me the top 5 binders and their binding modes"
- "Run MD on the best compound for 10 nanoseconds"
- "Generate a paper from this screening campaign"
- "What are the hotspot scaffolds in these results?"
"""
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum

class ResearchIntent(Enum):
    """Detected research intent from natural language."""
    DOCK = "dock_compounds"
    ANALYZE = "analyze_results"
    GENERATE_REPORT = "generate_report"
    GENERATE_PAPER = "generate_paper"
    RUN_MD = "run_molecular_dynamics"
    LOAD_TARGET = "load_target"
    SCREEN_LIBRARY = "screen_library"
    VARIANT_ANALYSIS = "variant_analysis"
    OPTIMIZE_PARAMS = "optimize_parameters"
    HELP = "help"
    UNKNOWN = "unknown"

class MasterAgent:
    """Master Agent that coordinates team and responds to voice commands."""
    
    def __init__(self):
        self.agent_id = "master_001"
        self.name = "Dr. Sarah - Research Lead"
        self.description = "Master agent coordinating your research team"
        self.status = "ready"
        self.current_project_id = None
        self.current_target = None
        self.conversation_history = []
        self.last_action = None
        self.agent_team = {
            'optimizer': None,
            'analyst': None,
            'orchestrator': None,
        }

    def process_voice_command(self, transcript: str) -> Dict:
        """Process voice input and generate response."""
        intent, entities = self._parse_intent(transcript)
        
        # Store in conversation history
        self.conversation_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'user_input': transcript,
            'intent': intent.value,
        })
        
        # Generate response and action
        response = self._handle_intent(intent, entities)
        return response

    def _parse_intent(self, text: str) -> Tuple[ResearchIntent, Dict]:
        """Extract research intent and entities from text."""
        text_lower = text.lower()
        entities = self._extract_entities(text)
        
        # Intent matching
        if any(word in text_lower for word in ['dock', 'docking', 'screen']):
            return ResearchIntent.DOCK, entities
        elif any(word in text_lower for word in ['analyze', 'analysis', 'hotspot', 'scaffold']):
            return ResearchIntent.ANALYZE, entities
        elif any(word in text_lower for word in ['report', 'generate report', 'summary']):
            return ResearchIntent.GENERATE_REPORT, entities
        elif any(word in text_lower for word in ['paper', 'manuscript', 'publication']):
            return ResearchIntent.GENERATE_PAPER, entities
        elif any(word in text_lower for word in ['md', 'molecular dynamics', 'simulation', 'dynamics']):
            return ResearchIntent.RUN_MD, entities
        elif any(word in text_lower for word in ['load', 'select', 'target']):
            return ResearchIntent.LOAD_TARGET, entities
        elif any(word in text_lower for word in ['optimize', 'parameter', 'tune']):
            return ResearchIntent.OPTIMIZE_PARAMS, entities
        elif any(word in text_lower for word in ['variant', 'mutation', 'mutant']):
            return ResearchIntent.VARIANT_ANALYSIS, entities
        elif any(word in text_lower for word in ['help', 'what can you', 'how do']):
            return ResearchIntent.HELP, entities
        
        return ResearchIntent.UNKNOWN, entities

    def _extract_entities(self, text: str) -> Dict:
        """Extract compound IDs, targets, parameters from text."""
        entities = {
            'compounds': [],
            'targets': [],
            'parameters': {},
            'count': None,
            'duration': None,
        }
        
        # Extract compound IDs (REF-001, AGI-042, etc.)
        import re
        compound_pattern = r'(REF|AGI)-\d{1,3}'
        entities['compounds'] = re.findall(compound_pattern, text, re.IGNORECASE)
        
        # Extract target names
        targets = ['SOD1', 'LRRK2', 'GBA1', 'SNCA', 'TDP43', 'FUS', 'COL1A1', 'FGFR3']
        for target in targets:
            if target in text.upper():
                entities['targets'].append(target)
        
        # Extract numbers (for counts, durations)
        numbers = re.findall(r'\d+', text)
        if numbers:
            entities['count'] = int(numbers[0])
        
        # Extract duration (10 nanoseconds, 100 steps, etc.)
        if 'nanosecond' in text.lower() or 'ns' in text:
            entities['duration'] = 'nanoseconds'
        elif 'microsecond' in text.lower() or 'us' in text:
            entities['duration'] = 'microseconds'
        
        return entities

    def _handle_intent(self, intent: ResearchIntent, entities: Dict) -> Dict:
        """Generate response and delegate to team agents."""
        
        if intent == ResearchIntent.DOCK:
            return self._handle_dock_request(entities)
        elif intent == ResearchIntent.ANALYZE:
            return self._handle_analysis_request(entities)
        elif intent == ResearchIntent.GENERATE_REPORT:
            return self._handle_report_request()
        elif intent == ResearchIntent.GENERATE_PAPER:
            return self._handle_paper_request()
        elif intent == ResearchIntent.RUN_MD:
            return self._handle_md_request(entities)
        elif intent == ResearchIntent.LOAD_TARGET:
            return self._handle_load_target(entities)
        elif intent == ResearchIntent.OPTIMIZE_PARAMS:
            return self._handle_optimize_request()
        elif intent == ResearchIntent.HELP:
            return self._handle_help()
        else:
            return self._handle_unknown()

    def _handle_dock_request(self, entities: Dict) -> Dict:
        """Orchestrate docking workflow."""
        count = entities.get('count', 50)
        target = entities['targets'][0] if entities['targets'] else self.current_target
        
        return {
            'intent': 'dock',
            'message': f"Starting docking of {count} compounds against {target}. Using optimizer agent to tune parameters...",
            'voice_response': f"Alright, I'm spinning up a docking campaign against {target}. Dock will run {count} compounds through our Monte Carlo pipeline. Expect results in about 5 to 10 minutes depending on compound complexity.",
            'action': {
                'type': 'dock_campaign',
                'target': target,
                'compounds': count,
                'agents_involved': ['optimizer', 'dock_engine'],
                'estimated_time': '5-10 minutes',
            },
            'vr_visualization': {
                'scene': 'docking_progress',
                'show_target_structure': True,
                'show_ligand_positions': True,
                'highlight_pockets': True,
                'display_scores_in_realtime': True,
            }
        }

    def _handle_analysis_request(self, entities: Dict) -> Dict:
        """Delegate analysis to analyst agent."""
        return {
            'intent': 'analyze',
            'message': "Analyst agent activated. Scanning results for hotspots and synthesis difficulty...",
            'voice_response': "I'm having my analyst team look for chemical patterns in your screening results. They'll identify the recurring scaffolds in your top binders and tell you which ones are easiest to synthesize.",
            'action': {
                'type': 'analysis_campaign',
                'agents_involved': ['analyst'],
                'analyses': ['hotspot_detection', 'synthetic_accessibility', 'outlier_detection'],
                'estimated_time': '2-3 minutes',
            },
            'vr_visualization': {
                'scene': 'results_analysis',
                'show_structure_comparison': True,
                'highlight_hotspots': True,
                'color_by_sa_score': True,
            }
        }

    def _handle_report_request(self) -> Dict:
        """Generate publication-ready report."""
        return {
            'intent': 'report',
            'message': "Generating publication-ready report with methods, tables, and figures...",
            'voice_response': "I'm compiling your screening results into a research report. You'll get a nicely formatted document with your methods section, a results table ranked by binding affinity, and notes on validation steps.",
            'action': {
                'type': 'generate_report',
                'agents_involved': ['orchestrator'],
                'formats': ['markdown', 'json', 'html'],
                'estimated_time': '1-2 minutes',
            },
            'vr_visualization': {
                'scene': 'report_preview',
                'show_document': True,
                'allow_export': True,
            }
        }

    def _handle_paper_request(self) -> Dict:
        """Generate full research paper."""
        return {
            'intent': 'paper',
            'message': "Generating full research paper in LaTeX and Markdown...",
            'voice_response': "Alright, I'm drafting your paper. This includes abstract, introduction, methods, results, discussion, and references. You'll get both a LaTeX version for PDF and a Markdown version for bioRxiv.",
            'action': {
                'type': 'generate_paper',
                'agents_involved': ['orchestrator'],
                'formats': ['latex', 'markdown', 'json'],
                'estimated_time': '3-5 minutes',
            },
        }

    def _handle_md_request(self, entities: Dict) -> Dict:
        """Run molecular dynamics simulation."""
        duration = entities.get('duration', 'nanoseconds')
        count = entities.get('count', 10)
        
        return {
            'intent': 'md',
            'message': f"Starting interactive molecular dynamics for {count} {duration}...",
            'voice_response': f"Launching molecular dynamics. I'll simulate your ligand binding over {count} {duration} at 300 Kelvin. You can watch it happen in real-time here.",
            'action': {
                'type': 'run_md',
                'agents_involved': ['optimizer'],
                'duration': f"{count} {duration}",
                'temperature': '300K',
                'estimated_time': f"{count * 10} seconds",
            },
            'vr_visualization': {
                'scene': 'md_simulation',
                'show_trajectory': True,
                'show_energy_landscape': True,
                'show_hbonds': True,
                'allow_steering': True,  # User can grab and move ligand
                'playback_speed': '1x (can adjust)',
            }
        }

    def _handle_load_target(self, entities: Dict) -> Dict:
        """Load a target structure."""
        target = entities['targets'][0] if entities['targets'] else 'SOD1'
        self.current_target = target
        
        return {
            'intent': 'load_target',
            'message': f"Loading {target} structure from AlphaFold and PDB...",
            'voice_response': f"Pulling up {target} now. I'm fetching the best AlphaFold prediction and any crystal structures. Give me a second...",
            'action': {
                'type': 'load_structure',
                'target': target,
                'sources': ['alphafold', 'pdb'],
                'estimated_time': '2-3 seconds',
            },
            'vr_visualization': {
                'scene': 'structure_viewer',
                'show_structure': True,
                'show_pockets': True,
                'show_variants': True,
                'allow_rotation': True,
                'allow_zoom': True,
            }
        }

    def _handle_optimize_request(self) -> Dict:
        """Optimize computational parameters."""
        return {
            'intent': 'optimize',
            'message': "Optimizer agent analyzing convergence and suggesting parameter improvements...",
            'voice_response': "My optimization team is checking whether your current settings are giving you good results. They'll suggest tweaks to get faster convergence without sacrificing accuracy.",
            'action': {
                'type': 'optimize_parameters',
                'agents_involved': ['optimizer'],
                'analyses': ['convergence_check', 'scoring_refinement', 'sampling_efficiency'],
                'estimated_time': '2-3 minutes',
            },
        }

    def _handle_help(self) -> Dict:
        """Provide help and command suggestions."""
        return {
            'intent': 'help',
            'message': "Here's what I can do for you:",
            'voice_response': """
            You can ask me to:
            - Dock compounds against a target protein
            - Analyze screening results for hotspots
            - Generate research reports
            - Run molecular dynamics simulations
            - Load different target proteins
            - Optimize docking parameters
            - Create full research papers for publication
            
            Just speak naturally. For example: 'Dock 100 compounds against LRRK2' or 'Show me the top 5 binders and their binding modes'.
            """,
            'example_commands': [
                "Dock 50 compounds against SOD1",
                "Analyze these results for hotspots",
                "Run MD on the best compound for 10 nanoseconds",
                "Generate a report from this screening",
                "Load the LRRK2 target",
                "Optimize docking parameters",
            ],
        }

    def _handle_unknown(self) -> Dict:
        """Handle unrecognized commands."""
        return {
            'intent': 'unknown',
            'message': "I didn't quite understand that. Could you rephrase?",
            'voice_response': "I'm not sure what you're asking. Try something like 'dock compounds against SOD1' or 'analyze the screening results'. Need help? Just say 'help'.",
        }

    def get_status(self) -> Dict:
        """Return current status for HUD display."""
        return {
            'agent': self.name,
            'status': self.status,
            'current_project': self.current_project_id,
            'current_target': self.current_target,
            'last_action': self.last_action,
            'conversation_count': len(self.conversation_history),
        }

    def to_dict(self) -> Dict:
        """Serialize master agent state."""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'current_project_id': self.current_project_id,
            'current_target': self.current_target,
            'conversation_history': self.conversation_history[-10:],  # Last 10 commands
        }
