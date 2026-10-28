# 1. The question

## What the team actually needs to know

Not "how healthy is each account". That question has no end and no owner.

The question is: **which accounts would likely churn unless someone escalates, and why?** Everything
in this repo follows from answering that, and only that.

Three consequences:

1. **The output is a status and a reason, not a score.** A reason can be acted on ("the operations
   director said nothing is usable and the pilot ends in 46 days"). A score can only be argued with
   ("why 41 and not 55?").
2. **Red must be rare.** If a third of the accounts are red, nobody escalates any of them. When in
   doubt, yellow.
3. **No ranking, no revenue weighting.** Every red is handled the same way: someone senior gets
   involved this week. Ranking reds by contract value quietly tells the team that small accounts
   may churn.

## Who it is for

- **The person who owns customer success**: which accounts need escalation this week.
- **Account owners**: what is off on their own accounts, written about the customer, never about them.
- **Leadership**: the short list of reds and what each escalation needs.

## The four statuses

| Status | Meaning |
|---|---|
| **Red** | Would likely churn without escalation |
| **Yellow** | Something is off, not at escalation level |
| **Green** | Healthy, and we actually heard from the customer |
| **No signal** | No customer call in the window, so we cannot tell |

The fourth status is the most important design choice in the whole project. See
[05-backtesting.md](05-backtesting.md) for why.

## Scope: every installed account

Not only accounts marked "live". The accounts most at risk are often stuck between installation and
go-live, and a "live only" filter removes exactly those.

## Why not a churn probability

The natural first idea is to predict churn: fit a model on past churns, output a percentage.

You need many churned accounts to do that. A young company with a handful of churns would be fitting
a story with decimals. A weighted health score has the same problem with extra steps: the weights are
guesses, and the red threshold gets chosen afterwards to make the board look right.

Written rules are also guesses, but **anyone can read them, argue with them and change them**, and a
changelog records why each one changed. When there are enough churns to fit something, revisit this.
