# 9. The product story: six versions in three weeks

This page is for anyone who builds products. It isn't about the rules; it's about how the rules got
here. Each version started with something its user said, or something the data got wrong. Each
version also had something taken out.

## Who it's for, and the job

| | |
|---|---|
| **User** | The person who owns customer success for an installed base of B2B accounts, and the account owners who act on the board every Monday |
| **Job** | "Tell me which accounts need me this week, and why, without me reading every call." |
| **Not the job** | Forecasting revenue, scoring accounts, judging the people who own them |
| **Success looks like** | A churn is seen weeks before it happens, and a red is trusted enough that someone acts on it the same day |

## The versions

| Version | What triggered it | What changed | What was taken out |
|---|---|---|---|
| **v0.1** | "We have a feeling about which accounts are in trouble. It's right about the loud ones." | Agents read every account's calls weekly against written rules. Red, yellow, green, each reason with a quote | Any score or probability |
| **v0.2** | A **backtest** on an account that had already left: v0.1 gave **zero weeks of warning** | "Silence is not health" (no call can't be green); the nearest end date includes pilot ends and decision meetings; delivery judged on reality, not a go-live field | Trust in the go-live date field |
| **v0.3** | The first real weekly run, and a request to make every account near renewal yellow. That would have mixed "something is wrong" with "renewal is coming" | **Orange** = something wrong *and* the end date is within 90 days. Contract timing became a tag. A go-live clock for onboarding accounts | "Out of contract = red": past end dates were stale data more often than real exits |
| **v0.4** | "Our goal is daily use, but some customers get daily reports and have no reason to log in" | Product use joined the **same colours**: regular use counts in favour, and only a *collapse* counts against, only for accounts meant to use the product | A separate usage score. Page views as the measure: a screen left open made two steady accounts look like they were leaving |
| **v0.5** | A site that was leaving showed as orange: the decision came by email and appeared only in a team chat channel. Then the owner said: *"I just want red, orange, yellow and green, and why. It's becoming too complex."* | Team chat channels became a source, and a hard fact (equipment removed) is red. The board went down to **four colours and why** | The fifth status ("no signal"), the renewals strip, the recurring-reasons panel, and a proposed "Leaving" section |
| **v0.6** | The board had around twenty different tag wordings. *"Do we need any more?"* | **Six topics, one tag each**: Leaving, Contract, Tone, Product use, Go-live, Improvements | A tag that said "customer call in the last 4 weeks" (it said nothing, and was once false). Splitting late go-lives by whose fault (the cause couldn't be captured reliably) |

## What the versions have in common

- **Every addition replaced something.** v0.5 added a source and removed three parts of the page.
  v0.6 added a fixed vocabulary and removed a dozen ad-hoc wordings. The board got simpler as the
  rules got better.
- **New data joins the existing model; it doesn't get its own score.** Product use, contract dates
  and team chat all push an account toward a colour. None of them became a second number to argue
  about.
- **The user's words are the spec.** "Red, orange, yellow, green, and why" is the design brief for
  the whole board. When a proposal didn't fit that sentence, it didn't ship.
- **Ideas that would be hard to get right got turned down, not built badly.** Whose fault a delay
  was, and "out of contract = red", were both reasonable ideas. Both were dropped because the
  agents couldn't tell them apart reliably, and a confident wrong answer is worse than a plain one.
- **Every rule change updates every place the rule is written** (rules, board help text, agent
  prompt, code, these docs) in the same change. A board whose help text disagrees with its rules
  stops being trusted.

## What we'd measure to know it works

These aren't measured yet; they are what the product should be judged on.

| Measure | Why it matters |
|---|---|
| **Weeks of warning** before an account leaves | The whole point. v0.1 scored zero on its backtest |
| **Reds the reviewer confirms** | A red nobody believes gets ignored. Red is kept rare on purpose |
| **Colour changes per week** | Too many and the board is noise; none and it's not looking |
| **Days from a new red to an escalation** | A board that's read but not acted on doesn't save accounts |

## What's next, and what isn't

- **Next:** re-check the product-use cut-offs after a few weekly runs; backtest v0.6 on more
  accounts that left.
- **Not planned:** a churn probability (too few churns to calibrate), revenue weighting (every red
  gets the same treatment), or a seventh topic, unless reasons keep turning up that fit none of the
  six.
