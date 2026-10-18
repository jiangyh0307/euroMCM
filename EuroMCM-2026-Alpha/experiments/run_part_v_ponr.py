"""Point-of-no-return scan for the two effective Part V policies.

Preventive success: min_t H(t) > H_ext.
Recovery success: H(T) > H_ext, allowing an earlier crossing.
The scan reports the full sampled success set; no monotonicity is assumed.
"""
from __future__ import annotations

from pathlib import Path
import argparse
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


def scan(policy_name, make_policy, taus, params, thresholds):
    rows, sims = [], {}
    for tau in taus:
        policy = make_policy(float(tau))
        sim = simulate_rsi(params, 0.0, intervention=policy,
                           terminate_on_extinction=False)
        risk = assess_risk(sim.t, sim.H, sim.s_H, params.H0, thresholds,
                           p_bad=sim.p_bad_final_window, extinction_event_time=sim.extinction_time)
        minH = float(np.min(sim.H))
        finalH = float(sim.H[-1])
        row = {
            "policy": policy_name,
            "tau": float(tau),
            "risk_outcome": risk.outcome,
            "prevent_success": bool(not np.isfinite(sim.extinction_time)),
            "recover_success": bool(finalH > thresholds.H_ext),
            "min_H": minH,
            "final_H": finalH,
            "final_s_H": float(sim.s_H[-1]),
            "extinction_time": risk.extinction_time,
            "recovered_after_extinction": risk.recovered_after_extinction,
            "rapid_collapse": risk.rapid_collapse,
            "cumulative_collapse": risk.cumulative_collapse,
            "final_window_bad_fraction": risk.final_window_bad_fraction,
        }
        rows.append(row)
        sims[float(tau)] = sim
    return pd.DataFrame(rows), sims


def success_summary(df, column, taus):
    mask = df[column].to_numpy(dtype=bool)
    successful = df.loc[mask, "tau"].to_numpy(dtype=float)
    if successful.size == 0:
        return {"success_set": [], "sup": None, "min": None, "max": None,
                "contiguous": False, "grid_limited": False}
    # Success set is contiguous only on the sampled grid and only if every
    # sampled tau between its min and max succeeded.
    grid = np.asarray(taus, dtype=float)
    between = (grid >= successful.min()) & (grid <= successful.max())
    contiguous = bool(np.all(np.isin(grid[between], successful)))
    return {
        "success_set": successful.tolist(),
        "sup": float(successful.max()),
        "min": float(successful.min()),
        "max": float(successful.max()),
        "contiguous": contiguous,
        "grid_limited": bool(successful.max() == grid.max()),
    }


def trajectory_figure(df, sims, policy_name, thresholds, path_png, path_pdf):
    prevent = success_summary(df, "prevent_success", df.tau.tolist())
    recover = success_summary(df, "recover_success", df.tau.tolist())
    candidates = [0.0]
    for item in [prevent["sup"], recover["sup"]]:
        if item is not None:
            candidates.append(item)
            candidates.append(max(0.0, item - 1.0))
            candidates.append(min(float(df.tau.max()), item + 1.0))
    available = sorted(sims)
    candidates = sorted(set(min(available, key=lambda x: abs(x - c)) for c in candidates))[:6]
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    for tau in candidates:
        sim = sims[tau]
        ax.plot(sim.t, sim.H, lw=1.6, label=f"tau={tau:g} yr")
    ax.axhline(thresholds.H_ext, color="black", ls="--", lw=1.2,
               label="$H_{ext}$")
    ax.set_yscale("log")
    ax.set_xlabel("time (years)")
    ax.set_ylabel("human population (persons, log scale)")
    ax.set_title(f"{policy_name}: trajectories around sampled critical times")
    ax.legend(fontsize=8)
    fig.text(0.01, 0.005,
             "Preventive success: min H > H_ext. Recovery success: H(T) > H_ext. "
             "First passage and recovery are distinct; no irreversible-extinction claim.",
             fontsize=7.2, color="#444444")
    fig.tight_layout()
    fig.savefig(path_png, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", type=float, default=1.0)
    parser.add_argument("--max-tau", type=float, default=75.0)
    args = parser.parse_args()
    params = scenario_collapse_stress()
    thresholds = RiskThresholds(H_ext=params.H_ext, H_min=params.H_min,
                                delta_years=10.0, q_rapid=0.5, q_total=0.9,
                                W_window=params.W_window, s_min=params.s_min,
                                p_tol=params.p_tol)
    taus = np.arange(0.0, args.max_tau + 1e-12, args.step)
    policies = {
        "R_u0.8": lambda tau: Intervention(kind="protect", tau=tau, u_bar=0.8),
        "C_c0.1": lambda tau: Intervention(kind="cap", tau=tau, cap_fraction=0.1,
                                           tau_cap=params.tau_build),
    }
    all_rows, summaries, all_sims = [], [], {}
    for name, maker in policies.items():
        df, sims = scan(name, maker, taus, params, thresholds)
        all_rows.append(df)
        all_sims[name] = (df, sims)
        prevent = success_summary(df, "prevent_success", taus)
        recover = success_summary(df, "recover_success", taus)
        summary = {
            "policy": name,
            "tau_grid": [float(taus.min()), float(taus.max()), float(args.step)],
            "prevent": prevent,
            "recover": recover,
            "window_if_both": (None if prevent["sup"] is None or recover["sup"] is None
                               else float(recover["sup"] - prevent["sup"])),
            "no_monotonicity_assumed": True,
            "n_runs": len(df),
        }
        summaries.append(summary)
        trajectory_figure(df, sims, name, thresholds,
                          FIGURES / f"part_v_ponr_{name}.png",
                          FIGURES / f"part_v_ponr_{name}.pdf")
    full = pd.concat(all_rows, ignore_index=True)
    full.to_csv(TABLES / "part_v_ponr_scan.csv", index=False)
    pd.DataFrame(summaries).to_csv(TABLES / "part_v_ponr_summary.csv", index=False)
    manifest = {
        "background": "scenario_collapse_stress",
        "thresholds": thresholds.__dict__,
        "tau_step": args.step,
        "tau_max": args.max_tau,
        "policies": list(policies),
        "summary": summaries,
        "note": "Success sets are sampled-grid statements. No monotonicity, unique threshold or irreversibility is assumed.",
    }
    (TABLES / "part_v_ponr_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
