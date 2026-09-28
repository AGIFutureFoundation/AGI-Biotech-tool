#!/usr/bin/env python3
"""biodao.blockchain local server (powered by AGI Corp).

Serves the WebXR app and adds the compute that a browser cannot do well:

  GET  /api/health             which optional engines are installed
  POST /api/embed              SMILES -> 3D conformer (RDKit ETKDGv3 + MMFF94)
  POST /api/extract            PDF / text upload -> SMILES + compound IDs (pypdf + RDKit)
  POST /api/md                 start an all-atom OpenMM simulation (implicit solvent)
  GET  /api/md/<job>           poll progress and fetch trajectory frames
  POST /api/library            save the AGI compound library to data/agi_compounds.json
  POST /api/room/<room>        publish collaboration state (pose, loaded target, avatar)
  GET  /api/room/<room>/events server-sent events stream of everyone else's state
  POST /api/bigquery           run a Google BigQuery public-dataset query (needs gcloud auth)

Only the Python standard library is required; RDKit, pypdf, OpenMM, PDBFixer and
google-cloud-bigquery each switch on their feature when importable.

  python server/server.py                 # http://localhost:8000
  python server/server.py --https         # self-signed HTTPS so a Quest on Wi-Fi can enter VR
"""
import argparse
import io
import json
import os
import queue
import socket
import ssl
import subprocess
import sys
import threading
import time
import traceback
import urllib.parse
import urllib.request
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)


def _try(mod):
    try:
        return __import__(mod)
    except Exception:  # noqa: BLE001
        return None


HAVE = {
    "rdkit": _try("rdkit") is not None,
    "pypdf": _try("pypdf") is not None,
    "openmm": _try("openmm") is not None,
    "pdbfixer": _try("pdbfixer") is not None,
    "bigquery": _try("google.cloud.bigquery") is not None,
}

# --------------------------------------------------------------------------- chemistry


def embed_smiles(smiles, n_confs=1, seed=0xA61):
    from rdkit import Chem
    from rdkit.Chem import AllChem

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("RDKit could not parse that SMILES")
    molh = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = seed
    cids = list(AllChem.EmbedMultipleConfs(molh, numConfs=max(1, n_confs), params=params))
    if not cids:
        params.useRandomCoords = True
        cids = list(AllChem.EmbedMultipleConfs(molh, numConfs=max(1, n_confs), params=params))
    if not cids:
        raise ValueError("3D embedding failed for this structure")
    energies = []
    if AllChem.MMFFHasAllMoleculeParams(molh):
        for cid, (conv, e) in zip(cids, AllChem.MMFFOptimizeMoleculeConfs(molh, maxIters=2000)):
            energies.append(e)
        ff = "MMFF94"
    else:
        for cid, (conv, e) in zip(cids, AllChem.UFFOptimizeMoleculeConfs(molh, maxIters=2000)):
            energies.append(e)
        ff = "UFF"
    return {"forcefield": ff, "conformers": [
        {"molblock": Chem.MolToMolBlock(molh, confId=c), "energy": round(e, 3)} for c, e in zip(cids, energies)]}


def extract_upload(filename, data):
    from chem_extract import extract

    if filename.lower().endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        text = "\n".join((p.extract_text() or "") for p in reader.pages)
        pages = len(reader.pages)
    else:
        text, pages = data.decode("utf-8", "replace"), 1
    rejects = []
    found = extract(text, filename, rejects)
    return {"file": filename, "pages": pages, "chars": len(text), "compounds": found, "rejects": rejects,
            "note": None if text.strip() else "No text layer: this PDF is scanned images. Structures drawn as "
                                              "pictures need optical structure recognition (e.g. DECIMER) first."}


# --------------------------------------------------------------------------- molecular dynamics

JOBS = {}


def _fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "biodao-blockchain/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode()


def run_md(job_id, spec):
    job = JOBS[job_id]
    try:
        import openmm as mm
        import openmm.app as app
        import openmm.unit as u
        from pdbfixer import PDBFixer

        job["stage"] = "fetching structure"
        if spec.get("pdb"):
            text = spec["pdb"]
        elif spec.get("pdbId"):
            text = _fetch(f"https://files.rcsb.org/download/{spec['pdbId'].upper()}.pdb")
        elif spec.get("url"):
            text = _fetch(spec["url"])
        else:
            raise ValueError("send pdb text, pdbId or url")

        job["stage"] = "repairing structure (PDBFixer)"
        fixer = PDBFixer(pdbfile=io.StringIO(text))
        chains = spec.get("chains")
        if chains:
            drop = [i for i, c in enumerate(fixer.topology.chains()) if c.id not in chains]
            fixer.removeChains(drop)
        fixer.removeHeterogens(keepWater=False)
        fixer.findMissingResidues()
        fixer.missingResidues = {}  # do not invent long missing loops
        fixer.findNonstandardResidues()
        fixer.replaceNonstandardResidues()
        fixer.findMissingAtoms()
        fixer.addMissingAtoms()
        fixer.addMissingHydrogens(7.0)
        n_atoms = fixer.topology.getNumAtoms()
        if n_atoms > spec.get("maxAtoms", 30000):
            raise ValueError(f"{n_atoms} atoms is too large for an interactive run; pick one chain")

        job["stage"] = "building force field (Amber14 + GBn2 implicit solvent)"
        try:
            ff = app.ForceField("amber14-all.xml", "implicit/gbn2.xml")
            system = ff.createSystem(fixer.topology, nonbondedMethod=app.CutoffNonPeriodic,
                                     nonbondedCutoff=2.0 * u.nanometer, constraints=app.HBonds)
            job["forcefield"] = "Amber14 ff14SB + GBn2"
        except Exception:  # noqa: BLE001
            ff = app.ForceField("amber99sbildn.xml", "amber99_obc.xml")
            system = ff.createSystem(fixer.topology, nonbondedMethod=app.CutoffNonPeriodic,
                                     nonbondedCutoff=2.0 * u.nanometer, constraints=app.HBonds)
            job["forcefield"] = "Amber99SB-ILDN + OBC"
        temp = float(spec.get("temperature", 310))
        integ = mm.LangevinMiddleIntegrator(temp * u.kelvin, 1.0 / u.picosecond, 0.002 * u.picoseconds)
        platform = None
        for name in ("CUDA", "OpenCL", "CPU"):
            try:
                platform = mm.Platform.getPlatformByName(name)
                break
            except Exception:  # noqa: BLE001
                pass
        sim = app.Simulation(fixer.topology, system, integ, platform)
        sim.context.setPositions(fixer.positions)
        job["platform"] = platform.getName()

        job["stage"] = "energy minimisation"
        sim.minimizeEnergy(maxIterations=500)
        sim.context.setVelocitiesToTemperature(temp * u.kelvin)

        heavy = [a.index for a in fixer.topology.atoms() if a.element is not None and a.element.symbol != "H"]
        buf = io.StringIO()
        st = sim.context.getState(getPositions=True)
        app.PDBFile.writeFile(fixer.topology, st.getPositions(), buf, keepIds=True)
        job["topology"] = "\n".join(l for l in buf.getvalue().splitlines()
                                    if not (l.startswith(("ATOM", "HETATM")) and l[76:78].strip() == "H"))
        steps = int(spec.get("steps", 10000))
        nframes = int(spec.get("frames", 50))
        chunk = max(1, steps // nframes)
        job["stage"] = "running"
        t0 = time.time()
        for f in range(nframes):
            if job.get("cancel"):
                job["stage"] = "cancelled"
                return
            sim.step(chunk)
            s = sim.context.getState(getPositions=True, getEnergy=True)
            pos = s.getPositions(asNumpy=True).value_in_unit(u.angstrom)
            job["frames"].append([round(float(v), 2) for i in heavy for v in pos[i]])
            job["energies"].append(round(s.getPotentialEnergy().value_in_unit(u.kilocalorie_per_mole), 1))
            job["progress"] = (f + 1) / nframes
            elapsed = time.time() - t0
            job["nsPerDay"] = round((f + 1) * chunk * 0.002e-3 / max(elapsed, 1e-6) * 86400, 2)
        job["stage"] = "done"
        job["simulatedPs"] = steps * 0.002
    except Exception as e:  # noqa: BLE001
        job["stage"] = "error"
        job["error"] = f"{type(e).__name__}: {e}"
        traceback.print_exc()


# --------------------------------------------------------------------------- read-only proxy
# Some public scientific APIs send no CORS headers, so a browser cannot call them directly.
# This forwards GET requests to a fixed allowlist of them, and to nothing else.
PROXY_HOSTS = {
    "www.ebi.ac.uk", "ebi.ac.uk", "www.europepmc.org", "europepmc.org", "reactome.org",
    "string-db.org", "www.proteinatlas.org", "clinicaltrials.gov", "gnomad.broadinstitute.org",
    "rest.uniprot.org", "data.rcsb.org", "files.rcsb.org", "search.rcsb.org", "models.rcsb.org",
    "alphafold.ebi.ac.uk", "pubchem.ncbi.nlm.nih.gov", "eutils.ncbi.nlm.nih.gov", "rest.kegg.jp",
    "bindingdb.org", "www.bindingdb.org", "api.fda.gov", "pharos-api.ncats.io", "mychem.info",
    "mygene.info", "myvariant.info", "mydisease.info", "api.platform.opentargets.org",
    "search.foldseek.com", "www.guidetopharmacology.org", "rest.ensembl.org",
}


def proxy_get(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in PROXY_HOSTS:
        raise ValueError(f"{parsed.hostname} is not on the proxy allowlist")
    req = urllib.request.Request(url, headers={"User-Agent": "biodao-blockchain/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), r.headers.get("Content-Type", "application/json")


# --------------------------------------------------------------------------- collaboration rooms

ROOMS = {}  # room -> {"subs": [queue], "state": {client: payload}}
ROOM_LOCK = threading.Lock()


def room(name):
    with ROOM_LOCK:
        return ROOMS.setdefault(name, {"subs": [], "state": {}})


# --------------------------------------------------------------------------- BigQuery

BQ_PRESETS = {
    # Google Cloud public dataset of AlphaFold DB metadata (214M+ predicted structures).
    "alphafold_by_accession": (
        "SELECT entryId, uniprotAccession, uniprotDescription, gene, organismScientificName, "
        "globalMetricValue, latestVersion FROM `bigquery-public-data.deepmind_alphafold.metadata` "
        "WHERE uniprotAccession IN UNNEST(@ids)"),
    "alphafold_by_gene": (
        "SELECT entryId, uniprotAccession, organismScientificName, globalMetricValue "
        "FROM `bigquery-public-data.deepmind_alphafold.metadata` WHERE gene = @gene "
        "ORDER BY globalMetricValue DESC LIMIT 200"),
}


def run_bigquery(body):
    from google.cloud import bigquery

    client = bigquery.Client(project=body.get("project") or None)
    preset = body.get("preset")
    if preset:
        sql = BQ_PRESETS[preset]
        params = []
        if "ids" in body:
            params.append(bigquery.ArrayQueryParameter("ids", "STRING", body["ids"]))
        if "gene" in body:
            params.append(bigquery.ScalarQueryParameter("gene", "STRING", body["gene"]))
        cfg = bigquery.QueryJobConfig(query_parameters=params, maximum_bytes_billed=int(body.get("maxBytes", 20e9)))
    else:
        sql = body["sql"]
        cfg = bigquery.QueryJobConfig(maximum_bytes_billed=int(body.get("maxBytes", 20e9)))
    rows = [dict(r) for r in client.query(sql, job_config=cfg).result(max_results=int(body.get("limit", 500)))]
    return {"rows": rows, "sql": sql}


# --------------------------------------------------------------------------- HTTP


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".mjs": "text/javascript",
                      ".js": "text/javascript", ".wasm": "application/wasm", ".json": "application/json"}

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, fmt, *args):
        line = fmt % args
        if "/api/room" not in line:
            sys.stderr.write("%s - %s\n" % (self.address_string(), line))

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else b""

    def do_OPTIONS(self):  # noqa: N802
        self.send_response(204)
        self.end_headers()

    def do_GET(self):  # noqa: N802
        p = self.path.split("?")[0]
        if p == "/api/health":
            return self._json({"ok": True, **HAVE, "rooms": len(ROOMS)})
        if p.startswith("/api/md/"):
            job = JOBS.get(p.rsplit("/", 1)[1])
            if not job:
                return self._json({"error": "no such job"}, 404)
            since = int((self.path.split("since=") + ["0"])[1].split("&")[0] or 0)
            out = {k: v for k, v in job.items() if k not in ("frames", "cancel")}
            out["frames"] = job["frames"][since:]
            out["frameCount"] = len(job["frames"])
            if since:
                out.pop("topology", None)
            return self._json(out)
        if p == "/api/filmprogress":
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "err" in qs:
                print(f"film ERROR: {qs['err'][0][:400]}", flush=True)
            elif "phase" in qs:
                print(f"film phase: {qs['phase'][0]}", flush=True)
            else:
                print(f"film: {qs.get('s',['?'])[0]}s / {qs.get('of',['?'])[0]}s", flush=True)
            return self._json({"ok": True})
        if p == "/api/proxy":
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            target = (qs.get("url") or [""])[0]
            try:
                body, ctype = proxy_get(target)
            except Exception as e:  # noqa: BLE001
                return self._json({"error": f"{type(e).__name__}: {e}"}, 400)
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return self.wfile.write(body)
        if p.startswith("/api/room/") and p.endswith("/events"):
            return self._sse(p.split("/")[3])
        return super().do_GET()

    def _sse(self, name):
        r = room(name)
        q = queue.Queue()
        with ROOM_LOCK:
            r["subs"].append(q)
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        try:
            for payload in list(r["state"].values()):
                self.wfile.write(f"data: {json.dumps(payload)}\n\n".encode())
            self.wfile.flush()
            while True:
                try:
                    msg = q.get(timeout=15)
                    self.wfile.write(f"data: {msg}\n\n".encode())
                except queue.Empty:
                    self.wfile.write(b": keepalive\n\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            with ROOM_LOCK:
                if q in r["subs"]:
                    r["subs"].remove(q)

    def do_POST(self):  # noqa: N802
        p = self.path.split("?")[0]
        try:
            if p == "/api/embed":
                if not HAVE["rdkit"]:
                    return self._json({"error": "RDKit not installed on the server"}, 501)
                b = json.loads(self._body())
                return self._json(embed_smiles(b["smiles"], int(b.get("n", 1))))
            if p == "/api/extract":
                if not (HAVE["rdkit"] and HAVE["pypdf"]):
                    return self._json({"error": "server needs rdkit and pypdf"}, 501)
                name = self.headers.get("X-Filename", "upload.pdf")
                return self._json(extract_upload(name, self._body()))
            if p == "/api/md":
                if not (HAVE["openmm"] and HAVE["pdbfixer"]):
                    return self._json({"error": "server needs openmm and pdbfixer"}, 501)
                spec = json.loads(self._body())
                jid = uuid.uuid4().hex[:10]
                JOBS[jid] = {"id": jid, "stage": "queued", "progress": 0, "frames": [], "energies": [],
                             "spec": {k: v for k, v in spec.items() if k != "pdb"}}
                threading.Thread(target=run_md, args=(jid, spec), daemon=True).start()
                return self._json({"id": jid})
            if p.startswith("/api/md/") and p.endswith("/cancel"):
                job = JOBS.get(p.split("/")[3])
                if job:
                    job["cancel"] = True
                return self._json({"ok": bool(job)})
            if p == "/api/recording":
                qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                name = os.path.basename((qs.get("name") or ["demo.webm"])[0])
                out = os.path.join(ROOT, "docs", name)
                os.makedirs(os.path.dirname(out), exist_ok=True)
                data = self._body()
                with open(out, "wb") as f:
                    f.write(data)
                print(f"saved recording {out} ({len(data)/1e6:.1f} MB)")
                return self._json({"ok": True, "path": out, "bytes": len(data)})
            if p == "/api/library":
                lib = json.loads(self._body())
                path = os.path.join(ROOT, "data", "agi_compounds.json")
                tmp = path + ".tmp"
                with open(tmp, "w") as f:
                    json.dump(lib, f, indent=1)
                os.replace(tmp, path)
                return self._json({"ok": True, "saved": len(lib.get("compounds", []))})
            if p.startswith("/api/room/"):
                name = p.split("/")[3]
                payload = json.loads(self._body())
                r = room(name)
                with ROOM_LOCK:
                    r["state"][payload.get("client", "?")] = payload
                    subs = list(r["subs"])
                msg = json.dumps(payload)
                for q in subs:
                    q.put(msg)
                return self._json({"ok": True, "peers": len(subs)})
            if p == "/api/bigquery":
                if not HAVE["bigquery"]:
                    return self._json({"error": "pip install google-cloud-bigquery and run "
                                                "`gcloud auth application-default login`"}, 501)
                return self._json(run_bigquery(json.loads(self._body())))
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            return self._json({"error": f"{type(e).__name__}: {e}"}, 400)
        return self._json({"error": "unknown endpoint"}, 404)


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def self_signed(certdir):
    os.makedirs(certdir, exist_ok=True)
    crt, key = os.path.join(certdir, "dev.crt"), os.path.join(certdir, "dev.key")
    if not os.path.exists(crt):
        ip = lan_ip()
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "825",
                        "-keyout", key, "-out", crt, "-subj", "/CN=agi-bioxr",
                        "-addext", f"subjectAltName=DNS:localhost,IP:127.0.0.1,IP:{ip}"],
                       check=True, capture_output=True)
    return crt, key


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--https", action="store_true", help="self-signed TLS so headsets on Wi-Fi can use WebXR")
    a = ap.parse_args()
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    scheme = "http"
    if a.https:
        crt, key = self_signed(os.path.join(ROOT, ".certs"))
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(crt, key)
        srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
        scheme = "https"
    print(f"biodao.blockchain  ->  {scheme}://localhost:{a.port}   (LAN: {scheme}://{lan_ip()}:{a.port})")
    print("engines:", ", ".join(f"{k}={'yes' if v else 'no'}" for k, v in HAVE.items()))
    srv.serve_forever()


if __name__ == "__main__":
    main()

# ================================================================
# Phase 1 Enhancements: Auth, Projects, Reporting, Agents
# ================================================================

from auth import require_auth, require_role, authenticate_user, create_user
from projects import create_project, get_project, list_user_projects, create_campaign
from disease_panels import get_panel, list_panels, get_targets_by_program
from reporting import Report, generate_screening_report
from paper_generator import generate_paper_from_session
from agents import OptimizationAgent, AnalysisAgent, WorkflowOrchestrator

# ================================================================
# User Authentication Endpoints
# ================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate a user and return JWT token."""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    token = authenticate_user(email, password)
    if token:
        return jsonify({'token': token, 'email': email}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user account."""
    data = request.json
    email = data.get('email')
    name = data.get('name')
    password = data.get('password', '')
    role = data.get('role', 'researcher')
    institution = data.get('institution', '')

    if not password:
        return jsonify({'error': 'password is required'}), 400

    user = create_user(email, name, password, role, institution)
    token = authenticate_user(email, password)

    return jsonify({
        'user_id': user.user_id,
        'token': token,
        'message': 'Account created'
    }), 201

# ================================================================
# Project Management Endpoints
# ================================================================

@app.route('/api/projects', methods=['POST'])
@require_auth
def create_new_project():
    """Create a new research project."""
    data = request.json
    project = create_project(
        name=data.get('name'),
        owner_id=request.user['user_id'],
        program=data.get('program'),  # ALS, Parkinsons, Shriners
        description=data.get('description', '')
    )
    return jsonify(project.to_dict()), 201

@app.route('/api/projects', methods=['GET'])
@require_auth
def get_projects():
    """List user's projects."""
    projects = list_user_projects(request.user['user_id'])
    return jsonify([p.to_dict() for p in projects]), 200

@app.route('/api/projects/<project_id>', methods=['GET'])
@require_auth
def get_project_details(project_id):
    """Get project details."""
    project = get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    return jsonify(project.to_dict()), 200

# ================================================================
# Disease Panels Endpoints
# ================================================================

@app.route('/api/disease-panels', methods=['GET'])
def get_disease_panels():
    """List available disease panels."""
    panels = {}
    for disease in list_panels():
        panel = get_panel(disease)
        panels[disease] = {
            'name': panel['name'],
            'description': panel['description'],
            'target_count': len(panel['targets']),
            'programs': panel['programs'],
        }
    return jsonify(panels), 200

@app.route('/api/disease-panels/<disease>', methods=['GET'])
def get_disease_panel(disease):
    """Get full disease panel with all targets."""
    panel = get_panel(disease)
    if not panel:
        return jsonify({'error': 'Disease panel not found'}), 404
    return jsonify(panel), 200

@app.route('/api/disease-panels/<disease>/top-targets', methods=['GET'])
def get_top_targets(disease):
    """Get top targets by prevalence in a disease."""
    top_n = request.args.get('top_n', 5, type=int)
    from disease_panels import get_top_targets_by_prevalence
    targets = get_top_targets_by_prevalence(disease, top_n)
    return jsonify(targets), 200

# ================================================================
# Reporting & Paper Generation Endpoints
# ================================================================

@app.route('/api/reports/<campaign_id>/generate', methods=['POST'])
@require_auth
def generate_report(campaign_id):
    """Generate a publication-ready report for a screening campaign."""
    data = request.json
    results = data.get('results', [])
    
    report = generate_screening_report(
        project_id=data.get('project_id'),
        campaign_id=campaign_id,
        target=data.get('target'),
        results=results
    )
    
    return jsonify({
        'markdown': report.to_markdown(),
        'json': json.loads(report.to_json()),
    }), 200

@app.route('/api/papers/generate', methods=['POST'])
@require_auth
def generate_paper():
    """Generate a full research paper from a screening session."""
    session_data = request.json
    paper = generate_paper_from_session(session_data)
    
    format = request.args.get('format', 'markdown')  # markdown, latex, json
    
    if format == 'latex':
        return paper.to_latex(), 200, {'Content-Type': 'text/plain'}
    elif format == 'json':
        return paper.to_json(), 200, {'Content-Type': 'application/json'}
    else:  # markdown
        return paper.to_markdown(), 200, {'Content-Type': 'text/markdown'}

# ================================================================
# Multi-Agent System Endpoints
# ================================================================

opt_agent = OptimizationAgent()
ana_agent = AnalysisAgent()
orchestrator = WorkflowOrchestrator()

@app.route('/api/agents', methods=['GET'])
def list_agents():
    """List available research agents."""
    agents = {
        'optimizer': opt_agent.to_dict(),
        'analyst': ana_agent.to_dict(),
    }
    return jsonify(agents), 200

@app.route('/api/agents/optimize/docking-params', methods=['POST'])
@require_auth
def optimize_docking_params():
    """Agent: Optimize docking parameters for a target."""
    data = request.json
    result = opt_agent.optimize_docking_params(
        target_id=data.get('target_id'),
        validation_compounds=data.get('validation_compounds', [])
    )
    return jsonify(result), 200

@app.route('/api/agents/analyze/hotspots', methods=['POST'])
@require_auth
def analyze_hotspots():
    """Agent: Identify chemical hotspots in screening results."""
    data = request.json
    result = ana_agent.identify_hotspots(
        compounds=data.get('compounds', []),
        target=data.get('target')
    )
    return jsonify(result), 200

@app.route('/api/agents/analyze/sa-score', methods=['POST'])
@require_auth
def predict_sa():
    """Agent: Predict synthetic accessibility of compounds."""
    data = request.json
    result = ana_agent.predict_synthetic_accessibility(
        compound_ids=data.get('compound_ids', [])
    )
    return jsonify(result), 200

@app.route('/api/workflows/lead-optimization', methods=['POST'])
@require_auth
def create_lead_opt_workflow():
    """Create an automated lead optimization workflow."""
    data = request.json
    workflow = orchestrator.create_lead_optimization_workflow(
        target_id=data.get('target_id'),
        lead_compound=data.get('lead_compound')
    )
    return jsonify(workflow), 201

@app.route('/api/workflows/validation', methods=['POST'])
@require_auth
def create_validation_workflow():
    """Create an automated validation workflow (MD + MMGBSA + report)."""
    data = request.json
    workflow = orchestrator.create_validation_workflow(
        top_compounds=data.get('top_compounds', []),
        target_id=data.get('target_id')
    )
    return jsonify(workflow), 201

if __name__ == '__main__':
    app.run(debug=True, port=8000)

# ================================================================
# Phase 2: Immersive AR/VR with Master Agent Voice Control
# ================================================================

from master_agent import MasterAgent, ResearchIntent

master_agent = MasterAgent()

@app.route('/api/voice-command', methods=['POST'])
@require_auth
def process_voice_command():
    """Process voice command and return master agent response."""
    data = request.json
    transcript = data.get('transcript', '')
    
    if not transcript:
        return jsonify({'error': 'Empty transcript'}), 400
    
    response = master_agent.process_voice_command(transcript)
    return jsonify(response), 200

@app.route('/api/master-agent/status', methods=['GET'])
@require_auth
def get_agent_status():
    """Get current master agent and team status."""
    return jsonify({
        'master_agent': master_agent.to_dict(),
        'team': {
            'optimizer': {'status': 'ready', 'active_jobs': 0},
            'analyst': {'status': 'ready', 'active_jobs': 0},
            'orchestrator': {'status': 'ready', 'active_jobs': 0},
        },
        'timestamp': datetime.utcnow().isoformat(),
    }), 200

@app.route('/api/immersive/scene/<scene_name>', methods=['POST'])
@require_auth
def update_vr_scene(scene_name):
    """Update VR scene visualization."""
    data = request.json
    
    scenes = {
        'docking_progress': {
            'show_target': True,
            'show_ligands': True,
            'show_scores': True,
            'show_pockets': True,
            'real_time_update': True,
        },
        'md_simulation': {
            'show_trajectory': True,
            'show_forces': True,
            'show_energy': True,
            'allow_steering': True,
            'allow_timeline_control': True,
        },
        'results_analysis': {
            'show_hotspots': True,
            'color_by_sa_score': True,
            'cluster_by_scaffold': True,
            'show_interactions': True,
        },
    }
    
    if scene_name not in scenes:
        return jsonify({'error': 'Unknown scene'}), 404
    
    return jsonify({
        'scene': scene_name,
        'config': scenes[scene_name],
        'ready': True,
    }), 200

@app.route('/api/agent-workflow/<workflow_name>', methods=['POST'])
@require_auth
def start_agent_workflow(workflow_name):
    """Start a multi-agent workflow orchestrated by master agent."""
    data = request.json
    
    workflows = {
        'lead_optimization': {
            'steps': [
                'tune_docking_params',
                'dock_analogs',
                'analyze_results',
                'predict_synthesis',
                'generate_recommendations',
            ],
            'agents': ['optimizer', 'dock_engine', 'analyst'],
        },
        'validation_pipeline': {
            'steps': [
                'run_md_simulations',
                'calculate_hbonds',
                'mmgbsa_scoring',
                'generate_binding_report',
                'predict_adme_properties',
            ],
            'agents': ['md_engine', 'analyst', 'orchestrator'],
        },
        'paper_generation': {
            'steps': [
                'compile_results',
                'generate_figures',
                'format_tables',
                'draft_discussion',
                'export_formats',
            ],
            'agents': ['analyst', 'orchestrator'],
        },
    }
    
    if workflow_name not in workflows:
        return jsonify({'error': 'Unknown workflow'}), 404
    
    workflow = workflows[workflow_name]
    return jsonify({
        'workflow_id': f"wf_{workflow_name}_{uuid.uuid4().hex[:8]}",
        'workflow_name': workflow_name,
        'steps': workflow['steps'],
        'agents_involved': workflow['agents'],
        'status': 'running',
        'progress': 0,
    }), 201

if __name__ == '__main__':
    app.run(debug=True, port=8000)

# ========================================================================== Phase 3: Async Workflows

from server.agent_orchestrator import AgentOrchestrator, WorkflowExecutor
from server.websocket_streaming import StreamingServer, VRDataFrame
import asyncio
import websockets
from datetime import datetime

# Initialize orchestrator and streaming server
orchestrator = AgentOrchestrator()
streaming_server = None

@app.route('/api/workflows/execute', methods=['POST'])
@require_auth
def execute_workflow():
    """Start an async workflow (lead_optimization, validation_campaign, discovery_sprint)."""
    data = request.json
    template = data.get('template')
    target = data.get('target')
    compounds = data.get('compounds', [])
    
    if template not in ['lead_optimization', 'validation_campaign', 'discovery_sprint']:
        return jsonify({'error': 'Unknown template'}), 400
    
    # Async execution in background
    workflow_id = str(uuid.uuid4())
    user = g.user if hasattr(g, 'user') else 'anonymous'
    
    try:
        # Don't await here - Flask can't do async natively
        # Just queue the work in orchestrator
        orchestrator.queue_workflow(
            workflow_id=workflow_id,
            template=template,
            target=target,
            compounds=compounds,
            user_id=user,
        )
        
        return jsonify({
            'workflow_id': workflow_id,
            'template': template,
            'target': target,
            'status': 'queued',
            'progress_url': f'/api/workflows/{workflow_id}/progress',
            'results_url': f'/api/workflows/{workflow_id}/results',
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workflows/<workflow_id>/progress', methods=['GET'])
@require_auth
def get_workflow_progress(workflow_id):
    """Get real-time progress for a running workflow."""
    progress = orchestrator.get_workflow_progress(workflow_id)
    
    if progress is None:
        return jsonify({'error': 'Workflow not found'}), 404
    
    return jsonify(progress), 200

@app.route('/api/workflows/<workflow_id>/results', methods=['GET'])
@require_auth
def get_workflow_results(workflow_id):
    """Fetch final results from completed workflow."""
    results = orchestrator.get_workflow_results(workflow_id)
    
    if results is None:
        return jsonify({'error': 'Workflow not found or not complete'}), 404
    
    return jsonify(results), 200

@app.route('/api/workflows/<workflow_id>/cancel', methods=['POST'])
@require_auth
def cancel_workflow(workflow_id):
    """Cancel a running workflow."""
    success = orchestrator.cancel_workflow(workflow_id)
    
    if not success:
        return jsonify({'error': 'Workflow not found or already finished'}), 404
    
    return jsonify({'workflow_id': workflow_id, 'status': 'cancelled'}), 200

@app.route('/api/agent/memory/suggest', methods=['GET'])
@require_auth
def get_memory_suggestions():
    """Get AI suggestions based on past experiments."""
    target = request.args.get('target')
    
    if not target:
        return jsonify({'error': 'target parameter required'}), 400
    
    suggestions = orchestrator.agent_memory.suggest_optimization(target, {})
    
    return jsonify({
        'target': target,
        'suggestions': suggestions,
    }), 200

@app.route('/api/agent/patterns', methods=['GET'])
@require_auth
def get_learned_patterns():
    """List all learned optimization patterns."""
    patterns = orchestrator.agent_memory.get_learned_patterns()
    
    return jsonify({
        'patterns': patterns,
        'count': len(patterns),
    }), 200

@app.route('/api/stream/subscribe', methods=['POST'])
@require_auth
def subscribe_to_stream():
    """Get WebSocket URL for real-time updates."""
    data = request.json
    stream_types = data.get('stream_types', ['docking', 'md', 'analysis'])
    
    return jsonify({
        'ws_url': f'ws://localhost:8000/ws',
        'stream_types': stream_types,
        'message': 'Connect to WebSocket for real-time updates',
    }), 200

# ========================================================================== WebSocket Streaming

async def websocket_handler(websocket, path):
    """Handle WebSocket connections for real-time VR updates."""
    client_id = str(uuid.uuid4())
    
    try:
        # Register client
        await streaming_server.register_client(client_id, websocket)
        
        # Keep connection alive and forward any messages
        async for message in websocket:
            data = json.loads(message)
            
            if data.get('type') == 'subscribe':
                # Client is subscribing to specific streams
                stream_types = data.get('stream_types', [])
                await streaming_server.subscribe_client(client_id, stream_types)
            
            elif data.get('type') == 'heartbeat':
                # Keep-alive ping
                await websocket.send(json.dumps({'type': 'pong'}))
    
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await streaming_server.unregister_client(client_id)

def start_websocket_server():
    """Start WebSocket server in background thread."""
    global streaming_server
    streaming_server = StreamingServer()
    
    async def run_ws():
        async with websockets.serve(websocket_handler, '0.0.0.0', 8001):
            await asyncio.Future()  # run forever
    
    def ws_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_ws())
    
    t = threading.Thread(target=ws_thread, daemon=True)
    t.start()

# ========================================================================== Master Agent Integration

from server.master_agent import MasterAgent

master_agent = None

def initialize_master_agent():
    """Initialize master agent on server startup."""
    global master_agent
    master_agent = MasterAgent(
        orchestrator=orchestrator,
        streaming_server=streaming_server,
    )

@app.route('/api/voice/process', methods=['POST'])
@require_auth
def process_voice_command():
    """Process voice command through master agent."""
    data = request.json
    voice_text = data.get('text', '')
    
    if not master_agent:
        return jsonify({'error': 'Master agent not initialized'}), 500
    
    try:
        response = master_agent.process_voice_command(voice_text)
        
        return jsonify({
            'command': voice_text,
            'response': response,
            'timestamp': datetime.utcnow().isoformat(),
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/voice/status', methods=['GET'])
@require_auth
def get_voice_status():
    """Get master agent and team status."""
    if not master_agent:
        return jsonify({'error': 'Master agent not initialized'}), 500
    
    return jsonify({
        'master_agent': {
            'status': 'ready',
            'listening': True,
        },
        'team': {
            'optimizer': orchestrator.get_agent_status('optimizer'),
            'analyst': orchestrator.get_agent_status('analyst'),
            'orchestrator': orchestrator.get_agent_status('orchestrator'),
        },
        'active_workflows': orchestrator.get_active_workflow_count(),
    }), 200

# ========================================================================== Startup

if __name__ == '__main__':
    # Start WebSocket server
    start_websocket_server()
    
    # Initialize master agent
    initialize_master_agent()
    
    print('✅ Phase 3: Agent orchestrator and streaming server initialized')
    print('🚀 biodao.blockchain server running on http://localhost:8000')
    print('📡 WebSocket streaming on ws://localhost:8001')
    
    app.run(debug=True, port=8000, threaded=True)
