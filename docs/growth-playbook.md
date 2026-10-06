# Growth playbook (v0.1, 6 Oct 2026; re-research monthly)

Until Vish's own analytics exist, these are researched defaults. Every line says how sure we are.

## What LinkedIn rewards in 2026 (secondary sources, medium confidence)
- **Dwell time over reactions.** Reported as the main ranking signal since January 2026. Carousels hold attention longest (reported ~55 s vs ~15 s for text). → Carousel is the default format.
- **Document posts** show the highest engagement rate of any format in 2026 benchmarks (Dataslayer citing van der Blom and Sprout Social). Video is growing.
- **360Brew topical model:** posting consistently about one narrow topic helps distribution beyond your network. → Stay inside AI x marketing x creators.
- **External links:** posts with links in the body reportedly get ~60% less reach. Whether the first-comment workaround is also penalised is disputed between sources. → Default: no link in body, link in first comment, and test.
- **Engagement bait:** the reported March 2026 "Authenticity Update" penalises "Agree? Comment 👇"-style prompts, pods and automation. Polls are near-dead. → Questions must be genuine and easy to answer in one line.
- **First hour:** posts are tested on 2-5% of your network first. → Vish replies to every comment in the first 60 minutes.

## Posting time
- Germany (MagicPost, 68,529 German posts): no single golden hour; 7:00, 14:00 and 17:00 tie; **Wednesday** is the strongest day.
- Global (Buffer, 4.8M posts): Wednesday ~16:00 strongest.
- **Default slot: Wednesday 10:00 CET**, second slot Tuesday 14:00. Replace with Vish's own data after 4 weeks.

## Hooks
10 variants per post, scored: curiosity gap, specificity, honesty, under 12 words. Types: contrarian, specific number, "I tested X", before/after, myth-bust.

## Comments and DMs (ethical)
- One closing question people have a stake in ("Would you tell a client a draft was AI-assisted? Yes or no?").
- Resource offers only when the resource exists on Build with Vish. No fake scarcity.

## Self-improvement loop
After each post: impressions, saves, comments, reposts, profile views, DMs → `analytics/posts.csv`. After 8 posts, reweight `topics/backlog.json` scores by what correlates with saves and comments.

Sources: dataslayer.ai/blog/linkedin-algorithm-february-2026-whats-working-now · buffer.com/resources/best-time-to-post-on-linkedin · magicpost.in/blog/best-time-to-post-on-linkedin-germany (all retrieved 6 Oct 2026; vendor blogs, treat as directional).
