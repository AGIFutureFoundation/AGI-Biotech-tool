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
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

# Sibling modules in server/. These sit below the sys.path line above rather than with the
# stdlib imports because they are only importable once HERE is on the path, which keeps
# `python server/server.py`, `import server` and an import from the repo root all working.
from agent_orchestrator import AgentOrchestrator  # noqa: E402
from agents import AnalysisAgent, OptimizationAgent, WorkflowOrchestrator  # noqa: E402
from auth import AuthToken, authenticate_user, create_user  # noqa: E402
from disease_panels import get_panel, get_top_targets_by_prevalence, list_panels  # noqa: E402
from master_agent import MasterAgentWithOrchestration  # noqa: E402
from paper_generator import generate_paper_from_session  # noqa: E402
from projects import create_project, get_project, list_user_projects  # noqa: E402
from reporting import generate_screening_report  # noqa: E402


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
    "websockets": _try("websockets") is not None,
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
TOOL_SCHEMA = []


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


# --------------------------------------------------------------------------- agent command channel
# An external agent (server/mcp_server.py, or any HTTP client) calls a tool; the call is pushed to every
# connected browser session over server-sent events, the first one to answer wins, and the result comes
# back on the original request. This is what makes the running workspace drivable from outside.
COMMAND_SUBS = []          # queues, one per connected browser
COMMAND_WAITERS = {}       # command id -> queue waiting for the result
COMMAND_LOCK = threading.Lock()


def dispatch_command(tool, args, timeout=180):
    cid = uuid.uuid4().hex[:12]
    inbox = queue.Queue()
    with COMMAND_LOCK:
        if not COMMAND_SUBS:
            raise RuntimeError("no browser session is connected; open the workspace first")
        COMMAND_WAITERS[cid] = inbox
        subs = list(COMMAND_SUBS)
    payload = json.dumps({"id": cid, "tool": tool, "args": args})
    for q in subs:
        q.put(payload)
    try:
        return inbox.get(timeout=timeout)
    except queue.Empty:
        raise TimeoutError(f"the workspace did not answer within {timeout}s")
    finally:
        with COMMAND_LOCK:
            COMMAND_WAITERS.pop(cid, None)


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


# --------------------------------------------------------------------------- research agents

OPT_AGENT = OptimizationAgent()
ANA_AGENT = AnalysisAgent()
# Two different things both historically called "the orchestrator": WORKFLOWS returns static
# workflow *definitions* (agents.WorkflowOrchestrator), ORCHESTRATOR actually queues and tracks
# running work (agent_orchestrator.AgentOrchestrator).
WORKFLOWS = WorkflowOrchestrator()
MASTER_AGENT = MasterAgentWithOrchestration()
ORCHESTRATOR = AgentOrchestrator(MASTER_AGENT, {"optimizer": OPT_AGENT, "analyst": ANA_AGENT,
                                                "orchestrator": WORKFLOWS})
MASTER_AGENT.orchestrator = ORCHESTRATOR

VR_SCENES = {
    "docking_progress": {"show_target": True, "show_ligands": True, "show_scores": True,
                         "show_pockets": True, "real_time_update": True},
    "md_simulation": {"show_trajectory": True, "show_forces": True, "show_energy": True,
                      "allow_steering": True, "allow_timeline_control": True},
    "results_analysis": {"show_hotspots": True, "color_by_sa_score": True,
                         "cluster_by_scaffold": True, "show_interactions": True},
}

AGENT_WORKFLOWS = {
    "lead_optimization": {
        "steps": ["tune_docking_params", "dock_analogs", "analyze_results", "predict_synthesis",
                  "generate_recommendations"],
        "agents": ["optimizer", "dock_engine", "analyst"]},
    "validation_pipeline": {
        "steps": ["run_md_simulations", "calculate_hbonds", "mmgbsa_scoring", "generate_binding_report",
                  "predict_adme_properties"],
        "agents": ["md_engine", "analyst", "orchestrator"]},
    "paper_generation": {
        "steps": ["compile_results", "generate_figures", "format_tables", "draft_discussion",
                  "export_formats"],
        "agents": ["analyst", "orchestrator"]},
}

WORKFLOW_TEMPLATES = ("lead_optimization", "validation_campaign", "discovery_sprint")


# --------------------------------------------------------------------------- VR streaming (optional)
# Real-time trajectory/docking push to headsets. `websockets` is not a declared dependency, so
# this switches on only when it happens to be installed, like the other optional engines.

STREAMING = None
WS_PORT = 8001


def start_websocket_server(host="127.0.0.1", port=WS_PORT):
    """Start the VR streaming WebSocket server in a daemon thread. No-op without `websockets`."""
    global STREAMING
    if not HAVE["websockets"]:
        return False
    import asyncio

    import websockets

    from websocket_streaming import StreamingServer

    STREAMING = StreamingServer()

    async def handler(ws):
        client_id = uuid.uuid4().hex
        try:
            await STREAMING.register_client(client_id, ws)
            async for message in ws:
                data = json.loads(message)
                if data.get("type") == "subscribe":
                    await STREAMING.subscribe_client(client_id, data.get("stream_types", []))
                elif data.get("type") == "heartbeat":
                    await ws.send(json.dumps({"type": "pong"}))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await STREAMING.unregister_client(client_id)

    def serve():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run():
            async with websockets.serve(handler, host, port):
                await asyncio.Future()

        loop.run_until_complete(run())

    threading.Thread(target=serve, daemon=True).start()
    return True


# --------------------------------------------------------------------------- HTTP


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".mjs": "text/javascript",
                      ".js": "text/javascript", ".wasm": "application/wasm", ".json": "application/json",
                      ".glb": "model/gltf-binary", ".gltf": "model/gltf+json", ".hdr": "image/vnd.radiance",
                      ".ktx2": "image/ktx2", ".bin": "application/octet-stream"}

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

    def _text(self, text, ctype, code=200):
        body = text.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else b""

    def _payload(self):
        """Decoded JSON request body, or {} when there is none."""
        raw = self._body()
        return json.loads(raw) if raw.strip() else {}

    def _qs(self):
        return urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

    @staticmethod
    def _seg(path, n):
        """Path segment n, url-decoded. /api/projects/a1b2 -> _seg(p, 2) == 'a1b2'."""
        parts = path.strip("/").split("/")
        return urllib.parse.unquote(parts[n]) if n < len(parts) else ""

    def _user(self):
        """The caller's JWT claims, or None after emitting 401. Stdlib stand-in for @require_auth."""
        token = self.headers.get("Authorization", "").replace("Bearer ", "").strip()
        if not token:
            self._json({"error": "Missing authentication token"}, 401)
            return None
        claims = AuthToken.verify(token)
        if not claims:
            self._json({"error": "Invalid or expired token"}, 401)
            return None
        return claims

    def _has_role(self, user, *roles):
        """Stdlib stand-in for @require_role. Emits 403 and returns False on a role mismatch."""
        if user.get("role") in roles:
            return True
        self._json({"error": f"Requires one of: {', '.join(roles)}"}, 403)
        return False

    def do_OPTIONS(self):  # noqa: N802
        self.send_response(204)
        self.end_headers()

    def do_GET(self):  # noqa: N802
        p = self.path.split("?")[0]
        if p == "/api/scenes":
            d = os.path.join(ROOT, "assets", "scenes")
            out = []
            if os.path.isdir(d):
                for f in sorted(os.listdir(d)):
                    if f.lower().endswith((".glb", ".gltf")):
                        out.append({"file": f, "url": f"assets/scenes/{f}",
                                    "mb": round(os.path.getsize(os.path.join(d, f)) / 1e6, 1),
                                    "label": os.path.splitext(f)[0].replace("_", " ").replace("gtasa ", "").strip()})
            return self._json({"scenes": out})
        if p == "/api/tools":
            return self._json({"tools": TOOL_SCHEMA})
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
        if p == "/api/command/events":
            return self._command_sse()
        if p == "/api/command/status":
            with COMMAND_LOCK:
                return self._json({"sessions": len(COMMAND_SUBS), "pending": len(COMMAND_WAITERS)})
        if p.startswith("/api/room/") and p.endswith("/events"):
            return self._sse(p.split("/")[3])
        if p.startswith("/api/"):
            try:
                if self._api_get(p):
                    return
            except Exception as e:  # noqa: BLE001
                traceback.print_exc()
                return self._json({"error": f"{type(e).__name__}: {e}"}, 400)
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

    def _command_sse(self):
        q = queue.Queue()
        with COMMAND_LOCK:
            COMMAND_SUBS.append(q)
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        try:
            self.wfile.write(b": connected\n\n")
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
            with COMMAND_LOCK:
                if q in COMMAND_SUBS:
                    COMMAND_SUBS.remove(q)

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
            if p == "/api/command":
                body = json.loads(self._body())
                try:
                    out = dispatch_command(body["tool"], body.get("args") or {}, int(body.get("timeout", 180)))
                except (RuntimeError, TimeoutError) as e:
                    return self._json({"ok": False, "error": str(e)}, 503)
                return self._json(out)
            if p == "/api/command/result":
                body = json.loads(self._body())
                with COMMAND_LOCK:
                    waiter = COMMAND_WAITERS.get(body.get("id"))
                if waiter:
                    waiter.put({k: v for k, v in body.items() if k != "id"})
                return self._json({"ok": True})
            if p == "/api/tools":
                # The browser publishes its tool schema here so the MCP server can advertise it.
                global TOOL_SCHEMA
                TOOL_SCHEMA = json.loads(self._body())
                return self._json({"ok": True, "tools": len(TOOL_SCHEMA)})
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
            if self._api_post(p):
                return
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            return self._json({"error": f"{type(e).__name__}: {e}"}, 400)
        return self._json({"error": "unknown endpoint"}, 404)

    # ----------------------------------------------------------------- research platform API
    # Auth, projects, disease panels, reporting, agents and workflows. Each handler returns True
    # once it has written a response; returning None lets the caller fall through.

    def _api_get(self, p):  # noqa: C901
        if p == "/api/disease-panels":
            panels = {}
            for disease in list_panels():
                panel = get_panel(disease)
                panels[disease] = {"name": panel["name"], "description": panel["description"],
                                   "target_count": len(panel["targets"]), "programs": panel["programs"]}
            return self._json(panels) or True
        if p.startswith("/api/disease-panels/") and p.endswith("/top-targets"):
            top_n = int((self._qs().get("top_n") or ["5"])[0])
            return self._json(get_top_targets_by_prevalence(self._seg(p, 2), top_n)) or True
        if p.startswith("/api/disease-panels/"):
            panel = get_panel(self._seg(p, 2))
            if not panel:
                return self._json({"error": "Disease panel not found"}, 404) or True
            return self._json(panel) or True
        if p == "/api/agents":
            return self._json({"optimizer": OPT_AGENT.to_dict(), "analyst": ANA_AGENT.to_dict()}) or True

        # Everything below needs a bearer token.
        if p == "/api/projects" or p.startswith("/api/projects/") or p in (
                "/api/master-agent/status", "/api/agent/memory/suggest", "/api/agent/patterns",
                "/api/voice/status") or (
                p.startswith("/api/workflows/") and p.rsplit("/", 1)[-1] in ("progress", "results")):
            user = self._user()
            if not user:
                return True
        else:
            return None

        if p == "/api/projects":
            return self._json([x.to_dict() for x in list_user_projects(user["user_id"])]) or True
        if p.startswith("/api/projects/"):
            project = get_project(self._seg(p, 2))
            if not project:
                return self._json({"error": "Project not found"}, 404) or True
            return self._json(project.to_dict()) or True
        if p == "/api/master-agent/status":
            return self._json({
                "master_agent": MASTER_AGENT.to_dict(),
                "team": {name: ORCHESTRATOR.get_agent_status(name)
                         for name in ("optimizer", "analyst", "orchestrator")},
                "timestamp": datetime.utcnow().isoformat()}) or True
        if p == "/api/agent/memory/suggest":
            target = (self._qs().get("target") or [""])[0]
            if not target:
                return self._json({"error": "target parameter required"}, 400) or True
            return self._json({"target": target,
                               "suggestions": ORCHESTRATOR.agent_memory.suggest_optimization(target)}) or True
        if p == "/api/agent/patterns":
            patterns = ORCHESTRATOR.agent_memory.learned_patterns
            return self._json({"patterns": patterns, "count": len(patterns)}) or True
        if p == "/api/voice/status":
            return self._json({
                "master_agent": {"status": MASTER_AGENT.status, "listening": MASTER_AGENT.voice_enabled},
                "team": {name: ORCHESTRATOR.get_agent_status(name)
                         for name in ("optimizer", "analyst", "orchestrator")},
                "active_workflows": ORCHESTRATOR.get_active_workflow_count()}) or True
        wid = self._seg(p, 2)
        if p.endswith("/progress"):
            progress = ORCHESTRATOR.get_workflow_progress(wid)
            if progress is None:
                return self._json({"error": "Workflow not found"}, 404) or True
            return self._json(progress) or True
        results = ORCHESTRATOR.get_workflow_results(wid)
        if results is None:
            return self._json({"error": "Workflow not found or not complete"}, 404) or True
        return self._json(results) or True

    def _api_post(self, p):  # noqa: C901
        if p == "/api/auth/login":
            b = self._payload()
            token = authenticate_user(b.get("email"), b.get("password"))
            if not token:
                return self._json({"error": "Invalid credentials"}, 401) or True
            return self._json({"token": token, "email": b.get("email")}) or True
        if p == "/api/auth/register":
            b = self._payload()
            user = create_user(b.get("email"), b.get("name"), b.get("role", "researcher"),
                               b.get("institution", ""))
            return self._json({"user_id": user.user_id, "token": authenticate_user(user.email, b.get("password", "")),
                               "message": "Account created"}, 201) or True

        # Everything below needs a bearer token.
        if not (p.startswith(("/api/projects", "/api/reports/", "/api/papers/", "/api/agents/",
                              "/api/workflows/", "/api/voice", "/api/immersive/scene/",
                              "/api/agent-workflow/", "/api/stream/"))):
            return None
        user = self._user()
        if not user:
            return True
        b = self._payload()

        if p == "/api/projects":
            if not self._has_role(user, "admin", "pi", "researcher"):
                return True
            project = create_project(name=b.get("name"), owner_id=user["user_id"],
                                     program=b.get("program"), description=b.get("description", ""))
            return self._json(project.to_dict(), 201) or True
        if p.startswith("/api/reports/") and p.endswith("/generate"):
            report = generate_screening_report(project_id=b.get("project_id"), campaign_id=self._seg(p, 2),
                                               target=b.get("target"), results=b.get("results", []))
            return self._json({"markdown": report.to_markdown(), "json": json.loads(report.to_json())}) or True
        if p == "/api/papers/generate":
            paper = generate_paper_from_session(b)
            fmt = (self._qs().get("format") or ["markdown"])[0]
            if fmt == "latex":
                return self._text(paper.to_latex(), "text/plain") or True
            if fmt == "json":
                return self._text(paper.to_json(), "application/json") or True
            return self._text(paper.to_markdown(), "text/markdown") or True
        if p == "/api/agents/optimize/docking-params":
            return self._json(OPT_AGENT.optimize_docking_params(
                target_id=b.get("target_id"), validation_compounds=b.get("validation_compounds", []))) or True
        if p == "/api/agents/analyze/hotspots":
            return self._json(ANA_AGENT.identify_hotspots(compounds=b.get("compounds", []),
                                                          target=b.get("target"))) or True
        if p == "/api/agents/analyze/sa-score":
            return self._json(ANA_AGENT.predict_synthetic_accessibility(
                compound_ids=b.get("compound_ids", []))) or True
        if p == "/api/workflows/lead-optimization":
            return self._json(WORKFLOWS.create_lead_optimization_workflow(
                target_id=b.get("target_id"), lead_compound=b.get("lead_compound")), 201) or True
        if p == "/api/workflows/validation":
            return self._json(WORKFLOWS.create_validation_workflow(
                top_compounds=b.get("top_compounds", []), target_id=b.get("target_id")), 201) or True
        if p == "/api/workflows/execute":
            template = b.get("template")
            if template not in WORKFLOW_TEMPLATES:
                return self._json({"error": "Unknown template"}, 400) or True
            wid = str(uuid.uuid4())
            ORCHESTRATOR.queue_workflow(workflow_id=wid, template=template, target=b.get("target"),
                                        compounds=b.get("compounds", []), user_id=user["user_id"])
            return self._json({"workflow_id": wid, "template": template, "target": b.get("target"),
                               "status": "queued",
                               "progress_url": f"/api/workflows/{wid}/progress",
                               "results_url": f"/api/workflows/{wid}/results"}, 201) or True
        if p.startswith("/api/workflows/") and p.endswith("/cancel"):
            if not ORCHESTRATOR.cancel_workflow(self._seg(p, 2)):
                return self._json({"error": "Workflow not found or already finished"}, 404) or True
            return self._json({"workflow_id": self._seg(p, 2), "status": "cancelled"}) or True
        if p == "/api/stream/subscribe":
            types = b.get("stream_types", ["docking", "md", "analysis"])
            return self._json({"ws_url": f"ws://{self.headers.get('Host', 'localhost').split(':')[0]}:{WS_PORT}/ws",
                               "stream_types": types, "available": STREAMING is not None,
                               "message": "Connect to WebSocket for real-time updates"}) or True
        if p in ("/api/voice-command", "/api/voice/process"):
            transcript = b.get("transcript") or b.get("text") or ""
            if not transcript:
                return self._json({"error": "Empty transcript"}, 400) or True
            response = MASTER_AGENT.process_voice_command(transcript)
            if p == "/api/voice-command":
                return self._json(response) or True
            return self._json({"command": transcript, "response": response,
                               "timestamp": datetime.utcnow().isoformat()}) or True
        if p.startswith("/api/immersive/scene/"):
            scene = self._seg(p, 3)
            if scene not in VR_SCENES:
                return self._json({"error": "Unknown scene"}, 404) or True
            return self._json({"scene": scene, "config": VR_SCENES[scene], "ready": True}) or True
        if p.startswith("/api/agent-workflow/"):
            name = self._seg(p, 2)
            if name not in AGENT_WORKFLOWS:
                return self._json({"error": "Unknown workflow"}, 404) or True
            wf = AGENT_WORKFLOWS[name]
            return self._json({"workflow_id": f"wf_{name}_{uuid.uuid4().hex[:8]}", "workflow_name": name,
                               "steps": wf["steps"], "agents_involved": wf["agents"],
                               "status": "running", "progress": 0}, 201) or True
        return None


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
    # Loopback by default. 56 of the 58 /api routes enforce no token at all,
    # so binding every interface put the whole surface on the local network.
    # Pass --host 0.0.0.0 deliberately to reach a headset over Wi-Fi.
    ap.add_argument("--host", default="127.0.0.1")
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
    if start_websocket_server():
        print(f"VR streaming     ->  ws://localhost:{WS_PORT}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
