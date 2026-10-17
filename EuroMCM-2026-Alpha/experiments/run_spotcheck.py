"""Stratified exploratory spot checks; not a full-library numerical certificate."""
import json
import signal
import time
from pathlib import Path

import numpy as np
import pandas as pd

from alpha.rsi import simulate_rsi
from run_acceptance import physical_checks
from run_verify_uq import reconstruct

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results/tables"


def timeout(signum, frame):
    raise TimeoutError("spot-check case exceeded 30 seconds")


def main():
    samples = pd.read_csv(TABLES / "uq_samples.csv")
    old = pd.read_csv(TABLES / "uq_results.csv")
    rng = np.random.default_rng(20261018)
    selected = []
    for name, group in samples.groupby("scenario", sort=True):
        indices = rng.choice(len(group), size=3, replace=False)
        for index in indices:
            selected.append(group.iloc[index].to_dict())
    (TABLES / "p0_spotcheck_selection.json").write_text(json.dumps({
        "seed": 20261018, "sampling": "three parameter vectors per range, without replacement",
        "alignments": [0.0, 0.5, 1.0], "independent_parameter_vectors": 12,
        "note": "alignments share parameters; the 36 checks are not 36 independent vectors",
        "selected": [{"scenario": r["scenario"], "sample_id": int(r["sample_id"])}
                     for r in selected],
    }, indent=2), encoding="utf-8")
    signal.signal(signal.SIGALRM, timeout)
    rows = []
    for sample in selected:
        p = reconstruct(sample)
        for a in [0.0, 0.5, 1.0]:
            previous = old[(old.scenario == sample["scenario"]) &
                           (old.sample_id == sample["sample_id"]) & np.isclose(old.a, a)].iloc[0]
            row = dict(scenario=sample["scenario"], sample_id=int(sample["sample_id"]),
                       a=a, legacy_outcome=previous.outcome)
            start = time.perf_counter()
            try:
                signal.alarm(30)
                sim = simulate_rsi(p, a, rtol=1e-8, atol=1e-10, max_step=.5)
                row.update(outcome=sim.outcome, min_H=sim.min_H,
                           p_bad=sim.p_bad_final_window, extinction_time=sim.extinction_time,
                           same_as_legacy=sim.outcome == previous.outcome,
                           success=sim.success, **physical_checks(sim))
            except Exception as exc:
                row.update(outcome="failed", success=False, same_as_legacy=False, error=str(exc))
            finally:
                signal.alarm(0)
            row["elapsed_seconds"] = time.perf_counter() - start
            rows.append(row)
            pd.DataFrame(rows).to_csv(TABLES / "p0_spotcheck_results.csv", index=False)
            print(f"saved {len(rows)}/36: {row['scenario']}/{row['sample_id']}/a={a}: "
                  f"{row['outcome']} ({row['elapsed_seconds']:.1f}s)", flush=True)
    results = pd.DataFrame(rows)
    summary = dict(simulations=len(results), parameter_vectors=len(selected),
                   failed=int((~results.success).sum()),
                   legacy_classification_changes=int((results.success & ~results.same_as_legacy).sum()),
                   all_library_verified=False,
                   status="stratified_spot_check_only",
                   expansion_rule="Any classification change or failure requires focused follow-up.")
    (TABLES / "p0_spotcheck_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
