"""Generate Part III alignment phase diagram, safe-state slice, and thresholds."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import pandas as pd

from alpha.alignment import alignment_scan, phase_diagram, safe_initial_states, scan_summary
from alpha.rsi import simulate_rsi
from alpha.scenarios import scenario_stress
from alpha.viability import viability_certificate

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
TAB = ROOT / "results" / "tables"
FIG.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)

OUTCOME_TO_INT = {"extinction": 0, "marginal": 1, "non_marginal": 2, "failed": 3}
COLORS = ["#b2182b", "#f4a582", "#1b7837", "#bdbdbd"]


def _style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 130,
            "savefig.dpi": 300,
            "font.size": 10,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def figure5(phase: pd.DataFrame, cert, path_png: Path, path_pdf: Path) -> None:
    a_vals = np.sort(phase["a"].unique())
    eta_vals = np.sort(phase["eta"].unique())
    grid = np.full((eta_vals.size, a_vals.size), np.nan)
    for _, row in phase.iterrows():
        i = int(np.argmin(np.abs(eta_vals - row["eta"])))
        j = int(np.argmin(np.abs(a_vals - row["a"])))
        grid[i, j] = OUTCOME_TO_INT[row["outcome"]]
    cmap = ListedColormap(COLORS)
    norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], cmap.N)
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.2), gridspec_kw={"width_ratios": [1.35, 1.0]})
    ax = axes[0]
    im = ax.pcolormesh(
        a_vals,
        eta_vals,
        grid,
        shading="nearest",
        cmap=cmap,
        norm=norm,
    )
    ax.set_xlim(a_vals.min() - 0.05, a_vals.max() + 0.05)
    ax.set_ylim(eta_vals.min() / 1.15, eta_vals.max() * 1.15)
    ax.set_yscale("log")
    ax.set_xlabel("Alignment $a$")
    ax.set_ylabel("RSI capability-growth parameter $\\eta$ (1/year, log scale)")
    ax.set_title("Alignment–RSI phase diagram: stress scenario")
    ax.axvline(cert.a_safe, color="black", ls="--", lw=1.5)
    ax.text(
        cert.a_safe + 0.018,
        eta_vals.min() * 1.25,
        f"$a_{{safe}}$ = {cert.a_safe:.2f}\n(sufficient population-floor certificate)",
        fontsize=8.5,
        va="bottom",
    )
    cbar = fig.colorbar(im, ax=ax, ticks=[0, 1, 2, 3])
    cbar.ax.set_yticklabels(["Extinction", "Marginal", "Non-marginal", "Failed"])

    ax2 = axes[1]
    eta_fixed = 0.5
    sub = phase[np.isclose(phase["eta"], eta_fixed)].sort_values("a")
    ax2.plot(sub["a"], sub["min_H"], marker="o", color="#1f4e79", lw=1.8, label="$\\min_{t\\leq T} H(t)$")
    ax2.set_yscale("log")
    ax2.axhline(cert.a_safe * 0 + 1.0e7, color="#555555", ls=":", lw=1.0, label="$H_{min}$")
    ax2.axhline(1.0e6, color="#b2182b", ls="--", lw=1.0, label="$H_{ext}$")
    ax2.axvline(cert.a_safe, color="black", ls="--", lw=1.2, label="$a_{safe}$ (certificate)")
    ax2.set_xlabel("Alignment $a$")
    ax2.set_ylabel("minimum human population (persons, log scale)")
    ax2.set_title(f"Fixed $\\eta$ = {eta_fixed}: numerical minimum vs analytic threshold")
    ax2.legend(frameon=True, fontsize=8)

    fig.text(
        0.01,
        0.005,
        "Stress-scenario parameters are conditional assumptions. The analytic certificate is a sufficient population-floor condition, "
        "not non-marginal welfare and not a real-world safety guarantee.",
        fontsize=7.5,
        color="#444444",
    )
    fig.tight_layout()
    fig.savefig(path_png, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)


def figure_safe_states(df: pd.DataFrame, path_png: Path, path_pdf: Path) -> None:
    a_unique = sorted(df["a"].unique())
    fig, axes = plt.subplots(1, len(a_unique), figsize=(4.0 * len(a_unique), 4.4), sharey=True)
    if len(a_unique) == 1:
        axes = [axes]
    for ax, a in zip(axes, a_unique):
        sub = df[np.isclose(df["a"], a)]
        A_vals = np.sort(sub["A0"].unique())
        q_vals = np.sort(sub["q0"].unique())
        grid = np.full((A_vals.size, q_vals.size), np.nan)
        for _, row in sub.iterrows():
            i = int(np.argmin(np.abs(A_vals - row["A0"])))
            j = int(np.argmin(np.abs(q_vals - row["q0"])))
            grid[i, j] = 1.0 if row["population_floor"] else 0.0
        ax.pcolormesh(
            q_vals,
            A_vals,
            grid,
            shading="nearest",
            cmap=ListedColormap(["#f4a582", "#1b7837"]),
            vmin=0,
            vmax=1,
        )
        ax.set_xlim(q_vals.min() / 1.15, q_vals.max() * 1.15)
        ax.set_ylim(A_vals.min() / 1.3, A_vals.max() * 1.3)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("initial capability $q_0$ (log scale)")
        if ax is axes[0]:
            ax.set_ylabel("initial hardware $A_0$ (log scale)")
        ax.set_title(f"Population-floor safe slice, a = {a:.2f}")
    fig.text(
        0.01,
        0.005,
        "Green = min H >= H_min; orange = failure. This is a fixed-policy finite-horizon grid, not a control viability kernel.",
        fontsize=7.5,
        color="#444444",
    )
    fig.tight_layout()
    fig.savefig(path_png, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)


def figure_horizon(df: pd.DataFrame, path_png: Path, path_pdf: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    for T, sub in df.groupby("T"):
        sub = sub.sort_values("a")
        ax.plot(sub["a"], sub["min_H"], marker="o", lw=1.6, label=f"T = {T:g} yr")
    ax.set_yscale("log")
    ax.axhline(1.0e7, color="#555555", ls=":", lw=1.0, label="$H_{min}$")
    ax.axhline(1.0e6, color="#b2182b", ls="--", lw=1.0, label="$H_{ext}$")
    ax.set_xlabel("Alignment $a$")
    ax.set_ylabel("minimum human population (persons, log scale)")
    ax.set_title("Horizon sensitivity of the minimum population")
    ax.legend(frameon=True, fontsize=8)
    fig.tight_layout()
    fig.savefig(path_png, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    _style()
    base = scenario_stress()
    cert = viability_certificate(base, rho_max=base.rho)
    a_values = np.linspace(0.0, 1.0, 11)
    eta_values = np.array([0.02, 0.05, 0.1, 0.2, 0.5, 1.0])
    phase_rows = phase_diagram(base, a_values, eta_values)
    phase = pd.DataFrame(phase_rows)
    phase.to_csv(TAB / "alignment_phase_diagram.csv", index=False)
    figure5(phase, cert, FIG / "fig5_alignment_phase.png", FIG / "fig5_alignment_phase.pdf")

    rows = alignment_scan(base, a_values)
    scan = pd.DataFrame(rows)
    scan.to_csv(TAB / "alignment_scan.csv", index=False)
    summary = scan_summary(rows)
    with open(TAB / "alignment_summary.txt", "w", encoding="utf-8") as fh:
        fh.write(f"a_safe certificate: {cert.a_safe:.6f}\n")
        fh.write(f"b_under: {cert.b_under:.6f}\n")
        fh.write(f"a_num_population (grid): {summary['a_num_population']}\n")
        fh.write(f"a_num_non_marginal (grid): {summary['a_num_non_marginal']}\n")
        fh.write(f"safe population set: {summary['safe_population_set']}\n")
        fh.write(f"non-marginal set: {summary['non_marginal_set']}\n")
        fh.write("monotonicity_assumed: False\n")
        fh.write(cert.assumptions + "\n")

    A_vals = np.array([1.0e3, 3.0e3, 1.0e4, 3.0e4, 1.0e5, 3.0e5, 9.0e5])
    q_vals = np.array([1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0])
    safe_rows = []
    for a in [0.0, 0.2, 0.4]:
        safe_rows.extend(safe_initial_states(base, a, A_vals, q_vals))
    safe_df = pd.DataFrame(safe_rows)
    safe_df.to_csv(TAB / "alignment_safe_initial_states.csv", index=False)
    figure_safe_states(safe_df, FIG / "figS_safe_initial_states.png", FIG / "figS_safe_initial_states.pdf")

    horizon_rows = []
    for T in [50.0, 100.0, 150.0]:
        p = replace(base, T=T)
        for a in [0.0, 0.25, 0.5, 0.75, 1.0]:
            sim = simulate_rsi(p, alignment=a, dt_internal=1.0)
            horizon_rows.append(
                {
                    "T": T,
                    "a": a,
                    "outcome": sim.outcome,
                    "min_H": sim.min_H,
                    "final_H": float(sim.H[-1]),
                    "final_s_H": float(sim.s_H[-1]),
                    "extinction_time": sim.extinction_time,
                    "p_bad": sim.p_bad_final_window,
                }
            )
    horizon = pd.DataFrame(horizon_rows)
    horizon.to_csv(TAB / "alignment_horizon_sensitivity.csv", index=False)
    figure_horizon(horizon, FIG / "figS_alignment_horizon.png", FIG / "figS_alignment_horizon.pdf")

    print(phase.to_string(index=False))
    print("a_safe", cert.a_safe, "a_num_pop", summary["a_num_population"])


if __name__ == "__main__":
    main()
