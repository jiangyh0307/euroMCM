"""Disclosed scenario definitions.

All values are ASSUMPTION unless explicitly marked otherwise in parameters.py.
No scenario is a forecast.  The stress scenarios deliberately explore severe
resource competition and are not estimates of likely future AI behaviour.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, Tuple

from .rsi import RSIParameters


def base_rsi() -> RSIParameters:
    return RSIParameters(
        L_service=2.0e6,
        T=100.0,
        dt=0.5,
        H0=8.0e9,
        H_min=1.0e8,
        H_ext=1.0e6,
        s_min=0.8,
        E_total=3.0e10,
        w_A0=1.0,
        e0=10000.0,
    )


def scenario_low() -> RSIParameters:
    return replace(
        base_rsi(),
        eta=0.02,
        xi=0.10,
        omega=0.0,
        q_c=20.0,
        M_max=1.0e4,
        c_A=0.2,
        r0=0.1,
        E_total=3.0e10,
    )


def scenario_moderate() -> RSIParameters:
    return replace(
        base_rsi(),
        eta=0.20,
        xi=0.20,
        omega=0.50,
        q_c=10.0,
        M_max=1.0e5,
        c_A=0.5,
        r0=0.2,
        E_total=2.0e10,
        w_A0=10.0,
    )


def scenario_rapid() -> RSIParameters:
    return replace(
        base_rsi(),
        eta=0.80,
        xi=0.0,
        omega=1.0,
        q_c=5.0,
        M_max=1.0e6,
        c_A=1.0,
        r0=0.5,
        E_total=1.5e10,
        w_A0=300.0,
    )


def scenario_stress() -> RSIParameters:
    return replace(
        base_rsi(),
        eta=0.5,
        xi=0.0,
        omega=1.0,
        q_c=5.0,
        M_max=1.0e6,
        c_A=1.0,
        r0=0.5,
        E_total=1.0e10,
        e0=10000.0,
        w_A0=10000.0,
        beta_H=0.2,
        delta_H=0.12,
        H0=1.0e8,
        H_min=1.0e7,
        H_ext=1.0e6,
    )


def scenario_collapse_stress() -> RSIParameters:
    """Pressure background for the revised risk adjudication.

    H0 is raised to 1e9 so that H_ext=1e8 remains a genuine lower threshold;
    H_min=2e8 is above H_ext. The RSI/demographic stress parameters otherwise
    follow scenario_stress(). This is the new Part V pressure background and
    must not be mixed with the legacy scenario_stress() results.
    """
    return replace(
        scenario_stress(),
        H0=1.0e9,
        H_ext=1.0e8,
        H_min=2.0e8,
        T=100.0,
        W_window=10.0,
        s_min=0.8,
        p_tol=0.0,
    )


def controlled_stress_scenarios() -> Dict[str, RSIParameters]:
    """2x2 factorial: human demography (baseline/fast) x AI pressure (baseline/stress).

    The resource supply differs between the baseline-AI and stress-AI arms; the
    factorial isolates human demography and AI pressure but not resource supply.
    """
    human_base = dict(
        beta_H=0.02, delta_H=0.01, H0=8.0e9, H_min=1.0e8, H_ext=1.0e6
    )
    human_fast = dict(
        beta_H=0.20, delta_H=0.12, H0=1.0e8, H_min=1.0e7, H_ext=1.0e6
    )
    ai_base = dict(
        eta=0.20, xi=0.20, omega=0.20, q_c=10.0, M_max=1.0e5,
        E_total=3.0e10, e0=10000.0, w_A0=1.0, c_A=0.5, r0=0.2,
    )
    ai_stress = dict(
        eta=0.50, xi=0.0, omega=1.0, q_c=5.0, M_max=1.0e6,
        E_total=1.0e10, e0=10000.0, w_A0=10000.0, c_A=1.0, r0=0.5,
    )
    out: Dict[str, RSIParameters] = {}
    for hname, hpars in [("baseline_human", human_base), ("fast_human", human_fast)]:
        for aname, apars in [("baseline_ai", ai_base), ("stress_ai", ai_stress)]:
            common = dict(
                L_service=2.0e6,
                M_max=apars["M_max"],
                c_A=apars["c_A"],
                r0=apars["r0"],
                eta=apars["eta"],
                xi=apars["xi"],
                omega=apars["omega"],
                q_c=apars["q_c"],
                E_total=apars["E_total"],
                e0=apars["e0"],
                w_A0=apars["w_A0"],
                **hpars,
            )
            out[f"{hname}__{aname}"] = replace(base_rsi(), **common)
    return out


def uq_specs() -> Dict[str, Dict[str, Tuple[float, float, str]]]:
    """Ranges for three disclosed scenario measures.

    Each entry is (low, high, scale) with scale in {"uniform", "log"}.
    These are exploratory ranges, not empirical distributions.
    """
    return {
        "conservative": {
            "eta": (0.02, 0.10, "log"),
            "xi": (0.0, 0.3, "uniform"),
            "omega": (0.0, 0.3, "uniform"),
            "q_c": (8.0, 20.0, "log"),
            "M_max": (1.0e4, 1.0e5, "log"),
            "c_A": (0.1, 0.5, "log"),
            "w_A0": (1.0, 10.0, "log"),
            "e0": (1000.0, 5000.0, "log"),
            "E_total": (2.0e10, 3.0e10, "log"),
            "beta_H": (0.10, 0.20, "uniform"),
            "r_H": (0.40, 0.70, "uniform"),
            "L_service": (1.5e6, 3.0e6, "log"),
            "rho": (0.05, 0.15, "uniform"),
            "H0": (1.0e9, 8.0e9, "log"),
        },
        "central": {
            "eta": (0.05, 0.30, "log"),
            "xi": (0.0, 0.5, "uniform"),
            "omega": (0.0, 0.8, "uniform"),
            "q_c": (5.0, 15.0, "log"),
            "M_max": (1.0e4, 5.0e5, "log"),
            "c_A": (0.1, 0.8, "log"),
            "w_A0": (1.0, 100.0, "log"),
            "e0": (2000.0, 10000.0, "log"),
            "E_total": (1.5e10, 3.0e10, "log"),
            "beta_H": (0.10, 0.20, "uniform"),
            "r_H": (0.40, 0.75, "uniform"),
            "L_service": (1.0e6, 3.0e6, "log"),
            "rho": (0.05, 0.20, "uniform"),
            "H0": (5.0e8, 8.0e9, "log"),
        },
        "aggressive": {
            "eta": (0.10, 1.00, "log"),
            "xi": (0.0, 0.5, "uniform"),
            "omega": (0.3, 1.5, "uniform"),
            "q_c": (3.0, 10.0, "log"),
            "M_max": (1.0e5, 1.0e6, "log"),
            "c_A": (0.3, 1.0, "log"),
            "w_A0": (10.0, 10000.0, "log"),
            "e0": (5000.0, 20000.0, "log"),
            "E_total": (0.8e10, 2.0e10, "log"),
            "beta_H": (0.15, 0.25, "uniform"),
            "r_H": (0.50, 0.80, "uniform"),
            "L_service": (1.0e6, 2.5e6, "log"),
            "rho": (0.05, 0.20, "uniform"),
            "H0": (1.0e8, 8.0e9, "log"),
        },
        "stress_augmented": {
            "eta": (0.30, 1.00, "log"),
            "xi": (0.0, 0.10, "uniform"),
            "omega": (0.80, 1.20, "uniform"),
            "q_c": (3.0, 8.0, "log"),
            "M_max": (5.0e5, 1.0e6, "log"),
            "c_A": (0.7, 1.0, "log"),
            "w_A0": (3000.0, 10000.0, "log"),
            "e0": (8000.0, 20000.0, "log"),
            "E_total": (0.8e10, 1.2e10, "log"),
            "beta_H": (0.15, 0.25, "uniform"),
            "r_H": (0.50, 0.80, "uniform"),
            "L_service": (1.0e6, 2.0e6, "log"),
            "rho": (0.05, 0.15, "uniform"),
            "H0": (1.0e8, 3.0e8, "log"),
        },
    }
