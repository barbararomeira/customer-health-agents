"""The vocabulary the agents and the deterministic code share.

The status rules themselves are written in docs/04-status-rules.md for the agents to apply. This module holds only
the parts code can check: which statuses and drivers exist, which drivers count as strong signals,
and how long a strong signal must last before it can contribute to red.
"""

STATUSES = ("red", "yellow", "green", "no_signal")

# Shown on the board in this order.
STATUS_ORDER = {"red": 0, "yellow": 1, "no_signal": 2, "green": 3}

DRIVERS = {
    "churn_signal": "Churn signal",
    "disengagement": "Disengaging",
    "tone": "Tone",
    "value_not_proven": "Value not proven",
    "trust_broken": "Data trust",
    "stuck": "Stuck",
    "unmet_ask": "Open ask",
    "other": "Context",
}

# The five warning signs that can add up to red. "unmet_ask" and "other" can make an account
# yellow, never red.
STRONG_DRIVERS = {"disengagement", "tone", "value_not_proven", "trust_broken", "stuck"}

# A strong signal contributes to red only once it has lasted this many weeks of the window.
MIN_WEEKS_FOR_RED = 3

# How many strong signals, each lasting MIN_WEEKS_FOR_RED, make red without an explicit churn signal.
MIN_STRONG_SIGNALS_FOR_RED = 2
