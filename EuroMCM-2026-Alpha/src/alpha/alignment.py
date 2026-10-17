"""Alignment scans, finite-horizon outcomes, and fixed-policy safety maps."""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, Iterable, List, Optional, Sequence

import numpy as np

from .rsi import RSIParameters, simulate_rsi
from .viability import viability_certificate


OUTCOME_ORDER = ("extinction", "marginal", "non_marginal", "failed")


def alignment_scan(
    params: RSIParameters,
    a_values: Sequence[float],
    *,
    simulation_kwargs: Optional[dict] = None,
) -> List[Dict[str, object]]:
    simulation_kwargs = simulation_kwargs or {}
    rows: List[Dict[str, object]] = []
    for a in a_values:
        try:
            sim = simulate_rsi(params, alignment=float(a), **simulation_kwargs)
            rows.append(
                {
                    "a": float(a),
                    "outcome": sim.outcome,
                    "success": sim.success,
                    "min_H": sim.min_H,
                    "p_bad_final_window": sim.p_bad_final_window,
                    "extinction_time": sim.extinction_time,
                    "censored": sim.censored,
                    "final_H": float(sim.H[-1]),
                    "final_A": float(sim.A[-1]),
                    "final_q": float(sim.q[-1]),
                    "final_s_H": float(sim.s_H[-1]),
                    "final_s_A": float(sim.s_A[-1]),
                    "final_zeta": float(sim.zeta[-1]),
                    "population_floor": bool(sim.min_H >= params.H_min),
                    "non_marginal": sim.outcome == "non_marginal",
                    "status": sim.status,
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "a": float(a),
                    "outcome": "failed",
                    "success": False,
                    "min_H": float("nan"),
                    "p_bad_final_window": float("nan"),
                    "extinction_time": float("nan"),
                    "censored": True,
                    "final_H": float("nan"),
                    "final_A": float("nan"),
                    "final_q": float("nan"),
                    "final_s_H": float("nan"),
                    "final_s_A": float("nan"),
                    "final_zeta": float("nan"),
                    "population_floor": False,
                    "non_marginal": False,
                    "status": f"error: {exc}",
                }
            )
    return rows


def scan_summary(rows: Sequence[Dict[str, object]]) -> Dict[str, object]:
    valid = [r for r in rows if r["success"]]
    safe = [float(r["a"]) for r in valid if r["population_floor"]]
    nm = [float(r["a"]) for r in valid if r["non_marginal"]]
    return {
        "n": len(rows),
        "n_valid": len(valid),
        "a_grid": [float(r["a"]) for r in rows],
        "safe_population_set": safe,
        "non_marginal_set": nm,
        "a_num_population": min(safe) if safe else float("inf"),
        "a_num_non_marginal": min(nm) if nm else float("inf"),
        "monotonicity_assumed": False,
    }


def phase_diagram(
    params: RSIParameters,
    a_values: Sequence[float],
    eta_values: Sequence[float],
    *,
    simulation_kwargs: Optional[dict] = None,
) -> List[Dict[str, object]]:
    simulation_kwargs = simulation_kwargs or {}
    rows: List[Dict[str, object]] = []
    for eta in eta_values:
        for a in a_values:
            p = replace(params, eta=float(eta))
            try:
                sim = simulate_rsi(p, alignment=float(a), **simulation_kwargs)
                rows.append(
                    {
                        "a": float(a),
                        "eta": float(eta),
                        "outcome": sim.outcome,
                        "success": sim.success,
                        "min_H": sim.min_H,
                        "p_bad": sim.p_bad_final_window,
                        "population_floor": bool(sim.min_H >= p.H_min),
                        "status": sim.status,
                    }
                )
            except Exception as exc:
                rows.append(
                    {
                        "a": float(a),
                        "eta": float(eta),
                        "outcome": "failed",
                        "success": False,
                        "min_H": float("nan"),
                        "p_bad": float("nan"),
                        "population_floor": False,
                        "status": f"error: {exc}",
                    }
                )
    return rows


def safe_initial_states(
    params: RSIParameters,
    alignment: float,
    A0_values: Sequence[float],
    q0_values: Sequence[float],
    *,
    simulation_kwargs: Optional[dict] = None,
) -> List[Dict[str, object]]:
    simulation_kwargs = simulation_kwargs or {}
    rows: List[Dict[str, object]] = []
    for A0 in A0_values:
        for q0 in q0_values:
            try:
                p = replace(params, A0=float(A0), q0=float(q0))
                sim = simulate_rsi(p, alignment=alignment, **simulation_kwargs)
                rows.append(
                    {
                        "a": float(alignment),
                        "A0": float(A0),
                        "q0": float(q0),
                        "outcome": sim.outcome,
                        "success": sim.success,
                        "min_H": sim.min_H,
                        "population_floor": bool(sim.min_H >= p.H_min),
                        "non_marginal": sim.outcome == "non_marginal",
                        "status": sim.status,
                    }
                )
            except Exception as exc:
                rows.append(
                    {
                        "a": float(alignment),
                        "A0": float(A0),
                        "q0": float(q0),
                        "outcome": "failed",
                        "success": False,
                        "min_H": float("nan"),
                        "population_floor": False,
                        "non_marginal": False,
                        "status": f"error: {exc}",
                    }
                )
    return rows


def comparison_with_certificate(
    params: RSIParameters,
    rows: Sequence[Dict[str, object]],
    *,
    rho_max: Optional[float] = None,
) -> Dict[str, object]:
    cert = viability_certificate(params, rho_max=rho_max)
    summary = scan_summary(rows)
    return {
        "a_safe": cert.a_safe,
        "a_num_population": summary["a_num_population"],
        "a_num_non_marginal": summary["a_num_non_marginal"],
        "certificate_feasible": cert.feasible,
        "b_under": cert.b_under,
        "safe_population_set": summary["safe_population_set"],
    }
