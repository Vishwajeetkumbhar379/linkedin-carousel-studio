# FreeLLMAPI vs OmniRoute: two GitHub repos that stack free AI tokens, and the honest maths

## Two repos, one promise

Free AI tokens are having a moment on GitHub. Two open-source projects keep turning up in my feed, and both make big claims at the top of their READMEs.

**FreeLLMAPI** opens with: "7.4 billion tokens per month. 34 free LLM providers. 635 free model endpoints. One OpenAI-compatible endpoint." It stacks the free tiers of many AI providers behind a single `/v1` API. A router picks an available model, falls over to the next provider when one is rate-limited, and tracks usage per key so you stay under each free cap. Version 0.8.0 landed on npm on 6 October, and the project is MIT-licensed.

**OmniRoute** headlines "~1.62B Free Tokens / Month". The core idea is the same: one local endpoint (`http://localhost:20128/v1`) that any OpenAI-compatible tool can point at, with automatic fallback when a provider says no. Version 3.8.51 shipped on npm on 30 September, also MIT.

## Why one says 7.4B and the other says 1.62B

This is the part worth reading slowly. OmniRoute's free-tier document explains that it counts each shared pool once. Its own example: Mistral's free plan is one 1B a month allowance per organisation, and listing it under five models does not make it 5B. The same document says that summing its catalogue model by model would read about 7.4B.

So OmniRoute publishes the lower, pool-deduplicated number and calls ~1.62B the documented recurring grant. A first month with one-time signup credits can reach ~2.22B, but that part does not recur.

The two headlines are not a contradiction. They are two ways of counting. Treat both as the maintainers' figures, and treat the smaller one as closer to what a single account can actually spend in a month.

## The honest catch

FreeLLMAPI's README is refreshingly direct about its limits: no frontier models, variable latency, no SLA, and the endpoint gets less capable late in the day as the best models hit their daily caps, then resets at midnight UTC. OmniRoute says its figures are re-audited every two weeks and move both ways, because providers change free tiers without much warning.

Free also has a data question. Every provider in the chain has its own terms, so check them before you send anything sensitive.

## What I'd do

- Use a router like this for drafts, research summaries, rewrites and batch jobs, where a slower or weaker model is fine.
- Keep client data, contracts and anything personal out of it.
- Start with three or four provider keys, not thirty-four. Add more once you know what you actually use.
- Keep your important workflows on a model you pay for and trust. Let free capacity take the overflow.

Getting started is short. FreeLLMAPI has a one-line installer (Docker required): `curl -fsSL https://freellmapi.co/install.sh | bash`, then open `http://localhost:3001` and add your keys on the Keys page. For OmniRoute, run `npm i -g omniroute` and point your tool at `http://localhost:20128/v1`.

My honest view: the real win isn't the giant number. It's one endpoint that keeps working when a single provider hits its limit.

## Sources

- FreeLLMAPI README: https://github.com/tashfeenahmed/freellmapi
- FreeLLMAPI release history (npm): https://registry.npmjs.org/freellmapi
- OmniRoute README: https://github.com/diegosouzapw/OmniRoute
- OmniRoute free-tier methodology (FREE_TIERS.md): https://github.com/diegosouzapw/OmniRoute/blob/HEAD/docs/reference/FREE_TIERS.md
- OmniRoute release history (npm): https://registry.npmjs.org/omniroute
