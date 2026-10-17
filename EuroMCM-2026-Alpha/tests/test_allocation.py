import warnings

import numpy as np
import pytest
from scipy.optimize import minimize

from alpha.allocation import allocate_resources


def _b_H(P, d, S, human=0):
    D = d * P[:, None]
    b = 1.0
    for j in range(len(S)):
        if D[human, j] > 0:
            if S[j] <= 0:
                return 0.0
            b = min(b, S[j] / D[human, j])
    return min(1.0, max(0.0, b))


def _reference(P, d, S, w, a, human=0, eps=1e-12):
    P = np.asarray(P, float)
    d = np.asarray(d, float)
    S = np.asarray(S, float)
    w = np.asarray(w, float)
    D = d * P[:, None]
    W = w * P
    scale = np.maximum(S, 1e-12)
    l = np.zeros(len(P))
    l[human] = a * _b_H(P, d, S, human)
    n = len(P)
    Wn = W / max(float(W.max()), 1e-300)

    def obj(x):
        return -float(np.sum(Wn * np.log(x + eps)))

    def jac(x):
        return -Wn / (x + eps)

    cons = [{"type": "ineq", "fun": lambda x: 1.0 - (D.T @ x) / scale,
             "jac": lambda x: -(D.T) / scale[:, None]}]
    bounds = [(max(float(l[i]), 0.0), 1.0) for i in range(n)]
    best = None
    for frac in (0.5, 0.1, 0.9, 0.01):
        x0 = np.clip(l + frac * (1.0 - l), l, 1.0)
        res = minimize(obj, x0, jac=jac, method="SLSQP", bounds=bounds,
                       constraints=cons, options={"ftol": 1e-12, "maxiter": 2000})
        if res.success:
            if best is None or res.fun < best.fun:
                best = res
    if best is None:
        return None
    return np.clip(best.x, l, 1.0)


def test_single_resource_analytic():
    rng = np.random.default_rng(1)
    for _ in range(100):
        P = rng.uniform(0.1, 100, 2)
        w = rng.uniform(0.1, 5, 2)
        d = rng.uniform(0.1, 10, 2)
        S = rng.uniform(0.01, 0.9 * (d[0] * P[0] + d[1] * P[1]))
        res = allocate_resources(P, d.reshape(2, 1), [S], w, alignment=0.0)
        expected = S * w / (d * (w[0] * P[0] + w[1] * P[1]))
        if np.all(expected < 1.0):
            assert res.success
            assert np.allclose(res.satisfaction, expected, rtol=1e-10, atol=1e-12)
            assert res.shadow_prices_reliable
            assert np.isclose(res.shadow_prices[0], (w[0] * P[0] + w[1] * P[1]) / S)
        else:
            D = d * P
            if S >= D.sum():
                expected_capped = np.ones(2)
            else:
                lam_lo, lam_hi = 0.0, 1.0
                while float(D @ np.minimum(1.0, (w * P) / (lam_hi * D))) > S:
                    lam_hi *= 2.0
                for _ in range(200):
                    mid = 0.5 * (lam_lo + lam_hi)
                    trial = np.minimum(1.0, (w * P) / (mid * D))
                    if float(D @ trial) > S:
                        lam_lo = mid
                    else:
                        lam_hi = mid
                expected_capped = np.minimum(1.0, (w * P) / (lam_hi * D))
            assert np.allclose(res.satisfaction, expected_capped, rtol=1e-8, atol=1e-10)


def test_abundant_supply():
    res = allocate_resources([2.0, 3.0], [[1.0, 0.5], [0.2, 2.0]], [100.0, 100.0], [1.0, 1.0])
    assert res.success
    assert np.allclose(res.satisfaction, 1.0)
    assert np.all(res.slack > 0.0)
    assert np.allclose(res.shadow_prices, 0.0)
    assert res.shadow_prices_reliable


def test_alignment_zero_and_one():
    P = [1.0, 1.0]
    d = [[1.0], [1.0]]
    S = [0.4]
    w = [1.0, 1.0]
    r0 = allocate_resources(P, d, S, w, alignment=0.0)
    assert np.allclose(r0.satisfaction, [0.2, 0.2])
    r1 = allocate_resources(P, d, S, w, alignment=1.0)
    assert np.allclose(r1.satisfaction, [0.4, 0.0])


def test_alignment_one_human_maximum_with_residual():
    res = allocate_resources(
        [1.0, 1.0], [[1.0, 0.5], [0.0, 1.0]], [1.0, 1.0], [1.0, 1.0], alignment=1.0
    )
    assert np.allclose(res.satisfaction, [1.0, 0.5])
    assert np.allclose(res.allocations, [[1.0, 0.5], [0.0, 0.5]])


def test_alignment_one_forced_zero():
    res = allocate_resources(
        [1.0, 1.0], [[1.0, 1.0], [1.0, 0.0]], [1.0, 1.0], [1.0, 1.0], alignment=1.0
    )
    assert res.success
    assert np.allclose(res.satisfaction, [1.0, 0.0])
    assert np.allclose(res.allocations[1], 0.0)
    assert any("forced_zero_1" in name for name in res.active_constraints)


def test_zero_population():
    res = allocate_resources(
        [0.0, 5.0], [[1.0], [1.0]], [2.0], [1.0, 1.0], alignment=1.0
    )
    assert res.success
    assert res.satisfaction[0] == 1.0
    assert np.allclose(res.allocations[0], 0.0)
    assert np.all(np.isfinite(res.satisfaction))
    assert np.allclose(res.satisfaction[1], 0.4)


def test_zero_supply_forced_zero():
    res = allocate_resources([1.0, 1.0], [[1.0], [1.0]], [0.0], [1.0, 1.0])
    assert res.success
    assert np.allclose(res.satisfaction, 0.0)
    assert np.allclose(res.allocations, 0.0)
    assert np.isnan(res.utilization[0])
    assert res.slack[0] == 0.0


def test_zero_demand_group():
    res = allocate_resources([1.0, 1.0], [[1.0], [0.0]], [0.5], [1.0, 1.0])
    assert res.success
    assert res.satisfaction[0] == 0.5
    assert res.satisfaction[1] == 1.0
    assert np.allclose(res.allocations[1], 0.0)


def test_two_binding_resources():
    res = allocate_resources([1.0, 1.0], [[2.0, 1.0], [1.0, 2.0]], [1.0, 1.0], [1.0, 1.0])
    assert res.success
    assert np.allclose(res.satisfaction, [1.0 / 3.0, 1.0 / 3.0], atol=1e-12)
    assert res.shadow_prices_reliable
    assert np.allclose(res.shadow_prices, [1.0, 1.0], atol=1e-10)
    assert len([n for n in res.active_constraints if n.startswith("resource_")]) == 2


def test_cap_and_lower_bound():
    res = allocate_resources([1.0, 1.0], [[1.0], [10.0]], [5.0], [1.0, 1.0])
    assert res.success
    assert np.allclose(res.satisfaction, [1.0, 0.4], atol=1e-12)

    res_floor = allocate_resources([1.0, 1.0], [[1.0], [1.0]], [1.0], [0.1, 10.0], alignment=0.5)
    assert res_floor.success
    assert np.allclose(res_floor.satisfaction, [0.5, 0.5], atol=1e-10)


def test_unit_scaling_invariance():
    rng = np.random.default_rng(7)
    for _ in range(20):
        P = rng.uniform(1.0, 10.0, 2)
        d = rng.uniform(0.1, 3.0, (2, 2))
        S = rng.uniform(0.1, 5.0, 2)
        w = rng.uniform(0.1, 3.0, 2)
        a = float(rng.choice([0.0, 0.3, 0.9]))
        base = allocate_resources(P, d, S, w, alignment=a)
        c = 3.7
        scaled = allocate_resources(c * P, d, c * S, w, alignment=a)
        assert np.allclose(base.satisfaction, scaled.satisfaction, atol=1e-9)
        weight_scaled = allocate_resources(P, d, S, 5.0 * w, alignment=a)
        assert np.allclose(base.satisfaction, weight_scaled.satisfaction, atol=1e-9)


def test_redundant_constraint():
    res = allocate_resources(
        [1.0, 1.0], [[1.0, 1.0], [1.0, 1.0]], [1.0, 1.0], [1.0, 1.0]
    )
    assert res.success
    assert np.allclose(res.satisfaction, [0.5, 0.5])
    assert np.all(res.allocations.sum(axis=0) <= np.array([1.0, 1.0]) + 1e-12)


def test_tiny_population():
    res = allocate_resources([1e-14, 1.0], [[1.0], [1.0]], [0.5], [1.0, 1.0])
    assert res.success
    assert np.all(np.isfinite(res.satisfaction))
    assert np.all(res.satisfaction >= 0.0)
    assert np.all(res.satisfaction <= 1.0)
    assert np.all(res.allocations.sum(axis=0) <= np.array([0.5]) + 1e-12)


def test_random_feasibility_and_reference_objective():
    rng = np.random.default_rng(2026)
    for _ in range(200):
        m = int(rng.integers(1, 4))
        P = rng.uniform(0.05, 20.0, 2)
        d = rng.uniform(0.0, 5.0, (2, m))
        S = rng.uniform(0.0, 20.0, m)
        w = rng.uniform(0.1, 5.0, 2)
        a = float(rng.choice([0.0, 0.2, 0.5, 0.8, 1.0]))
        res = allocate_resources(P, d, S, w, alignment=a)
        assert res.success
        assert np.all(res.satisfaction >= 0.0)
        assert np.all(res.satisfaction <= 1.0 + 1e-12)
        D = d * P[:, None]
        used = D * res.satisfaction[:, None]
        assert np.all(used.sum(axis=0) <= S + 1e-8 * np.maximum(1.0, S))

        if np.all(res.satisfaction > 1e-3):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                ref = _reference(P, d, S, w, a)
            if ref is not None:
                D = d * P[:, None]
                W = w * P
                obj_exact = float(np.sum(W * np.log(res.satisfaction)))
                obj_ref = float(np.sum(W * np.log(ref + 1e-12)))
                assert obj_exact >= obj_ref - 2e-4


def test_shadow_prices_kkt_interior():
    rng = np.random.default_rng(99)
    for _ in range(50):
        P = rng.uniform(1.0, 10.0, 2)
        d = rng.uniform(0.5, 4.0, (2, 2))
        S = rng.uniform(0.5, 3.0, 2)
        w = rng.uniform(0.5, 3.0, 2)
        res = allocate_resources(P, d, S, w)
        if not res.shadow_prices_reliable:
            continue
        if np.any(res.satisfaction <= 0) or np.any(res.satisfaction >= 1):
            continue
        D = d * P[:, None]
        W = w * P
        lhs = W / res.satisfaction
        rhs = D @ res.shadow_prices
        assert np.allclose(lhs, rhs, rtol=1e-6, atol=1e-7)


def test_generic_fallback_three_groups():
    res = allocate_resources(
        [1.0, 1.0, 1.0],
        [[1.0, 0.2], [0.5, 1.0], [0.3, 0.4]],
        [1.2, 1.0],
        [1.0, 1.0, 1.0],
        allow_generic=True,
    )
    assert res.success
    assert res.regularized
    assert np.all(res.satisfaction >= 0.0)
    assert np.all(res.satisfaction <= 1.0)
    used = np.asarray([[1.0, 0.2], [0.5, 1.0], [0.3, 0.4]]) * res.satisfaction[:, None]
    assert np.all(used.sum(axis=0) <= np.array([1.2, 1.0]) + 1e-8)


def test_tiny_population_matches_single_resource_formula():
    for p in [1e-8, 1e-14, 1e-20, 1e-40]:
        res = allocate_resources([p, 1.0], [[1.0], [1.0]], [0.5], [1.0, 1.0])
        expected = 0.5 / (1.0 + p)
        assert res.success
        assert np.allclose(res.satisfaction, [expected, expected], rtol=1e-12, atol=1e-15)


def test_two_binding_still_exact_after_relaxation_path():
    res = allocate_resources([1.0, 1.0], [[2.0, 1.0], [1.0, 2.0]], [1.0, 1.0], [1.0, 1.0])
    assert res.success
    assert np.allclose(res.satisfaction, [1.0 / 3.0, 1.0 / 3.0], atol=1e-12)
    assert res.message == "exact_polygon"
