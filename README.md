# Secure Data Storage in Python

Store user accounts the safe way: check the input, hash the password,
and give every record its own integrity hash so you can tell later
whether anyone changed the file.

This is a small, single-file project. It reads a list of users from a
JSON file, converts it into a secure form, checks that secure form
when it is read back, and compares a second file against the original
to find tampering. It prints every step as it goes, so you can follow
along and see what is happening.

No real user data is in this repo. The sample files contain three
made-up users — alice, bob and carol — with clearly fake passwords
like `ExamplePass1!`. Never put real passwords in a repo.

---

## What the project does

In one run, `secure_app.py` does all of this:

1. **Validates user input.** A username must be 3–30 characters
   (letters, digits, `_`, `.` or `-`). An email must look like
   `name@example.com`. A password must be at least 8 characters and
   contain an uppercase letter, a lowercase letter, a digit and a
   special character. Characters like `<`, `>` and quotes are rejected.
   Good input is accepted, bad input is rejected with a reason.
2. **Shows SQL injection and XSS being stopped.** A classic attack
   string such as `' OR '1'='1` is passed to a database query as a
   parameter, never glued into the SQL text, so the database treats it
   as plain data and returns no rows. A script tag is escaped with
   `html.escape()` so a browser would show it as text, not run it.
3. **Hashes passwords.** Passwords are never stored in plain text.
   They are turned into a one-way hash with a fresh random salt
   (see "Hashing vs encryption" below).
4. **Stores a new user securely.** The stored record has four fields:
   `username`, `email`, `password_hash` and `integrity`. There is no
   `password` field at all.
5. **Gives every record an integrity hash.** A SHA-256 hash is made
   from the username, email and password hash of each record and
   stored next to it.
6. **Verifies integrity when reading back.** The file is read again,
   the hash is recalculated for every record, and each record is
   reported as PASS or FAIL.
7. **Proves tampering is caught.** A copy of the secure file is made
   with one record changed on purpose, and that record — and only that
   record — fails the check.
8. **Compares the tampered sample file with the original.** The
   supplied tampered file has no integrity hashes in it, so it is
   compared field by field. The report names the username and the
   field that changed — `bob` / `password` — and never prints any
   password value.

---

## Why plain-text passwords are dangerous

Imagine a website stores passwords exactly as users type them:

```json
{"username": "alice", "email": "alice@example.com", "password": "ExamplePass1!"}
```

If that file or database is ever leaked, stolen, copied by mistake,
or seen by someone who should not have access, every password is
immediately usable. The attacker does not need to crack anything —
they just log in as alice, as bob, as everyone.

It gets worse, because people reuse passwords. A password leaked
from one small site is often tried on email, banking and social
media accounts too. One plain-text leak can unlock many accounts
for the same person.

That is why the first rule of storing passwords is simple:

> **Never store a password. Store a hash of the password instead.**

---

## Hashing vs encryption

These two words sound similar, but they do opposite jobs.

| | Hashing | Encryption |
|---|---|---|
| **Purpose** | Prove you know the secret, without storing it | Hide data so only someone with the key can read it |
| **Reversible?** | No — one-way only | Yes — decrypt with the key |
| **Used for** | Passwords | Messages, files, disks, network traffic |
| **If the key/hash leaks** | Attacker still has to guess the password, one guess at a time | Attacker can decrypt everything |

**Encryption** scrambles data with a key, and the same key unscrambles
it. That is perfect for a message you need to read again later, but
terrible for a password: anyone who gets the key gets every password.

**Hashing** runs data through a one-way function. You can turn a
password into a hash, but you cannot turn the hash back into the
password. To check a login, you hash the password the user just
typed and compare it with the stored hash. If the two hashes match,
the password was right — and the real password was never stored
or printed anywhere.

A hash is not magic, though. Two problems need fixing:

- **Same password, same hash.** If two users both pick
  `ExamplePass1!`, their hashes would be identical, and an attacker
  could tell they share a password. Worse, attackers pre-compute
  hashes for millions of common passwords (a "rainbow table") and
  just look the hash up.
- **Hashes are fast.** A computer can try billions of guesses per
  second against a fast hash like plain SHA-256.

Both problems are fixed by **salt** and **slow hashing**, explained next.

---

## Salt

A **salt** is a random string, different for every user and every
password, mixed in with the password before hashing.

```
hash = slow_hash(password + salt)
stored = salt + hash
```

Because the salt is random, the same password hashed twice gives
two completely different results. In this project you can see it
in the output:

```
Same password hashed twice differs (fresh salt): True
```

That kills rainbow tables: an attacker would have to build a new
table for every single salt, which is not practical. The salt is
stored next to the hash — that is fine, because the salt is not
secret. Its only job is to make each hash unique.

---

## bcrypt and PBKDF2

A password hash also needs to be **slow on purpose**. If checking
one guess takes a fraction of a second, trying a million passwords
takes days instead of seconds.

This project tries bcrypt first, and falls back to PBKDF2 if
bcrypt is not installed:

- **bcrypt** — the standard choice for password hashing. It builds
  in its own salt and a cost factor that makes it slow. Install it
  with `pip install bcrypt` if you want to use it.
- **PBKDF2-HMAC-SHA256** — a fallback using only Python's standard
  library, so the script still works with no extra installs. It
  runs SHA-256 **200,000 times** with a random 16-byte salt. The
  stored value looks like this:

  ```
  pbkdf2_sha256$200000$<salt in hex>$<hash in hex>
  ```

  The `200000` is the iteration count, so anyone reading the stored
  value knows exactly how it was made.

Both methods store the salt and the settings with the hash, so
`check_password()` can re-run the same process on a login attempt
and compare the results safely with `hmac.compare_digest()`
(a comparison that takes the same time whether it matches or not,
so timing cannot leak information).

To check a password, the code never decrypts anything — there is
nothing to decrypt. It hashes the attempt and compares hashes:

```
typed password  ->  hash with stored salt  ->  equals stored hash?
```

---

## Integrity hashes

Hashing protects passwords. **Integrity hashes** protect the whole
record: they tell you whether the file was changed after it was
written.

For each user, the project builds one string from the record's
contents and hashes it with SHA-256:

```
integrity = SHA-256(username + email + password_hash)
```

That 64-character hex string is stored in the record as the
`integrity` field. A record in `test_run/users_secure.json` looks
like this (hash shortened here):

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password_hash": "pbkdf2_sha256$200000$...",
  "integrity": "a1b2c3d4..."
}
```

When the file is read back, the hash is calculated again from the
fields as they are now. If even one letter changed — in the email,
in the password hash, anywhere — the new hash will be completely
different, and the record fails:

```
alice: PASS
bob:   PASS
carol: PASS
```

Change one character and the check catches it. That is the point:
a hash is a fingerprint. You do not need to keep a second copy of
the data to know it changed; you just need the fingerprint.

---

## How tamper detection works

There are two different checks in this project, because the two
files being checked are different:

### 1. Records that have an integrity hash

This is the strong check. The secure file (`users_secure.json`)
contains an `integrity` field per record. On read-back, each
record's hash is recalculated and compared:

- hash matches → **PASS**, the record is untouched.
- hash differs → **FAIL**, something changed.

The project also demonstrates this by changing alice's
`password_hash` in a copy and re-checking: only alice fails,
bob and carol still pass.

### 2. A file with no integrity hashes

The supplied tampered file (`users_tampered_sample.json`) is a
plain list of users with plain-text passwords — it has no integrity
field at all, so the hash check cannot be used. Instead, the
project compares it with the original file field by field.

The important design choice: **the report names the username and
the field that changed, and never prints a value.**

```
Result: FAIL - tampered record(s) found:
  TAMPERED: bob - differing field(s): password
```

Only bob's password differs between the two sample files — alice
and carol are identical — so only bob is reported. Printing values
would leak passwords into logs and screenshots, so the code
deliberately reports field *names* only. That is a habit worth
keeping in any real system: logs should say *what* changed,
never *what the secret was*.

---

## How to run it

### Requirements

- Python 3.8 or newer. No other software is needed.
- Optional: `pip install bcrypt` — if bcrypt is installed the
  project uses it; if not, it uses the PBKDF2 fallback from the
  standard library and says so in the output.

### Step by step

```bash
# 1. Get the code
git clone https://github.com/aryangyro/secure-data-storage-python.git
cd secure-data-storage-python

# 2. (Optional) use bcrypt instead of the fallback
pip install bcrypt

# 3. Run it with the sample files
python3 secure_app.py --original users_sample.json --tampered users_tampered_sample.json --outdir test_run
```

That is it. There is nothing to configure and no database to set
up — the script uses plain JSON files and an in-memory SQLite
database for the injection demo.

### Your own files

You can point the script at your own files instead of the samples.
They must be JSON lists of users with `username`, `email` and
`password` fields, like the samples:

```bash
python3 secure_app.py --original users.json --tampered users_tampered.json --outdir test_run
```

If you run it with no arguments at all, it looks for `users.json`
and `users_tampered.json` in the current folder, and falls back to
the sample files if those are not there:

```bash
python3 secure_app.py
```

---

## Expected output

Running with the sample files prints eight sections. The key
results to look for are:

```
Secure User Input: validation
Valid input: testuser / testuser@example.com -> ACCEPTED
Invalid - empty username: REJECTED [...]
Invalid - bad email: REJECTED [...]
Invalid - weak password: REJECTED [...]
```

```
SQL injection / XSS prevention
Attack input "' OR '1'='1" -> rows: [] (treated as data)
Attack input "alice'; DROP TABLE users; --" -> rows: [] (treated as data)
Table still has 1 row(s).
XSS input '<script>alert(1)</script>' -> escaped: '&lt;script&gt;alert(1)&lt;/script&gt;'
```

```
Password hashing
Method: PBKDF2-HMAC-SHA256, 200,000 iterations, 16-byte salt
(bcrypt not installed, so this stdlib fallback is used)
Correct password checks out: True
Wrong password checks out: False
Same password hashed twice differs (fresh salt): True
```

If bcrypt is installed, the method line says `Method: bcrypt`
instead.

```
Secure Data Storage: storing a new user
Stored to test_run/users_new.json
Fields stored: ['email', 'integrity', 'password_hash', 'username']
Plaintext 'password' key present: False
```

```
Verify integrity when reading back
  alice: PASS
  bob: PASS
  carol: PASS
Overall: PASS - all records intact
```

```
Detecting modifications in a secure copy
  alice: FAIL
  bob: PASS
  carol: PASS
```

This is the deliberate change: alice's password hash was altered
in the copy, so only alice fails.

```
Verify the tampered file against the original
Original: 3 records, checked file: 3 records
Result: FAIL - tampered record(s) found:
  TAMPERED: bob - differing field(s): password
```

Only bob's password differs between the two sample files, so
only bob is named — and no password value is printed anywhere.

The run finishes with a short summary and the output folder:

```
Final verification summary
Valid input accepted, bad/injection input rejected,
passwords hashed, secure storage verified on read-back,
and tampering in the checked file detected.
Files written to: test_run
```

### Files created in `test_run/`

| File | What it is |
|---|---|
| `users_new.json` | One new user stored in secure form |
| `users_secure.json` | All 3 sample users converted to secure form |
| `users_secure_altered.json` | The secure file with alice's password hash changed, to prove the check works |

---

## File list

| File | What it is |
|---|---|
| `secure_app.py` | The whole project — one file, about 250 lines |
| `users_sample.json` | 3 fake users: alice, bob, carol (dummy passwords) |
| `users_tampered_sample.json` | The same 3 users, with only bob's password changed |
| `README.md` | This file |
| `WORKLOG.md` | What was built and what was hard about it |
| `.gitignore` | Keeps generated output and real user files out of the repo |

The sample data is deliberately small — three users is enough to
show the idea, and small enough to read at a glance. The
tampered file differs from the original in exactly one place,
so the expected result is unambiguous.

---

## Glossary

- **Plain text** — data stored exactly as typed, readable by anyone
  who sees the file. Passwords must never be stored this way.
- **Hash** — the output of a one-way function. Easy to compute,
  practically impossible to reverse.
- **Salt** — a random value mixed in before hashing, different for
  every password, so identical passwords get different hashes.
- **bcrypt** — a password-hashing algorithm with a built-in salt
  and a cost factor that makes it deliberately slow.
- **PBKDF2** — Password-Based Key Derivation Function 2. A standard
  way to make a fast hash slow by repeating it many times
  (200,000 times here).
- **Iteration count** — how many times the hash function is repeated.
  More iterations = slower to guess, slower to check.
- **Integrity hash** — a hash of a whole record, stored with it,
  so any later change can be detected by recalculating it.
- **SHA-256** — a widely used hash function that produces a
  64-character fingerprint of any input.
- **SQL injection** — an attack where input is smuggled into a
  database query to change what the query does. Stopped here by
  passing input as a parameter (`?`) instead of building it into
  the SQL string.
- **XSS (cross-site scripting)** — an attack where input containing
  a `<script>` tag is shown to another user and runs in their
  browser. Stopped here by escaping `<`, `>` and `&` with
  `html.escape()`.
- **Parameterised query** — a database query with placeholders
  (`?`) for values. The database treats the values as data only,
  never as code.
- **Tamper detection** — noticing that stored data was changed,
  by comparing it against a hash or an original copy.

---

## Limitations — read this before using it for real

This is a learning project, not production security code:

- **JSON files are not a database.** Anyone who can read the file
  can read the hashes. Real systems store hashes in a database
  with proper access control.
- **The integrity hash has no secret key.** Anyone who can edit
  the file can also recalculate the hash after changing a record,
  so this detects accidental changes and simple tampering, not a
  skilled attacker. A real system would use an HMAC with a secret
  key kept separate from the data.
- **No login system.** The script hashes and checks passwords, but
  there is no web server, no sessions, and no rate limiting.
  A real login needs lockouts after failed attempts, password
  reset flows, and more.
- **The sample passwords are fake.** `ExamplePass1!` and friends
  are placeholders so the file format is clear. Never use them
  as real passwords.
- **PBKDF2 at 200,000 iterations is a reasonable fallback, but
  bcrypt (or Argon2) is the better default** when you can install
  it — that is why the code tries bcrypt first.
