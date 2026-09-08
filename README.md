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
| Public page | Reads `data/glossary.json` and renders all 8,397 terms. Search, A–Z jump, faceted filtering, shareable permalinks. |
| Console | Working. Carries the full 8,397-term baseline embedded in the file. |
| Data files | Extracted and validated. `data/glossary.json` holds all 8,397 terms. |
| Hosting | Live on GitHub Pages. AWS not yet provisioned — see `docs/deployment.md`. |

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

1. **`Data Governance &amp; Management CoP (DGM)`** — an HTML entity in the source
   data means this source does not match its own description, so those 11 terms
   cannot be filtered by source at all. Fix in the console, then re-export. See
   `docs/data-notes.md`.
2. **Every term shows "None recorded" for AKA and Related.** The baseline export has
   no column for them, so the fields are empty for all 8,397 terms. The relationship
   display works; there is simply nothing to display yet. Populating it is console
   work.
3. **Decide whether the console is hosted at all.** It has no authentication and
   contains the entire glossary. See `docs/deployment.md`.
4. **Term Type: single-value or multi-value?** Built as pipe-delimited multi-value to
   match the other two fields, but MISMO's published Term Type page states every term
   gets one and only one. Currently no row in the data uses more than one, so a revert
   is cheap. Unresolved.
5. **AKA and Related have no column in the upload format.** They travel in the full
   export and the console backup, never in a change-set. Extending MISMO's upload
   schema to carry them is a change worth planning for.
6. **Fonts load from Google Fonts.** If MISMO would rather not depend on a third-party
   CDN, self-host Libre Franklin. The page already falls back to `system-ui` if the
   request is blocked.

## How the public page handles 8,397 terms

Worth knowing before editing `index.html`, since several choices exist only because of
scale:

- **Rows render 60 at a time** as the reader scrolls. Building all 8,397 at once blocks
  the main thread long enough to be felt on every keystroke.
- **The rendered window is anchored.** Jumping to P renders 60 rows starting at P
  rather than the 5,200 that precede it, and the list says how many are above with a
  way back. Measured: an anchored jump is ~80ms; rendering through was ~1.6s.
- **Term bodies are built on first expand**, not up front — most are never opened.
- **Expanding mutates one row** instead of re-rendering the list, so scroll position
  and other open rows survive.
- **Reverse AKA/Related links are indexed once at load.** Computing them per row was
  quadratic.
- **Search is debounced 140ms.**
- **Permalinks are hashes** (`#escrow-analysis`), not paths, so the same file works on
  GitHub Pages, on S3 behind CloudFront, and from localhost with no rewrite rule
  configured anywhere. Slugs keep parenthetical text, because dropping it collided
  `Abatement (Rental)` with `Abatement (Tax)` — verified zero collisions across all
  8,397 terms.
