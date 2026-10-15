# Moving buildwithvish to Cloudflare Pages (free)

Why: Netlify's free plan ran out of credits on 15 Oct 2026 (every production deploy costs 15 of the 300 monthly credits,
shared by 5 projects). Cloudflare Pages is free with no per-deploy cost and unlimited static traffic. Your domain
buildwithvvish.com already uses Cloudflare DNS, so this is the same Cloudflare account.

What's already done in the `buildwithvish` repo: `wrangler.toml` (serves `site/`), `functions/api/newsletter.js`
(MailerLite), `functions/api/partner.js` (partner form by email), `functions/api/ig-webhook.js` (Instagram auto-DM),
the site's forms now post to `/api/...`, every link uses https://buildwithvvish.com. Tested and compiled with wrangler.

## Your steps (about 15 minutes)
1. **Create the Pages project.** dash.cloudflare.com > Workers & Pages > Create > Pages > Connect to Git > allow GitHub >
   pick `buildwithvish` > production branch `main`, framework preset None, build command empty, output directory `site` >
   Save and Deploy. You get a `buildwithvish.pages.dev` address within a minute.
2. **Copy the newsletter secrets.** In Netlify (app.netlify.com > buildwithvish > Site configuration > Environment
   variables) reveal `MAILERLITE_API_TOKEN` and `MAILERLITE_GROUP_ID`. In Cloudflare (Pages project > Settings >
   Variables and Secrets) add both as type Secret. Then Deployments > Retry deployment.
3. **Move the domain.** Pages project > Custom domains > Set up a domain > `buildwithvvish.com` > Activate. Cloudflare
   swaps the records that point to Netlify for you. Repeat for `www.buildwithvvish.com`.
4. **Check.** Open https://buildwithvvish.com, open a guide, sign up to Build Notes with a test email and confirm it arrives.
5. **Stop Netlify builds.** Netlify > buildwithvish > Project configuration > Build & deploy > Stop builds. Keep the
   project until 4 Nov; then one deploy turns buildwithvish.netlify.app into a redirect to the domain.
6. **Optional, partner form to your inbox.** Cloudflare > buildwithvvish.com > Email > Email Routing > Enable, add your
   Gmail as a destination and confirm the email Cloudflare sends. Tell Claude, which then switches on the email binding
   and adds `PARTNER_TO`. Until then the form shows "Email me instead" with your address.
7. **Auto-DM.** In `docs/instagram-autodm.md` the webhook URL is now https://buildwithvvish.com/api/ig-webhook and the
   Instagram secrets go into the same Cloudflare Variables and Secrets.
