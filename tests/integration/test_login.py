"""
test_login.py  —  unit tests for login functions in server.py
Run with: pytest test_login.py -v

Tests cover authenticate_account() and create_account() in isolation
by patching out all file I/O and the accounts HashTable.
"""

import sys
import types
import hashlib
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()


def make_account(password: str, team: str = "default") -> dict:
    return {"password": hash_pw(password), "team": team}


# ---------------------------------------------------------------------------
# Fixture: load server module with a controlled accounts table
# ---------------------------------------------------------------------------

@pytest.fixture()
def server(monkeypatch, tmp_path):
    """
    Import server.py with:
      - all data files redirected to a temp directory (no real disk I/O)
      - websockets stubbed out so the event loop never starts
      - accounts pre-populated via the returned helper
    Returns the loaded server module.
    """
    # Remove any cached copy
    for key in list(sys.modules.keys()):
        if key in ("server", "websockets", "websockets.exceptions"):
            del sys.modules[key]

    # Stub websockets so importing server.py doesn't fail
    ws_mod = types.ModuleType("websockets")
    ws_exc = types.ModuleType("websockets.exceptions")
    class ConnectionClosed(Exception): pass
    ws_exc.ConnectionClosed = ConnectionClosed
    ws_mod.exceptions = ws_exc
    ws_mod.serve = MagicMock()
    sys.modules["websockets"] = ws_mod
    sys.modules["websockets.exceptions"] = ws_exc

    # Stub every other sibling module server.py imports
    for mod_name in ("games", "leaderboards", "profile",
                     "match_history", "player_search", "memory"):
        m = types.ModuleType(mod_name)
        m.refresh = lambda: None
        sys.modules[mod_name] = m

    # Point data files at temp dir so no real files are read/written
    (tmp_path / "accounts.ndjson").write_text("")
    (tmp_path / "chats.ndjson").write_text("")
    (tmp_path / "sessions.ndjson").write_text("")
    (tmp_path / "games.ndjson").write_text("")

    # Build sys.path so data_structures is importable
    project_root = Path(__file__).parent.parent / "py_server"
    for p in [str(project_root), str(project_root / "data_structures")]:
        if p not in sys.path:
            sys.path.insert(0, p)

    # Patch the data_folder path before import
    with patch("builtins.open", mock_open(read_data="")):
        import importlib.util
        server_path = project_root / "server.py"
        spec = importlib.util.spec_from_file_location("server", server_path)
        srv = importlib.util.module_from_spec(spec)

        # Redirect data_folder before module-level code runs
        srv.__dict__["data_folder"] = tmp_path
        spec.loader.exec_module(srv)

    # Override file paths to temp dir
    srv.accounts_file  = tmp_path / "accounts.ndjson"
    srv.sessions_file  = tmp_path / "sessions.ndjson"
    srv.chats_file     = tmp_path / "chats.ndjson"

    return srv


# ---------------------------------------------------------------------------
# authenticate_account — happy paths
# ---------------------------------------------------------------------------

class TestAuthenticateAccountValid:

    def test_existing_correct_password(self, server):
        server.accounts.put("alice", make_account("secret"))
        assert server.authenticate_account("alice", "secret") == "existing"

    def test_new_user_returns_new(self, server):
        assert server.authenticate_account("ghost", "anypass") == "new"

    def test_wrong_password_returns_invalid(self, server):
        server.accounts.put("alice", make_account("correct"))
        assert server.authenticate_account("alice", "wrong") == "invalid"

    def test_strips_whitespace_from_username(self, server):
        server.accounts.put("alice", make_account("pw"))
        assert server.authenticate_account("  alice  ", "pw") == "existing"

    def test_strips_whitespace_from_password(self, server):
        server.accounts.put("alice", make_account("pw"))
        assert server.authenticate_account("alice", "  pw  ") == "existing"

    def test_wrong_password_after_strip(self, server):
        server.accounts.put("alice", make_account("pw"))
        assert server.authenticate_account("alice", "  wrong  ") == "invalid"


# ---------------------------------------------------------------------------
# authenticate_account — edge / invalid inputs
# ---------------------------------------------------------------------------

class TestAuthenticateAccountEdge:

    def test_empty_username_returns_invalid(self, server):
        assert server.authenticate_account("", "pw") == "invalid"

    def test_empty_password_returns_invalid(self, server):
        assert server.authenticate_account("alice", "") == "invalid"

    def test_both_empty_returns_invalid(self, server):
        assert server.authenticate_account("", "") == "invalid"

    def test_whitespace_only_username_returns_invalid(self, server):
        assert server.authenticate_account("   ", "pw") == "invalid"

    def test_whitespace_only_password_returns_invalid(self, server):
        assert server.authenticate_account("alice", "   ") == "invalid"

    def test_case_sensitive_username(self, server):
        server.accounts.put("Alice", make_account("pw"))
        # "alice" (lowercase) is a different, unknown user
        assert server.authenticate_account("alice", "pw") == "new"

    def test_case_sensitive_password(self, server):
        server.accounts.put("alice", make_account("Password"))
        assert server.authenticate_account("alice", "password") == "invalid"

    def test_unicode_password(self, server):
        server.accounts.put("alice", make_account("pässwörd"))
        assert server.authenticate_account("alice", "pässwörd") == "existing"

    def test_very_long_username(self, server):
        username = "a" * 500
        assert server.authenticate_account(username, "pw") == "new"

    def test_very_long_password(self, server):
        server.accounts.put("alice", make_account("pw"))
        assert server.authenticate_account("alice", "x" * 10_000) == "invalid"

    def test_sql_injection_style_input(self, server):
        assert server.authenticate_account("' OR '1'='1", "pw") == "new"

    def test_returns_string_not_bool(self, server):
        result = server.authenticate_account("nobody", "pw")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# create_account
# ---------------------------------------------------------------------------

class TestCreateAccount:

    def test_creates_account_in_memory(self, server):
        server.create_account("bob", hash_pw("pw"), "red")
        account = server.accounts.get("bob")
        assert account is not None

    def test_stores_correct_password_hash(self, server):
        server.create_account("bob", hash_pw("pw"), "red")
        assert server.accounts.get("bob")["password"] == hash_pw("pw")

    def test_stores_team(self, server):
        server.create_account("bob", hash_pw("pw"), "blue")
        assert server.accounts.get("bob")["team"] == "blue"

    def test_default_team(self, server):
        server.create_account("bob", hash_pw("pw"))
        assert server.accounts.get("bob")["team"] == "default"

    def test_new_account_authenticates_immediately(self, server):
        server.create_account("carol", hash_pw("mypass"), "green")
        assert server.authenticate_account("carol", "mypass") == "existing"

    def test_overwrite_existing_account(self, server):
        server.create_account("dave", hash_pw("old"), "red")
        server.create_account("dave", hash_pw("new"), "blue")
        assert server.accounts.get("dave")["password"] == hash_pw("new")
        assert server.accounts.get("dave")["team"] == "blue"

    def test_multiple_accounts_independent(self, server):
        server.create_account("eve",   hash_pw("pw1"), "red")
        server.create_account("frank", hash_pw("pw2"), "blue")
        assert server.authenticate_account("eve",   "pw1") == "existing"
        assert server.authenticate_account("frank", "pw2") == "existing"
        assert server.authenticate_account("eve",   "pw2") == "invalid"

    def test_appends_to_accounts_file(self, server, tmp_path):
        server.create_account("grace", hash_pw("pw"), "red")
        content = (tmp_path / "accounts.ndjson").read_text()
        assert "grace" in content

    def test_unicode_username(self, server):
        server.create_account("ñoño", hash_pw("pw"), "red")
        assert server.accounts.get("ñoño")["team"] == "red"

    def test_create_then_wrong_password_fails(self, server):
        server.create_account("henry", hash_pw("correct"), "red")
        assert server.authenticate_account("henry", "wrong") == "invalid"


# ---------------------------------------------------------------------------
# Login flow — authenticate then create (simulates the full login path)
# ---------------------------------------------------------------------------

class TestLoginFlow:

    def test_new_user_flow(self, server):
        """Unknown user → 'new' → create_account → then authenticates."""
        result = server.authenticate_account("newuser", "pass123")
        assert result == "new"
        server.create_account("newuser", hash_pw("pass123"), "red")
        assert server.authenticate_account("newuser", "pass123") == "existing"

    def test_existing_user_flow(self, server):
        """Pre-existing account authenticates directly without re-creating."""
        server.accounts.put("olduser", make_account("hunter2"))
        assert server.authenticate_account("olduser", "hunter2") == "existing"

    def test_wrong_password_never_creates(self, server):
        """A failed login must not create or modify any account."""
        server.accounts.put("victim", make_account("correct"))
        server.authenticate_account("victim", "wrong")
        # password must not have changed
        assert server.authenticate_account("victim", "correct") == "existing"

    def test_login_after_multiple_failed_attempts(self, server):
        server.accounts.put("alice", make_account("right"))
        for _ in range(5):
            assert server.authenticate_account("alice", "wrong") == "invalid"
        assert server.authenticate_account("alice", "right") == "existing"

    def test_many_users_no_collision(self, server):
        """100 distinct accounts must each authenticate independently."""
        for i in range(100):
            server.create_account(f"user{i}", hash_pw(f"pw{i}"), "red")
        for i in range(100):
            assert server.authenticate_account(f"user{i}", f"pw{i}") == "existing"
            assert server.authenticate_account(f"user{i}", f"pw{i+1}") == "invalid"