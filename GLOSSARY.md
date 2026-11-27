# Glossary — Secure Data Storage in Python

The README already has a short glossary of the terms used most in this
project. This file adds the terms you will meet when you read further
about password storage, hashing and the attacks against them. Plain
English, one or two lines per term, in alphabetical order.

## The terms

- **Argon2** — a modern password-hashing algorithm, and the current
  recommended default in many guides (it won the Password Hashing
  Competition in 2015). Like bcrypt it is slow on purpose, but it also
  uses memory, which makes it harder to attack with specialised
  hardware. This project uses bcrypt or PBKDF2, but Argon2 is the one
  to reach for in a new project if you can install it.
- **Collision** — two different inputs producing the same hash. A good
  hash function makes collisions so unlikely that you never have to
  worry about them in practice, but the possibility is why old hash
  functions like MD5 are retired: collisions were found for MD5, so it
  can no longer be trusted for integrity.
- **Constant-time comparison** — comparing two values in a way that
  takes the same time whether they match or not. A normal `==` can leak
  information through timing: it stops at the first different character,
  so an attacker measuring response times can guess the value one
  character at a time. This project uses `hmac.compare_digest()` for
  exactly that reason.
- **Credential stuffing** — taking username and password pairs leaked
  from one site and trying them on many other sites, betting that people
  reuse passwords. It is the main reason a leak anywhere is dangerous
  everywhere, and why unique passwords matter more than clever ones.
- **Data at rest** — data sitting in storage: a file, a database, a
  backup. It needs protection even though nobody is using it right now,
  because a stolen disk or a leaked backup is just as bad as an
  intercepted message.
- **Data in transit** — data moving between systems: over a network,
  between a browser and a server. It is protected with encryption such
  as TLS, so anyone listening in the middle sees only scrambled bytes.
- **Dictionary attack** — guessing passwords from a list of likely
  ones: common passwords, words from a dictionary, names, dates. Fast
  hashing makes this cheap for an attacker, which is why passwords need
  slow hashing and salt.
- **Entropy** — a measure of how unpredictable something is. A password
  like `Tr7$kq!9z` has far more entropy than `password123`, which is
  why the first is far harder to guess. Length adds entropy faster than
  complexity does, which is why passphrases work well.
- **HMAC — Hash-based Message Authentication Code** — a hash combined
  with a secret key, so it proves both that the data is unchanged and
  that whoever made the hash knew the key. The integrity hash in this
  project has no key, so it detects accidental changes and simple
  tampering; a real system would use an HMAC with a key kept separate
  from the data.
- **Key derivation** — turning a password (or another secret) into a
  cryptographic key by running it through a slow, salted process.
  PBKDF2 is a key derivation function; bcrypt is one too. The point is
  the same: make each guess expensive.
- **Key management** — the unglamorous work of creating, storing,
  rotating and retiring keys safely. Encryption is only as strong as
  the handling of its keys: a key sitting next to the data it protects
  is barely better than no encryption at all.
- **Key stretching** — making a hash deliberately slow by repeating it
  many times, so guessing becomes expensive. PBKDF2 does this with
  200,000 iterations in this project. Same idea as a "work factor" or
  "cost factor".
- **Pepper** — a secret value, the same for every user, mixed into the
  hash alongside the per-user salt. Unlike the salt, the pepper is kept
  secret and stored separately from the database, so a stolen database
  alone is not enough to start guessing passwords.
- **Preimage** — the original input to a hash. A good hash function
  makes it practically impossible to work backwards from a hash to its
  preimage, which is what makes storing hashes safe.
- **Rainbow table** — a pre-computed list of hashes for millions of
  common passwords, used to look a hash up instead of guessing. Salts
  defeat rainbow tables: with a unique salt per user, the attacker
  would need a new table for every single account.
- **scrypt** — another slow password-hashing algorithm, like bcrypt and
  Argon2, designed to use memory as well as time so it is expensive to
  attack at scale.
- **Timing attack** — learning a secret by measuring how long a system
  takes to answer. Comparing a guessed password with `==` leaks timing
  information; constant-time comparison closes that leak.
- **Work factor / cost factor** — the setting that controls how slow a
  password hash is: the iteration count in PBKDF2, the cost in bcrypt.
  Raising it makes guessing slower and logins slightly slower too.
  It should go up over time as computers get faster.

## Terms that are easy to mix up

- **Hashing vs encryption** — hashing is one-way, for proving you know
  a secret without storing it. Encryption is reversible, for hiding
  data you need to read back. Passwords get hashed, messages get
  encrypted. Mixing them up is how plain-text passwords end up in
  databases.
- **Salt vs pepper** — a salt is random per user and stored openly with
  the hash; a pepper is the same for everyone and kept secret. Both
  make guessing harder, in different ways.
- **Integrity hash vs HMAC** — an integrity hash detects change, but
  anyone who can edit the file can recalculate it. An HMAC needs a
  secret key, so only someone with the key can produce a valid one.
