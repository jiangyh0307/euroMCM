# ARCHIVED v2 SNAPSHOT — superseded by the root README and docs/p0_acceptance.md

Historical record only. Its pre-specified terminology, solver recommendations,
test counts and validation claims are superseded; none of the ranges was preregistered.

# EuroMCM 2026 α — Our Turn

## Status

**Parts I–IV, reliability-revised first executable version: implemented, tested, and run.** The repository contains the unified allocator, historical compatibility analysis, RSI dynamics, alignment/viability calculations, uncertainty quantification, generated figures and tables, and an English mathematical draft. It is a research handoff, not the final 25-page competition paper. Authoritative problem statement: `../2026_Problem_Alpha.pdf`.

The numerical conclusions are **conditional on scenario assumptions**. No RSI parameter is empirically calibrated. Historical compatibility is not causal validation. Monte Carlo frequencies are not objective real-world extinction probabilities.

## Research question

> Under what physical, dynamical, and resource-allocation conditions can humanity avoid extinction and marginalization in a world shared with recursively self-improving AI?

The project studies four linked questions:

1. What drives competitive exclusion in a two-population resource model?
2. How do recursive self-improvement, hardware production, and physical constraints jointly determine RSI expansion?
3. What resource protections are sufficient to preserve a human population floor?
4. Which conclusions survive parameter and structural uncertainty?

## Unified framework

Historical and future cases use the **same** weighted proportional-fair allocator:

```text
maximize  sum_i W_i log(s_i)
subject to sum_i D_ij s_i <= S_j
           l_i <= s_i <= 1
```

with `D_ij = d_ij P_i`, `W_i = w_i P_i`. Energy, land service, and hardware production remain in separate units. Part I uses `a=0`; Parts II–IV add the human protection floor `s_H >= a b_H` and, for `a=1`, an endpoint-consistent construction budget.

The core analytic results, with proofs, are in [`docs/mathematical_model.md`](docs/mathematical_model.md):

- Proposition 1: single-resource weighted-fair allocation.
- Proposition 2: historical relative-advantage condition.
- Proposition 3: efficiency–expansion threshold.
- Proposition 4: industrial self-sufficiency threshold.
- Proposition 5: conditional human population-floor invariance.
- Finite-horizon screen: extinction within `T` is impossible if `H(0)e^{-delta_H T} > H_ext`.

## Project structure

```text
EuroMCM-2026-Alpha/
├── README.md
├── requirements.txt
├── run_all.sh
├── configs/
│   ├── historical.yaml
│   ├── rsi_baseline.yaml
│   └── uq_scenarios.yaml
├── src/alpha/
│   ├── __init__.py
│   ├── allocation.py
│   ├── historical.py
│   ├── rsi.py
│   ├── alignment.py
│   ├── viability.py
│   ├── uncertainty.py
│   ├── parameters.py
│   └── scenarios.py
├── experiments/
│   ├── run_historical.py
│   ├── run_rsi.py
│   ├── run_alignment.py
│   └── run_uq.py
├── results/
│   ├── figures/
│   └── tables/
├── docs/
│   ├── mathematical_model.md
│   ├── results.md
│   ├── assumptions.md
│   ├── limitations.md
│   ├── part_i.md ... part_iv.md
│   └── HANDOFF_zh.md
├── paper/
│   ├── outline.md
│   └── draft_parts_i_iv.tex
└── tests/
    ├── conftest.py
    ├── test_allocation.py
    ├── test_historical.py
    ├── test_rsi.py
    ├── test_viability.py
    └── test_uncertainty.py
```

## Installation

Tested with Python 3.9.6 on macOS. Python 3.11+ is recommended but not required by the current code.

```bash
python3 -m pip install -r requirements.txt
```

The code uses NumPy, SciPy, pandas, Matplotlib, PyYAML and pytest. The allocator's exact two-group solver does not require CVXPY. The generic fallback for more than two active groups uses SciPy SLSQP and is marked regularized.

## Reproduce everything

```bash
./run_all.sh
```

Equivalent individual commands:

```bash
export PYTHONPATH=src
python3 -m pytest -q tests
python3 experiments/run_historical.py
python3 experiments/run_rsi.py
python3 experiments/run_alignment.py
python3 experiments/run_uq.py --n 100 --seed 2026 --dt 1.0
```

The full UQ run with 100 draws per measure takes several minutes on a laptop. The LaTeX draft in `paper/draft_parts_i_iv.tex` is **not compiled** in this environment because no LaTeX engine is installed; the PDF must be built later with `pdflatex` or `tectonic` from the `paper/` directory. For a quick UQ pilot:

```bash
python3 experiments/run_uq.py --n 30 --seed 2026 --dt 1.0
```

All figures are written as PNG and PDF under `results/figures/`; tables and CSV/JSON outputs are under `results/tables/`.

## Figures

|Figure|File|Content|
|---|---|---|
|1|`fig1_historical_trajectories`|Historical `N`, `M`, satisfaction, `T_rep` and compatibility bands|
|2|`fig2_historical_compatibility`|`T_rep` map over acquisition-weight and birth-rate ratios|
|3|`fig3_rsi_scenarios`|`H`, `A`, `q`, `zeta` for low/moderate/rapid scenarios|
|4|`fig4_rsi_resources`|AI energy demand/allocation, human adequacy, bottlenecks, thresholds|
|5|`fig5_alignment_phase`|Alignment–RSI phase diagram and `a_safe` overlay|
|6|`fig6_uq_probabilities`|Outcome probabilities under the three pre-specified measures, Wilson intervals|
|S1|`figS_historical_sensitivity`|Threshold, initial-ratio and energy-difference sensitivity|
|S2|`figS_safe_initial_states`|Fixed-policy population-floor safe slices|
|S3|`figS_alignment_horizon`|Horizon sensitivity|
|S4|`figS_uq_sensitivity`|Rank-based sensitivity for the pre-specified aggressive measure|
|S5|`figS_structural_robustness`|Structural robustness, pre-specified aggressive library|
|S6|`figS_uq_stress_augmented`|Exploratory stress-augmented probabilities (post-hoc)|
|S7|`figS_structural_robustness_stress_augmented`|Structural robustness, exploratory stress library|
|S8|`figS_controlled_stress`|Controlled human-demography x AI-pressure factorial|

## Key computed results

Full detail: [`docs/results.md`](docs/results.md).

- **Historical baseline:** `T_rep = 2867.46 yr` (European band 2,600–5,400). Full 650-cell grid: 14 European-compatible cells (2.15%), 30 regional-compatible (4.62%), 325 censored, 0 errors. H0 and H1 both have compatible cells; the data do not distinguish them.
- **RSI scenarios:** low/moderate scenarios are non-marginal at `a=0.5`; rapid is marginal; the joint stress scenario reaches extinction at `a=0` (`t=68.86 yr`) and marginal survival at `a=0.5/1.0`. The low scenario's AI is not self-sustaining in the human-free counterfactual; moderate/rapid/stress are self-sustaining there, conditional on exogenous power.
- **Controlled 2x2 factorial:** baseline human + stress AI is marginal (`min H=3.57e9`), fast human + baseline AI is marginal (`min H=1.00e8`), and only fast human + stress AI reaches extinction. Extinction requires both in this design; this is not a claim about real human demography.
- **Alignment:** stress certificate `a_safe = 0.600`; numerical population-floor threshold on the 0.1 grid is `0.400`. The certificate is conservative. Non-marginal survival was not observed in the stress scenario.
- **UQ (N=100), pre-specified measures:** conservative is all marginal; central is 98% marginal, 2% non-marginal; the broad aggressive measure has 2% extinction at `a=0` [0.6%, 7.0%], 0 at `a>=0.5`, and 3-4% non-marginal. These are the primary comparison results.
- **Exploratory stress-augmented measure (post-hoc, not pre-registered):** extinction probability 0.42 at `a=0` [0.33,0.52], 0 at `a>=0.5`; non-marginal 0.19 at `a=1.0` [0.13,0.28]. This measure was constructed after exploratory runs and must not be presented as a forecast.
- **Structural robustness:** pre-specified aggressive library is population-floor safe for 80/80 pairs at `a>=0.2` (robust set `{0.2,0.4,0.6,0.8,1.0}`); exploratory stress-augmented library reaches 80/80 at `a>=0.6` (robust set `{0.6,0.8,1.0}`). Robust non-marginal set is empty in both.
- **Finite-horizon screen:** baseline `H(t) >= H(0)e^{-0.01t}` gives `2.95e9` at 100 years, above `H_ext=1e6`; extinction within 100 years is impossible under baseline demography regardless of AI/alignment.

## Parameter sources and data

- `results/tables/parameter_table.csv` — every key parameter with unit, baseline, admissible range, provenance category, reference and rationale.
- `src/alpha/parameters.py` — executable provenance registry.
- `src/alpha/scenarios.py` — executable scenario definitions and UQ ranges.
- `configs/*.yaml` — human-readable mirrors of the baseline and sampling design.

Evidence labels: **SOURCE** (problem-reported or verifiable), **ESTIMATE** (transparent derivation), **ASSUMPTION** (exploratory scenario). The problem-reported historical bands, adult energy ranges, disputed density ratio and IEA data-centre statistics are SOURCE in this sense; we have not independently re-checked the underlying publications. All demographic and RSI parameters are ASSUMPTION or ESTIMATE, not calibrated measurements.

## Assumptions and limitations

Read [`docs/assumptions.md`](docs/assumptions.md) and [`docs/limitations.md`](docs/limitations.md) before using any number.

Key limitations:

- Historical compatibility is not causal validation; the parameter family is non-identifiable and the 2.15% fraction depends on the grid design and fixed remaining parameters.
- RSI parameters are not empirical. Hardware units, AI energy intensity, acquisition weights, automation, manufacturing and construction energy are scenario values.
- Power supply is exogenous; the human-free counterfactual does not prove autonomous power-plant operation.
- The three-state model treats hardware loss as completed decommissioning; idle-but-unremoved capacity is not represented.
- The alignment parameter is an operational resource-protection definition, not a measure of AI intent.
- The population-floor certificate is sufficient under strong assumptions and does not guarantee welfare or non-marginal survival.
- Monte Carlo probabilities are conditional on disclosed measures and model structure, not real-world extinction probabilities.
- The fixed-step RK4 integrator remains the default for robustness. The earlier adaptive-solver chatter was partly caused by a scale-separation defect in the allocator; after the fix, adaptive `solve_ivp` completes the previously hanging case and agrees with RK4 in a regression test. No global error bound is claimed.
- The pre-specified UQ measures are conservative, central and broad aggressive. The `stress_augmented` measure is post-hoc exploratory and is reported separately; it must not be presented as a pre-registered comparison or forecast.
- Numerical alignment results are not monotone; no unique critical alignment is claimed.

## Tests

```bash
python3 -m pytest -q tests
```

Current result: **41 passed**. Tests cover the analytic single-resource solution, KKT/dual checks, abundant supply, caps and floors, zero populations, zero supply, two binding resources, unit scaling, tiny-population analytic regression (down to 1e-40), random feasible comparisons, historical event/censoring/time scaling, RSI domain and energy conservation, the efficiency identity, the industrial threshold, alignment endpoints, the viability certificate, RK4/solve_ivp agreement on the previously chattering case, dt convergence, non-saturating growth, sampling reproducibility and probability partitions.

## Completed / remaining

Completed (P0 v1):

- Unified allocator with exact two-group polygon solver, boundary handling, and a robust single-resource relaxation for extreme scale separation.
- Historical dynamics, compatibility grid, H0/H1 comparison, censoring and sensitivity.
- RSI three-state dynamics, construction/manufacturing/site constraints, industrial dependency, human-free counterfactual.
- Alignment outcomes, phase diagram, fixed-policy safe-state slices, analytic certificate.
- Scenario Monte Carlo, Wilson intervals, rank sensitivity, structural robustness, and a controlled 2x2 human-demography x AI-pressure factorial.
- Figures 1–6 and supplementary figures S1–S8; parameter table; English mathematical draft and LaTeX draft.
- Unit tests and reproduction commands.

Remaining (P1/P2):

- Independently verify the historical references and improve calibration; add spatial migration and regional structure.
- Replace scenario RSI parameters with better empirical hardware/energy/land evidence; add supply-chain and idle-capacity states.
- Implement Part V: at least two human intervention policies and timing comparisons, including a computing-power cap and a fallible shutdown mechanism.
- Extend to viability kernels, robust control, bifurcation analysis and EVPI.
- Produce the final competition paper, one-page summary sheet, ENOCH letter, verified references, AI-use report and final typesetting.

The original problem's intervention comparison is **not** satisfied by this repository yet.

## Handoff

1. Read `docs/mathematical_model.md` for definitions and proofs.
2. Read `docs/results.md` for computed numbers and figure/table paths.
3. Read `src/alpha/parameters.py` and `src/alpha/scenarios.py` before changing any numerical input.
4. Run `python3 -m pytest -q tests` after any model change.
5. Regenerate figures with the commands above; do not edit plots by hand.
6. Keep the distinction between SOURCE, ESTIMATE and ASSUMPTION in every new parameter.
7. Do not present scenario probabilities as real-world extinction probabilities, and do not present historical compatibility as causal validation.
8. Keep the pre-specified measures separate from the post-hoc `stress_augmented` exploratory measure. The latter must not be described as pre-registered.
