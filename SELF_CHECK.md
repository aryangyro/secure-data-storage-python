# Self-Check: Secure Data Storage in Python

Five questions to test whether the ideas in this project actually stuck. Answer from memory first, then check the answer underneath.

## Question 1

Two users both pick the password `ExamplePass1!`. Without a salt, what would an attacker learn from the stored hashes — and what does the salt change?

<details>
<summary>Answer</summary>

Without a salt, both users would have the **identical hash**, so an attacker can tell at a glance that they share a password — and can pre-compute hashes for millions of common passwords once (a rainbow table) and look them all up. A salt is a random value, different for every user, mixed in before hashing, so the same password gives two completely different hashes. The salt is stored next to the hash — that is fine, because the salt is not secret. Its only job is to make each hash unique.
</details>

## Question 2

Why does this project use a *slow* hash (bcrypt, or PBKDF2 with 200,000 iterations) instead of plain SHA-256 for passwords?

<details>
<summary>Answer</summary>

Because plain SHA-256 is **fast** — a computer can try billions of guesses per second against it. A slow hash makes each guess take a fraction of a second, so trying a million passwords takes days instead of seconds. That hardly matters to one real user logging in, but it makes guessing very expensive for an attacker. Speed is good for checking files, bad for checking passwords.
</details>

## Question 3

A record's `integrity` field is a SHA-256 hash of `username + email + password_hash`. Someone changes one letter in alice's email in the file. What happens when the file is read back — and why does the check work without keeping a second copy of the data?

<details>
<summary>Answer</summary>

Alice's record **fails** and only alice fails — bob and carol still pass. The hash is recalculated from the fields as they are now, and even one changed letter produces a completely different hash, so it no longer matches the stored one. No second copy is needed: the hash is a fingerprint, and you only need the fingerprint to know something changed.
</details>

## Question 4

The tampered sample file has no integrity hashes in it at all. How does the project still catch the tampering — and why does the report name the field but never print the value?

<details>
<summary>Answer</summary>

It compares the tampered file with the original **field by field**, and reports the username and the field that changed — `bob` / `password` — without ever printing a value. Printing values would leak passwords into logs and screenshots. That is a habit worth keeping in any real system: logs should say *what* changed, never *what the secret was*.
</details>

## Question 5

An attacker changes a record in `users_secure.json` **and** recalculates its integrity hash to match. Does the check catch it? What would stop this in a real system?

<details>
<summary>Answer</summary>

No, the check does **not** catch it. The integrity hash here has no secret key, so anyone who can edit the file can also recalculate the hash after changing a record. This check catches accidental changes and simple tampering, not a skilled attacker. A real system would use an **HMAC with a secret key kept separate from the data** — then only someone with the key could produce a valid hash.
</details>

## Spot the mistake

A teammate says: "I encrypted the passwords with AES, so they are safe." What is wrong with that?

<details>
<summary>Answer</summary>

Encryption is **reversible** — anyone who gets the key gets every password. Passwords should be **hashed**, not encrypted: a one-way fingerprint you can check a login against but never reverse. Encrypting passwords is one of the classic mistakes, and it is exactly the confusion the "Hashing vs encryption" section in the README is about.
</details>

## Scoring yourself

- **5–6 right:** You understand the project, including its limits. The next step worth trying is adding an HMAC with a secret key — see the Limitations section in the README.
- **3–4 right:** Solid. Re-read the section you missed — the salt and the integrity hash are the two ideas everything else builds on.
- **0–2 right:** Run the project again (`python3 secure_app.py ...`) and watch the output section by section. Seeing alice fail the integrity check makes the idea click faster than reading about it.
