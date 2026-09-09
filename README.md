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
| Editing | The console reads and writes this repository. Publishing commits `data/glossary.json`; the draft saves daily to `.console/draft.json`. See `docs/console.md`. |

## Layout

```
index.html              public browse page
data/
  glossary.json         all 8,397 terms, one per line
  reference.json        focus area / term type / source descriptions
console/
  index.html            management console
docs/mockups/           layout explorations, kept for reference, not deployed
.console/
  draft.json            work in progress, saved daily by the console
docs/
  console.md            running the console, one-time setup, recovery
  data-notes.md         data shape, known quirks, verified counts
  encoding.md           damaged characters, repair rules, platform test
  deployment.md         hosting plan and what AWS needs to provision
tools/
  extract-data.py       regenerates data/ from a console export
  encoding-canary.csv   change-set for testing what the platform preserves
  check-encoding.py     checks a platform export against the canary
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

## Console storage

The console's working draft lives in **IndexedDB, scoped per origin**. A draft built up
at `file:///C:/Users/you/Downloads/` will **not** appear at `http://localhost:8000/` or
at a hosted URL — different origin, empty database.

Connecting the repository is what makes this safe: the draft is committed daily, so a
new machine or a new URL can pick it up with **Load from repository**. Before the
repository is connected, or to move an unsaved draft, use **Download backup** then
**Restore from backup**.

The console now needs to be served over HTTP rather than opened from disk, since it
reads `data/glossary.json` from the repository. It still carries an embedded baseline
as a fallback for working offline.

## Known work items

1. **27 terms carry damaged characters**, six of them in the term name. The console
   now detects and proposes a correction for every one; they still need approving,
   and the data regenerating afterwards. Before restoring any stripped symbols to
   the glossary, run the platform test in `docs/encoding.md` — the pipeline that
   caused this damage may still be causing it.
2. **`Data Governance &amp; Management CoP (DGM)`** — an HTML entity in the source
   data means this source does not match its own description, so those 11 terms
   cannot be filtered by source at all. Fix in the console, then re-export. See
   `docs/data-notes.md`.
3. **Every term shows "None recorded" for AKA and Related.** The baseline export has
   no column for them, so the fields are empty for all 8,397 terms. The relationship
   display works; there is simply nothing to display yet. Populating it is console
   work.
4. **Decide whether the console is hosted at all.** It has no authentication and
   contains the entire glossary. See `docs/deployment.md`.
5. **Term Type: single-value or multi-value?** Built as pipe-delimited multi-value to
   match the other two fields, but MISMO's published Term Type page states every term
   gets one and only one. Currently no row in the data uses more than one, so a revert
   is cheap. Unresolved.
6. **AKA and Related have no column in the upload format.** They travel in the full
   export and the console backup, never in a change-set. Extending MISMO's upload
   schema to carry them is a change worth planning for.
7. **Which names should carry a trademark symbol.** Needs the list of registered
   marks and the house rule for how often to mark them. See the scope note at the end
   of `docs/encoding.md`.
8. **Fonts load from Google Fonts.** If MISMO would rather not depend on a third-party
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
