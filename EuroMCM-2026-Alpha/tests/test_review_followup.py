import numpy as np
import pytest
from dataclasses import replace
from alpha.risk import assess_risk, RiskThresholds
from alpha.rsi import RSIParameters, rsi_diagnostics, simulate_rsi, Intervention

def test_event_catches_between_sample_excursion():
    r = assess_risk([0, 1], [2e8, 2e8], [1, 1], 1e9,
                    RiskThresholds(), p_bad=0, extinction_event_time=0.4)
    assert r.extinction and r.recovered_after_extinction
    assert r.extinction_time == 0.4

def test_no_event_is_authoritative():
    r = assess_risk([0, 1], [2e8, 2e8], [1, 1], 1e9,
                    RiskThresholds(), p_bad=0, extinction_event_time=np.nan)
    assert not r.extinction

def test_bad_event_time_rejected():
    with pytest.raises(ValueError):
        assess_risk([0, 1], [2e8, 2e8], [1, 1], 1e9,
                    RiskThresholds(), extinction_event_time=2)

def test_deprivation_mortality_changes_only_human_growth():
    p = RSIParameters(E_total=0)
    a = rsi_diagnostics(p, p.H0, p.A0, p.q0)
    b = rsi_diagnostics(replace(p, deprivation_mortality=.06), p.H0, p.A0, p.q0)
    assert np.isclose((b.dH-a.dH)/p.H0, -.06)
    assert a.dA == b.dA and a.dq == b.dq

def test_deprivation_mortality_zero_when_adequate():
    p = RSIParameters(A0=0, rho=0)
    a = rsi_diagnostics(p, p.H0, 0, p.q0)
    b = rsi_diagnostics(replace(p, deprivation_mortality=.06), p.H0, 0, p.q0)
    assert a.allocation.satisfaction[0] >= .8
    assert a.dH == b.dH

def test_mortality_settings_validation():
    with pytest.raises(ValueError):
        replace(RSIParameters(), deprivation_mortality=-1).validate()


def test_certificate_includes_deprivation_mortality():
    from alpha.viability import viability_certificate
    p = replace(RSIParameters(), beta_H=.2, delta_H=.12,
                deprivation_mortality=.06)
    cert = viability_certificate(p)
    required = (.12+.06)/(.2+.06/.8)
    assert cert.r_human == pytest.approx(required)
    assert cert.a_safe == pytest.approx(required/cert.b_under)
