"""Part V exploratory pressure slice: same policy grid under the joint stress scenario.

This is separate from the reference-background 25-run comparison. It is included
only to exercise policies when the no-intervention path is not non-marginal.
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from alpha.rsi import Intervention, simulate_rsi
from alpha.scenarios import scenario_stress
from run_part_v import _metrics

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results/tables"
FIGURES = ROOT / "results/figures"


def run_one(name, policy, params, alignment=0.0):
    sim = simulate_rsi(params, alignment=alignment, intervention=policy,
                       terminate_on_extinction=False)
    row = {"policy": name, "kind": policy.kind, "tau": policy.tau,
           "strength": (policy.u_bar if policy.kind == "protect"
                        else policy.cap_fraction if policy.kind == "cap" else float("nan")),
           "alignment": alignment}
    row.update(_metrics(sim, params, alignment, policy))
    return row


def main():
    params = scenario_stress()
    rows = [run_one("none", Intervention(kind="none"), params)]
    for tau in [0.0, 25.0, 50.0, 75.0]:
        for u in [0.5, 0.8, 1.0]:
            rows.append(run_one("R", Intervention(kind="protect", tau=tau, u_bar=u), params))
        for c in [0.1, 0.5, 1.0]:
            rows.append(run_one("C", Intervention(kind="cap", tau=tau,
                                                  cap_fraction=c,
                                                  tau_cap=params.tau_build), params))
    df = pd.DataFrame(rows)
    df.to_csv(TABLES / "part_v_stress_experiments.csv", index=False)
    base = df[df.policy == "none"].iloc[0]
    plt.rcParams.update({"figure.dpi": 130, "savefig.dpi": 300, "font.size": 10,
                         "axes.grid": True, "grid.alpha": .25})
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.7))
    for u, color in zip([0.5, 0.8, 1.0], ["#1f4e79", "#c55a11", "#a50021"]):
        sub = df[(df.policy == "R") & (df.strength == u)].sort_values("tau")
        axes[0].plot(sub.tau, sub.final_H / 1e9, "o-", color=color, label=f"u={u}")
        axes[1].plot(sub.tau, sub.p_bad, "o-", color=color, label=f"u={u}")
        axes[2].plot(sub.tau, sub.D_s_years, "o-", color=color, label=f"u={u}")
    axes[0].axhline(base.final_H / 1e9, color="black", ls="--", label="no intervention")
    axes[1].axhline(base.p_bad, color="black", ls="--", label="no intervention")
    axes[2].axhline(base.D_s_years, color="black", ls="--", label="no intervention")
    for ax, ylabel in zip(axes, ["final H (billions)", "final-window p_bad",
                                 "s_H<s_min duration (years)"]):
        ax.set_xlabel("activation time tau (years)")
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=8)
    fig.suptitle("Policy R under joint stress: exploratory pressure slice (not the reference comparison)")
    fig.tight_layout()
    for ext in ["png", "pdf"]:
        fig.savefig(FIGURES / f"part_v_stress_R_timing.{ext}", bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.7))
    for c, color in zip([0.1, 0.5, 1.0], ["#1f4e79", "#c55a11", "#a50021"]):
        sub = df[(df.policy == "C") & (df.strength == c)].sort_values("tau")
        axes[0].plot(sub.tau, sub.final_H / 1e9, "o-", color=color, label=f"C/A_max={c}")
        axes[1].plot(sub.tau, sub.p_bad, "o-", color=color, label=f"C/A_max={c}")
        axes[2].plot(sub.tau, sub.C_install_hardware_units / 1e3, "o-", color=color,
                     label=f"C/A_max={c}")
    axes[0].axhline(base.final_H / 1e9, color="black", ls="--", label="no intervention")
    axes[1].axhline(base.p_bad, color="black", ls="--", label="no intervention")
    for ax, ylabel in zip(axes, ["final H (billions)", "final-window p_bad",
                                 "blocked new installation (10^3 units)"]):
        ax.set_xlabel("activation time tau (years)")
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=8)
    fig.suptitle("Policy C under joint stress: exploratory pressure slice (not the reference comparison)")
    fig.tight_layout()
    for ext in ["png", "pdf"]:
        fig.savefig(FIGURES / f"part_v_stress_C_timing.{ext}", bbox_inches="tight")
    plt.close(fig)
    print(df[["policy", "tau", "strength", "outcome", "min_H", "final_H",
              "final_s_H", "p_bad", "D_s_years", "C_install_hardware_units",
              "C_protect_MWh"]].to_string(index=False))


if __name__ == "__main__":
    main()
