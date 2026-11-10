"""The vocabulary the agents and the deterministic code share.

The status rules themselves are written in docs/04-status-rules.md for the agents to apply. This module holds only
the parts code can check: which statuses, drivers and tag topics exist, which drivers count as strong signals,
and how long a strong signal must last before it can contribute to red.
"""

# v0.6: four colours, nothing else. "No customer call" is a yellow reason, not a fifth status.
STATUSES = ("red", "orange", "yellow", "green")

# Shown on the board in this order. Older history may hold "no_signal"; it is drawn as yellow.
STATUS_ORDER = {"red": 0, "orange": 1, "yellow": 2, "green": 3}

DRIVERS = {
    "churn_signal": "Churn signal",
    "leaving": "Leaving",
    "disengagement": "Disengaging",
    "tone": "Tone",
    "value_not_proven": "Value not proven",
    "trust_broken": "Data trust",
    "stuck": "Stuck",
    "unmet_ask": "Open ask",
    "golive_late": "Go-live late",
    "usage_collapse": "Product use stopped",
    "other": "Context",
}

# The warning signs that can add up to red. "unmet_ask", "golive_late" and "other" can make an
# account yellow, never red.
STRONG_DRIVERS = {"disengagement", "tone", "value_not_proven", "trust_broken", "stuck", "usage_collapse"}

# A strong signal contributes to red only once it has lasted this many weeks of the window.
MIN_WEEKS_FOR_RED = 3

# There is no health score, but red has implied weights: an explicit churn signal (or a confirmed
# exit) is worth 2 points, each DIFFERENT strong signal that has lasted MIN_WEEKS_FOR_RED is worth 1,
# and red starts at 2. So: one churn signal, one confirmed exit, or two lasting warning signs.
CHURN_SIGNAL_POINTS = 2
LASTING_WARNING_POINTS = 1
RED_AT_POINTS = 2

# Orange = something is wrong AND the nearest end date is this close (or already passed).
ORANGE_WITHIN_DAYS = 90

# The "why" on every card: six fixed topics, at most one tag per topic, written "Topic: value".
# Tags explain the colour; they never change it.
TOPICS = ("Leaving", "Contract", "Tone", "Product use", "Go-live", "Improvements")

# Which topic each driver's tag goes under, and its wording.
DRIVER_TAG = {
    "churn_signal": ("Leaving", "said they may stop"),
    "leaving": ("Leaving", "site is ending"),
    "disengagement": ("Tone", "decision makers gone quiet"),
    "tone": ("Tone", "worse than usual"),
    "value_not_proven": ("Improvements", "no value seen yet"),
    "trust_broken": ("Improvements", "our numbers disputed"),
    "stuck": ("Improvements", "not delivering"),
    "unmet_ask": ("Improvements", "open request unanswered"),
    "golive_late": ("Go-live", "late"),
    "usage_collapse": ("Product use", "stopped"),
}
