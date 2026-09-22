# Security Policy

## What this software is

biodao.blockchain is a local molecular workspace. You run `server/server.py` on your own machine
and open it in a browser or a headset. There is no hosted service, no account system worth the
name, and no telemetry. Outbound traffic goes only to public scientific databases, through a
read-only proxy with a fixed host allowlist in `server/server.py` (`PROXY_HOSTS`): RCSB PDB,
AlphaFold DB, UniProt, EBI, Open Targets, ChEMBL, PubChem, NCBI E-utilities, Europe PMC, Reactome,
STRING, Human Protein Atlas, gnomAD, ClinicalTrials.gov, openFDA, Pharos/NCATS, KEGG, BindingDB,
Foldseek, BioThings, Ensembl and Guide to Pharmacology. Requests to any other host are refused, and
only `https` GET is forwarded.

That keeps the attack surface small, but it is not zero, and the notes below matter more than the
reassurance above.

## Known hazards you should understand before deploying

These are current, verified properties of the code, not hypotheticals. None of them is a problem on
a laptop you control. All of them are a problem on a shared or public network.

**The server listens on every interface by default.** `server/server.py` defaults to
`--host 0.0.0.0`, and the WebSocket streaming server does the same. Anyone who can reach your
machine's port 8000 gets the workspace — this is deliberate, because it is how a headset on the
same Wi-Fi connects, but it means an untrusted network exposes the app. Pass `--host 127.0.0.1` if
you do not need the LAN.

**Authentication is a demo stub, not authentication.** `server/auth.py`'s `authenticate_user()`
ignores the password argument entirely: it returns a valid JWT for any email already present in the
in-memory user store, and its own docstring says "In production, use bcrypt". There is no password
storage, and the user store does not survive a restart. Do not put this behind a public address and
do not treat its roles as a security boundary.

**`JWT_SECRET` has a default.** `server/auth.py` reads `os.getenv('JWT_SECRET',
'dev-secret-change-in-production')`. Tokens are HS256. Deployed without that variable set, the
signing key is a published constant and anyone can mint an admin token. If you ever run this
anywhere but localhost, set `JWT_SECRET` to a long random value first.

**Most API routes are unauthenticated.** Only two handlers in `server/server.py` call the token
check; everything else — structure loading, docking, simulation, file ingestion, the BigQuery
panel — is open to whoever can reach the port.

**The workspace is drivable from outside.** The agent command channel lets any HTTP client dispatch
tool calls into connected browser sessions. Combined with the two points above, reaching the port
means driving the app.

**Files you import are parsed locally.** PDF, DOCX, XLSX, HTML, XML, SDF and SMILES ingestion runs
through third-party parsers on your machine. Treat compound files from strangers with the same
caution as any other untrusted document.

**Structures and queries you load leave the machine.** A PDB id, gene name or SMILES string you
search is sent to the public database that answers it. Nothing else is transmitted, but if a
structure is confidential, a lookup discloses it to that database operator.

## Supported versions

There are no releases or version tags. The `main` branch is the only supported code. Fixes land
there; there is no backport process.

## Reporting a vulnerability

Email **x@agifuturefoundation.org** with `SECURITY` in the subject line. Please include:

- what you found, and which file and line it lives in;
- the exact command or request that demonstrates it, and its output — the project's general
  standard is that a claim is not established until it has been executed (see `CONTRIBUTING.md`);
- what an attacker gets out of it, and what they need to already have;
- how you would like to be credited, or that you would rather not be.

This is a small project without a staffed security function. Expect an acknowledgement within
about a week. If you have not heard anything after two weeks, send the email again — the more
likely explanation is that it was missed than that it was ignored.

Please do not open a public issue for a vulnerability, and please give the maintainer a reasonable
window to respond before publishing. There is no bug bounty.

## Out of scope

- The absence of real authentication, and the `JWT_SECRET` default. Both are documented above; a
  report that restates them adds nothing, though a patch fixing them is welcome.
- Anything that requires an attacker to already be running code as your user.
- Denial of service against a server you started yourself on your own machine.
- Vulnerabilities in the public databases the app queries. Report those to their operators.

Scientific incorrectness is not a security issue, but it is taken just as seriously here. Report a
wrong number through the "Suspect value" issue template instead.
