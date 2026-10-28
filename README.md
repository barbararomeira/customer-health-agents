# Customer health agents

![python](https://img.shields.io/badge/python-3.9%2B-blue) ![dependencies](https://img.shields.io/badge/dependencies-stdlib%20only-success) ![license](https://img.shields.io/badge/license-MIT-lightgrey)

### Red means "would likely churn without escalation". Nothing else.

**A weekly agent run that reads every installed account's customer calls and gives each one a
status (red, yellow, green or no signal) with the reason and the evidence. Plus the thinking behind
it: which signals and metrics were considered, how to read tone without a sentiment score, and how a
backtest on a churned account changed the rules.**

*Companion projects: [**product-discovery-agents**](https://github.com/barbararomeira/product-discovery-agents) reads customer calls for what to build; [**evidence-scored-call-review**](https://github.com/barbararomeira/evidence-scored-call-review) reads them for how the sales conversation went. This one reads them for whether the account is staying.*

| | |
|---|---|
| **Problem** | Churn risk lives in call tone, in who stopped turning up, and in end dates nobody connected to the complaint. Health scores turn that into a number people argue with instead of act on. |
| **Built** | Agents read each account's calls against written rules; deterministic code refuses any status those rules do not allow before a board is built. |
| **Human boundary** | The system says which accounts are red and why. A person reviews every new red before anyone else sees it and decides the escalation. |
| **Public scope** | Clean-room template on invented accounts and transcripts. Call-recorder, CRM and publishing integrations are excluded. |
| **Verification** | A validator over the agents' output (status rules, evidence on every reason, quotes checked verbatim against local transcripts, every account covered), tests on it and on the board, and a shipped example the tests rebuild. |
| **Status** | Rules v0.2, **proposed**. Backtested on one churned account. |

<p align="center"><img src="docs/example-board.png" alt="The example board: one red account with three quoted reasons and a pilot end date, three yellow cards, one no-signal card, one green account and a recurring-reasons panel." width="100%"></p>

---

## The problem

Every customer-facing team has a feeling about which accounts are in trouble. The feeling is usually
right about the loud ones and wrong about the quiet ones.

The quiet ones are the expensive ones: a decision maker who used to speak in every call and hasn't
for three weeks; a customer who said "it duplicates what we have" in a weekly call while the pilot
end date sat in a different system; no recordings for a month, read as "all fine". None of these
arrive as a complaint. All of them are in the calls, if somebody reads all of them, every week,
against the same rules.

## Read it in this order

| | | |
|---|---|---|
| 1 | [**The question**](docs/01-the-question.md) | What the check answers (and what it deliberately doesn't), the four statuses, why not a churn probability |
| 2 | [**Signals and metrics considered**](docs/02-signals-and-metrics.md) | Everything we thought about measuring (calls, meetings, product usage, contract), how each one misleads, and which ones made it into the rules |
| 3 | [**Reading tone**](docs/03-reading-tone.md) | Why an absolute sentiment score fails, and the alternative: each customer compared with their own earlier calls, speaker by speaker, with a quote for every claim |
| 4 | [**The status rules**](docs/04-status-rules.md) | The full v0.2 rules |
| 5 | [**Backtesting**](docs/05-backtesting.md) | v0.1 gave zero weeks of warning on a real churn. What it missed, what changed, and how to backtest |
| 6 | [**How the weekly run was designed**](docs/06-how-the-run-worked.md) | Agent roles, one finding, the board, the weekly rhythm |
| | [**Decisions**](DECISIONS.md) | 12 choices, each with what we considered and what it costs |
| | [**Worked example**](example-run/) | Six invented accounts, their calls, the findings and the board |
| | [**Agent prompt**](prompts/weekly.md) | The rules turned into instructions for the coordinator and the account readers |

## Quickstart

```bash
# See it work on the example (no API key, no install)
python3 -m healthcheck example-run/runs/2026-W12 --date 2026-03-16 --config config.example.json
open example-run/runs/2026-W12/board.html

# Run the tests
python3 -m pip install pytest && python3 -m pytest -q

# Use it on your own accounts
cp config.example.json config.json            # edit: internal speakers, never-a-risk list, models
mkdir transcripts notes                        # one transcript per call, one notes file per account
$EDITOR roster.json                            # every installed account; see example-run for the shape
./scripts/run_weekly.sh                        # needs Claude Code on the PATH
```

`config.json`, `roster.json`, `transcripts/`, `notes/` and `output/` are git-ignored. Your customers'
words never belong in a repo. The board is a local HTML file; publishing it is deliberately a
separate step, so a person sees every new red first ([Decision 9](DECISIONS.md#9-a-person-sees-a-new-red-before-anyone-else)).

## The ideas in one screen

- **Red is rare and rule-based.** One explicit churn signal, or two strong warning signs that have
  each lasted three of the last four weeks. When in doubt, yellow.
- **Silence isn't health.** No customer call in the window means *no signal*, never green.
- **Attendance is who speaks**, not who was on the invite.
- **Tone is compared with the same customer**, never with other customers.
- **A missing recording is unknown**, not a no-show, unless notes say otherwise.
- **The nearest end date decides urgency**: pilot end, decision meeting, contract or renewal,
  whichever comes first.
- **A second-hand statement can make yellow**, never red on its own.
- **Every reason has a quote and a link.** No evidence, no reason.
- **Reasons are about the customer**, never about the account owner.
- **No scores on the board.** People act on reasons and argue with numbers.

## What we deliberately left out

- **A churn probability.** Too few churns to calibrate one.
- **Revenue weighting.** Every red gets the same treatment.
- **Product usage.** Wanted, and listed in [the metrics](docs/02-signals-and-metrics.md#from-the-product),
  but it needs an integration per product. The roster is the place to add it.
- **Call-recorder and CRM connectors.** The run reads a folder of transcripts. Getting them there is
  yours; [product-discovery-agents](https://github.com/barbararomeira/product-discovery-agents/tree/main/sources)
  shows a folder setup and a connector setup.

## Repository layout

```
docs/                     the thinking: 01 question … 06 how the run works
DECISIONS.md              12 choices, what was considered, what each costs
prompts/weekly.md         coordinator prompt + account-reader brief ({{PLACEHOLDERS}} from config)
healthcheck/              rules.py (the numbers), validate.py (the checks), board.py, prompt.py — stdlib only
scripts/run_weekly.sh     the scheduled entry point: lock, agents, validate, build
config.example.json       copy to config.json
example-run/              six invented accounts, their calls and notes, findings and the board
tests/                    validator rules, board history, and a rebuild of the example
```

## Note on names

Every company, person and quote in this repo is invented. Northwind Robotics is the fictional vendor.

MIT licensed.
