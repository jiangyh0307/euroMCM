import numpy as np
import pytest

from alpha.rsi import RSIParameters, rsi_diagnostics, simulate_rsi
from alpha.scenarios import scenario_stress


def test_rsi_domain_and_energy_conservation():
    p = RSIParameters()
    sim = simulate_rsi(p, alignment=0.5, dt_internal=1.0)
    assert sim.success
    assert np.all(sim.H > 0)
    assert np.all(sim.A >= 0)
    assert np.all(sim.q > 0)
    assert np.all(sim.q <= p.q_max * (1 + 1e-8))
    assert np.all(sim.A <= p.A_max * (1 + 1e-8))
    assert np.all(sim.s_H >= 0) and np.all(sim.s_H <= 1)
    assert np.all(sim.s_A >= 0) and np.all(sim.s_A <= 1)
    assert np.all(sim.E_human_allocated + sim.E_AI_allocated <= sim.E_op + 1e-6 * np.maximum(1, sim.E_op))
    assert np.all(p.c_build * sim.B <= sim.R_build + 1e-6 * np.maximum(1, sim.R_build))
    assert np.all(sim.B <= sim.B_manufacturing + 1e-8)
    assert np.all(sim.A * p.ell_site <= p.L_site + 1e-6)


def test_efficiency_expansion_identity():
    p = RSIParameters()
    for q in [1.0, 5.0, 20.0]:
        for A in [1.0e3, 1.0e4, 1.0e5]:
            d = rsi_diagnostics(p, p.H0, A, q, alignment=0.5)
            expected = d.dA / A - p.xi * d.dq / q
            assert np.isclose(d.E_AI_demand_log_derivative, expected, rtol=1e-12, atol=1e-12)


def test_industrial_self_sufficiency_threshold():
    p = RSIParameters(c_A=0.5, delta_A=0.05, q_c=10.0, nu=2.0)
    qs = p.q_self()
    assert np.isclose(qs, 10.0 * (0.05 / 0.45) ** 0.5)
    for q in [0.5 * qs, qs, 2.0 * qs]:
        lhs = p.c_A * p.zeta(q)
        if q < qs:
            assert lhs < p.delta_A
        elif q > qs:
            assert lhs > p.delta_A
        else:
            assert np.isclose(lhs, p.delta_A, rtol=1e-12)
    p2 = RSIParameters(c_A=0.05, delta_A=0.05)
    assert np.isnan(p2.q_self())


def test_alignment_endpoint_consistency():
    p = RSIParameters(E_total=8.0e9, H0=8.0e9, L_service=2.0e6)
    d0 = rsi_diagnostics(p, p.H0, p.A0, p.q0, alignment=0.0)
    d1 = rsi_diagnostics(p, p.H0, p.A0, p.q0, alignment=1.0)
    assert d1.E_op >= d1.b_H_tot * p.e_H * p.H0 - 1e-6
    assert d1.allocation.satisfaction[0] >= d0.allocation.satisfaction[0] - 1e-12
    assert d1.R_build <= 0.1 * p.E_total + 1e-6


def test_stress_extinction_and_viability_threshold():
    p = scenario_stress()
    sim0 = simulate_rsi(p, alignment=0.0, dt_internal=1.0)
    assert sim0.outcome == "extinction"
    assert sim0.extinction_time > 0
    sim1 = simulate_rsi(p, alignment=0.6, dt_internal=1.0)
    assert sim1.min_H >= p.H_min
    assert sim1.outcome in {"marginal", "non_marginal"}


def test_rsi_dt_convergence():
    p = RSIParameters()
    s1 = simulate_rsi(p, alignment=0.5, integrator="rk4", dt_internal=1.0)
    s2 = simulate_rsi(p, alignment=0.5, integrator="rk4", dt_internal=0.5)
    assert s1.outcome == s2.outcome
    assert abs(s1.H[-1] - s2.H[-1]) / max(s2.H[-1], 1.0) < 1e-5
    assert abs(s1.A[-1] - s2.A[-1]) / max(s2.A[-1], 1.0) < 1e-5


def test_non_saturating_growth_is_finite_and_uncapped():
    p = RSIParameters(growth_mode="non_saturating", T=20.0)
    sim = simulate_rsi(p, alignment=0.5, dt_internal=0.5)
    assert np.all(np.isfinite(sim.q))
    assert sim.q[-1] > sim.q[0]
    p2 = RSIParameters(growth_mode="non_saturating", eta=1.0, T=10.0, A0=1.0e5)
    sim2 = simulate_rsi(p2, alignment=0.5, dt_internal=0.5)
    assert np.all(np.isfinite(sim2.q))
    assert sim2.q[-1] > p2.q_max


def test_fixed_construction_budget_can_undermine_a1_endpoint():
    from dataclasses import replace

    p = RSIParameters(E_total=8.0e9, H0=8.0e9, L_service=2.0e6)
    p_fixed = replace(p, budget_policy="fixed")
    d1 = rsi_diagnostics(p, p.H0, p.A0, p.q0, alignment=1.0)
    d_fixed = rsi_diagnostics(p_fixed, p.H0, p.A0, p.q0, alignment=1.0)
    assert d1.E_op >= p.e_H * p.H0 - 1e-6
    assert d_fixed.E_op < p.e_H * p.H0
    assert d1.allocation.satisfaction[0] >= 1.0 - 1e-12
    assert d_fixed.allocation.satisfaction[0] < 1.0


def test_rk4_matches_solve_ivp_on_previously_chattering_case():
    p = RSIParameters(
        L_service=2.0e6,
        E_total=8.0e9,
        e0=20000.0,
        xi=0.0,
        omega=1.0,
        w_A0=10.0,
        q_max=100.0,
        eta=0.5,
        q_c=5.0,
        M_max=1.0e6,
        c_A=1.0,
        r0=0.5,
        A_c=1.0e4,
    )
    s1 = simulate_rsi(p, alignment=0.0, integrator="rk4", dt_internal=0.5)
    s2 = simulate_rsi(
        p, alignment=0.0, integrator="solve_ivp", rtol=1e-6, atol=1e-8, max_step=2.0
    )
    assert s1.outcome == s2.outcome
    assert abs(s1.H[-1] - s2.H[-1]) / max(s2.H[-1], 1.0) < 1e-5
    assert abs(s1.A[-1] - s2.A[-1]) / max(s2.A[-1], 1e-20) < 1e-4
