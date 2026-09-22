// The overview a researcher opens first: what is being worked on, what has been screened, what the
// evidence says, and what the provenance chain holds. Hand-written SVG so it works offline, in a
// headset browser and at phone width, with no chart library.

const C = { accent: '#39d98a', accent2: '#4cc9f0', warn: '#ffbe0b', bad: '#ff5d73', dim: '#93a7bd', line: '#1e2b3c' };

export function computeStats(S) {
  const lib = S?.library?.compounds || [];
  const docked = lib.filter((c) => c.dockScore != null);
  const profiled = lib.filter((c) => c.profile?.desc);
  const records = S?.ledger?.records || [];
  const byProgramme = {};
  for (const t of S?.targets || []) byProgramme[t.program] = (byProgramme[t.program] || 0) + 1;
  const kinds = {};
  for (const r of records) kinds[r.kind] = (kinds[r.kind] || 0) + 1;
  const best = docked.slice().sort((a, b) => a.dockScore - b.dockScore);
  return {
    targets: (S?.targets || []).length,
    programmes: byProgramme,
    compounds: lib.length,
    docked: docked.length,
    profiled: profiled.length,
    cnsShare: profiled.length ? profiled.filter((c) => c.profile.rules?.bbbLikely).length / profiled.length : 0,
    lipinskiClean: profiled.filter((c) => (c.profile.rules?.lipinskiViolations ?? 9) === 0).length,
    novel: lib.filter((c) => c.known && !(c.known.exact || []).length).length,
    checked: lib.filter((c) => c.known).length,
    leaderboard: best.slice(0, 10),
    scores: docked.map((c) => c.dockScore),
    property: profiled.map((c) => ({ id: c.agiId, mw: c.profile.desc.mw, clogp: c.profile.desc.clogp, cns: c.profile.rules?.cnsMpo5 ?? 0, score: c.dockScore })),
    ledger: { records: records.length, kinds, head: (S?.ledger?.head || '').slice(0, 12), last: records[records.length - 1] },
    current: { target: S?.target?.symbol || null, structure: S?.protein?.name || null, atoms: S?.protein?.n || 0,
      ligand: S?.ligand?.name || null, score: S?.lastScore?.total ?? null, hbonds: S?.lastScore?.hbonds?.length ?? null,
      poses: (S?.poses || []).length },
    activity: activityByHour(records),
  };
}

function activityByHour(records) {
  const buckets = new Array(24).fill(0);
  const now = Date.now();
  for (const r of records) {
    const h = Math.floor((now - Date.parse(r.time)) / 3.6e6);
    if (h >= 0 && h < 24) buckets[23 - h]++;
  }
  return buckets;
}

const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const fmt = (v, n = 2) => (v == null || Number.isNaN(v) ? '–' : (+v).toFixed(n));

export function dashboardHTMLShell() {
  return `<div class="dash" id="dashRoot"></div>`;
}

export function renderDashboard(rootEl, data, { onOpenTarget, onOpenCompound, onRun } = {}) {
  const d = data;
  rootEl.innerHTML = `
    <div class="dash-grid">
      ${kpiCard(d)}
      ${currentCard(d)}
      ${programmeCard(d)}
      ${leaderboardCard(d)}
      ${propertyCard(d)}
      ${activityCard(d)}
      ${ledgerCard(d)}
      ${actionsCard()}
    </div>`;
  rootEl.querySelectorAll('[data-programme]').forEach((el) => {
    el.onclick = () => onOpenTarget && onOpenTarget(el.dataset.programme);
  });
  rootEl.querySelectorAll('[data-compound]').forEach((el) => {
    el.onclick = () => onOpenCompound && onOpenCompound(el.dataset.compound);
  });
  rootEl.querySelectorAll('[data-run]').forEach((el) => {
    el.onclick = () => onRun && onRun(el.dataset.run);
  });
}

function card(title, sub, body, cls = '') {
  return `<section class="dash-card ${cls}"><h3>${esc(title)}${sub ? `<small>${esc(sub)}</small>` : ''}</h3>${body}</section>`;
}

function kpiCard(d) {
  const kpis = [
    ['targets', d.targets], ['compounds', d.compounds], ['docked', d.docked],
    ['best score', d.leaderboard[0] ? fmt(d.leaderboard[0].dockScore) : '–'],
    ['brain-penetrant', d.profiled ? `${Math.round(d.cnsShare * 100)}%` : '–'],
    ['ledger records', d.ledger.records],
  ];
  return card('At a glance', null,
    `<div class="kpis">${kpis.map(([k, v]) => `<div class="kpi"><b>${esc(v)}</b><span>${esc(k)}</span></div>`).join('')}</div>`, 'span2');
}

function currentCard(d) {
  const c = d.current;
  if (!c.structure) return card('On the bench', null, '<p class="dash-empty">Nothing loaded yet. Pick a target to begin.</p>');
  return card('On the bench', c.target || '', `
    <div class="dash-rows">
      <div><span>structure</span><b>${esc(c.structure)}</b></div>
      <div><span>atoms</span><b>${c.atoms}</b></div>
      <div><span>ligand</span><b>${esc(c.ligand || 'none')}</b></div>
      <div><span>score</span><b>${fmt(c.score)} kcal/mol</b></div>
      <div><span>H-bonds</span><b>${c.hbonds ?? '–'}</b></div>
      <div><span>poses</span><b>${c.poses}</b></div>
    </div>`);
}

function programmeCard(d) {
  const entries = Object.entries(d.programmes).sort((a, b) => b[1] - a[1]);
  if (!entries.length) return '';
  const max = Math.max(...entries.map((e) => e[1]));
  const rows = entries.map(([name, n], i) => {
    const w = (n / max) * 100;
    return `<div class="bar-row" data-programme="${esc(name)}" title="Open ${esc(name)}">
      <span class="bar-label">${esc(name)}</span>
      <span class="bar-track"><span class="bar-fill" style="width:${w}%;background:${i === 0 ? C.accent : C.accent2}"></span></span>
      <span class="bar-value">${n}</span></div>`;
  }).join('');
  return card('Targets by programme', 'click to open', `<div class="bars">${rows}</div>`);
}

function leaderboardCard(d) {
  if (!d.leaderboard.length) {
    return card('Screening leaderboard', null,
      '<p class="dash-empty">No compounds docked yet. Load a target, then screen the library.</p>');
  }
  const worst = Math.max(...d.leaderboard.map((c) => Math.abs(c.dockScore)));
  const rows = d.leaderboard.map((c) => `
    <div class="bar-row" data-compound="${esc(c.agiId)}" title="${esc(c.label || c.canonical)}">
      <span class="bar-label">${esc(c.agiId || '—')}</span>
      <span class="bar-track"><span class="bar-fill" style="width:${(Math.abs(c.dockScore) / worst) * 100}%;background:${C.accent}"></span></span>
      <span class="bar-value">${fmt(c.dockScore)}</span></div>`).join('');
  return card('Screening leaderboard', 'kcal/mol, lower is better', `<div class="bars">${rows}</div>`);
}

// Molecular weight against lipophilicity, the plot every medicinal chemist reads first.
function propertyCard(d) {
  const pts = d.property.filter((p) => p.mw && p.clogp != null);
  if (!pts.length) return card('Property space', null, '<p class="dash-empty">Profile the library to see its property space.</p>');
  const W = 320, H = 210, pad = 34;
  const xs = (v) => pad + ((Math.min(Math.max(v, 100), 700) - 100) / 600) * (W - pad - 10);
  const ys = (v) => H - pad - ((Math.min(Math.max(v, -2), 7) + 2) / 9) * (H - pad - 12);
  // The rule-of-five box: MW under 500, cLogP under 5.
  const box = `<rect x="${xs(100)}" y="${ys(5)}" width="${xs(500) - xs(100)}" height="${ys(-2) - ys(5)}"
      fill="rgba(57,217,138,0.07)" stroke="${C.accent}" stroke-dasharray="4 4" stroke-opacity="0.5"/>`;
  const dots = pts.map((p) => {
    const r = p.score != null ? 6 : 3.4;
    const fill = p.score != null ? C.accent : C.accent2;
    return `<circle cx="${xs(p.mw).toFixed(1)}" cy="${ys(p.clogp).toFixed(1)}" r="${r}" fill="${fill}" fill-opacity="${p.score != null ? 0.85 : 0.5}"><title>${esc(p.id)} MW ${fmt(p.mw, 0)} cLogP ${fmt(p.clogp)}${p.score != null ? ` score ${fmt(p.score)}` : ''}</title></circle>`;
  }).join('');
  const axis = `
    <line x1="${pad}" y1="${H - pad}" x2="${W - 8}" y2="${H - pad}" stroke="${C.line}"/>
    <line x1="${pad}" y1="12" x2="${pad}" y2="${H - pad}" stroke="${C.line}"/>
    <text x="${W / 2}" y="${H - 8}" fill="${C.dim}" font-size="11" text-anchor="middle">molecular weight</text>
    <text x="12" y="${H / 2}" fill="${C.dim}" font-size="11" text-anchor="middle" transform="rotate(-90 12 ${H / 2})">cLogP</text>
    <text x="${pad}" y="${H - pad + 14}" fill="${C.dim}" font-size="10">100</text>
    <text x="${W - 20}" y="${H - pad + 14}" fill="${C.dim}" font-size="10">700</text>`;
  return card('Property space', 'filled dots are docked', `
    <svg viewBox="0 0 ${W} ${H}" class="dash-svg" role="img" aria-label="molecular weight against cLogP">${box}${axis}${dots}</svg>
    <p class="dash-note">Dashed box is Lipinski's rule of five. ${d.lipinskiClean} of ${d.profiled} pass cleanly${d.checked ? `, ${d.novel} of ${d.checked} checked have no exact PubChem match` : ''}.</p>`);
}

function activityCard(d) {
  const max = Math.max(1, ...d.activity);
  const W = 320, H = 90;
  const bars = d.activity.map((n, i) => {
    const h = (n / max) * (H - 24);
    return `<rect x="${(i * W) / 24 + 1.5}" y="${H - 16 - h}" width="${W / 24 - 3}" height="${h}" fill="${n ? C.accent2 : C.line}" rx="2"/>`;
  }).join('');
  return card('Activity', 'last 24 hours', `
    <svg viewBox="0 0 ${W} ${H}" class="dash-svg" role="img" aria-label="runs per hour">${bars}
      <text x="2" y="${H - 3}" fill="${C.dim}" font-size="10">24h ago</text>
      <text x="${W - 4}" y="${H - 3}" fill="${C.dim}" font-size="10" text-anchor="end">now</text></svg>`);
}

function ledgerCard(d) {
  const kinds = Object.entries(d.ledger.kinds).sort((a, b) => b[1] - a[1]);
  const last = d.ledger.last;
  return card('Provenance', 'SHA-256 chain', `
    <div class="chips">${kinds.map(([k, n]) => `<span class="dash-chip">${esc(k)} <b>${n}</b></span>`).join('') || '<span class="dash-empty">no records yet</span>'}</div>
    ${last ? `<p class="dash-note">Latest: <b>${esc(last.kind)}</b> at ${esc(last.time.slice(11, 19))}<br><code>${esc(d.ledger.head)}…</code></p>` : ''}
    <div class="dash-actions"><button data-run="ledger_verify">Verify chain</button><button data-run="ledger_export">Export</button></div>`);
}

function actionsCard() {
  return card('Next step', null, `
    <div class="dash-actions">
      <button class="primary" data-run="find_pockets">Find pockets</button>
      <button class="primary" data-run="dock">Dock ligand</button>
      <button data-run="screen">Screen library</button>
      <button data-run="evidence">Gather evidence</button>
      <button data-run="folds">Similar folds</button>
      <button data-run="report">Export report</button>
    </div>`);
}

// A plain-text session report, for pasting into a notebook or a DAO proposal.
export function buildReport(S, data) {
  const d = data || computeStats(S);
  const L = [];
  L.push(`biodao.blockchain session report`, `generated ${new Date().toISOString()}`, '');
  L.push(`Loaded: ${d.current.structure || 'nothing'}${d.current.target ? ` (${d.current.target})` : ''}`);
  if (d.current.ligand) L.push(`Ligand: ${d.current.ligand}, score ${fmt(d.current.score)} kcal/mol, ${d.current.hbonds} H-bonds`);
  L.push('', `Library: ${d.compounds} compounds, ${d.profiled} profiled, ${d.docked} docked`);
  if (d.leaderboard.length) {
    L.push('', 'Ranking (kcal/mol, lower is better):');
    d.leaderboard.forEach((c, i) => L.push(`  ${i + 1}. ${c.agiId || '—'}  ${fmt(c.dockScore)}  ${c.label ? c.label.slice(0, 48) : ''}`));
  }
  L.push('', `Provenance: ${d.ledger.records} records, head ${d.ledger.head}…`);
  L.push('', 'Scores come from a Vina-style empirical function and are approximate; treat them as a ranking.');
  return L.join('\n');
}
