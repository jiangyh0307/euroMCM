"""Refine the sampled preventive/recovery boundaries at 0.25-year resolution."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

from alpha.rsi import Intervention, simulate_rsi
from alpha.risk import RiskThresholds, assess_risk
from alpha.scenarios import scenario_collapse_stress

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results/tables"


def inspect_boundary(df, column, lo, hi):
    sub = df[(df.tau >= lo) & (df.tau <= hi)].sort_values("tau")
    ok = sub[sub[column]]
    bad = sub[~sub[column]]
    last_ok = float(ok.tau.max()) if len(ok) else None
    first_bad = float(bad.tau.min()) if len(bad) else None
    return {
        "range": [lo, hi],
        "success_taus": ok.tau.tolist(),
        "last_success": last_ok,
        "first_failure": first_bad,
        "resolution": 0.25,
        "monotone_on_range": bool(
            len(ok) == 0 or len(bad) == 0 or
            (last_ok is not None and first_bad is not None and last_ok < first_bad)
        ),
    }


def main():
    params = scenario_collapse_stress()
    thresholds = RiskThresholds(H_ext=params.H_ext, H_min=params.H_min,
                                delta_years=10.0, q_rapid=0.5, q_total=0.9,
                                W_window=params.W_window, s_min=params.s_min,
                                p_tol=params.p_tol)
    policies = {
        "R_u0.8": lambda tau: Intervention(kind="protect", tau=tau, u_bar=0.8),
        "C_c0.1": lambda tau: Intervention(kind="cap", tau=tau, cap_fraction=0.1,
                                           tau_cap=params.tau_build),
    }
    ranges = {"R_u0.8": [(40.0, 44.0), (55.0, 59.0)],
              "C_c0.1": [(40.0, 44.0), (62.0, 66.0)]}
    rows, summary = [], {}
    for name, maker in policies.items():
        for lo, hi in ranges[name]:
            taus = np.arange(lo, hi + 1e-12, 0.25)
            for tau in taus:
                sim = simulate_rsi(params, 0.0, intervention=maker(float(tau)),
                                   terminate_on_extinction=False)
                risk = assess_risk(sim.t, sim.H, sim.s_H, params.H0, thresholds,
                                   p_bad=sim.p_bad_final_window)
                rows.append({
                    "policy": name, "tau": float(tau),
                    "prevent_success": bool(np.min(sim.H) > thresholds.H_ext),
                    "recover_success": bool(sim.H[-1] > thresholds.H_ext),
                    "risk_outcome": risk.outcome,
                    "min_H": sim.min_H, "final_H": float(sim.H[-1]),
                    "extinction_time": risk.extinction_time,
                    "recovered_after_extinction": risk.recovered_after_extinction,
                })
    df = pd.DataFrame(rows)
    df.to_csv(TABLES / "part_v_ponr_refinement.csv", index=False)
    for name in policies:
        summary[name] = {
            "prevent": inspect_boundary(df[df.policy == name], "prevent_success",
                                        ranges[name][0][0], ranges[name][0][1]),
            "recover": inspect_boundary(df[df.policy == name], "recover_success",
                                        ranges[name][1][0], ranges[name][1][1]),
        }
    (TABLES / "part_v_ponr_refinement.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
