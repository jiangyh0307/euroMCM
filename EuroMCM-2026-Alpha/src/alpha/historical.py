"""Historical two-population resource competition and compatibility analysis."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
from scipy.integrate import solve_ivp

from .allocation import AllocationResult, allocate_resources


@dataclass
class HistoricalParameters:
    beta_N: float = 0.055
    beta_M: float = 0.055
    delta_N: float = 0.035
    delta_M: float = 0.035
    w_N: float = 1.0
    w_M: float = 1.0
    m_N: float = 2700.0
    m_M: float = 2500.0
    ell_N: float = 1.0
    ell_M: float = 1.0
    S_E: float = 6.0e10
    S_L: float = 1.0e6
    N0: float = 50000.0
    M0: float = 5000.0
    N_ref: float = 50000.0
    kappa: float = 0.01
    t_max: float = 10000.0

    def validate(self) -> None:
        if self.beta_N <= 0 or self.beta_M <= 0:
            raise ValueError("beta_N and beta_M must be positive")
        if self.delta_N < 0 or self.delta_M < 0:
            raise ValueError("mortality rates must be nonnegative")
        if self.w_N <= 0 or self.w_M <= 0:
            raise ValueError("resource weights must be positive")
        if self.m_N <= 0 or self.m_M <= 0:
            raise ValueError("daily energy requirements must be positive")
        if self.ell_N < 0 or self.ell_M < 0:
            raise ValueError("land requirements must be nonnegative")
        if self.S_E < 0 or self.S_L < 0:
            raise ValueError("supplies must be nonnegative")
        if self.N0 <= 0 or self.M0 <= 0:
            raise ValueError("historical initial populations must be positive")
        if self.N_ref <= 0 or not (0 < self.kappa < 1):
            raise ValueError("N_ref must be positive and kappa must lie in (0, 1)")
        if self.t_max <= 0:
            raise ValueError("t_max must be positive")
        if self.M0 <= 0:
            raise ValueError("M0 must be positive")

    @property
    def N_crit(self) -> float:
        return self.kappa * self.N_ref

    @property
    def energy_demand_N(self) -> float:
        return 365.0 * self.m_N

    @property
    def energy_demand_M(self) -> float:
        return 365.0 * self.m_M

    def per_unit_demands(self) -> np.ndarray:
        return np.array(
            [
                [self.energy_demand_N, self.ell_N],
                [self.energy_demand_M, self.ell_M],
            ],
            dtype=float,
        )

    def supplies(self) -> np.ndarray:
        return np.array([self.S_E, self.S_L], dtype=float)

    def weights(self) -> np.ndarray:
        return np.array([self.w_N, self.w_M], dtype=float)

    def r_N(self) -> float:
        return self.delta_N / self.beta_N

    def r_M(self) -> float:
        return self.delta_M / self.beta_M


@dataclass
class HistoricalSimulation:
    t: np.ndarray
    N: np.ndarray
    M: np.ndarray
    s_N: np.ndarray
    s_M: np.ndarray
    T_rep: float
    censored: bool
    status: str
    message: str
    min_N: float
    max_M: float
    params: HistoricalParameters


def historical_allocation(
    params: HistoricalParameters, N: float, M: float
) -> AllocationResult:
    if N < 0 or M < 0:
        raise ValueError("populations must be nonnegative")
    scale = max(N, M, 1.0)
    return allocate_resources(
        [N / scale, M / scale],
        params.per_unit_demands(),
        params.supplies() / scale,
        params.weights(),
        alignment=0.0,
    )


def historical_rhs(t: float, y: Sequence[float], params: HistoricalParameters) -> List[float]:
    logN, logM = float(y[0]), float(y[1])
    N = float(np.exp(np.clip(logN, -700.0, 700.0)))
    M = float(np.exp(np.clip(logM, -700.0, 700.0)))
    alloc = historical_allocation(params, N, M)
    return [
        params.beta_N * float(alloc.satisfaction[0]) - params.delta_N,
        params.beta_M * float(alloc.satisfaction[1]) - params.delta_M,
    ]


def _historical_rk4_step(
    params: HistoricalParameters, t: float, y: np.ndarray, h: float
) -> np.ndarray:
    k1 = np.asarray(historical_rhs(t, y, params), dtype=float)
    k2 = np.asarray(historical_rhs(t + 0.5 * h, y + 0.5 * h * k1, params), dtype=float)
    k3 = np.asarray(historical_rhs(t + 0.5 * h, y + 0.5 * h * k2, params), dtype=float)
    k4 = np.asarray(historical_rhs(t + h, y + h * k3, params), dtype=float)
    return y + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def simulate_historical(
    params: HistoricalParameters,
    *,
    t_eval: Optional[Sequence[float]] = None,
    integrator: str = "rk4",
    dt_internal: float = 5.0,
    record_satisfaction: bool = True,
    method: str = "DOP853",
    rtol: float = 1e-8,
    atol: float = 1e-10,
    max_step: float = 50.0,
) -> HistoricalSimulation:
    params.validate()
    log_n_crit = float(np.log(params.N_crit))

    if params.N0 <= params.N_crit:
        t = np.array([0.0]) if t_eval is None else np.asarray(t_eval, dtype=float)
        N = np.full(t.shape, params.N0)
        M = np.full(t.shape, params.M0)
        alloc = historical_allocation(params, params.N0, params.M0)
        return HistoricalSimulation(
            t=t,
            N=N,
            M=M,
            s_N=np.full(t.shape, float(alloc.satisfaction[0])),
            s_M=np.full(t.shape, float(alloc.satisfaction[1])),
            T_rep=0.0,
            censored=False,
            status="already_below_threshold",
            message="N0 is at or below the effective extinction threshold",
            min_N=float(params.N0),
            max_M=float(params.M0),
            params=params,
        )

    if integrator == "solve_ivp":
        def event_n(t: float, y: Sequence[float]) -> float:
            return float(y[0]) - log_n_crit

        event_n.direction = -1
        event_n.terminal = True
        y0 = [float(np.log(params.N0)), float(np.log(params.M0))]
        sol = solve_ivp(
            lambda t, y: historical_rhs(t, y, params),
            (0.0, params.t_max),
            y0,
            method=method,
            rtol=rtol,
            atol=atol,
            max_step=max_step,
            events=event_n,
            dense_output=True,
        )
        if not sol.success:
            raise RuntimeError(f"historical integration failed: {sol.message}")
        if t_eval is None:
            times = np.asarray(sol.t, dtype=float)
        else:
            requested = np.asarray(t_eval, dtype=float)
            times = requested[requested <= float(sol.t[-1]) + 1e-12]
        if sol.t_events[0].size > 0:
            event_time = float(sol.t_events[0][0])
            if times.size == 0 or times[-1] < event_time - 1e-12:
                times = np.append(times, event_time)
        states = sol.sol(times)
        t = times
        y = states
        extinction_time = (
            float(sol.t_events[0][0]) if sol.t_events[0].size > 0 else float("nan")
        )
    elif integrator == "rk4":
        if dt_internal <= 0:
            raise ValueError("dt_internal must be positive")
        y = np.array([np.log(params.N0), np.log(params.M0)], dtype=float)
        t = 0.0
        times = [0.0]
        states = [y.copy()]
        extinction_time = float("nan")
        while t < params.t_max - 1e-14:
            h = min(float(dt_internal), params.t_max - t)
            y_new = _historical_rk4_step(params, t, y, h)
            if y_new[0] <= log_n_crit and y[0] > log_n_crit:
                frac = (log_n_crit - y[0]) / (y_new[0] - y[0])
                frac = float(np.clip(frac, 0.0, 1.0))
                t_event = t + frac * h
                y_event = y + frac * (y_new - y)
                times.append(t_event)
                states.append(y_event)
                extinction_time = t_event
                break
            t += h
            y = y_new
            times.append(t)
            states.append(y.copy())
        t_grid = np.asarray(times, dtype=float)
        y_grid = np.asarray(states, dtype=float).T
        if np.isfinite(extinction_time):
            keep = t_grid <= extinction_time + 1e-12
            t_grid = t_grid[keep]
            y_grid = y_grid[:, keep]
        if t_eval is None:
            t = t_grid
            y = y_grid
        else:
            requested = np.asarray(t_eval, dtype=float)
            t = requested[requested <= t_grid[-1] + 1e-12]
            if np.isfinite(extinction_time) and (t.size == 0 or t[-1] < extinction_time - 1e-12):
                t = np.append(t, extinction_time)
            y = np.vstack(
                [np.interp(t, t_grid, y_grid[0]), np.interp(t, t_grid, y_grid[1])]
            )
    else:
        raise ValueError("integrator must be 'rk4' or 'solve_ivp'")

    N = np.exp(np.clip(y[0], -700.0, 700.0))
    M = np.exp(np.clip(y[1], -700.0, 700.0))
    if record_satisfaction:
        s_N = np.empty_like(N)
        s_M = np.empty_like(M)
        for i in range(t.size):
            alloc = historical_allocation(params, float(N[i]), float(M[i]))
            s_N[i] = float(alloc.satisfaction[0])
            s_M[i] = float(alloc.satisfaction[1])
    else:
        s_N = np.full_like(N, np.nan)
        s_M = np.full_like(M, np.nan)

    if np.isfinite(extinction_time):
        censored = False
        status = "reached_threshold"
        message = "effective disappearance threshold crossed"
    else:
        extinction_time = float("nan")
        censored = True
        status = "censored"
        message = "threshold not crossed within the historical horizon"

    return HistoricalSimulation(
        t=t,
        N=N,
        M=M,
        s_N=s_N,
        s_M=s_M,
        T_rep=extinction_time,
        censored=censored,
        status=status,
        message=message,
        min_N=float(np.min(N)),
        max_M=float(np.max(M)),
        params=params,
    )


def _scan_one(args: Tuple[float, float, HistoricalParameters]) -> Dict[str, object]:
    w_ratio, beta_ratio, base = args
    p = replace(base, w_M=base.w_N * w_ratio, beta_M=base.beta_N * beta_ratio)
    try:
        sim = simulate_historical(
            p, integrator="rk4", dt_internal=10.0, record_satisfaction=False
        )
        return {
            "w_ratio": w_ratio,
            "beta_ratio": beta_ratio,
            "T_rep": sim.T_rep,
            "censored": sim.censored,
            "status": sim.status,
            "min_N": sim.min_N,
            "max_M": sim.max_M,
            "compatible_EU": bool((not sim.censored) and 2600.0 <= sim.T_rep <= 5400.0),
            "compatible_regional": bool((not sim.censored) and 1400.0 <= sim.T_rep <= 2900.0),
            "error": "",
        }
    except Exception as exc:
        return {
            "w_ratio": w_ratio,
            "beta_ratio": beta_ratio,
            "T_rep": float("nan"),
            "censored": True,
            "status": "error",
            "min_N": float("nan"),
            "max_M": float("nan"),
            "compatible_EU": False,
            "compatible_regional": False,
            "error": str(exc),
        }


def compatibility_scan(
    base: HistoricalParameters,
    w_ratios: Sequence[float],
    beta_ratios: Sequence[float],
    *,
    workers: int = 1,
) -> List[Dict[str, object]]:
    tasks = [
        (float(w), float(b), base) for w in w_ratios for b in beta_ratios
    ]
    if workers <= 1:
        return [_scan_one(task) for task in tasks]
    from multiprocessing import Pool

    with Pool(processes=workers) as pool:
        return pool.map(_scan_one, tasks)


def summarize_scan(rows: Sequence[Dict[str, object]]) -> Dict[str, object]:
    valid = [r for r in rows if r["status"] != "error"]
    crossed = [r for r in valid if not r["censored"]]
    eu = [r for r in valid if r["compatible_EU"]]
    regional = [r for r in valid if r["compatible_regional"]]
    times = np.array([r["T_rep"] for r in crossed], dtype=float)
    return {
        "n_total": len(rows),
        "n_valid": len(valid),
        "n_errors": len(rows) - len(valid),
        "n_crossed": len(crossed),
        "n_censored": len(valid) - len(crossed),
        "n_compatible_EU": len(eu),
        "fraction_compatible_EU": len(eu) / len(valid) if valid else float("nan"),
        "n_compatible_regional": len(regional),
        "fraction_compatible_regional": len(regional) / len(valid) if valid else float("nan"),
        "crossed_time_min": float(np.min(times)) if times.size else float("nan"),
        "crossed_time_median": float(np.median(times)) if times.size else float("nan"),
        "crossed_time_max": float(np.max(times)) if times.size else float("nan"),
    }
