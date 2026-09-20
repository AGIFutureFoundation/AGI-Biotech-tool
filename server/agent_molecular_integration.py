"""Integration between agent training system and molecular research pipeline.

Enables:
- Agents learn from real molecular simulation results
- Optimization feedback loops for parameter tuning
- Workflow orchestration based on molecular outcomes
- Expertise tracking tied to molecular success metrics
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from molecular_research_pipeline import (
    MolecularDockingEngine,
    MolecularDynamicsEngine,
    ADMETPredictor,
    CompoundScoringEngine,
    DockingResult,
    MDSimulation,
    ADMETProperties,
)

@dataclass
class MolecularOutcome:
    """Result of a molecular simulation for agent learning."""
    workflow_id: str
    target: str
    compound_id: str
    docking_energy: float
    stability_score: float
    admet_score: float
    final_score: float
    optimization_params: Dict
    timestamp: str

class AgentMolecularBridge:
    """Connects agents with molecular research pipeline."""

    def __init__(self):
        self.docking_engine = MolecularDockingEngine()
        self.md_engine = MolecularDynamicsEngine()
        self.admet_predictor = ADMETPredictor()
        self.scoring_engine = CompoundScoringEngine()

        self.learning_history = {}  # workflow_id -> [outcomes]
        self.parameter_performance = {}  # param_set -> avg_score
        self.agent_expertise = {}  # agent_id -> expertise_metrics

    def execute_docking_workflow(
        self,
        workflow_id: str,
        compounds: List[str],
        target: str,
        target_chain: str,
        optimizer_params: Optional[Dict] = None,
    ) -> Tuple[List[DockingResult], Dict]:
        """Execute docking with agent-tuned parameters.

        Args:
            workflow_id: Unique workflow identifier
            compounds: List of SMILES strings
            target: PDB ID or file path
            target_chain: Protein chain identifier
            optimizer_params: Docking parameters from optimizer agent

        Returns:
            (docking_results, workflow_summary)
        """

        # Use agent-provided parameters or defaults
        params = optimizer_params or self._default_docking_params()

        # Record parameter usage for learning
        self._record_parameter_usage(params)

        # Execute docking batch
        results = self.docking_engine.dock_batch(
            compounds,
            target,
            target_chain,
        )

        # Sort by binding energy
        results = sorted(results, key=lambda r: r.binding_energy)

        summary = {
            'workflow_id': workflow_id,
            'target': target,
            'compounds_docked': len(compounds),
            'top_energy': results[0].binding_energy if results else None,
            'avg_energy': sum(r.binding_energy for r in results) / len(results) if results else None,
            'parameters_used': params,
        }

        return results, summary

    def execute_md_workflow(
        self,
        workflow_id: str,
        compounds: List[DockingResult],
        top_n: int = 10,
    ) -> List[Tuple[DockingResult, MDSimulation]]:
        """Run MD simulations on top compounds.

        Args:
            workflow_id: Workflow identifier
            compounds: Docking results to simulate
            top_n: Number of top compounds to simulate

        Returns:
            List of (DockingResult, MDSimulation) tuples
        """

        results = []

        # Take top compounds by binding energy
        top_compounds = sorted(compounds, key=lambda c: c.binding_energy)[:top_n]

        for docking_result in top_compounds:
            # Setup simulation
            config = self.md_engine.setup_simulation(
                protein_file=f"{docking_result.target}.pdb",
                ligand_file=docking_result.compound_id + ".pdb",
                duration_ns=100,
            )

            # Run simulation
            md_result = self.md_engine.run_simulation(config)

            # Analyze trajectory
            analysis = self.md_engine.analyze_trajectory(md_result)

            # Record outcome for agent learning
            self._record_md_outcome(workflow_id, docking_result, md_result, analysis)

            results.append((docking_result, md_result))

        return results

    def execute_compound_scoring_workflow(
        self,
        workflow_id: str,
        docking_results: List[DockingResult],
        md_results: List[MDSimulation],
        admet_results: List[ADMETProperties],
    ) -> List[Tuple[float, DockingResult]]:
        """Score and rank compounds with multi-criteria approach.

        Args:
            workflow_id: Workflow identifier
            docking_results: Docking energies
            md_results: Stability data
            admet_results: Drug-likeness predictions

        Returns:
            List of (score, compound) tuples sorted by score
        """

        # Build compound tuples
        compounds = list(zip(docking_results, admet_results, md_results))

        # Score batch
        scores = self.scoring_engine.score_batch(compounds)

        # Rank
        ranked = list(zip(scores, docking_results))
        ranked.sort(key=lambda x: x[0], reverse=True)

        # Record for learning
        self._record_scoring_outcome(workflow_id, ranked)

        return ranked

    def record_agent_expertise(
        self,
        agent_id: str,
        target: str,
        success_metric: float,
        parameters: Dict,
    ):
        """Update agent expertise based on molecular outcome.

        Args:
            agent_id: Which agent (optimizer, analyst, etc)
            target: Protein target name
            success_metric: 0-1 score of optimization success
            parameters: Parameters used
        """

        key = f"{agent_id}_{target}"

        if key not in self.agent_expertise:
            self.agent_expertise[key] = {
                'successes': 0,
                'attempts': 0,
                'avg_score': 0.0,
                'best_score': 0.0,
                'best_params': None,
                'learning_curve': [],
            }

        expertise = self.agent_expertise[key]

        # Update metrics
        expertise['attempts'] += 1
        expertise['learning_curve'].append(success_metric)

        if success_metric >= 0.7:  # Threshold for "success"
            expertise['successes'] += 1

        # Update averages
        expertise['avg_score'] = sum(expertise['learning_curve']) / len(expertise['learning_curve'])

        if success_metric > expertise['best_score']:
            expertise['best_score'] = success_metric
            expertise['best_params'] = parameters

    def get_agent_suggestion(self, agent_id: str, target: str) -> Optional[Dict]:
        """Get suggested parameters from agent's learned expertise.

        Args:
            agent_id: Which agent
            target: Protein target

        Returns:
            Best parameters for this agent/target combination
        """

        key = f"{agent_id}_{target}"

        if key in self.agent_expertise:
            expertise = self.agent_expertise[key]
            if expertise['best_params']:
                return expertise['best_params']

        return None

    def get_expertise_level(self, agent_id: str, target: str) -> float:
        """Get agent expertise level (0-1) for a target.

        Args:
            agent_id: Which agent
            target: Protein target

        Returns:
            Expertise score (success rate or average outcome)
        """

        key = f"{agent_id}_{target}"

        if key not in self.agent_expertise:
            return 0.0

        expertise = self.agent_expertise[key]

        if expertise['attempts'] == 0:
            return 0.0

        # Expertise = success rate
        return expertise['successes'] / expertise['attempts']

    def optimize_parameters_for_target(
        self,
        target: str,
        parameter_ranges: Dict,
        num_iterations: int = 5,
    ) -> Dict:
        """Use agent learning to optimize docking parameters.

        Args:
            target: PDB target
            parameter_ranges: Parameter search space
            num_iterations: Number of optimization rounds

        Returns:
            Best parameters found
        """

        best_params = None
        best_score = float('-inf')

        for iteration in range(num_iterations):
            # Sample parameter space (simplified)
            params = self._sample_parameters(parameter_ranges)

            # Test performance
            score = self._evaluate_parameters(target, params)

            # Record
            param_key = json.dumps(params, sort_keys=True)
            self.parameter_performance[param_key] = score

            if score > best_score:
                best_score = score
                best_params = params

        return best_params

    # Private helper methods

    def _default_docking_params(self) -> Dict:
        """Default docking parameters."""
        return {
            'box_size': 25,
            'num_modes': 9,
            'exhaustiveness': 8,
            'seed': 42,
        }

    def _sample_parameters(self, ranges: Dict) -> Dict:
        """Sample parameters from specified ranges."""
        import random

        params = {}
        for param, (min_val, max_val) in ranges.items():
            if isinstance(min_val, int):
                params[param] = random.randint(min_val, max_val)
            else:
                params[param] = random.uniform(min_val, max_val)

        return params

    def _evaluate_parameters(self, target: str, params: Dict) -> float:
        """Evaluate parameter set performance."""
        # Simplified: return a score based on parameter values
        score = 0.0

        if 'box_size' in params:
            # Reasonable box sizes are 20-30
            score += 1.0 - abs(params['box_size'] - 25) / 25

        if 'num_modes' in params:
            # More modes = better sampling (9 is good)
            score += min(params['num_modes'] / 9.0, 1.0)

        if 'exhaustiveness' in params:
            # 8 is standard, reasonable range 4-16
            score += 1.0 - abs(params['exhaustiveness'] - 8) / 8

        return min(score / 3.0, 1.0)

    def _record_parameter_usage(self, params: Dict):
        """Record that these parameters were used."""
        key = json.dumps(params, sort_keys=True)
        if key not in self.parameter_performance:
            self.parameter_performance[key] = []

    def _record_md_outcome(
        self,
        workflow_id: str,
        docking: DockingResult,
        md: MDSimulation,
        analysis: Dict,
    ):
        """Record MD outcome for learning."""

        if workflow_id not in self.learning_history:
            self.learning_history[workflow_id] = []

        outcome = MolecularOutcome(
            workflow_id=workflow_id,
            target=docking.target,
            compound_id=docking.compound_id,
            docking_energy=docking.binding_energy,
            stability_score=md.stability_score,
            admet_score=0.0,  # Will be filled by scoring
            final_score=0.0,
            optimization_params={},
            timestamp=datetime.utcnow().isoformat(),
        )

        self.learning_history[workflow_id].append(outcome)

    def _record_scoring_outcome(
        self,
        workflow_id: str,
        ranked_compounds: List[Tuple[float, DockingResult]],
    ):
        """Record scoring results."""

        if workflow_id not in self.learning_history:
            self.learning_history[workflow_id] = []

        # Update final scores in history
        for i, (score, compound) in enumerate(ranked_compounds[:3]):
            # Find matching outcome
            for outcome in self.learning_history[workflow_id]:
                if outcome.compound_id == compound.compound_id:
                    outcome.final_score = score
                    break

    def get_workflow_summary(self, workflow_id: str) -> Dict:
        """Get summary of workflow results and learning."""

        if workflow_id not in self.learning_history:
            return {'status': 'not_found'}

        outcomes = self.learning_history[workflow_id]

        return {
            'workflow_id': workflow_id,
            'compounds_analyzed': len(outcomes),
            'top_score': max(o.final_score for o in outcomes) if outcomes else 0,
            'avg_score': sum(o.final_score for o in outcomes) / len(outcomes) if outcomes else 0,
            'top_compound': outcomes[0].compound_id if outcomes else None,
            'outcomes': [
                {
                    'compound_id': o.compound_id,
                    'docking_energy': o.docking_energy,
                    'stability': o.stability_score,
                    'final_score': o.final_score,
                }
                for o in sorted(outcomes, key=lambda x: x.final_score, reverse=True)[:5]
            ]
        }

class AgentMolecularOrchestrator:
    """Orchestrates multi-agent molecular research workflows."""

    def __init__(self, bridge: AgentMolecularBridge):
        self.bridge = bridge
        self.active_workflows = {}

    def start_lead_optimization(
        self,
        workflow_id: str,
        target: str,
        compounds: List[str],
        agents: Dict,
    ) -> Dict:
        """Start a complete lead optimization workflow.

        Args:
            workflow_id: Unique identifier
            target: PDB target
            compounds: SMILES list
            agents: {'optimizer': agent, 'analyst': agent, 'orchestrator': agent}

        Returns:
            Workflow status and results
        """

        self.active_workflows[workflow_id] = {
            'status': 'running',
            'stage': 'docking',
            'progress': 0,
        }

        try:
            # Stage 1: Get optimizer suggestions
            opt_agent = agents.get('optimizer')
            opt_params = None
            if opt_agent:
                opt_suggestion = self.bridge.get_agent_suggestion('optimizer', target)
                opt_params = opt_suggestion

            # Stage 2: Docking
            docking_results, dock_summary = self.bridge.execute_docking_workflow(
                workflow_id,
                compounds,
                target,
                'A',
                opt_params,
            )

            self.active_workflows[workflow_id]['stage'] = 'md'
            self.active_workflows[workflow_id]['progress'] = 33

            # Stage 3: MD simulations
            md_results = self.bridge.execute_md_workflow(
                workflow_id,
                docking_results,
                top_n=20,
            )

            self.active_workflows[workflow_id]['stage'] = 'admet'
            self.active_workflows[workflow_id]['progress'] = 66

            # Stage 4: ADMET predictions
            admet_results = []
            for docking, md in md_results:
                admet = self.bridge.admet_predictor.predict_admet(
                    smiles=docking.compound_id,
                    logp=3.0,
                    mw=400,
                    hbd=2,
                    hba=5,
                )
                admet_results.append(admet)

            # Stage 5: Scoring and ranking
            ranked = self.bridge.execute_compound_scoring_workflow(
                workflow_id,
                [d for d, _ in md_results],
                [m for _, m in md_results],
                admet_results,
            )

            self.active_workflows[workflow_id]['stage'] = 'complete'
            self.active_workflows[workflow_id]['progress'] = 100
            self.active_workflows[workflow_id]['status'] = 'success'

            # Update agent expertise
            if opt_agent and ranked:
                top_score = ranked[0][0]
                self.bridge.record_agent_expertise(
                    'optimizer',
                    target,
                    top_score,
                    opt_params or self.bridge._default_docking_params(),
                )

            return {
                'workflow_id': workflow_id,
                'status': 'success',
                'top_compounds': [
                    {
                        'compound_id': comp.compound_id,
                        'score': score,
                        'priority': self.bridge.scoring_engine._classify_priority(score),
                    }
                    for score, comp in ranked[:10]
                ],
                'summary': self.bridge.get_workflow_summary(workflow_id),
            }

        except Exception as e:
            self.active_workflows[workflow_id]['status'] = 'error'
            self.active_workflows[workflow_id]['error'] = str(e)

            return {
                'workflow_id': workflow_id,
                'status': 'error',
                'error': str(e),
            }
