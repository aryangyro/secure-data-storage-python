# Work log

## Nov 8, 2026 — Secure data storage in Python

### What was built

A single-file Python project that stores user accounts securely:
input validation, password hashing, per-record integrity hashes,
and tamper detection.

- `secure_app.py` (about 250 lines) — the whole project. It
  validates usernames, emails and passwords; shows SQL injection
  and XSS inputs being neutralised with parameterised queries and
  HTML escaping; hashes passwords with bcrypt when it is
  available and PBKDF2-HMAC-SHA256 (200,000 iterations, 16-byte
  salt) as a standard-library fallback; stores each user with a
  `password_hash` and a SHA-256 `integrity` field and no plaintext
  `password` key; verifies every record on read-back; and compares
  a tampered file against the original, reporting username and
  field names only, never values.
- `users_sample.json` — three fake users (alice, bob, carol)
  with clearly dummy passwords, so anyone can run the project
  without real data.
- `users_tampered_sample.json` — the same three users, with only
  bob's password changed, so the tamper check has exactly one
  thing to find.
- `README.md` — a long beginner-friendly guide: why plain-text
  passwords are dangerous, hashing vs encryption, salt,
  bcrypt/PBKDF2, integrity hashes, how tamper detection works,
  step-by-step run instructions, expected output, a file list,
  a glossary, and limitations.
- `.gitignore` — keeps the generated `test_run/` output and any
  real `users.json` files out of the repo.

### Test results

Ran on Nov 8, 2026 with:

```bash
python3 secure_app.py --original users_sample.json --tampered users_tampered_sample.json --outdir test_run
```

- Validation: valid input accepted, empty username, bad email
  and weak password all rejected with reasons.
- Injection/XSS: both attack strings returned no rows, the table
  kept its 1 row, and the script tag was escaped.
- Hashing: bcrypt was not installed in this environment, so the
  PBKDF2 fallback ran. Correct password checked out (`True`),
  wrong password did not (`False`), and hashing the same
  password twice gave different results (fresh salt).
- Integrity on read-back: alice, bob and carol all **PASS**.
- Deliberately altered secure copy: only alice **FAIL**,
  bob and carol still **PASS**.
- Tampered file check: **FAIL — TAMPERED: bob, differing
  field(s): password**. Only bob, only the password field,
  and no password value was printed.
- Running with no arguments also works: it picks up
  `users.json` / `users_tampered.json` if present, otherwise
  the sample files, and gives the same result.

### Challenges

- **Keeping it short.** The first version of this script was
  much longer, with separate demo modes. It was trimmed to
  about 250 lines so it stays readable and plausible as a
  small personal project — one file, one clear flow, no
  extra modes.
- **Cleaning it for GitHub.** The original version had
  hard-coded local download paths and references to where
  the data came from. Those were removed: the script now
  defaults to `users.json` / `users_tampered.json` in the
  current folder, or to the sample files if those are not
  there, so anyone cloning the repo can run it straight away.
- **Fake data that is clearly fake.** The sample files needed
  to look like real user data in format, but be obviously
  unusable as real passwords. The sample passwords are
  placeholder values like `ExamplePass1!`, and the tampered
  file changes only bob's password, so the expected test
  result is a single, unambiguous line.
- **Reporting tampering without leaking secrets.** The easy
  version of the comparison prints the two values that
  differ. That would print passwords into the terminal and
  any log. The comparison was written to report field names
  only, which is a small detail but the right habit.
- **bcrypt not being installed.** The test environment had no
  bcrypt, so the fallback path is the one that was actually
  exercised. The code handles both, and the README explains
  both, rather than assuming one is always there.
