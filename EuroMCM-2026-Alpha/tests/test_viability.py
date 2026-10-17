import numpy as np
import pytest

from alpha.rsi import RSIParameters, simulate_rsi
from alpha.scenarios import scenario_stress
from alpha.viability import (a_safe, b_under, delta_critical,
                             extinction_impossible_by_bound,
                             extinction_lower_bound, viability_certificate)


def test_b_under_analytic():
    assert b_under([10.0, 20.0], [1.0, 2.0], 2.0) == 1.0
    assert np.isclose(b_under([1.0, 20.0], [1.0, 2.0], 2.0), 0.5)
    assert b_under([0.0], [1.0], 2.0) == 0.0


def test_a_safe_analytic():
    assert np.isclose(a_safe(0.1, 0.2, 1.0), 0.5)
    assert np.isinf(a_safe(0.1, 0.0, 1.0))
    assert np.isinf(a_safe(0.1, 0.2, 0.0))


def test_base_certificate():
    p = RSIParameters()
    cert = viability_certificate(p)
    assert cert.feasible
    assert np.isclose(cert.a_safe, 0.5)


def test_stress_certificate_and_simulation():
    p = scenario_stress()
    cert = viability_certificate(p)
    assert cert.feasible
    assert np.isclose(cert.a_safe, 0.6)
    sim = simulate_rsi(p, alignment=cert.a_safe, dt_internal=1.0)
    assert sim.min_H >= p.H_min


def test_certificate_not_necessary():
    p = scenario_stress()
    sim = simulate_rsi(p, alignment=0.0, dt_internal=1.0)
    assert sim.outcome == "extinction"


def test_finite_horizon_population_bound():
    dc = delta_critical(8.0e9, 1.0e6, 100.0)
    assert np.isclose(dc, 0.08987196820661973)
    assert np.isclose(extinction_lower_bound(8.0e9, 0.01, 100), 2.9430355293715387e9)
    assert extinction_impossible_by_bound(8.0e9, 0.01, 1.0e6, 100)
    assert not extinction_impossible_by_bound(8.0e9, dc, 1.0e6, 100)
