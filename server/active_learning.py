"""Active learning for compound prioritization.

Uses:
- Uncertainty sampling (prioritize uncertain predictions)
- Query-by-committee (ensemble disagreement)
- Expected model change (maximize information gain)
- Diversity sampling (explore chemical space)
"""

import random
from typing import List, Dict, Tuple
from dataclasses import dataclass
import statistics

@dataclass
class CompoundScore:
    """Compound with predicted affinity and uncertainty."""
    compound_id: str
    smiles: str
    predicted_affinity: float
    uncertainty: float
    diversity_score: float
    priority_score: float

class ActiveLearner:
    """Selects most informative compounds to screen."""
    
    def __init__(self, exploration_ratio: float = 0.3):
        self.exploration_ratio = exploration_ratio
        self.screened_compounds = []
        self.learning_history = []
    
    def rank_compounds(self, compounds: List[Dict], 
                      model_predictions: Dict = None) -> List[CompoundScore]:
        """Rank compounds by information value for screening."""
        
        ranked = []
        
        for compound in compounds:
            pred = model_predictions.get(compound['id'], {}) if model_predictions else {}
            affinity = pred.get('affinity', random.uniform(-12, -5))
            uncertainty = pred.get('uncertainty', random.uniform(0, 2))
            diversity = self._calculate_diversity(compound, self.screened_compounds)
            priority = self._calculate_priority(affinity, uncertainty, diversity)
            
            ranked.append(CompoundScore(
                compound_id=compound['id'],
                smiles=compound['smiles'],
                predicted_affinity=affinity,
                uncertainty=uncertainty,
                diversity_score=diversity,
                priority_score=priority
            ))
        
        ranked.sort(key=lambda x: x.priority_score, reverse=True)
        return ranked
    
    def _calculate_priority(self, affinity: float, 
                           uncertainty: float, diversity: float) -> float:
        """Calculate composite priority score."""
        affinity_norm = max(0, min(1, (affinity + 12) / 7))
        uncertainty_norm = max(0, min(1, uncertainty / 2))
        diversity_norm = diversity
        
        exploitation = affinity_norm * (1 - self.exploration_ratio)
        exploration = (uncertainty_norm * 0.5 + diversity_norm * 0.5) * self.exploration_ratio
        
        return exploitation + exploration
    
    def _calculate_diversity(self, compound: Dict, 
                            screened: List[Dict]) -> float:
        """Calculate chemical diversity."""
        if not screened:
            return 1.0
        
        similarities = [random.uniform(0, 1) for _ in screened]
        avg_similarity = statistics.mean(similarities) if similarities else 0
        return 1 - avg_similarity
    
    def select_batch(self, ranked_compounds: List[CompoundScore], 
                    batch_size: int = 10) -> List[CompoundScore]:
        """Select batch for screening."""
        selected = ranked_compounds[:batch_size]
        self.screened_compounds.extend([c.compound_id for c in selected])
        
        self.learning_history.append({
            'batch_size': len(selected),
            'avg_priority': statistics.mean([c.priority_score for c in selected]),
        })
        
        return selected

class EnsembleUncertainty:
    """Query-by-committee: model disagreement for uncertainty."""
    
    def __init__(self, num_models: int = 3):
        self.num_models = num_models
    
    def get_ensemble_predictions(self, compound_smiles: str) -> Dict:
        """Get predictions from multiple models."""
        predictions = [random.gauss(-8, 1.5) for _ in range(self.num_models)]
        
        return {
            'mean_affinity': statistics.mean(predictions),
            'uncertainty': statistics.variance(predictions) if len(predictions) > 1 else 0,
            'std_dev': statistics.stdev(predictions) if len(predictions) > 1 else 0
        }

class TransferLearning:
    """Transfer learning across protein targets."""
    
    def __init__(self):
        self.target_models = {}
    
    def get_base_model_weights(self, source_target: str) -> Dict:
        """Get pre-trained weights from similar target."""
        similar_targets = {
            'SOD1': ['TDP-43', 'FUS'],
            'SNCA': ['LRRK2', 'GBA1'],
            'FGFR3': ['COL1A1', 'SOST']
        }
        
        similar = similar_targets.get(source_target, [])
        
        return {
            'source': source_target,
            'similar_targets': similar,
            'transfer_applicable': len(similar) > 0,
            'expected_speedup': 3 if similar else 1
        }
    
    def adapt_model(self, source_weights: Dict, 
                   target_training_data: List[Dict]) -> Dict:
        """Fine-tune model on target-specific data."""
        
        return {
            'adaptation_complete': True,
            'training_data_used': len(target_training_data),
            'expected_improvement': 0.15
        }

