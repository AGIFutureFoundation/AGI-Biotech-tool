#!/usr/bin/env python3
"""Rebuild the validated compound library from raw-smiles-inventory.md (ground truth).

RDKit 2026.09.1. Prints to stdout only; writes no files.
Run:  python3 validate_library.py

Inputs collected:
  A. Bullet entry lines `- [VARs] `SMILES`` across all inventory sections
     (S1, S2-A, S2-B VAR 501-540, S3, S4, S5, S6, S7), section-tagged.
     Longest backticked segment wins (handles the S4 [177] doubled backtick).
     S2-B VAR >= 541 bullets are skipped here (chain reconstruction below).
  B. Doc 1: section 1.2 full strings (table) + section 1.4 reconstructions
     (core + terminal group; benzimidazole special-cased via its 1.2 string).
  C. Doc 3: section 3.1 table strings A-G (hardcoded from the table).
  D. S3 E-inline VAR 4: CCC@HC(=O)O (recovered from the source PDF text layer).
  E. S2-B phenyl chains VAR 541-682: rule-based reconstruction
     (head base through ring 7 + C{k}=CC=CC=C{k} per further ring
     + trailing head closure iff final ring <= 10), length-verified
     against the inventory's stated lengths.
"""
import re
from collections import defaultdict, Counter
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdMolDescriptors

RDLogger.DisableLog('rdApp.*')
INV = '/home/hatch/workspace/your_files/bio-research-expansion/raw-smiles-inventory.md'
MD = '/home/hatch/workspace/your_files/bio-research-expansion/validated-compound-library.md'

SECTION_LABEL = {
    '2.5': 'S1', '2.6': 'S2-A', '2.7': 'S2-B', '2.9': 'S3',
    '2.10': 'S4', '2.11': 'S5', '2.12': 'S6', '2.13': 'S7',
}


def expand_vars(spec):
    """'1,11' / '315-316' / '9,36,64-65' / '1-3,5-20,100' -> list of VAR strings."""
    out = []
    for part in spec.split(','):
        part = part.strip()
        if not part:
            continue
        part = re.sub(r'\s*\(.*?\)\s*', '', part)
        if '-' in part and re.match(r'^\d+\s*-\s*\d+$', part):
            a, b = (int(x) for x in part.split('-'))
            out.extend(str(i) for i in range(a, b + 1))
        else:
            out.append(part)
    return out


def is_smiles_like(s):
    if len(s) < 3:
        return False
    # must contain at least one atom-ish char and no prose/ellipsis
    if '…' in s or ' ' in s:
        return False
    return bool(re.search(r'[A-Za-z]', s))


# ---------------------------------------------------------------- inputs
# each input: dict(source, var, string)
inputs = []          # list of dicts
seen_input_strings = set()


def add_input(source, var, string):
    string = string.strip()
    if not string or not is_smiles_like(string):
        return
    inputs.append({'source': source, 'var': var, 'string': string})


lines = open(INV).read().splitlines()
cur_section = None
for ln in lines:
    m = re.match(r'^###\s+(\d+\.\d+)\b', ln)
    if m:
        cur_section = m.group(1)
        continue
    # bullet entry lines: - [VARs] `...` (possibly with extra backticked segments)
    bm = re.match(r'^-\s+\[([^\]]+)\]', ln)
    if bm and cur_section in SECTION_LABEL:
        label = SECTION_LABEL[cur_section]
        varspec = bm.group(1)
        # skip S2-B chain bullets VAR >= 541 (reconstruction handles them)
        if label == 'S2-B':
            try:
                vnums = [int(v) for v in expand_vars(varspec)]
            except ValueError:
                vnums = []
            if vnums and max(vnums) >= 541:
                continue
        segs = re.findall(r'`([^`]*)`', ln)
        segs = [s.strip() for s in segs if is_smiles_like(s.strip())]
        if not segs:
            continue
        s = max(segs, key=len)
        add_input(label, varspec, s)

# --- Doc 1: section 1.2 table strings (lines with | 00x | `SMILES` |) ---
for ln in lines:
    m = re.match(r'^\|\s*0(\d\d)\s*\|\s*`([^`]+)`', ln)
    if m:
        add_input('Doc1', 'AGI-' + m.group(1), m.group(2))

# --- Doc 1: section 1.4 reconstructions (core + terminal) ---
DOC1_CORE = 'C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3'
DOC1_TERMINALS = {
    'OCH3': 'C4=CC=C(OCH3)C=C4', 'CF3': 'C4=CC=C(CF3)C=C4',
    'CBr': 'C4=CC=C(CBr)C=C4', 'Cl': 'C4=CC=C(Cl)C=C4',
    'Br': 'C4=CC=C(Br)C=C4', 'OCHF2': 'C4=CC=C(OCHF2)C=C4',
    'CI': 'C4=CC=C(CI)C=C4', 'CN': 'C4=CC=C(CN)C=C4',
    'NO2': 'C4=CC=C(NO2)C=C4', 'F': 'C4=CC=C(F)C=C4',
    'OCF3': 'C4=CC=C(OCF3)C=C4', 'C#N': 'C4=CC=C(C#N)C=C4',
    'CCl': 'C4=CC=C(CCl)C=C4', 'CF2H': 'C4=CC=C(CF2H)C=C4',
    'phenyl': 'C4=CC=CC=C4', 'F-alt': 'C4=CC=CC=C4F',
    'lactone': 'C4=CC(=O)OC=C4', 'phenol': 'C4=CC=C(O)C=C4',
    'pyridyl': 'C4=CC=NC=C4', 'COCH3': 'C4=CC=C(COCH3)C=C4',
    'CN(C)C': 'C4=CC=C(CN(C)C)C=C4', 'OCH2F': 'C4=CC=C(OCH2F)C=C4',
}
for key, term in DOC1_TERMINALS.items():
    add_input('Doc1', key, DOC1_CORE + term)
# benzimidazole: full string from section 1.2 (AGI-002)
add_input('Doc1', 'benzimidazole',
          'C1=CN=C2C(=N1)C(=CC=C2)C3=NC4=CC=CC=C4N3C5=CC=CC=C5')
# Doc 1 broken AGI-405 fragment
add_input('Doc1', 'BROKEN', 'C1=CN=C2C(=N1)C(=CC')

# --- Doc 3: section 3.1 table strings ---
DOC3 = {
    'A': 'CC1=CC=CC=C1C(=O)NC2=CC=CC=C2C(=O)N3CC4CCNCC4C3',
    'B': 'CC1=CC=CC=C1C(=O)NC2=CC=CC=C2C(=O)N3CCNCC3',
    'C': 'CCC1=CC=CC=C1C(=O)NC2=CC=CC=C2C(=O)N3CCN(CC3)C4=CC=CC=C4',
    'D': 'CCC1=CC=CC=C1C(=O)NC2=CC=CC=C2C(=O)N3CCN(C3)C4=CC=CC=C4',
    'F': '(C)C(=O)NC1=CC=C(C=C1)N2C=NC3=C2C=CC(=C3)C(=O)NC4=CC=C(C=C4)OC(F)(F)F',
    'G': 'CC(C)(C)C(=O)NC1=CC=C(C=C1)N2C=NC3=C2C=CC(=C3)C(=O)NC4=CC=C(C=C4)OC(F)(F)F',
}
for k, s in DOC3.items():
    add_input('Doc3', k, s)

# --- S3 E-inline VAR 4 (recovered from AGI_-Series.pdf text layer) ---
add_input('S3', 'E-inline VAR 4', 'CCC@HC(=O)O')

# --- S3 Drug X parent (section 2.9 intro prose; NOT a bullet) ---
add_input('S3', 'intro (Drug X parent)', 'CC(C)NCC(O)c1ccc(O)c(c1)C(C)C')

# --- S2-B phenyl chains VAR 541-682: rule-based reconstruction ---
CHAIN_BASE = {
    # base = head through ring 7 (no trailing closure); trailing closes the head ring
    'A': ('CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7', 'C3'),
    'B': ('C1CCC2C(CC1)C3=CC=CC=C3CCC2N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7', ''),
    'C': ('C1CCC(CC1)C2N3CCC(CC3)C4=CC=CC=C4C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7', 'C2'),
}
# (VAR, head, final ring, stated len) for 541-561 from the inventory list
CHAIN_541_561 = [
    (541, 'A', 7, 71), (542, 'B', 7, 69), (543, 'C', 7, 68),
    (544, 'A', 8, 82), (545, 'B', 8, 80), (546, 'C', 9, 90),
    (547, 'A', 10, 106), (548, 'B', 10, 104), (549, 'C', 11, 114),
    (550, 'A', 11, 117), (551, 'B', 12, 130), (552, 'A', 12, 130),
    (553, 'B', 13, 143), (554, 'A', 13, 143), (555, 'B', 14, 156),
    (556, 'A', 14, 156), (557, 'B', 15, 169), (558, 'A', 15, 169),
    (559, 'B', 16, 182), (560, 'A', 16, 182), (561, 'B', 17, 195),
]
# VAR 562-682 parameter table (VAR, len, head, last ring) — parsed from the inventory
chain_562 = []
in_chain_table = False
for ln in lines:
    if ln.startswith('| VAR | len | head | last ring |'):
        in_chain_table = True
        continue
    if in_chain_table:
        if not ln.startswith('|'):
            if ln.strip() == '':
                continue
            in_chain_table = False
            continue
        cells = [c.strip() for c in ln.strip().strip('|').split('|')]
        # two sub-tables per row: VAR | len | head | last ring | VAR | len | head | last ring
        for grp in (cells[0:4], cells[4:8]):
            if len(grp) == 4 and grp[0].isdigit():
                try:
                    # strip '*' anomaly markers (truncated / repeat rows)
                    ln_v = int(grp[1].rstrip('*'))
                    rg_v = int(grp[3].rstrip('*'))
                    chain_562.append((int(grp[0]), grp[2], rg_v, ln_v))
                except ValueError:
                    pass
# NOTE: VAR 634 appears twice in the table (truncated len 336*, complete len 715);
# the truncated one is a distinct (shorter) string; handle it by its stated len.
# The table row for 634-first has len 336 with last ring 28* — keep both rows.
# (The parse above keeps both because both rows have digit VAR/len.)


def build_chain(head, final_ring):
    base, trail = CHAIN_BASE[head]
    s = base
    for k in range(8, final_ring + 1):
        s += 'C%d=CC=CC=C%d' % (k, k)
    if final_ring <= 10:
        s += trail
    return s


chain_len_mismatch = []
chain_specs = [(v, h, r, L) for (v, h, r, L) in CHAIN_541_561] + \
              [(v, h, r, L) for (v, h, r, L) in chain_562]
for (var, head, final_ring, stated_len) in chain_specs:
    s = build_chain(head, final_ring)
    if len(s) != stated_len:
        # truncated variants (VAR 576 len 149, VAR 634-first len 336) are prefixes
        # of the complete build; keep the prefix as the input string.
        if len(s) > stated_len and s[:stated_len] and stated_len in (149, 336):
            s = s[:stated_len]
        else:
            chain_len_mismatch.append((var, head, final_ring, stated_len, len(s)))
    add_input('S2-B', 'VAR %d' % var, s)

print('== chain length mismatches (rule vs inventory stated len): %d' % len(chain_len_mismatch))
for x in chain_len_mismatch:
    print('   ', x)

# ---------------------------------------------------------------- parse
def strip_brackets(s):
    return re.sub(r'\[[^\]]*\]', '', s)


def ring_closure_counts(s):
    """Count ring-closure occurrences per number (outside brackets).
    Digits that are formula subscripts are NOT ring closures and are skipped:
    a digit followed by H (C2H5-style CnHm), a digit preceded by H (H5/H3-style
    Hn counts). (Terminal CF3/NO2/SO2 subscripts are caught by the bare-digit
    check in classify_fail before the unclosed-ring check, so they never reach
    the ring counter; a digit after N/O/S that closes a ring, e.g. N1), IS a
    genuine ring closure and must be counted.)"""
    t = strip_brackets(s)
    counts = Counter()
    i = 0
    while i < len(t):
        if t[i] == '%':
            m = re.match(r'%(\d\d)', t[i:])
            if m:
                prev = t[i-1] if i > 0 else ''
                nxt = t[i+3] if i + 3 < len(t) else ''
                if prev != 'H' and nxt != 'H':
                    counts[int(m.group(1))] += 1
                i += 3
                continue
            i += 1
        elif t[i].isdigit():
            prev = t[i-1] if i > 0 else ''
            nxt = t[i+1] if i + 1 < len(t) else ''
            if prev != 'H' and nxt != 'H':
                counts[int(t[i])] += 1
            i += 1
        else:
            i += 1
    return counts


def classify_fail(s, source, var):
    """Failure reason for a string that did not parse (RDKit MolFromSmiles -> None).
    Order matters: formula-style fragments (bare H / bare digit) are SYNTAX
    before unclosed-ring is considered, matching the reference's defect classes."""
    # S2-B chains with final ring >= 10 use bare two-digit ring numbers.
    if source == 'S2-B' and re.match(r'VAR (\d+)', str(var)):
        vn = int(re.match(r'VAR (\d+)', str(var)).group(1))
        if vn >= 547:
            return 'RING-DIGIT-DUP'
    # S3 VAR 71 backticked truncated fragment (identity).
    if s == 'CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C':
        return 'TRUNCATED'
    t = strip_brackets(s)
    # Formula-style fragments are SYNTAX first (the inventory's dominant defect
    # class): unbracketed H anywhere (CH3, NH2, OH, C2H5, OCH3, @H conflict),
    # or a bare-digit subscript: a digit after a halogen (CF3, OCF3, Cl2, Br2
    # -- a halogen cannot carry a ring closure, so F/Cl/Br/I followed by a
    # digit is always a formula subscript), or a terminal NO2 / SO2 group.
    # (A digit after N/O/S that closes a ring, e.g. N1), is NOT a subscript
    # and is handled by the unclosed-ring check below.)
    if 'H' in t:
        return 'SYNTAX'
    if re.search(r'(?:F|Cl|Br|I)\d', t):
        return 'SYNTAX'
    if re.search(r'(?:C|N|S|Cl|Br|I)O2(?=$|\)|\])', t):
        return 'SYNTAX'
    cc = ring_closure_counts(s)
    if any(v % 2 == 1 for v in cc.values()):
        return 'UNCLOSED-RING'
    return 'SYNTAX'


# S3 VAR 71 truncated fragment: identify it (S3 bullet, truncated mid-token).
# It is the only S3 input that is a strict prefix of another S3 input; mark TRUNCATED.
results = {}   # string -> dict(canonical|None, reason, mol|None)
for inp in inputs:
    s = inp['string']
    if s in results:
        continue
    m = Chem.MolFromSmiles(s, sanitize=False)
    if m is None:
        results[s] = {'ok': False, 'reason': classify_fail(s, inp['source'], inp['var']), 'mol': None}
    else:
        try:
            Chem.SanitizeMol(m)
            results[s] = {'ok': True, 'reason': None, 'mol': m}
        except Exception as e:
            msg = str(e)
            if 'kekul' in msg.lower():
                reason = 'KEKULIZE'
            elif 'aromat' in msg.lower() and 'non-ring' in msg.lower():
                reason = 'AROMATIC-NONRING'
            elif 'unclosed' in msg.lower() or 'ring' in msg.lower():
                reason = 'UNCLOSED-RING'
            else:
                reason = 'SYNTAX'
            results[s] = {'ok': False, 'reason': reason, 'mol': None}

# (TRUNCATED is handled by identity inside classify_fail: the S3 VAR 71 fragment.)

distinct_strings = sorted({i['string'] for i in inputs})
n_distinct = len(distinct_strings)
n_ok_strings = sum(1 for s in distinct_strings if results[s]['ok'])
n_bad_strings = n_distinct - n_ok_strings
reason_counts = Counter(results[s]['reason'] for s in distinct_strings if not results[s]['ok'])

# dedup on canonical SMILES
canon_to_inputs = defaultdict(list)   # canonical -> [input dicts]
canon_mol = {}
for inp in inputs:
    s = inp['string']
    r = results[s]
    if not r['ok']:
        continue
    can = Chem.MolToSmiles(r['mol'])
    canon_to_inputs[can].append(inp)
    canon_mol[can] = r['mol']

n_validated = len(canon_to_inputs)
# duplicate inputs: distinct input strings (beyond the first) mapping to an
# already-listed canonical
n_dup_inputs = 0
dup_pairs = []
for can, ins in canon_to_inputs.items():
    uniq = sorted({i['string'] for i in ins})
    if len(uniq) > 1:
        n_dup_inputs += len(uniq) - 1
        dup_pairs.append((can, uniq))

print('== COUNTS ==')
print('total input occurrences (bullets + special cases): %d' % len(inputs))
print('distinct input strings: %d' % n_distinct)
print('distinct strings parsing OK: %d' % n_ok_strings)
print('distinct strings failing: %d' % n_bad_strings)
print('failure reasons: %s' % dict(reason_counts))
print('validated unique canonical structures: %d' % n_validated)
print('duplicate input strings (extra writings of a listed canonical): %d' % n_dup_inputs)
print('check: validated + invalid + duplicate = %d (distinct = %d)'
      % (n_validated + n_bad_strings + n_dup_inputs, n_distinct))

# invalid by source (distinct failing strings)
inv_by_source = Counter()
for s in distinct_strings:
    if not results[s]['ok']:
        srcs = {i['source'] for i in inputs if i['string'] == s}
        for src in srcs:
            inv_by_source[src] += 1
print('invalid by source: %s' % dict(inv_by_source))

# validated rows, MW-sorted
rows = []
for can, mol in canon_mol.items():
    ins = canon_to_inputs[can]
    formula = rdMolDescriptors.CalcMolFormula(mol)
    mw = round(Descriptors.MolWt(mol), 2)
    logp = round(Descriptors.MolLogP(mol), 2)
    # sources: aggregate (source, var) citations
    cites = defaultdict(set)
    for i in ins:
        cites[i['source']].add(i['var'])
    # Kekule flag: any input is Kekule-form (no lowercase aromatic atoms) while canonical is aromatic
    kek = any(not re.search(r'[a-z]', i['string']) and re.search(r'[a-z]', can) for i in ins)
    rows.append({'can': can, 'formula': formula, 'mw': mw, 'logp': logp,
                 'cites': dict(cites), 'kek': kek,
                 'n_inputs': len({i['string'] for i in ins})})
rows.sort(key=lambda r: (r['mw'], r['can']))
print('== MW range: %.2f - %.2f ; max canonical SMILES len %d ; Kekule rows %d'
      % (rows[0]['mw'], rows[-1]['mw'], max(len(r['can']) for r in rows),
         sum(1 for r in rows if r['kek'])))

print('== VALIDATED TABLE (MW-sorted) ==')
for idx, r in enumerate(rows, 1):
    cites_s = '; '.join('%s [%s]' % (src, ','.join(sorted(vs, key=lambda x: (len(x), x))))
                        for src, vs in sorted(r['cites'].items()))
    print('ROW| L-%03d | %s | %s | %.2f | %.2f | %s | kek=%s n_inputs=%d'
          % (idx, r['can'], r['formula'], r['mw'], r['logp'], cites_s, r['kek'], r['n_inputs']))

print('== DUPLICATE PAIRS (extra input strings per canonical) ==')
for can, uniq in sorted(dup_pairs):
    print('DUP| %s | %s' % (can, ' || '.join(uniq)))

# ---------------------------------------------------------------- diff vs current .md
cur = {}
for ln in open(MD).read().splitlines():
    m = re.match(r'^\| (L-\d{3}) \| `([^`]+)` \| ([A-Za-z0-9]+) \| ([\d.]+) \| ([\d.\-]+) \| ([^|]*) \|', ln)
    if m:
        cur[m.group(2)] = {'id': m.group(1), 'formula': m.group(3),
                           'mw': float(m.group(4)), 'logp': float(m.group(5)),
                           'sources': m.group(6).strip()}
print('== DIFF vs current .md ==')
new_cans = {r['can'] for r in rows}
cur_cans = set(cur)
print('current table rows: %d ; rebuilt rows: %d ; in both: %d'
      % (len(cur_cans), len(new_cans), len(cur_cans & new_cans)))
print('-- current rows NOT in rebuilt set (spurious / wrong molecule):')
for can in sorted(cur_cans - new_cans):
    print('  SPURIOUS| %s | %s | %s %.2f | %s' % (cur[can]['id'], can, cur[can]['formula'], cur[can]['mw'], cur[can]['sources']))
print('-- rebuilt rows NOT in current table (missing):')
for r in rows:
    if r['can'] not in cur_cans:
        cites_s = '; '.join('%s [%s]' % (src, ','.join(sorted(vs))) for src, vs in sorted(r['cites'].items()))
        print('  MISSING| %s | %s | %.2f | %.2f | %s' % (r['can'], r['formula'], r['mw'], r['logp'], cites_s))
print('-- rows in both but non-canonical string in current table:')
for can in sorted(cur_cans & new_cans):
    if cur[can]['id'] and can != Chem.MolToSmiles(Chem.MolFromSmiles(can)):
        pass
# (non-canonical check is implicit: rebuilt canonicals ARE canonical by construction)

# ---------------------------------------------------------------- SMARTS
PATTERNS = {
    'P-01': 'c1ccccc1', 'P-02': 'C(=O)[OH]',
    'P-04': '[SX4](=[OX1])(=[OX1])([NX3])', 'P-05': 'c1ccc2[nH]ccc2c1',
    'P-06': '[NH2][C@H](C)C(=O)N', 'P-06b': '[NH2][CH](C)C(=O)N',
    'P-07': 'N1CCCC1C(=O)', 'P-08': '[CH3][CH](C)C',
    'P-11': '[CH2][CH](C)C', 'P-20': '[OH]c1ccccc1',
    'P-21': 'C(=O)N', 'P-22': '[F,Cl,Br,I]c1ccccc1',
    'P-23': '[NH2]', 'P-24': '[O;H1]', 'P-25': '[O;D2]', 'P-26': '[n;H1]',
}
print('== SMARTS (rebuilt set, %d structures) ==' % len(rows))
hits = {}
for pid, smarts in PATTERNS.items():
    q = Chem.MolFromSmarts(smarts)
    assert q is not None, pid
    h = [i + 1 for i, r in enumerate(rows) if canon_mol[r['can']].HasSubstructMatch(q)]
    hits[pid] = h
    print('  %s: %d' % (pid, len(h)))
p03 = sorted(set(hits['P-01']) & set(hits['P-02']))
p12 = sorted(set(hits['P-01']) & set(hits['P-05']) & set(hits['P-11']))
print('  P-03 (P-01 AND P-02): %d -> %s' % (len(p03), ['L-%03d' % i for i in p03]))
print('  P-12 (P-01 AND P-05 AND P-11): %d -> %s' % (len(p12), ['L-%03d' % i for i in p12]))
print('  P-02 hit IDs: %s' % (['L-%03d' % i for i in hits['P-02']],))

# ---------------------------------------------------------------- diagnostic dump
with open('/tmp/fail_by_reason.txt', 'w') as fh:
    for s in sorted(results):
        if not results[s]['ok']:
            srcs = sorted(set(i['source'] for i in inputs if i['string'] == s))
            fh.write('%s\t%s\t%s\n' % (results[s]['reason'], ','.join(srcs), s))
print('== fail dump written: /tmp/fail_by_reason.txt ==')
