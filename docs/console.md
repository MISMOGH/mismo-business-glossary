# Running the console

The console is the glossary's editing tool. The facilitator works entirely inside it —
open a page, make changes, publish. There is no need to visit GitHub, run any commands,
or understand version control. The repository underneath is plumbing.

## What the repository does

| File | Written when | Contains |
| --- | --- | --- |
| `data/glossary.json` | you press **Publish** | the published glossary the public site reads |
| `.console/draft.json` | every hour, automatically | the work in progress |

Committing `data/glossary.json` *is* publishing: the site rebuilds itself from that
file within a minute or two.

The draft file holds only the **difference** from the published version, not a full
copy. A full copy is about 2.9MB; the difference is usually a couple of kilobytes. That
keeps a daily commit from bloating the repository over a months-long editing cycle.

## Why the draft is saved at all

Between publishes the working draft lives in this browser's IndexedDB, on one machine.
Clearing site data, a browser reset or a dead laptop would take four months of work with
it. The daily save means the repository always holds something recent, and the history
means any earlier day can be recovered.

It happens quietly — on load if an hour has passed, and again during a long session.
**Save draft now** forces it. If more than a day goes by without a save reaching the
repository, the panel says so rather than failing silently.

## One-time setup

Do this once, on the facilitator's machine, on their behalf. They never need to see the
token or know it exists.

1. Create a fine-grained access token:
   - GitHub → Settings → Developer settings → Personal access tokens → Fine-grained
   - **Resource owner**: the account that owns the repository, not your personal account
   - **Repository access**: only `mismo-business-glossary`
   - **Repository permissions**: **Contents: read and write** — nothing else
   - **Expiration**: up to a year. Diarise the renewal; it is your job, not theirs.
2. Open the console and press **Connect…**
3. Enter the facilitator's name, the repository (`owner/repository`), the branch
   (`main`), and the token. The name is recorded on every change — the token belongs
   to the account rather than the person, so without it the history cannot tell one
   facilitator from another.
4. Press **Check and save**, then accept the offer to load from the repository.

The token is stored in this browser only and is sent nowhere except GitHub. Anyone who
can use this browser profile can publish, so treat the machine as you would one holding
any other publishing credential.

When the token expires the console says so plainly, keeps the draft safe locally, and
carries on letting them edit. Nothing is lost; it just stops saving until reconnected.

## Day-to-day

1. Open the console. It loads the draft from this browser and checks the repository in
   the background.
2. Edit. Search, bulk-tag, fix flagged issues, add or remove terms. Everything stages
   for review; nothing changes the draft until applied.
3. The draft saves itself to the repository every hour.
4. When the working group has agreed a version, press **Publish**. That commits the new
   glossary, updates the site, and downloads a change-set CSV as a record of what
   changed for the group.

## Handing over to a new facilitator

The facilitator will change over time. Nothing about the glossary is tied to an
individual, so a handover is short:

1. **Revoke the outgoing token.** GitHub → Settings → Developer settings → Fine-grained
   tokens → delete it. This takes effect immediately and everywhere, including any copy
   still sitting in the old browser. Revocation, not a password, is the real control
   here.
2. **Ask them to press Save draft now before they finish**, so nothing is stranded. The
   hourly save means at most an hour is ever at risk, but a clean final save costs
   nothing.
3. **Issue a new token** for the incoming facilitator, on the same terms: this
   repository only, Contents read and write.
4. On their machine, press **Connect…**, enter their name and the new token, then
   **Load from repository**.

They receive the published glossary and the most recent saved draft. Nothing needs to
be copied off the old laptop, and the old laptop keeps nothing usable.

Because each person enters their own name, the history shows who made which change
across the whole succession, even though every commit is authored by the same account.

## If two people ever edit

The design assumes one editor. If a second person edits in another browser, the second
publish fails rather than overwriting the first — the commit is not forced. Recovery is
to load from the repository and redo the lost edits, so avoid the situation rather than
relying on the safeguard.

## If something goes wrong

**"The access token was rejected."** It expired or was revoked. Issue a new one and
press Connect. The draft is untouched.

**A publish failed.** Nothing was written; the repository and the draft are both as
they were. Retry. If it keeps failing, the change-set CSV still downloads, so a version
can be produced by hand.

**The draft looks wrong or has been lost.** Every daily save is in the repository's
history. `.console/draft.json` at any past commit can be restored — ask whoever
administers the repository.

**Starting fresh on a new machine.** Connect, then **Load from repository**. That pulls
the published glossary plus the most recent saved draft.
