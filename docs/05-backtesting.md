# 5. Backtesting: how the rules got better

The only honest test of churn rules is an account that actually left. Run the rules over its last
months of calls, week by week, and ask: **how many weeks of warning would the board have given?**

## The first backtest: zero weeks

Version 0.1 of the rules was run against an account that had already churned. It gave **no warning
at all**. Three reasons, each a lesson:

| What happened | Why the rules missed it | Change in v0.2 |
|---|---|---|
| No customer call had been recorded for months | With no calls, there were no negative signals, so the account looked fine | **No signal** became its own status (a yellow reason since v0.5), and **green needs a customer call**. Silence isn't health |
| The customer said in calls that it wasn't giving them value | "Value not proven" only fired near the **renewal** date, which was months away. The customer actually decided at the **end of the trial phase** | Every 90-day rule uses the **nearest end date**: contract, renewal, pilot/POC end or a named decision meeting |
| The account was installed but never really delivered | "Stuck" trusted the go-live date field, which had been filled in | "Stuck" is judged on **real delivery**, not the field |

Plus two smaller changes: three weeks of unexplained missing meetings is yellow, and a relayed
customer statement can make yellow.

**The generalisation:** a rule that depends on a date is only as good as the choice of date, and
the date the customer decides on is often not the one in the contract field.

## How to run a backtest

1. Take an account that left. Collect every call, note and date for its last 3–6 months.
2. Step through it a week at a time, giving the rules only what was known **that week**.
3. Record the status each week. The first red is your warning; count the weeks to the churn.
4. For every week that should have been red and wasn't, write down which rule missed it and why.
5. Change the rule, write the reason in the changelog, and re-run **every** earlier backtest.
   A fix for one churn must not make the board noisier for everyone else.

## Also check the other direction

A rule set that turns every account red would pass every backtest. So also check:

- **How many reds this week?** If it isn't rare, the rules are too loose.
- **Reds that were overridden.** Each override, with its reason, is a false positive to learn from.
- **Accounts that stayed after being red.** Was the escalation the reason, or was the red wrong?

## Status

v0.2 is **proposed**: backtested on one churned account, not yet agreed with the team that will use
it. One backtest is a direction, not a validation.
