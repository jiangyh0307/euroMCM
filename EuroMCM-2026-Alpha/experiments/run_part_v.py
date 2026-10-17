"""Part V minimal policy experiment: resource protection R vs installation cap C.

25 deterministic main runs: 1 no-intervention + 12 R + 12 C on the reference
background. No policy benefit is assumed; metrics are computed from simulations.
"""
from __future__ import annotations

from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from alpha.rsi import Intervention, rsi_diagnostics, simulate_rsi
from alpha.scenarios import base_rsi

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results/tables"
FIGURES = ROOT / "results/figures"
_trapz = getattr(np, "trapezoid", np.trapz)


def _metrics(sim, params, alignment, policy):
    t, H, A, q = sim.t, sim.H, sim.A, sim.q
    s_H = sim.s_H
    T = params.T
    D_s = float(_trapz((s_H < params.s_min).astype(float), t))
    J_s = float(_trapz(np.maximum(params.s_min - s_H, 0.0), t) / (T * params.s_min))
    J_H = float(_trapz(np.maximum(params.H_min - H, 0.0), t) / (T * params.H_min))
    E_build = float(_trapz(params.c_build * sim.B, t))
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
            diag0 = rsi_diagnostics(params, float(H[i]), float(A[i]), float(q[i]),
                                    alignment, t=float(ti), intervention=None)
            diagp = rsi_diagnostics(params, float(H[i]), float(A[i]), float(q[i]),
                                    alignment, t=float(ti), intervention=policy)
            displaced[i] = max(0.0, diag0.E_AI_allocated - diagp.E_AI_allocated)
        C_protect = float(_trapz(displaced, t))
    C_duration = float(max(0.0, T - policy.tau) if policy.kind != "none" else 0.0)
    return {
        "outcome": sim.outcome,
        "success": sim.success,
        "min_H": sim.min_H,
        "final_H": float(H[-1]),
        "min_s_H": float(np.min(s_H)),
        "final_s_H": float(s_H[-1]),
        "p_bad": sim.p_bad_final_window,
        "D_s_years": D_s,
        "J_s": J_s,
        "J_H": J_H,
        "E_build_MWh": E_build,
        "C_install_hardware_units": C_install,
        "C_protect_MWh": C_protect,
        "C_duration_years": C_duration,
        "A_hardware_years": float(_trapz(A, t)),
        "mean_A": float(np.mean(A)),
        "mean_q": float(np.mean(q)),
        "final_q": float(q[-1]),
        "mean_zeta": float(np.mean(sim.zeta)),
        "final_zeta": float(sim.zeta[-1]),
        "extinction_time": sim.extinction_time,
        "capacity_violation": sim.capacity_violation,
    }


def run_one(name, policy, params, alignment=0.0):
    sim = simulate_rsi(params, alignment=alignment, intervention=policy,
                       terminate_on_extinction=False)
    row = {"policy": name, "kind": policy.kind, "tau": policy.tau,
           "strength": (policy.u_bar if policy.kind == "protect"
                        else policy.cap_fraction if policy.kind == "cap" else np.nan),
           "alignment": alignment}
    row.update(_metrics(sim, params, alignment, policy))
    return row, sim


def main():
    params = base_rsi()
    rows, simulations = [], {}
    base_policy = Intervention(kind="none")
    row, sim = run_one("none", base_policy, params)
    rows.append(row)
    simulations[("none", None)] = sim
    for tau in [0.0, 25.0, 50.0, 75.0]:
        for u in [0.5, 0.8, 1.0]:
            policy = Intervention(kind="protect", tau=tau, u_bar=u)
            row, sim = run_one("R", policy, params)
            rows.append(row)
            simulations[("R", (tau, u))] = sim
        for c in [0.1, 0.5, 1.0]:
            policy = Intervention(kind="cap", tau=tau, cap_fraction=c,
                                  tau_cap=params.tau_build)
            row, sim = run_one("C", policy, params)
            rows.append(row)
            simulations[("C", (tau, c))] = sim
    df = pd.DataFrame(rows)
    df.to_csv(TABLES / "part_v_main_experiments.csv", index=False)
    summary = df[["policy", "tau", "strength", "outcome", "min_H", "final_H",
                  "min_s_H", "final_s_H", "p_bad", "D_s_years", "J_s", "J_H",
                  "C_install_hardware_units", "C_protect_MWh", "E_build_MWh",
                  "C_duration_years", "mean_A", "final_q", "mean_zeta"]].copy()
    summary.to_csv(TABLES / "part_v_main_summary.csv", index=False)

    base = df[df.policy == "none"].iloc[0]
    plt.rcParams.update({"figure.dpi": 130, "savefig.dpi": 300, "font.size": 10,
                         "axes.grid": True, "grid.alpha": .25})
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.7))
    for u, color in zip([0.5, 0.8, 1.0], ["#1f4e79", "#c55a11", "#a50021"]):
        sub = df[(df.policy == "R") & np.isclose(df.strength, u)].sort_values("tau")
        axes[0].plot(sub.tau, 100.0 * (sub.final_H - base.final_H) / base.final_H,
                     "o-", color=color, label=f"u={u}")
        axes[1].plot(sub.tau, sub.p_bad, "o-", color=color, label=f"u={u}")
        axes[2].plot(sub.tau, sub.D_s_years, "o-", color=color, label=f"u={u}")
    for ax, ylabel in zip(axes, ["final H change vs no intervention (%)",
                                 "final-window p_bad",
                                 "s_H<s_min duration (years)"]):
        ax.axhline((0.0 if ax is axes[0] else
                    base.p_bad if ax is axes[1] else base.D_s_years),
                   color="black", ls="--", lw=1.0, label="no intervention")
        if ax is axes[1]:
            ax.text(0.02, 0.92, "all 25 reference runs: p_bad = 0",
                    transform=ax.transAxes, fontsize=8)
        ax.set_xlabel("activation time tau (years)")
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=8)
    fig.suptitle("Policy R: resource protection timing and strength; reference background")
    fig.tight_layout()
    for ext in ["png", "pdf"]:
        fig.savefig(FIGURES / f"part_v_R_timing.{ext}", bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.7))
    for c, color in zip([0.1, 0.5, 1.0], ["#1f4e79", "#c55a11", "#a50021"]):
        sub = df[(df.policy == "C") & np.isclose(df.strength, c)].sort_values("tau")
        axes[0].plot(sub.tau, 100.0 * (sub.final_H - base.final_H) / base.final_H,
                     "o-", color=color, label=f"C/A_max={c}")
        axes[1].plot(sub.tau, sub.p_bad, "o-", color=color, label=f"C/A_max={c}")
        axes[2].plot(sub.tau, sub.C_install_hardware_units / 1e3, "o-", color=color,
                     label=f"C/A_max={c}")
    for ax, ylabel in zip(axes, ["final H change vs no intervention (%)",
                                 "final-window p_bad",
                                 "blocked new installation (10^3 units)"]):
        ax.axhline((0.0 if ax is axes[0] else
                    base.p_bad if ax is axes[1] else 0.0),
                   color="black", ls="--", lw=1.0, label="no intervention")
        if ax is axes[1]:
            ax.text(0.02, 0.92, "all 25 reference runs: p_bad = 0",
                    transform=ax.transAxes, fontsize=8)
        ax.set_xlabel("activation time tau (years)")
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=8)
    fig.suptitle("Policy C: new-installation cap timing and strength; reference background")
    fig.tight_layout()
    for ext in ["png", "pdf"]:
        fig.savefig(FIGURES / f"part_v_C_timing.{ext}", bbox_inches="tight")
    plt.close(fig)

    # Assemble a compact actual-results table for the handoff.
    concise = summary.copy()
    concise["final_H"] = concise.final_H / 1e9
    concise["final_H"] = concise["final_H"].round(6)
    concise.to_csv(TABLES / "part_v_main_summary_compact.csv", index=False)
    print(df[["policy", "tau", "strength", "outcome", "final_H", "final_s_H",
              "p_bad", "D_s_years", "J_s", "C_install_hardware_units",
              "C_protect_MWh"]].to_string(index=False))
    print("saved", len(df), "main policy runs")


if __name__ == "__main__":
    main()
