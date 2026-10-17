from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from alpha.rsi import RSIParameters, _bad_fraction, simulate_rsi, rsi_diagnostics
from alpha.uncertainty import probability_summary
from alpha.allocation import allocate_resources


@pytest.mark.parametrize("scale", [1e-80, 1e-40, 1.0, 1e40, 1e80])
def test_water_filling_with_cap_is_weight_unit_invariant(scale):
    r = allocate_resources([1, 1], [[1], [10]], [5], [scale, scale])
    assert np.allclose(r.satisfaction, [1, 0.4], atol=1e-12)


def test_horizon_and_window_endpoints_are_included():
    p = replace(RSIParameters(), T=11.3, W_window=2.2, dt=0.7)
    for integrator in ["rk4", "solve_ivp"]:
        sim = simulate_rsi(p, 0.5, integrator=integrator)
        assert sim.t[-1] == pytest.approx(p.T)
        assert np.min(abs(sim.t - (p.T - p.W_window))) < 1e-12
        assert sim.numerical_diagnostics["projection_count"] == 0


def test_zero_land_demand_does_not_divide_by_zero():
    p = replace(RSIParameters(), ell_H=0.0)
    d = rsi_diagnostics(p, p.H0, p.A0, p.q0, 1.0)
    assert d.allocation.success


@pytest.mark.parametrize("integrator", ["rk4", "solve_ivp"])
def test_absent_ai_is_an_invariant_state(integrator):
    p = replace(RSIParameters(), A0=0.0, L_site=0.0, T=12.0)
    sim = simulate_rsi(p, 1.0, integrator=integrator)
    assert np.all(sim.A == 0)
    assert np.allclose(sim.q, p.q0)
    assert np.all(sim.B == 0)


def test_equality_is_not_marginal_due_to_roundoff():
    p = RSIParameters()
    times = np.array([90.0, 95.0, 100.0])
    assert _bad_fraction(times, np.full(3, p.H_min),
                         np.full(3, np.nextafter(p.s_min, 0.0)), p) == 0
    assert _bad_fraction(times, np.full(3, p.H_min),
                         np.full(3, p.s_min - 1e-7), p) == 1


def test_failed_runs_remain_visible_in_probability_denominator():
    rows = pd.DataFrame([
        dict(scenario="x", a=0, success=True, outcome="marginal"),
        dict(scenario="x", a=0, success=False, outcome="failed"),
    ])
    row = probability_summary(rows).iloc[0]
    assert row.n_total == 2 and row.n_failed == 1 and row.n_valid == 1


def test_invalid_outcome_cannot_be_counted_as_success():
    rows = pd.DataFrame([dict(scenario="x", a=0, success=True, outcome="unknown")])
    with pytest.raises(ValueError):
        probability_summary(rows)


def test_failure_blocks_full_library_safety_claim(monkeypatch):
    from types import SimpleNamespace
    import alpha.uncertainty as uq

    p = RSIParameters()
    monkeypatch.setattr(uq, "sample_parameters", lambda *args: [(0, p, {})])

    def simulation(params, **kwargs):
        if params.allocation_rule == "priority" and params.growth_mode == "non_saturating":
            raise RuntimeError("deliberate verification failure")
        return SimpleNamespace(outcome="non_marginal", success=True, min_H=p.H0)

    monkeypatch.setattr(uq, "simulate_rsi", simulation)
    detail, summary = uq.structural_robustness(n_samples=1, a_values=[1.0])
    assert len(detail) == 4
    assert summary.iloc[0].n_failed == 1
    assert not summary.iloc[0].robust_population_floor
    assert not summary.iloc[0].robust_non_marginal


@pytest.mark.parametrize("key,value", [("eta", np.nan), ("omega", -1), ("xi", -0.1)])
def test_invalid_parameters_are_rejected(key, value):
    with pytest.raises(ValueError):
        replace(RSIParameters(), **{key: value}).validate()
