import sys
import os
import hashlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "py_server")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data_structures")))

import server
from hash_table import HashTable


def _reset_login_state():
    """Reset server auth state for repeatable login test setup."""
    server.accounts = HashTable()
    server._append_account = lambda username, account_data: None


def test_login_flow():
    _reset_login_state()

    assert server.authenticate_account("", "pass") == "invalid", "Empty username should be invalid"
    assert server.authenticate_account("alice", "") == "invalid", "Empty password should be invalid"
    assert server.authenticate_account("   ", "pass") == "invalid", "Whitespace username should be invalid"
    assert server.authenticate_account("new_user", "secret") == "new", "Unknown user should be detected as new"
    _reset_login_state()

    password_hash = hashlib.sha256("secret".encode("utf-8")).hexdigest()
    server.create_account("alice", password_hash, team="pink")
    assert server.authenticate_account("alice", "secret") == "existing", "Correct password should authenticate existing account"
    assert server.authenticate_account("alice", "wrong-password") == "invalid", "Wrong password should be invalid"

def run_all_tests():
    test_login_flow()
    print("\nAll tests passed.")


if __name__ == "__main__":
    run_all_tests()
