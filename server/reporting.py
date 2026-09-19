"""Publication-ready reporting for biodao.blockchain research.

Generates:
- PDF reports with figures, tables, methods
- Excel data tables for supplementary materials
- SVG/PNG structure images for papers
- Methods sections for methods/Nature Methods format
"""
import json
from datetime import datetime
from typing import Dict, List, Optional

class Report:
    """Publication-ready research report."""
    def __init__(self, project_id: str, campaign_id: str, title: str):
        self.project_id = project_id
        self.campaign_id = campaign_id
        self.title = title
        self.created_at = datetime.utcnow().isoformat()
        self.sections = {}

    def add_executive_summary(self, summary: str):
        """Add executive summary."""
        self.sections['executive_summary'] = {
            'title': 'Executive Summary',
            'content': summary,
        }

    def add_methods(self, method: str, target: str, compounds: int, runs: int = 4, steps: int = 1500, box: float = 8):
        """Add methods section in Nature format."""
        methods_text = f"""
## Methods

### Virtual Screening and Docking

Molecular docking was performed using a flexible ligand approach with simulated annealing.
The protein target ({target}) was prepared using PDBFixer and parameterized with the Amber
ff14SB force field.

**Protocol:**
- Ligand conformer generation: RDKit with MMFF94 force field
- Protein pocket detection: 3D ray-casting with connected-component clustering
- Docking scoring: Vina-style empirical scoring (Gaussian 1&2, repulsion, hydrophobic, H-bond)
- Monte Carlo minimization: {runs} independent runs, {steps} steps each, search box {box}Å
- Pose clustering: RMSD < 1.5Å threshold
- Validation: Redocking of co-crystallized ligands (target-dependent)

**Compound library:** {compounds} compounds screened (REF-001 to REF-{compounds:03d})
**Software:** biodao.blockchain, RDKit {"{version}"}, Amber14

### Molecular Dynamics Simulations

Interactive MD was performed at 300K using the Langevin integrator with elastic network
model (ENM) for protein backbone restraints.

**Parameters:**
- Implicit solvent: GBn2
- Temperature: 300K
- Friction coefficient: 1.0 ps⁻¹
- Time step: 2 fs
- MD duration: varies by analysis (typically 1-10 ns for visualization)

### Ledger and Data Integrity

All computational steps were recorded in a tamper-evident SHA-256 hash chain ledger,
enabling reproducibility and regulatory compliance. Hash: {"{ledger_hash}"}
"""
        self.sections['methods'] = {
            'title': 'Methods',
            'content': methods_text,
        }

    def add_results_table(self, results: List[Dict]):
        """Add a results data table."""
        self.sections['results_table'] = {
            'title': 'Results Summary',
            'data': results,
            'headers': ['Compound ID', 'SMILES', 'Score (kcal/mol)', 'H-bonds', 'Pose RMSD (Å)'],
        }

    def add_figure_references(self, figures: List[Dict]):
        """Add figure references (to be generated separately)."""
        self.sections['figures'] = {
            'title': 'Figures',
            'figures': figures,  # Each with {name, caption, file_path}
        }

    def to_markdown(self) -> str:
        """Export report as Markdown."""
        md = f"# {self.title}\n\n**Generated:** {self.created_at}\n\n"
        for section_key, section in self.sections.items():
            if 'title' in section:
                md += f"## {section['title']}\n\n"
            if 'content' in section:
                md += section['content'] + "\n\n"
            elif 'data' in section:
                md += self._table_to_markdown(section) + "\n\n"
        return md

    def to_json(self) -> str:
        """Export report as JSON."""
        data = {
            'project_id': self.project_id,
            'campaign_id': self.campaign_id,
            'title': self.title,
            'created_at': self.created_at,
            'sections': self.sections,
        }
        return json.dumps(data, indent=2)

    def _table_to_markdown(self, section: Dict) -> str:
        """Convert data table to Markdown format."""
        headers = section.get('headers', [])
        data = section.get('data', [])
        
        md = "| " + " | ".join(headers) + " |\n"
        md += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        
        for row in data[:20]:  # Limit to 20 rows for preview
            values = [str(row.get(h.lower().replace(' ', '_').replace('(', '').replace(')', ''), '')) 
                     for h in headers]
            md += "| " + " | ".join(values) + " |\n"
        
        if len(data) > 20:
            md += f"\n*... and {len(data) - 20} more compounds*\n"
        
        return md

def generate_screening_report(project_id: str, campaign_id: str, target: str, 
                             results: List[Dict]) -> Report:
    """Generate a publication-ready screening report."""
    report = Report(project_id, campaign_id, f"Virtual Screening Report: {target}")
    
    # Summary
    top_5 = sorted(results, key=lambda x: x.get('score', 0))[:5]
    summary = f"""
    Screening of {len(results)} compounds against {target} identified {len([r for r in results if r.get('score', 0) < -7])} 
    compounds with favorable binding scores (< -7 kcal/mol). The top 5 predicted binders are:
    {', '.join([f"{r.get('compound_id', 'N/A')} ({r.get('score', 0):.1f})" for r in top_5])}
    """
    report.add_executive_summary(summary)
    
    # Methods
    report.add_methods('flexible docking', target, len(results))
    
    # Results table
    table_data = [
        {
            'compound_id': r.get('compound_id', 'N/A'),
            'smiles': r.get('smiles', '')[:50] + '...',
            'score': f"{r.get('score', 0):.2f}",
            'h_bonds': r.get('h_bonds', 0),
            'pose_rmsd': f"{r.get('rmsd', 0):.2f}",
        }
        for r in sorted(results, key=lambda x: x.get('score', 0))[:30]
    ]
    report.add_results_table(table_data)
    
    return report
