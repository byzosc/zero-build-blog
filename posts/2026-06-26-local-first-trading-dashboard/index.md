---
title: "The First Feature in My Trading Dashboard Was Not a Chart. It Was a Read-Only Boundary."
date: 2026-06-26
summary: A local-first, self-hosted trading analytics dashboard that reads positions, delayed market data, macro context, and a personal rule base. It computes deterministic context and LLM prompts, but never places orders or emits trade signals.
wechat_url:
tags: [webdev, dataviz, fastapi, react, self-hosting]
lang: en
translations: [zh]
---

<!-- English is the default version. 中文原文见 index.zh.md（站内点「中文」按钮切换）。 -->

# The First Feature in My Trading Dashboard Was Not a Chart. It Was a Read-Only Boundary.

![A local-first, read-only trading analytics dashboard](cover.png)

> **Up front:** this is a software engineering post, not investment advice. The project is read-only analytics. It does not place orders, does not emit buy/sell signals, and promises nothing about returns.

## TL;DR

| Problem | My approach |
| --- | --- |
| Trading tools can overreach | No broker connection by default; read-only when connected |
| Bad data can look convincing | Distorted quotes are labeled “do not use” |
| Real-time data can cost money | UI confirmation plus server-side throttle |
| LLMs can hallucinate | They receive facts and rules, not execution authority |
| Slow gateways freeze pages | Single-flight executor, hard timeout, cached snapshot |

---

## 1. Why I wrote the boundary first

**Point:** In trading software, “cannot do dangerous things” matters more than “looks advanced.”

I wanted one screen that pulled together what I check before making a decision:

- Positions.
- Delayed quotes.
- Technical context.
- Macro background.
- News summaries.
- My own written rules.
- An LLM-ready context bundle.

But the hard constraint came first: **local-first, read-only by default.**

The dashboard may help me organize information, frame risk, and spot conflicts with my own rules. It must not place orders. That boundary has to be architecture, not marketing copy.

## 2. Wrong frame / better frame

| Wrong frame | Better frame |
| --- | --- |
| The chart is the product | The boundary and data quality are the product |
| Let the LLM recommend trades | Let the LLM read facts and rules only |
| Read-only is a promise | Read-only is enforced by code paths |
| Missing data should be mocked | Missing data should be labeled missing |
| More real-time is always better | Use paid real-time data only when explicitly needed |

## 3. Read-only by design

**Point:** The safety property is enforced in several independent places.

| Layer | Constraint |
| --- | --- |
| Default state | Home view and polling use local snapshots plus delayed/free data |
| Broker connection | Only explicit user refresh connects |
| Session config | Broker session opens with `readonly=True` |
| Code path | No order-placement call exists in the codebase |
| Degraded mode | Offline gateway re-marks old snapshots; it does not fake data |

Read-only is not a sentence in the README. It is the shape of the code.

## 4. Data honesty

**Point:** A dashboard you cannot trust at a glance is worse than no dashboard.

The app adds several reliability gates:

- Wide bid/ask spread or bid > ask: mark as distorted and tell the user not to use it.
- Implausible implied volatility: discard Greeks derived from it.
- Missing option Greeks: explain why, such as no real-time options subscription.
- Paid real-time snapshot: require UI confirmation and server-side throttling.
- Re-marked stale snapshot: label the valuation mode (`live`, `snapshot_external_mark`, `snapshot_stale`).

> I do not want a dashboard that pretends to know the market. I want one that knows when it should not be trusted.

## 5. Stack: restraint over spectacle

| Layer | Choice |
| --- | --- |
| Frontend | Vite + React + TypeScript |
| Backend | FastAPI + uvicorn |
| Visualization | Panels, tables, status bars; no heavy charting library |
| Data | Free/delayed by default; paid real-time only on demand |
| LLM | Context assembly only; no execution authority |

The lack of a charting library is intentional. This tool is for reading context before a decision, not staring at candles.

## 6. “Real-time” without WebSockets

**Point:** Not every dashboard needs socket plumbing.

The frontend uses disciplined polling:

- Frequent checks for broker connectivity and portfolio state.
- Slower refresh for macro and calendar data.
- Per-source TTLs on the backend: quotes in seconds, options in minutes, fundamentals and daily bars in hours, calendar in days.
- Parallel cross-source fetches via a thread pool.
- A global semaphore to avoid provoking 429s from free APIs.

It is not flashy. It is stable.

## 7. LLMs read facts. They do not press buttons.

**Point:** Letting an LLM participate in analysis does not mean giving it authority.

My personal rule base lives as notes. The app retrieves relevant rules and assembles them with holdings, quotes, macro context, and news.

The retrieval pipeline degrades gracefully:

```text
lexical recall -> semantic vectors -> multi-query expansion -> section expansion -> LLM rerank -> full pass
```

If an upper stage fails, it falls back to lexical search. Embeddings are cached with a content hash, so edited rules invalidate automatically.

There is also a useful escape hatch: export all rules as plain text. The rule base is small enough to paste into a long-context web LLM when needed.

## 8. Pits and fixes

| Pit | Symptom | Fix |
| --- | --- | --- |
| Half-open broker gateway froze the page | Account/portfolio call hung ~54s while holding a lock | Single-flight executor, hard timeout, cached snapshot |
| Free data source died | Page moved and gained JS anti-scraping | Migrate source and handle cookie/token handshake |
| “Stale options” was misdiagnosed | Market-closed wide spreads looked like bad data | Harden reliability checks |
| Deploy was its own boss fight | Cache, stdin, SSH command length, path conversion | Split into a runbook |

## 9. Trade-offs

- It is a single-user personal tool, not SaaS.
- CORS is pinned to localhost and it leans on a private network.
- Free data is delayed; truly real-time data costs money.
- Some third-party unofficial endpoints can change.
- There are MVP remnants in the tree.
- Again: this is read-only analytics, not an auto-trader and not advice.

## 10. Checklist

- [ ] Define what the tool must never do.
- [ ] Do not connect to high-authority systems by default.
- [ ] Require explicit confirmation for costly or risky data.
- [ ] Label bad data instead of beautifying it.
- [ ] Let LLMs read context, not execute actions.
- [ ] Put timeouts and caches around slow external dependencies.
- [ ] Treat deployment as a runbook.

## 11. Final thought

The interesting work was never about predicting markets.

It was about building a tool that is honest about data, restrained with permissions, and useful for thinking.

Those three properties matter in any dashboard.

→ **[github.com/ZerbLion/trading-pannel](https://github.com/ZerbLion/trading-pannel)**

