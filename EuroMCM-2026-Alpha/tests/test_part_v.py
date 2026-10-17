from dataclasses import replace
import numpy as np
import pytest

from alpha.rsi import Intervention, RSIParameters, rsi_diagnostics, simulate_rsi


def test_intervention_validation():
    Intervention(kind="protect", tau=0, u_bar=0.5).validate()
    Intervention(kind="cap", tau=0, cap_fraction=0.5, tau_cap=1).validate()
    with pytest.raises(ValueError):
        Intervention(kind="bad").validate()
    with pytest.raises(ValueError):
        Intervention(kind="protect", u_bar=1.5).validate()
    with pytest.raises(ValueError):
        Intervention(kind="cap", cap_fraction=-0.1).validate()


def test_protection_below_alignment_is_inactive():
    p = RSIParameters(T=20.0, dt=0.5)
    base = simulate_rsi(p, 0.5, intervention=None)
    pol = simulate_rsi(p, 0.5, intervention=Intervention(
        kind="protect", tau=0.0, u_bar=0.3))
    assert np.allclose(base.H, pol.H, rtol=1e-10, atol=1e-8)
    assert np.allclose(base.s_H, pol.s_H, rtol=1e-10, atol=1e-10)
    assert np.allclose(pol.protection_g, 0.5)


def test_protection_endpoint_reaches_human_maximum():
    p = RSIParameters(H0=6e10, H_min=1e8, H_ext=1e6, T=10.0)
    d = rsi_diagnostics(p, p.H0, p.A0, p.q0, 0.0, t=0.0,
                        intervention=Intervention(kind="protect", tau=0.0, u_bar=1.0))
    assert np.isclose(d.allocation.satisfaction[0], d.b_H_tot, rtol=1e-10, atol=1e-10)
    assert np.isclose(d.protection_g, 1.0)


def test_cap_with_full_fraction_is_inactive():
    p = RSIParameters(T=20.0, dt=0.5)
    base = simulate_rsi(p, 0.5, intervention=None)
    pol = simulate_rsi(p, 0.5, intervention=Intervention(
        kind="cap", tau=0.0, cap_fraction=1.0, tau_cap=p.tau_build))
    assert np.allclose(base.A, pol.A, rtol=1e-10, atol=1e-8)
    assert np.allclose(base.B, pol.B, rtol=1e-10, atol=1e-10)


def test_cap_keeps_installed_stock_below_target():
    p = RSIParameters(T=30.0, dt=0.5)
    cap = 0.1 * p.A_max
    sim = simulate_rsi(p, 0.5, intervention=Intervention(
        kind="cap", tau=0.0, cap_fraction=0.1, tau_cap=p.tau_build))
    assert sim.A[0] == pytest.approx(p.A0)
    assert np.max(sim.A) <= cap * (1 + 1e-8)
    assert sim.outcome in {"marginal", "non_marginal", "extinction"}


def test_cap_grandfathers_existing_excess_without_jump():
    p = RSIParameters(A0=9e5, T=100.0, dt=0.5)
    cap = 0.1 * p.A_max
    sim = simulate_rsi(p, 0.5, intervention=Intervention(
        kind="cap", tau=0.0, cap_fraction=0.1, tau_cap=p.tau_build))
    assert sim.A[0] == pytest.approx(9e5)
    assert np.min(sim.A) <= cap
    assert sim.A[-1] < sim.A[0]


def test_policy_energy_land_and_manufacturing_constraints():
    p = RSIParameters(T=30.0, dt=0.5)
    for pol in [
        Intervention(kind="protect", tau=5.0, u_bar=0.9),
        Intervention(kind="cap", tau=5.0, cap_fraction=0.3, tau_cap=p.tau_build),
    ]:
        sim = simulate_rsi(p, 0.0, intervention=pol)
        assert np.all(sim.E_human_allocated + sim.E_AI_allocated <= sim.E_op + 1e-6 * np.maximum(1, sim.E_op))
        assert np.all(p.c_build * sim.B <= sim.R_build + 1e-6 * np.maximum(1, sim.R_build))
        assert np.all(sim.B <= sim.manufacturing + 1e-8)
        assert np.all(sim.A * p.ell_site <= p.L_site + 1e-6)


def test_protection_switch_time_is_recorded():
    p = RSIParameters(T=20.0, dt=0.5)
    sim = simulate_rsi(p, 0.2, intervention=Intervention(
        kind="protect", tau=8.0, u_bar=0.9))
    before = sim.t < 8.0 - 1e-12
    after = sim.t >= 8.0 - 1e-12
    assert np.allclose(sim.protection_g[before], 0.2)
    assert np.allclose(sim.protection_g[after], 0.9)


def test_full_horizon_continues_after_extinction_when_requested():
    from alpha.scenarios import scenario_stress
    p = replace(scenario_stress(), T=100.0, dt=0.5)
    short = simulate_rsi(p, 0.0, terminate_on_extinction=True)
    full = simulate_rsi(p, 0.0, terminate_on_extinction=False)
    assert short.outcome == "extinction"
    assert full.outcome == "extinction"
    assert np.isfinite(full.extinction_time)
    assert full.t[-1] == pytest.approx(p.T)
    assert short.t[-1] < p.T
    assert np.isfinite(full.p_bad_final_window)


def test_shutdown_zero_fraction_is_baseline():
    p = RSIParameters(T=20.0, dt=0.5)
    base = simulate_rsi(p, 0.5, intervention=None)
    pol = simulate_rsi(p, 0.5, intervention=Intervention(
        kind="shutdown", tau=5.0, shutdown_fraction=0.0))
    assert np.allclose(base.H, pol.H, rtol=1e-10, atol=1e-8)
    assert np.allclose(base.A, pol.A, rtol=1e-10, atol=1e-8)


def test_full_shutdown_disables_operation_but_keeps_installed_stock():
    p = RSIParameters(A0=1e5, T=20.0, dt=0.5)
    pol = Intervention(kind="shutdown", tau=5.0, shutdown_fraction=1.0)
    sim = simulate_rsi(p, 0.5, intervention=pol)
    assert sim.A[0] == pytest.approx(1e5)
    # Installed stock decays; it is not reset to zero at activation.
    assert sim.A[-1] > 0
    assert sim.A[-1] < sim.A[0]
    assert np.all(p.ell_site * sim.A <= p.L_site + 1e-6)
    d = rsi_diagnostics(p, p.H0, 1e5, p.q0, 0.5, t=10.0, intervention=pol)
    assert d.operating_fraction == 0.0
    assert d.B == 0.0
    assert d.E_AI_demand == 0.0
    assert d.allocation.satisfaction[1] == 1.0
