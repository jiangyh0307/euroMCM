"""Generate Part IV scenario-probability, sensitivity and robustness outputs.

All ranges are exploratory, not preregistered. The first three are earlier
broad ranges. The stress-augmented range was selected later after inspecting
outcomes, and is kept separate from the broad comparison.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from alpha.uncertainty import (
    probability_summary,
    rank_sensitivity,
    run_uq,
    structural_robustness,
)

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
TAB = ROOT / "results" / "tables"
FIG.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)

SCENARIOS = ["conservative", "central", "aggressive"]
EXPLORATORY = ["stress_augmented"]
COLORS = {
    "extinction": "#b2182b",
    "marginal": "#f4a582",
    "non_marginal": "#1b7837",
}


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


def _plot_probabilities(ax, sub: pd.DataFrame) -> None:
    for outcome, prob_key, ci_key, label in [
        ("extinction", "P_extinction", "P_ext", "Extinction"),
        ("marginal", "P_marginal", "P_marg", "Marginal survival"),
        ("non_marginal", "P_non_marginal", "P_nm", "Non-marginal survival"),
    ]:
        ax.plot(sub["a"], sub[prob_key], marker="o", color=COLORS[outcome], lw=1.8, label=label)
        ax.fill_between(
            sub["a"], sub[f"{ci_key}_lo"], sub[f"{ci_key}_hi"],
            color=COLORS[outcome], alpha=0.18, linewidth=0,
        )
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("Alignment $a$")
    ax.legend(frameon=True, fontsize=8)


def figure6(prob: pd.DataFrame, path_png: Path, path_pdf: Path, n: int) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.2), sharey=True)
    for ax, scenario in zip(axes, SCENARIOS):
        _plot_probabilities(ax, prob[prob["scenario"] == scenario].sort_values("a"))
        ax.set_title(f"{scenario.capitalize()} (broad exploratory range)")
    axes[0].set_ylabel("conditional outcome probability")
    fig.suptitle(f"Outcome frequencies under broad exploratory ranges (N = {n} per range)", y=1.03)
    fig.text(
        0.01,
        0.005,
        "Bands are pointwise Wilson sampling intervals for iid draws. These are conditional model-scenario probabilities, "
        "not objective probabilities of real-world human extinction.",
        fontsize=7.4,
        color="#444444",
    )
    fig.tight_layout()
    fig.savefig(path_png, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)


def figure_exploratory(prob: pd.DataFrame, path_png: Path, path_pdf: Path, n: int) -> None:
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    _plot_probabilities(ax, prob[prob["scenario"] == "stress_augmented"].sort_values("a"))
    ax.set_ylabel("conditional outcome probability")
    ax.set_title("Exploratory stress-augmented measure (post-hoc)")
    fig.suptitle(f"Stress-augmented exploratory probabilities (N = {n})", y=1.03)
    fig.text(
        0.01,
        0.005,
        "This measure was constructed after exploratory runs to exercise the extinction boundary. It is not pre-registered "
        "and must not be read as a forecast or as evidence about real-world extinction risk.",
        fontsize=7.2,
        color="#444444",
    )
    fig.tight_layout()
    fig.savefig(path_png, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)


def _pick_panel(sens: pd.DataFrame, candidates):
    for output, a_used in candidates:
        sub = sens[
            (sens["output"] == output)
            & np.isclose(sens["a"], a_used)
            & np.isfinite(sens["spearman_rho"])
        ].copy()
        if not sub.empty:
            values = sub.groupby("input")["spearman_rho"].mean()
            if values.nunique() > 1:
                return output, a_used
    return candidates[0]


def figure_sensitivity(sens: pd.DataFrame, path_png: Path, path_pdf: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.8))
    selected = [
        _pick_panel(
            sens[sens["scenario"] == "aggressive"],
            [("log10_min_H", 0.5), ("non_marginal", 1.0)],
        ),
        _pick_panel(
            sens[sens["scenario"] == "aggressive"],
            [("extinction", 0.0), ("non_marginal", 1.0), ("log10_min_H", 0.5)],
        ),
    ]
    for ax, (output, a_used) in zip(axes, selected):
        sub = sens[
            (sens["scenario"] == "aggressive")
            & (sens["output"] == output)
            & np.isclose(sens["a"], a_used)
            & np.isfinite(sens["spearman_rho"])
        ].copy()
        sub = sub[sub["input"] != "H0"]
        if sub.empty:
            ax.text(0.5, 0.5, "no finite rank correlations", ha="center", va="center")
            continue
        sub["abs_rho"] = sub["spearman_rho"].abs()
        sub = sub.sort_values("abs_rho", ascending=True).tail(12)
        ax.barh(sub["input"], sub["spearman_rho"], color="#1f4e79", alpha=0.85)
        ax.axvline(0, color="black", lw=0.8)
        ax.set_xlabel("Spearman rank correlation")
        ax.set_title(f"Broad aggressive range, a = {a_used:.1f}: {output}")
    fig.suptitle("Rank-based global sensitivity screening (association, not causal effect)", y=1.02)
    fig.text(
        0.01,
        0.005,
        "Bootstrap intervals are omitted from the bars for legibility; see results/tables/uq_sensitivity.csv. "
        "Rank correlations do not establish causal importance. The post-hoc stress-augmented measure is excluded from this primary panel.",
        fontsize=7.0,
        color="#444444",
    )
    fig.tight_layout()
    fig.savefig(path_png, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)


def figure_structural(
    summary: pd.DataFrame,
    path_png: Path,
    path_pdf: Path,
    *,
    title: str,
    note: str,
) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    sub = summary.sort_values("a")
    ax.plot(sub["a"], sub["n_population_floor"] / sub["n_pairs"], marker="o", lw=1.8,
            color="#1f4e79", label="population floor safe")
    ax.plot(sub["a"], sub["n_non_marginal"] / sub["n_pairs"], marker="s", lw=1.8,
            color="#1b7837", label="non-marginal safe")
    for _, row in sub.iterrows():
        if row["robust_population_floor"]:
            ax.plot(row["a"], 1.02, marker="v", color="#1f4e79", ms=8, clip_on=False)
        if row["robust_non_marginal"]:
            ax.plot(row["a"], 1.06, marker="v", color="#1b7837", ms=8, clip_on=False)
    ax.set_ylim(-0.02, 1.1)
    ax.set_xlabel("Alignment $a$")
    ax.set_ylabel("fraction of tested pairs safe")
    ax.set_title(title)
    ax.legend(frameon=True, fontsize=8)
    fig.text(0.01, 0.005, note, fontsize=7.2, color="#444444")
    fig.tight_layout()
    fig.savefig(path_png, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)


def _run_block(scenarios, args, a_grid):
    all_samples = []
    all_results = []
    for scenario in scenarios:
        print(f"running {scenario} ...", flush=True)
        samples, results = run_uq(
            scenario, args.n, args.seed, a_grid, dt_internal=args.dt
        )
        samples.to_csv(TAB / f"uq_samples_{scenario}.csv", index=False)
        results.to_csv(TAB / f"uq_results_{scenario}.csv", index=False)
        all_samples.append(samples)
        all_results.append(results)
    return pd.concat(all_samples, ignore_index=True), pd.concat(all_results, ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=100)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--dt", type=float, default=1.0)
    args = parser.parse_args()
    _style()
    a_grid = np.round(np.linspace(0.0, 1.0, 11), 2)

    samples_main, results_main = _run_block(SCENARIOS, args, a_grid)
    samples_expl, results_expl = _run_block(EXPLORATORY, args, a_grid)
    samples = pd.concat([samples_main, samples_expl], ignore_index=True)
    results = pd.concat([results_main, results_expl], ignore_index=True)
    samples.to_csv(TAB / "uq_samples.csv", index=False)
    results.to_csv(TAB / "uq_results.csv", index=False)

    prob_main = probability_summary(results_main)
    prob_expl = probability_summary(results_expl)
    prob_main.to_csv(TAB / "uq_probabilities.csv", index=False)
    prob_expl.to_csv(TAB / "uq_probabilities_stress_augmented.csv", index=False)
    figure6(prob_main, FIG / "fig6_uq_probabilities.png", FIG / "fig6_uq_probabilities.pdf", args.n)
    figure_exploratory(
        prob_expl,
        FIG / "figS_uq_stress_augmented.png",
        FIG / "figS_uq_stress_augmented.pdf",
        args.n,
    )

    sens_mid = rank_sensitivity(samples, results, a_value=0.5, seed=args.seed)
    sens_low = rank_sensitivity(samples, results, a_value=0.0, seed=args.seed)
    sens = pd.concat([sens_mid, sens_low], ignore_index=True)
    sens.to_csv(TAB / "uq_sensitivity.csv", index=False)
    figure_sensitivity(sens, FIG / "figS_uq_sensitivity.png", FIG / "figS_uq_sensitivity.pdf")

    detail_main, robust_main = structural_robustness(
        n_samples=20, seed=args.seed, a_values=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
        scenario="aggressive", dt_internal=args.dt,
    )
    detail_main.to_csv(TAB / "structural_robustness_detail.csv", index=False)
    robust_main.to_csv(TAB / "structural_robustness_summary.csv", index=False)
    figure_structural(
        robust_main,
        FIG / "figS_structural_robustness.png",
        FIG / "figS_structural_robustness.pdf",
        title="Structural robustness: broad exploratory aggressive range",
        note=(
            "20 sampled aggressive-measure parameter vectors crossed with proportional/priority allocation and "
            "saturating/non-saturating growth. This is empirical robustness over tested cases, not a continuous-domain guarantee."
        ),
    )

    detail_expl, robust_expl = structural_robustness(
        n_samples=20, seed=args.seed, a_values=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
        scenario="stress_augmented", dt_internal=args.dt,
    )
    detail_expl.to_csv(TAB / "structural_robustness_detail_stress_augmented.csv", index=False)
    robust_expl.to_csv(TAB / "structural_robustness_summary_stress_augmented.csv", index=False)
    figure_structural(
        robust_expl,
        FIG / "figS_structural_robustness_stress_augmented.png",
        FIG / "figS_structural_robustness_stress_augmented.pdf",
        title="Structural robustness: exploratory stress-augmented library",
        note=(
            "20 sampled stress-augmented vectors crossed with proportional/priority allocation and saturating/non-saturating growth. "
            "This library is post-hoc exploratory, not pre-registered; it is not a forecast."
        ),
    )

    summary = {
        "n_per_scenario": args.n,
        "seed": args.seed,
        "a_grid": a_grid.tolist(),
        "earlier_broad_exploratory_ranges": SCENARIOS,
        "exploratory_measure": EXPLORATORY,
        "broad_exploratory_probabilities_at_a_0_0.5_1": prob_main[
            prob_main["a"].isin([0.0, 0.5, 1.0])
        ].to_dict(orient="records"),
        "exploratory_probabilities_at_a_0_0.5_1": prob_expl[
            prob_expl["a"].isin([0.0, 0.5, 1.0])
        ].to_dict(orient="records"),
        "robust_population_floor_a_main": robust_main[robust_main["robust_population_floor"]]["a"].tolist(),
        "robust_non_marginal_a_main": robust_main[robust_main["robust_non_marginal"]]["a"].tolist(),
        "robust_population_floor_a_exploratory": robust_expl[robust_expl["robust_population_floor"]]["a"].tolist(),
        "robust_non_marginal_a_exploratory": robust_expl[robust_expl["robust_non_marginal"]]["a"].tolist(),
        "failed_runs_main": int((~results_main["success"]).sum()),
        "failed_runs_exploratory": int((~results_expl["success"]).sum()),
    }
    with open(TAB / "uq_summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    # Data-driven candidate unknowns: use only the pre-specified measures.
    main_sens = sens[sens["scenario"].isin(SCENARIOS)].copy()
    pivot = main_sens[np.isfinite(main_sens["spearman_rho"])].copy()
    if not pivot.empty:
        pivot["abs_rho"] = pivot["spearman_rho"].abs()
        use = ((pivot["output"] == "log10_min_H") & np.isclose(pivot["a"], 0.5)) | (
            (pivot["output"] == "extinction") & np.isclose(pivot["a"], 0.0)
        )
        ranking = (
            pivot[use]
            .groupby("input")["abs_rho"]
            .mean()
            .sort_values(ascending=False)
        )
        ranking = ranking.drop(index=["H0"], errors="ignore")
        with open(TAB / "uq_priority_unknowns.txt", "w", encoding="utf-8") as fh:
            fh.write(
                "Candidate measurement priorities from mean absolute Spearman correlation "
                "across the three broad exploratory ranges; outputs are log10_min_H at a=0.5 and extinction at a=0.0.\n"
            )
            fh.write("H0 is excluded because it is an initial condition, not a measurable model parameter.\n")
            fh.write("The post-hoc stress-augmented measure is excluded from this primary ranking.\n")
            fh.write(ranking.to_string())
            fh.write("\n")

    expl_sens = sens[sens["scenario"].isin(EXPLORATORY)].copy()
    expl_pivot = expl_sens[np.isfinite(expl_sens["spearman_rho"])].copy()
    if not expl_pivot.empty:
        expl_pivot["abs_rho"] = expl_pivot["spearman_rho"].abs()
        use = ((expl_pivot["output"] == "log10_min_H") & np.isclose(expl_pivot["a"], 0.5)) | (
            (expl_pivot["output"] == "extinction") & np.isclose(expl_pivot["a"], 0.0)
        )
        expl_rank = (
            expl_pivot[use]
            .groupby("input")["abs_rho"]
            .mean()
            .sort_values(ascending=False)
        )
        expl_rank = expl_rank.drop(index=["H0"], errors="ignore")
        with open(TAB / "uq_priority_unknowns_stress_augmented.txt", "w", encoding="utf-8") as fh:
            fh.write(
                "Candidate measurement priorities for the exploratory stress-augmented measure only.\n"
                "Outputs: log10_min_H at a=0.5 and extinction at a=0.0. H0 excluded as an initial condition.\n"
                "This measure is post-hoc; it is not pre-registered and not a forecast.\n"
            )
            fh.write(expl_rank.to_string())
            fh.write("\n")

    print(prob_main[prob_main["a"].isin([0.0, 0.5, 1.0])].to_string(index=False))
    print(prob_expl[prob_expl["a"].isin([0.0, 0.5, 1.0])].to_string(index=False))
    print("main robust population-floor a:", summary["robust_population_floor_a_main"])
    print("main robust non-marginal a:", summary["robust_non_marginal_a_main"])
    print("exploratory robust population-floor a:", summary["robust_population_floor_a_exploratory"])
    print("exploratory robust non-marginal a:", summary["robust_non_marginal_a_exploratory"])


if __name__ == "__main__":
    main()
