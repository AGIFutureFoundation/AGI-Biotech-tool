#!/usr/bin/env python3
"""AGI BioXR local server.

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
    req = urllib.request.Request(url, headers={"User-Agent": "agi-bioxr/1.0"})
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
    print(f"AGI BioXR  ->  {scheme}://localhost:{a.port}   (LAN: {scheme}://{lan_ip()}:{a.port})")
    print("engines:", ", ".join(f"{k}={'yes' if v else 'no'}" for k, v in HAVE.items()))
    srv.serve_forever()


if __name__ == "__main__":
    main()
