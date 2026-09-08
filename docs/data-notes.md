# Data notes

Everything here was verified by parsing `data/glossary.json`, not assumed. Counts are
from the 2026-09-02 baseline (`GlossaryItems_20260902100228.csv`, 8,397 terms).

## Shape

`data/glossary.json` is a single object with `meta` and `terms`. Each term:

```json
{"id":"…uuid…","term":"Escrow","definition":"…","source":"MBA Glossary",
 "termType":"Data","focusArea":"#MBAGlossary","aka":[],"related":[]}
```

The file is written **one term per line** deliberately. It is valid JSON either way,
but one-per-line means a changed definition shows up as a one-line git diff instead of
a change buried inside a single 2.9MB line.

### Field notes

- **`id`** — all 8,397 are valid, unique UUIDs. Verified: no duplicates.
- **`source`, `focusArea`, `termType`** — **pipe-delimited multi-value** strings, e.g.
  `#LDD|#Origination`. Split on `|` and trim; do not compare the raw string.
- **`aka`, `related`** — arrays of **term IDs, not names**, so renaming a term does not
  break references to it. Currently empty for every term: the baseline export has no
  column for them. The console is where they get populated.
- Links are **one-way as entered**. The reverse direction is computed for display, not
  written into the data.

## Verified counts

| | Count |
| --- | --- |
| Terms | 8,397 |
| Distinct focus areas in the data | 17 |
| Distinct term types | 9 |
| Distinct sources | 11 |
| Rows with more than one term type | 0 |
| Rows with no term type | 1 |

### Sources, by number of terms

| Source | Terms |
| --- | --- |
| MISMO Logical Data Dictionary (LDD) | 5,568 |
| MBA Glossary | 1,704 |
| LDD Document | 422 |
| MISMO Life of Loan | 292 |
| MISMO eMortgage | 124 |
| LDD Acronym | 110 |
| MISMO Governing Documents | 69 |
| Artificial Intelligence Glossary | 40 |
| LDD Attribute | 38 |
| MISMO (Non-LDD) | 34 |
| Data Governance &amp; Management CoP (DGM) | 11 |

## Known quirks

### The DGM source does not match its own description

`data/glossary.json` spells this source with an HTML entity:

```
Data Governance &amp; Management CoP (DGM)
```

`data/reference.json` uses the literal character:

```
Data Governance & Management CoP (DGM)
```

They therefore do not match, and those 11 terms will show a source with **no
description** in the reference panel once the full dataset is loaded. This is invisible
today because the 25-term sample contains none of them.

This is a data defect, not a display bug — the entity should not be in the source data.
The console's `entity` issue rule already detects and offers to fix it. Fix it there,
re-export, and regenerate. Do not paper over it by adding the entity spelling to
`reference.json`.

### `#MISMOGOV` is undocumented

Used on **58 terms**, but not listed on MISMO's published Focus Area Descriptions page.
`reference.json` marks it `__UNDOCUMENTED__` and the panel says so plainly rather than
inventing a description. Getting an official description is an open question for MISMO.

> Note: an earlier project handoff put this at 69 terms. That figure was the count for
> the **`MISMO Governing Documents` source**, which is a different field. The focus-area
> count is 58.

### `#Appraisal` is documented but unused

It appears on MISMO's published Focus Area page and in `reference.json`, but on **zero
terms** in the export. The reference panel hides zero-count entries behind the
"Show N with no matching terms" toggle, so it stays reachable without cluttering the list.

### Source name mismatch with MISMO's website

MISMO's site calls it **"MBA Business Glossary"**. The data says **"MBA Glossary"**. The
data's spelling is authoritative here; `reference.json` notes the discrepancy in the
description text.

### Focus area vs. source overlap

`#MBAGlossary` is a *focus area*. `MBA Glossary` is a *source*. Same underlying MBA
glossary, recorded in two different fields. This is correct, not a duplicate — the
public page keeps them apart with colour and column labels.

### Other defects present in the source export

Detected by the console's issue rules. Counts are from the original CSV analysis:

| Issue | Rows |
| --- | --- |
| Stray leading/trailing whitespace | 285 |
| Literal line break inside a field | 67 |
| Doubled internal spaces | 49 |
| HTML entities where a literal character was meant | 11 |
| Character-encoding corruption (UTF-8 read as Latin-1) | 1 |
| Missing term type | 1 |

The encoding corruption is in **Credit Report**, where an apostrophe arrives as `â€™`.
The console corrects it by explicit substitution rather than re-decoding the whole
string, which would corrupt correctly-encoded text elsewhere.

Note that **none of these are fixed in `data/glossary.json`** — it is a faithful
extraction of the baseline. Fixes belong in the console, which stages them for
individual approval, followed by a re-export.

## Latent synonym data

Some definitions are already synonym pointers written as prose. `Impound` is defined as
literally `See ESCROW.` Others end with `Also see MORTGAGE.` or `AKA: Tri-Merge, …`.
That is real relationship data sitting in text where nothing can query it, and it is
the argument for populating the structured `aka` field.

## Regenerating the data files

`tools/extract-data.py` rebuilds `data/` from a console export. It expects the console
HTML at `../_source/glossary-console.html` and the public page at
`../_source/glossary-public-v1.html`; adjust the paths at the top for wherever the
export actually lives.

```bash
cd tools && python3 extract-data.py
```

It prints the term count and the classification counts so the output can be checked
against the table above before committing.
