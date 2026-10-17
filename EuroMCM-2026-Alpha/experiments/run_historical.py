"""Generate Part I historical figures, tables, and compatibility diagnostics."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from alpha.historical import (
    HistoricalParameters,
    compatibility_scan,
    simulate_historical,
    summarize_scan,
)

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
TAB = ROOT / "results" / "tables"
FIG.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)


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


def _baseline_trajectory(base: HistoricalParameters, points: int = 500):
    sim0 = simulate_historical(base, max_step=25.0)
    horizon = sim0.T_rep if not sim0.censored else base.t_max
    t_eval = np.linspace(0.0, horizon, points)
    sim = simulate_historical(base, t_eval=t_eval, max_step=25.0)
    return sim


def figure1(sim, path_png: Path, path_pdf: Path) -> None:
    fig = plt.figure(figsize=(10.5, 7.4))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.7, 1.0, 0.75], hspace=0.42)
    ax = fig.add_subplot(gs[0])
    ax.plot(sim.t, sim.N, color="#1f4e79", lw=2.0, label="Neanderthal $N(t)$")
    ax.plot(sim.t, sim.M, color="#c55a11", lw=2.0, label="Modern human $M(t)$")
    ax.set_yscale("log")
    ax.set_xlabel("time (years)")
    ax.set_ylabel("population (persons, log scale)")
    ax.set_title("Historical resource competition: baseline scenario")
    ax.axhline(sim.params.N_crit, color="#1f4e79", ls=":", lw=1.2)
    ax.text(
        0.02,
        sim.params.N_crit * 1.25,
        f"$N_{{crit}}=\\kappa N_{{ref}}$ = {sim.params.N_crit:,.0f}",
        color="#1f4e79",
        fontsize=9,
    )
    if not sim.censored:
        ax.axvline(sim.T_rep, color="black", ls="--", lw=1.2)
        ax.annotate(
            f"$T_{{rep}}$ = {sim.T_rep:,.0f} yr",
            xy=(sim.T_rep, sim.N[-1]),
            xytext=(0.55, 0.25),
            textcoords="axes fraction",
            arrowprops=dict(arrowstyle="->", lw=1.0, color="black"),
            fontsize=10,
        )
    else:
        ax.text(
            0.55,
            0.25,
            "threshold not crossed within the horizon (censored)",
            transform=ax.transAxes,
            fontsize=10,
        )
    ax.legend(frameon=True, loc="upper right")

    ax2 = fig.add_subplot(gs[1])
    ax2.plot(sim.t, sim.s_N, color="#1f4e79", lw=1.8, label="$s_N(t)$")
    ax2.plot(sim.t, sim.s_M, color="#c55a11", lw=1.8, label="$s_M(t)$")
    ax2.axhline(sim.params.r_N(), color="#1f4e79", ls=":", lw=1.0)
    ax2.axhline(sim.params.r_M(), color="#c55a11", ls=":", lw=1.0)
    ax2.set_ylim(0, 1.02)
    ax2.set_xlabel("time (years)")
    ax2.set_ylabel("resource satisfaction")
    ax2.legend(frameon=True, ncol=2, loc="lower right")
    ax2.set_title("Allocated resource satisfaction; dotted lines are $r_i=\\delta_i/\\beta_i$", fontsize=10)

    ax3 = fig.add_subplot(gs[2])
    ax3.set_xlim(0, max(6000, sim.T_rep if not sim.censored else sim.params.t_max))
    ax3.set_ylim(0.3, 2.2)
    ax3.axhspan(1.82, 2.08, xmin=0, xmax=1, color="#d9e2f3", alpha=0.7)
    ax3.axhspan(0.82, 1.08, xmin=0, xmax=1, color="#fbe5d6", alpha=0.8)
    ax3.plot([2600, 5400], [1.95, 1.95], color="#1f4e79", lw=6, solid_capstyle="butt")
    ax3.plot([1400, 2900], [0.95, 0.95], color="#c55a11", lw=6, solid_capstyle="butt")
    if not sim.censored:
        ax3.plot([sim.T_rep], [1.95], marker="v", color="black", ms=9, label="baseline $T_{rep}$")
        ax3.plot([sim.T_rep], [0.95], marker="v", color="black", ms=9)
    ax3.set_yticks([0.95, 1.95])
    ax3.set_yticklabels(["France / N. Spain\n1,400–2,900 yr", "Europe\n2,600–5,400 yr"])
    ax3.set_xlabel("overlap duration (years)")
    ax3.set_title("Observed bands are durations, not calendar intervals; the model is not calibrated to them", fontsize=9)
    ax3.grid(axis="y", visible=False)

    fig.text(
        0.01,
        0.005,
        "Baseline values are scenario assumptions (see docs/mathematical_model.md and src/alpha/parameters.py). "
        "This is a compatibility demonstration, not causal validation.",
        fontsize=7.5,
        color="#444444",
    )
    fig.savefig(path_png, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)


def figure2(rows, path_png: Path, path_pdf: Path, summary: dict) -> None:
    df = pd.DataFrame(rows)
    w = np.sort(df["w_ratio"].unique())
    b = np.sort(df["beta_ratio"].unique())
    grid = np.full((b.size, w.size), np.nan)
    censored = np.zeros((b.size, w.size), dtype=bool)
    for _, row in df.iterrows():
        i = int(np.argmin(np.abs(b - row["beta_ratio"])))
        j = int(np.argmin(np.abs(w - row["w_ratio"])))
        if row["censored"] or row["status"] == "error":
            censored[i, j] = True
        else:
            grid[i, j] = row["T_rep"]
    masked = np.ma.masked_array(grid, mask=np.isnan(grid))
    fig, ax = plt.subplots(figsize=(8.4, 6.4))
    cmap = plt.get_cmap("viridis").copy()
    cmap.set_bad("#d9d9d9")
    mesh = ax.pcolormesh(w, b, masked, shading="auto", cmap=cmap, vmin=0, vmax=8000)
    cb = fig.colorbar(mesh, ax=ax)
    cb.set_label("$T_{rep}$ (years); grey = censored or incompatible run")

    try:
        finite = np.where(np.isnan(grid), 1e9, grid)
        cs = ax.contour(w, b, finite, levels=[2600, 5400], colors="white", linewidths=1.8, linestyles="--")
        ax.clabel(cs, fmt="%d yr", fontsize=8)
    except Exception:
        pass

    ax.axvline(1.0, color="white", lw=1.2, ls=":")
    ax.plot([1.0], [1.0], marker="*", color="red", ms=13, mec="white", mew=0.8, label="H0 baseline")
    ax.set_xlabel("$w_M/w_N$ (modern-human / Neanderthal acquisition-weight ratio)")
    ax.set_ylabel("$\\beta_M/\\beta_N$ (potential birth-rate ratio)")
    ax.set_title("Historical compatibility map (fixed remaining parameters)")
    ax.legend(loc="upper left", frameon=True)
    text = (
        f"compatible European cells: {summary['n_compatible_EU']}/{summary['n_valid']} "
        f"({100*summary['fraction_compatible_EU']:.1f}%)\n"
        f"censored: {summary['n_censored']}; errors: {summary['n_errors']}\n"
        "fraction is design-measure dependent, not a posterior probability"
    )
    ax.text(0.02, 0.02, text, transform=ax.transAxes, fontsize=8.2,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#888888", alpha=0.85))
    fig.text(
        0.01,
        0.005,
        "Each cell is an independent scenario with the baseline demographic and resource assumptions. "
        "Colored cells must not be read as calibrated history.",
        fontsize=7.4,
        color="#444444",
    )
    fig.savefig(path_png, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)


def sensitivity_tables(base: HistoricalParameters) -> pd.DataFrame:
    rows = []
    for kappa in [0.001, 0.005, 0.01, 0.02, 0.05]:
        p = replace(base, kappa=kappa)
        sim = simulate_historical(p, max_step=50.0)
        rows.append(
            {
                "analysis": "kappa",
                "value": kappa,
                "T_rep": sim.T_rep,
                "censored": sim.censored,
                "status": sim.status,
            }
        )
    for ratio in [0.01, 0.05, 0.1, 0.5, 1.0, 10.0]:
        p = replace(base, M0=base.N0 * ratio)
        sim = simulate_historical(p, max_step=50.0)
        rows.append(
            {
                "analysis": "M0_over_N0",
                "value": ratio,
                "T_rep": sim.T_rep,
                "censored": sim.censored,
                "status": sim.status,
            }
        )
    for diff in [100.0, 200.0, 350.0]:
        p = replace(base, m_N=base.m_M + diff)
        sim = simulate_historical(p, max_step=50.0)
        rows.append(
            {
                "analysis": "m_N_minus_m_M",
                "value": diff,
                "T_rep": sim.T_rep,
                "censored": sim.censored,
                "status": sim.status,
            }
        )
    for model, w_ratio in [("H0", 1.0), ("H1", 1.2)]:
        for beta_ratio in [0.9, 1.0, 1.1]:
            p = replace(base, w_M=base.w_N * w_ratio, beta_M=base.beta_N * beta_ratio)
            sim = simulate_historical(p, max_step=50.0)
            rows.append(
                {
                    "analysis": model,
                    "value": beta_ratio,
                    "w_ratio": w_ratio,
                    "T_rep": sim.T_rep,
                    "censored": sim.censored,
                    "status": sim.status,
                }
            )
    return pd.DataFrame(rows)


def figureS(sens: pd.DataFrame, path_png: Path, path_pdf: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.8))
    panels = [
        ("kappa", "$\\kappa$ (extinction threshold fraction)", "T_rep vs threshold"),
        ("M0_over_N0", "$M_0/N_0$ (initial ratio)", "T_rep vs initial ratio"),
        ("m_N_minus_m_M", "$m_N-m_M$ (kcal/person/day)", "T_rep vs energy difference"),
    ]
    for ax, (key, xlabel, title) in zip(axes, panels):
        sub = sens[sens["analysis"] == key].sort_values("value")
        ax.plot(sub["value"], sub["T_rep"], marker="o", color="#1f4e79", lw=1.7)
        ax.axhspan(2600, 5400, color="#d9e2f3", alpha=0.6)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("$T_{rep}$ (years)")
        ax.set_title(title)
        if key in {"M0_over_N0"}:
            ax.set_xscale("log")
        for _, r in sub.iterrows():
            if r["censored"]:
                ax.annotate("censored", (r["value"], ax.get_ylim()[1] * 0.92),
                            fontsize=7, color="#c55a11", ha="center")
    fig.suptitle("Historical threshold, initial-condition and energy-demand sensitivity", y=1.02)
    fig.text(0.01, -0.04, "Blue bands show the European 2,600–5,400 year compatibility duration.", fontsize=8)
    fig.tight_layout()
    fig.savefig(path_png, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="use a coarser compatibility grid")
    args = parser.parse_args()
    _style()
    base = HistoricalParameters()
    sim = _baseline_trajectory(base)
    pd.DataFrame(
        {"t": sim.t, "N": sim.N, "M": sim.M, "s_N": sim.s_N, "s_M": sim.s_M}
    ).to_csv(TAB / "historical_baseline_trajectory.csv", index=False)
    figure1(sim, FIG / "fig1_historical_trajectories.png", FIG / "fig1_historical_trajectories.pdf")

    n_w = 13 if args.quick else 25
    n_b = 13 if args.quick else 25
    w_ratios = np.unique(np.round(np.concatenate([np.linspace(0.2, 2.0, n_w), [1.0]]), 12))
    beta_ratios = np.unique(np.round(np.concatenate([np.linspace(0.5, 1.5, n_b), [1.0]]), 12))
    rows = compatibility_scan(base, w_ratios, beta_ratios, workers=1)
    df = pd.DataFrame(rows)
    df.to_csv(TAB / "historical_compatibility_scan.csv", index=False)
    summary = summarize_scan(rows)
    with open(TAB / "historical_compatibility_summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    figure2(rows, FIG / "fig2_historical_compatibility.png", FIG / "fig2_historical_compatibility.pdf", summary)

    sens = sensitivity_tables(base)
    sens.to_csv(TAB / "historical_sensitivity.csv", index=False)
    figureS(sens, FIG / "figS_historical_sensitivity.png", FIG / "figS_historical_sensitivity.pdf")

    baseline_row = df[(np.isclose(df["w_ratio"], 1.0)) & (np.isclose(df["beta_ratio"], 1.0))]
    with open(TAB / "historical_baseline_summary.json", "w", encoding="utf-8") as fh:
        json.dump(
            {
                "T_rep": sim.T_rep,
                "censored": sim.censored,
                "N_crit": base.N_crit,
                "baseline_scan_row": baseline_row.to_dict(orient="records"),
            },
            fh,
            indent=2,
        )
    print(json.dumps(summary, indent=2))
    print("baseline T_rep:", sim.T_rep, "censored:", sim.censored)


if __name__ == "__main__":
    main()
