# Deployment

Both pages are static HTML with no server side. That keeps hosting simple and cheap:
object storage plus a CDN. No EC2, no load balancer, no database.

Two targets:

- **GitHub Pages** — live now at `mismogh.github.io/mismo-business-glossary`, and serving
  both the public page and the console. Used for review while AWS is provisioned.
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
  of that; this matters more than anything else for page load. The console file is a
  further ~2.3MB.

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

## The console is hosted too

Decided and in place. `console/index.html` ships with the site and is served at
`/console/`. Two things make that safe:

- **It has no write access of its own.** Publishing requires a GitHub access token that
  the facilitator supplies and which lives only in their browser. Without one the console
  is a read-only view of a glossary that is public anyway.
- **It never writes to AWS.** The console commits to the Git repository; the repository
  triggers the deployment. So the AWS deployment credentials are needed only by the
  automated workflow, never by a person or a browser.

That last point is worth stating plainly for a security review: **there is no path from
the console to the S3 bucket**, and no human uploads files to it.

If MISMO later wants the console URL itself restricted rather than merely unwritable,
CloudFront can require a password at the edge before serving the page. That is a small
addition once the distribution exists, and is the main capability AWS gives us that
GitHub Pages cannot.

---

---

## Cutover checklist

- [x] Public page reads `data/glossary.json` and performs acceptably at 8,397 terms
- [x] Permalinks resolve (hash-based, so no rewrite rule is needed on any host)
- [x] Console hosting decided: shipped with the site, protected by requiring a token to write
- [ ] AWS resources provisioned; certificate validated in `us-east-1`
- [ ] Deployment role/user created and its credentials added to GitHub
- [ ] `deploy.yml` switched from the Pages job to the S3 job
- [ ] DNS cut over
- [ ] Facilitator's draft saved to the repository **before** the URL changes — the
      console's working copy is per-origin and does not follow the tool to a new domain.
      Signing in at the new URL and loading the online copy restores it.
