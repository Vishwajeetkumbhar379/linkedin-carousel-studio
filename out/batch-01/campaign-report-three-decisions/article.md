# Turn any campaign report into three decisions with AI

# Turn any campaign report into three decisions with AI

Most campaign reports are written to prove work was done. Thirty charts, every metric given equal weight, and a "learnings" slide at the end that nobody reaches. I've sat through plenty of these on the creator marketing side, and the meeting nearly always gets spent on slide two.

What people actually read is page one. If page one says what to do next, the report did its job. So I now use AI to turn the report into a short decision memo, with the charts moved to the appendix.

## The one rule: the sheet does the maths

Before any AI touches the report, every number is calculated in the spreadsheet: reach, engagement rate, CPM, cost per result, whatever you report on. If you need a refresher on those four, see [Creator campaign math in plain English](https://buildwithvish.netlify.app/#read-creator-campaign-math).

The AI never calculates. It only writes about numbers it's given. That removes most of the risk of an AI report quietly inventing or rounding something.

## Pass 1: The so-what pass

Paste the finished table, then:

```
Here is our calculated campaign table: [paste].
Do not recalculate or add any numbers.

Give me exactly 3 decisions for next month:
- KEEP: one thing to keep doing
- CHANGE: one thing to change
- STOP: one thing to stop

For each: the decision in one line, the number from the table that supports it, and one sentence on why.
If the data doesn't support a decision, say so instead of forcing one.
```

The last line matters. Three forced decisions are worse than two honest ones.

## Pass 2: The sceptic pass

```
Now act as a sceptical finance lead reading this.
For each decision: would you challenge it? What number or comparison would you ask for?
Be specific and brief.
```

This is the meeting before the meeting. If the AI asks "compared to what?", your boss will too. Add the benchmark, or soften the decision.

## Pass 3: The what-we-don't-know pass

```
List what this data cannot tell us.
For each gap: why it matters, and what we could measure next time to close it.
Max 4 points.
```

Typical answers: whether sales were caused by the campaign, how much reach overlapped between creators, what happened after the tracking window closed. Saying this out loud makes the report more trusted, not less. In my experience, clients relax when you name the limits before they find them.

## Put it together

Your page one now has three parts:

1. **Three decisions**, each with its evidence number
2. **What we'd challenge**, already answered
3. **What we don't know yet**, and the plan to measure it

Everything else, including every chart, goes behind it. Nothing is lost. It just stops being the report.

## What I'd do

- Build page one first next time, then decide which charts are needed to support it. You'll cut more than half.
- Save the three prompts in a Claude or ChatGPT Project, with your report template loaded, so it's one paste per campaign.
- Once it works for a few reports in a row, automate the weekly version. My setup is in [A weekly report that writes itself](https://buildwithvish.netlify.app/#read-report-that-writes-itself).
- Always check the evidence number against the sheet before sending. AI can still copy a figure from the wrong row.

## Sources

No statistics in this one. It's a workflow from my own reporting work. Related guides: [A weekly report that writes itself](https://buildwithvish.netlify.app/#read-report-that-writes-itself) and [The influencer campaign report clients actually read](https://buildwithvish.netlify.app/#read-influencer-report-template).
