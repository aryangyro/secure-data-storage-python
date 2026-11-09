# Exercises to try — Secure Data Storage in Python

Small hands-on exercises for this project. Each one takes a few
minutes and uses only the sample files. Run the project first (see
the README) so you know what normal output looks like, then try
these.

## Exercise 1: Add a fourth user

1. Make a copy of `users_sample.json` and add a fourth user of your
   own — pick a username, an email, and a password that passes the
   rules (at least 8 characters, with upper- and lowercase letters,
   a digit, and a special character).
2. Run the script with your file as the `--original` argument.
3. Check the output: does your new user appear in
   `test_run/users_secure.json`? Does the integrity check report
   PASS for all four records?

This shows the whole pipeline working on data you made yourself,
not just the supplied samples.

## Exercise 2: Tamper with your own copy

1. Run the project once, so `test_run/users_secure.json` exists.
2. Open that file and change one small thing in **carol's** record
   — for example, change one letter of her email address. Do not
   touch the `integrity` field.
3. Run the script again and look at the verification output. Only
   carol should fail; alice and bob should still pass.
4. Now try changing the `integrity` field itself instead, and run
   it again. What happens?

The second part is worth thinking about: the check catches changes
to the data, but if someone can edit the file they can also edit
the stored hash. That is exactly the limitation the README
mentions — a real system would use an HMAC with a secret key kept
separate from the data.

## Exercise 3: Compare bcrypt with PBKDF2

1. Run the project without bcrypt installed and note the
   `password_hash` values in `test_run/users_secure.json`. They
   start with `pbkdf2_sha256$200000$`.
2. Install bcrypt (`pip install bcrypt`) and run it again.
3. Compare the new hashes with the old ones. How are they
   different? Both store the salt and the settings with the hash,
   but the formats are not the same — can you spot where the salt
   is in each one?

This is a good way to see that "hashing a password" is not one
single method: the idea is the same, but the format depends on the
algorithm.

## Exercise 4: Try to break the validation

Try each of these as a password and read the rejection reason the
script prints:

- `password` (all lowercase, no digit, no special character)
- `Pass1!` (too short)
- `Password1` (no special character)
- `PASSWORD1!` (no lowercase letter)

Then try a username with a `<` in it, and an email without an `@`.
Each rejection should come with a reason. If you were writing the
validation yourself, which rule would you add next, and why?
