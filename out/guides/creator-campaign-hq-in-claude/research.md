# Research notes: creator-campaign-hq-in-claude (checked 2026-10-08)

## Claude Projects (support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects)
- Projects: left sidebar / claude.ai/projects. "+ New Project" upper right. Name + description (Claude cannot see them).
- "Set project instructions" -> write -> "Save instructions". Applies to every chat in the project.
- Knowledge area on right of the project page; "+" uploads docs, text files, code snippets.
- Context does NOT carry between project chats unless in project knowledge.
- Free: up to five projects. No limit stated for paid.
- Paid plans: RAG mode auto when knowledge nears context window (article 11473015: Pro/Max/Team/Enterprise, up to 10x more content, automatic, indicator shown; tips: clear descriptive filenames, group related docs, name specific docs in questions).
- Sharing: Team/Enterprise only ("Share project"; Can view / Can edit). Team/Enterprise creation: "Keep it private" or "Share with your broader organization".
- Project memory: each project has own memory, separate from other projects and non-project chats. On by default Free/Pro/Max. Turn off per chat via "+" menu before first message.
- Archive: "..." upper right.

## File limits (support.claude.com/en/articles/8241126-uploading-files-to-claude)
- Chat: 500MB per file, 20 files per chat. Images up to 8000x8000. PDFs up to 1000 pages.
- Project files: 30MB per file; no fixed count but total must fit context window; text extraction only (except multimodal PDFs).
- Types: PDF, DOCX, CSV, TXT, HTML, ODT, RTF, EPUB, JSON, XLSX (+ JPEG, PNG, GIF, WebP). XLSX requires code execution and file creation enabled.
- PDFs <=100 pages: text + visuals (charts). 101-1000 pages: text only.
- Tips: split large docs; refer to PDF pages by viewer page numbers.

## Connectors (support.claude.com/en/articles/11176164)
- Add: Customize > Connectors, "+" ; or in chat "+" > Connectors > Manage connectors. Click connector > Connect, authenticate.
- Web connectors on all plans incl Free; mobile installs beta. Custom remote MCP: Free limited to one.
- Team/Enterprise: owner must enable under Organization settings > Connectors; members authenticate individually. Tool permissions: Always allow / Needs approval / Blocked (owner-set).
- Connectors can modify data. Only connect services you trust and need. Disconnect: Customize > Connectors > select > disconnect.
- Team/Enterprise: connectors work only in private projects; chats with synced content can't be shared.

## Google Workspace connectors (support.claude.com/en/articles/10166901)
- Gmail: search/read email, draft emails, manage labels/threads, list drafts, attachment metadata (not attachment content). Send/reply/forward need approval by default each time.
- Drive: search/retrieve Docs, read Sheets, Slides, PDFs, images, MS Office; text only extracted; embedded images not processed. Sharing/moving/trashing need approval by default.
- Drive files in Projects: yes, private projects only, via "Drive" under Files; Google Docs sync from Drive; disabled for shared projects.
- "We do not train our models on your Gmail, Drive, or Calendar connector data." (consumer users who opted in to training may have copied connector content used - see article).
- Disconnect: Customize > Connectors > Google connector > Disconnect.
- Sheets live edit is a separate beta connector. Not relied on in guide.

## Skills (support.claude.com/en/articles/12512198 and 12512180)
- Free/Pro/Max/Team/Enterprise; requires code execution enabled. Customize > Skills (claude.ai/customize/skills) > "Add"/"+" ; upload ZIP whose root is the skill folder; folder name must match skill name.
- SKILL.md frontmatter: name (<=64 chars), description (<=200 chars; Claude uses it to decide when to invoke). Body loaded only when needed. Optional REFERENCE files.
- Custom skills private to your account; Team/Enterprise owners can provision org-wide.
- Don't hardcode API keys/passwords; review downloaded skills.
- Existing guide: #read-claude-skill-for-repeat-task (do not duplicate).

## Memory (support.claude.com/en/articles/11817273)
- Settings > Memory: view/edit/delete topics. Toggle "Generate memory from chats". Reset memory deletes all incl project memory.
- Incognito (ghost icon) not saved. Sensitive topics (health, religion, politics, gender identity) not stored by default; "Include sensitive topics in memory" toggle. Govt ID numbers, financial account numbers never saved.

## Privacy: model improvement (privacy.claude.com/en/articles/12109829) - see fetch notes below.

## Ad disclosure (regulator pages seen in search results; direct fetch of asa.org.uk and commission.europa.eu failed with DNS error from the sandbox)
- ASA/CAP "Influencers' guide to making clear that ads are ads" https://www.asa.org.uk/advice-online/influencers-guide.html : third edition 23 March 2023; core test: "Consumers should be able to recognise that something is an ad, without having to click or otherwise interact with it." Prominent label such as #Ad is minimum; avoid vague "Supported by", "In association with", "#aff", "#sp". Brands share responsibility; making approved labels a contract obligation and monitoring posts are practical steps. ASA says updating for DMCCA 2024.
- EU Influencer Legal Hub https://commission.europa.eu/live-work-travel-eu/consumer-rights-and-complaints/influencer-legal-hub_en : launched Oct 2023; videos, legal briefs; paid creators count as traders and must disclose ads transparently; not exhaustive, not legal advice. Free products/services count as benefit (Legal brief 6).
- Existing site guide covers the detail: #read-ad-labels-in-europe. In HQ guide only say "check against the rules that apply in each market; the model is a second pair of eyes, not a lawyer".

## Not verified / avoid
- No specific model names, prices, or per-plan Project counts beyond Free = 5.
- No claims about Claude reading platform analytics directly; creators' stats come from exports.
