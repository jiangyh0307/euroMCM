"""Part V risk-revised policy grid.

Uses the new risk hierarchy: effective extinction at H_ext=1e8, rapid collapse
(10-year >=50% loss with H<=H_min), cumulative collapse (>=90% loss relative to H0),
then marginal/non-marginal adequacy. The population ODE is unchanged.
"""
from __future__ import annotations

from pathlib import Path
import json

import pandas as pd
import numpy as np

from alpha.rsi import Intervention, rsi_diagnostics, simulate_rsi
from alpha.risk import RiskThresholds, assess_risk, paired_damage
from alpha.scenarios import base_rsi, scenario_collapse_stress
from run_part_v import _trapz

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results/tables"


def cost_metrics(sim, params, alignment, policy):
    t = sim.t
    C_install = 0.0
    C_protect = 0.0
    if policy.kind == "cap":
        blocked = np.maximum(sim.B_before_policy - sim.B, 0.0)
        blocked[t < policy.tau] = 0.0
        C_install = float(_trapz(blocked, t))
    if policy.kind == "protect":
        displaced = np.zeros_like(t)
        for i, ti in enumerate(t):
            if ti < policy.tau:
                continue
            d0 = rsi_diagnostics(params, sim.H[i], sim.A[i], sim.q[i], alignment,
                                 t=ti, intervention=None)
            dp = rsi_diagnostics(params, sim.H[i], sim.A[i], sim.q[i], alignment,
                                 t=ti, intervention=policy)
            displaced[i] = max(0.0, d0.E_AI_allocated - dp.E_AI_allocated)
        C_protect = float(_trapz(displaced, t))
    return {
        "C_install_hardware_units": C_install,
        "C_protect_MWh": C_protect,
        "E_build_MWh": float(_trapz(params.c_build * sim.B, t)),
        "C_duration_years": float(max(0.0, params.T - policy.tau) if policy.kind != "none" else 0.0),
    }


def run_grid(background, thresholds):
    no_ai_params = replace_params(background)
    no_ai = simulate_rsi(no_ai_params, 0.0, terminate_on_extinction=False)
    rows = []

    def add(policy, name):
        sim = simulate_rsi(background, 0.0, intervention=policy,
                           terminate_on_extinction=False)
        risk = assess_risk(sim.t, sim.H, sim.s_H, background.H0, thresholds,
                           p_bad=sim.p_bad_final_window, extinction_event_time=sim.extinction_time)
        damage = paired_damage(sim.t, sim.H, no_ai.t, no_ai.H)
        row = {
            "policy": name, "kind": policy.kind, "tau": policy.tau,
            "strength": (policy.u_bar if policy.kind == "protect"
                         else policy.cap_fraction if policy.kind == "cap" else np.nan),
            "alignment": 0.0,
            "risk_outcome": risk.outcome,
            "extinction": risk.extinction,
            "rapid_contraction": risk.rapid_contraction,
            "rapid_collapse": risk.rapid_collapse,
            "cumulative_collapse": risk.cumulative_collapse,
            "catastrophe": risk.catastrophe,
            "terminal_extinction": risk.terminal_extinction,
            "recovered_after_extinction": risk.recovered_after_extinction,
            "extinction_time": risk.extinction_time,
            "rapid_collapse_time": risk.rapid_collapse_time,
            "rapid_contraction_time": risk.rapid_contraction_time,
            "cumulative_loss": risk.cumulative_loss,
            "max_total_loss": risk.max_total_loss,
            "max_rapid_loss": risk.max_rapid_loss,
            "final_window_bad_fraction": risk.final_window_bad_fraction,
            "min_H": sim.min_H,
            "final_H": float(sim.H[-1]),
            "min_s_H": float(np.min(sim.s_H)),
            "final_s_H": float(sim.s_H[-1]),
            "paired_final_damage": damage["final_damage"],
            "paired_mean_damage": damage["mean_damage"],
            "paired_max_damage": damage["max_damage"],
            "no_ai_risk_outcome": assess_risk(no_ai.t, no_ai.H, no_ai.s_H,
                                              no_ai_params.H0, thresholds,
                                              p_bad=no_ai.p_bad_final_window,
                                              extinction_event_time=no_ai.extinction_time).outcome,
            **cost_metrics(sim, background, 0.0, policy),
        }
        rows.append(row)

    add(Intervention(kind="none"), "none")
    for tau in [0.0, 25.0, 50.0, 75.0]:
        for u in [0.5, 0.8, 1.0]:
            add(Intervention(kind="protect", tau=tau, u_bar=u), "R")
        for c in [0.1, 0.5, 1.0]:
            add(Intervention(kind="cap", tau=tau, cap_fraction=c,
                             tau_cap=background.tau_build), "C")
    return pd.DataFrame(rows)


def replace_params(params):
    from dataclasses import replace
    return replace(params, A0=0.0, rho=0.0)


def main():
    thresholds = RiskThresholds(H_ext=1e8, H_min=2e8, delta_years=10.0,
                                q_rapid=0.5, q_total=0.9, W_window=10.0,
                                s_min=0.8, p_tol=0.0)
    reference = base_rsi()
    reference = reference.__class__(**{**reference.__dict__,
                                       "H_ext": 1e8, "H_min": 2e8})
    stress = scenario_collapse_stress()
    main = run_grid(reference, thresholds)
    stress_df = run_grid(stress, thresholds)
    main.to_csv(TABLES / "part_v_risk_main_experiments.csv", index=False)
    stress_df.to_csv(TABLES / "part_v_risk_stress_experiments.csv", index=False)
    main[["policy", "tau", "strength", "risk_outcome", "extinction",
          "terminal_extinction", "recovered_after_extinction", "rapid_collapse",
          "cumulative_collapse", "extinction_time", "final_H", "final_s_H",
          "cumulative_loss", "max_total_loss", "paired_final_damage",
          "C_install_hardware_units", "C_protect_MWh" ]].to_csv(
        TABLES / "part_v_risk_main_summary.csv", index=False)
    stress_df[["policy", "tau", "strength", "risk_outcome", "extinction",
               "terminal_extinction", "recovered_after_extinction", "rapid_collapse",
               "cumulative_collapse", "extinction_time", "final_H", "final_s_H",
               "cumulative_loss", "max_total_loss", "paired_final_damage",
               "C_install_hardware_units", "C_protect_MWh" ]].to_csv(
        TABLES / "part_v_risk_stress_summary.csv", index=False)
    manifest = {
        "thresholds": thresholds.__dict__,
        "reference": {"H0": reference.H0, "H_ext": reference.H_ext,
                      "H_min": reference.H_min, "runs": len(main),
                      "outcomes": main.risk_outcome.value_counts().to_dict()},
        "stress": {"H0": stress.H0, "H_ext": stress.H_ext,
                   "H_min": stress.H_min, "runs": len(stress_df),
                   "outcomes": stress_df.risk_outcome.value_counts().to_dict()},
        "note": "Population ODE unchanged; risk hierarchy only. Old H_ext=1e6 results are legacy.",
    }
    (TABLES / "part_v_risk_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("reference outcomes", main.risk_outcome.value_counts().to_dict())
    print("stress outcomes", stress_df.risk_outcome.value_counts().to_dict())
    print(stress_df[["policy", "tau", "strength", "risk_outcome", "extinction_time",
                     "final_H", "final_s_H", "paired_final_damage",
                     "C_install_hardware_units", "C_protect_MWh"]].to_string(index=False))


if __name__ == "__main__":
    main()
