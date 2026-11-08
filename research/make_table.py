"""Generate the validated-library markdown table rows from the rebuild output.

Reads /tmp/rebuild_out8.txt (ROW + DUP lines from validate_library.py) and the
current validated-compound-library.md (for carried-over special notes), and
prints the markdown table rows for a given L-ID range, one row per line, in
exactly the format used in the deliverable.

Usage: python3 make_table.py <first> <last>   (e.g. 1 70)
"""
import re
import sys

KEK = 'Kekulé input → aromatic canonical (normal conversion)'

cur = {}
for ln in open('/home/hatch/workspace/your_files/bio-research-expansion/validated-compound-library.md'):
    m = re.match(r'^\| (L-\d{3}) \| `([^`]+)` \| ([A-Za-z0-9]+) \| ([\d.]+) \| ([\d.\-]+) \| ([^|]*) \| ([^|]*) \|', ln)
    if m:
        cur[m.group(2)] = m.group(7).strip()

def clean_note(note):
    n = note.replace(KEK, '')
    n = re.sub(r'Also written as:[^;]*', '', n)
    n = re.sub(r"\['([^']+)'\]", r'\1', n)
    n = re.sub(r"\['([^']+)', '([^']+)'\]", r'\1, \2', n)
    n = re.sub(r"\['([^']+)', '([^']+)', '([^']+)'\]", r'\1, \2, \3', n)
    n = re.sub(r';\s*;', ';', n).strip(' ;')
    return n

dups = {}
for ln in open('/tmp/rebuild_out8.txt'):
    m = re.match(r'^DUP\| (\S+) \| (.+)$', ln)
    if m:
        dups[m.group(1)] = [p.strip() for p in m.group(2).split('||')]

rows = []
for ln in open('/tmp/rebuild_out8.txt'):
    m = re.match(r'^ROW\| (L-\d{3}) \| (\S+) \| (\S+) \| ([\d.]+) \| ([\d.\-]+) \| ([^|]+) \| kek=(True|False) n_inputs=(\d+)', ln)
    if m:
        rows.append(m.groups())

def fmt_sources(s):
    out = []
    for p in [x.strip() for x in s.strip().split(';')]:
        m = re.match(r'^(\S+)\s+\[(.+)\]$', p)
        out.append('%s: [%s]' % (m.group(1), m.group(2)) if m else p)
    return '; '.join(out)

OVERRIDE = {
    # Doc1 key rows (doc-claimed MW/LogP carried from the first-pass table;
    # the first-pass file was overwritten by the rebuild, so these are pinned
    # here by canonical SMILES rather than read back from it).
    'c1ccc(-n2ccnc2-c2cccc3nccnc23)cc1':
        'Doc1 key phenyl; doc-claimed MW 301.32 / LogP 3.1 (doc-claimed, unvalidated)',
    'c1cc(-c2nccn2-c2ccncc2)c2nccnc2c1':
        'Doc1 key pyridyl; doc-claimed MW 286.32 / LogP 2.8 (doc-claimed, unvalidated)',
    'Oc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1':
        'Doc1 key phenol; doc-claimed MW 307.31 / LogP 2.5 (doc-claimed, unvalidated)',
    'O=c1cc(-n2ccnc2-c2cccc3nccnc23)cco1':
        'Doc1 key lactone; doc-claimed MW 331.32 / LogP 2.9 (doc-claimed, unvalidated)',
    'Fc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1':
        'Doc1 key F; doc-claimed MW 319.32 / LogP 3.4 (doc-claimed, unvalidated); para-F isomer — distinct from the ortho-F (F-alt) row; inventory "same molecule" claim is wrong (§10)',
    'Fc1ccccc1-n1ccnc1-c1cccc2nccnc12':
        'Doc1 key F-alt; doc-claimed MW 319.32 / LogP 3.4 (doc-claimed, unvalidated); ortho-F isomer — distinct from the para-F (F) row; inventory "same molecule" claim is wrong (§10)',
    'N#Cc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1':
        'Doc1 key C#N; doc-claimed MW 302.32 / LogP 3.2, 3.3 (doc-claimed, unvalidated)',
    'NCc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1':
        'Doc1 key CN; doc-claimed MW 305.31 / LogP 2.5 (doc-claimed, unvalidated)',
    'Clc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1':
        'Doc1 key Cl; doc-claimed MW 317.76 / LogP 3.7, 3.8 (doc-claimed, unvalidated)',
    'ClCc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1':
        'Doc1 key CCl; doc-claimed MW 331.21 / LogP 3.7 (doc-claimed, unvalidated)',
    'c1ccc(-n2c(-c3cccc4nccnc34)nc3ccccc32)cc1':
        'Doc1 key benzimidazole; doc-claimed MW 371.40 / LogP 4.2 (doc-claimed, unvalidated)',
    'CN(C)Cc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1':
        'Doc1 key CN(C)C; doc-claimed MW 335.35 / LogP 3.2 (doc-claimed, unvalidated)',
    'Brc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1':
        'Doc1 key Br; doc-claimed MW 353.32, 363.32 / LogP 3.5, 3.9, 4.1 (doc-claimed, unvalidated); Doc1 AGI-183 (catalog, CRBN/FLIP) — DO NOT MERGE with AGI-183 paper row X-02 (§4/§10)',
    'BrCc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1':
        'Doc1 key CBr; doc-claimed MW 371.21 / LogP 4.0 (doc-claimed, unvalidated)',
    'ICc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1':
        'Doc1 key CI; doc-claimed MW 397.20 / LogP 4.5 (doc-claimed, unvalidated)',
    # Doc3 rows.
    'Cc1ccccc1C(=O)Nc1ccccc1C(=O)N1CCNCC1':
        'Doc3 B; doc-claimed MW 296.34 (x68; once 426.55 — same SMILES, two MWs)',
    'Cc1ccccc1C(=O)Nc1ccccc1C(=O)N1CC2CCNCC2C1':
        'Doc3 A; doc-claimed MW 342.41 (x71; once 296.34 — same SMILES, two MWs)',
    'CCc1ccccc1C(=O)Nc1ccccc1C(=O)N1CCN(c2ccccc2)C1':
        'Doc3 D — typo variant of C (missing piperazine carbon; 5-ring, not 6-ring); doc-claimed MW 426.55 (x2)',
    'CCc1ccccc1C(=O)Nc1ccccc1C(=O)N1CCN(c2ccccc2)CC1':
        'Doc3 C; doc-claimed MW 426.55 (x67)',
    # Riluzole parent (S5).
    'CN(Cc1ccc(C(=O)Nc2ccccc2)cc1)c1ccccc1':
        'Doc-claimed riluzole parent (benzamide-like) — MISMATCH vs PubChem riluzole (§7)',
    'CC(O)CCOCP(=O)(COC(N)=O)COC(=O)N1CCC(O)(c2nccc(N)n2)C1':
        'Tenofovir-like phosphonate (S7) — isomeric/phosphonate pair duplicate (see §6)',
    'CC(C)(C)C(=O)Nc1ccc(-n2cnc3cc(C(=O)Nc4ccc(OC(F)(F)F)cc4)ccc32)cc1':
        'Doc3 G (full form); doc-claimed venetoclax parent — MISMATCH vs PubChem venetoclax (§7)',
    'CC(C)C(C(=O)NC1CCC(C(C(=O)O)(c2ccccc2)c2ccccc2)CC1)c1ccc(-c2ccccc2)cc1':
        'Doc-claimed atorvastatin-like parent (VAR 4 form) — MISMATCH vs PubChem atorvastatin (§7)',
}

def gen_row(r):
    lid, can, form, mw, logp, src, kek, nin = r
    special = OVERRIDE.get(can, clean_note(cur.get(can, '')))
    bits = []
    if special:
        bits.append(special)
    if can in dups:
        alt = [s for s in dups[can] if s != can]
        if alt:
            bits.append('Also written as: ' + '; '.join('`%s`' % a for a in alt))
    if kek == 'True':
        bits.append(KEK)
    if re.search(r'VAR 54[1-6]\b', src):
        bits.append('S2 phenyl-chain reconstruction (see Method)')
    return '| %s | `%s` | %s | %s | %s | %s | %s |' % (
        lid, can, form, mw, logp, fmt_sources(src), '; '.join(bits))

first, last = int(sys.argv[1]), int(sys.argv[2])
for r in rows[first - 1:last]:
    print(gen_row(r))
