# Encoding

## The problem

Twenty-seven terms in the 2026-09-02 export carry damaged characters. Every one of
them was originally a curly apostrophe, a curly quote, an em dash, or a registered
mark. They arrive in three forms:

| Form | Terms | Recoverable? |
| --- | --- | --- |
| `U+FFFD` replacement character | 19 | No — the original byte is gone |
| `ï¿½` (a `U+FFFD` that was itself re-encoded and mis-read) | 7 | No |
| `â€™` (UTF-8 read as Latin-1) | 1 | Yes — the bytes are intact |

The distinction matters. `â€™` is a reversible mis-decode: the original bytes survived
and a substitution table restores them exactly. `U+FFFD` is not. The decoder met a
byte it could not interpret and threw it away. Nothing recovers it.

Six of the affected terms have the damage **in the term name**, so it is visible in the
A–Z index without expanding anything: Builder's Risk Insurance, Buyer's Market,
Engineer's Report, Finder's Fee, Sheriff's Deed, Surveyor's Certificate.

## How the console repairs it

`fixReplacementChar()` in `console/index.html`. Because the characters cannot be
recovered, everything it produces is **inference from context**, which is why each
correction is still approved individually rather than applied in bulk.

Rules, in the order they run — the order is load-bearing:

1. Normalise `ï¿½` to a single `U+FFFD`, and apply the reversible mojibake table.
2. **Whitespace on both sides → em dash.** Checked against the whole glossary: there
   are exactly four markers of this shape and all four are em dashes.
3. **`MERS` + marker → `MERS®`.** See below.
4. **Paired markers → curly quotes.**
5. **Leftover markers adjacent to a word → possessive apostrophe.**

Steps 4 and 5 cannot be swapped. A closing quote after a word ending in `s` —
`…"yes"…` — is locally identical to a plural possessive — `owners'`. Only pairing
separates them. Running possessives first turns `"yes"` into `yes'` and leaves an
orphan, which is exactly the bug this ordering was written to fix.

Anything still holding a `U+FFFD` after all five steps is reported under a separate
rule with no proposed fix. On the current data that set is empty.

### Why MERS is a registered mark and not a copyright

The term **XML** contains this sentence with the `®` intact:

> This term is also defined in the MERS® eRegistry Procedures Manual available at
> members.mersinc.org.

The term **Uniform Electronic Transaction Act. (UETA)** contains the same boilerplate
sentence with the character destroyed. Same text, one survived, one did not. That is
what identifies the character — it was not inferred from the surrounding words.

It is `U+00AE REGISTERED SIGN`, not `U+00A9 COPYRIGHT SIGN`. Different marks with
different legal meanings.

### One-off decisions

`FFFD_OVERRIDES` in the console holds decisions that no general rule covers. Currently
one: **Reinforcement Learning (RL)** had an opening quote with no closing partner
anywhere in the definition, so it was deleted rather than a closing quote invented.
Reviewed 2026-09-08.

## Before restoring symbols to the glossary

Special characters were previously stripped from definitions because the platform
could not carry them. **That platform is almost certainly what produced these 27
defects**, and the MERS pair shows it damages the same character inconsistently —
passing it through in one row and destroying it in another.

Writing symbols back into a pipeline that still breaks them manufactures new `U+FFFD`,
and `U+FFFD` cannot be undone. Test first.

The console is not the weak link. Its CSV writer and parser round-trip `®`, `©`, `™`,
curly quotes, em dashes, accented letters, embedded commas, embedded quotes and
embedded newlines with zero loss — verified in a browser against the console's own
`toCSV`/`parseCSV`.

### The test

1. Upload `tools/encoding-canary.csv` to the glossary system. It is a normal
   change-set: twelve `add` rows, each carrying one character under test, all named
   `ZZTest …` so they are easy to find and remove.
2. Let the system process it, then download the export it produces.
3. Run the checker against that export:

   ```bash
   python3 tools/check-encoding.py path/to/export-from-the-platform.csv
   ```

It reports per character whether the byte survived, and when one is lost it names the
symptom — destroyed to `U+FFFD`, mojibake, HTML-entity encoded, or turned into a
literal `?`. Exit status is 1 on any loss, so it can be wired into a check later.

4. **Delete the ZZTest terms from the glossary afterwards.**

If it passes, symbols can be reintroduced. If it fails, the fix is upstream in the
platform's encoding, not in the glossary data — and re-adding symbols before then will
only create more damage of the kind that cannot be repaired.

### Scope, once the platform passes

Which names carry a mark, and how often to mark them, is a branding and legal decision
rather than a technical one. For reference, the current data contains:

- `MISMO` — 6,582 occurrences, none carrying a symbol
- `MERS` — 66 occurrences, one carrying `®`
- `Fannie Mae` (28), `Freddie Mac` (24), `FICO` (3), `Desktop Underwriter` (1),
  `Loan Prospector` (1) — none carrying a symbol
- Copyright signs — **zero** anywhere in the glossary

Standard practice marks the first or most prominent use rather than every instance.
Marking all 6,582 occurrences of MISMO would read badly and asserts a registration
status that should come from whoever owns the marks, not from this data. Get the list
of registered names and the house rule, and it can be encoded as a console rule.
