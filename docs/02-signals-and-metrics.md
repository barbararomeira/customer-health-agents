# 2. Signals and metrics considered

Everything we thought about measuring, what it would tell us, where it comes from, how it misleads,
and whether the current rules use it.

**Use:** ✅ in the rules · 🟡 context only · ⏳ wanted, not available yet · ❌ considered and rejected

## From the calls (the richest source)

| Signal | What it tells you | How it misleads | Use |
|---|---|---|---|
| **Explicit churn statements** ("we won't continue", "we're looking at another vendor", "we'll pause") | The customer has already decided or is deciding | Rarely: these are said plainly when they are said. Watch for jokes and hypotheticals | ✅ red on its own |
| **"No value" statements** ("nothing usable", "duplicates what we have") | The customer can't see what they're paying for | Said in frustration on a bad day. Only red if an end date is within 90 days | ✅ |
| **Decision-maker attendance**: does the sponsor still *speak* in calls? | Disengagement at the level that decides renewal | Calendar invites list who was asked, not who came. Count speakers in the transcript | ✅ |
| **Customer's share of talking time** | Engaged customers talk, ask, push back | Demo and training calls are vendor-heavy by nature. Compare like with like | 🟡 tone marker |
| **Questions asked by the customer** | Curiosity and planning are signs of future use | Same as above | 🟡 tone marker |
| **Deferring language** ("we'll see", "after the budget review", "not a priority now") | Our topic moved down their list | Can be honest scheduling. Needs repetition | ✅ tone marker |
| **Disputes over our numbers** ("the counts are wrong again") | Trust in the data is breaking | One dispute during a fix is normal. Repeated, with no fix in sight, is not | ✅ data trust |
| **Repeated unanswered asks** | They're waiting on us, and noticing | Our backlog, not their intent. Yellow, never red | ✅ yellow |
| **Expansion talk** (new lines, new sites) | Strongest positive signal there is | Can be an individual's wish without budget | 🟡 supports green |
| **Champion or sponsor change** | The person who bought it is gone | A new person can be just as committed. Red only if nobody has taken over | ✅ |
| **Competitor or in-house mentions** | They're pricing the alternative | Sometimes negotiation theatre. Still red: it needs a senior conversation either way | ✅ |

## From the meeting pattern

| Signal | What it tells you | How it misleads | Use |
|---|---|---|---|
| **Cancelled or no-show recurring meetings** | Disengagement | **A missing recording is not a no-show.** The recorder wasn't invited, a different link was used, the meeting moved to the shop floor. Only count it when notes confirm it | ✅ when confirmed |
| **Weeks with no customer call at all** | We don't know | Read as "all fine" by default. That is the trap | ✅ → *no signal* status |
| **Customer reply latency** (email, chat) | Responsiveness | Holidays, shutdowns, time zones | ⏳ |
| **Meeting cadence changes** (weekly → monthly) | Lower priority, or a calmer phase | Often agreed and healthy. Check the reason | 🟡 |

## From the product

| Signal | What it tells you | How it misleads | Use |
|---|---|---|---|
| **Logins, active users, report opens** | Whether anyone uses it day to day | A shop-floor screen watched by 20 people is one login | ⏳ wanted |
| **Usage trend vs the account's own baseline** | Usage falling away | Seasonal shutdowns, line rebuilds | ⏳ |
| **Data-quality incidents** | Whether what we show is right | Our internal incident ≠ the customer noticing | 🟡 |
| **Time from installation to go-live** | Delivery stuck | The go-live date field is often filled in optimistically. Judge by real delivery | ✅ "stuck" (12+ weeks) |

## From the contract

| Signal | What it tells you | How it misleads | Use |
|---|---|---|---|
| **Nearest end date**: contract, renewal, **pilot/POC end**, or a named decision meeting | When the decision actually happens | Using only the renewal date. **This is the mistake that gave zero weeks of warning** in the backtest | ✅ the 90-day window |
| **Renewal date in the CRM** | — | Often empty or stale | ❌ use the account tracker instead |
| **Contract value** | — | Weighting by revenue says small accounts may churn | ❌ |
| **Support ticket volume** | Friction | High volume can mean an engaged customer | 🟡 |

## From inside the company

| Signal | Use |
|---|---|
| **Account owner's notes** (blockers, last update) | 🟡 explain gaps (was the meeting cancelled?), never the customer's voice |
| **Something the customer said off the record, relayed by a colleague** | ✅ can make yellow; can support red but **never make it alone** |
| **Internal calls about the account** | 🟡 resolve facts only ("renewal talks are ongoing") |

## What we chose not to count against an account

- Deliberate product design the customer agreed to (for example, on-premise hosting with no remote
  access). It shows up in calls as a limitation, but it isn't a failure.
- Customer-side delays (holidays, legal, their IT) are context. They still count toward "stuck" if
  they stall the account, because the risk is real whoever caused it.
- The account owner's performance. Reasons are about the customer.
