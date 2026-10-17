#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH=src
python3 -m pytest -q tests --junitxml=results/tables/p0_tests.xml
python3 experiments/export_parameters.py
python3 experiments/run_acceptance.py --section bounds
python3 experiments/run_acceptance.py --section controlled
python3 experiments/run_acceptance.py --section numerics
python3 experiments/run_spotcheck.py
python3 experiments/run_part_v.py
python3 experiments/run_part_v_risk.py
python3 experiments/run_part_v_ponr.py --step 1
python3 experiments/run_part_v_ponr_refine.py
python3 experiments/run_part_v_shutdown.py
python3 experiments/run_part_v_uncertainty.py
python3 experiments/run_part_vi_robustness.py
python3 experiments/finalize_handoff.py
