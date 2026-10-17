"""Scenario-based uncertainty quantification and structural robustness."""

from __future__ import annotations

import warnings
from dataclasses import replace
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy.stats import ConstantInputWarning, spearmanr

from .rsi import RSIParameters, simulate_rsi
from .scenarios import base_rsi, uq_specs
from .viability import viability_certificate


def _draw(rng: np.random.Generator, low: float, high: float, scale: str) -> float:
    if scale == "log":
        return float(np.exp(rng.uniform(np.log(low), np.log(high))))
    return float(rng.uniform(low, high))


def sample_parameters(
    scenario: str,
    n: int,
    seed: int,
) -> List[Tuple[int, RSIParameters, Dict[str, float]]]:
    specs = uq_specs()
    if scenario not in specs:
        raise ValueError(f"unknown scenario {scenario}")
    spec = specs[scenario]
    rng = np.random.default_rng(seed)
    samples: List[Tuple[int, RSIParameters, Dict[str, float]]] = []
    for i in range(n):
        draws: Dict[str, float] = {}
        for key, (low, high, scale) in spec.items():
            draws[key] = _draw(rng, low, high, scale)
        beta_H = draws["beta_H"]
        r_H = draws["r_H"]
        delta_H = beta_H * r_H
        p = replace(
            base_rsi(),
            beta_H=beta_H,
            delta_H=delta_H,
            eta=draws["eta"],
            xi=draws["xi"],
            omega=draws["omega"],
            q_c=draws["q_c"],
            M_max=draws["M_max"],
            c_A=draws["c_A"],
            w_A0=draws["w_A0"],
            e0=draws["e0"],
            E_total=draws["E_total"],
            L_service=draws["L_service"],
            rho=draws["rho"],
            H0=draws["H0"] if "H0" in draws else 8.0e9,
            H_min=1.0e7,
            H_ext=1.0e6,
            T=100.0,
            dt=1.0,
        )
        draws["delta_H"] = delta_H
        draws["r_H"] = r_H
        samples.append((i, p, draws))
    return samples


def _q_self_crossing(
    t: np.ndarray, q: np.ndarray, q_self: float
) -> Tuple[bool, float]:
    if not np.isfinite(q_self) or q_self <= 0.0:
        return False, float("nan")
    idx = np.where(q >= q_self)[0]
    if idx.size == 0:
        return False, float("nan")
    return True, float(t[idx[0]])


def run_uq(
    scenario: str,
    n: int,
    seed: int,
    a_values: Sequence[float],
    *,
    dt_internal: float = 1.0,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    samples = sample_parameters(scenario, n, seed)
    sample_rows = []
    result_rows = []
    for sample_id, p, draws in samples:
        cert = viability_certificate(p, rho_max=p.rho)
        row = {
            "scenario": scenario,
            "sample_id": sample_id,
            "a_safe": cert.a_safe,
            "b_under": cert.b_under,
            "q_self": p.q_self(),
            **draws,
        }
        sample_rows.append(row)
        for a in a_values:
            try:
                sim = simulate_rsi(p, alignment=float(a), dt_internal=dt_internal)
                crossed, t_cross = _q_self_crossing(sim.t, sim.q, p.q_self())
                result_rows.append(
                    {
                        "scenario": scenario,
                        "sample_id": sample_id,
                        "a": float(a),
                        "outcome": sim.outcome,
                        "success": sim.success,
                        "min_H": sim.min_H,
                        "p_bad": sim.p_bad_final_window,
                        "extinction_time": sim.extinction_time,
                        "final_H": float(sim.H[-1]),
                        "final_A": float(sim.A[-1]),
                        "final_q": float(sim.q[-1]),
                        "final_s_H": float(sim.s_H[-1]),
                        "final_s_A": float(sim.s_A[-1]),
                        "final_zeta": float(sim.zeta[-1]),
                        "q_self_crossed": crossed,
                        "t_q_self": t_cross,
                        "a_safe": cert.a_safe,
                    }
                )
            except Exception as exc:
                result_rows.append(
                    {
                        "scenario": scenario,
                        "sample_id": sample_id,
                        "a": float(a),
                        "outcome": "failed",
                        "success": False,
                        "min_H": float("nan"),
                        "p_bad": float("nan"),
                        "extinction_time": float("nan"),
                        "final_H": float("nan"),
                        "final_A": float("nan"),
                        "final_q": float("nan"),
                        "final_s_H": float("nan"),
                        "final_s_A": float("nan"),
                        "final_zeta": float("nan"),
                        "q_self_crossed": False,
                        "t_q_self": float("nan"),
                        "a_safe": cert.a_safe,
                        "error": str(exc),
                    }
                )
    return pd.DataFrame(sample_rows), pd.DataFrame(result_rows)


def wilson_interval(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    if n <= 0:
        return float("nan"), float("nan")
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * np.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return float(max(0.0, center - half)), float(min(1.0, center + half))


def probability_summary(results: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (scenario, a), group in results.groupby(["scenario", "a"], sort=True):
        valid = group[group["success"]]
        if not valid["outcome"].isin(["extinction", "marginal", "non_marginal"]).all():
            raise ValueError("successful simulations must have exactly one defined outcome")
        n = len(valid)
        n_ext = int((valid["outcome"] == "extinction").sum())
        n_marg = int((valid["outcome"] == "marginal").sum())
        n_nm = int((valid["outcome"] == "non_marginal").sum())
        p_ext = n_ext / n if n else float("nan")
        p_marg = n_marg / n if n else float("nan")
        p_nm = n_nm / n if n else float("nan")
        lo_e, hi_e = wilson_interval(n_ext, n)
        lo_m, hi_m = wilson_interval(n_marg, n)
        lo_n, hi_n = wilson_interval(n_nm, n)
        rows.append(
            {
                "scenario": scenario,
                "a": float(a),
                "n_total": len(group),
                "n_valid": n,
                "n_failed": len(group) - n,
                "n_extinction": n_ext,
                "n_marginal": n_marg,
                "n_non_marginal": n_nm,
                "P_extinction": p_ext,
                "P_marginal": p_marg,
                "P_non_marginal": p_nm,
                "P_sum": p_ext + p_marg + p_nm,
                "P_ext_lo": lo_e,
                "P_ext_hi": hi_e,
                "P_marg_lo": lo_m,
                "P_marg_hi": hi_m,
                "P_nm_lo": lo_n,
                "P_nm_hi": hi_n,
            }
        )
    return pd.DataFrame(rows)


def _bootstrap_spearman(
    x: np.ndarray, y: np.ndarray, rng: np.random.Generator, n_boot: int = 200
) -> Tuple[float, float]:
    if x.size < 3 or np.all(x == x[0]) or np.all(y == y[0]):
        return float("nan"), float("nan")
    values = []
    for _ in range(n_boot):
        idx = rng.integers(0, x.size, x.size)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConstantInputWarning)
            rho, _ = spearmanr(x[idx], y[idx])
        if np.isfinite(rho):
            values.append(float(rho))
    if not values:
        return float("nan"), float("nan")
    return float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))


def rank_sensitivity(
    samples: pd.DataFrame,
    results: pd.DataFrame,
    *,
    a_value: float = 0.5,
    seed: int = 2026,
) -> pd.DataFrame:
    inputs = [
        "eta", "xi", "omega", "q_c", "M_max", "c_A", "w_A0", "e0",
        "E_total", "beta_H", "r_H", "L_service", "rho", "H0",
    ]
    inputs = [key for key in inputs if key in samples.columns]
    rows = []
    for scenario in sorted(results["scenario"].unique()):
        sub = results[
            (results["scenario"] == scenario)
            & (np.isclose(results["a"], a_value))
            & (results["success"])
        ].copy()
        merged = sub.merge(
            samples[samples["scenario"] == scenario],
            on=["scenario", "sample_id"],
            suffixes=("", "_sample"),
        )
        if merged.empty:
            continue
        outputs = {
            "log10_min_H": np.log10(np.maximum(merged["min_H"].to_numpy(dtype=float), 1e-300)),
            "extinction": (merged["outcome"] == "extinction").astype(float).to_numpy(),
            "non_marginal": (merged["outcome"] == "non_marginal").astype(float).to_numpy(),
            "a_safe": merged["a_safe_sample"].to_numpy(dtype=float)
            if "a_safe_sample" in merged.columns
            else merged["a_safe"].to_numpy(dtype=float),
        }
        rng = np.random.default_rng(seed)
        for key in inputs:
            x = merged[key].to_numpy(dtype=float)
            for out_name, y in outputs.items():
                if x.size < 3 or np.all(x == x[0]) or np.all(y == y[0]):
                    rho, lo, hi = float("nan"), float("nan"), float("nan")
                    note = "constant or insufficient sample"
                else:
                    rho, _ = spearmanr(x, y)
                    lo, hi = _bootstrap_spearman(x, y, rng)
                    note = ""
                rows.append(
                    {
                        "scenario": scenario,
                        "a": a_value,
                        "input": key,
                        "output": out_name,
                        "spearman_rho": float(rho),
                        "ci_low": lo,
                        "ci_high": hi,
                        "n": int(x.size),
                        "note": note,
                    }
                )
    return pd.DataFrame(rows)


def structural_robustness(
    n_samples: int = 20,
    seed: int = 2026,
    a_values: Sequence[float] = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
    *,
    scenario: str = "aggressive",
    dt_internal: float = 1.0,
) -> pd.DataFrame:
    samples = sample_parameters(scenario, n_samples, seed)
    structures = [
        ("proportional", "saturating"),
        ("proportional", "non_saturating"),
        ("priority", "saturating"),
        ("priority", "non_saturating"),
    ]
    rows = []
    for sample_id, p, _ in samples:
        for rule, growth in structures:
            q = replace(p, allocation_rule=rule, growth_mode=growth)
            for a in a_values:
                try:
                    sim = simulate_rsi(q, alignment=float(a), dt_internal=dt_internal)
                    rows.append(
                        {
                            "sample_id": sample_id,
                            "allocation_rule": rule,
                            "growth_mode": growth,
                            "a": float(a),
                            "outcome": sim.outcome,
                            "success": sim.success,
                            "min_H": sim.min_H,
                            "population_floor": bool(sim.min_H >= q.H_min),
                            "non_marginal": sim.outcome == "non_marginal",
                        }
                    )
                except Exception as exc:
                    rows.append(
                        {
                            "sample_id": sample_id,
                            "allocation_rule": rule,
                            "growth_mode": growth,
                            "a": float(a),
                            "outcome": "failed",
                            "success": False,
                            "min_H": float("nan"),
                            "population_floor": False,
                            "non_marginal": False,
                            "error": str(exc),
                        }
                    )
    detail = pd.DataFrame(rows)
    summary_rows = []
    for a, group in detail.groupby("a", sort=True):
        valid = group[group["success"]]
        n = len(valid)
        n_pop = int(valid["population_floor"].sum())
        n_nm = int(valid["non_marginal"].sum())
        summary_rows.append(
            {
                "a": float(a),
                "n_pairs": n,
                "n_population_floor": n_pop,
                "n_non_marginal": n_nm,
                "n_total": len(group),
                "n_failed": len(group) - n,
                "robust_population_floor": bool(n == len(group) and n > 0 and n_pop == n),
                "robust_non_marginal": bool(n == len(group) and n > 0 and n_nm == n),
            }
        )
    return detail, pd.DataFrame(summary_rows)
