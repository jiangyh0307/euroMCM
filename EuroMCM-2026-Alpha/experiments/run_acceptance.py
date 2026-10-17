"""P0 audit: controlled RSI contrasts, individual analytic bounds, solver checks.

This protocol is exploratory and explicitly follows the v1/v2 audits. It does
not retroactively preregister those experiments. Existing exploratory results
are retained; new verification outputs have a p0_ prefix.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from alpha.rsi import RSIParameters, simulate_rsi
from alpha.scenarios import (base_rsi, scenario_low, scenario_moderate,
                             scenario_rapid, scenario_stress)
from alpha.viability import extinction_impossible_by_bound
from alpha.uncertainty import sample_parameters, probability_summary


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results/tables"
FIGURES = ROOT / "results/figures"


def sample_bound_audit():
    samples = pd.read_csv(TABLES / "uq_samples.csv")
    results = pd.read_csv(TABLES / "uq_results.csv")
    rows = []
    for _, sample in samples.iterrows():
        H0 = float(sample.H0)
        delta = float(sample.delta_H)
        threshold = 1e6
        horizon = 100.0
        log_margin = np.log(H0 / threshold) - delta * horizon
        selected = results[(results.scenario == sample.scenario) &
                           (results.sample_id == sample.sample_id)]
        events = selected[selected.outcome == "extinction"]
        first_event = events.extinction_time.min() if len(events) else np.nan
        earliest = np.log(H0 / threshold) / delta if delta > 0 else np.inf
        contradiction = bool(len(events) and first_event < earliest - 1e-5)
        rows.append(dict(scenario=sample.scenario, sample_id=sample.sample_id,
                         H0=H0, delta_H=delta, T=horizon, H_ext=threshold,
                         log_extinction_margin=log_margin,
                         extinction_impossible_by_T=extinction_impossible_by_bound(
                             H0, delta, threshold, horizon),
                         earliest_possible_extinction=earliest,
                         observed_extinction_runs=len(events),
                         earliest_recorded_event=first_event,
                         contradicts_analytic_bound=contradiction))
    frame = pd.DataFrame(rows)
    frame.to_csv(TABLES / "p0_sample_bound_audit.csv", index=False)
    summary = frame.groupby("scenario").agg(
        samples=("sample_id", "size"),
        analytically_excluded=("extinction_impossible_by_T", "sum"),
        contradictions=("contradicts_analytic_bound", "sum"),
    )
    summary.to_csv(TABLES / "p0_sample_bound_summary.csv")
    return summary.reset_index().to_dict("records")


def controlled_experiment(config):
    rows, parameter_rows, no_ai_rows = [], [], []
    base = replace(base_rsi(), **config["fixed_parameters"])
    varied = config["varied_parameters"]
    for range_name in config["ranges"]:
        draws = sample_parameters(range_name, config["n_per_range"], config["seed"])
        print(f"controlled RSI: {range_name}", flush=True)
        for sample_id, drawn, _ in draws:
            params = replace(base, **{key: getattr(drawn, key) for key in varied})
            parameter_rows.append(dict(range_name=range_name, sample_id=sample_id,
                                       **asdict(params)))
            # No-AI paired counterfactual: same humans, supplies and land partition;
            # disable AI construction reservation and remove installed AI stock.
            no_ai = replace(params, A0=0.0, rho=0.0)
            no_ai_sim = simulate_rsi(no_ai, 0.0, integrator="solve_ivp",
                                     rtol=1e-8, atol=1e-10, max_step=0.5)
            no_ai_rows.append(dict(scenario=range_name, sample_id=sample_id,
                                   outcome=no_ai_sim.outcome, success=no_ai_sim.success,
                                   min_H=no_ai_sim.min_H,
                                   p_bad=no_ai_sim.p_bad_final_window,
                                   final_H=float(no_ai_sim.H[-1]),
                                   final_s_H=float(no_ai_sim.s_H[-1])))
            for a in config["alignment_grid"]:
                try:
                    sim = simulate_rsi(params, a, integrator="solve_ivp",
                                       rtol=1e-8, atol=1e-10, max_step=0.5)
                    rows.append(dict(scenario=range_name, sample_id=sample_id, a=a,
                                     outcome=sim.outcome, success=sim.success,
                                     min_H=sim.min_H, final_H=sim.H[-1],
                                     final_A=sim.A[-1], final_q=sim.q[-1],
                                     final_s_H=sim.s_H[-1],
                                     p_bad=sim.p_bad_final_window,
                                     extinction_time=sim.extinction_time,
                                     projection_count=sim.numerical_diagnostics["projection_count"]))
                except Exception as exc:
                    rows.append(dict(scenario=range_name, sample_id=sample_id, a=a,
                                     outcome="failed", success=False, error=str(exc)))
    parameters = pd.DataFrame(parameter_rows)
    for key, value in asdict(base).items():
        if key not in varied:
            if not (parameters[key] == value).all():
                raise RuntimeError(f"controlled experiment changed fixed parameter {key}")
    parameters.to_csv(TABLES / "p0_controlled_parameters.csv", index=False)
    results = pd.DataFrame(rows)
    results.to_csv(TABLES / "p0_controlled_results.csv", index=False)
    probabilities = probability_summary(results)
    probabilities.to_csv(TABLES / "p0_controlled_probabilities.csv", index=False)
    no_ai = pd.DataFrame(no_ai_rows)
    no_ai.to_csv(TABLES / "p0_no_ai_counterfactual.csv", index=False)
    paired = results.merge(no_ai, on=["scenario", "sample_id"], suffixes=("_ai", "_no_ai"))
    severity = {"non_marginal": 0, "marginal": 1, "extinction": 2, "failed": 3}
    paired["outcome_worsened_by_ai"] = [
        severity.get(ai, 3) > severity.get(h, 3)
        for ai, h in zip(paired.outcome_ai, paired.outcome_no_ai)
    ]
    paired["delta_min_H"] = paired.min_H_ai - paired.min_H_no_ai
    paired["delta_final_H"] = paired.final_H_ai - paired.final_H_no_ai
    paired["relative_delta_final_H"] = paired.delta_final_H / paired.final_H_no_ai
    paired["delta_final_s_H"] = paired.final_s_H_ai - paired.final_s_H_no_ai
    paired["delta_p_bad"] = paired.p_bad_ai - paired.p_bad_no_ai
    paired.to_csv(TABLES / "p0_paired_rsi_effects.csv", index=False)
    paired_summary = (paired.groupby(["scenario", "a"], as_index=False)
                      .agg(n=("sample_id", "size"),
                           mean_delta_min_H=("delta_min_H", "mean"),
                           median_delta_min_H=("delta_min_H", "median"),
                           mean_relative_delta_final_H=("relative_delta_final_H", "mean"),
                           mean_delta_final_s_H=("delta_final_s_H", "mean"),
                           mean_delta_p_bad=("delta_p_bad", "mean"),
                           fraction_worse=("outcome_worsened_by_ai", "mean"),
                           no_ai_extinction=("outcome_no_ai", lambda s: (s == "extinction").mean()),
                           ai_extinction=("outcome_ai", lambda s: (s == "extinction").mean())))
    paired_summary.to_csv(TABLES / "p0_paired_rsi_summary.csv", index=False)
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.5))
    metrics = [
        ("mean_relative_delta_final_H", "AI vs no-AI change in final H / no-AI H"),
        ("mean_delta_final_s_H", "AI vs no-AI change in final human adequacy"),
        ("mean_delta_p_bad", "AI vs no-AI change in final-window bad fraction"),
    ]
    colors = {"conservative": "#1f4e79", "central": "#c55a11", "aggressive": "#a50021"}
    for ax, (metric, ylabel) in zip(axes, metrics):
        for name in config["ranges"]:
            sub = paired_summary[paired_summary.scenario == name].sort_values("a")
            ax.plot(sub.a, sub[metric], "o-", color=colors[name], label=name)
        ax.axhline(0, color="#555555", lw=.8)
        ax.set_xlabel("Alignment a")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=.2)
    axes[-1].legend(fontsize=8)
    fig.suptitle("Paired AI-present minus no-AI counterfactual; fixed human/resource background")
    fig.tight_layout()
    for extension in ["png", "pdf"]:
        fig.savefig(FIGURES / f"p0_paired_rsi_effects.{extension}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
    for ax, name in zip(axes, config["ranges"]):
        sub = probabilities[probabilities.scenario == name]
        for outcome, color in [("extinction", "#b2182b"), ("marginal", "#f4a582"),
                               ("non_marginal", "#1b7837")]:
            ax.plot(sub.a, sub[f"P_{outcome}"], "o-", color=color, label=outcome)
        ax.set(title=f"{name}: RSI-only variation", xlabel="Alignment a", ylim=(-.03, 1.03))
        ax.grid(alpha=.2)
    axes[0].set_ylabel("Conditional scenario frequency")
    axes[-1].legend(fontsize=8)
    fig.suptitle(f"Controlled exploratory pilot: human demography and supplies fixed; N={config['n_per_range']}/range")
    fig.tight_layout()
    for extension in ["png", "pdf"]:
        fig.savefig(FIGURES / f"p0_controlled_rsi.{extension}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    return dict(draws=len(parameters), ai_present_simulations=len(results),
                no_ai_counterfactual_simulations=len(no_ai),
                paired_comparisons=len(paired),
                failures=int((~results.success).sum() + (~no_ai.success).sum()),
                fixed_parameters_verified=True,
                no_ai_outcomes=no_ai.outcome.value_counts().to_dict(),
                paired_summary=paired_summary.to_dict("records"),
                probabilities=probabilities.to_dict("records"))


def validation_cases():
    cases = []
    for name, maker in [("low", scenario_low), ("moderate", scenario_moderate),
                         ("rapid", scenario_rapid)]:
        for a in [0, .8, 1]:
            cases.append((f"{name}_a{a}", maker(), a))
    for a in [0, .2, .3, .4, .6, .8, 1]:
        cases.append((f"stress_a{a}", scenario_stress(), a))
    cases.append(("tiny_hardware", replace(base_rsi(), A0=1e-12), .5))
    cases.append(("near_site_cap", replace(scenario_stress(), A0=9.9e5), .4))
    old = pd.read_csv(TABLES / "uq_results.csv")
    for name in ["conservative", "central", "aggressive", "stress_augmented"]:
        subset = old[(old.scenario == name) & old.success].copy()
        subset["score"] = abs(subset.final_s_H - .8)
        near = subset.sort_values("score").iloc[0]
        extrema = subset.sort_values("min_H").iloc[0]
        draws = {i: p for i, p, _ in sample_parameters(name, 100, 2026)}
        for label, row in [("adequacy", near), ("minimum", extrema)]:
            cases.append((f"{name}_{label}_sample{int(row.sample_id)}",
                          draws[int(row.sample_id)], float(row.a)))
    return cases


def compare_trajectories(sim, reference):
    end = min(sim.t[-1], reference.t[-1])
    times = np.linspace(0, end, 2001)
    out = {}
    for key in ["H", "A", "q"]:
        values = np.exp(np.interp(times, sim.t, np.log(getattr(sim, key))))
        expected = np.exp(np.interp(times, reference.t, np.log(getattr(reference, key))))
        scale = (reference.params.A_max if key == "A" else np.maximum(expected, 1e-300))
        out[f"{key}_error"] = float(np.max(abs(values - expected) / scale))
    out["same_outcome"] = sim.outcome == reference.outcome
    out["bad_fraction_error"] = (
        abs(sim.p_bad_final_window - reference.p_bad_final_window)
        if not sim.outcome == "extinction" and not reference.outcome == "extinction" else np.nan)
    out["event_time_error"] = (
        abs(sim.extinction_time - reference.extinction_time)
        if sim.outcome == reference.outcome == "extinction" else np.nan)
    return out


def physical_checks(sim):
    p = sim.params
    op_violation = np.max((sim.E_AI_allocated + sim.E_human_allocated - sim.E_op) /
                          max(p.E_total, 1))
    build_violation = np.max((p.c_build * sim.B - sim.R_build) / max(p.E_total, 1))
    factory_violation = np.max((sim.B - sim.manufacturing) / max(p.M_max, 1))
    log_bound_slack = np.log(sim.H / p.H0) + p.delta_H * sim.t
    return dict(operating_violation=float(max(0, op_violation)),
                construction_violation=float(max(0, build_violation)),
                manufacturing_violation=float(max(0, factory_violation)),
                analytic_population_bound_violation=float(max(0, -min(log_bound_slack))),
                projection_count=sim.numerical_diagnostics["projection_count"])


def numerical_audit(config):
    rows = []
    limits = config["comparison"]
    for name, p, a in validation_cases():
        print(f"numerical audit: {name}", flush=True)
        p = replace(p, dt=0.1)
        try:
            reference = simulate_rsi(p, a, integrator="solve_ivp", rtol=1e-10,
                                     atol=1e-12, max_step=0.125)
        except Exception as exc:
            rows.append(dict(case=name, method="reference", pass_check=False, error=str(exc)))
            continue
        methods = [("rk4_1", dict(integrator="rk4", dt_internal=1.0)),
                   ("rk4_0.5", dict(integrator="rk4", dt_internal=0.5)),
                   ("rk4_0.25", dict(integrator="rk4", dt_internal=0.25)),
                   ("adaptive_0.25", dict(integrator="solve_ivp", rtol=1e-8,
                                          atol=1e-10, max_step=.25))]
        for method, kwargs in methods:
            try:
                sim = simulate_rsi(p, a, **kwargs)
                metrics = compare_trajectories(sim, reference)
                physics = physical_checks(sim)
                ok = bool(metrics["same_outcome"] and
                          metrics["H_error"] <= limits["relative_H_error"] and
                          metrics["A_error"] <= limits["capacity_normalized_A_error"] and
                          metrics["q_error"] <= limits["relative_q_error"] and
                          (not np.isfinite(metrics["event_time_error"]) or
                           metrics["event_time_error"] <= limits["event_time_error_years"]) and
                          (not np.isfinite(metrics["bad_fraction_error"]) or
                           metrics["bad_fraction_error"] <= limits["bad_fraction_error"]) and
                          max(physics[k] for k in physics if k != "projection_count") <= 1e-8)
                if method.startswith("adaptive"):
                    ok = bool(ok and metrics["H_error"] <= limits["adaptive_refinement_error"] and
                              metrics["q_error"] <= limits["adaptive_refinement_error"])
                rows.append(dict(case=name, method=method, a=a, outcome=sim.outcome,
                                 reference_outcome=reference.outcome, pass_check=ok,
                                 p_bad=sim.p_bad_final_window,
                                 reference_p_bad=reference.p_bad_final_window,
                                 **metrics, **physics))
            except Exception as exc:
                rows.append(dict(case=name, method=method, pass_check=False, error=str(exc)))
    frame = pd.DataFrame(rows)
    frame.to_csv(TABLES / "p0_numerical_audit.csv", index=False)
    return dict(cases=frame.case.nunique(), comparisons=len(frame),
                passed=int(frame.pass_check.sum()),
                failures=frame[~frame.pass_check].replace({np.nan: None}).to_dict("records"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--section", choices=["all", "bounds", "controlled", "numerics"], default="all")
    args = parser.parse_args()
    with open(ROOT / "configs/p0_acceptance.yaml") as handle:
        config = yaml.safe_load(handle)
    summary = dict(protocol=config, status="targeted_validation_not_global_certificate")
    if args.section in ["all", "bounds"]:
        summary["sample_bounds"] = sample_bound_audit()
    if args.section in ["all", "controlled"]:
        summary["controlled"] = controlled_experiment(config)
    if args.section in ["all", "numerics"]:
        summary["numerics"] = numerical_audit(config)
    path = TABLES / f"p0_acceptance_{args.section}.json"
    path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    display = {k: v for k, v in summary.items() if k not in ["protocol", "controlled"]}
    if "numerics" in display:
        display["numerics"] = {k: v for k, v in summary["numerics"].items() if k != "failures"}
        display["numerics"]["failed_comparisons"] = len(summary["numerics"]["failures"])
    print(json.dumps(display, indent=2))


if __name__ == "__main__":
    main()
