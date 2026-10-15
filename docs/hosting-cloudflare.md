# Moving buildwithvish to Cloudflare Workers (free)

Why: Netlify's free plan ran out of credits on 15 Oct 2026 (every production deploy costs 15 of the 300 monthly credits,
shared by 5 projects). Cloudflare is free with no per-deploy cost, and static pages are served free and unmetered. Your
domain buildwithvvish.com already uses Cloudflare DNS, so this is the same Cloudflare account.

Cloudflare's dashboard now creates a Worker (with static assets) when you import a repo, so the site runs as a Worker,
not a Pages project (changed 15 Oct, same day). Only `/api/*` runs code; every page is a static asset.

What's already done in the `buildwithvish` repo: `wrangler.toml` (Worker `buildwithvish`, assets from `site/`, only
`/api/*` runs the Worker), `worker/index.js` (routes `/api/newsletter`, `/api/partner`, `/api/ig-webhook` to the handlers
in `functions/api/`), the site's forms post to `/api/...`, every link uses https://buildwithvvish.com. Tested locally
with `wrangler dev` (pages, deep links, security headers, webhook handshake and signature check, form validation).

## Your steps (about 15 minutes)
1. **Create the Worker.** dash.cloudflare.com > Workers & Pages > Create > Import a repository > `buildwithvish`.
   Project name `buildwithvish`, build command empty, deploy command `npx wrangler deploy`, preview command as given >
   Deploy. You get a `buildwithvish.<your-subdomain>.workers.dev` address in a minute or two.
2. **Copy the newsletter secrets.** In Netlify (app.netlify.com > buildwithvish > Site configuration > Environment
   variables) reveal `MAILERLITE_API_TOKEN` and `MAILERLITE_GROUP_ID`. In Cloudflare (Workers & Pages > buildwithvish >
   Settings > Variables and Secrets > Add) add both with type **Secret** (a plain Text variable is wiped by the next
   deploy). Saving deploys them straight away.
3. **Move the domain.** Cloudflare > buildwithvvish.com > DNS > Records: delete the records that point to Netlify (the
   A records for `buildwithvvish.com`, 75.2.60.5 and 99.83.231.61, and the CNAME `www` to buildwithvish.netlify.app).
   Leave MX and TXT records alone. Then straight away: Workers & Pages > buildwithvish > Settings > Domains & Routes >
   Add > Custom domain > `buildwithvvish.com`, and again for `www.buildwithvvish.com`. The site is down for a minute in
   between; Cloudflare makes the new records and the certificate itself.
4. **www to the main domain (optional, 1 minute).** Cloudflare > buildwithvvish.com > Rules > Templates > "Redirect from
   WWW to root" > Deploy.
5. **Check.** Open https://buildwithvvish.com, open a guide, sign up to Build Notes with a test email and confirm it arrives.
6. **Stop Netlify builds.** Netlify > buildwithvish > Project configuration > Build & deploy > Stop builds. Keep the
   project until 4 Nov; then one deploy turns buildwithvish.netlify.app into a redirect to the domain.
7. **Optional, partner form to your inbox.** Cloudflare > buildwithvvish.com > Email > Email Routing > Enable, add your
   Gmail as a destination and confirm the email Cloudflare sends. Tell Claude, which then switches on the email binding
   and adds `PARTNER_TO`. Until then the form shows "Email me instead" with your address.
8. **Auto-DM.** In `docs/instagram-autodm.md` the webhook URL is https://buildwithvvish.com/api/ig-webhook and the
   Instagram secrets go into the same Variables and Secrets (type Secret).
