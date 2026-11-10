# 8. Product usage in the status (v0.4)

Calls tell you what the customer *says*. Product usage tells you what they *do*. This page is how
usage enters the same red / orange / yellow / green model, without a separate usage score.

## The goal, and the trap

The goal is that customers use the product every day. The trap: some accounts get their results
pushed to them (a daily report by email, chat notifications) and have no reason to log in yet.
Counting "no logins" against them would punish exactly the accounts where the reports work.

So usage counts **in an account's favour** whenever it's there, and **against it only when it
collapses**, and only for accounts that are meant to use the product.

## What is measured

- **User-day:** one customer person who opened the product **and interacted** (a click) that day.
  The click filter matters: a shop-floor screen left open on a dashboard produces thousands of page
  views and almost no clicks. Page views made two steady accounts look like they were leaving; user-days showed
  they were not.
- **Days used:** days in the last 20 working days with at least one customer user-day.
- **Usual level:** the account's own user-days in the 8 weeks before the last 4. Never compared
  with other accounts.
- **Who is a customer:** users are mapped to accounts by email domain. Your own staff are excluded,
  including colleagues who log in with a non-company address. One domain that covers several sites
  (a country team serving two plants) is **not judged** until usage can be split by site, for example
  by the line or site id in the page address.

## Account types (read from your account tracker every run)

| Type | How you know | How usage counts |
|---|---|---|
| **Product account** | Live, and the tracker says the customer works in the product | Positive and negative (collapse) |
| **Report-first** | Live, results delivered by reports | Positive only |
| **Not live yet** | Off or partially live | Positive only. The go-live clock judges these |

## The rules

| Usage | Effect |
|---|---|
| Daily use (15+ of 20 days) or regular use (5+ of 20) | **Engagement.** Supports green (a customer call is still needed). If the team uses the product regularly, decision makers going quiet on calls is not a strong warning sign on its own |
| **Collapse:** regular use before (4+ user-days per 4 weeks), then each of the last 3 weeks at or below max(1, 10% of the usual weekly level) | **One lasting warning sign (1 point).** Alone it makes yellow; with one other lasting warning it makes red. Never red alone |
| Halved, low, or not used in 4 weeks | **Shown as a tag, no points.** The account owner can act on it |

## Why "collapse", not "drop"

We checked every churned customer that had usage history: four of them. All four looked the same.
Use didn't slowly halve; it **fell to almost nothing** before or around the churn. Several healthy
accounts, meanwhile, had weeks at half their usual level (holidays, a line rebuild, a champion on
leave). A halving rule would have flagged them; the collapse rule didn't.

Four churns is a small sample, and we did not have exact churn dates, so this tells you the pattern,
not how many weeks of warning it gives. The cut-offs (15 / 5 days, 4 user-days, 10%, 3 weeks) are a
first proposal. Re-check them against the call findings after a few weekly runs.

## In the run

1. One query per run returns user-days per email domain in 7-day blocks for the last 12 weeks
   (one row per domain, so it stays under API row limits).
2. A small script maps domains to accounts, reads each account's type from the tracker, and writes
   the usage line per account: days used, user-days vs usual, collapse yes/no, and the tag text.
3. The call readers get each account's usage line with the rules above. A collapse becomes a reason
   like any other, with the numbers as evidence.
4. If the analytics tool can't be read, the run continues **without** usage and says so. It never
   guesses.
