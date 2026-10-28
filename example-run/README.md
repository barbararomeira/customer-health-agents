# Example run

Six invented accounts, their last four weeks of calls and notes, the findings written from them,
and the [board](runs/2026-W12/board.html) ([screenshot](../docs/example-board.png)). Rebuild it
from the repo root with:

```bash
python3 -m healthcheck example-run/runs/2026-W12 --date 2026-03-16 --config config.example.json
```

The findings were written the way an account reader writes them, so you can see what each rule
looks like on real-shaped data. Each account shows one rule:

| Account | Status | Why it is this status, and not one step worse |
|---|---|---|
| **Acme Foods** | Red | An explicit churn signal ("we won't continue") with the pilot ending in 46 days. Also two strong signals lasting three weeks: value questioned on 24 Feb and 10 Mar, and counts disputed in both calls. |
| **Corvel Plastics** | Yellow | Procurement questioning the licence count, but **relayed** in an internal note, not said on a call. Relayed statements cannot make red alone. |
| **Halden Pumps** | Yellow | The plant manager has stopped speaking in calls (spoke on 19 Feb, absent 5 and 12 Mar). That is disengagement, but only two weeks old. |
| **Vertex Motors** | Yellow | An ask unanswered for two weeks, chased by the plant manager in person. Open asks are never red. |
| **Orbis Packaging** | No signal | No customer call in the window. The notes explain it (monthly calls during a rebuild), so it is not counted as a no-show, but notes cannot make it green. |
| **Lumen Devices** | Green | A customer call in the window, positive, asking to expand. |

`runs/history.json` holds two earlier weeks, so the trend tab has something to show and the *New*
tags work. **Brightwater Labs** appears in those weeks and not in this roster, so the board shows it
as *Left*.

Try breaking it: in `runs/2026-W12/findings_g1.json`, set Halden's status to `red` and its
`weeks_present` to 3, then rebuild. The validator refuses and no board is built, because one strong
signal is not two.
