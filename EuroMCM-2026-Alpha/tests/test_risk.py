import numpy as np
import pytest

from alpha.risk import RiskThresholds, assess_risk, paired_damage


def _base_t(n=1001):
    return np.linspace(0.0, 100.0, n)


def test_threshold_order_validation():
    with pytest.raises(ValueError):
        assess_risk([0, 1], [1.5e8, 1.5e8], [1, 1], 1.5e8, RiskThresholds())


def test_effective_extinction_precedence():
    t = _base_t()
    H = np.full_like(t, 8e9)
    H[t >= 20] = 5e7
    r = assess_risk(t, H, np.ones_like(t), 8e9, RiskThresholds())
    assert r.extinction and r.outcome == "extinction"
    assert r.terminal_extinction
    assert not r.recovered_after_extinction
    assert np.isclose(r.extinction_time, t[np.argmax(t >= 20)])


def test_recovered_first_passage_is_flagged_not_irreversible():
    t = _base_t()
    H = np.full_like(t, 8e9)
    H[(t >= 20) & (t < 40)] = 5e7
    r = assess_risk(t, H, np.ones_like(t), 8e9, RiskThresholds())
    assert r.extinction
    assert r.recovered_after_extinction
    assert not r.terminal_extinction


def test_rapid_contraction_without_small_population_is_not_collapse():
    t = _base_t()
    H = np.full_like(t, 8e9)
    H[t >= 5] = 3.9e9
    r = assess_risk(t, H, np.ones_like(t), 8e9, RiskThresholds())
    assert r.rapid_contraction
    assert not r.rapid_collapse
    assert not r.cumulative_collapse
    assert r.outcome == "non_marginal"


def test_rapid_collapse_requires_size_floor():
    t = _base_t()
    H = np.full_like(t, 5e9)
    H[t >= 5] = 1.5e8
    r = assess_risk(t, H, np.ones_like(t), 5e9, RiskThresholds())
    assert r.rapid_contraction and r.rapid_collapse
    assert r.outcome == "rapid_collapse"
    assert not r.extinction


def test_cumulative_collapse_without_rapid_event():
    t = _base_t()
    H = 8e9 * np.exp(-0.025 * t)
    r = assess_risk(t, H, np.ones_like(t), 8e9, RiskThresholds())
    assert r.cumulative_loss > 0.9
    assert not r.rapid_collapse
    assert not r.extinction
    assert r.outcome == "cumulative_collapse"


def test_marginal_and_non_marginal_after_no_catastrophe():
    t = _base_t()
    H = np.full_like(t, 8e9)
    marginal = assess_risk(t, H, np.full_like(t, 0.7), 8e9, RiskThresholds())
    non = assess_risk(t, H, np.ones_like(t), 8e9, RiskThresholds())
    assert marginal.outcome == "marginal"
    assert non.outcome == "non_marginal"


def test_paired_damage():
    t = np.linspace(0, 10, 101)
    ref = 8e9 * np.exp(0.01 * t)
    ai = 0.5 * ref
    d = paired_damage(t, ai, t, ref)
    assert np.isclose(d["final_damage"], 0.5)
    assert np.isclose(d["mean_damage"], 0.5)
