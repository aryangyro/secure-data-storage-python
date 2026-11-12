# Common Mistakes in Secure Data Storage

Mistakes that show up again and again when people store user data, and
what each one costs. Each one maps to something `secure_app.py` in this
repo does on purpose.

## 1. Storing passwords in plain text

The most basic mistake, and still the most common. If the file leaks,
every password leaks with it. Hash passwords with bcrypt (or Argon2),
never store the password itself. This repo hashes with bcrypt and a
per-user salt.

## 2. Hashing without a salt

Two users with the same password get the same hash, so an attacker can
crack thousands of accounts at once with a precomputed table. A random
salt per user makes every hash unique, even for identical passwords.

## 3. Using a fast hash for passwords

MD5 and SHA-256 are built to be fast — which is exactly what you do
*not* want for passwords, because fast means an attacker can try
billions of guesses per second. Use a slow, purpose-built password hash
like bcrypt, which is deliberately expensive to compute.

## 4. No integrity check on the stored file

If nobody checks whether the file was changed, an attacker can edit a
record (say, change a role from `user` to `admin`) and nobody notices.
This repo gives every record its own SHA-256 integrity hash and checks
it on every read. A mismatch means tampering.

## 5. Validating input once and trusting it forever

Data that was valid when it was written may not be valid when it is
read back — especially if the file was edited by hand or by another
program. Re-validate on read, not just on write.

## 6. Putting real data in the repo

Sample files in a public repo get copied, forked and scraped. Never
put real usernames, emails or passwords in a repository. The sample
users here (alice, bob, carol) are made up, with clearly fake
passwords like `ExamplePass1!`.

## 7. Logging sensitive data by accident

A debug line that prints the whole user record can end up in a log
file that gets shared or stored somewhere unsafe. Log that an action
happened, not the data it involved. Never log a password, a hash, or a
full record.

## How to use this file

For each mistake, try to reproduce it in a throwaway copy of the
sample data, then run `secure_app.py` and watch how the checks catch
it. Breaking it yourself is the fastest way to remember why the check
exists.
