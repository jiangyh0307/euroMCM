"""Conditional population-floor certificates and welfare bounds."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Sequence

import numpy as np

from .rsi import RSIParameters


def delta_critical(H0: float, H_ext: float, T: float) -> float:
    """Largest constant baseline mortality for which the lower bound stays above H_ext."""
    if H0 <= 0 or H_ext <= 0 or T <= 0 or H0 <= H_ext:
        raise ValueError("require T>0 and H0>H_ext>0")
    return float(np.log(H0 / H_ext) / T)


def extinction_lower_bound(H0: float, delta_H: float, T: float) -> float:
    if H0 <= 0 or delta_H < 0 or T < 0:
        raise ValueError("require H0>0, delta_H>=0, T>=0")
    return float(H0 * np.exp(-delta_H * T))


def extinction_impossible_by_bound(H0: float, delta_H: float,
                                  H_ext: float, T: float) -> bool:
    """Strict comparison matches the model's H <= H_ext extinction event."""
    return extinction_lower_bound(H0, delta_H, T) > H_ext


@dataclass
class ViabilityCertificate:
    b_under: float
    a_safe: float
    r_human: float
    energy_floor: float
    land_floor: float
    feasible: bool
    assumptions: str


def b_under(
    supply_floor: Sequence[float],
    per_capita_demand_upper: Sequence[float],
    H_min: float,
) -> float:
    if H_min <= 0:
        raise ValueError("H_min must be positive")
    values = [1.0]
    for s, d in zip(supply_floor, per_capita_demand_upper):
        if d > 0.0:
            if s <= 0.0:
                return 0.0
            values.append(float(s) / (float(d) * float(H_min)))
    return float(max(0.0, min(values)))


def a_safe(delta_H: float, beta_H: float, b_under_value: float) -> float:
    if beta_H <= 0.0 or b_under_value <= 0.0:
        return float("inf")
    return float(delta_H / (beta_H * b_under_value))


def viability_certificate(
    params: RSIParameters,
    *,
    E_min: Optional[float] = None,
    L_service_min: Optional[float] = None,
    rho_max: Optional[float] = None,
) -> ViabilityCertificate:
    E_min = params.E_total if E_min is None else float(E_min)
    L_service_min = params.L_service if L_service_min is None else float(L_service_min)
    rho_max = params.rho if rho_max is None else float(rho_max)
    if not (0.0 <= rho_max < 1.0):
        raise ValueError("rho_max must lie in [0, 1)")
    energy_floor = (1.0 - rho_max) * E_min
    land_floor = L_service_min
    b = b_under(
        [energy_floor, land_floor],
        [params.e_H, params.ell_H],
        params.H_min,
    )
    threshold = a_safe(params.delta_H, params.beta_H, b)
    feasible = bool(threshold <= 1.0)
    return ViabilityCertificate(
        b_under=b,
        a_safe=threshold,
        r_human=params.delta_H / params.beta_H if params.beta_H > 0 else float("inf"),
        energy_floor=energy_floor,
        land_floor=land_floor,
        feasible=feasible,
        assumptions=(
            "Sufficient population-floor certificate under uniform operational "
            "resource floors, exact enforcement of s_H>=a b_H, a locally Lipschitz "
            "well-posed coupled ODE, and forward invariance of the other state "
            "constraints. It does not guarantee s_H>=s_min or social welfare."
        ),
    )


def b_all_for_welfare(
    params: RSIParameters,
    H_upper: float,
    *,
    E_min: Optional[float] = None,
    L_service_min: Optional[float] = None,
    rho_max: Optional[float] = None,
) -> float:
    E_min = params.E_total if E_min is None else float(E_min)
    L_service_min = params.L_service if L_service_min is None else float(L_service_min)
    rho_max = params.rho if rho_max is None else float(rho_max)
    energy_floor = (1.0 - rho_max) * E_min
    return b_under([energy_floor, L_service_min], [params.e_H, params.ell_H], H_upper)


def welfare_safe_alignment(
    params: RSIParameters,
    H_upper: float,
    *,
    E_min: Optional[float] = None,
    L_service_min: Optional[float] = None,
    rho_max: Optional[float] = None,
) -> float:
    b = b_all_for_welfare(
        params, H_upper, E_min=E_min, L_service_min=L_service_min, rho_max=rho_max
    )
    if b <= 0.0:
        return float("inf")
    return float(params.s_min / b)


def population_floor_holds(H: Sequence[float], H_min: float) -> bool:
    return bool(np.min(np.asarray(H, dtype=float)) >= H_min)
