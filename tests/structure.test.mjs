// Offline checks for the structure parsers in js/structure.js.
//
// This is the stage upstream of everything — pockets, docking, refinement, dynamics, analysis all read what
// these functions produce. A column misread here does not announce itself; it comes out the other end as a
// slightly wrong answer that looks like a slightly wrong score.
//
// PDB is a fixed-column format, not a whitespace-delimited one, and the test that matters most is the one
// that proves the parser knows the difference: coordinates like "-123.456-123.456" have no space between
// them and a splitting parser reads one number where there are two.
//
// Fixtures are hand-written PDB and mmCIF text with the columns counted out, so every expectation is
// derived from the format specification rather than from the implementation's current behaviour.
//
//   node --test tests/structure.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { parsePDB, parsePDBFrames, parseMmCIF, parseMolblock, parseAny } from '../js/structure.js';

// PDB ATOM record columns, 1-based, from the format specification:
//   1-6 record  7-11 serial  13-16 name  17 altLoc  18-20 resName  22 chainID  23-26 resSeq  27 iCode
//   31-38 x  39-46 y  47-54 z  55-60 occupancy  61-66 tempFactor  77-78 element
const L = (s) => s;
const pdb = (...lines) => lines.join('\n') + '\n';

test('a single ATOM record is read out of its columns, field by field', () => {
  const st = parsePDB(pdb(
    L('ATOM     12  CB  LEU B 345      11.104 -13.207   8.500  1.00 27.43           C'),
  ));
  assert.equal(st.n, 1);
  assert.equal(st.atomName[0], 'CB');
  assert.equal(st.resName[0], 'LEU');
  assert.equal(st.chain[0], 'B');
  assert.equal(st.resSeq[0], 345);
  assert.equal(st.element[0], 'C');
  assert.ok(Math.abs(st.pos[0] - 11.104) < 1e-3, `x was ${st.pos[0]}`);
  assert.ok(Math.abs(st.pos[1] + 13.207) < 1e-3, `y was ${st.pos[1]}`);
  assert.ok(Math.abs(st.pos[2] - 8.5) < 1e-3, `z was ${st.pos[2]}`);
  assert.ok(Math.abs(st.bfac[0] - 27.43) < 1e-2, `B-factor was ${st.bfac[0]}`);
  assert.equal(st.het[0], 0, 'an ATOM record is not a heteroatom');
});

test('coordinates packed with no separating space are still three numbers', () => {
  // The classic failure: a parser that splits on whitespace reads "-123.456-123.456" as one token.
  const st = parsePDB(pdb(
    L('ATOM      1  C   LIG X   1    -123.456-123.456 -99.999  1.00  0.00           C'),
  ));
  assert.equal(st.n, 1);
  assert.ok(Math.abs(st.pos[0] + 123.456) < 1e-3, `x was ${st.pos[0]}`);
  assert.ok(Math.abs(st.pos[1] + 123.456) < 1e-3, `y was ${st.pos[1]}`);
  assert.ok(Math.abs(st.pos[2] + 99.999) < 1e-3, `z was ${st.pos[2]}`);
});

test('the element comes from columns 77-78, and is inferred from the name when they are blank', () => {
  const st = parsePDB(pdb(
    L('ATOM      1  N   ALA A   1       0.000   0.000   0.000  1.00  0.00           N'),
    L('ATOM      2  OG1 THR A   2       1.500   0.000   0.000  1.00  0.00'),
  ));
  assert.equal(st.element[0], 'N', 'taken from the element column');
  assert.equal(st.element[1], 'O', 'inferred from the atom name when the column is missing');
});

test('an atom named CA is carbon in a residue and calcium as an ion, by the column convention', () => {
  // The PDB convention is positional: a C-alpha is written " CA " with the element letter in column 14,
  // a calcium ion is written "CA  " starting in column 13. Nothing but the columns distinguishes them.
  const st = parsePDB(pdb(
    L('ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00  0.00'),
    L('HETATM    2 CA    CA A   2      20.000   0.000   0.000  1.00  0.00'),
  ));
  assert.equal(st.element[0], 'C', 'a C-alpha is carbon');
  assert.equal(st.element[1], 'CA', 'a calcium ion is calcium');
});

test('two-letter elements survive inference', () => {
  const st = parsePDB(pdb(
    L('HETATM    1 FE    FE A   1       0.000   0.000   0.000  1.00  0.00'),
    L('HETATM    2 CL    CL A   2      10.000   0.000   0.000  1.00  0.00'),
    L('HETATM    3 ZN    ZN A   3      20.000   0.000   0.000  1.00  0.00'),
  ));
  assert.deepEqual(Array.from(st.element), ['FE', 'CL', 'ZN']);
});

test('only one alternate conformer is kept', () => {
  const st = parsePDB(pdb(
    L('ATOM      1  CB ASER A  10       0.000   0.000   0.000  0.60 20.00           C'),
    L('ATOM      2  CB BSER A  10       0.500   0.000   0.000  0.40 20.00           C'),
    L('ATOM      3  OG ASER A  10       1.500   0.000   0.000  0.60 20.00           O'),
  ));
  assert.equal(st.n, 2, 'conformer B must be dropped, not merged in alongside A');
  assert.ok(Math.abs(st.pos[0] - 0.0) < 1e-6, 'the surviving CB is conformer A');
});

test('insertion codes make separate residues, each keeping its own C-alpha', () => {
  // Antibody CDR loops are numbered 100, 100A, 100B. Dropping the insertion code merges them, and a merged
  // residue keeps only the last C-alpha it saw — which silently halves the backbone the elastic network
  // model anchors on and mislabels every residue downstream. This was a real defect, fixed in iteration 14.
  const st = parsePDB(pdb(
    L('ATOM      1  N   ALA A 100      11.000  13.000  10.000  1.00 20.00           N'),
    L('ATOM      2  CA  ALA A 100      12.000  13.000  10.000  1.00 20.00           C'),
    L('ATOM      3  N   ALA A 100A     14.000  13.000  10.000  1.00 20.00           N'),
    L('ATOM      4  CA  ALA A 100A     15.000  13.000  10.000  1.00 20.00           C'),
    L('ATOM      5  CA  GLY A 101      17.000  13.000  10.000  1.00 20.00           C'),
  ));
  assert.equal(st.residues.length, 3, `expected ALA100, ALA100A and GLY101, got ${st.residues.length}`);
  const [r1, r2, r3] = st.residues;
  assert.equal(r1.iCode, '');
  assert.equal(r2.iCode, 'A');
  assert.equal(r1.resSeq, 100);
  assert.equal(r2.resSeq, 100, 'the sequence number is shared; only the insertion code differs');
  assert.equal(r1.ca, 1, 'ALA100 keeps its own C-alpha');
  assert.equal(r2.ca, 3, 'ALA100A keeps its own, rather than overwriting the first');
  assert.equal(r3.label, 'GLY101');
  assert.equal(r2.label, 'ALA100A', 'a label must distinguish an inserted residue from its neighbour');
  // Every atom belongs to the residue it was written under.
  assert.deepEqual(Array.from(st.atomRes), [0, 0, 1, 1, 2]);
});

test('mmCIF reads insertion codes too, so both formats group residues the same way', () => {
  const cif = [
    'data_test',
    'loop_',
    '_atom_site.group_PDB',
    '_atom_site.id',
    '_atom_site.type_symbol',
    '_atom_site.label_atom_id',
    '_atom_site.label_comp_id',
    '_atom_site.auth_asym_id',
    '_atom_site.auth_seq_id',
    '_atom_site.pdbx_PDB_ins_code',
    '_atom_site.Cartn_x',
    '_atom_site.Cartn_y',
    '_atom_site.Cartn_z',
    'ATOM 1 N N   ALA A 100 ? 11.0 13.0 10.0',
    'ATOM 2 C CA  ALA A 100 ? 12.0 13.0 10.0',
    'ATOM 3 N N   ALA A 100 A 14.0 13.0 10.0',
    'ATOM 4 C CA  ALA A 100 A 15.0 13.0 10.0',
  ].join('\n');
  const st = parseMmCIF(cif);
  assert.equal(st.n, 4);
  assert.equal(st.residues.length, 2, 'the inserted residue must be its own residue in mmCIF as well');
  assert.equal(st.residues[0].iCode, '', 'a "?" insertion code means none');
  assert.equal(st.residues[1].iCode, 'A');
  assert.equal(st.residues[0].ca, 1);
  assert.equal(st.residues[1].ca, 3);
});

test('a multi-model file reads the first model unless told otherwise', () => {
  const text = pdb(
    L('MODEL        1'),
    L('ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00  0.00           C'),
    L('ATOM      2  CA  ALA A   2       3.800   0.000   0.000  1.00  0.00           C'),
    L('ENDMDL'),
    L('MODEL        2'),
    L('ATOM      1  CA  ALA A   1       0.000   0.000   1.000  1.00  0.00           C'),
    L('ATOM      2  CA  ALA A   2       3.800   0.000   1.000  1.00  0.00           C'),
    L('ENDMDL'),
  );
  const first = parsePDB(text);
  assert.equal(first.n, 2, 'two models must not be stacked into one structure');
  assert.ok(Math.abs(first.pos[2] - 0) < 1e-6, 'the first model is the one kept');
  assert.equal(parsePDB(text, { allModels: true }).n, 4, 'allModels reads both');
});

test('parsePDBFrames turns a trajectory into one coordinate frame per model', () => {
  const frames = parsePDBFrames(pdb(
    L('MODEL        1'),
    L('ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00  0.00           C'),
    L('ATOM      2  CA  ALA A   2       3.800   0.000   0.000  1.00  0.00           C'),
    L('ENDMDL'),
    L('MODEL        2'),
    L('ATOM      1  CA  ALA A   1       0.000   0.000   1.000  1.00  0.00           C'),
    L('ATOM      2  CA  ALA A   2       3.800   0.000   1.000  1.00  0.00           C'),
    L('ENDMDL'),
  ));
  assert.equal(frames.length, 2);
  for (const f of frames) assert.equal(f.length, 6, 'two atoms, three coordinates each');
  assert.ok(Math.abs(frames[0][2] - 0) < 1e-6);
  assert.ok(Math.abs(frames[1][2] - 1) < 1e-6, 'the second frame carries the second model');
});

test('a standard residue written as HETATM is still polymer', () => {
  // Selenomethionine and AMBER-style output arrive as HETATM but are part of the chain. A pocket detector
  // that skips them would carve a hole in the protein surface.
  const st = parsePDB(pdb(
    L('HETATM    1  CA  ALA A   1       0.000   0.000   0.000  1.00  0.00           C'),
    L('HETATM    2  C1  LIG A   2      20.000   0.000   0.000  1.00  0.00           C'),
  ));
  assert.equal(st.het[0], 0, 'a standard residue is promoted back to polymer');
  assert.equal(st.het[1], 1, 'an actual ligand stays a heteroatom');
  assert.equal(st.residues[0].polymer, true);
  assert.equal(st.residues[1].polymer, false);
});

test('waters and ions are classified apart from the polymer', () => {
  const st = parsePDB(pdb(
    L('ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00  0.00           C'),
    L('HETATM    2  O   HOH A   2      10.000   0.000   0.000  1.00  0.00           O'),
    L('HETATM    3 NA    NA A   3      20.000   0.000   0.000  1.00  0.00'),
  ));
  const [ala, hoh, na] = st.residues;
  assert.ok(ala.polymer && !ala.water && !ala.ion);
  assert.ok(hoh.water && !hoh.polymer, 'water must be recognised as water');
  assert.ok(na.ion && !na.polymer, 'a sodium ion must be recognised as an ion');
});

test('CONECT records bond the ligand atoms they name', () => {
  // Two heteroatoms placed 2.4 A apart — too far for distance-based perception to bond them, so if they
  // come out bonded it is because CONECT was honoured.
  const text = pdb(
    L('HETATM    1  C1  LIG A   1       0.000   0.000   0.000  1.00  0.00           C'),
    L('HETATM    2  C2  LIG A   1       2.400   0.000   0.000  1.00  0.00           C'),
    L('CONECT    1    2'),
  );
  const withConect = parsePDB(text);
  const bonded = (st, i, j) => {
    for (let k = 0; k < st.bonds.length; k += 3) {
      if ((st.bonds[k] === i && st.bonds[k + 1] === j) || (st.bonds[k] === j && st.bonds[k + 1] === i)) return true;
    }
    return false;
  };
  assert.ok(bonded(withConect, 0, 1), 'CONECT should bond atoms that are too far apart to be perceived');
  const without = parsePDB(text.split('\n').filter((l) => !l.startsWith('CONECT')).join('\n'));
  assert.ok(!bonded(without, 0, 1), 'without CONECT, 2.4 A is too far to bond — so the test above means something');
});

test('bond perception finds the bonds real geometry implies, and no more', () => {
  const st = parsePDB(pdb(
    L('ATOM      1  N   ALA A   1       0.000   0.000   0.000  1.00  0.00           N'),
    L('ATOM      2  CA  ALA A   1       1.458   0.000   0.000  1.00  0.00           C'),
    L('ATOM      3  C   ALA A   1       2.000   1.420   0.000  1.00  0.00           C'),
    L('ATOM      4  O   ALA A   1       3.220   1.560   0.000  1.00  0.00           O'),
    L('ATOM      5  CA  GLY A  50      30.000   0.000   0.000  1.00  0.00           C'),
  ));
  assert.equal(st.bonds.length / 3, 3, 'N-CA, CA-C, C-O and nothing else');
  // The distant atom is bonded to nothing, and every atom knows its neighbours.
  assert.equal(st.nbr[4].length, 0, 'an atom 30 A away must not be bonded to anything');
  assert.deepEqual(st.nbr[1].slice().sort(), [0, 2], 'the C-alpha is bonded to N and C');
});

test('a molblock is read from its counts line and its blocks', () => {
  const mol = [
    'ethanol',
    '  test',
    '',
    '  3  2  0  0  0  0  0  0  0  0999 V2000',
    '    0.0000    0.0000    0.0000 C   0  0',
    '    1.5000    0.0000    0.0000 C   0  0',
    '    2.0000    1.4000    0.0000 O   0  0',
    '  1  2  1  0',
    '  2  3  1  0',
    'M  END',
  ].join('\n');
  const st = parseMolblock(mol);
  assert.equal(st.n, 3);
  assert.deepEqual(Array.from(st.element), ['C', 'C', 'O']);
  assert.equal(st.bonds.length / 3, 2, 'the bond block is used rather than re-perceiving from distance');
  assert.ok(Math.abs(st.pos[3] - 1.5) < 1e-4);
  assert.equal(st.kind, 'small', 'a molblock is a small molecule');
});

test('parseAny dispatches on content, not just on the file name', () => {
  const pdbText = pdb(L('ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00  0.00           C'));
  assert.equal(parseAny(pdbText, 'whatever.txt').n, 1);
  const mol = ['x', '', '', '  1  0  0  0  0  0  0  0  0  0999 V2000',
    '    0.0000    0.0000    0.0000 C   0  0', 'M  END'].join('\n');
  const m = parseAny(mol, 'ligand.sdf');
  assert.equal(m.n, 1);
  assert.equal(m.kind, 'small');
});

test('a blank or junk input does not throw', () => {
  for (const text of ['', '\n\n', 'HEADER    NOTHING USEFUL HERE']) {
    const st = parsePDB(text);
    assert.equal(st.n, 0, `"${text.slice(0, 20)}" should parse to an empty structure`);
    assert.deepEqual(st.residues, []);
  }
});
