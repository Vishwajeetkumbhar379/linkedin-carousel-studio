# One-time setup: Meta, YouTube, TikTok (Vish, about 45 min in total)

**Never paste a key in the chat.** Every key goes into the Claude environment settings: the cloud environment menu in the session's title bar, then Edit. Save each one under Network secrets (labelled API credentials in older versions of the app), or as an environment variable, with exactly the name given below. A new session picks them up.

## 1. Meta: auto-DM and Instagram + Facebook posting (30 min)
Follow `docs/instagram-autodm.md` steps 2 to 9, with these additions:
- **In App Review (step 9), also request:**
  - `instagram_business_content_publish`, which posts reels and Trial Reels.
  - For Facebook Reels: add the "Facebook Login for Business" use case with `pages_manage_posts` and `pages_read_engagement`. This needs a Facebook Page linked to @buildwith.vish.
- **Secrets in Cloudflare** (Workers & Pages > buildwithvish > Settings > Variables and Secrets):
  - `IG_ACCESS_TOKEN`
  - `IG_APP_SECRET`
  - `IG_VERIFY_TOKEN`
  - `STATS_TOKEN`
- **Also add `IG_ACCESS_TOKEN` to the Claude environment** under the same name, for posting.

## 2. YouTube Shorts (10 min)
1. Go to console.cloud.google.com and create a new project, "Build with Vish publisher".
2. Under APIs & Services > Library, enable **YouTube Data API v3**.
3. Set up the OAuth consent screen:
   1. Choose External, then fill in the app name and your email.
   2. Add your YouTube Google account as a test user.
   3. Click **Publish app** (In production). You'll see an "unverified app" warning when you sign in; that's fine for your own account. Without this step, the login expires every 7 days.
4. Under Credentials, choose Create OAuth client ID with type **TVs and Limited Input devices**.
5. Add these secrets to the Claude environment:
   - `YT_CLIENT_ID`
   - `YT_CLIENT_SECRET`
6. Tell Claude "YouTube done". You'll get a short code to approve at google.com/device. Claude stores the resulting login straight into Cloudflare, so you never see it.

## 3. TikTok (10 min, then TikTok reviews the app)
1. Go to developers.tiktok.com, log in with your TikTok account, and create an app called "Build with Vish publisher".
2. Add the products **Login Kit** and **Content Posting API**.
3. App details:
   - Privacy URL: https://buildwithvvish.com/privacy.html
   - Terms URL: https://buildwithvvish.com/terms.html (Claude adds this page).
   - Website: https://buildwithvvish.com. If TikTok asks for a verification file, send it to Claude and it goes on the site.
4. Add these secrets to the Claude environment:
   - `TIKTOK_CLIENT_KEY`
   - `TIKTOK_CLIENT_SECRET`
5. Submit the app for review. Until it's approved, TikTok only allows private posts or drafts, so you make them public with one tap in the app.

## LinkedIn
Already covered through Typefully. Nothing to do.
