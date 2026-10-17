"""Small Part V uncertainty ensemble: fixed background, varied RSI parameters."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import json

import pandas as pd

from alpha.rsi import Intervention, simulate_rsi
from alpha.risk import RiskThresholds, assess_risk, paired_damage
from alpha.scenarios import scenario_collapse_stress
from alpha.uncertainty import sample_parameters

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results/tables"


def main(n=8, seed=2027):
    base = scenario_collapse_stress()
    thresholds = RiskThresholds(H_ext=base.H_ext, H_min=base.H_min,
                                delta_years=10.0, q_rapid=0.5, q_total=0.9,
                                W_window=base.W_window, s_min=base.s_min,
                                p_tol=base.p_tol)
    policies = [
        ("none", Intervention(kind="none")),
        ("R_tau0_u0.8", Intervention(kind="protect", tau=0.0, u_bar=0.8)),
        ("R_tau25_u0.8", Intervention(kind="protect", tau=25.0, u_bar=0.8)),
        ("R_tau50_u0.8", Intervention(kind="protect", tau=50.0, u_bar=0.8)),
        ("C_tau0_c0.1", Intervention(kind="cap", tau=0.0, cap_fraction=0.1,
                                      tau_cap=base.tau_build)),
        ("C_tau25_c0.1", Intervention(kind="cap", tau=25.0, cap_fraction=0.1,
                                       tau_cap=base.tau_build)),
        ("C_tau50_c0.1", Intervention(kind="cap", tau=50.0, cap_fraction=0.1,
                                       tau_cap=base.tau_build)),
    ]
    varied = ["eta", "xi", "omega", "q_c", "M_max", "c_A", "w_A0", "e0"]
    samples = sample_parameters("stress_augmented", n, seed)
    rows = []
    for sid, drawn, _ in samples:
        p = replace(base, **{key: getattr(drawn, key) for key in varied})
        no_ai = replace(p, A0=0.0, rho=0.0)
        no_sim = simulate_rsi(no_ai, 0.0, terminate_on_extinction=False)
        for name, pol in policies:
            sim = simulate_rsi(p, 0.0, intervention=pol,
                               terminate_on_extinction=False)
            risk = assess_risk(sim.t, sim.H, sim.s_H, p.H0, thresholds,
                               p_bad=sim.p_bad_final_window)
            damage = paired_damage(sim.t, sim.H, no_sim.t, no_sim.H)
            rows.append({
                "sample_id": sid, "policy": name,
                "risk_outcome": risk.outcome,
                "extinction": risk.extinction,
                "terminal_extinction": risk.terminal_extinction,
                "recovered_after_extinction": risk.recovered_after_extinction,
                "rapid_collapse": risk.rapid_collapse,
                "cumulative_collapse": risk.cumulative_collapse,
                "final_H": float(sim.H[-1]), "min_H": sim.min_H,
                "final_s_H": float(sim.s_H[-1]),
                "final_window_bad_fraction": risk.final_window_bad_fraction,
                "paired_final_damage": damage["final_damage"],
                "eta": p.eta, "xi": p.xi, "omega": p.omega,
                "q_c": p.q_c, "M_max": p.M_max, "c_A": p.c_A,
                "w_A0": p.w_A0, "e0": p.e0,
            })
    df = pd.DataFrame(rows)
    df.to_csv(TABLES / "part_v_uncertainty_results.csv", index=False)
    summary = (df.groupby("policy", as_index=False)
               .agg(n=("sample_id", "size"),
                    P_extinction=("extinction", "mean"),
                    P_recovered=("recovered_after_extinction", "mean"),
                    P_rapid=("rapid_collapse", "mean"),
                    mean_final_H=("final_H", "mean"),
                    mean_final_s_H=("final_s_H", "mean"),
                    mean_damage=("paired_final_damage", "mean")))
    summary.to_csv(TABLES / "part_v_uncertainty_summary.csv", index=False)
    manifest = {
        "background": "scenario_collapse_stress fixed demographics/resources/thresholds",
        "varied_parameters": varied,
        "source_range": "stress_augmented (exploratory, not preregistered)",
        "n": n, "seed": seed, "policies": [name for name, _ in policies],
        "note": "Small exploratory ensemble; not a real-world probability.",
    }
    (TABLES / "part_v_uncertainty_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
