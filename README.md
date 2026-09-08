# MISMO Business Glossary

Two related things live in this repository:

- **`index.html`** — the public glossary browse page. Search, letter-grouped index,
  faceted filtering by focus area / term type / source, and a reference panel that
  explains what each classification means.
- **`console/index.html`** — the management console. An admin tool that replaces the
  current CSV-with-an-`Action`-column upload process with real validation, staged
  review, vocabulary governance, and a draft/release cycle.

This is a **standalone project**. It is not part of the MISMO Initiative Hub and does
not share that project's data or design system.

## Status

| Piece | State |
| --- | --- |
| Public page | Working, but still bound to a 25-term sample embedded in the HTML. Not yet reading `data/glossary.json`. |
| Console | Working. Carries the full 8,397-term baseline embedded in the file. |
| Data files | Extracted and validated. `data/glossary.json` holds all 8,397 terms. |
| Hosting | Not deployed. See `docs/deployment.md`. |

The next substantive work item is wiring the public page to `data/glossary.json`.
See "Known work items" below.

## Layout

```
index.html              public browse page
data/
  glossary.json         all 8,397 terms, one per line
  reference.json        focus area / term type / source descriptions
console/
  index.html            management console (self-contained, opens from file://)
docs/
  data-notes.md         data shape, known quirks, verified counts
  deployment.md         hosting plan and what AWS needs to provision
tools/
  extract-data.py       regenerates data/ from a console export
.github/workflows/
  deploy.yml            publishes on push to main
```

## Working locally

Everything is static — no build step, no dependencies.

The console opens directly from disk: double-click `console/index.html`. It embeds its
own baseline precisely so it works over `file://`, where `fetch()` is blocked.

The public page will need a local server once it reads `data/glossary.json`, for the
same reason — `fetch()` does not work from `file://`:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## Console storage — read this before moving the console anywhere

The console keeps its draft, vocabulary, staged edits and release history in
**IndexedDB, which is scoped per origin**. A draft built up at
`file:///C:/Users/you/Downloads/` will **not** appear when you open the same tool at
`http://localhost:8000/` or at a hosted URL. Different origin, empty database.

Before switching between local files, localhost and a hosted copy: use
**Download backup**, then **Restore from backup** on the other side.

## Known work items

1. **Wire the public page to `data/glossary.json`.** It currently uses a 25-term
   sample. At 8,397 terms the existing full-list `innerHTML` rebuild on every
   keystroke will stall; the list needs virtualizing or capping until the user
   searches.
2. **Permalinks are decorative.** Each expanded term displays
   `/business-glossary/<slug>`, but nothing serves those URLs. Needs either
   hash-based routing or a CloudFront Function rewriting to the single page.
3. **Decide whether the console is hosted at all.** It has no authentication and
   contains the entire glossary. See `docs/deployment.md`.
4. **`Data Governance &amp; Management CoP (DGM)`** — an HTML entity in the source
   data means this value does not match its own description. See `docs/data-notes.md`.
5. **Term Type: single-value or multi-value?** Built as pipe-delimited multi-value to
   match the other two fields, but MISMO's published Term Type page states every term
   gets one and only one. Currently no row in the data uses more than one, so a revert
   is cheap. Unresolved.
6. **AKA and Related have no column in the upload format.** They travel in the full
   export and the console backup, never in a change-set. Extending MISMO's upload
   schema to carry them is a change worth planning for.
