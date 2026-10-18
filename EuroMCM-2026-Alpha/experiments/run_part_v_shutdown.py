"""Fallible shutdown branches under the risk-revised stress background.

Success and failure are simulated separately; the mixture is exact conditioning
on the two branches for the assumed success probability p_s.
"""
from __future__ import annotations
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from alpha.rsi import Intervention, simulate_rsi
from alpha.risk import RiskThresholds, assess_risk
from alpha.scenarios import scenario_collapse_stress

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results/tables"
FIGURES = ROOT / "results/figures"


def branch_row(policy, tau, k, params, thresholds, branch):
    sim = simulate_rsi(params, 0.0, intervention=policy,
                       terminate_on_extinction=False)
    risk = assess_risk(sim.t, sim.H, sim.s_H, params.H0, thresholds,
                       p_bad=sim.p_bad_final_window, extinction_event_time=sim.extinction_time)
    return {
        "branch": branch, "tau": tau, "shutdown_fraction": k,
        "risk_outcome": risk.outcome,
        "extinction": risk.extinction,
        "terminal_extinction": risk.terminal_extinction,
        "recovered_after_extinction": risk.recovered_after_extinction,
        "rapid_collapse": risk.rapid_collapse,
        "cumulative_collapse": risk.cumulative_collapse,
        "extinction_time": risk.extinction_time,
        "final_H": float(sim.H[-1]),
        "min_H": sim.min_H,
        "final_s_H": float(sim.s_H[-1]),
        "final_window_bad_fraction": risk.final_window_bad_fraction,
        "operating_fraction_end": sim.numerical_diagnostics.get("operating_fraction_end", np.nan),
    }


def main():
    params = scenario_collapse_stress()
    thresholds = RiskThresholds(H_ext=params.H_ext, H_min=params.H_min,
                                delta_years=10.0, q_rapid=0.5, q_total=0.9,
                                W_window=params.W_window, s_min=params.s_min,
                                p_tol=params.p_tol)
    taus = [0.0, 25.0, 50.0, 75.0]
    ks = [0.5, 1.0]
    p_success_values = [0.5, 0.9]
    failure = {"branch": "failure (no effect)", "tau": np.nan, "shutdown_fraction": 0.0}
    fail_sim = simulate_rsi(params, 0.0, intervention=None,
                            terminate_on_extinction=False)
    fail_risk = assess_risk(fail_sim.t, fail_sim.H, fail_sim.s_H, params.H0,
                            thresholds, p_bad=fail_sim.p_bad_final_window, extinction_event_time=fail_sim.extinction_time)
    failures = {
        "risk_outcome": fail_risk.outcome,
        "extinction": fail_risk.extinction,
        "terminal_extinction": fail_risk.terminal_extinction,
        "recovered_after_extinction": fail_risk.recovered_after_extinction,
        "rapid_collapse": fail_risk.rapid_collapse,
        "cumulative_collapse": fail_risk.cumulative_collapse,
        "extinction_time": fail_risk.extinction_time,
        "final_H": float(fail_sim.H[-1]),
        "min_H": fail_sim.min_H,
        "final_s_H": float(fail_sim.s_H[-1]),
        "final_window_bad_fraction": fail_risk.final_window_bad_fraction,
    }
    branches = []
    for tau in taus:
        for k in ks:
            pol = Intervention(kind="shutdown", tau=tau, shutdown_fraction=k)
            row = branch_row(pol, tau, k, params, thresholds, "success")
            branches.append(row)
    branch_df = pd.DataFrame(branches)
    branch_df.to_csv(TABLES / "part_v_shutdown_branches.csv", index=False)

    mixture_rows = []
    for _, s in branch_df.iterrows():
        for p_s in p_success_values:
            mixture_rows.append({
                "tau": s.tau, "shutdown_fraction": s.shutdown_fraction,
                "p_success_assumed": p_s,
                "P_extinction": p_s * float(s.extinction) + (1 - p_s) * float(failures["extinction"]),
                "P_rapid_collapse": p_s * float(s.rapid_collapse) + (1 - p_s) * float(failures["rapid_collapse"]),
                "P_cumulative_collapse": p_s * float(s.cumulative_collapse) + (1 - p_s) * float(failures["cumulative_collapse"]),
                "P_recovered_after_extinction": p_s * float(s.recovered_after_extinction) + (1 - p_s) * float(failures["recovered_after_extinction"]),
                "expected_final_H": p_s * s.final_H + (1 - p_s) * failures["final_H"],
                "expected_min_H": p_s * s.min_H + (1 - p_s) * failures["min_H"],
                "expected_final_s_H": p_s * s.final_s_H + (1 - p_s) * failures["final_s_H"],
                "expected_final_window_bad_fraction": p_s * s.final_window_bad_fraction + (1 - p_s) * failures["final_window_bad_fraction"],
                "note": "p_success is an assumed scenario parameter, not an empirical estimate.",
            })
    mixture = pd.DataFrame(mixture_rows)
    mixture.to_csv(TABLES / "part_v_shutdown_mixture.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    for tau, color in zip(taus, ["#1f4e79", "#c55a11", "#a50021", "#6a3d9a"]):
        s = simulate_rsi(params, 0.0, intervention=Intervention(
            kind="shutdown", tau=tau, shutdown_fraction=1.0),
            terminate_on_extinction=False)
        ax.plot(s.t, s.H, color=color, lw=1.5, label=f"shutdown tau={tau:g}")
    ax.plot(fail_sim.t, fail_sim.H, "k--", lw=1.3, label="failure / no effect")
    ax.axhline(params.H_ext, color="black", ls=":", lw=1.0, label="$H_{ext}$")
    ax.set_yscale("log")
    ax.set_xlabel("time (years)")
    ax.set_ylabel("human population (persons, log scale)")
    ax.set_title("Fallible full shutdown: success branches vs failure branch")
    ax.legend(fontsize=8)
    fig.text(0.01, 0.005,
             "p_success is not estimated here. First-passage and recovery are distinct; "
             "the failed branch is no intervention.",
             fontsize=7.2, color="#444444")
    fig.tight_layout()
    fig.savefig(FIGURES / "part_v_shutdown.png", bbox_inches="tight")
    fig.savefig(FIGURES / "part_v_shutdown.pdf", bbox_inches="tight")
    plt.close(fig)

    manifest = {
        "background": "scenario_collapse_stress",
        "thresholds": thresholds.__dict__,
        "taus": taus, "shutdown_fractions": ks,
        "p_success_assumed": p_success_values,
        "failure_branch": failures,
        "note": "Branch mixture is exact conditional on Z; p_success is assumed, not calibrated. No monetary cost.",
    }
    (TABLES / "part_v_shutdown_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(mixture.to_string(index=False))


if __name__ == "__main__":
    main()
