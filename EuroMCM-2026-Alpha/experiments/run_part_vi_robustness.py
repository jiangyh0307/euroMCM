"""Part VI robustness: critical-time windows for five pre-specified parameter sets."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from alpha.rsi import Intervention, simulate_rsi
from alpha.risk import RiskThresholds, assess_risk
from alpha.scenarios import scenario_collapse_stress

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results/tables"
FIGURES = ROOT / "results/figures"


def run_tau(params, thresholds, name, policy_name, policy_maker, tau, stage):
    policy = policy_maker(float(tau))
    sim = simulate_rsi(params, 0.0, intervention=policy,
                       terminate_on_extinction=False, max_step=0.5)
    risk = assess_risk(sim.t, sim.H, sim.s_H, params.H0, thresholds,
                       p_bad=sim.p_bad_final_window, extinction_event_time=sim.extinction_time)
    minH = float(np.min(sim.H))
    finalH = float(sim.H[-1])
    return {
        "set": name, "policy": policy_name, "stage": stage, "tau": float(tau),
        "prevent_success": bool(not np.isfinite(sim.extinction_time)),
        "recover_success": bool(finalH > thresholds.H_ext),
        "risk_outcome": risk.outcome,
        "min_H": minH, "final_H": finalH,
        "final_s_H": float(sim.s_H[-1]),
        "extinction_time": risk.extinction_time,
        "recovered_after_extinction": risk.recovered_after_extinction,
        "rapid_collapse": risk.rapid_collapse,
        "cumulative_collapse": risk.cumulative_collapse,
        "final_window_bad_fraction": risk.final_window_bad_fraction,
    }


def scan_metric(params, thresholds, name, policy_name, maker, taus, stage, column):
    rows = [run_tau(params, thresholds, name, policy_name, maker, t, stage)
            for t in taus]
    df = pd.DataFrame(rows)
    success = df[df[column]].tau.to_numpy(dtype=float)
    failure = df[~df[column]].tau.to_numpy(dtype=float)
    last_success = float(success.max()) if success.size else None
    first_failure = float(failure.min()) if failure.size else None
    return rows, last_success, first_failure, df


def refine_around(params, thresholds, name, policy_name, maker, last_success,
                  first_failure, step, lo, hi):
    if last_success is None or first_failure is None:
        return []
    left = max(lo, last_success - 1.0)
    right = min(hi, first_failure + 1.0)
    taus = np.arange(left, right + 1e-12, step)
    return [run_tau(params, thresholds, name, policy_name, maker, t, "refine")
            for t in taus]


def main():
    config = yaml.safe_load((ROOT / "configs/part_vi_robustness.yaml").read_text())
    thresholds = RiskThresholds(**config["risk"])
    base = scenario_collapse_stress()
    tau_min = float(config["scan"]["tau_min"])
    tau_max = float(config["scan"]["tau_max"])
    coarse = np.arange(tau_min, tau_max + 1e-12, float(config["scan"]["coarse_step"]))
    refine_step = float(config["scan"]["refine_step"])
    policies = {
        "R": lambda tau: Intervention(kind="protect", tau=tau,
                                      u_bar=float(config["policies"]["R"]["u_bar"])),
        "C": lambda tau: Intervention(kind="cap", tau=tau,
                                      cap_fraction=float(config["policies"]["C"]["cap_fraction"]),
                                      tau_cap=base.tau_build),
    }
    all_rows, summary_rows = [], []
    for set_name, spec in config["sets"].items():
        print(f"set {set_name}", flush=True)
        overrides = spec.get("overrides", {}) or {}
        params = replace(base, **{k: float(v) for k, v in overrides.items()})
        no_ai = replace(params, A0=0.0, rho=0.0)
        no_sim = simulate_rsi(no_ai, 0.0, terminate_on_extinction=False)
        no_risk = assess_risk(no_sim.t, no_sim.H, no_sim.s_H, params.H0,
                              thresholds, p_bad=no_sim.p_bad_final_window, extinction_event_time=no_sim.extinction_time)
        ai0 = simulate_rsi(params, 0.0, intervention=None,
                           terminate_on_extinction=False)
        ai0_risk = assess_risk(ai0.t, ai0.H, ai0.s_H, params.H0, thresholds,
                               p_bad=ai0.p_bad_final_window, extinction_event_time=ai0.extinction_time)
        for policy_name, maker in policies.items():
            print(f"  policy {policy_name}: coarse scan", flush=True)
            rows = []
            boundary = {}
            for column, label in [("prevent_success", "prevent"),
                                  ("recover_success", "recover")]:
                coarse_rows, last, first, _ = scan_metric(
                    params, thresholds, set_name, policy_name, maker,
                    coarse, "coarse", column)
                rows.extend(coarse_rows)
                print(f"  policy {policy_name}: refine {label} boundary", flush=True)
                refined = refine_around(params, thresholds, set_name, policy_name,
                                        maker, last, first, refine_step,
                                        tau_min, tau_max)
                rows.extend(refined)
                if refined:
                    rdf = pd.DataFrame(refined)
                    rlast = rdf[rdf[column]].tau.max() if rdf[column].any() else np.nan
                    rfirst = rdf[~rdf[column]].tau.min() if (~rdf[column]).any() else np.nan
                    boundary[label] = {
                        "last_success": float(rlast) if np.isfinite(rlast) else None,
                        "first_failure": float(rfirst) if np.isfinite(rfirst) else None,
                    }
                else:
                    boundary[label] = {"last_success": last, "first_failure": first}
            all_rows.extend(rows)
            p, r = boundary["prevent"], boundary["recover"]
            window = (None if p["last_success"] is None or r["last_success"] is None
                      else float(r["last_success"] - p["last_success"]))
            summary_rows.append({
                "set": set_name, "description": spec.get("description", ""),
                "policy": policy_name,
                "prevent_last_success": p["last_success"],
                "prevent_first_failure": p["first_failure"],
                "recover_last_success": r["last_success"],
                "recover_first_failure": r["first_failure"],
                "window_years": window,
                "no_ai_outcome": no_risk.outcome,
                "no_ai_terminal": no_risk.terminal_extinction,
                "no_ai_final_H": float(no_sim.H[-1]),
                "no_ai_extinction_time": no_risk.extinction_time,
                "no_intervention_outcome": ai0_risk.outcome,
                "no_intervention_extinction_time": ai0_risk.extinction_time,
                "no_intervention_final_H": float(ai0.H[-1]),
                "coarse_step": float(config["scan"]["coarse_step"]),
                "refine_step": refine_step,
            })
    full = pd.DataFrame(all_rows)
    summary = pd.DataFrame(summary_rows)
    full.to_csv(TABLES / "part_vi_robustness_tau_scan.csv", index=False)
    summary.to_csv(TABLES / "part_vi_robustness_summary.csv", index=False)
    manifest = {
        "pre_specified": True,
        "sets": config["sets"],
        "policies": config["policies"],
        "thresholds": config["risk"],
        "scan": config["scan"],
        "note": "Boundary values are sampled-grid statements; no general monotonicity or irreversibility claim.",
    }
    (TABLES / "part_vi_robustness_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), sharey=True)
    for ax, policy in zip(axes, ["R", "C"]):
        sub = summary[summary.policy == policy].sort_values("set")
        x = np.arange(len(sub))
        ax.bar(x - 0.18, sub.prevent_last_success, width=0.36, color="#1f4e79",
               label="prevent last success")
        ax.bar(x + 0.18, sub.recover_last_success, width=0.36, color="#c55a11",
               label="recover last success")
        for i, (_, row) in enumerate(sub.iterrows()):
            if row.window_years is not None:
                ax.text(i, max(row.prevent_last_success or 0, row.recover_last_success or 0) + 1.5,
                        f"W={row.window_years:.1f}", ha="center", fontsize=8)
        ax.set_xticks(x)
        ax.set_xticklabels(sub.set, rotation=25, ha="right", fontsize=8)
        ax.set_ylim(0, 82)
        ax.set_title(f"Policy {policy}")
        ax.set_ylabel("last sampled successful tau (years)")
        ax.grid(axis="y", alpha=.25)
        ax.legend(fontsize=8)
    fig.suptitle("Part VI: sampled preventive/recovery deadlines across five pre-specified sets")
    fig.text(0.01, 0.005,
             "Bar values are last sampled successes; no bar/None means no success on the 0-75 year grid. "
             "Window W is the difference of last successes, not an exact continuous boundary.",
             fontsize=7.2, color="#444444")
    fig.tight_layout()
    fig.savefig(FIGURES / "part_vi_windows.png", bbox_inches="tight")
    fig.savefig(FIGURES / "part_vi_windows.pdf", bbox_inches="tight")
    plt.close(fig)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
