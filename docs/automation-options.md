# Publishing and automation options (checked 6 Oct 2026)

Hard rule: nothing posts, emails, DMs or deploys publicly without Vish's tap. No scrapers, no unofficial LinkedIn bots, no auto-commenting on other people's posts.

| Option | Posts PDF carousels? | Cost | Approval step | Trade-off |
|---|---|---|---|---|
| **(a) LinkedIn native scheduler** | Sources conflict; several say PDF documents can't be scheduled natively | Free | Vish schedules by hand | Fastest manual path: open the review pack on the phone, upload PDF, paste caption, post |
| **(b) Zapier "Create Share Update"** | No (text, links, images only per Zapier docs) | Free tier limited | Zapier approval paths are paid | Fine for text+image posts, not carousels |
| **(c1) Postiz (open source, self-host)** | Yes, via LinkedIn's official API | Free (self-host) or paid cloud | Drafts queue + manual "publish" | Best free fit; needs a small server (Docker) and a LinkedIn developer app |
| **(c2) Buffer** | Document posts on paid plans | Free plan: text/image | Draft + approve on paid team plans | Easiest UI; PDFs cost money |
| **(c3) Typefully** | Unclear for LinkedIn PDFs | Free tier | Drafts | Connector in claude.ai is "connect incomplete"; finish the connection to test it |
| **(d) Google Sheet or Notion approval queue** | n/a (queue, not a poster) | Free | Vish ticks "approved" | Pairs with (a) or (c1): engine fills the sheet, Vish approves, poster posts |

## Recommendation
1. **Now (zero setup):** engine builds the review pack → Gmail **draft** to Vish + Todoist task "Approve: <title>" with the PDF and caption → Vish posts with LinkedIn's app (2 minutes).
2. **Next (free, 1 hour setup):** Postiz self-hosted on a free-tier VM or Vish's laptop, with the Sheet as the queue. Engine creates Postiz drafts; Vish taps publish.
3. Skip Zapier for carousels. Use it only for the resource-delivery hand-off below.

## Comment / DM resource delivery (honest version)
- Instagram's keyword-comment gate works on Instagram. On LinkedIn, 2026 reporting says "comment X below" is treated as engagement bait. So the default CTA is a real question, and the resource sits on the Build with Vish page linked in the first comment.
- If Vish still wants a keyword offer: the resource gets a **MailerLite form** on the page (double opt-in, already wired on Build with Vish via the Netlify function). When Vish replies to a commenter, he sends the page link himself. No auto-DMs.
