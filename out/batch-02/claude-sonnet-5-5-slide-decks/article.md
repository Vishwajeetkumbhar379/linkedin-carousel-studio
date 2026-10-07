# Claude Sonnet 5.5 builds decks from your own template: a 4-step workflow for marketers

## What Anthropic released

On 28 September Anthropic released **Claude Sonnet 5.5**, the second model in the Claude 5.5 family after Opus 5.5. Anthropic says it generates output 30%+ faster than Sonnet 5 and costs up to 30% less per task in its testing, at the same per-token price: $2 per million input tokens and $10 per million output tokens.

## The part marketers should notice

Anthropic describes Sonnet 5.5 as strongest at well-scoped everyday tasks and at "creating polished documents, slides, and spreadsheets". Early testers said it can follow slide templates to create decks that need minimal editing.

The most concrete example is Anthropic's own: it gave the model a public company's quarterly earnings materials, call transcripts and a slide template, and asked for a 10-slide operating review. Two experts judged the first draft ready to send as is.

That's an internal test, not an independent benchmark, so treat it as a promise to check, not a result to quote to your boss. Still, it's a clear signal that "build me a deck from my template" is becoming a normal workflow.

## The 4-step workflow

**01 · Pick Sonnet 5.5.** Anthropic says it's available on all platforms. In the Claude apps the default effort is Medium, which is fine for a first draft.

**02 · Upload two things.** Your real slide template, and your source material: the brief, the report, the data export. The template is what stops it inventing a layout.

**03 · Prompt with rules.** Something like:

> Use my template. 10 slides, one message per slide. Cite the source for every number. Flag anything you guessed.

**04 · Check every number.** Open the sources, compare, correct. The model drafts. You sign it off.

## When to use Opus instead

Anthropic's developer guide is direct about this: Sonnet 5.5 fits best when the task has a clear spec and a way to check the result, and for the hardest long-horizon work an Opus model is the better choice. A deck built from clear inputs suits Sonnet. A strategy that needs judgement across messy, conflicting inputs may be better on Opus 5.5.

## What I'd do

I'd start with the deck I build most often, like a monthly campaign review, and run Sonnet 5.5 alongside my usual process for one cycle. I'd track two things: time to a first draft, and how many corrections I make before it's sendable. If the corrections stay high, I'd look at my inputs first. A vague brief makes a vague deck, whichever model you use.

And I'd never let a number go out that I haven't traced back to its source.

## Sources

- Anthropic, Introducing Claude Sonnet 5.5 (28 Sep 2026): https://www.anthropic.com/claude-sonnet-5-5
- Anthropic developer guide, Building with Claude Sonnet 5.5 (28 Sep 2026): https://claude.dev/blog/building-with-claude-sonnet-5-5/
