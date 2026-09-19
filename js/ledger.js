// Provenance ledger: a tamper-evident record of what was done in the workspace.
//
// Every result worth citing later — a compound import, a docking run, a simulation, an AlphaFold 3 job —
// is written as a record whose hash covers the previous record's hash, so the sequence cannot be edited
// after the fact without breaking the chain. This is a local hash chain (SHA-256 via the Web Crypto API),
// not a blockchain: nothing is broadcast and no consensus is involved. What it gives you is an export
// whose root hash you can anchor on-chain, in a DAO proposal, or in a lab notebook, and later verify.
const LS_KEY = 'biodao-ledger-v1';
const GENESIS = '0'.repeat(64);

async function sha256(text) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

// The exact string that gets hashed. Key order is fixed so a re-hash always reproduces it.
function canonical(rec) {
  return JSON.stringify([rec.index, rec.time, rec.kind, rec.actor, rec.prev, rec.payload]);
}

export class Ledger extends EventTarget {
  constructor() {
    super();
    this.records = [];
    this.actor = 'anonymous';
    try { this.records = JSON.parse(localStorage.getItem(LS_KEY) || '[]'); } catch { this.records = []; }
  }

  get head() { return this.records.length ? this.records[this.records.length - 1].hash : GENESIS; }

  async append(kind, payload) {
    const rec = {
      index: this.records.length,
      time: new Date().toISOString(),
      kind,
      actor: this.actor,
      prev: this.head,
      payload,
    };
    rec.hash = await sha256(canonical(rec));
    this.records.push(rec);
    this.save();
    this.dispatchEvent(new CustomEvent('append', { detail: rec }));
    return rec;
  }

  // Re-hash every record and confirm each one still points at its predecessor.
  async verify() {
    let prev = GENESIS;
    for (const rec of this.records) {
      if (rec.prev !== prev) return { ok: false, brokenAt: rec.index, reason: 'previous hash does not match' };
      const again = await sha256(canonical(rec));
      if (again !== rec.hash) return { ok: false, brokenAt: rec.index, reason: 'record contents were altered' };
      prev = rec.hash;
    }
    return { ok: true, length: this.records.length, head: prev };
  }

  save() { try { localStorage.setItem(LS_KEY, JSON.stringify(this.records)); } catch { /* quota */ } }

  clear() { this.records = []; this.save(); this.dispatchEvent(new CustomEvent('append', { detail: null })); }

  export() {
    return {
      chain: 'biodao.blockchain provenance ledger',
      generator: 'biodao.blockchain (powered by AGI Corp)',
      algorithm: 'SHA-256 hash chain, Web Crypto',
      exported: new Date().toISOString(),
      length: this.records.length,
      head: this.head,
      records: this.records,
    };
  }

  // Short human-readable line for the UI.
  static describe(rec) {
    const p = rec.payload || {};
    switch (rec.kind) {
      case 'dock': return `${p.compound} → ${p.target} · ${p.score} kcal/mol`;
      case 'screen': return `screened ${p.compounds} compounds → ${p.target} · best ${p.best}`;
      case 'md': return `${p.engine} dynamics · ${p.target} · ${p.ps} ps`;
      case 'import': return `imported ${p.count} compounds from ${p.source}`;
      case 'af3': return `AlphaFold 3 job · ${p.target}${p.ligand ? ' + ' + p.ligand : ''}`;
      case 'structure': return `loaded ${p.name}`;
      default: return rec.kind;
    }
  }
}
