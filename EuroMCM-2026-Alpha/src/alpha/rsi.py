"""Resource-constrained recursive self-improvement dynamics."""

from __future__ import annotations

from dataclasses import dataclass, replace, fields, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.integrate import solve_ivp

_trapz = getattr(np, "trapezoid", np.trapz)

from .allocation import (
    AllocationResult,
    allocate_resources,
    allocate_resources_priority,
)


@dataclass
class Intervention:
    """Piecewise-constant Part V policy.

    kind="none"    : no policy
    kind="protect" : resource-protection floor g=max(alignment,u_bar) for t>=tau
    kind="cap"     : new-installation cap C=cap_fraction*A_max for t>=tau
    """

    kind: str = "none"
    tau: float = 0.0
    u_bar: float = 0.0
    cap_fraction: float = 1.0
    tau_cap: Optional[float] = None
    shutdown_fraction: float = 1.0

    def validate(self) -> None:
        if self.kind not in {"none", "protect", "cap", "shutdown"}:
            raise ValueError("intervention kind must be none, protect or cap")
        if self.tau < 0:
            raise ValueError("intervention tau must be nonnegative")
        if not (0.0 <= self.u_bar <= 1.0):
            raise ValueError("u_bar must lie in [0,1]")
        if not (0.0 <= self.cap_fraction <= 1.0):
            raise ValueError("cap_fraction must lie in [0,1]")
        if self.tau_cap is not None and self.tau_cap <= 0:
            raise ValueError("tau_cap must be positive when supplied")
        if not (0.0 <= self.shutdown_fraction <= 1.0):
            raise ValueError("shutdown_fraction must lie in [0,1]")

    def effective_protection(self, t: float, alignment: float) -> float:
        if self.kind == "protect" and t >= self.tau:
            return max(alignment, self.u_bar)
        return alignment

    def cap_target(self, A_max: float) -> float:
        return self.cap_fraction * A_max

    def operating_fraction(self, t: float) -> float:
        if self.kind == "shutdown" and t >= self.tau:
            return max(0.0, 1.0 - self.shutdown_fraction)
        return 1.0

    def cap_rate(self, t: float, A: float, B0: float, params: "RSIParameters") -> float:
        if self.kind != "cap" or t < self.tau:
            return B0
        tau_cap = params.tau_build if self.tau_cap is None else self.tau_cap
        target = self.cap_target(params.A_max)
        return min(B0, max(0.0, target - A) / tau_cap)


@dataclass
class RSIParameters:
    beta_H: float = 0.02
    delta_H: float = 0.01
    e_H: float = 1.0
    ell_H: float = 1.0e-4
    e0: float = 10000.0
    xi: float = 0.2
    ell_A: float = 1.0e-4
    w_H: float = 1.0
    w_A0: float = 1.0
    omega: float = 0.2
    L_site: float = 100.0
    L_service: float = 2.0e6
    ell_site: float = 1.0e-4
    c_build: float = 5000.0
    rho: float = 0.1
    c_H: float = 10000.0
    c_A: float = 0.5
    H_ref: float = 8.0e9
    M_max: float = 1.0e5
    r0: float = 0.2
    gamma: float = 0.0
    tau_build: float = 2.0
    eta: float = 0.2
    A_c: float = 1.0e4
    q_max: float = 100.0
    q0: float = 1.0
    nu: float = 2.0
    q_c: float = 10.0
    delta_A: float = 0.05
    mu_A: float = 0.5
    E_total: float = 3.0e10
    A0: float = 1.0e4
    H0: float = 8.0e9
    T: float = 100.0
    dt: float = 0.5
    H_ext: float = 1.0e6
    H_min: float = 1.0e8
    s_min: float = 0.8
    W_window: float = 10.0
    p_tol: float = 0.0
    allocation_rule: str = "proportional"
    growth_mode: str = "saturating"
    budget_policy: str = "endpoint_consistent"
    manufacturing_mode: str = "substitutive"

    def validate(self) -> None:
        for item in fields(self):
            value = getattr(self, item.name)
            if isinstance(value, (float, int)) and not np.isfinite(value):
                raise ValueError(f"{item.name} must be finite")
        if self.xi < 0 or self.omega < 0:
            raise ValueError("xi and omega must be nonnegative")
        if self.beta_H <= 0:
            raise ValueError("beta_H must be positive")
        if self.delta_H < 0:
            raise ValueError("delta_H must be nonnegative")
        if self.e_H <= 0 or self.ell_H < 0:
            raise ValueError("human resource requirements must be positive/nonnegative")
        if self.e0 <= 0 or self.ell_A < 0:
            raise ValueError("AI resource requirements must be positive/nonnegative")
        if self.w_H <= 0 or self.w_A0 <= 0:
            raise ValueError("resource weights must be positive")
        if self.L_site < 0 or self.L_service < 0:
            raise ValueError("land supplies must be nonnegative")
        if self.ell_site <= 0:
            raise ValueError("ell_site must be positive")
        if self.c_build <= 0:
            raise ValueError("c_build must be positive")
        if not (0.0 <= self.rho <= 1.0):
            raise ValueError("rho must lie in [0, 1]")
        if self.c_H < 0 or self.c_A < 0 or self.M_max < 0:
            raise ValueError("production parameters must be nonnegative")
        if self.H_ref <= 0:
            raise ValueError("H_ref must be positive")
        if self.r0 < 0 or self.gamma < 0 or self.tau_build <= 0:
            raise ValueError("hardware expansion parameters are invalid")
        if self.eta < 0 or self.A_c <= 0:
            raise ValueError("RSI parameters are invalid")
        if self.q_max <= 0 or self.q0 <= 0:
            raise ValueError("capability parameters must be positive")
        if self.growth_mode == "saturating" and self.q0 > self.q_max:
            raise ValueError("q0 must not exceed q_max in the saturating model")
        if self.nu <= 0 or self.q_c <= 0:
            raise ValueError("automation parameters must be positive")
        if self.delta_A < 0 or self.mu_A < 0:
            raise ValueError("hardware retirement rates must be nonnegative")
        if self.E_total < 0:
            raise ValueError("E_total must be nonnegative")
        if self.A0 < 0 or self.H0 <= 0:
            raise ValueError("initial states are invalid")
        if self.A0 > self.A_max * (1.0 + 1e-12):
            raise ValueError("A0 exceeds the physical facility capacity")
        if self.T <= 0 or self.dt <= 0:
            raise ValueError("time horizon and output step must be positive")
        if not (0.0 < self.H_ext < self.H_min <= self.H0):
            raise ValueError("thresholds must satisfy 0 < H_ext < H_min <= H0")
        if not (0.0 < self.s_min <= 1.0):
            raise ValueError("s_min must lie in (0, 1]")
        if not (0.0 < self.W_window <= self.T):
            raise ValueError("W_window must lie in (0, T]")
        if not (0.0 <= self.p_tol < 1.0):
            raise ValueError("p_tol must lie in [0, 1)")
        if self.allocation_rule not in {"proportional", "priority"}:
            raise ValueError("unknown allocation rule")
        if self.growth_mode not in {"saturating", "non_saturating"}:
            raise ValueError("unknown growth mode")
        if self.budget_policy not in {"endpoint_consistent", "fixed"}:
            raise ValueError("unknown budget policy")
        if self.manufacturing_mode not in {"substitutive", "additive"}:
            raise ValueError("unknown manufacturing mode")

    @property
    def A_max(self) -> float:
        return self.L_site / self.ell_site

    def zeta(self, q: float) -> float:
        q = max(float(q), 0.0)
        return q ** self.nu / (q ** self.nu + self.q_c ** self.nu)

    def r_A(self, q: float) -> float:
        return self.r0 * max(float(q), 0.0) ** self.gamma

    def q_self(self) -> float:
        if self.c_A <= self.delta_A or self.delta_A <= 0.0:
            return float("nan")
        return self.q_c * (self.delta_A / (self.c_A - self.delta_A)) ** (1.0 / self.nu)


@dataclass
class RSIDiagnostics:
    allocation: AllocationResult
    b_H_tot: float
    R_build: float
    E_op: float
    manufacturing: float
    zeta: float
    B_desired: float
    B_manufacturing: float
    B_energy: float
    B_site: float
    B: float
    dH: float
    dA: float
    dq: float
    E_AI_demand: float
    E_AI_allocated: float
    E_human_allocated: float
    E_AI_demand_log_derivative: float
    B_before_policy: float = float("nan")
    protection_g: float = float("nan")
    intervention_kind: str = "none"
    operating_fraction: float = 1.0


def _budgets(params: RSIParameters, H: float, alignment: float) -> Tuple[float, float, float]:
    if H > 0.0:
        caps = [1.0, params.E_total / (params.e_H * H)]
        if params.ell_H > 0:
            caps.append(params.L_service / (params.ell_H * H))
        b_H_tot = min(caps)
    else:
        b_H_tot = 1.0
    fixed = params.rho * params.E_total
    if params.budget_policy == "fixed":
        R_build = fixed
    else:
        protected = max(0.0, params.E_total - alignment * b_H_tot * params.e_H * H)
        R_build = min(fixed, protected)
    R_build = max(0.0, min(params.E_total, R_build))
    E_op = params.E_total - R_build
    return b_H_tot, R_build, E_op


def rsi_diagnostics(
    params: RSIParameters,
    H: float,
    A: float,
    q: float,
    alignment: float = 0.0,
    t: float = 0.0,
    intervention: Optional[Intervention] = None,
) -> RSIDiagnostics:
    if not np.all(np.isfinite([H, A, q])) or H < 0.0 or A < 0.0 or q <= 0.0:
        raise ValueError("state outside the mathematical domain")
    if not 0 <= alignment <= 1:
        raise ValueError("alignment must lie in [0, 1]")
    if intervention is not None:
        intervention.validate()
    g = alignment if intervention is None else intervention.effective_protection(t, alignment)
    H_eval = max(float(H), 0.0)
    A_eval = max(float(A), 0.0)
    q_eval = max(float(q), 1e-300)
    operating_fraction = 1.0 if intervention is None else intervention.operating_fraction(t)
    A_op = A_eval * operating_fraction

    b_H_tot, R_build, E_op = _budgets(params, H_eval, g)
    demands = np.array(
        [
            [params.e_H, params.ell_H],
            [params.e0 * q_eval ** (-params.xi), params.ell_A],
        ],
        dtype=float,
    )
    weights = np.array([params.w_H, params.w_A0 * q_eval ** params.omega], dtype=float)
    supplies = np.array([E_op, params.L_service], dtype=float)
    if params.allocation_rule == "proportional":
        alloc = allocate_resources(
            [H_eval, A_op], demands, supplies, weights, alignment=g
        )
    else:
        alloc = allocate_resources_priority(
            [H_eval, A_op], demands, supplies, weights, alignment=g
        )
    if not alloc.success:
        raise RuntimeError(f"resource allocation failed: {alloc.message}")

    s_H = float(alloc.satisfaction[0])
    s_A = float(alloc.satisfaction[1])
    zeta = params.zeta(q_eval)
    if params.manufacturing_mode == "substitutive":
        human_term = params.c_H * (1.0 - zeta) * H_eval / params.H_ref
    else:
        human_term = params.c_H * H_eval / params.H_ref
    manufacturing = min(
        params.M_max,
        human_term + params.c_A * zeta * A_op * s_A,
    )
    manufacturing = max(0.0, float(manufacturing))

    B_desired = max(0.0, params.r_A(q_eval) * A_op * s_A)
    B_manufacturing = manufacturing
    B_energy = R_build / params.c_build
    B_site = max(0.0, (params.A_max - A_eval) / params.tau_build)
    B0 = max(0.0, min(B_desired, B_manufacturing, B_energy, B_site))
    if intervention is None:
        B = B0
    else:
        B = max(0.0, intervention.cap_rate(t, A_eval, B0, params))

    dH = H_eval * (params.beta_H * s_H - params.delta_H)
    dA = B - params.delta_A * A_eval - params.mu_A * (1.0 - s_A) * A_op
    saturating = 1.0
    if params.growth_mode == "saturating":
        saturating = 1.0 - q_eval / params.q_max
    compute_share = A_op * s_A / (params.A_c + A_op * s_A)
    dq = params.eta * q_eval * compute_share * saturating

    E_AI_demand = params.e0 * q_eval ** (-params.xi) * A_op
    E_AI_allocated = E_AI_demand * s_A
    E_human_allocated = params.e_H * H_eval * s_H
    if A_eval > 0.0 and q_eval > 0.0:
        energy_log_derivative = dA / A_eval - params.xi * (dq / q_eval)
    else:
        energy_log_derivative = float("nan")

    return RSIDiagnostics(
        allocation=alloc,
        b_H_tot=b_H_tot,
        R_build=R_build,
        E_op=E_op,
        manufacturing=manufacturing,
        zeta=zeta,
        B_desired=B_desired,
        B_manufacturing=B_manufacturing,
        B_energy=B_energy,
        B_site=B_site,
        B=B,
        dH=dH,
        dA=dA,
        dq=dq,
        E_AI_demand=E_AI_demand,
        E_AI_allocated=E_AI_allocated,
        E_human_allocated=E_human_allocated,
        E_AI_demand_log_derivative=energy_log_derivative,
        B_before_policy=B0,
        protection_g=g,
        intervention_kind="none" if intervention is None else intervention.kind,
        operating_fraction=operating_fraction,
    )


def rsi_rhs(
    t: float,
    y: Sequence[float],
    params: RSIParameters,
    alignment: float = 0.0,
    intervention: Optional[Intervention] = None,
) -> List[float]:
    logH, logA, logq = float(y[0]), float(y[1]), float(y[2])
    H = float(np.exp(np.clip(logH, -700.0, 700.0)))
    A = (0.0 if params.A0 == 0.0 else
         float(np.exp(np.clip(logA, -700.0, 700.0))))
    q = float(np.exp(np.clip(logq, -700.0, 700.0)))
    diag = rsi_diagnostics(params, H, A, q, alignment, t=t, intervention=intervention)
    return [
        diag.dH / H if H > 0.0 else 0.0,
        diag.dA / A if A > 0.0 else 0.0,
        diag.dq / q if q > 0.0 else 0.0,
    ]


@dataclass
class RSISimulation:
    t: np.ndarray
    H: np.ndarray
    A: np.ndarray
    q: np.ndarray
    zeta: np.ndarray
    s_H: np.ndarray
    s_A: np.ndarray
    E_op: np.ndarray
    R_build: np.ndarray
    B: np.ndarray
    B_desired: np.ndarray
    B_manufacturing: np.ndarray
    B_energy: np.ndarray
    B_site: np.ndarray
    manufacturing: np.ndarray
    E_AI_demand: np.ndarray
    E_AI_allocated: np.ndarray
    E_human_allocated: np.ndarray
    outcome: str
    min_H: float
    p_bad_final_window: float
    extinction_time: float
    censored: bool
    status: str
    message: str
    success: bool
    alignment: float
    params: RSIParameters
    capacity_violation: bool = False
    numerical_diagnostics: Dict[str, object] = field(default_factory=dict)
    B_before_policy: Optional[np.ndarray] = None
    protection_g: Optional[np.ndarray] = None


def _trajectory_rows(
    params: RSIParameters,
    t: np.ndarray,
    y: np.ndarray,
    alignment: float,
    intervention: Optional[Intervention] = None,
) -> Dict[str, np.ndarray]:
    H = np.exp(np.clip(y[0], -700.0, 700.0))
    A = (np.zeros_like(y[1]) if params.A0 == 0.0 else
         np.exp(np.clip(y[1], -700.0, 700.0)))
    q = np.exp(np.clip(y[2], -700.0, 700.0))
    keys = [
        "zeta", "s_H", "s_A", "E_op", "R_build", "B", "B_desired",
        "B_manufacturing", "B_energy", "B_site", "manufacturing",
        "E_AI_demand", "E_AI_allocated", "E_human_allocated",
        "B_before_policy", "protection_g",
    ]
    out: Dict[str, np.ndarray] = {key: np.empty(t.size, dtype=float) for key in keys}
    for i in range(t.size):
        diag = rsi_diagnostics(
            params, float(H[i]), float(A[i]), float(q[i]), alignment,
            t=float(t[i]), intervention=intervention,
        )
        out["zeta"][i] = diag.zeta
        out["s_H"][i] = float(diag.allocation.satisfaction[0])
        out["s_A"][i] = float(diag.allocation.satisfaction[1])
        out["E_op"][i] = diag.E_op
        out["R_build"][i] = diag.R_build
        out["B"][i] = diag.B
        out["B_desired"][i] = diag.B_desired
        out["B_manufacturing"][i] = diag.B_manufacturing
        out["B_energy"][i] = diag.B_energy
        out["B_site"][i] = diag.B_site
        out["manufacturing"][i] = diag.manufacturing
        out["E_AI_demand"][i] = diag.E_AI_demand
        out["E_AI_allocated"][i] = diag.E_AI_allocated
        out["E_human_allocated"][i] = diag.E_human_allocated
        out["B_before_policy"][i] = diag.B_before_policy
        out["protection_g"][i] = diag.protection_g
    return {
        "H": H, "A": A, "q": q, **out
    }


def _bad_fraction(
    t: np.ndarray,
    H: np.ndarray,
    s_H: np.ndarray,
    params: RSIParameters,
) -> float:
    start = max(0.0, params.T - params.W_window)
    mask = t >= start - 1e-12
    if np.count_nonzero(mask) < 2:
        return float("nan")
    tt = t[mask]
    bad = ((H[mask] < params.H_min * (1 - 1e-10)) |
           (s_H[mask] < params.s_min - 1e-10)).astype(float)
    area = float(_trapz(bad, tt))
    duration = float(tt[-1] - tt[0])
    if duration <= 0.0:
        return float("nan")
    return area / duration


def _output_times(T: float, dt: float, window: float) -> np.ndarray:
    """Include both the actual horizon and the exact observation-window start."""
    return np.unique(np.concatenate((np.arange(0.0, T, dt), [T - window, T])))


def _dense_bad_fraction(
    solution, params, alignment, horizon, breakpoints, intervention=None
):
    """Integrate the indicator by resource/population threshold event intervals.

    Equality passes with a 1e-10 satisfaction/relative-population comparison
    tolerance. The event detection resolution is controlled by max_step.
    """
    start = params.T - params.W_window
    if horizon < params.T - 1e-9:
        return float("nan")
    points = np.unique([start, params.T] + [
        float(x) for x in breakpoints if start < x < params.T
    ])
    bad_time = 0.0
    for left, right in zip(points[:-1], points[1:]):
        H, A, q = np.exp(np.clip(solution(0.5 * (left + right)), -700, 700))
        if params.A0 == 0.0:
            A = 0.0
        mid = 0.5 * (left + right)
        s_H = rsi_diagnostics(
            params, H, A, q, alignment, t=mid, intervention=intervention
        ).allocation.satisfaction[0]
        if H < params.H_min * (1 - 1e-10) or s_H < params.s_min - 1e-10:
            bad_time += right - left
    return bad_time / params.W_window


def _rk4_step(
    params: RSIParameters,
    t: float,
    y: np.ndarray,
    h: float,
    alignment: float,
    intervention: Optional[Intervention] = None,
) -> np.ndarray:
    k1 = np.asarray(rsi_rhs(t, y, params, alignment, intervention), dtype=float)
    k2 = np.asarray(rsi_rhs(t + 0.5 * h, y + 0.5 * h * k1, params, alignment, intervention), dtype=float)
    k3 = np.asarray(rsi_rhs(t + 0.5 * h, y + 0.5 * h * k2, params, alignment, intervention), dtype=float)
    k4 = np.asarray(rsi_rhs(t + h, y + h * k3, params, alignment, intervention), dtype=float)
    return y + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def simulate_rsi(
    params: RSIParameters,
    alignment: float = 0.0,
    *,
    integrator: str = "solve_ivp",
    dt_internal: Optional[float] = None,
    method: str = "DOP853",
    rtol: float = 1e-8,
    atol: float = 1e-10,
    max_step: float = 0.25,
    intervention: Optional[Intervention] = None,
    terminate_on_extinction: bool = True,
) -> RSISimulation:
    params.validate()
    if not (0.0 <= alignment <= 1.0):
        raise ValueError("alignment must lie in [0, 1]")
    if intervention is not None:
        intervention.validate()
    if params.H0 <= params.H_ext:
        raise ValueError("H0 must start above H_ext")

    y0 = np.array(
        [np.log(params.H0), np.log(params.A0) if params.A0 > 0 else 0.0,
         np.log(params.q0)], dtype=float
    )
    diagnostics = {"integrator": integrator, "projection_count": 0,
                   "comparison_tolerance": 1e-10}
    refined_bad_fraction = None

    if integrator == "solve_ivp":
        def event_h(t: float, y: Sequence[float]) -> float:
            return float(y[0]) - float(np.log(params.H_ext))

        event_h.direction = -1
        event_h.terminal = terminate_on_extinction

        def event_floor(t, y):
            return float(y[0]) - np.log(params.H_min * (1 - 1e-10))

        def event_adequacy(t, y):
            H, A, q = np.exp(np.clip(y, -700.0, 700.0))
            if params.A0 == 0.0:
                A = 0.0
            return (rsi_diagnostics(
                params, H, A, q, alignment, t=t, intervention=intervention
            ).allocation.satisfaction[0] - (params.s_min - 1e-10))

        t_eval = _output_times(params.T, params.dt, params.W_window)
        sol = solve_ivp(
            lambda t, y: rsi_rhs(t, y, params, alignment, intervention),
            (0.0, params.T),
            y0,
            method=method,
            rtol=rtol,
            atol=atol,
            max_step=max_step,
            events=[event_h, event_floor, event_adequacy],
            dense_output=True,
        )
        if not sol.success:
            raise RuntimeError(f"RSI integration failed: {sol.message}")
        if sol.t_events[0].size > 0:
            extinction_time = float(sol.t_events[0][0])
            if terminate_on_extinction:
                t = t_eval[t_eval <= extinction_time + 1e-12]
                if t.size == 0 or t[-1] < extinction_time - 1e-12:
                    t = np.append(t, extinction_time)
            else:
                t = t_eval
            y = sol.sol(t)
        else:
            extinction_time = float("nan")
            t = t_eval
            y = sol.sol(t)
        refined_bad_fraction = _dense_bad_fraction(
            sol.sol, params, alignment, float(sol.t[-1]),
            list(sol.t_events[1]) + list(sol.t_events[2]),
            intervention=intervention,
        )
        diagnostics.update({"rhs_evaluations": sol.nfev,
                            "classification_method": "threshold_events",
                            "max_step": max_step})
    elif integrator == "rk4":
        dt = float(params.dt if dt_internal is None else dt_internal)
        if dt <= 0.0:
            raise ValueError("dt_internal must be positive")
        times = [0.0]
        states = [y0.copy()]
        y = y0.copy()
        t = 0.0
        extinction_time = float("nan")
        while t < params.T - 1e-14:
            next_window = params.T - params.W_window
            boundary = next_window if t < next_window - 1e-12 else params.T
            h = min(dt, params.T - t, boundary - t)
            y_new = _rk4_step(params, t, y, h, alignment, intervention)
            if not np.all(np.isfinite(y_new)):
                raise RuntimeError("nonfinite RK4 state; reduce dt_internal")
            a_excess = (y_new[1] - np.log(params.A_max) if params.A0 > 0 else 0.0)
            q_excess = (y_new[2] - np.log(params.q_max)
                        if params.growth_mode == "saturating" else 0.0)
            if max(a_excess, q_excess) > 1e-6:
                raise RuntimeError("RK4 exceeded an invariant ceiling; reduce dt_internal")
            if y_new[0] <= float(np.log(params.H_ext)) and y[0] > float(np.log(params.H_ext)):
                frac = (float(np.log(params.H_ext)) - y[0]) / (y_new[0] - y[0])
                frac = float(np.clip(frac, 0.0, 1.0))
                t_event = t + frac * h
                y_event = y + frac * (y_new - y)
                times.append(t_event)
                states.append(y_event)
                if not np.isfinite(extinction_time):
                    extinction_time = t_event
                if terminate_on_extinction:
                    break
            t += h
            y = y_new
            times.append(t)
            states.append(y.copy())
        t = np.asarray(times, dtype=float)
        y = np.asarray(states, dtype=float).T
        diagnostics.update({"dt_internal": dt,
                            "classification_method": "sampled_indicator"})
        if terminate_on_extinction and np.isfinite(extinction_time):
            keep = t <= extinction_time + 1e-12
            t = t[keep]
            y = y[:, keep]
    else:
        raise ValueError("integrator must be 'rk4' or 'solve_ivp'")

    rows = _trajectory_rows(params, t, y, alignment, intervention=intervention)
    H = rows["H"]
    min_H = float(np.min(H))
    if np.isfinite(extinction_time):
        outcome = "extinction"
        censored = False
        status = "reached_extinction_threshold"
        message = "H reached the effective extinction threshold"
        if terminate_on_extinction:
            p_bad = float("nan")
        else:
            p_bad = (_bad_fraction(t, H, rows["s_H"], params)
                     if refined_bad_fraction is None else refined_bad_fraction)
    else:
        extinction_time = float("nan")
        censored = True
        status = "completed_horizon"
        message = "simulation reached the study horizon"
        p_bad = (_bad_fraction(t, H, rows["s_H"], params)
                 if refined_bad_fraction is None else refined_bad_fraction)
        if np.isnan(p_bad):
            outcome = "failed"
            status = "classification_failed"
            message = "final-window adequacy could not be integrated"
        elif p_bad > params.p_tol:
            outcome = "marginal"
        else:
            outcome = "non_marginal"

    capacity_violation = bool(np.any(rows["A"] > params.A_max * (1.0 + 1e-8)))
    capability_violation = bool(params.growth_mode == "saturating" and
                               np.any(rows["q"] > params.q_max * (1 + 1e-6)))
    if capacity_violation or capability_violation:
        raise RuntimeError("saved trajectory violates an invariant ceiling")
    diagnostics["max_A_over_capacity"] = (float(np.max(rows["A"]) / params.A_max)
                                           if params.A_max > 0 else 0.0)
    diagnostics["max_q_over_ceiling"] = float(np.max(rows["q"]) / params.q_max)
    success = bool(outcome != "failed")
    return RSISimulation(
        t=t,
        H=H,
        A=rows["A"],
        q=rows["q"],
        zeta=rows["zeta"],
        s_H=rows["s_H"],
        s_A=rows["s_A"],
        E_op=rows["E_op"],
        R_build=rows["R_build"],
        B=rows["B"],
        B_desired=rows["B_desired"],
        B_manufacturing=rows["B_manufacturing"],
        B_energy=rows["B_energy"],
        B_site=rows["B_site"],
        manufacturing=rows["manufacturing"],
        E_AI_demand=rows["E_AI_demand"],
        E_AI_allocated=rows["E_AI_allocated"],
        E_human_allocated=rows["E_human_allocated"],
        outcome=outcome,
        min_H=min_H,
        p_bad_final_window=p_bad,
        extinction_time=extinction_time,
        censored=censored,
        status=status,
        message=message,
        success=success,
        alignment=alignment,
        params=params,
        capacity_violation=capacity_violation,
        numerical_diagnostics=diagnostics,
        B_before_policy=rows["B_before_policy"],
        protection_g=rows["protection_g"],
    )


def simulate_human_free(
    params: RSIParameters,
    alignment: float = 0.0,
    *,
    method: str = "DOP853",
    rtol: float = 1e-7,
    atol: float = 1e-9,
    max_step: float = 1.0,
) -> Dict[str, np.ndarray]:
    """Counterfactual H=0 dynamics with recomputed AI-only allocation."""
    p = replace(params, H0=1.0, H_ext=0.5, H_min=0.6)
    p.validate()
    if p.A0 <= 0:
        raise ValueError("A0 must be positive")
    y0 = [float(np.log(p.A0)), float(np.log(p.q0))]

    def rhs(t: float, y: Sequence[float]) -> List[float]:
        A = float(np.exp(np.clip(y[0], -700.0, 700.0)))
        q = float(np.exp(np.clip(y[1], -700.0, 700.0)))
        diag = rsi_diagnostics(p, 0.0, A, q, alignment)
        return [diag.dA / A if A > 0 else 0.0, diag.dq / q if q > 0 else 0.0]

    t_eval = np.arange(0.0, p.T + 0.5 * p.dt, p.dt)
    t_eval = t_eval[t_eval <= p.T + 1e-12]
    sol = solve_ivp(rhs, (0.0, p.T), y0, method=method, rtol=rtol, atol=atol,
                    max_step=max_step, t_eval=t_eval)
    if not sol.success:
        raise RuntimeError(f"human-free integration failed: {sol.message}")
    A = np.exp(np.clip(sol.y[0], -700.0, 700.0))
    q = np.exp(np.clip(sol.y[1], -700.0, 700.0))
    return {"t": sol.t, "A": A, "q": q}
