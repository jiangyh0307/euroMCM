"""Risk adjudication for population trajectories.

The population ODE is unchanged. This module distinguishes an absolute
population floor, a rapid (short-window) collapse, and a cumulative relative
loss. The thresholds are policy/scenario conventions, not empirical estimates.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Sequence, Tuple

import numpy as np

_trapz = getattr(np, "trapezoid", np.trapz)


@dataclass(frozen=True)
class RiskThresholds:
    H_ext: float = 1.0e8
    H_min: float = 2.0e8
    delta_years: float = 10.0
    q_rapid: float = 0.5
    q_total: float = 0.9
    W_window: float = 10.0
    s_min: float = 0.8
    p_tol: float = 0.0

    def validate(self, H0: float) -> None:
        if not (0.0 < self.H_ext < self.H_min < H0):
            raise ValueError("require 0 < H_ext < H_min < H0")
        if self.delta_years <= 0 or self.W_window <= 0:
            raise ValueError("delta_years and W_window must be positive")
        if not (0.0 < self.q_rapid < 1.0) or not (0.0 < self.q_total < 1.0):
            raise ValueError("q thresholds must lie in (0,1)")
        if not (0.0 < self.s_min <= 1.0) or not (0.0 <= self.p_tol < 1.0):
            raise ValueError("invalid adequacy thresholds")


@dataclass
class RiskAssessment:
    outcome: str
    extinction: bool
    rapid_collapse: bool
    rapid_contraction: bool
    cumulative_collapse: bool
    catastrophe: bool
    terminal_extinction: bool
    recovered_after_extinction: bool
    extinction_time: float
    rapid_collapse_time: float
    rapid_contraction_time: float
    cumulative_loss: float
    max_total_loss: float
    final_window_bad_fraction: float
    max_rapid_loss: float
    details: Dict[str, float]


def _interp_log(t: np.ndarray, H: np.ndarray, times: np.ndarray) -> np.ndarray:
    logH = np.log(np.maximum(np.asarray(H, dtype=float), 1e-300))
    return np.exp(np.interp(times, t, logH))


def _bad_fraction(t: np.ndarray, H: np.ndarray, s_H: np.ndarray,
                  thresholds: RiskThresholds) -> float:
    start = max(0.0, float(t[-1]) - thresholds.W_window)
    mask = t >= start - 1e-12
    if np.count_nonzero(mask) < 2:
        return float("nan")
    tt = t[mask]
    bad = ((H[mask] < thresholds.H_min * (1 - 1e-10)) |
           (s_H[mask] < thresholds.s_min - 1e-10)).astype(float)
    area = float(_trapz(bad, tt))
    duration = float(tt[-1] - tt[0])
    return area / duration if duration > 0 else float("nan")


def assess_risk(
    t: Sequence[float],
    H: Sequence[float],
    s_H: Sequence[float],
    H0: float,
    thresholds: RiskThresholds,
    *,
    p_bad: Optional[float] = None,
    extinction_event_time: Optional[float] = None,
) -> RiskAssessment:
    """Assess a full trajectory; optional solver event must use this H_ext.

    A finite extinction_event_time overrides sampled first passage; NaN means
    the solver found no event. Omitting it preserves sample-based assessment.
    """
    t = np.asarray(t, dtype=float)
    H = np.asarray(H, dtype=float)
    s_H = np.asarray(s_H, dtype=float)
    if t.size != H.size or H.size != s_H.size or t.size < 2:
        raise ValueError("t, H and s_H must be equal-length trajectories")
    thresholds.validate(float(H0))
    if np.any(~np.isfinite(H)) or np.any(H <= 0):
        raise ValueError("H must be finite and positive")
    if np.any(np.diff(t) < 0):
        raise ValueError("t must be nondecreasing")

    # When provided, the solver event is authoritative, including NaN for no event.
    if extinction_event_time is not None:
        event_time = float(extinction_event_time)
        if np.isinf(event_time) or (np.isfinite(event_time) and not t[0] <= event_time <= t[-1]):
            raise ValueError("extinction event time outside trajectory")
        extinction = bool(np.isfinite(event_time))
    else:
        extinction = bool(np.min(H) <= thresholds.H_ext * (1 + 1e-12))
    terminal_extinction = bool(H[-1] <= thresholds.H_ext * (1 + 1e-12))
    recovered_after_extinction = bool(extinction and not terminal_extinction)
    if extinction:
        extinction_time = (float(extinction_event_time) if extinction_event_time is not None
                           else float(t[np.argmax(H <= thresholds.H_ext * (1 + 1e-12))]))
    else:
        extinction_time = float("nan")

    horizon = float(t[-1])
    last_start = horizon - thresholds.delta_years
    if last_start > t[0] + 1e-12:
        starts = t[t <= last_start + 1e-12]
        future = _interp_log(t, H, starts + thresholds.delta_years)
        current = np.interp(starts, t, H)
        ratio = future / current
        contraction = ratio <= (1.0 - thresholds.q_rapid)
        size_ok = future <= thresholds.H_min
        rapid = contraction & size_ok
        rapid_contraction = bool(np.any(contraction))
        rapid_collapse = bool(np.any(rapid))
        rapid_contraction_time = float(starts[np.argmax(contraction)]) if rapid_contraction else float("nan")
        rapid_collapse_time = float(starts[np.argmax(rapid)]) if rapid_collapse else float("nan")
        max_rapid_loss = float(max(0.0, 1.0 - np.min(ratio)))
    else:
        rapid_collapse = False
        rapid_contraction = False
        rapid_collapse_time = float("nan")
        rapid_contraction_time = float("nan")
        max_rapid_loss = 0.0

    cumulative_loss = float(max(0.0, 1.0 - H[-1] / H0))
    max_total_loss = float(max(0.0, 1.0 - np.min(H) / H0))
    cumulative_collapse = bool(cumulative_loss >= thresholds.q_total)
    if p_bad is None:
        p_bad = _bad_fraction(t, H, s_H, thresholds)
    p_bad = float(p_bad) if p_bad is not None else float("nan")

    if extinction:
        outcome = "extinction"
    elif rapid_collapse:
        outcome = "rapid_collapse"
    elif cumulative_collapse:
        outcome = "cumulative_collapse"
    elif np.isfinite(p_bad) and p_bad > thresholds.p_tol:
        outcome = "marginal"
    else:
        outcome = "non_marginal"
    return RiskAssessment(
        outcome=outcome,
        extinction=extinction,
        rapid_collapse=rapid_collapse,
        rapid_contraction=rapid_contraction,
        cumulative_collapse=cumulative_collapse,
        catastrophe=bool(extinction or rapid_collapse or cumulative_collapse),
        terminal_extinction=terminal_extinction,
        recovered_after_extinction=recovered_after_extinction,
        extinction_time=extinction_time,
        rapid_collapse_time=rapid_collapse_time,
        rapid_contraction_time=rapid_contraction_time,
        cumulative_loss=cumulative_loss,
        max_total_loss=max_total_loss,
        final_window_bad_fraction=p_bad,
        max_rapid_loss=max_rapid_loss,
        details={
            "H_ext": thresholds.H_ext,
            "H_min": thresholds.H_min,
            "delta_years": thresholds.delta_years,
            "q_rapid": thresholds.q_rapid,
            "q_total": thresholds.q_total,
        },
    )


def paired_damage(
    t_ai: Sequence[float], H_ai: Sequence[float],
    t_ref: Sequence[float], H_ref: Sequence[float],
) -> Dict[str, float]:
    """Damage of AI-present relative to a paired no-AI path on the common interval."""
    t_ai = np.asarray(t_ai, dtype=float)
    t_ref = np.asarray(t_ref, dtype=float)
    start = max(float(t_ai[0]), float(t_ref[0]))
    end = min(float(t_ai[-1]), float(t_ref[-1]))
    if end <= start:
        raise ValueError("paired trajectories do not overlap")
    grid = np.unique(np.concatenate((t_ai[(t_ai >= start) & (t_ai <= end)],
                                     t_ref[(t_ref >= start) & (t_ref <= end)],
                                     [start, end])))
    ai = _interp_log(t_ai, H_ai, grid)
    ref = _interp_log(t_ref, H_ref, grid)
    damage = 1.0 - ai / ref
    return {
        "final_damage": float(damage[-1]),
        "mean_damage": float(_trapz(damage, grid) / (end - start)),
        "max_damage": float(np.max(damage)),
    }


__all__ = ["RiskThresholds", "RiskAssessment", "assess_risk", "paired_damage"]
