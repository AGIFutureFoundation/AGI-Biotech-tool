#!/usr/bin/env python3
"""MCP server: lets Claude (or any MCP client) drive a live biodao.blockchain workspace.

The workspace runs in a browser. This process speaks MCP over stdin/stdout, and forwards each tool call
to `server/server.py`, which pushes it to the connected browser session and waits for the answer. So the
agent is not simulating the app: it is operating the same buttons a researcher would, and the result it
gets back is the one on screen.

Register it with Claude Code:

    claude mcp add biodao -- /Users/romanbridge.x/Projects/agi-bioxr/.venv/bin/python \\
        /Users/romanbridge.x/Projects/agi-bioxr/server/mcp_server.py

Requirements: the workspace server running (`.venv/bin/python server/server.py`) and the app open in a
browser tab. Nothing else; no keys, no network beyond localhost.
"""
import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("BIODAO_URL", "http://localhost:8000")
PROTOCOL_VERSION = "2024-11-05"

# Used when the browser has not published its live schema yet, so the tool list is never empty.
FALLBACK_TOOLS = [
    {"name": "load_target", "description": "Load a target by gene symbol (SOD1, LRRK2, BCL2L1).",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "load_structure", "description": "Load a PDB entry by id.",
     "parameters": {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}},
    {"name": "find_pockets", "description": "Detect and rank binding pockets.", "parameters": {"type": "object", "properties": {}}},
    {"name": "dock", "description": "Dock the current ligand and report ranked poses.",
     "parameters": {"type": "object", "properties": {"runs": {"type": "integer"}, "steps": {"type": "integer"}}}},
    {"name": "screen_library", "description": "Dock the whole compound library and rank it.",
     "parameters": {"type": "object", "properties": {"limit": {"type": "integer"}}}},
    {"name": "gather_evidence", "description": "Collect target evidence from the public databases.", "parameters": {"type": "object", "properties": {}}},
    {"name": "describe_scene", "description": "Describe what is loaded and the latest result.", "parameters": {"type": "object", "properties": {}}},
]


def http(path, payload=None, timeout=240):
    url = f"{BASE}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode() or "{}") or {"ok": False, "error": f"HTTP {e.code}"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"workspace unreachable at {BASE}: {e}"}


def live_tools():
    got = http("/api/tools")
    tools = got.get("tools") if isinstance(got, dict) else None
    return tools or FALLBACK_TOOLS


def mcp_tool_list():
    out = []
    for t in live_tools():
        out.append({
            "name": t["name"],
            "description": t.get("description", ""),
            "inputSchema": t.get("parameters") or {"type": "object", "properties": {}},
        })
    return out


def call_tool(name, args):
    status = http("/api/command/status")
    if isinstance(status, dict) and status.get("sessions", 0) == 0:
        return ("The workspace server is running but no browser session is connected. "
                f"Open {BASE} in a browser, then try again."), True
    res = http("/api/command", {"tool": name, "args": args or {}})
    if not isinstance(res, dict):
        return f"unexpected reply: {res!r}", True
    if res.get("ok"):
        payload = res.get("result")
        return json.dumps(payload, indent=1) if not isinstance(payload, str) else payload, False
    return res.get("error", "the workspace reported a failure"), True


def respond(msg_id, result=None, error=None):
    out = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        out["error"] = error
    else:
        out["result"] = result
    sys.stdout.write(json.dumps(out) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method, msg_id = msg.get("method"), msg.get("id")

        if method == "initialize":
            respond(msg_id, {"protocolVersion": PROTOCOL_VERSION,
                             "capabilities": {"tools": {"listChanged": True}},
                             "serverInfo": {"name": "biodao.blockchain", "version": "1.0.0"}})
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            respond(msg_id, {"tools": mcp_tool_list()})
        elif method == "tools/call":
            params = msg.get("params") or {}
            text, is_error = call_tool(params.get("name"), params.get("arguments"))
            respond(msg_id, {"content": [{"type": "text", "text": text}], "isError": is_error})
        elif method == "ping":
            respond(msg_id, {})
        elif msg_id is not None:
            respond(msg_id, error={"code": -32601, "message": f"unknown method {method}"})


if __name__ == "__main__":
    main()
