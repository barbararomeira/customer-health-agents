# 7. Proposed for v0.3

**Not applied.** The code and the example still follow v0.2. This is the next set of changes, written
down after the first real weekly run, while the contract end dates it depends on were being corrected.

## 1. Colour means risk, and only risk

In v0.2, "the contract ends soon" is mixed into the colours through the 90-day rules. v0.3 splits
it out, so each colour has one meaning:

| Colour | Meaning |
|---|---|
| **Red** | Would likely churn without escalation: a churn signal, two lasting warning signs, **or a contract past its end date with no renewal or extension signed** |
| **Orange** *(new)* | Something is wrong **and** the contract ends within 90 days |
| **Yellow** | Something is wrong, with no near deadline |
| **Green** | Healthy, whatever the contract date |

## 2. Contract timing becomes a tag

Every account within 90 days of its end date gets a **"Renews in X days"** tag, green ones included,
and appears in a **"Renewals in the next 90 days"** strip at the top of the board, sorted by date. A
healthy account with a renewal next month still needs someone to run the renewal; it just doesn't
need an escalation.

End dates come from the sales pipeline (close date plus committed term) and the CRM renewal date
once it is reliably filled in.

## 3. Onboarding accounts are judged on the go-live clock

Installed accounts that are not fully live are judged on how long go-live is taking, not on call
volume.

- The clock starts at installation. **The target is 4 weeks.**
- **Go-live late** (a new warning sign): more than **5 weeks** from installation without a full
  go-live. More than **12 weeks** counts as a strong warning sign.
- **A partial go-live is not a go-live.** The clock keeps running until every contracted line is live.
- No customer call is fine during the first 5 weeks. After that, a late go-live with no customer
  call is flagged, because silence during a delay is when dissatisfaction builds unseen. *(This is
  the one case where v0.3 would look past "no signal".)*

## 4. Two lookbacks

- The **last 4 weeks** set this week's status (unchanged).
- The **last 12 weeks** give each customer's baseline for tone and attendance, and catch slow
  patterns, such as a sponsor or leadership gradually dropping out of meetings.

## What would change in the code

- `STATUSES` gains `orange`; the board gets an orange section and pill.
- The roster's `end_date` drives a tag and a renewals strip instead of a status.
- `roster.json` gains `installed_on` and `fully_live_on`; a `golive_late` driver is added, strong
  after 12 weeks.
- `config.json` gains `baseline_weeks: 12`.

## Open questions

- Is orange a separate escalation path, or a yellow with a deadline? If the response is the same,
  it should be a tag, not a colour.
- The 4 / 5 / 12-week onboarding numbers are targets the team chose, not measured from past
  go-lives. Check them against the actual installation-to-go-live history before using them.
