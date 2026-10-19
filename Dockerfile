# A deployable image, because the brief promises one.
#
# docs/investor-brief.html offers pharma "an agent-operable workspace behind
# their own firewall". Until this file there was no way to put it there: no
# container, no deployment artefact, nothing but a README and a virtualenv on
# the author's laptop. That is a claim the product could not support, which is
# the class of gap this repository exists to close rather than carry.
#
#   docker build -t biodao .
#   docker run --rm -p 8000:8000 biodao          # http://localhost:8000
#   docker run --rm biodao make verify           # the gate, inside the image
#
# Two deliberate choices worth stating:
#
# NOT slim. rdkit, openmm and lxml are compiled wheels with system library
# dependencies; python:3.12-slim saves about 700 MB and then needs most of it
# back as build-essential, libxrender and friends, for a result that breaks
# whenever a wheel is missing for the platform. The full image builds on arm64
# and amd64 without a compiler toolchain.
#
# The venv is kept, not flattened into the system Python. Every command in this
# repository is written as `.venv/bin/python` on purpose -- the Makefile says
# why: the system interpreter has neither RDKit nor pytest, and several modules
# degrade quietly when an import fails, so the wrong interpreter produces a
# passing run that proves nothing. Keeping the venv means a command that works
# on a laptop works here character for character.
FROM python:3.12

# Node is here for `make jstest` and the evals, which are half the test suite.
# An image that can only run the Python half cannot run `make verify`, and an
# image that cannot run the gate is not the thing the gate certified.
RUN apt-get update \
 && apt-get install -y --no-install-recommends nodejs npm ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencies first, so a source edit does not re-resolve the wheel set.
COPY requirements.txt ./
RUN python -m venv .venv \
 && .venv/bin/pip install --no-cache-dir --upgrade pip \
 && .venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as a non-root user. The server writes only to the content store and the
# key directory, both under $HOME, so the image needs no writable application
# directory and can run read-only if the deployment wants that.
RUN useradd --create-home --uid 10001 biodao \
 && chown -R biodao:biodao /app
USER biodao
ENV HOME=/home/biodao

# 127.0.0.1 is the repository's default and the right one for a laptop. In a
# container it would make the server unreachable from outside, since the
# published port forwards to the container's own interface. 0.0.0.0 here is
# therefore not a loosening of the default: the isolation that --host 127.0.0.1
# provides on a laptop is provided by the container boundary instead, and
# whether the port is exposed is the operator's decision at `docker run`.
#
# JWT_SECRET is deliberately not set. server/auth.py warns when it is missing
# and the warning tells you how to set it; baking a default here would turn
# that warning off and ship every deployment the same signing key.
EXPOSE 8000
ENV AGI_CONTENT_STORE=/home/biodao/.cache/agi-bioxr/objects

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD .venv/bin/python -c "import urllib.request,sys; \
      sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/', timeout=4).status < 500 else 1)"

CMD [".venv/bin/python", "server/server.py", "--host", "0.0.0.0", "--port", "8000"]
