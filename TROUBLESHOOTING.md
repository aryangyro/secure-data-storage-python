# Troubleshooting

Things that go wrong when you run this project, and what to do about
each one. Work through the list from the top — most problems are one
of the first three.

---

## 1. `ModuleNotFoundError: No module named 'bcrypt'`

**What it means:** the project tried to use bcrypt for password
hashing, but bcrypt is not installed in your Python.

**What to do:** this project has a built-in fallback, so it should
still run — it will print a note saying it is using PBKDF2 instead.
If you want bcrypt (it is the better option), install it:

```
pip install bcrypt
```

Then run the project again. If `pip` itself is not found, try
`pip3 install bcrypt`, or `python3 -m pip install bcrypt`.

## 2. `FileNotFoundError` for `users.json` or `sample_users.json`

**What it means:** you ran the script from a different folder than
the one the files live in, so Python cannot find them.

**What to do:** move into the project folder first, then run it:

```
cd secure-data-storage-python
python3 secure_app.py
```

If the file really is missing, check you downloaded the whole repo —
the sample files are `sample_users.json` and `sample_users_tampered.json`.

## 3. A record shows FAIL when you expected PASS

**What it means:** the integrity hash stored for that record does not
match the record now. Either the file was changed after it was created
(that is the tamper detection working correctly), or you edited the
secure file by hand.

**What to do:** do not edit `secure_users.json` by hand — even fixing a
typo changes the hash and the record will fail. If you need different
sample data, edit `sample_users.json` and run the program again from
scratch, so it creates a fresh secure file.

## 4. `UnicodeDecodeError` or strange characters in the output

**What it means:** a file was saved with an unusual encoding, or it
contains characters Python did not expect.

**What to do:** open the file in a plain text editor and re-save it as
UTF-8. Do not use a word processor (Word, Google Docs) to edit `.json`
or `.py` files — they add hidden formatting that breaks things. Use
Notepad, VS Code, or any code editor.

## 5. The tamper demo says "no tampering detected"

**What it means:** the tampered copy is identical to the original,
which usually means the tampered sample file was overwritten with a
fresh copy, or you are comparing a file against itself.

**What to do:** check that `sample_users_tampered.json` actually
differs from `sample_users.json` — change one character in the tampered
file (for example, one letter of a username) and run the program again.
The demo only works if the two files are genuinely different.

## 6. Tests fail with `AssertionError`

**What to do:** run the tests on their own first and read the first
failure, not the last one — later failures are often caused by the
first:

```
python3 test_secure_app.py
```

Common causes: running the tests from the wrong folder (see problem 2),
or an older copy of `secure_app.py` in the same folder shadowing the
real one. Make sure there is only one `secure_app.py` in the folder.

## 7. "Permission denied" when running the script

**What it means:** the file does not have permission to run as a
program, which is normal — Python scripts are usually run *through*
Python, not directly.

**What to do:** run it with Python in front:

```
python3 secure_app.py
```

Do not use `chmod +x` as a first step; it is not needed here.

---

## Still stuck?

Re-read the error message slowly — the first line usually names the
file and the line number where things went wrong. Then check the
`README.md` section "How to run it" and make sure you followed the
steps in order. Nine times out of ten, the problem is the wrong folder,
a missing install, or an edited file that should have been left alone.
