"""Unified two-population resource allocation with a protected human floor.

The public function accepts per-unit demands and per-unit weights.  Total
demands and weights are formed internally as ``D_ij = d_ij P_i`` and
``W_i = w_i P_i``.  The baseline allocation is weighted proportional fairness

    max sum_i W_i log(s_i)
    s.t. sum_i D_ij s_i <= S_j,  l_i <= s_i <= 1.

For two active populations the solver enumerates the exact KKT candidates of
the resulting polygon.  A numerical fallback exists only for more than two
active populations and is explicitly marked as regularized.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

try:
    from scipy.optimize import minimize
except Exception:
    minimize = None


@dataclass
class AllocationResult:
    satisfaction: np.ndarray
    allocations: np.ndarray
    utilization: np.ndarray
    slack: np.ndarray
    active_constraints: List[str]
    shadow_prices: np.ndarray
    shadow_prices_reliable: bool
    success: bool
    message: str
    regularized: bool = False
    epsilon: Optional[float] = None
    lower_bounds: Optional[np.ndarray] = None
    group_active: Optional[np.ndarray] = None
    max_resource_violation: float = 0.0
    metadata: Dict[str, object] = field(default_factory=dict)


def _as_1d(values: Sequence[float], name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    return arr


def _resource_scale(demands: np.ndarray, supplies: np.ndarray) -> np.ndarray:
    if demands.size == 0:
        return np.maximum(np.abs(supplies), 1e-12)
    return np.maximum.reduce(
        [
            np.abs(supplies),
            np.max(demands, axis=0),
            np.full(supplies.shape, 1e-12, dtype=float),
        ]
    )


def _feasible(
    s: np.ndarray,
    demands: np.ndarray,
    supplies: np.ndarray,
    lower: np.ndarray,
    scale: np.ndarray,
    tol: float,
) -> bool:
    if np.any(~np.isfinite(s)):
        return False
    if np.any(s < lower - tol) or np.any(s > 1.0 + tol):
        return False
    used = demands.T @ s
    return bool(np.all(used <= supplies + tol * scale))


def _repair_feasibility(
    s: np.ndarray,
    lower: np.ndarray,
    demands: np.ndarray,
    supplies: np.ndarray,
    scale: np.ndarray,
    tol: float,
) -> Tuple[np.ndarray, float]:
    used = demands.T @ s
    violation = float(np.max((used - supplies) / scale)) if supplies.size else 0.0
    if violation <= tol:
        return s, max(0.0, violation)

    direction = s - lower
    alpha = 1.0
    for j in range(supplies.size):
        base = float(demands[:, j] @ lower)
        slope = float(demands[:, j] @ direction)
        if slope > 0.0:
            alpha = min(alpha, max(0.0, (supplies[j] - base) / slope))
    alpha = min(1.0, max(0.0, alpha))

    lo, hi = 0.0, alpha
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        trial = lower + mid * direction
        trial_used = demands.T @ trial
        if np.all(trial_used <= supplies + 1e-15 * scale):
            lo = mid
        else:
            hi = mid
    repaired = lower + lo * direction
    repaired_used = demands.T @ repaired
    repaired_violation = (
        float(np.max((repaired_used - supplies) / scale)) if supplies.size else 0.0
    )
    return repaired, max(0.0, repaired_violation)


def _objective(s: np.ndarray, weights: np.ndarray) -> float:
    if np.any(s <= 0.0):
        return -np.inf
    return float(np.sum(weights * np.log(s)))


def _single_resource_solution(
    a: np.ndarray,
    supply: float,
    weights: np.ndarray,
    lower: np.ndarray,
    *,
    max_iter: int = 80,
) -> Optional[np.ndarray]:
    """Exact water-filling for one resource, robust to extreme scale separation.

    Returns None only when the lower bounds alone exceed the supply.
    """
    a = np.asarray(a, dtype=float)
    weights = np.asarray(weights, dtype=float)
    lower = np.asarray(lower, dtype=float)
    s = np.ones(2, dtype=float)
    positive = a > 0.0
    if not np.any(positive):
        return s
    weights = weights / np.max(weights[positive])
    if supply <= 0.0:
        s[positive] = 0.0
        if np.any(s < lower - 1e-12):
            return None
        return s
    if float(a @ np.ones(2)) <= supply:
        return np.ones(2)
    if float(a @ lower) > supply * (1.0 + 1e-12) + 1e-300:
        return None

    active_weight = float(np.sum(weights[a > 0.0]))
    if active_weight > 0.0:
        interior = np.ones(2, dtype=float)
        valid = True
        for i in range(2):
            if a[i] > 0.0:
                interior[i] = supply * float(weights[i]) / (a[i] * active_weight)
                if interior[i] > 1.0 + 1e-12 or interior[i] < lower[i] - 1e-12:
                    valid = False
                    break
        if valid:
            return np.clip(interior, lower, 1.0)

    def allocation(lam: float) -> np.ndarray:
        out = np.ones(2, dtype=float)
        for i in range(2):
            if a[i] > 0.0:
                out[i] = min(1.0, max(float(lower[i]), float(weights[i]) / (lam * a[i])))
        return out

    lam_lo = 0.0
    lam_hi = 1.0
    while float(a @ allocation(lam_hi)) > supply:
        lam_hi *= 2.0
        if lam_hi > 1e300:
            break
    for _ in range(max_iter):
        mid = 0.5 * (lam_lo + lam_hi)
        if float(a @ allocation(mid)) > supply:
            lam_lo = mid
        else:
            lam_hi = mid
    return allocation(lam_hi)


def _solve_two_group_exact(
    demands: np.ndarray,
    supplies: np.ndarray,
    weights: np.ndarray,
    lower: np.ndarray,
    scale: np.ndarray,
    tol: float,
) -> Tuple[np.ndarray, str]:
    for j in range(supplies.size):
        if demands[0, j] > 0.0 or demands[1, j] > 0.0:
            relaxed = _single_resource_solution(
                demands[:, j], float(supplies[j]), weights, lower
            )
            if relaxed is not None and _feasible(
                relaxed, demands, supplies, lower, scale, 1e-10
            ):
                return relaxed, "single_resource_relaxation"

    constraints: List[Tuple[float, float, float, str]] = []
    for j in range(supplies.size):
        if demands[0, j] > 0.0 or demands[1, j] > 0.0:
            constraints.append(
                (float(demands[0, j]), float(demands[1, j]), float(supplies[j]), f"resource_{j}")
            )
    constraints.append((1.0, 0.0, 1.0, "upper_0"))
    constraints.append((0.0, 1.0, 1.0, "upper_1"))
    constraints.append((-1.0, 0.0, -float(lower[0]), "lower_0"))
    constraints.append((0.0, -1.0, -float(lower[1]), "lower_1"))

    candidates: List[np.ndarray] = []

    for a in range(len(constraints)):
        a1, a2, b, _ = constraints[a]
        for c in range(a + 1, len(constraints)):
            c1, c2, d, _ = constraints[c]
            det = a1 * c2 - a2 * c1
            if abs(det) <= 1e-14:
                continue
            s0 = (b * c2 - a2 * d) / det
            s1 = (a1 * d - b * c1) / det
            candidate = np.array([s0, s1], dtype=float)
            if _feasible(candidate, demands, supplies, lower, scale, 1e-9):
                if np.all(candidate > 0.0):
                    candidates.append(candidate)

    for j in range(supplies.size):
        a1 = float(demands[0, j])
        a2 = float(demands[1, j])
        if a1 > 0.0 and a2 > 0.0:
            total = float(weights[0] + weights[1])
            candidate = np.array(
                [
                    float(weights[0]) * float(supplies[j]) / (a1 * total),
                    float(weights[1]) * float(supplies[j]) / (a2 * total),
                ],
                dtype=float,
            )
            if _feasible(candidate, demands, supplies, lower, scale, 1e-9):
                if np.all(candidate > 0.0):
                    candidates.append(candidate)

    if not candidates:
        raise RuntimeError("two-group exact solver found no feasible candidate")

    best = max(candidates, key=lambda x: _objective(x, weights))
    return best, "exact_polygon"


def _solve_generic(
    demands: np.ndarray,
    supplies: np.ndarray,
    weights: np.ndarray,
    lower: np.ndarray,
    scale: np.ndarray,
    tol: float,
) -> Tuple[np.ndarray, str, float]:
    if minimize is None:
        raise RuntimeError("scipy is required for the generic allocation fallback")
    n = demands.shape[0]
    epsilon = 1e-12
    floor = np.maximum(lower, epsilon)

    def objective(x: np.ndarray) -> float:
        return float(-np.sum(weights * np.log(x + epsilon)))

    def gradient(x: np.ndarray) -> np.ndarray:
        return -weights / (x + epsilon)

    constraints = [
        {
            "type": "ineq",
            "fun": lambda x: supplies - demands.T @ x,
            "jac": lambda x: -demands.T,
        }
    ]
    bounds = [(float(floor[i]), 1.0) for i in range(n)]
    x0 = np.clip(0.5 * (floor + 1.0), floor, 1.0)
    result = minimize(
        objective,
        x0,
        jac=gradient,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"ftol": 1e-13, "maxiter": 1000, "disp": False},
    )
    if not result.success:
        raise RuntimeError(f"generic allocator failed: {result.message}")
    s = np.asarray(result.x, dtype=float)
    s = np.clip(s, lower, 1.0)
    return s, "generic_slsqp", epsilon


def _active_constraints(
    s: np.ndarray,
    demands: np.ndarray,
    supplies: np.ndarray,
    lower: np.ndarray,
    scale: np.ndarray,
    tol: float,
    active_group: np.ndarray,
    forced_zero: np.ndarray,
) -> List[str]:
    names: List[str] = []
    used = demands.T @ s
    for j in range(supplies.size):
        if supplies[j] > 0.0 and supplies[j] - used[j] <= tol * scale[j]:
            names.append(f"resource_{j}")
        elif supplies[j] <= 0.0 and used[j] > 0.0:
            names.append(f"resource_{j}_violated")
    for i in range(s.shape[0]):
        if not active_group[i]:
            continue
        if s[i] >= 1.0 - tol:
            names.append(f"upper_{i}")
        if s[i] <= lower[i] + tol:
            names.append(f"lower_{i}")
        if forced_zero[i]:
            names.append(f"forced_zero_{i}")
    return names


def _recover_shadow_prices(
    s: np.ndarray,
    demands: np.ndarray,
    supplies: np.ndarray,
    weights: np.ndarray,
    lower: np.ndarray,
    active_group: np.ndarray,
    active_resources: List[int],
    tol: float,
) -> Tuple[np.ndarray, bool]:
    m = supplies.size
    shadow = np.zeros(m, dtype=float)

    def unreliable():
        return np.full(m, np.nan, dtype=float), False

    if not active_resources:
        return shadow, True

    idx = [i for i in range(s.shape[0]) if active_group[i]]
    interior: List[int] = []
    upper: List[int] = []
    lower_active: List[int] = []
    for i in idx:
        if s[i] >= 1.0 - tol:
            upper.append(i)
        elif s[i] <= lower[i] + tol:
            lower_active.append(i)
        else:
            interior.append(i)

    k = len(active_resources)

    if len(interior) == 2:
        A = demands[np.ix_(interior, active_resources)]
        rhs = np.array([weights[i] / s[i] for i in interior], dtype=float)
        sol, residuals, rank, _ = np.linalg.lstsq(A, rhs, rcond=None)
        if rank != k:
            return unreliable()
        residual_norm = float(np.linalg.norm(A @ sol - rhs))
        if residual_norm > 1e-7 * max(1.0, float(np.linalg.norm(rhs))):
            return unreliable()
        if np.any(sol < -1e-9):
            return unreliable()
        shadow[active_resources] = np.maximum(sol, 0.0)
        return shadow, True

    if len(interior) == 1 and k == 1:
        i = interior[0]
        j = active_resources[0]
        if demands[i, j] <= 0.0:
            return unreliable()
        lam = float(weights[i] / s[i] / demands[i, j])
        if lam < -1e-9:
            return unreliable()
        lam = max(lam, 0.0)
        for q in upper:
            lhs = lam * float(demands[q, j])
            if lhs > float(weights[q] / s[q]) + 1e-7:
                return unreliable()
        for q in lower_active:
            lhs = lam * float(demands[q, j])
            if lhs < float(weights[q] / s[q]) - 1e-7:
                return unreliable()
        shadow[j] = lam
        return shadow, True

    if len(interior) == 0 and len(upper) > 0 and len(lower_active) == 0:
        return unreliable()

    return unreliable()


def allocate_resources(
    populations: Sequence[float],
    per_unit_demands: Sequence[Sequence[float]],
    supplies: Sequence[float],
    per_unit_weights: Sequence[float],
    alignment: float = 0.0,
    human_index: int = 0,
    *,
    tol: float = 1e-10,
    allow_generic: bool = True,
) -> AllocationResult:
    """Allocate m resources between n populations under weighted fairness.

    Parameters
    ----------
    populations : array_like, shape (n,)
        Population sizes.  Zero-population groups are inactive.
    per_unit_demands : array_like, shape (n, m)
        Resource requirement per population unit.  The totals are formed as
        ``demands[i, j] * populations[i]``.
    supplies : array_like, shape (m,)
        Available resource supply in that resource's own unit.
    per_unit_weights : array_like, shape (n,)
        Resource-acquisition weight per population unit.
    alignment : float
        Protection level in [0, 1] for the human group.
    human_index : int
        Index of the human group whose lower bound is ``alignment * b_H``.
    """
    P = _as_1d(populations, "populations")
    S = _as_1d(supplies, "supplies")
    w = _as_1d(per_unit_weights, "per_unit_weights")
    d = np.asarray(per_unit_demands, dtype=float)
    if d.ndim != 2:
        raise ValueError("per_unit_demands must be a two-dimensional array")
    if d.shape != (P.size, S.size):
        raise ValueError("per_unit_demands must have shape (n_groups, n_resources)")
    if not np.all(np.isfinite(d)):
        raise ValueError("per_unit_demands must be finite")
    if np.any(P < 0.0):
        raise ValueError("populations must be nonnegative")
    if np.any(S < 0.0):
        raise ValueError("supplies must be nonnegative")
    if np.any(d < 0.0):
        raise ValueError("per_unit_demands must be nonnegative")
    if np.any(w < 0.0):
        raise ValueError("per_unit_weights must be nonnegative")
    if not (0.0 <= alignment <= 1.0):
        raise ValueError("alignment must lie in [0, 1]")
    if not (0 <= human_index < P.size):
        raise ValueError("human_index is out of range")

    n, m = d.shape
    D_raw = d * P[:, None]
    W = w * P
    active = P > 0.0
    if np.any(w[active] <= 0.0):
        raise ValueError("active populations require strictly positive weights")

    resource_scale = _resource_scale(D_raw, S)
    D = D_raw / resource_scale
    Sn = S / resource_scale

    b_H = 1.0
    if P[human_index] > 0.0:
        for j in range(m):
            if D[human_index, j] > 0.0:
                if Sn[j] <= 0.0:
                    b_H = 0.0
                    break
                b_H = min(b_H, float(Sn[j] / D[human_index, j]))
    b_H = float(np.clip(b_H, 0.0, 1.0))
    lower = np.zeros(n, dtype=float)
    if P[human_index] > 0.0:
        lower[human_index] = alignment * b_H

    s = np.ones(n, dtype=float)
    s[active] = 0.0
    forced_zero = np.zeros(n, dtype=bool)

    remaining = [i for i in range(n) if active[i]]
    for i in list(remaining):
        if np.any((D[i] > 0.0) & (Sn <= 0.0)):
            forced_zero[i] = True
            s[i] = 0.0
            remaining.remove(i)
            if lower[i] > 0.0:
                used_raw = D_raw * s[:, None]
                return AllocationResult(
                    satisfaction=s,
                    allocations=used_raw,
                    utilization=np.full(m, np.nan),
                    slack=S.copy(),
                    active_constraints=[],
                    shadow_prices=np.full(m, np.nan),
                    shadow_prices_reliable=False,
                    success=False,
                    message="infeasible lower bound on a zero-supply resource",
                    lower_bounds=lower,
                    group_active=active,
                )

    scale = _resource_scale(D, Sn)

    while remaining:
        demand_remaining = D[remaining]
        lower_remaining = lower[remaining]
        residual = Sn - demand_remaining.T @ lower_remaining
        newly_forced = []
        for i in remaining:
            if lower[i] > 0.0:
                continue
            positive_demands = D[i] > 0.0
            if np.any(positive_demands & (residual <= 0.0)):
                newly_forced.append(i)
        if not newly_forced:
            break
        for i in newly_forced:
            forced_zero[i] = True
            s[i] = 0.0
            remaining.remove(i)

    message = "exact two-group allocation"
    regularized = False
    epsilon: Optional[float] = None

    if remaining:
        D_rem = D[remaining]
        W_rem = W[remaining]
        lower_rem = lower[remaining]

        if len(remaining) == 1:
            i = remaining[0]
            caps = []
            for j in range(m):
                if D[i, j] > 0.0:
                    caps.append(float(Sn[j] / D[i, j]))
            cap = min([1.0] + caps)
            s_i = max(float(lower[i]), min(1.0, cap))
            s_rem = np.array([s_i], dtype=float)
            message = "single remaining group at maximum feasible satisfaction"
        elif len(remaining) == 2:
            s_rem, message = _solve_two_group_exact(
                D_rem, Sn, W_rem, lower_rem, scale, tol
            )
        else:
            if not allow_generic:
                raise ValueError("more than two active groups requires allow_generic=True")
            s_rem, message, epsilon = _solve_generic(
                D_rem, Sn, W_rem, lower_rem, scale, tol
            )
            regularized = True

        for pos, i in enumerate(remaining):
            s[i] = float(np.clip(s_rem[pos], lower[i], 1.0))

    for i in range(n):
        if not active[i]:
            s[i] = 1.0

    s, repaired_violation = _repair_feasibility(s, lower, D, Sn, scale, 1e-12)

    used = D_raw * s[:, None]
    slack = S - used.sum(axis=0)
    utilization = np.full(m, np.nan, dtype=float)
    for j in range(m):
        if S[j] > 0.0:
            utilization[j] = float(used[:, j].sum() / S[j])

    slack_normalized = Sn - D.T @ s
    active_resources = [
        j for j in range(m) if Sn[j] > 0.0 and slack_normalized[j] <= 1e-9 * scale[j]
    ]
    active_names = _active_constraints(
        s, D, Sn, lower, scale, 1e-9, active, forced_zero
    )
    shadow_normalized, reliable = _recover_shadow_prices(
        s, D, Sn, W, lower, active, active_resources, 1e-8
    )
    if reliable:
        shadow = shadow_normalized / resource_scale
    else:
        shadow = np.full(m, np.nan, dtype=float)
    max_violation = (
        float(np.max((used.sum(axis=0) - S) / resource_scale)) if m else 0.0
    )
    resource_ok = bool(
        np.all(used.sum(axis=0) <= S + 1e-8 * resource_scale)
        if m
        else True
    )
    success = bool(
        np.all(np.isfinite(s))
        and np.all(s >= -1e-12)
        and np.all(s <= 1.0 + 1e-12)
        and resource_ok
    )
    return AllocationResult(
        satisfaction=s,
        allocations=used,
        utilization=utilization,
        slack=slack,
        active_constraints=active_names,
        shadow_prices=shadow,
        shadow_prices_reliable=reliable,
        success=success,
        message=message,
        regularized=regularized,
        epsilon=epsilon,
        lower_bounds=lower,
        group_active=active,
        max_resource_violation=max(0.0, max_violation, repaired_violation),
        metadata={
            "b_H": b_H,
            "active_resources": active_resources,
            "forced_zero": forced_zero.copy(),
        },
    )


def allocate_resources_priority(
    populations: Sequence[float],
    per_unit_demands: Sequence[Sequence[float]],
    supplies: Sequence[float],
    per_unit_weights: Sequence[float],
    alignment: float = 0.0,
    human_index: int = 0,
    *,
    tol: float = 1e-10,
) -> AllocationResult:
    """AI-first priority stress test with the same floor and conservation rules.

    This is not the baseline allocator.  It sets the human group at its floor,
    gives the AI group the maximum feasible residual, and then gives the human
    group any additional feasible residual.  Shadow prices are not reported
    because this rule is not the proportional-fairness optimum.
    """
    P = _as_1d(populations, "populations")
    S = _as_1d(supplies, "supplies")
    w = _as_1d(per_unit_weights, "per_unit_weights")
    d = np.asarray(per_unit_demands, dtype=float)
    if d.ndim != 2:
        raise ValueError("per_unit_demands must be a two-dimensional array")
    if d.shape != (P.size, S.size):
        raise ValueError("per_unit_demands must have shape (n_groups, n_resources)")
    if P.size != 2:
        raise ValueError("priority stress test is implemented for two groups")
    if not np.all(np.isfinite(d)):
        raise ValueError("per_unit_demands must be finite")
    if np.any(P < 0.0) or np.any(S < 0.0) or np.any(d < 0.0) or np.any(w < 0.0):
        raise ValueError("populations, supplies, demands and weights must be nonnegative")
    if not (0.0 <= alignment <= 1.0):
        raise ValueError("alignment must lie in [0, 1]")
    if not (0 <= human_index < P.size):
        raise ValueError("human_index is out of range")

    n, m = d.shape
    D_raw = d * P[:, None]
    W = w * P
    active = P > 0.0
    if np.any(w[active] <= 0.0):
        raise ValueError("active populations require strictly positive weights")
    resource_scale = _resource_scale(D_raw, S)
    D = D_raw / resource_scale
    Sn = S / resource_scale

    b_H = 1.0
    if P[human_index] > 0.0:
        for j in range(m):
            if D[human_index, j] > 0.0:
                if Sn[j] <= 0.0:
                    b_H = 0.0
                    break
                b_H = min(b_H, float(Sn[j] / D[human_index, j]))
    b_H = float(np.clip(b_H, 0.0, 1.0))
    lower = np.zeros(n, dtype=float)
    if P[human_index] > 0.0:
        lower[human_index] = alignment * b_H

    s = np.ones(n, dtype=float)
    forced_zero = np.zeros(n, dtype=bool)
    ai_index = 1 - human_index

    if P[human_index] > 0.0:
        s[human_index] = lower[human_index]
    if P[ai_index] <= 0.0:
        s[ai_index] = 1.0
        if P[human_index] > 0.0:
            caps = []
            for j in range(m):
                if D[human_index, j] > 0.0:
                    caps.append(float(Sn[j] / D[human_index, j]))
            s[human_index] = max(
                lower[human_index], min([1.0] + caps)
            )
    else:
        residual = Sn - D[human_index] * s[human_index]
        caps_ai = []
        for j in range(m):
            if D[ai_index, j] > 0.0:
                if residual[j] <= 0.0:
                    caps_ai.append(0.0)
                else:
                    caps_ai.append(float(residual[j] / D[ai_index, j]))
        s[ai_index] = min([1.0] + caps_ai)
        if s[ai_index] <= 0.0:
            s[ai_index] = 0.0
            forced_zero[ai_index] = True
        residual_h = Sn - D[ai_index] * s[ai_index]
        caps_h = []
        for j in range(m):
            if D[human_index, j] > 0.0:
                caps_h.append(float(residual_h[j] / D[human_index, j]))
        s[human_index] = max(
            lower[human_index], min([1.0] + caps_h)
        )

    for i in range(n):
        if not active[i]:
            s[i] = 1.0

    s, repaired_violation = _repair_feasibility(s, lower, D, Sn, _resource_scale(D, Sn), 1e-12)
    used = D_raw * s[:, None]
    slack = S - used.sum(axis=0)
    utilization = np.full(m, np.nan, dtype=float)
    for j in range(m):
        if S[j] > 0.0:
            utilization[j] = float(used[:, j].sum() / S[j])
    active_names = _active_constraints(
        s, D, Sn, lower, _resource_scale(D, Sn), 1e-9, active, forced_zero
    )
    max_violation = (
        float(np.max((used.sum(axis=0) - S) / resource_scale)) if m else 0.0
    )
    resource_ok = bool(
        np.all(used.sum(axis=0) <= S + 1e-8 * resource_scale)
        if m
        else True
    )
    success = bool(
        np.all(np.isfinite(s))
        and np.all(s >= -1e-12)
        and np.all(s <= 1.0 + 1e-12)
        and resource_ok
    )
    return AllocationResult(
        satisfaction=s,
        allocations=used,
        utilization=utilization,
        slack=slack,
        active_constraints=active_names,
        shadow_prices=np.full(m, np.nan),
        shadow_prices_reliable=False,
        success=success,
        message="AI-first priority stress test",
        lower_bounds=lower,
        group_active=active,
        max_resource_violation=max(0.0, max_violation, repaired_violation),
        metadata={"b_H": b_H, "forced_zero": forced_zero.copy()},
    )
