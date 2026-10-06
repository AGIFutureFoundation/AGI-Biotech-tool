"""Three ways this server gave away more than it meant to.

All three were found by review rather than by the suite, and all three are the
same shape: a check that exists in one place and not in its neighbour, so the
code reads as if it were enforced.

  Registration took the role from the request body, on an endpoint that needs
  no authentication. Anyone could POST {"role": "admin"} and receive
  manage_users, delete_projects and edit_all. It also dropped the password, so
  create_user stored password_hash = None and the account it had just made
  could never be signed in to.

  /api/projects filtered by membership; /api/projects/<id> did not. The listing
  being correct is what made the gap easy to miss.

  Access-Control-Allow-Origin was "*" on every response and /api/command sat
  outside the authenticated prefix list, so any page the user was visiting
  could drive their local workspace. Binding 127.0.0.1 does not help: a browser
  tab is on 127.0.0.1 too.
"""
import importlib

import pytest

import auth
import server


@pytest.fixture(autouse=True)
def _clean_users():
    saved = dict(auth.USERS_DB)
    auth.USERS_DB.clear()
    yield
    auth.USERS_DB.clear()
    auth.USERS_DB.update(saved)


# --------------------------------------------------------------------------- registration

def test_registration_does_not_let_the_client_pick_its_role():
    """The handler must not pass a request-supplied role into create_user."""
    # Read the file, not a method: registration is not handled in do_POST, and
    # inspect.getsource on the wrong method raised rather than failing the
    # assertion -- which looked like a code bug and was a test bug.
    src = open(server.__file__).read()
    start = src.index('if p == "/api/auth/register":')
    block = src[start:start + 1600]

    # Assert on the call, not on a substring of the block. Twice now a comment
    # explaining why something was removed has contained the very string the
    # test looked for, failing a correct fix. The call is the thing that runs.
    call_start = block.index("user = create_user(")
    call = block[call_start:block.index(")", block.index("password=", call_start))]

    assert 'b.get("role"' not in call, f"registration passes a request role: {call}"
    assert '"researcher"' in call, f"registration should pin the role: {call}"
    assert "password=" in call, f"registration must pass the password: {call}"


def test_a_registered_account_can_actually_log_in():
    """The regression: the password was dropped, so the new account was dead."""
    user = auth.create_user("a@example.test", "A", "researcher", "", password="hunter2")

    assert user.password_hash is not None
    assert auth.authenticate_user("a@example.test", "hunter2")
    assert auth.authenticate_user("a@example.test", "wrong") is None


def test_an_account_made_without_a_password_still_cannot_log_in():
    """The underlying guarantee must stay: no password means no sign-in."""
    user = auth.create_user("b@example.test", "B")
    assert user.password_hash is None
    assert auth.authenticate_user("b@example.test", "") is None


def test_admin_is_not_a_role_a_new_account_can_hold(): 
    """Pins what the escalation would have granted, so the loss is visible."""
    assert auth.Permission.has_permission("admin", "manage_users")
    assert auth.Permission.has_permission("admin", "delete_projects")
    assert not auth.Permission.has_permission("researcher", "manage_users")
    assert not auth.Permission.has_permission("researcher", "delete_projects")


# --------------------------------------------------------------------------- project access

def test_fetching_a_project_checks_membership():
    """A bare dict lookup here let any logged-in user read any project by id."""
    source = open(server.__file__).read()
    start = source.index('if p.startswith("/api/projects/"):')
    block = source[start:start + 900]

    assert "project.members" in block, "project fetch does not check membership"


def test_a_project_you_cannot_see_is_indistinguishable_from_one_that_is_gone():
    """Otherwise the endpoint confirms which ids exist to anyone who asks."""
    source = open(server.__file__).read()
    start = source.index('if p.startswith("/api/projects/"):')
    block = source[start:start + 900]

    # Count the response construction, not the phrase: the comment explaining
    # this very property also contains it, which inflated the count to 2.
    assert block.count('{"error": "Project not found"}, 404') == 1, \
        "the missing and forbidden cases should share one response"
    assert "403" not in block, "a distinct 403 here leaks which project ids exist"


# --------------------------------------------------------------------------- cross-origin

class _Req:
    """Enough of a handler to exercise the origin check."""
    def __init__(self, origin=None, host="localhost:8800"):
        self.headers = {}
        if origin:
            self.headers["Origin"] = origin
        self.headers["Host"] = host

    _origin_allowed = server.Handler._origin_allowed


@pytest.mark.parametrize("origin,allowed", [
    (None,                      True),   # curl, a native client, same-origin GET
    ("http://localhost:8800",   True),   # the app itself
    ("http://127.0.0.1:8800",   True),
    ("http://localhost:3000",   True),   # a dev server on the same machine
    ("https://evil.example",    False),
    ("http://evil.example",     False),
    ("null",                    False),  # sandboxed iframe
])
def test_origin_allowlist(origin, allowed):
    assert _Req(origin)._origin_allowed() is allowed


def test_a_cross_origin_post_is_refused_before_any_handler_runs():
    """Headers are not a defence: CORS gates reading the reply, not sending it.

    A state-changing POST lands whether or not the attacker can read what came
    back, so the refusal has to happen on the request.
    """
    import inspect
    src = inspect.getsource(server.Handler.do_POST)
    head = src[:src.index("try:")]

    assert "_origin_allowed" in head, "do_POST does not check Origin before dispatching"
    assert "403" in head


def test_the_wildcard_origin_is_gone():
    source = open(server.__file__).read()
    assert '"Access-Control-Allow-Origin", "*"' not in source
