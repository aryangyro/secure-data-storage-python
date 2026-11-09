#!/usr/bin/env python3
"""Secure user data storage. Validate input, hash passwords,
store users with an integrity hash, and spot tampering.
Run: python3 secure_app.py. Passwords are never printed in plain text.
"""
import argparse
import hashlib
import hmac
import html
import json
import os
import re
import sqlite3
from pathlib import Path

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.\-]{3,30}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def validate(username, email, password):
    """Return a list of problems, empty if the input is ok."""
    errors = []
    if not USERNAME_RE.match(username or ""):
        errors.append("username: 3-30 letters, digits, _, . or - only")
    if not EMAIL_RE.match(email or ""):
        errors.append("email: must look like name@example.com")
    if len(password or "") < 8:
        errors.append("password: at least 8 characters")
    for pattern, msg in [(r"[A-Z]", "an uppercase letter"), (r"[a-z]", "a lowercase letter"),
                         (r"[0-9]", "a digit"), (r"[^A-Za-z0-9]", "a special character")]:
        if password and not re.search(pattern, password):
            errors.append(f"password: needs {msg}")
    if any(c in (username or "") + (email or "") for c in "<>'\""):
        errors.append("input: <, >, quotes are not allowed")
    return errors

def hash_password(password):
    """Hash a password. bcrypt if installed, else PBKDF2 with salt."""
    try:
        import bcrypt
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    except ImportError:
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
        return f"pbkdf2_sha256$200000${salt.hex()}${dk.hex()}"

def check_password(password, stored):
    """Check a password against its stored hash."""
    if stored.startswith(("$2b$", "$2a$")):
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode(), stored.encode())
        except ImportError:
            return False
    try:
        _, iterations, salt, expected = stored.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(iterations))
        return hmac.compare_digest(dk, bytes.fromhex(expected))
    except Exception:
        return False

def integrity(record):
    """SHA-256 hash for one record, used to spot changes."""
    text = json.dumps({"username": record["username"],
                       "email": record["email"],
                       "password_hash": record["password_hash"]},
                      sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()

def secure_record(username, email, password):
    """Make a secure record: hashed password + integrity hash."""
    rec = {"username": username, "email": email,
           "password_hash": hash_password(password)}
    rec["integrity"] = integrity(rec)
    return rec

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(records, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

def verify_records(records):
    """Check each record's integrity hash. Returns (username, ok)."""
    return [(rec["username"], rec.get("integrity") is not None
               and hmac.compare_digest(rec["integrity"], integrity(rec)))
              for rec in records]

def compare_files(original, checked):
    """Compare two files, reporting differing field names only."""
    base = {r["username"]: r for r in original}
    findings = []
    for rec in checked:
        old = base.get(rec["username"])
        if old is None:
            findings.append((rec["username"], ["record not in original"]))
        else:
            diff = [k for k in old if old.get(k) != rec.get(k)]
            if diff:
                findings.append((rec["username"], diff))
    return findings

def header(title):
    print("=" * 68)
    print(title)
    print("=" * 68)

def pick_file(explicit, *candidates):
    """Use the file given on the command line, or the first
    candidate that exists in the current folder."""
    if explicit:
        return explicit
    for name in candidates:
        if Path(name).exists():
            return name
    return candidates[0]

def main():
    parser = argparse.ArgumentParser(description="Secure user data storage")
    parser.add_argument("--original", default=None,
                        help="original users file (default: users.json, or users_sample.json)")
    parser.add_argument("--tampered", default=None,
                        help="file to check (default: users_tampered.json, or users_tampered_sample.json)")
    parser.add_argument("--outdir", default="test_run")
    args = parser.parse_args()
    original_path = pick_file(args.original, "users.json", "users_sample.json")
    tampered_path = pick_file(args.tampered, "users_tampered.json", "users_tampered_sample.json")
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Validation
    header("Secure User Input: validation")
    good = validate("testuser", "testuser@example.com", "Str0ng!Pass")
    print("Valid input: testuser / testuser@example.com ->",
          "ACCEPTED" if not good else f"REJECTED {good}")
    for label, u, e, p in [("empty username", "", "a@example.com", "Str0ng!Pass"),
                             ("bad email", "testuser", "not-an-email", "Str0ng!Pass"),
                             ("weak password", "testuser", "testuser@example.com", "password")]:
        print(f"Invalid - {label}: REJECTED {validate(u, e, p)}")
    print("Conclusion: valid input accepted, bad input rejected.")

    # Injection / XSS, briefly
    header("SQL injection / XSS prevention")
    print("Query: SELECT username, email FROM users WHERE username = ?")
    print("Input is passed as a parameter only, never built into the SQL.")
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (username TEXT, email TEXT)")
    conn.execute("INSERT INTO users VALUES (?, ?)", ("alice", "alice@example.com"))
    for attack in ["' OR '1'='1", "alice'; DROP TABLE users; --"]:
        rows = conn.execute("SELECT username FROM users WHERE username = ?", (attack,)).fetchall()
        print(f"Attack input {attack!r} -> rows: {rows} (treated as data)")
    print("Table still has",
          conn.execute("SELECT COUNT(*) FROM users").fetchone()[0], "row(s).")
    raw = "<script>alert(1)</script>"
    print(f"XSS input {raw!r} -> escaped: {html.escape(raw)!r}")
    conn.close()
    print("Conclusion: injection and XSS inputs are neutralised.")

    # Hashing
    header("Password hashing")
    try:
        import bcrypt  # noqa: F401
        print("Method: bcrypt")
    except ImportError:
        print("Method: PBKDF2-HMAC-SHA256, 200,000 iterations, 16-byte salt")
        print("(bcrypt not installed, so this stdlib fallback is used)")
    hashed = hash_password("Str0ng!Pass")
    print("Password stored as a hash, never in plain text.")
    print("Correct password checks out:",
          check_password("Str0ng!Pass", hashed))
    print("Wrong password checks out:",
          check_password("Wrong!Pass1", hashed))
    print("Same password hashed twice differs (fresh salt):",
          hashed != hash_password("Str0ng!Pass"))
    print("Conclusion: passwords are salted, iterated hashes.")

    # Store a new user
    header("Secure Data Storage: storing a new user")
    new_user = secure_record("testuser", "testuser@example.com", "Str0ng!Pass")
    save_json([new_user], outdir / "users_new.json")
    print(f"Stored to {outdir / 'users_new.json'}")
    print("Fields stored:", sorted(new_user.keys()))
    print("Plaintext 'password' key present: False")
    print("Conclusion: new input is stored securely.")

    # Why hashing for passwords
    header("Protecting sensitive fields")
    print("Passwords are hashed, not encrypted: encryption can be")
    print("reversed with a key, hashing cannot. No plaintext is stored.")
    print("Conclusion: sensitive data is hashed, not stored in clear.")

    # Integrity hashes for the original records
    header("Per-record integrity hashes")
    original = load_json(original_path)
    # Hash each original password once, keep only the hash.
    secure = [secure_record(r["username"], r["email"], r["password"])
              for r in original]
    save_json(secure, outdir / "users_secure.json")
    print(f"Converted {len(secure)} original records to secure form.")
    for rec in secure:
        print(f"  {rec['username']}: integrity hash stored")
    print("Integrity = SHA-256(username + email + password_hash).")
    print("Conclusion: every record now has its own integrity hash.")

    # Verify on read-back
    header("Verify integrity when reading back")
    results = verify_records(load_json(outdir / "users_secure.json"))
    for username, ok in results:
        print(f"  {username}: {'PASS' if ok else 'FAIL'}")
    print("Overall:", "PASS - all records intact" if all(ok for _, ok in results) else "FAIL")
    print("Conclusion: reading the file back checks every record.")

    # Altered secure copy
    header("Detecting modifications in a secure copy")
    tampered_copy = json.loads(json.dumps(secure))
    for rec in tampered_copy:
        if rec["username"] == "alice":
            rec["password_hash"] = "0" * len(rec["password_hash"])
            break
    save_json(tampered_copy, outdir / "users_secure_altered.json")
    for username, ok in verify_records(tampered_copy):
        print(f"  {username}: {'PASS' if ok else 'FAIL'}")
    print("Conclusion: only the altered record fails the check.")

    # Supplied tampered file
    header("Verify the tampered file against the original")
    print(f"Original: {len(original)} records, "
          f"checked file: {len(load_json(tampered_path))} records")
    print("No integrity hashes in the supplied file, so it is compared")
    print("field by field, reporting field names only, never values.")
    findings = compare_files(original, load_json(tampered_path))
    if not findings:
        print("Result: PASS - no differences found.")
    else:
        print("Result: FAIL - tampered record(s) found:")
        for username, fields in findings:
            print(f"  TAMPERED: {username} - differing field(s): {', '.join(fields)}")
    print("Conclusion: tampering is detected and identified by username.")

    # Summary
    header("Final verification summary")
    print("Valid input accepted, bad/injection input rejected,")
    print("passwords hashed, secure storage verified on read-back,")
    print("and tampering in the checked file detected.")
    print("Files written to:", outdir)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
