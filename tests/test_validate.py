import pytest

from healthcheck.validate import validate, validate_account

EV = [{"label": "call", "url": "https://calls.example/1"}]


def reason(driver, weeks=1, relayed=False, quote=None, evidence=EV):
    w = {"reason": "r", "driver": driver, "weeks_present": weeks, "relayed": relayed, "evidence": evidence}
    if quote:
        w["quote"] = quote
    return w


def account(status, why, call=True, headline="h"):
    return {"account": "Acme", "status": status, "why": why, "customer_call_in_window": call, "headline": headline}


def errors(a, base_dir="."):
    return validate_account(a, base_dir)[0]


# --- red ---------------------------------------------------------------------------------------

def test_red_with_explicit_churn_signal_passes():
    assert errors(account("red", [reason("churn_signal", quote="we won't renew")])) == []


def test_red_with_two_strong_signals_lasting_three_weeks_passes():
    why = [reason("tone", 3, quote="fine."), reason("disengagement", 4)]
    assert errors(account("red", why)) == []


def test_red_with_two_strong_signals_but_one_too_young_fails():
    why = [reason("tone", 3, quote="fine."), reason("disengagement", 2)]
    assert any("red without" in x for x in errors(account("red", why)))


def test_red_from_the_same_driver_twice_is_one_signal_not_two():
    why = [reason("tone", 3, quote="fine."), reason("tone", 4)]
    assert any("red without" in x for x in errors(account("red", why)))


def test_open_ask_and_context_never_count_toward_red():
    why = [reason("unmet_ask", 5, quote="still waiting"), reason("other", 5), reason("tone", 3)]
    assert any("red without" in x for x in errors(account("red", why)))


def test_relayed_churn_signal_cannot_make_red_alone():
    why = [reason("churn_signal", relayed=True, quote="they said they'll cancel")]
    errs = errors(account("red", why))
    assert any("red without" in x for x in errs)
    assert any("verbatim customer quote" in x for x in errs)


def test_relayed_statement_can_support_red_alongside_a_direct_one():
    why = [reason("churn_signal", quote="we're looking at another vendor"), reason("tone", 1, relayed=True)]
    assert errors(account("red", why)) == []


def test_red_needs_a_quote():
    assert any("quote" in x for x in errors(account("red", [reason("churn_signal")])))


# --- green and no signal -----------------------------------------------------------------------

def test_without_a_customer_call_the_only_status_is_no_signal():
    """The first check: silence is not health, and it is not yellow or red either."""
    for status in ("green", "yellow", "red"):
        why = [reason("churn_signal", quote="we won't renew")]
        assert any("first check makes it no signal" in x for x in errors(account(status, why, call=False)))


def test_red_points_follow_the_implied_weights():
    from healthcheck.validate import red_points
    assert red_points([reason("churn_signal")]) == 2
    assert red_points([reason("tone", 3), reason("stuck", 5)]) == 2
    assert red_points([reason("tone", 3), reason("stuck", 2), reason("unmet_ask", 9)]) == 1
    assert red_points([reason("churn_signal", relayed=True), reason("tone", 3, relayed=True)]) == 0


def test_no_signal_without_a_call_passes():
    assert errors(account("no_signal", [], call=False, headline=None)) == []


# --- evidence ----------------------------------------------------------------------------------

def test_reason_without_evidence_link_fails():
    why = [reason("unmet_ask", evidence=[{"label": "call"}])]
    assert any("no evidence" in x for x in errors(account("yellow", why)))


def test_yellow_needs_a_reason():
    assert any("no reason" in x for x in errors(account("yellow", [])))


def test_unknown_status_and_driver_fail():
    assert errors(account("amber", [])) == ["Acme: unknown status 'amber'"]
    assert any("unknown driver" in x for x in errors(account("yellow", [reason("vibes")])))


# --- verbatim quotes against local transcripts -------------------------------------------------

@pytest.fixture
def transcripts(tmp_path):
    (tmp_path / "a.md").write_text("[00:10] Laura: After a month we have nothing usable.\n")
    (tmp_path / "b.md").write_text("[00:20] Tom: The counts were off again.\n")
    return tmp_path


def test_quote_found_in_one_of_several_cited_transcripts_passes(transcripts):
    ev = [{"url": "b.md#L1"}, {"url": "a.md#L1"}]
    why = [reason("churn_signal", quote="After a month we have nothing usable", evidence=ev)]
    assert errors(account("red", why), base_dir=str(transcripts)) == []


def test_quote_matching_ignores_curly_quotes_and_punctuation(transcripts):
    why = [reason("churn_signal", quote="after a month, we have nothing usable!", evidence=[{"url": "a.md"}])]
    assert errors(account("red", why), base_dir=str(transcripts)) == []


def test_paraphrased_quote_fails(transcripts):
    why = [reason("churn_signal", quote="After a month nothing is usable", evidence=[{"url": "a.md"}])]
    assert any("not verbatim" in x for x in errors(account("red", why), base_dir=str(transcripts)))


def test_remote_links_are_not_checked_for_quotes(transcripts):
    why = [reason("churn_signal", quote="anything at all")]
    assert errors(account("red", why), base_dir=str(transcripts)) == []


# --- the run as a whole ------------------------------------------------------------------------

def test_every_roster_account_needs_a_finding():
    errs, _ = validate([account("green", [])], roster=[{"account": "Acme"}, {"account": "Vertex"}])
    assert errs == ["Vertex: in the roster but has no finding (every installed account gets a status)"]


def test_duplicate_findings_fail():
    errs, _ = validate([account("green", []), account("green", [])])
    assert any("appears twice" in x for x in errs)


def test_long_headline_is_a_warning_not_an_error():
    errs, warns = validate([account("green", [], headline=" ".join(["word"] * 20))])
    assert errs == [] and len(warns) == 1
