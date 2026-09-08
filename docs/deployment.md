# Deployment

Both pages are static HTML with no server side. That keeps hosting simple and cheap:
object storage plus a CDN. No EC2, no load balancer, no database.

Two targets:

- **GitHub Pages** — live immediately, no procurement. Used for preview and stakeholder
  review while AWS is being provisioned.
- **AWS S3 + CloudFront** — the production target, on MISMO's existing AWS contract.

The same files serve both. Nothing built for Pages is wasted at cutover.

---

## What AWS needs to provision

Hand this list to whoever administers the AWS account.

### 1. S3 bucket

- Private. **Block Public Access enabled** on all four settings.
- Not the legacy "static website hosting" mode — CloudFront reads from the bucket
  directly.
- Versioning on, so a bad deploy can be rolled back.

### 2. CloudFront distribution

- Origin: the S3 bucket, via **Origin Access Control (OAC)**. This is what lets the
  bucket stay private while the site is public.
- Default root object: `index.html`.
- Redirect HTTP to HTTPS.
- Compression enabled. `data/glossary.json` is ~2.9MB raw and compresses to a fraction
  of that; this matters more than anything else for page load.

### 3. ACM certificate

- For the chosen hostname, e.g. `glossary.mismo.org`.
- **Must be issued in `us-east-1`**, regardless of which region the bucket lives in.
  CloudFront only reads certificates from that region. This is the single most common
  thing to get wrong.
- Validation is via DNS, so whoever controls the MISMO domain has to add a record.
  Start this early — it is the longest pole.

### 4. DNS

- A record (alias) for the hostname pointing at the CloudFront distribution.

### 5. Deployment identity

Preferred: an **IAM role with a GitHub OIDC trust policy**, so no long-lived access key
ever exists. Alternative: an IAM user with an access key, stored as a GitHub secret.

Either way, scope permissions to this one bucket and this one distribution:

| Action | Resource |
| --- | --- |
| `s3:PutObject`, `s3:DeleteObject` | `arn:aws:s3:::<bucket>/*` |
| `s3:ListBucket` | `arn:aws:s3:::<bucket>` |
| `cloudfront:CreateInvalidation` | the distribution ARN |

Nothing broader. No `s3:*`, no account-wide CloudFront access.

### Simpler alternative

**AWS Amplify Hosting** bundles the bucket, CDN, certificate and DNS into one setup and
connects straight to a Git repository. Less control, considerably less to configure.
Defensible if the AWS team would rather not hand-assemble the pieces above.

---

## Cache behaviour

Worth getting right up front, because it is annoying to retrofit:

- **`index.html`** — short TTL or `no-cache`. It must not be stale, or users get an old
  page pointing at data that has moved.
- **`data/*.json`** — long TTL. These change only when the glossary is republished, and
  they are the large files.
- Every deploy issues a CloudFront invalidation so a publish is visible immediately
  rather than whenever the edge cache happens to expire.

The workflow in `.github/workflows/deploy.yml` handles the invalidation.

---

## Should the console be hosted?

**This needs a decision before anything is deployed.** `console/index.html` is an
editing tool with no authentication and the entire glossary embedded in it. Anyone with
the URL gets both.

Three options:

1. **Do not host it.** Keep running it as a local file. Simplest, and it loses nothing:
   the console is deliberately built to work over `file://`. The `.github/workflows`
   config excludes it from deploys by default for this reason.
2. **Separate distribution behind authentication** — Cognito, or CloudFront signed
   cookies. Correct if more than one person needs it.
3. **Internal-only path** — an origin restricted by IP or WAF rule to MISMO's network.

Whichever is chosen, note that the console's single-user IndexedDB storage is a real
limitation independent of hosting. Edits accumulate over months with no shared state
and no record of who changed what. If more than one person will ever edit the glossary,
that needs a backend, and hosting the current console does not provide one.

---

## Cutover checklist

- [x] Public page reads `data/glossary.json` and performs acceptably at 8,397 terms
- [x] Permalinks resolve (hash-based, so no rewrite rule is needed on any host)
- [ ] Console hosting decision made and recorded here
- [ ] AWS resources provisioned; certificate validated in `us-east-1`
- [ ] Deployment role/user created and its credentials added to GitHub
- [ ] `deploy.yml` switched from the Pages job to the S3 job
- [ ] DNS cut over
- [ ] Console draft backed up **before** anyone opens a hosted copy — IndexedDB is
      per-origin and does not follow the tool to a new URL
