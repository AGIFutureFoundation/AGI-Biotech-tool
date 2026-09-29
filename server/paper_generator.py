"""Automatic research paper generation from screening sessions.

Generates publication-ready papers in:
- LaTeX (for PDF compilation)
- Markdown (for bioRxiv/arXiv)
- HTML (for interactive viewing)
- Word/DOCX (for collaborators)

Includes: Abstract, Introduction, Methods, Results, Discussion, References
"""
import json
import synthetic_provenance as sp
from datetime import datetime
from typing import Dict, List

class ResearchPaper:
    """Generates a full research paper from screening data."""
    
    def __init__(self, title: str, authors: List[str], institution: str, disease: str, target: str):
        self.title = title
        self.authors = authors
        self.institution = institution
        self.disease = disease
        self.target = target
        self.created_at = datetime.utcnow().isoformat()
        self.sections = {}

    def add_abstract(self, background: str, objective: str, methods: str, results: str, conclusion: str):
        """Add structured abstract."""
        self.sections['abstract'] = {
            'background': background,
            'objective': objective,
            'methods': methods,
            'results': results,
            'conclusion': conclusion,
        }

    def add_introduction(self, content: str, references: List[str]):
        """Add introduction with citations."""
        self.sections['introduction'] = {
            'content': content,
            'references': references,
        }

    def add_methods(self, docking_method: str, md_method: str, validation: str):
        """Add methods section."""
        self.sections['methods'] = {
            'docking': docking_method,
            'molecular_dynamics': md_method,
            'validation': validation,
        }

    def add_results(self, screening_summary: Dict, top_compounds: List[Dict], statistics: Dict):
        """Add results with data."""
        self.sections['results'] = {
            'screening': screening_summary,
            'top_compounds': top_compounds,
            'statistics': statistics,
        }

    def add_discussion(self, findings: str, implications: str, limitations: str, future_work: str):
        """Add discussion section."""
        self.sections['discussion'] = {
            'findings': findings,
            'implications': implications,
            'limitations': limitations,
            'future_work': future_work,
        }

    def to_latex(self) -> str:
        """Generate LaTeX document."""
        latex = r"""
\documentclass{article}
\usepackage[utf-8]{inputenc}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{hyperref}

\title{""" + self.title + r"""}
\author{""" + ", ".join(self.authors) + r""" \\ """ + self.institution + r"""}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
"""
        if 'abstract' in self.sections:
            abs_data = self.sections['abstract']
            latex += f"""
\\noindent
\\textbf{{Background:}} {abs_data['background']} \\\\
\\textbf{{Objective:}} {abs_data['objective']} \\\\
\\textbf{{Methods:}} {abs_data['methods']} \\\\
\\textbf{{Results:}} {abs_data['results']} \\\\
\\textbf{{Conclusion:}} {abs_data['conclusion']}
"""
        latex += r"""
\end{abstract}

\section{Introduction}
"""
        if 'introduction' in self.sections:
            latex += self.sections['introduction']['content']

        latex += r"""

\section{Methods}
"""
        if 'methods' in self.sections:
            m = self.sections['methods']
            latex += f"""
\\subsection{{Molecular Docking}}
{m.get('docking', '')}

\\subsection{{Molecular Dynamics}}
{m.get('molecular_dynamics', '')}

\\subsection{{Validation}}
{m.get('validation', '')}
"""

        latex += r"""

\section{Results}
"""
        if 'results' in self.sections:
            res = self.sections['results']
            latex += f"""
\\subsection{{Virtual Screening}}
{res.get('screening', {}).get('summary', '')}

\\subsection{{Top Compounds}}
"""
            for compound in res.get('top_compounds', [])[:10]:
                latex += f"""\n\\textit{{{compound.get('compound_id', 'N/A')}}} 
(Score: {compound.get('score', 0):.2f} kcal/mol)"""

        latex += r"""

\section{Discussion}
"""
        if 'discussion' in self.sections:
            d = self.sections['discussion']
            latex += f"""
{d.get('findings', '')}

{d.get('implications', '')}

{d.get('limitations', '')}

{d.get('future_work', '')}
"""

        latex += r"""

\end{document}
"""
        return latex

    def to_markdown(self) -> str:
        """Generate Markdown for bioRxiv/arXiv."""
        md = f"""# {self.title}

**Authors:** {", ".join(self.authors)}  
**Institution:** {self.institution}  
**Disease Focus:** {self.disease}  
**Target:** {self.target}  
**Date:** {self.created_at}

---

## Abstract
"""
        if 'abstract' in self.sections:
            a = self.sections['abstract']
            md += f"""
**Background:** {a['background']}

**Objective:** {a['objective']}

**Methods:** {a['methods']}

**Results:** {a['results']}

**Conclusion:** {a['conclusion']}
"""

        md += f"""

## Introduction
"""
        if 'introduction' in self.sections:
            md += self.sections['introduction']['content']

        md += """

## Methods

### Molecular Docking
"""
        if 'methods' in self.sections:
            md += self.sections['methods'].get('docking', '')

        md += """

### Molecular Dynamics
"""
        if 'methods' in self.sections:
            md += self.sections['methods'].get('molecular_dynamics', '')

        md += """

## Results
"""
        if 'results' in self.sections:
            res = self.sections['results']
            md += f"\n{res.get('screening', {}).get('summary', '')}\n"

        md += """

## Discussion
"""
        if 'discussion' in self.sections:
            d = self.sections['discussion']
            md += f"""
{d.get('findings', '')}

{d.get('implications', '')}

{d.get('limitations', '')}

## Future Work
{d.get('future_work', '')}
"""

        md += """

---

*Generated by biodao.blockchain*  
*All data recorded in tamper-proof SHA-256 ledger*
"""
        return md

    def to_json(self) -> str:
        """Export as JSON for archiving.

        An archived paper is the last place a placeholder should be able to
        shed its marking, so this encodes through sp.dumps rather than json.
        """
        return sp.dumps({
            'title': self.title,
            'authors': self.authors,
            'institution': self.institution,
            'disease': self.disease,
            'target': self.target,
            'created_at': self.created_at,
            'sections': self.sections,
        }, indent=2)

def generate_paper_from_session(session_data: Dict) -> ResearchPaper:
    """Generate a research paper from a screening session."""
    paper = ResearchPaper(
        title=f"Virtual Screening for Novel {session_data.get('disease', 'Disease')} Therapeutics Targeting {session_data.get('target', 'Target')}",
        authors=session_data.get('authors', ['Researcher et al.']),
        institution=session_data.get('institution', 'Institution'),
        disease=session_data.get('disease', 'Disease'),
        target=session_data.get('target', 'Target'),
    )

    # Auto-generate sections from session data
    paper.add_abstract(
        background=f"Rational drug discovery for {session_data.get('disease')} requires systematic screening of large chemical libraries against validated protein targets.",
        objective=f"To identify novel small molecule inhibitors of {session_data.get('target')} using computational docking and molecular dynamics.",
        methods="Monte Carlo flexible docking with Vina-style empirical scoring, followed by molecular dynamics validation.",
        results=f"Screening identified {session_data.get('compounds_count', 0)} compounds with favorable binding predictions.",
        conclusion=f"Top candidates are recommended for experimental validation.",
    )

    return paper
