# Result provenance for the manuscript

All numerical values are conditional model outputs. Tables in main.tex were generated from these source files in the local EuroMCM project; numerical experiment code was not changed during manuscript drafting.

| Manuscript material | Project source |
|---|---|
| Historical baseline and 650-point compatibility slice | results/tables/historical_baseline_summary.json; historical_compatibility_summary.json |
| Common and pressure scenario settings | src/alpha/rsi.py; src/alpha/scenarios.py; configs/part_v_risk.yaml |
| Revised 25+25 policies and selected population/adequacy table | results/tables/part_v_risk_main_experiments.csv; part_v_risk_stress_experiments.csv |
| Quarter-year timing brackets | results/tables/part_v_ponr_refinement.json; review_boundary_recheck.csv |
| Earlier four physical scenarios | results/tables/part_vi_robustness_summary.csv |
| Additional eight settings and 621-run design | results/tables/review_sensitivity_summary.csv; review_sensitivity_runs.csv; review_sensitivity_manifest.json |
| Risk-convention assessment | results/tables/review_risk_conventions.csv |
| Mechanism trajectories | results/tables/review_policy_mechanisms.csv |
| Small pressure conditional-frequency table | results/tables/part_v_uncertainty_results.csv; part_v_uncertainty_manifest.json |
| Fixed-background pilot | results/tables/p0_controlled_probabilities.csv; p0_paired_rsi_summary.csv |
| Earlier structural libraries | results/tables/structural_robustness_summary.csv; structural_robustness_summary_stress_augmented.csv |
| Sampling supports | src/alpha/scenarios.py::uq_specs |
| Numerical audits | results/tables/p0_acceptance_numerics.json; p0_spotcheck_summary.json; review_boundary_recheck.csv |

Earlier structural/pilot outputs are described as exploratory and were not all rerun with continuous-event adjudication. Current exact event time and primary timing brackets use the recent dedicated checks. The manuscript is not a real-world forecast or a continuous-domain robust-control certificate.

Reference pages checked during drafting include Kelly's author page, Springer metadata for Viability Theory (2011), original article/preprint records for historical overlap and human–LLM resource experiments, NBER bibliographic data, and IEA Energy and AI (2025). Adult-energy and disputed density figures are attributed to the competition problem where mentioned, without inventing unsupported underlying bibliography entries.
