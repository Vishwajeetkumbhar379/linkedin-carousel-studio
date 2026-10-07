Two GitHub repos promise billions of free AI tokens.

I read both READMEs this week.

→ FreeLLMAPI: "7.4 billion tokens per month. 34 free LLM providers." One OpenAI-compatible endpoint that switches provider when one hits a rate limit.
→ OmniRoute: "~1.62B free tokens / month." Same idea, plus a long write-up on how they count.

Why the gap? OmniRoute counts each shared pool once. Its own docs say that adding up its catalogue model by model would read about 7.4B. But one Mistral allowance listed under five models is still one allowance.

Both numbers are the maintainers' figures, not mine.

The honest catch, straight from FreeLLMAPI's README: no frontier models, no SLA, and quality dips late in the day as top models hit their daily caps.

How I'd use it: drafts, research summaries, rewrites, batch jobs. Not client data, and not anything that has to work at 9am on launch day.

Would you run your first drafts through free models?
