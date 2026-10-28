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

# There is no health score, but red has implied weights: an explicit churn signal is worth 2 points,
# each DIFFERENT strong signal that has lasted MIN_WEEKS_FOR_RED is worth 1, and red starts at 2.
# So: one churn signal, or two lasting warning signs. Open asks and younger warnings are worth 0.
CHURN_SIGNAL_POINTS = 2
LASTING_WARNING_POINTS = 1
RED_AT_POINTS = 2
