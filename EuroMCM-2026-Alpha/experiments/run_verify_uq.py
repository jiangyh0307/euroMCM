"""Recheck the stored exploratory UQ library with adaptive, event-based solves.

The stored vectors are reused exactly; no resampling or range selection occurs.
Legacy outputs remain in place. Verified outputs have the p0_verified_ prefix.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, fields, replace
import argparse
import json
from pathlib import Path
import time
import signal

import numpy as np
import pandas as pd

from alpha.rsi import RSIParameters, simulate_rsi
from alpha.scenarios import base_rsi
from alpha.uncertainty import probability_summary, rank_sensitivity
from run_acceptance import physical_checks
from run_uq import _style, figure6, figure_exploratory

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results/tables"
FIGURES = ROOT / "results/figures"


def reconstruct(row):
    names = {f.name for f in fields(RSIParameters)}
    pars = {k: float(v) for k, v in row.items() if k in names}
    pars.update(H_min=1e7, H_ext=1e6, T=100.0, dt=0.25)
    return replace(base_rsi(), **pars)


def verify_vector(task):
    sample, legacy = task
    p = reconstruct(sample)
    rows = []
    for old in legacy:
        started = time.perf_counter()
        a = float(old["a"])
        common = dict(scenario=sample["scenario"], sample_id=sample["sample_id"],
                      a=a, legacy_outcome=old["outcome"],
                      legacy_min_H=old["min_H"], legacy_p_bad=old.get("p_bad", np.nan))
        try:
            def timed_out(signum, frame):
                raise TimeoutError("adaptive solve exceeded the 60-second case budget")
            signal.signal(signal.SIGALRM, timed_out)
            signal.alarm(60)
            sim = simulate_rsi(p, a, rtol=1e-8, atol=1e-10, max_step=.25)
            physics = physical_checks(sim)
            if max(physics[k] for k in physics if k != "projection_count") > 1e-8:
                raise RuntimeError("physical checks failed")
            rows.append(dict(**common, outcome=sim.outcome, success=sim.success,
                             min_H=sim.min_H, p_bad=sim.p_bad_final_window,
                             final_H=sim.H[-1], final_A=sim.A[-1], final_q=sim.q[-1],
                             final_s_H=sim.s_H[-1], extinction_time=sim.extinction_time,
                             outcome_changed=sim.outcome != old["outcome"],
                             elapsed_seconds=time.perf_counter() - started, **physics))
        except Exception as exc:
            rows.append(dict(**common, outcome="failed", success=False, error=str(exc),
                             elapsed_seconds=time.perf_counter() - started))
        finally:
            signal.alarm(0)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--limit", type=int, default=8,
                        help="maximum vectors per invocation; default is a short batch")
    parser.add_argument("--all", action="store_true", help="explicitly request the full remainder")
    args = parser.parse_args()
    samples = pd.read_csv(TABLES / "uq_samples.csv")
    legacy = pd.read_csv(TABLES / "uq_results.csv")
    tasks = []
    effective = []
    for sample in samples.to_dict("records"):
        old = legacy[(legacy.scenario == sample["scenario"]) &
                     (legacy.sample_id == sample["sample_id"])]
        tasks.append((sample, old.to_dict("records")))
        effective.append(dict(scenario=sample["scenario"], sample_id=sample["sample_id"],
                              **asdict(reconstruct(sample))))
    checkpoint = TABLES / "p0_verified_uq_checkpoint.csv"
    rows = pd.read_csv(checkpoint).to_dict("records") if checkpoint.exists() else []
    done = {(r["scenario"], int(r["sample_id"])) for r in rows}
    pending = [task for task in tasks if
               (task[0]["scenario"], int(task[0]["sample_id"])) not in done]
    if not args.all:
        pending = pending[:args.limit]
    start = time.perf_counter()
    print(f"stored={len(tasks)}, checkpointed={len(done)}, this batch={len(pending)}", flush=True)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(verify_vector, task) for task in pending]
        for future in as_completed(futures):
            result = future.result()
            rows.extend(result)
            pd.DataFrame(rows).to_csv(checkpoint, index=False)
            key = result[0]
            print(f"saved {key['scenario']}/{int(key['sample_id'])}: "
                  f"{len(result)} solves, {sum(not r['success'] for r in result)} failures", flush=True)
    done = {(r["scenario"], int(r["sample_id"])) for r in rows}
    if len(done) < len(tasks):
        print(f"batch saved: {len(done)}/{len(tasks)} vectors; full-library verification INCOMPLETE", flush=True)
        return
    results = pd.DataFrame(rows)
    results.to_csv(TABLES / "p0_verified_uq_results.csv", index=False)
    pd.DataFrame(effective).to_csv(TABLES / "p0_verified_effective_parameters.csv", index=False)
    probabilities = probability_summary(results)
    probabilities.to_csv(TABLES / "p0_verified_uq_probabilities.csv", index=False)
    _style()
    broad = probabilities[probabilities.scenario != "stress_augmented"]
    narrow = probabilities[probabilities.scenario == "stress_augmented"]
    figure6(broad, FIGURES / "p0_verified_uq_probabilities.png",
            FIGURES / "p0_verified_uq_probabilities.pdf", 100)
    figure_exploratory(narrow, FIGURES / "p0_verified_stress_probabilities.png",
                       FIGURES / "p0_verified_stress_probabilities.pdf", 100)
    sensitivity = pd.concat([rank_sensitivity(samples, results, a_value=a)
                             for a in [0.0, .5]], ignore_index=True)
    sensitivity.to_csv(TABLES / "p0_verified_sensitivity.csv", index=False)
    summary = dict(stored_vectors=len(tasks), simulations=len(results),
                   elapsed_seconds=time.perf_counter() - start,
                   failures=int((~results.success).sum()),
                   changed_outcomes=int(results.get("outcome_changed", pd.Series(False)).sum()),
                   changes_by_scenario=results.groupby("scenario").outcome_changed.sum().to_dict(),
                   comparison_tolerance=1e-10, integrator="DOP853",
                   max_step=.25, rtol=1e-8, atol=1e-10,
                   design_status="all ranges exploratory; none preregistered")
    (TABLES / "p0_verified_uq_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
