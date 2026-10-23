# Instagram comment-to-DM: setup and how it works (free, self-hosted, replaces ManyChat)

v2, 23 Oct 2026. Someone comments a keyword (EDIT, CITED...) on one of Vish's posts or Reels. Within seconds they get one private DM with a "Send me the link" button and a short public reply ("Sent! Check your DMs"). When they tap the button, they get the link to the free resource. If they follow, they also get a thank-you; if they don't, a friendly follow nudge. The link always arrives, follow or not.

- **Code:** in the `buildwithvish` repo:
  - `lib/ig-autodm/core.mjs` (logic);
  - `lib/ig-autodm/config.json` (keywords and copy);
  - `functions/api/ig-webhook.js` and `worker/index.js` (routes).
- **Tests:** `node --test lib/ig-autodm/core.test.mjs` (21 tests; Meta mocked, real SQL on SQLite).
- **Runs on:** Cloudflare Workers, free plan. Storage is Cloudflare D1, free: 100,000 row writes a day, about 10 rows per person who asks.
- **URLs:**
  - Webhook: `https://buildwithvvish.com/api/ig-webhook`
  - Tracked links: `https://buildwithvvish.com/go/<keyword>`
  - Stats: `https://buildwithvvish.com/api/autodm-stats?days=30`
- **Policies:** privacy `https://buildwithvvish.com/privacy.html`, data deletion `https://buildwithvvish.com/data-deletion.html`.
- **Scope:** Vish's own posts only. Nothing comments, likes or DMs on anyone else's posts, and no DM goes to anyone who didn't comment or message first.

## The flow, step by step
1. **Comment.** A comment with a keyword arrives through Meta's "comments" webhook. The keyword is matched as a whole word, in any case.
2. **Guards:**
   - the signature is checked (HMAC SHA-256 with the app secret);
   - Vish's own comments are skipped;
   - each comment is handled once (Meta's redeliveries are ignored);
   - each person gets each keyword once a week;
   - there's an hourly cap of 200 DMs (Meta allows about 750 an hour, as reported by tool vendors).
3. **Private Reply.** One per comment, within 7 days of it (Meta's rule). It's Meta's official Private Replies API, carrying a quick-reply button. If Meta refuses the button (a 4xx error), the plain link goes out instead, with no follow check.
4. **Public reply** under the comment, one of 6 rotating lines.
5. **The tap.** When they tap the button (or reply "link"), a "messages" webhook arrives. Messaging the account is the consent Meta requires before the app can read `is_user_follow_business`. Then:
   - followers get a thank-you plus the link;
   - non-followers get the link plus one follow nudge;
   - if the follow status is unknown, they get the plain link.
6. **Click.** `/go/<keyword>` counts the click, then redirects to the resource with `utm_source=instagram&utm_medium=dm&utm_campaign=<keyword>`. Unknown keywords go to `/resources`.
7. **Stats.** For each keyword, each day:
   - comments, dm_sent, link_sent, clicks;
   - followers, non_followers, follow_unknown;
   - duplicates, capped;
   - dm_failed, link_failed, public_failed.

   The JSON lives at `/api/autodm-stats`, behind `STATS_TOKEN`.

**Errors.** Meta is always answered with 200 (so it doesn't retry storms). Failed DMs are counted, and the person is freed so their next comment can try again. Network errors are caught. If counters fail (for example, the D1 daily limit), DMs still go out. A daily cron at 03:17 UTC deletes expired dedupe rows.

**Honest limits:**
- **Follow check:** a true follow check is only possible after the person messages the account, which is why the button exists. Tapping it is their consent.
- **Locked resources:** we never lock a free resource behind a follow. Meta's Platform Terms and Instagram's spam rules make follow-gating risky, and it annoys people.
- **The button:** quick-reply buttons don't show in every Instagram client. The DM says "No button? Just reply LINK", which works too.

## One-time setup (Vish, about 30 minutes)
1. **Instagram:** a Professional account (Creator). Done on 22 Oct.
2. **Meta developer account:** at developers.facebook.com, accept the developer terms.
3. **Create the app:**
   1. Go to My Apps > Create app.
   2. Pick the use case "Manage messaging and content on Instagram" (Instagram API with Instagram Login).
   3. Name it "Build with Vish replies".
4. **Token:**
   1. Go to Instagram > API setup with Instagram login > Generate access token.
   2. Log in as @buildwith.vish and copy the token.
   3. Also copy the Instagram app secret.
5. **Cloudflare secrets.** In dash.cloudflare.com, open Workers & Pages > buildwithvish > Settings > Variables and Secrets, and add these, each with type Secret. Never paste them in a chat.
   - `IG_ACCESS_TOKEN` (from step 4)
   - `IG_APP_SECRET` (from step 4)
   - `IG_VERIFY_TOKEN` (any made-up phrase)
   - `STATS_TOKEN` (any long random phrase, used to read the stats)
6. **Database.** Nothing to do. The first deploy after merging this branch creates the D1 database `buildwithvish-autodm` and links it (Wrangler's automatic provisioning). Check Workers & Pages > buildwithvish > Bindings: `DB` should show. The tables create themselves on the first comment.
7. **Webhook:**
   1. In the app, open Instagram > Webhooks.
   2. Set the Callback URL to the webhook URL above, and the Verify token to the same phrase as `IG_VERIFY_TOKEN`.
   3. Click Verify and save.
   4. Subscribe to **comments** and **messages**. Both are needed for the button flow.
8. **Test:**
   1. Add a second Instagram account as an Instagram tester (App roles > Roles) and accept the invite on it.
   2. From that account, comment "CITED" on one of your posts. The button DM should arrive within seconds.
   3. Tap it; the link arrives.
9. **App Review (free).** This makes it work for everyone, not only testers.
   1. Request Advanced Access for `instagram_business_basic`, `instagram_business_manage_comments` and `instagram_business_manage_messages`.
   2. Give the privacy URL and a screen recording of step 8.
   3. Explain the use: "When someone comments a keyword on my own posts, the app sends one private reply. When they tap the button, it sends the free guide they asked for and checks whether they follow so it can thank them."

   Until it's approved, only accounts with a role on the app get DMs.

## Every 60 days
The access token lasts 60 days. Claude can refresh it (GET `graph.instagram.com/refresh_access_token`), but Vish pastes the new value into the Cloudflare secret.

## Reading the stats
```
curl -H "Authorization: Bearer $STATS_TOKEN" "https://buildwithvvish.com/api/autodm-stats?days=7"
```
The `social-analytics-report` skill turns this, together with Instagram Insights, into the weekly keep / test / change / stop report.

## Adding a keyword
1. Add a line to `lib/ig-autodm/config.json`: `"WORD": {"title": "...", "url": "/resources/<slug>"}`.
2. Run the tests.
3. Push the buildwithvish branch, and merge it after Vish approves.

`url: null` means the resource isn't live yet: those comments are counted and skipped.

Button DMs rotate between 3 versions, link DMs 2 to 4, and public replies 6. Copy rules: British English, no dashes, SlopMonster clean. The config test checks for dashes and placeholders.
