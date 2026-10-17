import numpy as np
import pytest

from alpha.historical import (
    HistoricalParameters,
    historical_allocation,
    simulate_historical,
)


def test_historical_baseline_event_and_positivity():
    p = HistoricalParameters()
    sim = simulate_historical(p, dt_internal=5.0, record_satisfaction=True)
    assert not sim.censored
    assert 2000.0 < sim.T_rep < 4000.0
    assert np.all(sim.N > 0)
    assert np.all(sim.M > 0)
    assert np.all((sim.s_N >= 0) & (sim.s_N <= 1))
    assert np.all((sim.s_M >= 0) & (sim.s_M <= 1))
    assert abs(sim.N[-1] - p.N_crit) / p.N_crit < 1e-6
    assert sim.status == "reached_threshold"


def test_historical_censoring():
    p = HistoricalParameters(S_E=1.0e13, t_max=1000.0)
    sim = simulate_historical(p, dt_internal=5.0, record_satisfaction=False)
    assert sim.censored
    assert np.isnan(sim.T_rep)
    assert sim.status == "censored"


def test_historical_already_below_threshold():
    p = HistoricalParameters(N0=400.0, N_ref=50000.0, kappa=0.01)
    sim = simulate_historical(p, record_satisfaction=False)
    assert sim.T_rep == 0.0
    assert not sim.censored
    assert sim.status == "already_below_threshold"


def test_historical_time_scaling_invariance():
    p = HistoricalParameters()
    c = 2.0
    q = HistoricalParameters(beta_N=p.beta_N * c, beta_M=p.beta_M * c,
                             delta_N=p.delta_N * c, delta_M=p.delta_M * c)
    s1 = simulate_historical(p, dt_internal=2.5, record_satisfaction=False)
    s2 = simulate_historical(q, dt_internal=1.25, record_satisfaction=False)
    assert not s1.censored and not s2.censored
    assert np.isclose(s1.T_rep / s2.T_rep, c, rtol=2e-3)


def test_historical_single_resource_invasion_condition():
    p = HistoricalParameters(w_N=1.0, w_M=1.0)
    C_N = p.w_N / (p.energy_demand_N * p.r_N())
    C_M = p.w_M / (p.energy_demand_M * p.r_M())
    assert C_M > C_N
    s_M_on_N = min(1.0, p.w_M * p.energy_demand_N * p.r_N() /
                   (p.w_N * p.energy_demand_M))
    g_M_on_N = p.beta_M * s_M_on_N - p.delta_M
    assert g_M_on_N > 0


def test_historical_allocation_units():
    p = HistoricalParameters()
    sim = simulate_historical(p, t_eval=[0.0], record_satisfaction=True)
    alloc = historical_allocation(p, p.N0, p.M0)
    assert np.allclose(alloc.satisfaction, sim.s_N[:1] if sim.t.size == 1 else alloc.satisfaction)
    assert np.all(alloc.allocations.sum(axis=0) <= p.supplies() + 1e-6 * p.supplies())
