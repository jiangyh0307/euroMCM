"""Summarize actual selective-verification artifacts and record input/output hashes."""
from pathlib import Path
import hashlib
import json
import platform
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
import scipy

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results/tables"


def main():
    audit = pd.read_csv(TABLES / "p0_numerical_audit.csv")
    random = pd.read_csv(TABLES / "p0_spotcheck_results.csv")
    controlled = pd.read_csv(TABLES / "p0_controlled_results.csv")
    no_ai = pd.read_csv(TABLES / "p0_no_ai_counterfactual.csv")
    paired = pd.read_csv(TABLES / "p0_paired_rsi_effects.csv")
    bounds = pd.read_csv(TABLES / "p0_sample_bound_audit.csv")
    suite = ET.parse(TABLES / "p0_tests.xml").getroot().find("testsuite")
    tests = {key: int(suite.attrib[key]) for key in ["tests", "failures", "errors", "skipped"]}
    adaptive = audit[audit.method == "adaptive_0.25"]
    physics_ok = bool((random[["operating_violation", "construction_violation",
                               "manufacturing_violation", "analytic_population_bound_violation"]]
                       .max().max() <= 1e-8) and (random.projection_count == 0).all())
    accepted = bool(tests["failures"] == tests["errors"] == 0 and
                    len(adaptive) == 26 and adaptive.pass_check.all() and
                    len(random) == 36 and random.success.all() and random.same_as_legacy.all() and physics_ok and
                    len(controlled) == 480 and controlled.success.all() and
                    len(no_ai) == 96 and no_ai.success.all() and
                    len(paired) == 480 and paired.success_ai.all() and paired.success_no_ai.all() and
                    not bounds.contradicts_analytic_bound.any())
    paths = ["configs/p0_acceptance.yaml", "src/alpha/allocation.py", "src/alpha/rsi.py",
             "results/tables/uq_samples.csv", "results/tables/uq_results.csv",
             "results/tables/p0_controlled_parameters.csv", "results/tables/p0_controlled_results.csv",
             "results/tables/p0_no_ai_counterfactual.csv", "results/tables/p0_paired_rsi_effects.csv",
             "results/tables/p0_paired_rsi_summary.csv", "docs/population_protocol.md",
             "results/tables/p0_numerical_audit.csv", "results/tables/p0_spotcheck_selection.json",
             "results/tables/p0_spotcheck_results.csv", "results/tables/p0_tests.xml",
             "results/tables/part_v_main_experiments.csv", "results/tables/part_v_stress_experiments.csv",
             "results/tables/part_v_main_summary.csv", "results/tables/part_v_manifest.json",
             "results/tables/part_v_risk_main_experiments.csv",
             "results/tables/part_v_risk_stress_experiments.csv",
             "results/tables/part_v_risk_manifest.json", "docs/part_v_results.md",
             "docs/part_v_risk_results.md", "configs/part_v_risk.yaml",
             "src/alpha/risk.py", "results/tables/part_v_ponr_summary.csv",
             "results/tables/part_v_ponr_refinement.csv", "results/tables/part_v_shutdown_mixture.csv",
             "results/tables/part_v_uncertainty_summary.csv",
             "results/tables/part_vi_robustness_summary.csv",
             "results/tables/part_vi_robustness_manifest.json",
             "docs/part_vi_results.md"]
    hashes = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths}
    report = dict(status="selective_research_handoff_accepted" if accepted else "follow_up_required",
                  scope="targeted refinement plus stratified spot checks; not a full-library certificate",
                  tests=tests, python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                  targeted_cases=len(adaptive), adaptive_passes=int(adaptive.pass_check.sum()),
                  old_RK4_failed_comparisons=int((~audit.pass_check).sum()),
                  stratified_checks=len(random), random_class_changes=int((~random.same_as_legacy).sum()),
                  controlled_ai_simulations=len(controlled),
                  paired_no_ai_simulations=len(no_ai),
                  paired_comparisons=len(paired),
                  controlled_failures=int((~controlled.success).sum() + (~no_ai.success).sum()),
                  bound_vectors=len(bounds), bound_contradictions=int(bounds.contradicts_analytic_bound.sum()),
                  full_library_adaptive_verification="INCOMPLETE; discontinued as a P0 prerequisite by user request",
                  part_v_reference_runs=int(len(pd.read_csv(TABLES / "part_v_main_experiments.csv"))),
                  part_v_stress_runs=int(len(pd.read_csv(TABLES / "part_v_stress_experiments.csv"))),
                  part_v_shutdown="EXECUTED_BRANCH_GRID; p_success assumed",
                  part_v_risk_main_runs=int(len(pd.read_csv(TABLES / "part_v_risk_main_experiments.csv"))),
                  part_v_risk_stress_runs=int(len(pd.read_csv(TABLES / "part_v_risk_stress_experiments.csv"))),
                  part_v_ponr_runs=int(len(pd.read_csv(TABLES / "part_v_ponr_scan.csv"))),
                  part_v_shutdown_branches=int(len(pd.read_csv(TABLES / "part_v_shutdown_branches.csv"))),
                  part_v_uncertainty_runs=int(len(pd.read_csv(TABLES / "part_v_uncertainty_results.csv"))),
                  part_vi_sets=int(pd.read_csv(TABLES / "part_vi_robustness_summary.csv").set.nunique()),
                  part_vi_scans=int(len(pd.read_csv(TABLES / "part_vi_robustness_tau_scan.csv"))),
                  risk_thresholds="H_ext=1e8,H_min=2e8,Delta=10,q=0.5,q_total=0.9",
                  all_ranges="exploratory; no preregistration", latex_compilation="NOT EXECUTED: no engine",
                  artifacts_sha256=hashes)
    (TABLES / "p0_handoff_manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "artifacts_sha256"}, indent=2))


if __name__ == "__main__":
    main()
