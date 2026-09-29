"""The credential must not escape, and a model's opinion must not pass as a result.

Two failure modes, both quiet:

A key reaching a file, a log or an error body. This repository is public and
its .env gitignore entry was added after the first push, not before. The client
therefore reads os.environ and offers no other way in -- no config file, no
constructor argument, no string parameter. These tests assert the absence of
that path, because "we just won't pass a key" is a convention and conventions
get refactored.

A language model's answer being read as a computed value. The repo already
separates measurements from SyntheticValue placeholders. A model judgement is a
third category and the most dangerous of the three: a placeholder announces
itself, while "-8.4 kcal/mol" from a chat model looks exactly like a docking
result. Every response is labelled and the system prompt tells the model to
refuse the request rather than produce the number.
"""
import inspect
import json

import pytest

import llm_provider as llm


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for var in (llm.ENV_KEY, llm.ENV_BASE, llm.ENV_MODEL):
        monkeypatch.delenv(var, raising=False)


# --------------------------------------------------------------------------- the credential

def test_there_is_no_way_to_pass_a_key_as_an_argument():
    """A convention is not a boundary. No public function may accept one."""
    for name, fn in inspect.getmembers(llm, inspect.isfunction):
        if name.startswith("_"):
            continue
        params = set(inspect.signature(fn).parameters)
        for forbidden in ("key", "api_key", "token", "auth", "credential", "secret"):
            assert forbidden not in params, f"{name}() accepts {forbidden!r}"


def test_an_unconfigured_client_says_what_is_missing():
    state = llm.configured()
    assert state["configured"] is False
    assert set(state["missing"]) == {llm.ENV_KEY, llm.ENV_BASE}
    assert llm.ENV_KEY in state["reason"]


def test_configured_reports_the_endpoint_but_never_the_key(monkeypatch):
    monkeypatch.setenv(llm.ENV_KEY, "sk-secret-value-abcdefghijklmnop")
    monkeypatch.setenv(llm.ENV_BASE, "https://api.z.ai/api/paas/v4")

    blob = json.dumps(llm.configured())
    assert "https://api.z.ai/api/paas/v4" in blob
    assert "sk-secret-value" not in blob


def test_the_key_is_stripped_from_anything_returned(monkeypatch):
    """Provider error bodies quote request headers more often than expected."""
    monkeypatch.setenv(llm.ENV_KEY, "sk-secret-value-abcdefghijklmnop")
    scrubbed = llm._redact("Authorization: Bearer sk-secret-value-abcdefghijklmnop failed")

    assert "sk-secret-value" not in scrubbed
    assert "<redacted>" in scrubbed


def test_a_call_without_a_key_does_not_reach_the_network(monkeypatch):
    """Unconfigured must fail closed, not attempt an unauthenticated request."""
    def explode(*a, **kw):
        raise AssertionError("urlopen called with no key configured")

    monkeypatch.setattr(llm.urllib.request, "urlopen", explode)
    out = llm.complete([{"role": "user", "content": "hi"}])

    assert out["ok"] is False
    assert llm.ENV_KEY in out["reason"]


# --------------------------------------------------------------------------- opinion vs result

def test_every_response_carries_the_caveat():
    assert "not a measurement" in llm.JUDGEMENT_CAVEAT
    assert llm.JUDGEMENT_CAVEAT in json.dumps(llm.complete([]))


def test_the_judgement_marker_is_distinct_from_the_synthetic_marker():
    """Three categories, three labels: computed, placeholder, model opinion."""
    import synthetic_provenance as sp
    assert llm.JUDGEMENT_MARKER != sp.MARKER
    assert sp.MARKER not in llm.JUDGEMENT_MARKER


def test_the_system_prompt_forbids_inventing_computed_numbers(monkeypatch):
    """The prompt is the control, so its content is asserted rather than trusted."""
    captured = {}

    def fake_complete(messages, **kw):
        captured["messages"] = messages
        return {"ok": True, "text": "I cannot estimate that.", "schema_version": "1.0"}

    monkeypatch.setattr(llm, "complete", fake_complete)
    llm.judgement("What is the binding affinity of aspirin to BCL2?")

    system = captured["messages"][0]
    assert system["role"] == "system"
    for phrase in ("Do NOT invent numeric results", "docking run", "say so"):
        assert phrase in system["content"]


def test_a_successful_judgement_states_it_is_not_a_measurement(monkeypatch):
    monkeypatch.setattr(llm, "complete", lambda m, **kw: {
        "ok": True, "text": "Docking would answer that.", "schema_version": "1.0"})

    out = llm.judgement("anything")
    assert out["is_measurement"] is False
    assert out["judgement"] == "Docking would answer that."


# --------------------------------------------------------------------------- failure handling

def test_a_provider_error_is_returned_not_raised(monkeypatch):
    """An endpoint being down must not take the workspace with it."""
    monkeypatch.setenv(llm.ENV_KEY, "k" * 30)
    monkeypatch.setenv(llm.ENV_BASE, "https://example.invalid/v1")
    monkeypatch.setenv(llm.ENV_MODEL, "glm-5.2")

    def boom(*a, **kw):
        raise llm.urllib.error.URLError("nodename nor servname provided")

    monkeypatch.setattr(llm.urllib.request, "urlopen", boom)
    out = llm.complete([{"role": "user", "content": "hi"}])

    assert out["ok"] is False
    assert "URLError" in out["reason"]


def test_a_missing_model_is_refused_before_any_request(monkeypatch):
    monkeypatch.setenv(llm.ENV_KEY, "k" * 30)
    monkeypatch.setenv(llm.ENV_BASE, "https://example.invalid/v1")

    out = llm.complete([{"role": "user", "content": "hi"}])
    assert out["ok"] is False
    assert llm.ENV_MODEL in out["reason"]
