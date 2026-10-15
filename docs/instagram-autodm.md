# Instagram comment-to-DM: setup (free, replaces ManyChat)

Someone comments a keyword (CITED, EDIT, ...) on Vish's post or Reel, and within seconds they get one private DM
with the free guide, plus a short public reply ("Sent! Check your DMs"). Built 15 Oct 2026.

- Code: `buildwithvish` repo: `lib/ig-autodm/core.mjs` + `functions/api/ig-webhook.js` (runs free on Cloudflare Pages Functions since 15 Oct; Netlify ran out of credits).
- Keywords and guide links: `lib/ig-autodm/config.json` (url `null` = guide not written yet, comment skipped).
- Webhook URL: `https://buildwithvvish.com/api/ig-webhook`
- Privacy policy: `https://buildwithvvish.com/privacy.html` · Data deletion: `https://buildwithvvish.com/data-deletion.html`
- Limits (Instagram's rules): one private reply per comment, within 7 days of the comment; up to 750 an hour.
- Only Vish's own posts. Nothing comments, likes or DMs on anyone else's posts.

## One-time setup (Vish, about 30 minutes)

1. **Instagram:** Settings > Account type and tools > switch to a Professional account (Creator). Free.
2. **Meta developer account:** go to developers.facebook.com, log in with Facebook, accept the developer terms.
3. **Create the app:** My Apps > Create app > use case "Manage messaging and content on Instagram"
   (Instagram API with Instagram Login) > name it "Build with Vish replies".
4. **Connect the account:** in the app, Instagram > API setup with Instagram login > "Generate access token" >
   log in to your Instagram > copy the long token. Also copy the **Instagram app secret** (App settings > Basic, or
   the Instagram section).
5. **Cloudflare secrets:** dash.cloudflare.com > Workers & Pages > buildwithvish > Settings > Variables and Secrets > add (type Secret):
   - `IG_ACCESS_TOKEN` = the token from step 4
   - `IG_APP_SECRET` = the Instagram app secret
   - `IG_VERIFY_TOKEN` = any made-up phrase, e.g. three random words
   Then Deployments > Retry the latest deployment. (Never paste these into a chat.)
6. **Webhook:** in the app, Instagram > Webhooks > Callback URL = the webhook URL above, Verify token = the same
   phrase as `IG_VERIFY_TOKEN` > Verify and save > subscribe to **comments**.
7. **Test:** add a second Instagram account as an Instagram tester (App roles > Roles), accept the invite on that
   account, comment "CITED" on one of your posts from it. The DM should arrive within seconds.
8. **Go live for everyone (App Review, free):** App Review > request Advanced Access for
   `instagram_business_basic`, `instagram_business_manage_comments`, `instagram_business_manage_messages`.
   Use the privacy URL above, upload a short screen recording of step 7, and explain: "When someone comments a
   keyword on my own posts, the app sends them one private reply with the free guide they asked for." Until this is
   approved, only accounts with a role on the app get DMs.

## Every 60 days
The access token lasts 60 days. Claude can refresh it (GET `graph.instagram.com/refresh_access_token`), but the
new value has to be pasted into the Cloudflare secret by Vish.

## Adding a keyword
Add a line to `lib/ig-autodm/config.json` (`"WORD": {"title": "...", "url": "/#read-<guide-slug>"}`), push the buildwithvish repo.
Messages rotate between four human-sounding versions; public replies rotate between six.
