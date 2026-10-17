"""Generate Part II RSI scenario figures and tables."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from alpha.rsi import simulate_human_free, simulate_rsi
from alpha.scenarios import (
    controlled_stress_scenarios,
    scenario_low,
    scenario_moderate,
    scenario_rapid,
    scenario_stress,
)
from alpha.viability import viability_certificate

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


def _sim(p, a):
    return simulate_rsi(p, alignment=a, dt_internal=1.0)


def figure3(scenarios, path_png: Path, path_pdf: Path) -> None:
    colors = {"low": "#1f4e79", "moderate": "#c55a11", "rapid": "#a50021"}
    labels = {
        "low": "A: low RSI growth",
        "moderate": "B: moderate RSI growth",
        "rapid": "C: rapid RSI / automation",
    }
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 7.2))
    panels = [
        ("H", "Human population $H(t)$ (billions of persons)", False, 1.0e-9),
        ("A", "Installed hardware $A(t)$ (hardware units)", True, 1.0),
        ("q", "Capability index $q(t)$", False, 1.0),
        ("zeta", "Automation fraction $\\zeta(q(t))$", False, 1.0),
    ]
    for ax, (key, ylabel, logy, scale) in zip(axes.ravel(), panels):
        for name, sim in scenarios.items():
            ax.plot(sim.t, getattr(sim, key) * scale, color=colors[name], lw=1.9, label=labels[name])
        if logy:
            ax.set_yscale("log")
        ax.set_xlabel("time (years)")
        ax.set_ylabel(ylabel)
        if key == "zeta":
            ax.set_ylim(0, 1.02)
        if key == "q":
            ax.set_ylim(bottom=0)
        ax.legend(frameon=True, fontsize=8.5)
    axes[0, 0].set_title("Populations and capability under three disclosed scenarios (a = 0.5)")
    fig.text(
        0.01,
        0.005,
        "Every numerical parameter is a scenario assumption, not a measured RSI parameter. "
        "Panels use separate axes and units.",
        fontsize=7.5,
        color="#444444",
    )
    fig.tight_layout()
    fig.savefig(path_png, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)


def figure4(stress, path_png: Path, path_pdf: Path) -> None:
    sim = _sim(stress, 0.5)
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 7.2))
    ax = axes[0, 0]
    ax.plot(sim.t, sim.E_AI_demand, color="#a50021", lw=1.8, label="AI demand $e_A(q)A$")
    ax.plot(sim.t, sim.E_AI_allocated, color="#1f4e79", lw=1.8, ls="--", label="allocated to AI")
    ax.set_yscale("log")
    ax.set_xlabel("time (years)")
    ax.set_ylabel("operational energy (MWh/year)")
    ax.set_title("AI operational energy demand and allocation")
    ax.legend(frameon=True)

    ax = axes[0, 1]
    ax.plot(sim.t, sim.s_H, color="#2e7d32", lw=2.0, label="human satisfaction $s_H$")
    ax.axhline(stress.s_min, color="#555555", ls=":", lw=1.0, label="$s_{min}$")
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("time (years)")
    ax.set_ylabel("human resource satisfaction")
    ax.set_title("Human resource adequacy")
    ax.legend(frameon=True)

    ax = axes[1, 0]
    for key, label, color in [
        ("B_desired", "$B_{desired}$", "#a50021"),
        ("B_manufacturing", "$B_{manufacturing}$", "#c55a11"),
        ("B_energy", "$B_{energy}$", "#1f4e79"),
        ("B_site", "$B_{site}$", "#6a3d9a"),
        ("B", "$B=\\min(\\cdot)$", "black"),
    ]:
        ax.plot(sim.t, getattr(sim, key), color=color, lw=1.5, label=label)
    ax.set_yscale("log")
    ax.set_xlabel("time (years)")
    ax.set_ylabel("hardware production (units/year, log scale)")
    ax.set_title("Construction bottlenecks")
    ax.legend(frameon=True, fontsize=8)

    ax = axes[1, 1]
    ax.plot(sim.t, sim.H, color="#2e7d32", lw=2.0, label="human population $H$")
    ax.axhline(stress.H_min, color="#555555", ls=":", lw=1.0, label="$H_{min}$")
    ax.axhline(stress.H_ext, color="#a50021", ls="--", lw=1.0, label="$H_{ext}$")
    ax.set_yscale("log")
    ax.set_xlabel("time (years)")
    ax.set_ylabel("persons (log scale)")
    ax.set_title("Human population and viability thresholds")
    ax.legend(frameon=True)

    fig.suptitle("Resource and bottleneck diagnostics: stress scenario, a = 0.5", y=1.01)
    fig.text(
        0.01,
        0.005,
        "Stress scenario is a conditional stress test, not a forecast. "
        "Operational and construction energy are reported in separate panels and satisfy the budget identity.",
        fontsize=7.5,
        color="#444444",
    )
    fig.tight_layout()
    fig.savefig(path_png, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)


def figure_controlled(rows: pd.DataFrame, path_png: Path, path_pdf: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.0), sharey=False)
    for ax, human in zip(axes, ["baseline_human", "fast_human"]):
        sub = rows[rows["human_demography"] == human]
        for ai, color, label in [
            ("baseline_ai", "#1f4e79", "baseline AI"),
            ("stress_ai", "#a50021", "stress AI"),
        ]:
            s = sub[sub["ai_pressure"] == ai].sort_values("a")
            ax.plot(s["a"], s["min_H"], marker="o", lw=1.8, color=color, label=label)
        hmin = sub["H_min"].iloc[0]
        hext = sub["H_ext"].iloc[0]
        ax.axhline(hmin, color="#555555", ls=":", lw=1.0, label="$H_{min}$")
        ax.axhline(hext, color="#a50021", ls="--", lw=1.0, label="$H_{ext}$")
        ax.set_yscale("log")
        ax.set_xlabel("Alignment $a$")
        ax.set_ylabel("minimum human population (persons, log scale)")
        ax.set_title(f"{human.replace('_', ' ').capitalize()} demography")
        ax.legend(frameon=True, fontsize=8)
    fig.suptitle("Controlled 2x2 stress factorial: human demography x AI pressure", y=1.02)
    fig.text(
        0.01,
        0.005,
        "The four arms change human demography and AI pressure separately. The baseline-human arms are subject to the finite-horizon bound; "
        "extinction in the fast-human arm is not evidence about baseline human demography.",
        fontsize=7.2,
        color="#444444",
    )
    fig.tight_layout()
    fig.savefig(path_png, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    _style()
    scenarios = {
        "low": scenario_low(),
        "moderate": scenario_moderate(),
        "rapid": scenario_rapid(),
    }
    sims = {name: _sim(p, 0.5) for name, p in scenarios.items()}
    figure3(sims, FIG / "fig3_rsi_scenarios.png", FIG / "fig3_rsi_scenarios.pdf")
    stress = scenario_stress()
    figure4(stress, FIG / "fig4_rsi_resources.png", FIG / "fig4_rsi_resources.pdf")

    rows = []
    for name, p in {**scenarios, "stress": stress}.items():
        for a in [0.0, 0.5, 1.0]:
            sim = _sim(p, a)
            cert = viability_certificate(p, rho_max=p.rho)
            qs = p.q_self()
            if np.isfinite(qs):
                crossing = np.where(sim.q >= qs)[0]
                q_crossed = bool(crossing.size > 0)
                t_cross = float(sim.t[crossing[0]]) if q_crossed else float("nan")
            else:
                q_crossed = False
                t_cross = float("nan")
            rows.append(
                {
                    "scenario": name,
                    "a": a,
                    "outcome": sim.outcome,
                    "status": sim.status,
                    "min_H": sim.min_H,
                    "final_H": float(sim.H[-1]),
                    "final_A": float(sim.A[-1]),
                    "final_q": float(sim.q[-1]),
                    "final_s_H": float(sim.s_H[-1]),
                    "final_s_A": float(sim.s_A[-1]),
                    "final_zeta": float(sim.zeta[-1]),
                    "extinction_time": sim.extinction_time,
                    "censored": sim.censored,
                    "p_bad_final_window": sim.p_bad_final_window,
                    "q_self": qs,
                    "q_self_crossed": q_crossed,
                    "t_q_self": t_cross,
                    "a_safe": cert.a_safe,
                    "capacity_violation": sim.capacity_violation,
                }
            )
    pd.DataFrame(rows).to_csv(TAB / "rsi_scenario_summary.csv", index=False)

    hf_rows = []
    for name, p in {**scenarios, "stress": stress}.items():
        for a in [0.0, 0.5, 1.0]:
            hf = simulate_human_free(p, alignment=a)
            ratio = float(hf["A"][-1] / hf["A"][0])
            hf_rows.append(
                {
                    "scenario": name,
                    "a": a,
                    "A0": float(hf["A"][0]),
                    "A_end": float(hf["A"][-1]),
                    "A_ratio": ratio,
                    "q_end": float(hf["q"][-1]),
                    "q_self": p.q_self(),
                    "self_sustaining_counterfactual": bool(ratio > 1.0),
                }
            )
    pd.DataFrame(hf_rows).to_csv(TAB / "rsi_human_free_counterfactual.csv", index=False)

    controlled_rows = []
    for name, p in controlled_stress_scenarios().items():
        human, ai = name.split("__")
        for a in [0.0, 0.5, 1.0]:
            sim = simulate_rsi(p, alignment=a, dt_internal=1.0)
            controlled_rows.append(
                {
                    "arm": name,
                    "human_demography": human,
                    "ai_pressure": ai,
                    "a": a,
                    "outcome": sim.outcome,
                    "min_H": sim.min_H,
                    "final_H": float(sim.H[-1]),
                    "final_A": float(sim.A[-1]),
                    "final_q": float(sim.q[-1]),
                    "final_s_H": float(sim.s_H[-1]),
                    "extinction_time": sim.extinction_time,
                    "H_min": p.H_min,
                    "H_ext": p.H_ext,
                }
            )
    controlled = pd.DataFrame(controlled_rows)
    controlled.to_csv(TAB / "controlled_stress_factorial.csv", index=False)
    figure_controlled(
        controlled,
        FIG / "figS_controlled_stress.png",
        FIG / "figS_controlled_stress.pdf",
    )

    # Efficiency-expansion diagnostic on the rapid scenario.
    rapid = sims["rapid"]
    dlogE = np.gradient(np.log(np.maximum(rapid.E_AI_demand, 1e-300)), rapid.t)
    dlogA = np.gradient(np.log(np.maximum(rapid.A, 1e-300)), rapid.t)
    dlogq = np.gradient(np.log(np.maximum(rapid.q, 1e-300)), rapid.t)
    rhs = dlogA - rapid.params.xi * dlogq
    pd.DataFrame(
        {"t": rapid.t, "dlogE_numeric": dlogE, "dlogA_minus_xi_dlogq": rhs}
    ).to_csv(TAB / "rsi_efficiency_expansion_diagnostic.csv", index=False)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
