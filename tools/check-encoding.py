#!/usr/bin/env python3
"""Check whether the glossary platform preserved special characters.

Usage:
    python3 check-encoding.py <export-from-the-platform.csv>

Upload encoding-canary.csv to the glossary system, let it process, download the
resulting export, and point this at it. It finds the ZZTest rows and reports,
per character, whether the byte survived the round trip.

Exit status is 1 if anything was lost, so this can be wired into a check later.
"""
import csv, sys, unicodedata

# What each canary row is testing. Keyed by the tail of the term name.
EXPECT = {
    "Registered Mark":   "\u00ae",
    "Copyright Sign":    "\u00a9",
    "Trademark Sign":    "\u2122",
    "Curly Apostrophe":  "\u2019",
    "Curly Quotes":      "\u201c\u201d",
    "Em Dash":           "\u2014",
    "En Dash":           "\u2013",
    "Ellipsis":          "\u2026",
    "Accented Letters":  "\u00f1\u00ef\u00e9",
    "Ampersand":         "&",
    "Embedded Comma":    ",",
    "Embedded Quote":    '"',
}

# Symptoms of a broken pipeline, in the order we want them reported.
SYMPTOMS = [
    ("\ufffd",                      "replaced with U+FFFD (character destroyed, unrecoverable)"),
    ("\u00ef\u00bf\u00bd",          "double-encoded U+FFFD"),
    ("\u00e2\u20ac",                "mojibake: UTF-8 read as Latin-1 (recoverable)"),
    ("&amp;",                       "HTML-entity encoded"),
    ("?",                           "replaced with a literal question mark"),
]

def main(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("Term", "").startswith("ZZTest")]

    if not rows:
        print(f"No ZZTest rows found in {path}.")
        print("Was the canary uploaded, and is this the export that came back after?")
        return 2

    print(f"{len(rows)} canary row(s) found in {path}\n")
    lost = []
    for r in rows:
        label = r["Term"].replace("ZZTest ", "")
        want = EXPECT.get(label)
        got = r.get("Definition", "")
        if want is None:
            continue
        missing = [c for c in want if c not in got]
        # "&amp;" still contains "&", so presence alone does not prove the
        # ampersand survived as a literal. Treat entity encoding as a failure.
        entity = label == "Ampersand" and "&amp;" in got
        if not missing and not entity:
            print(f"  PASS  {label}")
            continue

        why = next((d for s, d in SYMPTOMS if s in got), "character is simply absent")
        if missing:
            names = ", ".join(f"U+{ord(c):04X} {unicodedata.name(c, '?')}" for c in missing)
        else:
            names = "the literal ampersand (came back HTML-encoded)"
        print(f"  FAIL  {label}")
        print(f"        lost: {names}")
        print(f"        symptom: {why}")
        print(f"        got: {got[:110]}")
        lost.append(label)

    print()
    if lost:
        print(f"{len(lost)} of {len(rows)} lost characters: {', '.join(lost)}")
        print("\nDo not re-add symbols to the glossary until this passes. Writing them")
        print("into a pipeline that destroys them produces more U+FFFD, and U+FFFD")
        print("cannot be undone — the original byte is gone.")
        return 1

    print("All characters survived. The platform handles UTF-8 correctly and")
    print("symbols can be reintroduced.")
    print("\nRemember to remove the ZZTest terms from the glossary afterwards.")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
